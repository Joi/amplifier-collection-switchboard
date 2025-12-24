"""Index Generator - generates transcript index from existing files."""

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from .logger import get_logger
from .paths import paths

logger = get_logger(__name__)


@dataclass
class TranscriptInfo:
    """Information about a single transcript."""
    folder_name: str
    title: str
    duration: int
    source: str
    created_at: str
    has_insights: bool


def extract_title_from_markdown(md_path: Path) -> str | None:
    """Extract title from first # heading in markdown."""
    try:
        with open(md_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("# "):
                    return line[2:].strip()
    except Exception as e:
        logger.debug(f"Could not extract title from {md_path}: {e}")
    return None


def extract_metadata_from_json(transcript_folder: Path) -> dict:
    """Extract duration, date, source from transcript.json."""
    # Look for JSON in data location
    data_json_path = paths.data_dir / "transcripts" / transcript_folder.name / "transcript.json"
    
    # Try data location first, then content location
    json_path = data_json_path if data_json_path.exists() else transcript_folder / "transcript.json"

    if json_path.exists():
        try:
            with open(json_path) as f:
                data = json.load(f)

                video_info = data.get("video", {})
                metadata = data.get("metadata", {})

                return {
                    "duration": video_info.get("duration", 0),
                    "source": video_info.get("source", "Unknown"),
                    "created_at": metadata.get("transcribed_at", ""),
                }
        except Exception as e:
            logger.debug(f"Could not extract metadata from {json_path}: {e}")

    return {"duration": 0, "source": "Unknown", "created_at": ""}


def format_duration(seconds: int | float) -> str:
    """Format duration in seconds to human-readable format."""
    if not seconds or seconds == 0:
        return "Unknown"

    seconds = int(seconds)
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


def scan_transcripts(transcripts_dir: Path) -> list[TranscriptInfo]:
    """Scan all transcript folders and extract info from existing files."""
    transcripts = []

    if not transcripts_dir.exists():
        logger.warning(f"Transcripts directory does not exist: {transcripts_dir}")
        return transcripts

    for folder in transcripts_dir.iterdir():
        if not folder.is_dir():
            continue

        transcript_md = folder / "transcript.md"
        if not transcript_md.exists():
            continue

        title = extract_title_from_markdown(transcript_md) or folder.name
        metadata = extract_metadata_from_json(folder)
        has_insights = (folder / "insights.md").exists()

        transcript_info = TranscriptInfo(
            folder_name=folder.name,
            title=title,
            duration=metadata["duration"],
            source=metadata["source"],
            created_at=metadata["created_at"],
            has_insights=has_insights,
        )

        transcripts.append(transcript_info)

    transcripts.sort(key=lambda t: t.created_at, reverse=True)
    return transcripts


def generate_index_markdown(transcripts: list[TranscriptInfo]) -> str:
    """Generate markdown index content."""
    lines = [
        "# Transcripts Index",
        "",
        f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ]

    if not transcripts:
        lines.append("No transcripts found.")
        lines.append("")
        lines.append("*Run `do transcribe <url>` to generate transcripts.*")
    else:
        lines.append(f"Total transcripts: {len(transcripts)}")
        lines.append("")
        lines.append("---")
        lines.append("")
        lines.append("## Recent Transcripts")
        lines.append("")

        for transcript in transcripts:
            lines.append(f"### {transcript.title}")

            link_parts = [f"**[Read Transcript]({transcript.folder_name}/transcript.md)**"]
            if transcript.has_insights:
                link_parts.append(f"[AI Insights]({transcript.folder_name}/insights.md)")
            lines.append(f"- {' | '.join(link_parts)}")

            metadata_parts = []

            duration_str = format_duration(transcript.duration)
            if duration_str != "Unknown":
                metadata_parts.append(f"Duration: {duration_str}")

            if transcript.source and transcript.source != "Unknown":
                metadata_parts.append(f"Source: {transcript.source}")

            if transcript.created_at:
                try:
                    dt = datetime.fromisoformat(transcript.created_at.replace("Z", "+00:00"))
                    metadata_parts.append(f"Created: {dt.strftime('%Y-%m-%d')}")
                except (ValueError, TypeError):
                    pass

            if metadata_parts:
                lines.append(f"- {' | '.join(metadata_parts)}")

            lines.append("")

    lines.append("---")
    lines.append("")
    lines.append("*Generated automatically. Run `do transcribe --index` to update.*")
    lines.append("")

    return "\n".join(lines)


def write_index(transcripts_dir: Path) -> None:
    """Scan transcripts and write index.md."""
    logger.info(f"Scanning transcripts in {transcripts_dir}")

    transcripts = scan_transcripts(transcripts_dir)
    logger.info(f"Found {len(transcripts)} transcripts")

    content = generate_index_markdown(transcripts)

    index_path = transcripts_dir / "index.md"
    index_path.write_text(content, encoding="utf-8")

    logger.info(f"Index generated at {index_path}")
