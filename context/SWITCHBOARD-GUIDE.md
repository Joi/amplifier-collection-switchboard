# Switchboard Vault Guide

The Switchboard is a personal knowledge management system built on Obsidian with 1100+ interconnected markdown files.

## Vault Structure

```
~/switchboard/
├── amplifier/              # Amplifier CLI project docs and configs
│   ├── project-status.json # Central project tracking
│   └── repos.json          # Git repository registry
├── chanoyu/                # Tea ceremony knowledge base
├── dailynote/              # Auto-generated daily notes (YYYY-MM-DD.md)
├── Docs/                   # Documentation and guides
│   └── Systems/            # System-specific documentation
├── GTD/                    # Getting Things Done workflow
│   ├── dashboard.md        # Main GTD dashboard
│   ├── inbox.md            # Capture inbox
│   ├── next-actions.md     # Active tasks
│   ├── waiting-for.md      # Delegated/blocked items
│   └── someday-maybe.md    # Future possibilities
├── people/                 # Person profiles (880 contacts)
└── people.index.json       # People index with emails
```

## File Conventions

### Frontmatter

Most files use YAML frontmatter:

```yaml
---
title: Page Title
created: 2025-01-01
updated: 2025-01-15
tags: [tag1, tag2]
aliases: [Alternative Name]
---
```

### Wikilinks

Internal references use Obsidian wikilinks:
- `[[Page Name]]` - Link to page
- `[[Page Name|Display Text]]` - Link with custom text
- `[[Page Name#Section]]` - Link to section

### Tags

Tags use hashtag format: `#project`, `#person`, `#concept`

## Key Data Files

### project-status.json

Central project registry with structure:

```json
{
  "version": "1.0",
  "lastUpdated": "2025-12-12T13:20:00Z",
  "projects": [
    {
      "id": "project-id",
      "title": "Project Title",
      "file": "PROJECT-FILE.md",
      "repoId": "github-repo-name",
      "status": "not-started|started|completed",
      "priority": "high|medium|low",
      "tags": ["tag1", "tag2"],
      "createdDate": "2025-01-01",
      "nextActions": ["Action 1", "Action 2"]
    }
  ]
}
```

### people.index.json

Contact index with structure:

```json
{
  "people": [
    {
      "name": "Full Name",
      "file": "people/Full Name.md",
      "email": "email@example.com",
      "tags": ["colleague", "friend"]
    }
  ]
}
```

## Daily Note Format

Daily notes follow this template:

```markdown
---
date: 2025-12-12
---

# Thursday, December 12, 2025

## Calendar

- 09:00 Meeting with [[Person Name]]
- 14:00 Project Review

## Projects

### Active
- [[Project A]] - Next: Complete feature X
- [[Project B]] - Waiting: Review from team

## Tasks

- [ ] Task from GTD inbox
- [ ] Follow up on email

## Notes

Space for daily notes and observations.
```

## GTD Integration

The GTD system syncs with Apple Reminders:

| Reminders List | GTD Category | File |
|---------------|--------------|------|
| Inbox | Capture | inbox.md |
| Next Actions | Active | next-actions.md |
| Waiting For | Blocked | waiting-for.md |
| Someday/Maybe | Future | someday-maybe.md |

## Chanoyu (Tea) Vault

The chanoyu subdirectory contains tea ceremony knowledge:
- Historical figures and schools
- Equipment and utensils
- Seasonal practices
- Aesthetic concepts

This content requires careful curation with verified sources.
