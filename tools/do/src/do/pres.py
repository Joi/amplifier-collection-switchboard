"""Presentation tracking."""

import click

from .pres_service import (
    list_presentations,
    add_presentation,
    start_presentation,
    complete_presentation,
    archive_presentation,
    get_stats as get_presentation_stats,
)


@click.group()
def pres():
    """Track presentations with priorities and deadlines."""
    pass


@pres.command()
@click.option('--all', 'show_all', is_flag=True, help='Include archived')
def list(show_all: bool):
    """List presentations."""
    items = list_presentations(include_archived=show_all)
    
    if not items:
        click.echo("📊 No presentations tracked")
        return
    
    # Group by status (handle both old and new status values)
    todo = [p for p in items if p['status'] in ('planned', 'in_progress', 'todo')]
    done = [p for p in items if p['status'] in ('completed', 'done')]
    archived = [p for p in items if p['status'] == 'archived']
    
    click.echo(f"📊 Presentations (Total: {len(items)} | Todo: {len(todo)} | Done: {len(done)})\n")
    
    if todo:
        click.echo("📋 TO DO\n")
        for p in todo:
            priority_icon = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}.get(p.get('priority', 'medium'), '🟡')
            click.echo(f"{priority_icon} [{p['id']}] {p['title']}")
            if p.get('deadline'):
                click.echo(f"   📅 Due: {p['deadline']}")
        click.echo()
    
    if done:
        click.echo("✅ DONE\n")
        for p in done[:5]:
            click.echo(f"   [{p['id']}] {p['title']}")
        if len(done) > 5:
            click.echo(f"   ... and {len(done) - 5} more")


@pres.command()
@click.argument('title')
@click.option('--deadline', '-d', help='Deadline (YYYY-MM-DD)')
@click.option('--priority', '-p', type=click.Choice(['low', 'medium', 'high', 'urgent']), default='medium')
@click.option('--url', '-u', help='Presentation URL')
def add(title: str, deadline: str, priority: str, url: str):
    """Add a new presentation."""
    pres = add_presentation(title, deadline=deadline, priority=priority, url=url)
    click.echo(f"✅ Added: [{pres['id']}] {title}")


@pres.command()
@click.argument('id_or_title')
def start(id_or_title: str):
    """Mark presentation as in-progress."""
    try:
        start_presentation(id_or_title)
        click.echo(f"▶️  Started: {id_or_title}")
    except ValueError:
        click.echo(f"❌ Not found: {id_or_title}", err=True)


@pres.command()
@click.argument('id_or_title')
def complete(id_or_title: str):
    """Mark presentation as completed."""
    try:
        complete_presentation(id_or_title)
        click.echo(f"✅ Completed: {id_or_title}")
    except ValueError:
        click.echo(f"❌ Not found: {id_or_title}", err=True)


@pres.command()
@click.argument('id_or_title')
def archive(id_or_title: str):
    """Archive a presentation."""
    try:
        archive_presentation(id_or_title)
        click.echo(f"📦 Archived: {id_or_title}")
    except ValueError:
        click.echo(f"❌ Not found: {id_or_title}", err=True)


@pres.command()
def stats():
    """Show presentation statistics."""
    s = get_presentation_stats()
    click.echo("📊 Presentation Statistics\n")
    click.echo(f"Total: {s['total']}")
    click.echo(f"Todo: {s['todo']}")
    click.echo(f"Done: {s['done']}")
    click.echo(f"Archived: {s['archived']}")
