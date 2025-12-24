# Transcribe

Turn YouTube videos and audio files into searchable, quotable transcripts.

## Features

- **YouTube & local files** - Works with URLs or local audio/video
- **Accurate transcription** - Uses OpenAI Whisper API
- **Readable output** - Smart paragraphs with clickable timestamps
- **AI insights** - Optional summaries and key quotes via Claude
- **Resume support** - Pick up where you left off if interrupted

## Installation

```bash
cd ~/amp-sb/tools/tool-transcribe
uv sync
```

## Usage

Via `do` CLI (recommended):
```bash
do transcribe https://youtube.com/watch?v=...
do transcribe podcast.mp3
do transcribe video1.mp4 video2.mp4 --resume
```

Direct:
```bash
transcribe transcribe https://youtube.com/watch?v=...
transcribe index  # regenerate index
```

## Options

- `--resume` - Resume interrupted session
- `--no-enhance` - Skip AI summaries/quotes (faster, cheaper)
- `--force-download` - Re-download audio even if cached
- `--output-dir` - Custom output directory

## Output

Transcripts are saved to `~/switchboard/transcripts/`:

```
~/switchboard/transcripts/
├── index.md              # Auto-generated index
├── VIDEO_ID/
│   ├── transcript.md     # Readable transcript
│   ├── insights.md       # AI summary & quotes
│   └── audio.mp3         # Preserved audio
```

## Requirements

- Python 3.11+
- ffmpeg (for audio extraction)
- OpenAI API key (for Whisper transcription)
- Anthropic API key (for AI enhancements, optional)

## Cost

OpenAI Whisper: ~$0.006/minute of audio
- 10 min video ≈ $0.06
- 60 min video ≈ $0.36
