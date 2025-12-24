"""Web to Markdown - uses local tool-web2md module."""

import subprocess
import sys
from pathlib import Path

import click

TOOL_PATH = Path(__file__).parent.parent.parent.parent / "tool-web2md"


def check_tool():
    """Check if tool-web2md is available."""
    if not TOOL_PATH.exists():
        click.echo(f"Error: tool-web2md not found at {TOOL_PATH}", err=True)
        sys.exit(1)


@click.command("web2md")
@click.argument("urls", nargs=-1, required=True)
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--no-images", is_flag=True, help="Skip downloading images")
@click.option("--resume", is_flag=True, help="Resume from saved state")
def web2md(urls, output, no_images, resume):
    """Convert web pages to clean markdown.
    
    Downloads pages, extracts content, cleans up formatting,
    and saves as organized markdown with images.
    
    Examples:
        do web2md https://example.com/article
        do web2md https://example.com/page -o ~/notes/
        do web2md https://site1.com https://site2.com
    """
    check_tool()
    
    click.echo(f"🌐 Converting {len(urls)} URL(s) to markdown...")
    
    cmd = ["uv", "run", "web2md"]
    cmd.extend(urls)
    
    if output:
        cmd.extend(["--output", output])
    if no_images:
        cmd.append("--no-images")
    if resume:
        cmd.append("--resume")
    
    result = subprocess.run(cmd, cwd=TOOL_PATH)
    sys.exit(result.returncode)
