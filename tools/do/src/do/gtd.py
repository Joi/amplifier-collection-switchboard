"""GTD workflow management with Apple Reminders."""

from pathlib import Path

import click

from .reminders import RemindersCache, add_reminder
from .service import (
    categorize_reminders,
    format_task,
    get_default_cache_path,
    get_stats,
    get_tasks_by_timeframe,
)


def get_cache() -> RemindersCache:
    """Get reminders cache instance."""
    return RemindersCache(get_default_cache_path())


@click.group()
def gtd():
    """GTD workflow management with Apple Reminders."""
    pass


@gtd.command()
@click.option('--all', 'show_all', is_flag=True, help='Include completed items')
def inbox(show_all: bool):
    """Show inbox items that need processing."""
    cache = get_cache()
    reminders = cache.get_all_reminders()
    
    inbox_items = [r for r in reminders 
                   if r.get('list') == 'Inbox' 
                   and (show_all or not r.get('completed'))]
    
    if not inbox_items:
        click.echo("📥 Inbox is empty - nice!")
        return
    
    click.echo(f"📥 Inbox ({len(inbox_items)} items)\n")
    
    for task in inbox_items:
        click.echo(format_task(task))


@gtd.command()
def today():
    """Show tasks due today."""
    cache = get_cache()
    reminders = cache.get_all_reminders()
    
    timeframe = get_tasks_by_timeframe(reminders)
    due_today = timeframe['due_today']
    
    if not due_today:
        click.echo("🎯 No tasks due today")
        return
    
    click.echo(f"🎯 Due Today ({len(due_today)} tasks)\n")
    
    for task in due_today:
        click.echo(format_task(task, show_due=False, show_list=True))


@gtd.command()
@click.option('--limit', '-n', default=10, help='Number of items to show')
def next(limit: int):
    """Show next actions (active tasks)."""
    cache = get_cache()
    reminders = cache.get_all_reminders()
    
    timeframe = get_tasks_by_timeframe(reminders)
    
    next_actions = []
    next_actions.extend(timeframe['due_today'])
    next_actions.extend(timeframe['due_this_week'])
    
    for task in timeframe['no_date']:
        if '!' in task.get('title', ''):
            next_actions.append(task)
    
    seen = set()
    unique = []
    for task in next_actions:
        task_id = task.get('id') or task.get('title')
        if task_id not in seen:
            seen.add(task_id)
            unique.append(task)
    
    if not unique:
        click.echo("✅ No immediate next actions")
        return
    
    click.echo(f"📋 Next Actions ({len(unique)} tasks)\n")
    
    for task in unique[:limit]:
        click.echo(format_task(task, show_list=True))
    
    if len(unique) > limit:
        click.echo(f"\n... and {len(unique) - limit} more")


@gtd.command()
def waiting():
    """Show items waiting on others."""
    cache = get_cache()
    reminders = cache.get_all_reminders()
    
    categories = categorize_reminders(reminders)
    waiting_items = categories['waiting']
    
    if not waiting_items:
        click.echo("⏸️  Nothing in waiting-for")
        return
    
    click.echo(f"⏸️  Waiting For ({len(waiting_items)} items)\n")
    
    for task in waiting_items:
        click.echo(format_task(task, show_list=True))


@gtd.command()
@click.option('--limit', '-n', default=10, help='Number of items to show')
def someday(limit: int):
    """Show someday/maybe items."""
    cache = get_cache()
    reminders = cache.get_all_reminders()
    
    categories = categorize_reminders(reminders)
    someday_items = categories['someday']
    
    if not someday_items:
        click.echo("💭 No someday/maybe items")
        return
    
    click.echo(f"💭 Someday/Maybe ({len(someday_items)} items)\n")
    
    for task in someday_items[:limit]:
        click.echo(format_task(task))
    
    if len(someday_items) > limit:
        click.echo(f"\n... and {len(someday_items) - limit} more")


@gtd.command()
def refresh():
    """Refresh cache from Apple Reminders."""
    click.echo("📥 Refreshing from Apple Reminders...")
    
    cache = get_cache()
    
    try:
        data = cache.refresh()
        total = data.get('totalReminders', 0)
        lists = len(data.get('lists', []))
        
        inbox_items = data.get('byList', {}).get('Inbox', [])
        inbox_active = len([i for i in inbox_items if not i.get('completed')])
        
        click.echo(f"✅ Cache updated")
        click.echo(f"   Total reminders: {total}")
        click.echo(f"   Lists: {lists}")
        click.echo(f"   Inbox (active): {inbox_active}")
        
    except Exception as e:
        click.echo(f"❌ Error refreshing: {e}", err=True)
        raise SystemExit(1)


@gtd.command()
@click.argument('title')
@click.option('--notes', '-n', default='', help='Additional notes')
@click.option('--due', '-d', default='', help='Due date (YYYY-MM-DD)')
def add(title: str, notes: str, due: str):
    """Add item to Inbox."""
    success = add_reminder('Inbox', title, notes=notes, due_date=due)
    
    if success:
        click.echo(f"✅ Added to Inbox: {title}")
    else:
        click.echo("❌ Failed to add reminder", err=True)
        raise SystemExit(1)


@gtd.command()
def stats():
    """Show GTD statistics."""
    cache = get_cache()
    reminders = cache.get_all_reminders()
    
    s = get_stats(reminders)
    
    click.echo("📊 GTD Statistics\n")
    click.echo(f"Total reminders: {s['total']}")
    click.echo(f"Active: {s['active']}")
    click.echo(f"Completed: {s['completed']}")
    click.echo()
    click.echo(f"📥 Inbox: {s['inbox']}")
    click.echo(f"🎯 Due today: {s['today']}")
    click.echo(f"📋 This week: {s['this_week']}")
    click.echo(f"⏸️  Waiting: {s['waiting']}")
    click.echo(f"💭 Someday: {s['someday']}")
