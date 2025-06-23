# Podcast Transcription Pipeline

A complete pipeline for discovering podcasts via Podchaser API and transcribing episodes using Modal cloud infrastructure with H100 GPUs and Whisper-large-v3.

## Features

- 🔍 **Podcast Discovery**: Search and find podcasts using Podchaser API
- 🎙️ **High-Quality Transcription**: Uses OpenAI's Whisper-large-v3 model
- ⚡ **Cloud GPU Processing**: Powered by Modal's H100 GPUs for fast transcription
- 💰 **Cost Efficient**: Auto-scaling with pay-per-use pricing
- 🌍 **Multi-Language Support**: Supports multiple languages
- 📁 **Structured Output**: Saves transcriptions as JSON with metadata
- 🔧 **Easy CLI Interface**: Simple command-line tools

## Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <repository-url>
cd podcast-transcription

# Install dependencies
uv sync
```

### 2. Setup Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env with your API keys
# - Get Podchaser API keys from: https://www.podchaser.com/api
# - Get Modal API token from: https://modal.com/
```

### 3. Deploy Modal App

```bash
# Deploy the transcription service to Modal
python scripts/deploy.py
```

### 4. Transcribe Podcasts

```bash
# Transcribe latest episode of a podcast
python scripts/transcribe.py "Super Data Science" --max-episodes 1

# Transcribe multiple episodes with filtering
python scripts/transcribe.py "Taskmaster Podcast" --max-episodes 3 --filter "Series 19"

# Auto-stop Modal app after transcription to save costs
python scripts/transcribe.py "What Did You Do Yesterday" --auto-stop
```

## Project Structure

```
podcast-transcription/
├── src/
│   └── podcast_transcription/          # Main package
│       ├── __init__.py                 # Package exports
│       ├── pipeline.py                 # Main pipeline class
│       ├── modal_client.py             # Modal cloud integration
│       ├── podcast_discovery.py        # Podcast search & discovery
│       └── config.py                   # Configuration
├── scripts/
│   ├── transcribe.py                   # CLI transcription interface
│   ├── deploy.py                       # Deploy Modal app
│   └── stop_modal.py                   # Stop Modal app (cost control)
├── examples/
│   └── basic_usage.py                  # Usage examples
├── transcriptions/                     # Output directory
├── pyproject.toml                      # Project configuration
├── env.example                         # Environment template
└── README.md                           # This file
```

## Usage Examples

### Basic Transcription

```python
from podcast_transcription import PodcastTranscriptionPipeline

# Initialize pipeline
pipeline = PodcastTranscriptionPipeline(output_dir="my_transcriptions")

# Transcribe latest episode
files = pipeline.process_podcast(
    podcast_name="Super Data Science",
    max_episodes=1,
    language="en"
)

print(f"Transcribed {len(files)} episodes")
```

### CLI Usage

```bash
# Transcribe with custom settings
python scripts/transcribe.py "Podcast Name" \
    --max-episodes 5 \
    --filter "interview" \
    --language en \
    --output-dir custom_output \
    --auto-stop

# Deploy Modal app
python scripts/deploy.py

# Check and stop Modal apps
python scripts/stop_modal.py
```

## Output Format

Transcriptions are saved as JSON files with comprehensive metadata:

```json
{
  "podcast_title": "Super Data Science",
  "episode_title": "Episode Title",
  "episode_date": "2025-01-15",
  "audio_url": "https://...",
  "transcription_text": "Full transcription text...",
  "transcription_chunks": [...],
  "episode_metadata": {...}
}
```

## Cost Management

- **Auto-scaling**: Modal apps scale to zero when not in use (no cost)
- **Auto-stop**: Use `--auto-stop` flag to immediately stop after transcription
- **Manual control**: Use `python scripts/stop_modal.py` to stop apps anytime
- **Efficient processing**: H100 GPUs provide fast transcription (~5 min per hour of audio)

## API Requirements

### Podchaser API
- Free tier available with rate limits
- Required for podcast discovery and episode metadata
- Get API keys at: https://www.podchaser.com/api

### Modal
- Pay-per-use cloud GPU platform
- H100 GPUs for fast transcription
- Auto-scaling and cost optimization
- Get started at: https://modal.com/

## Troubleshooting

### Common Issues

1. **Environment Variables**: Ensure `.env` file has correct API keys
2. **Modal Setup**: Run `modal setup` if not authenticated
3. **Unicode Errors (Windows)**: Set `$env:PYTHONIOENCODING="utf-8"`
4. **App Not Running**: Pipeline automatically deploys Modal app if needed

### Support

- Check logs for detailed error messages
- Ensure all dependencies are installed with `uv sync`
- Verify API credentials are correct

## License

This project is licensed under the MIT License.
