# tool-reading

Reading queue management for URLs and PDFs.

## Status: Planned

This tool will be implemented in Phase 3 (Milestone 3).

## Functionality

- Add URLs and PDFs to reading queue
- Priority-based sorting
- Track reading status (to-read, reading, read)
- Generate reading list dashboard

## Commands

- `list` - Show reading queue
- `add` - Add URL or PDF to queue
- `start` - Mark as currently reading
- `done` - Mark as read
- `priority` - Change item priority

## Priority Levels

- `urgent` - Time-sensitive
- `high` - Important for current work
- `medium` - General interest
- `low` - When time permits

## Source Migration

Port logic from: `~/obs-dailynotes/lib/reading.js`
