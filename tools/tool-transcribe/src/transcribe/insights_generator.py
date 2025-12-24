"""Insights Generator - combines summary and quotes into a single document."""

from .quote_extractor import Quote
from .summary_generator import Summary
from .logger import get_logger

logger = get_logger(__name__)


def generate_insights(
    summary: Summary | None,
    quotes: list[Quote] | None,
    title: str,
) -> str:
    """Combine summary and quotes into a single insights document."""
    lines = [
        f"# Insights: {title}",
        "",
    ]

    if summary and summary.overview:
        lines.extend([
            "## Overview",
            "",
            summary.overview,
            "",
        ])

    if summary and summary.key_points:
        lines.extend([
            "## Key Points",
            "",
        ])
        for point in summary.key_points:
            lines.append(f"- {point}")
        lines.append("")

    if quotes:
        lines.extend([
            "## Notable Quotes",
            "",
        ])

        notable_quotes = quotes[:7] if len(quotes) > 7 else quotes

        for quote in notable_quotes:
            timestamp_str = _format_timestamp(quote.timestamp)
            lines.append(f'> "{quote.text}"')

            if quote.timestamp_link:
                lines.append(f"> — [{timestamp_str}]({quote.timestamp_link})")
            else:
                lines.append(f"> — [{timestamp_str}]")

            if quote.context:
                lines.append(">")
                lines.append(f"> *{quote.context}*")

            lines.append("")

    if summary and summary.themes:
        lines.extend([
            "## Central Themes",
            "",
        ])
        for theme in summary.themes:
            lines.append(f"- {theme}")
        lines.append("")

    if quotes and len(quotes) > 7:
        lines.extend([
            "## Additional Quotes",
            "",
        ])

        for quote in quotes[7:]:
            timestamp_str = _format_timestamp(quote.timestamp)
            if quote.timestamp_link:
                lines.append(f'- "{quote.text}" [[{timestamp_str}]({quote.timestamp_link})]')
            else:
                lines.append(f'- "{quote.text}" [{timestamp_str}]')

        lines.append("")

    if not summary and not quotes:
        lines.extend([
            "## Note",
            "",
            "_No insights were generated for this content._",
            "",
        ])

    return "\n".join(lines)


def _format_timestamp(seconds: float) -> str:
    """Format timestamp as MM:SS or HH:MM:SS."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    return f"{minutes:02d}:{secs:02d}"
