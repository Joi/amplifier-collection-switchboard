# tool-presentations

Track presentations with priorities and deadlines.

## Status: Planned

This tool will be implemented in Phase 3 (Milestone 3).

## Functionality

- Add new presentations with topic, deadline, priority
- Track presentation status (added, started, completed)
- Store Notion/Slack URLs
- List presentations by priority or deadline
- Mark presentations as started/completed

## Commands

- `list` - Show all presentations
- `add` - Add new presentation
- `start` - Mark as started
- `complete` - Mark as completed
- `due` - Show presentations due soon

## Data Storage

Presentations stored in JSON format in switchboard vault.

## Source Migration

Port logic from: `~/obs-dailynotes/lib/presentations.js`
