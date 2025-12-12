# tool-dailynotes

Generate daily notes with calendar events and project status.

## Status: Planned

This tool will be implemented in Phase 1 (Milestone 1).

## Functionality

- Fetch calendar events via icalBuddy or AppleScript
- Read project status from `~/switchboard/amplifier/project-status.json`
- Generate Obsidian-compatible markdown
- Write to `~/switchboard/dailynote/YYYY-MM-DD.md`
- Open in Obsidian via URI

## Source Migration

Port logic from: `~/obs-dailynotes/lib/dailynotes.js`

## Implementation Notes

```python
# tools/tool-dailynotes/main.py
class DailyNotesTool:
    name = "dailynotes"
    description = "Generate daily note with calendar, projects, and tasks"
    
    async def execute(self, input: dict) -> ToolResult:
        # 1. Get today's date
        # 2. Fetch calendar events
        # 3. Read project-status.json
        # 4. Generate markdown from template
        # 5. Write to dailynote directory
        # 6. Return Obsidian URI
        pass
```
