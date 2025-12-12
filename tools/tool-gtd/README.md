# tool-gtd

GTD workflow management with Apple Reminders integration.

## Status: Planned

This tool will be implemented in Phase 2 (Milestone 2).

## Functionality

- Sync with Apple Reminders via AppleScript
- Manage inbox, next-actions, waiting-for, someday-maybe
- Generate GTD dashboard
- Process inbox items
- Weekly review support

## Commands

- `inbox` - Show inbox items
- `next` - Show next actions
- `waiting` - Show waiting-for items
- `someday` - Show someday/maybe items
- `refresh` - Sync with Apple Reminders
- `add` - Add item to inbox
- `process` - Interactive inbox processing

## Source Migration

Port logic from: `~/obs-dailynotes/lib/gtd.js`

## Apple Reminders Integration

```bash
# Get reminders from a list
osascript -e 'tell application "Reminders" to get name of every reminder in list "Inbox"'

# Add a reminder
osascript -e 'tell application "Reminders" to make new reminder in list "Inbox" with properties {name:"Task name"}'
```
