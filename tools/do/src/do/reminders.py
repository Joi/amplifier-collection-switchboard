"""Apple Reminders integration using reminders-cli.

Uses the `reminders` CLI tool (https://github.com/keith/reminders-cli)
to interact with macOS Reminders app.
"""

import json
import re
import subprocess
from datetime import datetime
from pathlib import Path


def get_reminder_lists() -> list[str]:
    """Get all reminder list names.
    
    Returns:
        List of list names
    """
    try:
        result = subprocess.run(
            ['reminders', 'show-lists', '--format', 'json'],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        return []
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return []


def get_reminders_from_list(list_name: str, include_completed: bool = False) -> list[dict]:
    """Get reminders from a specific list.
    
    Args:
        list_name: Name of the reminders list
        include_completed: Whether to include completed reminders
        
    Returns:
        List of reminder dicts
    """
    try:
        cmd = ['reminders', 'show', list_name, '--format', 'json']
        if include_completed:
            cmd.append('--include-completed')
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return []
        
        items = json.loads(result.stdout)
        
        # Transform to our format
        reminders = []
        for item in items:
            tags = extract_tags(item.get('title', ''), item.get('notes', ''))
            reminders.append({
                'id': item.get('externalId', ''),
                'title': item.get('title', ''),
                'list': list_name,
                'notes': item.get('notes', ''),
                'due': item.get('dueDate'),
                'completed': item.get('isCompleted', False),
                'flagged': item.get('isFlagged', False),
                'priority': item.get('priority', 0),
                'tags': tags,
            })
        
        return reminders
        
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        return []


def extract_tags(title: str, notes: str = '') -> list[str]:
    """Extract hashtags from title and notes.
    
    Args:
        title: Reminder title
        notes: Reminder notes
        
    Returns:
        List of tags (without #)
    """
    text = f"{title} {notes}"
    pattern = r'#([A-Za-z0-9_-]+(?::[A-Za-z0-9_-]+)?)'
    matches = re.findall(pattern, text)
    return [m.lower() for m in matches]


def add_reminder(list_name: str, title: str, notes: str = '', due_date: str = '') -> bool:
    """Add a new reminder to a list.
    
    Args:
        list_name: Name of the list to add to
        title: Reminder title
        notes: Optional notes
        due_date: Optional due date (YYYY-MM-DD format)
        
    Returns:
        True if successful
    """
    try:
        cmd = ['reminders', 'add', list_name, title]
        
        if notes:
            cmd.extend(['--notes', notes])
        if due_date:
            cmd.extend(['--due-date', due_date])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0
        
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


def complete_reminder(list_name: str, title: str) -> bool:
    """Mark a reminder as complete.
    
    Args:
        list_name: Name of the list
        title: Reminder title to complete
        
    Returns:
        True if successful
    """
    try:
        result = subprocess.run(
            ['reminders', 'complete', list_name, title],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False


class RemindersCache:
    """Cache for reminders data to avoid repeated CLI calls."""
    
    def __init__(self, cache_path: Path):
        self.cache_path = cache_path
        self._data = None
    
    def load(self) -> dict:
        """Load cache from disk."""
        if self._data is not None:
            return self._data
        
        if self.cache_path.exists():
            try:
                self._data = json.loads(self.cache_path.read_text())
                return self._data
            except json.JSONDecodeError:
                pass
        
        return {'byList': {}, 'timestamp': None}
    
    def save(self, data: dict):
        """Save cache to disk."""
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.cache_path.write_text(json.dumps(data, indent=2))
        self._data = data
    
    def refresh(self) -> dict:
        """Refresh cache from Apple Reminders."""
        lists = get_reminder_lists()
        by_list = {}
        total = 0
        
        for list_name in lists:
            items = get_reminders_from_list(list_name, include_completed=True)
            by_list[list_name] = items
            total += len(items)
        
        data = {
            'timestamp': datetime.now().isoformat(),
            'totalReminders': total,
            'lists': lists,
            'byList': by_list,
        }
        
        self.save(data)
        return data
    
    def get_all_reminders(self) -> list[dict]:
        """Get all reminders from cache."""
        data = self.load()
        reminders = []
        
        for list_name, items in data.get('byList', {}).items():
            for item in items:
                # Ensure list is set
                item['list'] = list_name
                reminders.append(item)
        
        return reminders
    
    def get_cache_age_hours(self) -> float | None:
        """Get cache age in hours."""
        data = self.load()
        timestamp = data.get('timestamp')
        if not timestamp:
            return None
        
        try:
            cache_time = datetime.fromisoformat(timestamp)
            age = datetime.now() - cache_time
            return age.total_seconds() / 3600
        except (ValueError, TypeError):
            return None
