"""CLI wrapper for obs-dailynotes.

Delegates to the Node.js tool at ~/obs-dailynotes for actual work.
"""

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
    if not (OBS_DAILYNOTES_PATH / "package.json").exists():
        click.echo(f"Error: package.json not found in {OBS_DAILYNOTES_PATH}", err=True)
        sys.exit(1)


@click.group()
def cli():
    """Daily notes and workflow tools.
    
    Wrapper around ~/obs-dailynotes for unified access.
    """
    pass


@cli.command()
def daily():
    """Generate today's daily note and open in Obsidian."""
    check_obs_dailynotes()
    
    result = subprocess.run(
        ["npm", "run", "daily"],
        cwd=OBS_DAILYNOTES_PATH
    )
    sys.exit(result.returncode)


@cli.command()
def pres():
    """Manage presentations (list, add, complete)."""
    check_obs_dailynotes()
    
    result = subprocess.run(
        ["npm", "run", "pres"],
        cwd=OBS_DAILYNOTES_PATH
    )
    sys.exit(result.returncode)


@cli.command()
def read():
    """Manage reading queue."""
    check_obs_dailynotes()
    
    result = subprocess.run(
        ["npm", "run", "read"],
        cwd=OBS_DAILYNOTES_PATH
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    cli()
