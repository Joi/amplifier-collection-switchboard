"""CLI interface for reading queue tool.

Commands:
    reading list      List reading queue
    reading add       Add URL or PDF to queue
    reading start     Start reading
    reading finish    Mark as read
    reading archive   Archive item
    reading open      Open URL in browser or PDF
    reading stats     Show statistics
"""

import subprocess

import click

from .service import (
    add_reading,
    archive_reading,
    find_reading,
    finish_reading,
    get_stats,
    list_reading,
    start_reading,
    update_reading,
)


PRIORITY_EMOJI = {'urgent': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}
TYPE_EMOJI = {'url': '🔗', 'pdf': '📄'}


def format_item(item: dict) -> str:
    """Format reading item for display."""
    prio_emoji = PRIORITY_EMOJI.get(item['priority'], '')
    type_emoji = TYPE_EMOJI.get(item['type'], '')
    title = item['title']
    item_id = item['id']
    
    parts = [f"{prio_emoji} {type_emoji} [{item_id}] {title}"]
    
    if item.get('estimatedMinutes'):
        parts.append(f"(~{item['estimatedMinutes']}min)")
    
    return ' '.join(parts)


@click.group()
def cli():
    """Reading queue management for URLs and PDFs."""
    pass


@cli.command('list')
@click.option('--status', '-s', type=click.Choice(['to-read', 'reading', 'read', 'archived']), help='Filter by status')
@click.option('--priority', '-p', type=click.Choice(['urgent', 'high', 'medium', 'low']), help='Filter by priority')
@click.option('--type', 'item_type', type=click.Choice(['url', 'pdf']), help='Filter by type')
@click.option('--tag', '-t', help='Filter by tag')
@click.option('--all', 'show_all', is_flag=True, help='Include archived')
def list_cmd(status, priority, item_type, tag, show_all):
    """List reading queue."""
    items = list_reading(
        status=status,
        priority=priority,
        item_type=item_type,
        tag=tag,
        include_archived=show_all,
    )
    
    stats = get_stats()
    click.echo(f"📚 Reading Queue (To Read: {stats['to_read']} | Reading: {stats['reading']} | Read: {stats['read']})\n")
    
    if not items:
        click.echo("No items found.")
        return
    
    # Group by status
    by_status = {'reading': [], 'to-read': [], 'read': [], 'archived': []}
    for item in items:
        by_status.get(item['status'], []).append(item)
    
    groups = [
        ('📖 CURRENTLY READING', 'reading', by_status['reading']),
        ('📚 TO READ', 'to-read', by_status['to-read']),
        ('✅ READ', 'read', by_status['read']),
        ('📦 ARCHIVED', 'archived', by_status['archived']),
    ]
    
    for title, status_key, group_items in groups:
        if group_items:
            click.echo(f"{title}\n")
            for item in group_items:
                click.echo(format_item(item))
                if item.get('source') and item['source'] != 'manual':
                    click.echo(f"   Source: {item['source']}")
            click.echo()


@cli.command()
@click.argument('url_or_path')
@click.option('--title', '-t', required=True, help='Item title')
@click.option('--deadline', '-d', help='Deadline (YYYY-MM-DD)')
@click.option('--priority', '-p', default='medium',
              type=click.Choice(['urgent', 'high', 'medium', 'low']), help='Priority level')
@click.option('--tags', help='Comma-separated tags')
@click.option('--source', default='manual', help='Source (e.g., newsletter, recommendation)')
@click.option('--notes', help='Additional notes')
@click.option('--estimate', type=int, help='Estimated minutes to read')
def add(url_or_path, title, deadline, priority, tags, source, notes, estimate):
    """Add URL or PDF to reading queue."""
    try:
        tag_list = [t.strip() for t in tags.split(',')] if tags else None
        
        item = add_reading(
            input_str=url_or_path,
            title=title,
            deadline=deadline,
            priority=priority,
            source=source,
            tags=tag_list,
            notes=notes or '',
            estimate=estimate,
        )
        
        click.echo(f"\n✅ Added to reading queue!\n")
        click.echo(f"ID: {item['id']}")
        click.echo(f"Title: {item['title']}")
        click.echo(f"Type: {item['type']}")
        click.echo(f"\nRun: reading list")
        
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('item_id')
def start(item_id):
    """Start reading (opens URL or PDF)."""
    try:
        item = start_reading(item_id)
        click.echo(f"\n✅ Started: {item['title']}")
        
        # Open the item
        if item['type'] == 'url' and item.get('url'):
            subprocess.run(['open', item['url']], check=False)
            click.echo("   Opened in browser")
        elif item['type'] == 'pdf' and item.get('path'):
            subprocess.run(['open', item['path']], check=False)
            click.echo("   Opened PDF")
            
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('item_id')
@click.option('--notes', '-n', help='Reading notes')
def finish(item_id, notes):
    """Mark reading as finished."""
    try:
        item = finish_reading(item_id, notes=notes)
        click.echo(f"\n✅ Finished: {item['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('item_id')
def archive(item_id):
    """Archive reading item."""
    try:
        item = archive_reading(item_id)
        click.echo(f"\n✅ Archived: {item['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command('open')
@click.argument('item_id')
def open_cmd(item_id):
    """Open URL in browser or PDF in viewer."""
    try:
        _, item, _ = find_reading(item_id)
        
        if item['type'] == 'url' and item.get('url'):
            subprocess.run(['open', item['url']], check=False)
            click.echo(f"🔗 Opened: {item['title']}")
        elif item['type'] == 'pdf' and item.get('path'):
            subprocess.run(['open', item['path']], check=False)
            click.echo(f"📄 Opened: {item['title']}")
        else:
            click.echo("❌ No URL or path available", err=True)
            raise SystemExit(1)
            
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
@click.argument('item_id')
@click.option('--title', '-t', help='Update title')
@click.option('--url', help='Update URL')
@click.option('--deadline', '-d', help='Update deadline')
@click.option('--priority', '-p', type=click.Choice(['urgent', 'high', 'medium', 'low']), help='Update priority')
@click.option('--notes', help='Update notes')
@click.option('--estimate', type=int, help='Update estimated minutes')
@click.option('--add-tag', help='Add a tag')
@click.option('--remove-tag', help='Remove a tag')
def update(item_id, title, url, deadline, priority, notes, estimate, add_tag, remove_tag):
    """Update reading item metadata."""
    try:
        item = update_reading(
            item_id,
            title=title,
            url=url,
            deadline=deadline,
            priority=priority,
            notes=notes,
            estimate=estimate,
            add_tag=add_tag,
            remove_tag=remove_tag,
        )
        click.echo(f"\n✅ Updated: {item['title']}")
    except ValueError as e:
        click.echo(f"❌ Error: {e}", err=True)
        raise SystemExit(1)


@cli.command()
def stats():
    """Show reading queue statistics."""
    s = get_stats()
    
    click.echo("📚 Reading Queue Statistics\n")
    click.echo(f"Total: {s['total']}")
    click.echo(f"To Read: {s['to_read']}")
    click.echo(f"Currently Reading: {s['reading']}")
    click.echo(f"Read: {s['read']}")
    click.echo(f"Archived: {s['archived']}")
    click.echo()
    click.echo(f"🔗 URLs: {s['urls']}")
    click.echo(f"📄 PDFs: {s['pdfs']}")


if __name__ == "__main__":
    cli()
