# tool-reading

Reading queue management for URLs and PDFs.

## Status: Implemented

## Installation

```bash
cd tools/tool-reading
uv run reading --help
```

## Commands

```bash
# List reading queue
reading list
reading list --status to-read
reading list --type url
reading list --priority high
reading list --all  # Include archived

# Add to queue
reading add "https://example.com/article" --title "Article Title"
reading add "/path/to/paper.pdf" --title "Paper Title" --estimate 30
reading add URL --title "Title" --priority high --tags "ai,research"

# Reading flow
reading start <id>    # Start reading (opens URL/PDF)
reading finish <id>   # Mark as read
reading archive <id>  # Archive

# Update metadata
reading update <id> --priority urgent
reading update <id> --add-tag "important"

# Open without changing status
reading open <id>

# Statistics
reading stats
```

## Data Format

Reading items stored in `~/switchboard/data/reading-queue.json`:

```json
{
  "id": "read-20251212-001",
  "type": "url",
  "title": "Article Title",
  "url": "https://example.com/article",
  "path": null,
  "status": "to-read",
  "priority": "medium",
  "deadline": null,
  "source": "manual",
  "tags": ["ai", "research"],
  "estimatedMinutes": 15
}
```

## Item Types

- `url` 🔗 - Web articles, blog posts
- `pdf` 📄 - PDF documents, papers

## Status Flow

```
to-read → reading → read → archived
```

## Priority Levels

- `urgent` 🔴 - Time-sensitive
- `high` 🟠 - Important for current work
- `medium` 🟡 - General interest (default)
- `low` 🟢 - When time permits

## Requirements

- Python 3.11+
- macOS (uses `open` command for URLs/PDFs)
