"""Web to Markdown - wraps ~/amplifier/scenarios/web_to_md."""

import subprocess
import sys
from pathlib import Path

import click

AMPLIFIER_PATH = Path.home() / "amplifier"


def check_web_to_md():
    """Check if web_to_md is available."""
    if not (AMPLIFIER_PATH / "scenarios" / "web_to_md").exists():
        click.echo(f"Error: web_to_md not found at {AMPLIFIER_PATH}/scenarios/web_to_md", err=True)
        sys.exit(1)


@click.command("web2md")
@click.argument("url")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
@click.option("--no-images", is_flag=True, help="Skip downloading images")
def web2md(url, output, no_images):
    """Convert a web page to clean markdown.
    
    Downloads the page, extracts content, cleans up formatting,
    and saves as organized markdown with images.
    
    Examples:
        do web2md https://example.com/article
        do web2md https://example.com/page -o ~/notes/
    """
    check_web_to_md()
    
    click.echo(f"🌐 Converting {url} to markdown...")
    
    cmd = ["uv", "run", "python", "-m", "scenarios.web_to_md", url]
    
    if output:
        cmd.extend(["--output", output])
    if no_images:
        cmd.append("--no-images")
    
    result = subprocess.run(cmd, cwd=AMPLIFIER_PATH)
    sys.exit(result.returncode)
