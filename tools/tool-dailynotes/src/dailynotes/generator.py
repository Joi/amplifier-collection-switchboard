"""Daily note generator.

Generates Obsidian-compatible markdown daily notes with calendar
events and project status.
"""

from datetime import datetime
from pathlib import Path

from .calendar import fetch_today_events, format_events_markdown
from .projects import load_project_status, format_projects_markdown


def get_today_date() -> str:
    """Get today's date in YYYY-MM-DD format."""
    return datetime.now().strftime('%Y-%m-%d')


def get_formatted_date() -> str:
    """Get today's date formatted for display (e.g., Thursday, December 12, 2025)."""
    return datetime.now().strftime('%A, %B %d, %Y')


def generate_daily_note(switchboard_path: Path) -> str:
    """Generate a complete daily note.
    
    Args:
        switchboard_path: Path to ~/switchboard/ vault
        
    Returns:
        Complete markdown content for daily note
    """
    today = get_today_date()
    formatted_date = get_formatted_date()
    
    # Fetch calendar events
    events = fetch_today_events()
    calendar_section = format_events_markdown(events)
    
    # Load project status
    project_data = load_project_status(switchboard_path)
    projects_section = format_projects_markdown(project_data)
    
    # Build the note
    lines = [
        "---",
        f"date: {today}",
        "---",
        "",
        f"# {formatted_date}",
        "",
        "## Calendar",
        "",
        calendar_section,
        "",
    ]
    
    # Add projects section if we have data
    if projects_section:
        lines.append(projects_section)
    
    # Add GTD dashboard link
    lines.extend([
        "## Tasks",
        "",
        "[[GTD Dashboard]]",
        "",
        "## Notes",
        "",
        "",
    ])
    
    return '\n'.join(lines)


def write_daily_note(switchboard_path: Path, content: str) -> Path:
    """Write daily note to the dailynote directory.
    
    Args:
        switchboard_path: Path to ~/switchboard/ vault
        content: Markdown content to write
        
    Returns:
        Path to the created file
    """
    today = get_today_date()
    dailynote_dir = switchboard_path / "dailynote"
    
    # Ensure directory exists
    dailynote_dir.mkdir(parents=True, exist_ok=True)
    
    # Write file
    note_path = dailynote_dir / f"{today}.md"
    note_path.write_text(content)
    
    return note_path


def get_obsidian_uri(note_path: Path, vault_name: str = "switchboard") -> str:
    """Generate Obsidian URI to open the note.
    
    Args:
        note_path: Path to the note file
        vault_name: Name of the Obsidian vault
        
    Returns:
        obsidian:// URI string
    """
    # Get relative path within vault
    # Assumes note_path is like ~/switchboard/dailynote/2025-12-12.md
    relative_path = note_path.name
    if note_path.parent.name == "dailynote":
        relative_path = f"dailynote/{note_path.name}"
    
    # URL encode the path
    from urllib.parse import quote
    encoded_path = quote(relative_path, safe='')
    
    return f"obsidian://open?vault={vault_name}&file={encoded_path}"
