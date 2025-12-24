"""Transcript Formatter - formats segments into readable paragraphs with timestamps."""

import re
from datetime import datetime

from .whisper_transcriber import Transcript, TranscriptSegment
from .video_loader import VideoInfo
from .logger import get_logger

logger = get_logger(__name__)


def format_transcript(
    transcript: Transcript,
    video_info: VideoInfo,
    video_url: str | None = None,
    target_paragraph_seconds: int = 30,
) -> str:
    """Format transcript segments into readable paragraphs with timestamps."""
    lines = [
        f"# {video_info.title}",
        "",
        "## Video Information",
        "",
        f"- **Source**: {video_info.source}",
        f"- **Duration**: {_format_duration(video_info.duration)}",
    ]

    if video_info.uploader:
        lines.append(f"- **Uploader**: {video_info.uploader}")

    if transcript.language:
        lines.append(f"- **Language**: {transcript.language}")

    lines.extend([
        f"- **Transcribed**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
    ])

    if video_info.description:
        lines.extend([
            "## Description",
            "",
            video_info.description,
            "",
        ])

    lines.extend([
        "## Transcript",
        "",
    ])

    if transcript.segments:
        continuous_text = _build_continuous_text_with_timestamps(
            transcript.segments, video_url, target_paragraph_seconds
        )
        formatted_text = _add_paragraph_breaks(continuous_text)
        lines.append(formatted_text)
        lines.append("")
    else:
        lines.append(transcript.text)
        lines.append("")

    return "\n".join(lines)


def _build_continuous_text_with_timestamps(
    segments: list[TranscriptSegment],
    video_url: str | None,
    timestamp_interval: int = 30,
) -> str:
    """Build continuous text with inline timestamps every 30 seconds."""
    if not segments:
        return ""

    text_parts = []
    last_timestamp_time = 0.0

    for segment in segments:
        if segment.start >= last_timestamp_time + timestamp_interval:
            timestamp_str = _format_timestamp(segment.start)

            if video_url and _is_youtube_url(video_url):
                video_id = _extract_youtube_id(video_url)
                if video_id:
                    link = f"https://youtube.com/watch?v={video_id}&t={int(segment.start)}"
                    timestamp_text = f" [{timestamp_str}]({link})"
                else:
                    timestamp_text = f" [{timestamp_str}]"
            else:
                timestamp_text = f" [{timestamp_str}]"

            text_parts.append(timestamp_text)
            last_timestamp_time = segment.start

        text_parts.append(" " + segment.text.strip())

    return "".join(text_parts).strip()


def _add_paragraph_breaks(text: str) -> str:
    """Add paragraph breaks every 4-5 sentences."""
    if not text:
        return ""

    sentences = re.split(r"(?<=[.!?])\s+", text)

    result = []
    sentence_count = 0
    current_paragraph = []

    for i, sentence in enumerate(sentences):
        current_paragraph.append(sentence)
        sentence_count += 1

        if sentence_count >= 4:
            if i + 1 < len(sentences):
                next_sentence = sentences[i + 1]
                clean_next = re.sub(r"\s*\[[^\]]+\](?:\([^)]+\))?\s*", " ", next_sentence).strip()
                words = clean_next.split()

                if words:
                    first_word = words[0].lower()
                    continuation_words = [
                        "but", "and", "so", "because", "however", "although",
                        "while", "yet", "furthermore", "moreover", "therefore", "thus",
                    ]

                    if first_word not in continuation_words:
                        result.append(" ".join(current_paragraph))
                        result.append("\n\n")
                        current_paragraph = []
                        sentence_count = 0
            else:
                result.append(" ".join(current_paragraph))

    if current_paragraph:
        result.append(" ".join(current_paragraph))

    return "".join(result)


def _format_duration(seconds: float) -> str:
    """Format duration as HH:MM:SS or MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"


def _format_timestamp(seconds: float) -> str:
    """Format timestamp as MM:SS or HH:MM:SS."""
    return _format_duration(seconds)


def _is_youtube_url(url: str) -> bool:
    """Check if URL is from YouTube."""
    youtube_domains = ["youtube.com", "youtu.be", "www.youtube.com", "m.youtube.com"]
    return any(domain in url.lower() for domain in youtube_domains)


def _extract_youtube_id(url: str) -> str | None:
    """Extract YouTube video ID from URL."""
    patterns = [
        r"(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None
