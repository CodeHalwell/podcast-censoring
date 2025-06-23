# Podcast Transcription API Reference

## PodcastTranscriptionPipeline

The main class for orchestrating podcast discovery and transcription.

### Constructor

```python
PodcastTranscriptionPipeline(output_dir: str = "transcriptions")
```

**Parameters:**
- `output_dir`: Directory where transcription files will be saved

### Methods

#### `process_podcast()`

Complete pipeline: search → get episodes → transcribe → save.

```python
process_podcast(
    podcast_name: str,
    max_episodes: int = 5,
    episode_filter: Optional[str] = None,
    language: str = 'en',
    auto_stop: bool = False
) -> list[pathlib.Path]
```

**Parameters:**
- `podcast_name`: Name of the podcast to search for
- `max_episodes`: Maximum number of episodes to transcribe
- `episode_filter`: Filter episodes by title containing this text
- `language`: Language code for transcription (e.g., 'en', 'es', 'fr')
- `auto_stop`: Automatically stop Modal app after transcription

**Returns:**
- List of paths to created transcription files

#### `search_and_get_podcast()`

Search for a podcast and return metadata.

```python
search_and_get_podcast(podcast_name: str) -> PodcastMetadata
```

## Podcast Discovery Functions

### `get_podcast_details()`

Get podcast details from the name of the podcast.

```python
get_podcast_details(podcast_name: str) -> PodcastMetadata
```

## Data Classes

### `PodcastMetadata`

```python
@dataclasses.dataclass
class PodcastMetadata:
    id: str                           # Unique ID for a podcast
    title: str                        # Title of podcast
    description: str                  # Plaintext description
    html_description: str             # HTML description
    web_url: str                      # Link to podcast on Podchaser
    language: Optional[str] = None    # Language code
```

### `EpisodeMetadata`

```python
@dataclasses.dataclass
class EpisodeMetadata:
    podcast_id: Union[str, int]       # Unique ID of podcast
    podcast_title: Optional[str]      # Title of podcast
    title: str                        # Episode title
    publish_date: str                 # Publish date
    description: str                  # Plaintext description
    html_description: str             # HTML description
    guid: str                         # Unique identifier
    guid_hash: str                    # Hash for filenames
    episode_url: Optional[str]        # Link to episode
    original_download_link: str       # Audio file URL
```

## Command Line Interface

### transcribe.py

Main CLI for transcription:

```bash
python scripts/transcribe.py "Podcast Name" [OPTIONS]
```

**Options:**
- `--max-episodes, -n`: Number of episodes (default: 5)
- `--filter, -f`: Filter episodes by title
- `--language, -l`: Language code (default: en)
- `--output-dir, -o`: Output directory (default: transcriptions)
- `--auto-stop`: Stop Modal app after transcription

### deploy.py

Deploy Modal app:

```bash
python scripts/deploy.py
```

### stop_modal.py

Stop Modal apps:

```bash
python scripts/stop_modal.py [app_name]
```

## Output Format

Transcription files are saved as JSON with this structure:

```json
{
  "podcast_title": "Podcast Name",
  "episode_title": "Episode Title",
  "episode_date": "2025-01-15",
  "audio_url": "https://example.com/audio.mp3",
  "transcription_text": "Full transcription...",
  "transcription_chunks": [],
  "episode_metadata": {
    "id": "episode_id",
    "title": "Episode Title",
    "description": "Episode description...",
    ...
  }
}
``` 