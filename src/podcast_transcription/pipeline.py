"""
Main podcast transcription pipeline.

Combines podcast discovery with Modal transcription to create a complete 
podcast processing pipeline.
"""

import json
import pathlib
import subprocess
import sys
from typing import Optional

from .config import get_logger
from .podcast_discovery import (
    PodcastMetadata, 
    get_podcast_details, 
    create_podchaser_client, 
    fetch_episodes_data
)

logger = get_logger(__name__)


class PodcastTranscriptionPipeline:
    """Complete pipeline for podcast discovery and transcription."""
    
    def __init__(self, output_dir: str = "transcriptions"):
        self.output_dir = pathlib.Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        logger.info("✅ Pipeline initialized successfully")
    
    def search_and_get_podcast(self, podcast_name: str) -> PodcastMetadata:
        """Search for a podcast and return metadata."""
        logger.info(f"🔍 Searching for podcast: '{podcast_name}'")
        
        try:
            podcast_details = get_podcast_details(podcast_name)
            logger.info(f"✅ Found podcast: '{podcast_details.title}' (ID: {podcast_details.id})")
            return podcast_details
        except Exception as e:
            logger.error(f"❌ Failed to find podcast '{podcast_name}': {str(e)}")
            logger.error(f"❌ Exception type: {type(e).__name__}")
            import traceback
            logger.error(f"❌ Full traceback: {traceback.format_exc()}")
            raise
    
    def get_episodes_with_urls(self, podcast: PodcastMetadata, max_episodes: int = 5, 
                              episode_filter: Optional[str] = None) -> list[dict]:
        """Get episode metadata including audio URLs."""
        logger.info(f"📡 Fetching episodes for '{podcast.title}'...")
        
        # Use the existing download method but capture episodes instead of downloading
        from gql import gql
        
        client = create_podchaser_client()
        episodes = fetch_episodes_data(gql=gql, client=client, podcast_id=podcast.id, max_episodes=max_episodes)
        
        logger.info(f"📋 Found {len(episodes)} episodes")
        
        # Sort episodes by air date (newest first)
        episodes_with_dates = []
        episodes_without_dates = []
        
        for ep in episodes:
            if ep.get('airDate'):
                episodes_with_dates.append(ep)
            else:
                episodes_without_dates.append(ep)
        
        episodes_with_dates.sort(key=lambda x: x.get('airDate', ''), reverse=True)
        episodes = episodes_with_dates + episodes_without_dates
        
        # Filter episodes if specified
        if episode_filter:
            episodes = [ep for ep in episodes if episode_filter.lower() in ep.get('title', '').lower()]
            logger.info(f"🔽 Filtered to {len(episodes)} episodes matching '{episode_filter}'")
        
        # Return only episodes with audio URLs
        valid_episodes = []
        for ep in episodes[:max_episodes]:
            if ep.get("audioUrl"):
                valid_episodes.append(ep)
            else:
                logger.warning(f"⚠️  Episode '{ep.get('title', 'Unknown')}' has no audio URL, skipping")
        
        logger.info(f"✅ Ready to transcribe {len(valid_episodes)} episodes")
        return valid_episodes

    def ensure_modal_app_running(self):
        """Ensure Modal app is running before transcription."""
        logger.info("🔄 Ensuring Modal app is running...")
        
        # Check if app is running
        try:
            result = subprocess.run([
                "modal", "app", "list"
            ], capture_output=True, text=True, check=True, 
               encoding='cp1252' if sys.platform == "win32" else None, 
               errors='replace' if sys.platform == "win32" else None)
            
            if 'example-base-whisper' in result.stdout and 'stopped' not in result.stdout:
                logger.info("✅ Modal app is already running")
                return True
            else:
                logger.info("📡 Modal app not running, deploying...")
                # Deploy the app
                deploy_result = subprocess.run([
                    "modal", "deploy", "src/podcast_transcription/modal_client.py"
                ], capture_output=True, text=True, check=True,
                   encoding='cp1252' if sys.platform == "win32" else None,
                   errors='replace' if sys.platform == "win32" else None)
                
                logger.info("✅ Modal app deployed, waiting for it to be ready...")
                # Wait for the app to be ready
                import time
                time.sleep(10)  # Give the app time to start up
                
                # Test if the app is ready by trying to call a simple method
                logger.info("🧪 Testing if Modal app is ready...")
                for attempt in range(3):
                    try:
                        test_result = subprocess.run([
                            "modal", "run", "src/podcast_transcription/modal_client.py::main"
                        ], capture_output=True, text=True, timeout=60,
                           encoding='cp1252' if sys.platform == "win32" else None,
                           errors='replace' if sys.platform == "win32" else None)
                        
                        if test_result.returncode == 0:
                            logger.info("✅ Modal app is ready to receive requests")
                            return True
                        else:
                            logger.info(f"⏳ App not ready yet, attempt {attempt + 1}/3...")
                            time.sleep(5)
                    except subprocess.TimeoutExpired:
                        logger.info(f"⏳ App startup timeout, attempt {attempt + 1}/3...")
                        time.sleep(5)
                
                logger.warning("⚠️  Modal app may not be fully ready, but proceeding...")
                return True
                
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to ensure Modal app is running: {e}")
            return False
    
    def transcribe_episode(self, episode: dict, language: str = 'en') -> Optional[dict]:
        """Transcribe a single episode using Modal via subprocess."""
        episode_title = episode.get('title', 'Unknown Episode')
        audio_url = episode.get('audioUrl')
        
        if not audio_url:
            logger.error(f"❌ No audio URL for episode: {episode_title}")
            return None
        
        logger.info(f"🎙️  Transcribing: {episode_title}")
        logger.info(f"📡 Audio URL: {audio_url}")
        
        try:
            # For now, let's modify the modal_client.py to use our URL
            # We'll create a simple approach by temporarily modifying the script
            
            # Read the original script
            original_script = pathlib.Path("src/podcast_transcription/modal_client.py").read_text()
            
            # Create a modified version with our URL and language
            modified_script = original_script.replace(
                'url = "https://pub-ebe9e51393584bf5b5bea84a67b343c2.r2.dev/examples_english_english.wav"',
                f'url = "{audio_url}"'
            ).replace(
                "result = Model().transcribe.remote(url, language='en')",
                f"result = Model().transcribe.remote(url, language='{language}')"
            )
            
            # Write temporary script
            temp_file = pathlib.Path("temp_transcribe.py")
            with open(temp_file, 'w') as f:
                f.write(modified_script)
            
            # Run the script via Modal with proper encoding
            import os
            
            # Set up environment for Modal
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            
            if sys.platform == "win32":
                process = subprocess.run([
                    "modal", "run", "temp_transcribe.py::main"
                ], capture_output=True, text=True, timeout=3600, 
                   encoding='cp1252', errors='replace', env=env)
            else:
                process = subprocess.run([
                    "modal", "run", "temp_transcribe.py::main"
                ], capture_output=True, text=True, timeout=3600, env=env)
            
            # Clean up temp file
            temp_file.unlink(missing_ok=True)
            
            if process.returncode == 0:
                output = process.stdout
                logger.info(f"✅ Modal transcription completed for: {episode_title}")
                
                # The modal_client script already outputs the result in a structured way
                # Let's extract the text from the output
                lines = output.split('\n')
                transcription_text = ""
                chunks: list[dict] = []
                
                # Look for the main transcription text after "TRANSCRIPTION RESULT:"
                capturing_text = False
                for line in lines:
                    if "TRANSCRIPTION RESULT:" in line:
                        capturing_text = True
                        continue
                    elif "TIMESTAMPED SEGMENTS:" in line:
                        capturing_text = False
                        continue
                    elif capturing_text and line.strip() and not line.startswith("="):
                        transcription_text += line.strip() + " "
                
                # Create a simple result structure
                result = {
                    "text": transcription_text.strip(),
                    "chunks": chunks  # For now, we'll keep this simple
                }
                
                if result["text"]:
                    logger.info(f"✅ Successfully transcribed: {episode_title}")
                    return {
                        'episode_metadata': episode,
                        'transcription': result,
                        'audio_url': audio_url
                    }
                else:
                    logger.error(f"❌ No transcription text found for: {episode_title}")
                    logger.error(f"Raw output: {output}")
                    return None
            else:
                logger.error(f"❌ Modal transcription failed with return code {process.returncode}")
                logger.error(f"stdout: {process.stdout}")
                logger.error(f"stderr: {process.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Transcription timed out for: {episode_title}")
            return None
        except Exception as e:
            logger.error(f"❌ Error transcribing '{episode_title}': {str(e)}")
            return None
    
    def save_transcription(self, transcription_data: dict, podcast_title: str) -> pathlib.Path:
        """Save transcription results to file."""
        episode_title = transcription_data['episode_metadata'].get('title', 'unknown')
        episode_date = transcription_data['episode_metadata'].get('airDate', 'unknown')
        
        # Create safe filename components
        safe_podcast = "".join(c for c in podcast_title if c.isalnum() or c in (' ', '-', '_')).strip()[:50]
        safe_episode = "".join(c for c in episode_title if c.isalnum() or c in (' ', '-', '_')).strip()[:80]
        
        # Clean up the date to be filename-safe
        if episode_date and episode_date != 'unknown':
            # Convert datetime to simple date format YYYY-MM-DD
            try:
                from datetime import datetime
                if 'T' in str(episode_date):
                    date_part = str(episode_date).split('T')[0]
                else:
                    date_part = str(episode_date).split(' ')[0]
                safe_date = date_part
            except:
                safe_date = "unknown"
        else:
            safe_date = "unknown"
        
        filename = f"{safe_podcast}_{safe_episode}_{safe_date}.json"
        filepath = self.output_dir / filename
        
        # Save comprehensive data
        output_data = {
            'podcast_title': podcast_title,
            'episode_title': episode_title,
            'episode_date': episode_date,
            'audio_url': transcription_data['audio_url'],
            'transcription_text': transcription_data['transcription']['text'],
            'transcription_chunks': transcription_data['transcription'].get('chunks', []),
            'episode_metadata': transcription_data['episode_metadata']
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"💾 Saved transcription to: {filepath}")
        return filepath
    
    def process_podcast(self, podcast_name: str, max_episodes: int = 5, 
                       episode_filter: Optional[str] = None, language: str = 'en', 
                       auto_stop: bool = False) -> list[pathlib.Path]:
        """Complete pipeline: search -> get episodes -> transcribe -> save."""
        logger.info(f"🚀 Starting podcast transcription pipeline")
        logger.info(f"📺 Podcast: {podcast_name}")
        logger.info(f"📊 Max episodes: {max_episodes}")
        if episode_filter:
            logger.info(f"🔍 Filter: {episode_filter}")
        logger.info(f"🌍 Language: {language}")
        
        # Step 0: Ensure Modal app is running
        if not self.ensure_modal_app_running():
            raise RuntimeError("Failed to start Modal app")
        
        # Step 1: Find podcast
        podcast = self.search_and_get_podcast(podcast_name)
        
        # Step 2: Get episodes with URLs
        episodes = self.get_episodes_with_urls(podcast, max_episodes, episode_filter)
        
        if not episodes:
            logger.error("❌ No valid episodes found")
            return []
        
        # Step 3: Transcribe each episode
        transcribed_files = []
        for i, episode in enumerate(episodes, 1):
            logger.info(f"\n📋 Processing episode {i}/{len(episodes)}")
            
            transcription_data = self.transcribe_episode(episode, language)
            
            if transcription_data:
                # Step 4: Save transcription
                saved_file = self.save_transcription(transcription_data, podcast.title)
                transcribed_files.append(saved_file)
                
                # Display preview
                text_preview = transcription_data['transcription']['text'][:200]
                logger.info(f"📝 Preview: {text_preview}...")
            else:
                logger.warning(f"⚠️  Skipping failed transcription for episode {i}")
        
        logger.info(f"\n✅ Pipeline complete! Transcribed {len(transcribed_files)}/{len(episodes)} episodes")
        logger.info(f"📁 Files saved to: {self.output_dir}")
        
        # Auto-stop Modal app if requested
        if auto_stop:
            logger.info("🛑 Auto-stopping Modal app to free resources...")
            try:
                subprocess.run(["modal", "app", "stop", "example-base-whisper"], 
                             capture_output=True, check=True)
                logger.info("💰 Modal app stopped - no more costs")
            except Exception as e:
                logger.warning(f"⚠️  Could not auto-stop Modal app: {e}")
        
        return transcribed_files 