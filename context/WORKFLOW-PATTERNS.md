# Workflow Patterns

Common patterns for interacting with Switchboard tools and data.

## Daily Workflow

### Morning Routine

1. Generate daily note with calendar and active projects
2. Review GTD inbox - process or defer items
3. Check high-priority presentations
4. Review reading queue for time-sensitive items

### End of Day

1. Capture new items to GTD inbox
2. Update project status if milestones reached
3. Add interesting URLs to reading queue

## GTD Patterns

### Inbox Processing

For each inbox item, decide:
- **Do it** (< 2 minutes) → Complete immediately
- **Delegate** → Move to Waiting For with person/date
- **Defer** → Move to Next Actions with context
- **Someday** → Move to Someday/Maybe
- **Delete** → Remove if not actionable

### Context Tags

Tasks use context prefixes:
- `@computer` - Requires computer
- `@phone` - Phone calls to make
- `@errands` - Out of office tasks
- `@home` - Home-specific tasks
- `@waiting` - Blocked on someone else

### Weekly Review

1. Process inbox to zero
2. Review Next Actions - still relevant?
3. Review Waiting For - follow up needed?
4. Review Someday/Maybe - promote any items?
5. Review projects - next actions defined?

## Presentation Tracking

### Priority Levels

- **P1**: Due within 1 week, high stakes
- **P2**: Due within 2 weeks, important
- **P3**: Due within 1 month, standard
- **P4**: No deadline, nice to have

### Presentation Lifecycle

1. **Added** - Initial capture with topic and deadline
2. **Started** - Work begun, Notion/Slack links added
3. **Completed** - Delivered, notes captured

## Reading Queue

### Sources

- URLs from browsing
- PDFs from email/downloads
- Papers from research
- Books (physical/digital)

### Priority Assignment

- **Urgent**: Time-sensitive, deadline-driven
- **High**: Important for current projects
- **Medium**: General interest, valuable
- **Low**: Nice to have, when time permits

## Knowledge Curation

### Gap Detection

Scan knowledge vault for:
- **Undefined concepts** - Terms mentioned but not explained
- **Stale content** - Not updated in 6+ months
- **Orphan pages** - No incoming links
- **Missing citations** - Claims without sources

### Citation Verification

For each claim needing verification:
1. Search academic sources (Semantic Scholar, arXiv)
2. Search authoritative web sources
3. Add citation in Obsidian format: `[^1]`
4. Stage changes for human review

### Content Addition Rules

- Only add content when explicitly requested
- Always stage for human review
- Preserve existing formatting
- Add to appropriate location in vault structure

## Repository Management

### Sync Operations

- **Status check** - Show uncommitted changes, ahead/behind
- **Pull** - Update from remote
- **Push** - Push local commits
- **Full sync** - Pull then push all repos

### Dashboard Generation

Generate markdown dashboard showing:
- Repos with uncommitted changes
- Repos ahead/behind remote
- Recent commit activity
- Repos needing attention
