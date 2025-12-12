# tool-presentations

Track presentations with priorities and deadlines.

## Status: Implemented

## Installation

```bash
cd tools/tool-presentations
uv run presentations --help
```

## Commands

```bash
# List presentations
presentations list
presentations list --status todo
presentations list --priority urgent
presentations list --all  # Include archived

# Add presentation
presentations add "https://docs.google.com/presentation/d/..." --title "My Talk"
presentations add URL --title "Talk" --deadline 2025-01-15 --priority high
presentations add URL --title "Talk" --notion "https://notion.so/..." --slack "https://slack.com/..."

# Manage status
presentations start <id>       # Mark as started
presentations complete <id>    # Mark as done
presentations archive <id>     # Archive

# Update metadata
presentations update <id> --priority urgent
presentations update <id> --deadline 2025-02-01
presentations update <id> --add-tag "conference"

# Open in browser
presentations open <id>           # Open slides
presentations open <id> --notion  # Open Notion brief
presentations open <id> --slack   # Open Slack thread

# Statistics
presentations stats
```

## Data Format

Presentations are stored in `~/switchboard/data/presentations.json`:

```json
{
  "id": "pres-20251212-001",
  "title": "My Talk",
  "url": "https://docs.google.com/presentation/d/...",
  "notionUrl": "https://notion.so/...",
  "slackUrl": null,
  "status": "todo",
  "priority": "high",
  "deadline": "2025-01-15",
  "tags": ["conference"],
  "estimatedHours": 4,
  "actualHours": 0
}
```

## Priority Levels

- `urgent` 🔴 - Immediate attention required
- `high` 🟠 - Important, due soon
- `medium` 🟡 - Standard priority (default)
- `low` 🟢 - When time permits

## Status Flow

```
todo → done → archived
  ↓
archived (can archive from any status)
```

## Requirements

- Python 3.11+
- Google Slides URLs only (validation enforced)
