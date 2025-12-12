"""GTD Dashboard generator.

Generates an Obsidian-compatible markdown dashboard showing
GTD tasks organized by category and timeframe.
"""

from datetime import datetime

from .reminders import RemindersCache
from .service import (
    categorize_reminders,
    extract_project,
    format_task,
    get_stats,
    get_tasks_by_timeframe,
)


def generate_dashboard(reminders: list[dict], cache: RemindersCache) -> str:
    """Generate GTD dashboard markdown.
    
    Args:
        reminders: List of reminder dicts
        cache: RemindersCache instance for metadata
        
    Returns:
        Markdown string
    """
    now = datetime.now()
    categories = categorize_reminders(reminders)
    timeframe = get_tasks_by_timeframe(reminders)
    stats = get_stats(reminders)
    
    lines = [
        "# GTD Dashboard",
        "",
        f"*Updated: {now.strftime('%Y-%m-%d %H:%M')}*",
    ]
    
    # Cache age warning
    age = cache.get_cache_age_hours()
    if age is not None:
        if age > 24:
            lines.append(f"*⚠️ Cache is {age/24:.1f} days old - run `gtd refresh`*")
        elif age > 2:
            lines.append(f"*Cache is {age:.1f} hours old*")
    
    lines.append("")
    
    # Today's Next Actions
    lines.append("## 🎯 Today's Next Actions")
    lines.append("")
    
    next_actions = []
    next_actions.extend(timeframe['due_today'])
    next_actions.extend(timeframe['due_this_week'][:2])
    # Add priority items
    for task in timeframe['no_date']:
        if '!' in task.get('title', ''):
            next_actions.append(task)
    next_actions = next_actions[:5]
    
    if next_actions:
        for task in next_actions:
            lines.append(format_task(task, show_list=True))
    else:
        lines.append("*No urgent actions - check Inbox or This Week*")
    lines.append("")
    
    # This Week
    if timeframe['due_this_week']:
        lines.append(f"## 📋 This Week ({len(timeframe['due_this_week'])} tasks)")
        lines.append("")
        for task in timeframe['due_this_week'][:10]:
            lines.append(format_task(task, show_list=True))
        if len(timeframe['due_this_week']) > 10:
            lines.append(f"*... and {len(timeframe['due_this_week']) - 10} more*")
        lines.append("")
    
    # Inbox
    lines.append(f"## 📥 Inbox ({len(categories['inbox'])} items)")
    lines.append("")
    
    if categories['inbox']:
        for task in categories['inbox']:
            lines.append(format_task(task))
        lines.append("")
        lines.append("*Process during weekly review: Add dates or #someday tag*")
    else:
        lines.append("*Inbox empty - nice!*")
    lines.append("")
    
    # Coming Up (2-4 weeks)
    if timeframe['coming_up']:
        lines.append(f"## 📅 Coming Up ({len(timeframe['coming_up'])} tasks)")
        lines.append("")
        for task in timeframe['coming_up'][:10]:
            lines.append(format_task(task))
        if len(timeframe['coming_up']) > 10:
            lines.append(f"*... and {len(timeframe['coming_up']) - 10} more*")
        lines.append("")
    
    # Waiting For
    if categories['waiting']:
        lines.append(f"## ⏸️ Waiting For ({len(categories['waiting'])} items)")
        lines.append("")
        for task in categories['waiting']:
            lines.append(format_task(task, show_list=True))
        lines.append("")
    
    # Active Projects
    projects = {}
    active = [r for r in reminders if not r.get('completed') and 'someday' not in r.get('tags', [])]
    
    for task in active:
        project = extract_project(task.get('tags', []))
        if project:
            if project not in projects:
                projects[project] = []
            projects[project].append(task)
    
    if projects:
        lines.append("## 🗂️ Active Projects")
        lines.append("")
        for name, tasks in sorted(projects.items(), key=lambda x: -len(x[1])):
            lines.append(f"### #project/{name} ({len(tasks)} tasks)")
            lines.append("")
    
    # Someday/Maybe
    if categories['someday']:
        lines.append(f"## 💭 Someday/Maybe ({len(categories['someday'])} items)")
        lines.append("")
        lines.append("*Review during weekly review - not actionable right now*")
        lines.append("")
        for task in categories['someday'][:5]:
            lines.append(format_task(task))
        if len(categories['someday']) > 5:
            lines.append(f"*... and {len(categories['someday']) - 5} more*")
        lines.append("")
    
    # Stats
    lines.append("---")
    lines.append("")
    lines.append("## 📊 Stats")
    lines.append("")
    lines.append(f"- **Total active**: {stats['active']} tasks")
    lines.append(f"- **Inbox**: {stats['inbox']} items")
    lines.append(f"- **Someday/Maybe**: {stats['someday']} tasks")
    lines.append("")
    
    return '\n'.join(lines)
