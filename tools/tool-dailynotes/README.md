# tool-dailynotes

Thin wrapper around `~/obs-dailynotes` for unified CLI access.

## Status: Implemented (Wrapper)

This tool delegates to the Node.js obs-dailynotes for actual work.

## Usage

```bash
cd ~/amplifier-collection-switchboard/tools/tool-dailynotes

# Generate today's daily note
uv run dailynotes daily

# Manage presentations
uv run dailynotes pres

# Manage reading queue
uv run dailynotes read
```

## Requirements

- Node.js and npm
- `~/obs-dailynotes` installed with `npm install`
- Google Calendar credentials configured in obs-dailynotes

## How It Works

This is a thin Python wrapper that calls `npm run <command>` in `~/obs-dailynotes`.
All the actual logic lives in the Node.js tool.

## Why a Wrapper?

To provide a unified CLI interface across all switchboard tools, allowing
natural language interaction from a single Amplifier session without
switching directories or remembering different command formats.
