"""Daily notes - wraps obs-dailynotes."""

import subprocess
import sys
from pathlib import Path

import click

OBS_DAILYNOTES_PATH = Path.home() / "obs-dailynotes"


def check_obs_dailynotes():
    """Check if obs-dailynotes is available."""
    if not OBS_DAILYNOTES_PATH.exists():
        click.echo(f"Error: obs-dailynotes not found at {OBS_DAILYNOTES_PATH}", err=True)
        sys.exit(1)


@click.command()
def daily():
    """Generate today's daily note and open in Obsidian."""
    check_obs_dailynotes()
    
    click.echo("📅 Generating daily note...")
    result = subprocess.run(
        ["npm", "run", "daily"],
        cwd=OBS_DAILYNOTES_PATH,
        capture_output=False
    )
    sys.exit(result.returncode)
