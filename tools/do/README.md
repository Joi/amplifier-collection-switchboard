# do

Unified personal workflow CLI.

## Usage

```bash
cd ~/amplifier-collection-switchboard/tools/do
uv run do <command>
```

## Commands

| Command | Description |
|---------|-------------|
| `do daily` | Generate daily note (wraps obs-dailynotes) |
| `do gtd inbox` | Show GTD inbox |
| `do gtd today` | Tasks due today |
| `do gtd add "Task"` | Add to inbox |
| `do pres list` | List presentations |
| `do pres add "Title"` | Add presentation |
| `do read list` | Reading queue |
| `do read add "url"` | Add to reading queue |
| `do knowledge gaps` | Run gap detection |
| `do knowledge stats` | Vault statistics |
| `do repos status` | Check all repos |
| `do repos sync` | Sync all repos |

## Install Globally

```bash
uv tool install .
# Then from anywhere:
do daily
do gtd inbox
```
