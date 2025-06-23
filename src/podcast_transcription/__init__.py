"""
Podcast Transcription Pipeline

A complete pipeline for discovering podcasts via Podchaser API and transcribing
episodes using Modal cloud infrastructure with H100 GPUs and Whisper-large-v3.
"""

from .pipeline import PodcastTranscriptionPipeline
from .podcast_discovery import PodcastMetadata, get_podcast_details

__version__ = "1.0.0"
__all__ = ["PodcastTranscriptionPipeline", "PodcastMetadata", "get_podcast_details"] 