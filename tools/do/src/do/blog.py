"""Blog commands - wraps ~/micro-blog tools."""

import subprocess
import sys
from pathlib import Path

import click

MICRO_BLOG_PATH = Path.home() / "micro-blog"


def check_micro_blog():
    """Check if micro-blog repo is available."""
    if not MICRO_BLOG_PATH.exists():
        click.echo(f"Error: micro-blog not found at {MICRO_BLOG_PATH}", err=True)
        sys.exit(1)


@click.group()
def blog():
    """Blog management - export from Notion, publish to micro.blog."""
    pass


@blog.command("list")
@click.option("--blog", "blog_name", type=click.Choice(["tea-journey", "tea-journey-jp"]), help="Which blog to list")
def list_posts(blog_name):
    """List posts from Notion blog database."""
    check_micro_blog()
    
    cmd = ["uv", "run", "python", "-m", "notion_blog.cli", "list"]
    if blog_name:
        # Set database via env or pass arg
        click.echo(f"Listing posts from {blog_name}...")
    
    result = subprocess.run(cmd, cwd=MICRO_BLOG_PATH)
    sys.exit(result.returncode)


@blog.command("export")
@click.option("--blog", "blog_name", type=click.Choice(["tea-journey", "tea-journey-jp"]), 
              default="tea-journey", help="Which blog to export")
@click.option("--output", "-o", type=click.Path(), help="Output directory")
def export_posts(blog_name, output):
    """Export posts from Notion to markdown files."""
    check_micro_blog()
    
    lang_dir = "english" if blog_name == "tea-journey" else "japanese"
    output_dir = output or (MICRO_BLOG_PATH / "content" / lang_dir)
    
    click.echo(f"Exporting {blog_name} to {output_dir}...")
    click.echo("Note: Use notion_blog CLI directly for full export control")
    click.echo(f"  cd {MICRO_BLOG_PATH}")
    click.echo("  uv run python -m notion_blog.cli list")


@blog.command("publish")
@click.option("--dir", "content_dir", type=click.Path(exists=True), required=True,
              help="Directory with markdown files to publish")
@click.option("--destination", type=click.Choice(["tea.ito.com", "cha.ito.com"]),
              help="Which micro.blog to publish to")
@click.option("--dry-run", is_flag=True, help="Preview without posting")
@click.option("--draft", is_flag=True, help="Create as drafts")
def publish(content_dir, destination, dry_run, draft):
    """Publish markdown files to micro.blog via Micropub API.
    
    Requires MICROBLOG_TOKEN environment variable.
    Get token from: https://micro.blog/account/apps
    """
    check_micro_blog()
    
    import os
    token = os.environ.get("MICROBLOG_TOKEN")
    if not token:
        click.echo("Error: MICROBLOG_TOKEN not set", err=True)
        click.echo("Get your token from: https://micro.blog/account/apps")
        sys.exit(1)
    
    # Map destination to micro.blog URL
    dest_map = {
        "tea.ito.com": "https://joitea.micro.blog/",
        "cha.ito.com": "https://joicha.micro.blog/",
    }
    
    cmd = [
        "uv", "run", "python", "scripts/import_posts.py",
        "--token", token,
        "--dir", content_dir,
    ]
    
    if destination:
        cmd.extend(["--destination", dest_map.get(destination, destination)])
    if dry_run:
        cmd.append("--dry-run")
    if draft:
        cmd.append("--draft")
    
    click.echo(f"Publishing to micro.blog...")
    result = subprocess.run(cmd, cwd=MICRO_BLOG_PATH)
    sys.exit(result.returncode)


@blog.command("write")
@click.argument("idea", type=click.Path(exists=True))
@click.option("--writings", type=click.Path(exists=True), 
              help="Directory with your existing posts for style extraction")
@click.option("--output", "-o", type=click.Path(), help="Output file for draft")
def write(idea, writings, output):
    """Generate a blog post from rough ideas using AI.
    
    Analyzes your writing style from existing posts and transforms
    rough notes into a polished draft that sounds like you.
    
    Example:
        do blog write my-idea.md --writings ~/switchboard/posts/
    """
    amplifier_path = Path.home() / "amplifier"
    
    if not (amplifier_path / "scenarios" / "blog_writer").exists():
        click.echo(f"Error: blog_writer not found at {amplifier_path}/scenarios/blog_writer", err=True)
        sys.exit(1)
    
    cmd = ["uv", "run", "python", "-m", "scenarios.blog_writer", idea]
    
    if writings:
        cmd.extend(["--writings", writings])
    if output:
        cmd.extend(["--output", output])
    
    click.echo("✍️ Generating blog post from your idea...")
    result = subprocess.run(cmd, cwd=amplifier_path)
    sys.exit(result.returncode)


@blog.command("status")
def status():
    """Show micro.blog migration status."""
    check_micro_blog()
    
    content_dir = MICRO_BLOG_PATH / "content"
    english_posts = list((content_dir / "english").glob("*.md"))
    japanese_posts = list((content_dir / "japanese").glob("*.md"))
    images = list((content_dir / "images").glob("*"))
    
    click.echo("Micro-blog Migration Status")
    click.echo("=" * 40)
    click.echo(f"English posts:  {len(english_posts)}")
    click.echo(f"Japanese posts: {len(japanese_posts)}")
    click.echo(f"Images:         {len(images)}")
    click.echo()
    click.echo("Next steps:")
    click.echo("  1. Get token: https://micro.blog/account/apps")
    click.echo("  2. Set MICROBLOG_TOKEN in environment")
    click.echo("  3. do blog publish --dir content/english --dry-run")
