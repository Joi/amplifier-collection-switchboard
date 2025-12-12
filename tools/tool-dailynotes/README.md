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

## Calendar Sources

**Primary: Google Calendar API**
- Uses existing credentials from obs-dailynotes
- Set environment variables:
  - `GCAL_CREDS_PATH` - Path to Google OAuth credentials JSON
  - `GCAL_TOKEN_PATH` - Path to stored OAuth token

**Fallback: macOS Calendar (AppleScript)**
- Used automatically if Google credentials not available
- Works with any calendar synced to macOS Calendar app

## Output

Creates `~/switchboard/dailynote/YYYY-MM-DD.md` with:

- **Calendar**: Today's events (Google Calendar or macOS fallback)
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
- (All day) Company Holiday

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

## Configuration

To use Google Calendar (recommended), copy your existing credentials:

```bash
# These should already be set in your obs-dailynotes .env
export GCAL_CREDS_PATH=~/.config/google/credentials.json
export GCAL_TOKEN_PATH=~/.config/google/token.json
```

## Data Sources

- **Calendar**: Google Calendar API (primary) or macOS Calendar (fallback)
- **Projects**: `~/switchboard/amplifier/project-status.json`
- **Output**: `~/switchboard/dailynote/`

## Requirements

- Python 3.11+
- macOS (for AppleScript fallback)
- Obsidian with vault named "switchboard"
- Google Calendar credentials (optional, for Google API)
