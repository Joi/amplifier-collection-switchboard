"""GTD service for categorizing and managing tasks."""

from datetime import datetime, timedelta
from pathlib import Path

from .reminders import RemindersCache


def get_default_cache_path() -> Path:
    """Get default path for reminders cache."""
    return Path.home() / "switchboard" / "reminders" / "reminders_cache.json"


def categorize_reminders(reminders: list[dict]) -> dict:
    """Categorize reminders by GTD categories.
    
    Args:
        reminders: List of reminder dicts
        
    Returns:
        Dict with categorized lists: inbox, today, waiting, someday, active
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    inbox = []
    due_today = []
    waiting = []
    someday = []
    active = []
    
    for r in reminders:
        if r.get('completed'):
            continue
        
        tags = r.get('tags', [])
        
        # Inbox items
        if r.get('list') == 'Inbox':
            inbox.append(r)
            continue
        
        # Waiting for
        if 'waiting' in tags:
            waiting.append(r)
            continue
        
        # Someday/maybe
        if 'someday' in tags:
            someday.append(r)
            continue
        
        # Due today
        due_date = r.get('due')
        if due_date:
            try:
                due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                if due.date() == today.date():
                    due_today.append(r)
                    continue
            except (ValueError, TypeError):
                pass
        
        # Active (everything else)
        active.append(r)
    
    return {
        'inbox': inbox,
        'today': due_today,
        'waiting': waiting,
        'someday': someday,
        'active': active,
    }


def get_tasks_by_timeframe(reminders: list[dict]) -> dict:
    """Get tasks organized by timeframe.
    
    Args:
        reminders: List of reminder dicts
        
    Returns:
        Dict with: due_today, due_this_week, coming_up, no_date
    """
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    week_from_now = today + timedelta(days=7)
    month_from_now = today + timedelta(days=30)
    
    # Filter to active only
    active = [r for r in reminders if not r.get('completed') 
              and 'someday' not in r.get('tags', [])
              and 'waiting' not in r.get('tags', [])]
    
    due_today = []
    due_this_week = []
    coming_up = []
    no_date = []
    
    for r in active:
        due_date = r.get('due')
        if not due_date:
            no_date.append(r)
            continue
        
        try:
            due = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
            due_local = due.replace(tzinfo=None)
            
            if due_local.date() == today.date():
                due_today.append(r)
            elif due_local < week_from_now:
                due_this_week.append(r)
            elif due_local < month_from_now:
                coming_up.append(r)
            # Tasks due more than a month out go to no_date for simplicity
            else:
                no_date.append(r)
        except (ValueError, TypeError):
            no_date.append(r)
    
    # Sort by due date
    due_this_week.sort(key=lambda r: r.get('due', ''))
    coming_up.sort(key=lambda r: r.get('due', ''))
    
    return {
        'due_today': due_today,
        'due_this_week': due_this_week,
        'coming_up': coming_up,
        'no_date': no_date,
    }


def extract_project(tags: list[str]) -> str | None:
    """Extract project name from tags.
    
    Args:
        tags: List of tags
        
    Returns:
        Project name or None
    """
    for tag in tags:
        if tag.startswith('project:'):
            return tag.replace('project:', '')
    return None


def format_task(task: dict, show_due: bool = True, show_list: bool = False) -> str:
    """Format a task for display.
    
    Args:
        task: Task dict
        show_due: Whether to show due date
        show_list: Whether to show list name
        
    Returns:
        Formatted string
    """
    title = task.get('title', 'Untitled')
    
    # Priority indicator
    prefix = ''
    if '!!' in title:
        prefix = '⚠️  '
    elif '!' in title:
        prefix = '❗ '
    
    # Clean title (remove tags for display)
    import re
    clean_title = re.sub(r'#[A-Za-z0-9_:-]+', '', title).strip()
    
    parts = [f"- [ ] {prefix}{clean_title}"]
    
    # Due date
    if show_due and task.get('due'):
        try:
            due = datetime.fromisoformat(task['due'].replace('Z', '+00:00'))
            due_str = due.strftime('%b %d')
            parts.append(f"(due {due_str})")
        except (ValueError, TypeError):
            pass
    
    # List name (for shared lists)
    if show_list and task.get('list'):
        list_name = task['list']
        if '/' in list_name:
            person = list_name.split('/')[1].replace(' To Do', '')
            parts.append(f"({person})")
    
    return ' '.join(parts)


def get_stats(reminders: list[dict]) -> dict:
    """Get GTD statistics.
    
    Args:
        reminders: List of reminder dicts
        
    Returns:
        Dict with stats
    """
    active = [r for r in reminders if not r.get('completed')]
    
    categories = categorize_reminders(reminders)
    timeframe = get_tasks_by_timeframe(reminders)
    
    return {
        'total': len(reminders),
        'active': len(active),
        'completed': len(reminders) - len(active),
        'inbox': len(categories['inbox']),
        'today': len(timeframe['due_today']),
        'this_week': len(timeframe['due_this_week']),
        'waiting': len(categories['waiting']),
        'someday': len(categories['someday']),
    }
