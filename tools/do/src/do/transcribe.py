"""Transcribe - uses local tool-transcribe module."""

import subprocess
import sys
from pathlib import Path

import click

TOOL_PATH = Path(__file__).parent.parent.parent.parent / "tool-transcribe"


def check_tool():
    """Check if tool-transcribe is available."""
    if not TOOL_PATH.exists():
        click.echo(f"Error: tool-transcribe not found at {TOOL_PATH}", err=True)
        sys.exit(1)


@click.command()
@click.argument("sources", nargs=-1, required=True)
@click.option("--resume", is_flag=True, help="Resume from last saved state")
@click.option("--no-enhance", is_flag=True, help="Skip AI enhancements (summaries/quotes)")
@click.option("--force-download", is_flag=True, help="Re-download audio even if cached")
def transcribe(sources, resume, no_enhance, force_download):
    """Transcribe YouTube videos or audio files.
    
    Examples:
        do transcribe https://youtube.com/watch?v=...
        do transcribe podcast.mp3
        do transcribe video1.mp4 video2.mp4 --resume
    """
    check_tool()
    
    click.echo("🎙️ Starting transcription...")
    
    cmd = ["uv", "run", "transcribe", "transcribe"]
    
    if resume:
        cmd.append("--resume")
    if no_enhance:
        cmd.append("--no-enhance")
    if force_download:
        cmd.append("--force-download")
    
    cmd.extend(sources)
    
    result = subprocess.run(cmd, cwd=TOOL_PATH)
    sys.exit(result.returncode)
