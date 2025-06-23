#!/usr/bin/env python3
"""
Command-line interface for podcast transcription pipeline.
"""

import argparse
import sys
from pathlib import Path

# Add src to path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from podcast_transcription import PodcastTranscriptionPipeline

def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Transcribe podcast episodes using Modal cloud infrastructure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Super Data Science" --max-episodes 1
  %(prog)s "Taskmaster Podcast" --max-episodes 3 --filter "Series 19"
  %(prog)s "What Did You Do Yesterday" --language en --auto-stop
  %(prog)s "Radio Ambulante" --language es --output-dir spanish_podcasts
        """
    )
    
    parser.add_argument(
        "podcast_name",
        help="Name of the podcast to search for and transcribe"
    )
    
    parser.add_argument(
        "--max-episodes", "-n",
        type=int,
        default=5,
        help="Maximum number of episodes to transcribe (default: 5)"
    )
    
    parser.add_argument(
        "--filter", "-f",
        dest="episode_filter",
        help="Filter episodes by title containing this text"
    )
    
    parser.add_argument(
        "--language", "-l",
        default="en",
        help="Language code for transcription (default: en)"
    )
    
    parser.add_argument(
        "--output-dir", "-o",
        default="transcriptions",
        help="Output directory for transcription files (default: transcriptions)"
    )
    
    parser.add_argument(
        "--auto-stop",
        action="store_true",
        help="Automatically stop Modal app after transcription to save costs"
    )
    
    args = parser.parse_args()
    
    print("🎙️  Podcast Transcription Pipeline")
    print("=" * 40)
    print(f"📺 Podcast: {args.podcast_name}")
    print(f"📊 Max episodes: {args.max_episodes}")
    if args.episode_filter:
        print(f"🔍 Filter: {args.episode_filter}")
    print(f"🌍 Language: {args.language}")
    print(f"📁 Output dir: {args.output_dir}")
    if args.auto_stop:
        print("🛑 Auto-stop: Enabled")
    print()
    
    try:
        # Initialize pipeline
        pipeline = PodcastTranscriptionPipeline(output_dir=args.output_dir)
        
        # Process podcast
        files = pipeline.process_podcast(
            podcast_name=args.podcast_name,
            max_episodes=args.max_episodes,
            episode_filter=args.episode_filter,
            language=args.language,
            auto_stop=args.auto_stop
        )
        
        if files:
            print(f"\n🎉 Success! Transcribed {len(files)} episode(s)")
            print("📄 Files created:")
            for file_path in files:
                print(f"  • {file_path}")
            print(f"\n💡 Files saved to: {Path(args.output_dir).absolute()}")
        else:
            print("\n❌ No episodes were successfully transcribed")
            return 1
            
        return 0
        
    except KeyboardInterrupt:
        print("\n👋 Transcription cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        return 1

if __name__ == "__main__":
    exit(main()) 