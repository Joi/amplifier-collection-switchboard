"""CLI interface for presentations tool.

Commands:
    presentations list      List presentations
    presentations add       Add new presentation
    presentations start     Mark as started
    presentations complete  Mark as complete
    presentations archive   Archive presentation
    presentations update    Update metadata
    presentations open      Open in browser
    presentations stats     Show statistics
"""

import subprocess
from datetime import datetime

import click

from .service import (
    add_presentation,
    archive_presentation,
    complete_presentation,
    find_presentation,
    get_stats,
    list_presentations,
    start_presentation,
    update_presentation,
)


PRIORITY_EMOJI = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}


def format_presentation(pres: dict, verbose: bool = False) -> str:
    """Format presentation for display."""
    emoji = PRIORITY_EMOJI.get(pres['priority'], '')
    title = pres['title']
    pres_id = pres['id']
    
    parts = [f"{emoji} [{pres_id}] {title}"]
    
    if pres.get('deadline'):
        deadline = pres['deadline']
        try:
            days = (datetime.fromisoformat(deadline) - datetime.now()).days
            if pres['status'] == 'done':
                parts.append(f"(completed)")
            elif days < 0:
                parts.append(f"(OVERDUE)")
            else:
                parts.append(f"(due in {days} days)")
        except ValueError:
            parts.append(f"(due {deadline})")
    
    return ' '.join(parts)


@click.group()
def cli():
    """Track presentations with priorities and deadlines."""
    pass


@cli.command('list')
@click.option('--status', '-s', type=click.Choice(['todo', 'done', 'archived']), help='Filter by status')
@click.option('--priority', '-p', type=click.Choice(['urgent', 'high', 'medium', 'low']), help='Filter by priority')
@click.option('--tag', '-t', help='Filter by tag')
@click.option('--all', 'show_all', is_flag=True, help='Include archived')
def list_cmd(status, priority, tag, show_all):
    """List presentations."""
    presentations = list_presentations(
        status=status,
        priority=priority,
        tag=tag,
        include_archived=show_all,
    )
    
    stats = get_stats()
    click.echo(f"📊 Presentations (Total: {stats['total']} | Todo: {stats['todo']} | Done: {stats['done']})\n")
    
    if not presentations:
        click.echo("No presentations found.")
        return
    
    # Group by status
    by_status = {'todo': [], 'done': [], 'archived': []}
    for p in presentations:
        by_status.get(p['status'], []).append(p)
    
    groups = [
        ('📋 TO DO', 'todo', by_status['todo']),
        ('✅ DONE', 'done', by_status['done']),
        ('📦 ARCHIVED', 'archived', by_status['archived']),
    ]
    
    for title, status_key, items in groups:
        if items:
            click.echo(f"{title}\n")
            for p in items:
                click.echo(format_presentation(p))
                if p.get('notionUrl'):
                    click.echo("   📝 Notion brief available")
                if p.get('slackUrl'):
                    click.echo("   💬 Slack conversation available")
            click.echo()


@cli.command()
@click.argument('url')
@click.option('--title', '-t', required=True, help='Presentation title')
@click.option('--deadline', '-d', help='Deadline (YYYY-MM-DD)')
@click.option('--priority', '-p', default='medium', 
              type=click.Choice(['urgent', 'high', 'medium', 'low']), help='Priority level')
@click.option('--notion', help='Notion brief URL')
@click.option('--slack', help='Slack conversation URL')
@click.option('--tags', help='Comma-separated tags')
@click.option('--notes', help='Additional notes')
@click.option('--estimate', type=float, help='Estimated hours')
def add(url, title, deadline, priority, notion, slack, tags, notes, estimate):
    """Add a new presentation."""
    try:
        tag_list = [t.strip() for t in tags.split(',')] if tags else None
        
        pres = add_presentation(
            url=url,
            title=title,
            deadline=deadline,
            priority=priority,
            notion_url=notion,
            slack_url=slack,
            tags=tag_list,
            notes=notes or '',
            estimate=estimate,
        )
        
        click.echo(f"\n✅ Presentation created!\n")
        click.echo(f"ID: {pres['id']}")
        click.echo(f"Title: {pres['title']}")
        click.echo(f"Status: {pres['status']}")
        if deadline:
            click.echo(f"Deadline: {deadline}")
        click.echo(f"\nRun: presentations list")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('pres_id')
def start(pres_id):
    """Start working on a presentation."""
    try:
        pres = start_presentation(pres_id)
        click.echo(f"\n✅ Started: {pres['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('pres_id')
@click.option('--hours', type=float, help='Actual hours spent')
@click.option('--notes', help='Completion notes')
def complete(pres_id, hours, notes):
    """Mark presentation as complete."""
    try:
        pres = complete_presentation(pres_id, hours=hours, notes=notes)
        click.echo(f"\n✅ Completed: {pres['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('pres_id')
def archive(pres_id):
    """Archive a presentation."""
    try:
        pres = archive_presentation(pres_id)
        click.echo(f"\n✅ Archived: {pres['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('pres_id')
@click.option('--title', '-t', help='Update title')
@click.option('--url', help='Update Google Slides URL')
@click.option('--deadline', '-d', help='Update deadline')
@click.option('--priority', '-p', type=click.Choice(['urgent', 'high', 'medium', 'low']), help='Update priority')
@click.option('--notion', help='Update Notion URL')
@click.option('--slack', help='Update Slack URL')
@click.option('--notes', help='Update notes')
@click.option('--estimate', type=float, help='Update estimated hours')
@click.option('--add-tag', help='Add a tag')
@click.option('--remove-tag', help='Remove a tag')
def update(pres_id, title, url, deadline, priority, notion, slack, notes, estimate, add_tag, remove_tag):
    """Update presentation metadata."""
    try:
        pres = update_presentation(
            pres_id,
            title=title,
            url=url,
            deadline=deadline,
            priority=priority,
            notion_url=notion,
            slack_url=slack,
            notes=notes,
            estimate=estimate,
            add_tag=add_tag,
            remove_tag=remove_tag,
        )
        click.echo(f"\n✅ Updated: {pres['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command('open')
@click.argument('pres_id')
@click.option('--notion', is_flag=True, help='Open Notion brief instead')
@click.option('--slack', is_flag=True, help='Open Slack conversation instead')
def open_cmd(pres_id, notion, slack):
    """Open presentation in browser."""
    try:
        _, pres, _ = find_presentation(pres_id)
        
        if notion:
            if not pres.get('notionUrl'):
                click.echo("❌ No Notion URL set", err=True)
                raise SystemExit(1)
            url = pres['notionUrl']
            click.echo(f"📝 Opening Notion brief: {pres['title']}")
        elif slack:
            if not pres.get('slackUrl'):
                click.echo("❌ No Slack URL set", err=True)
                raise SystemExit(1)
            url = pres['slackUrl']
            click.echo(f"💬 Opening Slack: {pres['title']}")
        else:
            url = pres['url']
            click.echo(f"🔗 Opening slides: {pres['title']}")
        
        subprocess.run(['open', url], check=False)
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
def stats():
    """Show presentation statistics."""
    s = get_stats()
    
    click.echo("📊 Presentation Statistics\n")
    click.echo(f"Total: {s['total']}")
    click.echo(f"Todo: {s['todo']} ({s['in_progress']} in progress, {s['planned']} planned)")
    click.echo(f"Done: {s['done']}")
    click.echo(f"Archived: {s['archived']}")
    click.echo()
    click.echo(f"🔴 Urgent: {s['urgent']}")
    if s['overdue'] > 0:
        click.echo(f"⚠️  Overdue: {s['overdue']}")


if __name__ == "__main__":
    cli()
