"""Markdown enhancement - adds frontmatter and cleans formatting."""

from datetime import datetime
from typing import Any

from .logger import get_logger

logger = get_logger(__name__)


def enhance_markdown(markdown: str, context: dict[str, Any]) -> str:
    """Enhance markdown content with frontmatter and improved formatting.
    
    Args:
        markdown: Raw markdown content
        context: Context including metadata about the page
        
    Returns:
        Enhanced markdown with frontmatter
    """
    frontmatter = create_frontmatter(context)
    return frontmatter + basic_enhance(markdown)


def create_frontmatter(context: dict[str, Any]) -> str:
    """Create YAML frontmatter for the markdown file.
    
    Args:
        context: Metadata about the page
        
    Returns:
        YAML frontmatter string
    """
    lines = ["---"]

    if "url" in context:
        lines.append(f"url: {context['url']}")

    title = context.get("title", "Untitled")
    lines.append(f"title: {title}")

    if "domain" in context:
        lines.append(f"domain: {context['domain']}")

    lines.append(f"retrieved_at: {datetime.now().isoformat()}")

    if "content_type" in context:
        lines.append(f"content_type: {context['content_type']}")

    lines.append("---")
    lines.append("")

    return "\n".join(lines)


def basic_enhance(markdown: str) -> str:
    """Basic markdown enhancement without AI.
    
    Args:
        markdown: Raw markdown content
        
    Returns:
        Cleaned up markdown
    """
    lines = markdown.split("\n")
    enhanced_lines = []

    for line in lines:
        line = line.rstrip()

        # Ensure headings have space after #
        if line.startswith("#"):
            parts = line.split(" ", 1)
            if len(parts) == 2 and not parts[0].endswith("#"):
                line = parts[0] + " " + parts[1].strip()

        enhanced_lines.append(line)

    # Join avoiding excessive blank lines
    result = []
    prev_blank = False

    for line in enhanced_lines:
        is_blank = not line.strip()

        if is_blank and prev_blank:
            continue

        result.append(line)
        prev_blank = is_blank

    return "\n".join(result)
