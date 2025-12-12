"""Reading queue management."""

import click

from .read_service import (
    list_reading,
    add_reading,
    start_reading,
    finish_reading,
    archive_reading,
    get_stats as get_reading_stats,
)


@click.group(name='read')
def read():
    """Manage reading queue for URLs and PDFs."""
    pass


@read.command()
@click.option('--all', 'show_all', is_flag=True, help='Include archived')
def list(show_all: bool):
    """List reading queue."""
    items = list_reading(include_archived=show_all)
    
    if not items:
        click.echo("📚 Reading queue is empty")
        return
    
    to_read = [r for r in items if r['status'] == 'to_read']
    reading = [r for r in items if r['status'] == 'reading']
    done = [r for r in items if r['status'] == 'read']
    
    click.echo(f"📚 Reading Queue (To Read: {len(to_read)} | Reading: {len(reading)} | Read: {len(done)})\n")
    
    if reading:
        click.echo("📖 CURRENTLY READING\n")
        for r in reading:
            icon = '🔗' if r.get('type') == 'url' else '📄'
            click.echo(f"{icon} [{r['id']}] {r['title']}")
        click.echo()
    
    if to_read:
        click.echo("📚 TO READ\n")
        for r in to_read[:10]:
            priority_icon = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(r.get('priority', 'medium'), '🟡')
            icon = '🔗' if r.get('type') == 'url' else '📄'
            click.echo(f"{priority_icon} {icon} [{r['id']}] {r['title']}")
        if len(to_read) > 10:
            click.echo(f"\n... and {len(to_read) - 10} more")


@read.command()
@click.argument('source')
@click.option('--title', '-t', help='Title (auto-detected if URL)')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), default='medium')
@click.option('--tags', help='Comma-separated tags')
def add(source: str, title: str, priority: str, tags: str):
    """Add URL or PDF to reading queue."""
    tag_list = [t.strip() for t in tags.split(',')] if tags else []
    item = add_reading(source, title=title, priority=priority, tags=tag_list)
    click.echo(f"✅ Added: [{item['id']}] {item['title']}")


@read.command()
@click.argument('id_or_title')
def start(id_or_title: str):
    """Start reading (mark as in-progress)."""
    try:
        start_reading(id_or_title)
        click.echo(f"📖 Started reading: {id_or_title}")
    except ValueError:
        click.echo(f"❌ Not found: {id_or_title}", err=True)


@read.command()
@click.argument('id_or_title')
def finish(id_or_title: str):
    """Mark as finished reading."""
    try:
        finish_reading(id_or_title)
        click.echo(f"✅ Finished: {id_or_title}")
    except ValueError:
        click.echo(f"❌ Not found: {id_or_title}", err=True)


@read.command()
@click.argument('id_or_title')
def archive(id_or_title: str):
    """Archive reading item."""
    try:
        archive_reading(id_or_title)
        click.echo(f"📦 Archived: {id_or_title}")
    except ValueError:
        click.echo(f"❌ Not found: {id_or_title}", err=True)


@read.command()
def stats():
    """Show reading queue statistics."""
    s = get_reading_stats()
    click.echo("📚 Reading Queue Statistics\n")
    click.echo(f"Total: {s['total']}")
    click.echo(f"To Read: {s['to_read']}")
    click.echo(f"Reading: {s['reading']}")
    click.echo(f"Read: {s['read']}")
    click.echo(f"Archived: {s['archived']}")
