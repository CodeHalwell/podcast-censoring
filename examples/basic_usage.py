#!/usr/bin/env python3
"""
Example usage of the Podcast Transcription Pipeline

This script demonstrates different ways to use the pipeline
for transcribing podcast episodes.
"""

import sys
from pathlib import Path

# Add src to path so we can import our package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from podcast_transcription import PodcastTranscriptionPipeline

def example_single_episode():
    """Example: Transcribe the latest episode of a podcast."""
    print("🎯 Example 1: Single Latest Episode")
    
    pipeline = PodcastTranscriptionPipeline(output_dir="examples/single")
    
    # Transcribe the most recent episode
    files = pipeline.process_podcast(
        podcast_name="Super Data Science",
        max_episodes=1,
        language="en"
    )
    
    print(f"✅ Transcribed {len(files)} episode(s)")


def example_multiple_episodes():
    """Example: Transcribe multiple recent episodes."""
    print("\n🎯 Example 2: Multiple Recent Episodes")
    
    pipeline = PodcastTranscriptionPipeline(output_dir="examples/multiple")
    
    # Transcribe 3 most recent episodes
    files = pipeline.process_podcast(
        podcast_name="Taskmaster Podcast", 
        max_episodes=3,
        language="en"
    )
    
    print(f"✅ Transcribed {len(files)} episode(s)")


def example_filtered_episodes():
    """Example: Transcribe episodes matching a filter."""
    print("\n🎯 Example 3: Filtered Episodes")
    
    pipeline = PodcastTranscriptionPipeline(output_dir="examples/filtered")
    
    # Only transcribe episodes with "interview" in the title
    files = pipeline.process_podcast(
        podcast_name="What Did You Do Yesterday",
        max_episodes=5,
        episode_filter="EP",  # Filter for episodes containing "EP"
        language="en"
    )
    
    print(f"✅ Transcribed {len(files)} episode(s)")


def example_non_english():
    """Example: Transcribe non-English podcast."""
    print("\n🎯 Example 4: Non-English Podcast")
    
    pipeline = PodcastTranscriptionPipeline(output_dir="examples/spanish")
    
    # Transcribe Spanish podcast
    files = pipeline.process_podcast(
        podcast_name="Radio Ambulante",  # Popular Spanish podcast
        max_episodes=1,
        language="es"  # Spanish language code
    )
    
    print(f"✅ Transcribed {len(files)} episode(s)")


def main():
    """Run all examples."""
    print("🚀 Running Podcast Transcription Pipeline Examples")
    print("=" * 60)
    
    try:
        # Run examples
        example_single_episode()
        example_multiple_episodes() 
        example_filtered_episodes()
        # example_non_english()  # Uncomment if you want to test Spanish
        
        print("\n🎉 All examples completed successfully!")
        print("📁 Check the 'examples/' directory for transcription files")
        
    except Exception as e:
        print(f"\n❌ Example failed: {str(e)}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main()) 