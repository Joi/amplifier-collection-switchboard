"""Reading queue service for managing reading items."""

from datetime import datetime

from .storage import (
    detect_type,
    generate_id,
    load_reading_queue,
    save_reading_queue,
)


def add_reading(
    input_str: str,
    title: str,
    deadline: str | None = None,
    priority: str = 'medium',
    source: str = 'manual',
    tags: list[str] | None = None,
    notes: str = '',
    estimate: int | None = None,
    item_type: str | None = None,
) -> dict:
    """Add a new reading item.
    
    Args:
        input_str: URL or file path
        title: Item title
        deadline: Optional deadline (YYYY-MM-DD)
        priority: Priority level (low, medium, high, urgent)
        source: Source of the item
        tags: Optional list of tags
        notes: Optional notes
        estimate: Optional estimated minutes
        item_type: Optional type override (url, pdf)
        
    Returns:
        Created item dict
    """
    if not title:
        raise ValueError('Title is required')
    
    data = load_reading_queue()
    item_id = generate_id(data['nextId'])
    detected_type = item_type or detect_type(input_str)
    
    item = {
        'id': item_id,
        'type': detected_type,
        'title': title,
        'url': input_str if detected_type == 'url' else None,
        'path': input_str if detected_type == 'pdf' else None,
        'status': 'to-read',
        'priority': priority,
        'deadline': deadline,
        'addedDate': datetime.now().isoformat(),
        'startedDate': None,
        'finishedDate': None,
        'archivedDate': None,
        'source': source,
        'tags': tags or [],
        'notes': notes,
        'estimatedMinutes': estimate,
        'reminderTaskId': None,
    }
    
    data['items'].append(item)
    data['nextId'] += 1
    
    save_reading_queue(data)
    
    return item


def find_reading(item_id: str) -> tuple[dict, dict, int]:
    """Find reading item by ID.
    
    Returns:
        Tuple of (data, item, index)
    """
    data = load_reading_queue()
    
    for i, item in enumerate(data['items']):
        if item['id'] == item_id:
            return data, item, i
    
    raise ValueError(f"Reading item {item_id} not found")


def start_reading(item_id: str) -> dict:
    """Start reading (to-read -> reading)."""
    data, item, _ = find_reading(item_id)
    
    if item['status'] != 'to-read':
        raise ValueError(f"Cannot start item in '{item['status']}' status")
    
    item['status'] = 'reading'
    item['startedDate'] = datetime.now().isoformat()
    
    save_reading_queue(data)
    return item


def finish_reading(item_id: str, notes: str | None = None) -> dict:
    """Finish reading (reading -> read)."""
    data, item, _ = find_reading(item_id)
    
    if item['status'] != 'reading':
        raise ValueError(f"Cannot finish item in '{item['status']}' status. Start it first.")
    
    item['status'] = 'read'
    item['finishedDate'] = datetime.now().isoformat()
    
    if notes:
        date_str = datetime.now().strftime('%Y-%m-%d')
        existing = item.get('notes', '')
        item['notes'] = f"{existing}\n\nReading notes ({date_str}): {notes}".strip()
    
    save_reading_queue(data)
    return item


def archive_reading(item_id: str) -> dict:
    """Archive reading item."""
    data, item, _ = find_reading(item_id)
    
    item['status'] = 'archived'
    item['archivedDate'] = datetime.now().isoformat()
    
    save_reading_queue(data)
    return item


def update_reading(item_id: str, **updates) -> dict:
    """Update reading item metadata."""
    data, item, _ = find_reading(item_id)
    
    if 'title' in updates and updates['title']:
        item['title'] = updates['title']
    if 'url' in updates and updates['url']:
        item['url'] = updates['url']
    if 'deadline' in updates:
        item['deadline'] = updates['deadline']
    if 'priority' in updates and updates['priority']:
        item['priority'] = updates['priority']
    if 'notes' in updates:
        item['notes'] = updates['notes']
    if 'estimate' in updates:
        item['estimatedMinutes'] = updates['estimate']
    if 'add_tag' in updates and updates['add_tag']:
        if updates['add_tag'] not in item['tags']:
            item['tags'].append(updates['add_tag'])
    if 'remove_tag' in updates and updates['remove_tag']:
        item['tags'] = [t for t in item['tags'] if t != updates['remove_tag']]
    
    save_reading_queue(data)
    return item


def list_reading(
    status: str | None = None,
    priority: str | None = None,
    item_type: str | None = None,
    tag: str | None = None,
    include_archived: bool = False,
) -> list[dict]:
    """List reading items with optional filters."""
    data = load_reading_queue()
    items = data['items']
    
    if status:
        items = [i for i in items if i['status'] == status]
    
    if priority:
        items = [i for i in items if i['priority'] == priority]
    
    if item_type:
        items = [i for i in items if i['type'] == item_type]
    
    if tag:
        items = [i for i in items if tag in i.get('tags', [])]
    
    if not include_archived:
        items = [i for i in items if i['status'] != 'archived']
    
    # Sort: priority, then deadline, then status
    priority_order = {'urgent': 0, 'high': 1, 'medium': 2, 'low': 3}
    status_order = {'reading': 0, 'to-read': 1, 'read': 2, 'archived': 3}
    
    def sort_key(item):
        prio = priority_order.get(item['priority'], 99)
        deadline = item.get('deadline') or '9999-99-99'
        stat = status_order.get(item['status'], 99)
        return (prio, deadline, stat)
    
    items.sort(key=sort_key)
    
    return items


def get_stats() -> dict:
    """Get reading queue statistics."""
    data = load_reading_queue()
    all_items = data['items']
    
    return {
        'total': len(all_items),
        'to_read': len([i for i in all_items if i['status'] == 'to-read']),
        'reading': len([i for i in all_items if i['status'] == 'reading']),
        'read': len([i for i in all_items if i['status'] == 'read']),
        'archived': len([i for i in all_items if i['status'] == 'archived']),
        'urls': len([i for i in all_items if i['type'] == 'url' and i['status'] != 'archived']),
        'pdfs': len([i for i in all_items if i['type'] == 'pdf' and i['status'] != 'archived']),
    }
