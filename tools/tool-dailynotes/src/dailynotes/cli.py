"""CLI interface for dailynotes tool.

Usage:
    dailynotes              # Generate today's note and open in Obsidian
    dailynotes --no-open    # Generate without opening
    dailynotes --dry-run    # Show what would be generated
"""

import subprocess
from pathlib import Path

import click

from .generator import (
    generate_daily_note,
    get_obsidian_uri,
    get_today_date,
    write_daily_note,
)


def get_switchboard_path() -> Path:
    """Get path to switchboard vault."""
    return Path.home() / "switchboard"


@click.command()
@click.option('--no-open', is_flag=True, help="Don't open in Obsidian after generating")
@click.option('--dry-run', is_flag=True, help="Show what would be generated without writing")
@click.option('--vault', default='switchboard', help="Obsidian vault name (default: switchboard)")
def cli(no_open: bool, dry_run: bool, vault: str):
    """Generate today's daily note with calendar and projects.
    
    Creates a markdown file at ~/switchboard/dailynote/YYYY-MM-DD.md
    with calendar events and active project status.
    """
    switchboard_path = get_switchboard_path()
    
    if not switchboard_path.exists():
        click.echo(f"Error: Switchboard vault not found at {switchboard_path}", err=True)
        raise SystemExit(1)
    
    today = get_today_date()
    click.echo(f"📅 Generating daily note for {today}...")
    
    # Generate content
    content = generate_daily_note(switchboard_path)
    
    if dry_run:
        click.echo("\n--- DRY RUN - Would generate: ---\n")
        click.echo(content)
        click.echo("\n--- END ---")
        return
    
    # Write file
    note_path = write_daily_note(switchboard_path, content)
    click.echo(f"✅ Created: {note_path}")
    
    # Open in Obsidian
    if not no_open:
        uri = get_obsidian_uri(note_path, vault)
        click.echo(f"📂 Opening in Obsidian...")
        subprocess.run(['open', uri], check=False)
    else:
        uri = get_obsidian_uri(note_path, vault)
        click.echo(f"📎 Open with: {uri}")


if __name__ == "__main__":
    cli()
