# tool-repos

Multi-repository sync and status.

## Status: Complete

## Functionality

- Check status across multiple git repositories
- Automated pull/push operations
- Generate repository dashboard
- Track uncommitted changes

## Commands

- `status` - Show status of all repos
- `sync` - Pull and push all repos
- `pull` - Pull all repos
- `push` - Push all repos
- `dashboard` - Generate markdown dashboard

## Data Source

Repository list: `~/switchboard/amplifier/repos.json`

## Source Migration

Port logic from: `~/obs-dailynotes/scripts/repos-sync.js`

## Dashboard Format

```markdown
## Repository Status

### Needs Attention
- repo-a: 3 uncommitted files
- repo-b: 2 commits behind remote

### Clean
- repo-c: Up to date
- repo-d: Up to date
```
