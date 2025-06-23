# PodCheck

PodCheck is an AI-powered podcast content analysis service designed to automatically detect and flag adult content in podcast episodes. The service helps content creators, platforms, and listeners identify potentially inappropriate content such as profanity, adult humor, or other mature themes.

## Features

- **Automatic Content Analysis**: Uses advanced speech recognition and AI models to transcribe and analyze podcast audio
- **Adult Content Detection**: Identifies profanity, adult jokes, and other mature content
- **Batch Processing**: Efficiently processes multiple episodes and podcasts
- **Cloud-Based**: Built on Modal for scalable, serverless processing
- **Multiple AI Models**: Supports both Whisper and WhisperX for transcription and analysis

## Architecture

The service consists of several key components:

- **Podcast Downloader** (`podcasts.py`): Handles podcast episode retrieval and storage
- **Transcription Engine** (`transcribe_modal.py`): Cloud-based transcription using Modal and Whisper
- **Advanced Transcription** (`transcription_whisper_x.py`): Enhanced transcription with speaker diarization using WhisperX
- **Content Analysis**: AI-powered analysis of transcribed content for adult themes

## Getting Started

1. **Environment Setup**
   ```bash
   # Install dependencies
   pip install -r requirements.txt
   
   # Set up environment variables
   cp .env.example .env
   # Add your API keys to .env
   ```

2. **API Keys Required**
   - `PODCHASER_DEV_KEY`: For podcast metadata retrieval
   - `HF_TOKEN`: Hugging Face token for speaker diarization
   - Modal credentials for cloud processing

3. **Usage**
   ```python
   # Basic transcription
   from transcribe_modal import Model
   result = Model().transcribe.remote(audio_url, language='en')
   
   # Advanced transcription with speaker detection
   from transcription_whisper_x import transcribe_with_speakers
   result = transcribe_with_speakers(audio_file)
   ```

## Use Cases

- **Content Moderation**: Automatically flag episodes containing adult content
- **Platform Compliance**: Ensure podcasts meet content guidelines
- **Parental Controls**: Help parents identify age-appropriate content
- **Content Categorization**: Organize podcasts by content maturity level

## Technical Details

- **GPU Processing**: Utilizes H100 GPUs for fast transcription
- **Caching**: Implements volume caching for model reuse
- **Concurrent Processing**: Supports multiple simultaneous transcriptions
- **Error Handling**: Robust error handling and retry mechanisms

## Contributing

This project is designed to help create safer podcast listening experiences. Contributions for improving content detection accuracy and adding new features are welcome.
