# Amplifier Collection: Switchboard

Personal workflow tools consolidating daily notes, GTD, presentations, reading queue, knowledge curation, and repository management into a unified Amplifier collection.

## Overview

This collection migrates functionality from:
- `work` CLI (Node.js) - daily notes, GTD, presentations, reading
- `knowledge-curator` (Python) - vault gap detection and citation verification
- `chanoyu` scripts - tea ceremony knowledge management

## Installation

```bash
amplifier collection add https://github.com/joi/amplifier-collection-switchboard
```

## Components

### Profiles

| Profile | Description |
|---------|-------------|
| `switchboard` | Main profile with all workflow tools enabled |

### Agents

| Agent | Description |
|-------|-------------|
| `knowledge-curator` | Wikipedia-style editor for knowledge vault |
| `gtd-helper` | Natural language GTD workflow assistant |
| `daily-planner` | Morning planning and daily note assistant |

### Tools

| Tool | Description | Status |
|------|-------------|--------|
| `tool-dailynotes` | Generate daily notes with calendar and projects | Planned |
| `tool-gtd` | GTD workflow with Apple Reminders integration | Planned |
| `tool-presentations` | Track presentations with priorities/deadlines | Planned |
| `tool-reading` | Reading queue management | Planned |
| `tool-knowledge` | Knowledge vault operations and gap detection | Planned |
| `tool-repos` | Multi-repository sync and status | Planned |

## Usage Examples

```bash
# Generate today's daily note
amplifier run --profile switchboard "generate today's daily note"

# GTD operations
amplifier run "what's in my GTD inbox?"
amplifier run "add 'Review PR' to my inbox"

# Presentations
amplifier run "show my presentations due this week"

# Knowledge curation
amplifier run "run gap detection on chanoyu vault"
```

## Data Locations

This collection integrates with existing data stores:

| Data | Location | Format |
|------|----------|--------|
| Switchboard Vault | `~/switchboard/` | Obsidian Markdown |
| Project Registry | `~/switchboard/amplifier/project-status.json` | JSON |
| GTD System | `~/switchboard/GTD/` | Markdown |
| People Index | `~/switchboard/people.index.json` | JSON |
| Daily Notes | `~/switchboard/dailynote/` | Markdown |

## Development

See [WORKFLOW-MIGRATION-STRATEGY.md](~/switchboard/amplifier/WORKFLOW-MIGRATION-STRATEGY.md) for the full migration plan.

### Roadmap

1. **Phase 1**: Foundation - Collection structure, `tool-dailynotes`
2. **Phase 2**: GTD Integration - `tool-gtd` with Apple Reminders
3. **Phase 3**: Presentations & Reading - `tool-presentations`, `tool-reading`
4. **Phase 4**: Knowledge System - `tool-knowledge` with chanoyu
5. **Phase 5**: Repository & Integration - `tool-repos`, end-to-end testing

## License

MIT
