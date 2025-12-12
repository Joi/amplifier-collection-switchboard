"""Presentations service for managing presentations."""

from datetime import datetime

from .storage import (
    generate_id,
    load_presentations,
    save_presentations,
    validate_slides_url,
)


def add_presentation(
    url: str,
    title: str,
    deadline: str | None = None,
    priority: str = 'medium',
    notion_url: str | None = None,
    slack_url: str | None = None,
    tags: list[str] | None = None,
    notes: str = '',
    estimate: float | None = None,
) -> dict:
    """Add a new presentation.
    
    Args:
        url: Google Slides URL
        title: Presentation title
        deadline: Optional deadline (YYYY-MM-DD)
        priority: Priority level (low, medium, high, urgent)
        notion_url: Optional Notion brief URL
        slack_url: Optional Slack conversation URL
        tags: Optional list of tags
        notes: Optional notes
        estimate: Optional estimated hours
        
    Returns:
        Created presentation dict
    """
    if not validate_slides_url(url):
        raise ValueError('Invalid Google Slides URL. Expected: https://docs.google.com/presentation/d/...')
    
    if not title:
        raise ValueError('Title is required')
    
    data = load_presentations()
    pres_id = generate_id(data['nextId'])
    
    presentation = {
        'id': pres_id,
        'title': title,
        'url': url,
        'notionUrl': notion_url,
        'slackUrl': slack_url,
        'status': 'todo',
        'priority': priority,
        'deadline': deadline,
        'createdDate': datetime.now().isoformat(),
        'startedDate': None,
        'completedDate': None,
        'archivedDate': None,
        'tags': tags or [],
        'notes': notes,
        'reminderTaskId': None,
        'estimatedHours': estimate,
        'actualHours': 0,
    }
    
    data['presentations'].append(presentation)
    data['nextId'] += 1
    
    save_presentations(data)
    
    return presentation


def find_presentation(pres_id: str) -> tuple[dict, dict, int]:
    """Find presentation by ID.
    
    Returns:
        Tuple of (data, presentation, index)
    """
    data = load_presentations()
    
    for i, pres in enumerate(data['presentations']):
        if pres['id'] == pres_id:
            return data, pres, i
    
    raise ValueError(f"Presentation {pres_id} not found")


def start_presentation(pres_id: str) -> dict:
    """Mark presentation as started."""
    data, pres, _ = find_presentation(pres_id)
    
    if pres['status'] == 'done':
        raise ValueError('Presentation is already done')
    
    if not pres['startedDate']:
        pres['startedDate'] = datetime.now().isoformat()
    
    save_presentations(data)
    return pres


def complete_presentation(pres_id: str, hours: float | None = None, notes: str | None = None) -> dict:
    """Mark presentation as complete."""
    data, pres, _ = find_presentation(pres_id)
    
    if pres['status'] == 'done':
        raise ValueError('Presentation is already done')
    
    pres['status'] = 'done'
    pres['completedDate'] = datetime.now().isoformat()
    
    if hours is not None:
        pres['actualHours'] = hours
    
    if notes:
        date_str = datetime.now().strftime('%Y-%m-%d')
        existing = pres.get('notes', '')
        pres['notes'] = f"{existing}\n\nCompletion notes ({date_str}): {notes}".strip()
    
    save_presentations(data)
    return pres


def archive_presentation(pres_id: str) -> dict:
    """Archive presentation."""
    data, pres, _ = find_presentation(pres_id)
    
    pres['status'] = 'archived'
    pres['archivedDate'] = datetime.now().isoformat()
    
    save_presentations(data)
    return pres


def update_presentation(pres_id: str, **updates) -> dict:
    """Update presentation metadata."""
    data, pres, _ = find_presentation(pres_id)
    
    if 'title' in updates and updates['title']:
        pres['title'] = updates['title']
    if 'url' in updates and updates['url']:
        if not validate_slides_url(updates['url']):
            raise ValueError('Invalid Google Slides URL')
        pres['url'] = updates['url']
    if 'notion_url' in updates:
        pres['notionUrl'] = updates['notion_url']
    if 'slack_url' in updates:
        pres['slackUrl'] = updates['slack_url']
    if 'deadline' in updates:
        pres['deadline'] = updates['deadline']
    if 'priority' in updates and updates['priority']:
        pres['priority'] = updates['priority']
    if 'notes' in updates:
        pres['notes'] = updates['notes']
    if 'estimate' in updates:
        pres['estimatedHours'] = updates['estimate']
    if 'add_tag' in updates and updates['add_tag']:
        if updates['add_tag'] not in pres['tags']:
            pres['tags'].append(updates['add_tag'])
    if 'remove_tag' in updates and updates['remove_tag']:
        pres['tags'] = [t for t in pres['tags'] if t != updates['remove_tag']]
    
    save_presentations(data)
    return pres


def list_presentations(
    status: str | None = None,
    priority: str | None = None,
    tag: str | None = None,
    include_archived: bool = False,
) -> list[dict]:
    """List presentations with optional filters."""
    data = load_presentations()
    presentations = data['presentations']
    
    # Filter by status
    if status:
        presentations = [p for p in presentations if p['status'] == status]
    
    # Filter by priority
    if priority:
        presentations = [p for p in presentations if p['priority'] == priority]
    
    # Filter by tag
    if tag:
        presentations = [p for p in presentations if tag in p.get('tags', [])]
    
    # Exclude archived unless requested
    if not include_archived:
        presentations = [p for p in presentations if p['status'] != 'archived']
    
    # Sort: priority, then deadline, then status
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    status_order = {'todo': 0, 'done': 1, 'archived': 2}
    
    def sort_key(p):
        prio = priority_order.get(p['priority'], 99)
        deadline = p.get('deadline') or '9999-99-99'
        stat = status_order.get(p['status'], 99)
        return (prio, deadline, stat)
    
    presentations.sort(key=sort_key)
    
    return presentations


def get_stats() -> dict:
    """Get presentation statistics."""
    data = load_presentations()
    all_pres = data['presentations']
    
    return {
        'total': len(all_pres),
        'todo': len([p for p in all_pres if p['status'] == 'todo']),
        'done': len([p for p in all_pres if p['status'] == 'done']),
        'archived': len([p for p in all_pres if p['status'] == 'archived']),
        'in_progress': len([p for p in all_pres if p['status'] == 'todo' and p.get('startedDate')]),
        'planned': len([p for p in all_pres if p['status'] == 'todo' and not p.get('startedDate')]),
        'urgent': len([p for p in all_pres if p['priority'] == 'urgent' and p['status'] != 'archived']),
        'overdue': len([p for p in all_pres if p.get('deadline') and p['deadline'] < datetime.now().strftime('%Y-%m-%d') and p['status'] == 'todo']),
    }
