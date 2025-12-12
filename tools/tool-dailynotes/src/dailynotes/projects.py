"""Project status integration.

Reads project-status.json from the switchboard vault and formats
for inclusion in daily notes.
"""

import json
from pathlib import Path


def load_project_status(switchboard_path: Path) -> dict | None:
    """Load project-status.json from switchboard vault.
    
    Args:
        switchboard_path: Path to ~/switchboard/
        
    Returns:
        Parsed JSON data or None if not found
    """
    status_file = switchboard_path / "amplifier" / "project-status.json"
    
    if not status_file.exists():
        return None
    
    try:
        return json.loads(status_file.read_text())
    except (json.JSONDecodeError, IOError):
        return None


def format_projects_markdown(data: dict | None) -> str:
    """Format project status as markdown for daily note.
    
    Args:
        data: Parsed project-status.json data
        
    Returns:
        Markdown formatted string
    """
    if not data or not data.get('projects'):
        return ""
    
    projects = data['projects']
    
    # Group by status
    started = [p for p in projects if p.get('status') == 'started']
    not_started = [p for p in projects if p.get('status') == 'not-started' and p.get('priority') == 'high']
    
    if not started and not not_started:
        return ""
    
    lines = ["## Projects", ""]
    
    # Priority order for sorting
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    priority_emoji = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
    
    # Active projects
    if started:
        lines.append("### Active")
        started.sort(key=lambda p: priority_order.get(p.get('priority', 'medium'), 99))
        
        for project in started:
            emoji = priority_emoji.get(project.get('priority', 'medium'), '')
            title = project.get('title', 'Untitled')
            file_name = project.get('file', '')
            
            # Create wikilink if file exists
            if file_name:
                line = f"- {emoji} **[[amplifier/{file_name}|{title}]]**"
            else:
                line = f"- {emoji} **{title}**"
            
            lines.append(line)
            
            # Show first next action
            next_actions = project.get('nextActions', [])
            if next_actions:
                lines.append(f"  - Next: {next_actions[0]}")
        
        lines.append("")
    
    # High-priority planned projects (limit to 3)
    if not_started:
        lines.append("### Planned (High Priority)")
        for project in not_started[:3]:
            title = project.get('title', 'Untitled')
            file_name = project.get('file', '')
            
            if file_name:
                lines.append(f"- [[amplifier/{file_name}|{title}]]")
            else:
                lines.append(f"- {title}")
        
        lines.append("")
    
    return '\n'.join(lines)
