# tool-dailynotes

Generate daily notes with calendar events and project status.

## Status: Implemented

## Installation

```bash
cd tools/tool-dailynotes
uv run dailynotes
```

Or install globally:
```bash
uv tool install .
dailynotes
```

## Usage

```bash
# Generate today's note and open in Obsidian
dailynotes

# Generate without opening
dailynotes --no-open

# Preview what would be generated
dailynotes --dry-run

# Use different vault name
dailynotes --vault my-vault
```

## Output

Creates `~/switchboard/dailynote/YYYY-MM-DD.md` with:

- **Calendar**: Today's events from macOS Calendar app
- **Projects**: Active projects from `project-status.json` with next actions
- **Tasks**: Link to GTD Dashboard
- **Notes**: Empty section for daily observations

## Example Output

```markdown
---
date: 2025-12-12
---

# Friday, December 12, 2025

## Calendar

- 09:00-09:30 Team Standup
- 14:00-15:00 Project Review (Zoom)

## Projects

### Active
- 🟠 **[[amplifier/POC-THEBOOK.md|The Practice of Change 2.0]]**
  - Next: Develop detailed biographical timeline
- 🟡 **[[amplifier/KNOWLEDGE-CURATOR.md|Knowledge Curator Agent]]**
  - Next: Integrate paper-search MCP

### Planned (High Priority)
- [[amplifier/WORKFLOW-MIGRATION-STRATEGY.md|Workflow Migration]]

## Tasks

[[GTD Dashboard]]

## Notes

```

## Data Sources

- **Calendar**: macOS Calendar app via AppleScript
- **Projects**: `~/switchboard/amplifier/project-status.json`
- **Output**: `~/switchboard/dailynote/`

## Requirements

- macOS (uses AppleScript for calendar)
- Python 3.11+
- Obsidian with vault named "switchboard"
