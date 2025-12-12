# tool-gtd

GTD workflow management with Apple Reminders integration.

## Status: Implemented

## Installation

```bash
cd tools/tool-gtd
uv run gtd --help
```

Or install globally:
```bash
uv tool install .
gtd inbox
```

## Commands

```bash
# View tasks by category
gtd inbox           # Items needing processing
gtd today           # Tasks due today
gtd next            # Next actions (today + this week + priority)
gtd waiting         # Items waiting on others (#waiting tag)
gtd someday         # Someday/maybe items (#someday tag)

# Management
gtd refresh         # Sync cache from Apple Reminders
gtd add "Task"      # Add item to Inbox
gtd stats           # Show GTD statistics
gtd dash            # Generate GTD dashboard markdown
```

## Examples

```bash
# Add a task to inbox
gtd add "Review PR for authentication feature"
gtd add "Call dentist" --due 2025-01-15

# Check what's due
gtd today
gtd next -n 5

# Weekly review
gtd refresh
gtd inbox
gtd waiting
gtd someday
```

## GTD Categories

Tasks are categorized by tags:
- **#waiting** - Items waiting on someone else
- **#someday** - Someday/maybe items (not actionable now)
- **#project:name** - Group tasks by project

## Apple Reminders Integration

Uses [reminders-cli](https://github.com/keith/reminders-cli) to sync with macOS Reminders.

Install with: `brew install keith/formulae/reminders-cli`

The tool reads from a JSON cache at `~/switchboard/reminders/reminders_cache.json` 
(compatible with existing obs-dailynotes cache).

## Dashboard Output

The `gtd dash` command generates `~/switchboard/GTD Dashboard.md`:

```markdown
# GTD Dashboard

*Updated: 2025-12-12 16:00*

## 🎯 Today's Next Actions

- [ ] Review PR for auth feature (due Dec 12)
- [ ] Call client about project

## 📥 Inbox (5 items)

- [ ] Schedule dentist appointment
- [ ] Read article on AI governance
...
```

## Data Location

- **Cache**: `~/switchboard/reminders/reminders_cache.json`
- **Dashboard**: `~/switchboard/GTD Dashboard.md`

## Requirements

- macOS
- Python 3.11+
- [reminders-cli](https://github.com/keith/reminders-cli) (`brew install keith/formulae/reminders-cli`)
