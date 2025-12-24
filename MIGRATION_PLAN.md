# Tool Migration Plan

Migration from `~/amplifier` (old system) to `~/amp-sb` (switchboard collection).

## Current State

| Location | Purpose | Status |
|----------|---------|--------|
| `~/amplifier` | Old scenarios/tools | Archive |
| `~/micro-blog` | Notion→micro.blog | Active, standalone |
| `~/amp-sb` | New `do` CLI | Active |

## Completed ✓

### 1. transcribe ✓
**Location:** `~/amp-sb/tools/tool-transcribe`
**Command:** `do transcribe <url>`
**Purpose:** YouTube/audio → searchable transcript with timestamps

Features migrated:
- YouTube audio download (yt-dlp)
- Whisper API transcription
- Timestamp formatting with clickable links
- AI summaries/key quotes (Claude)
- Resume support for interrupted sessions
- Index generation

### 2. web2md ✓
**Location:** `~/amp-sb/tools/tool-web2md`
**Command:** `do web2md <url>`
**Purpose:** Convert web pages to clean markdown

Features migrated:
- Paywall/auth wall detection
- Image downloading
- Domain-based organization
- YAML frontmatter
- Resume support
- Index generation

### ~~3. micro-blog integration~~ → ONE-TIME TASK
**Status:** Do via Claude directly, not as `do` command
**Reason:** One-time Notion→micro.blog migration, then writing directly to micro.blog going forward

## Not Migrating (Archive Only)

| Tool | Reason |
|------|--------|
| blog_writer | Low use, can use Claude directly |
| article_illustrator | No longer needed |
| blog_poster | Superseded by micro-blog |
| ideas_tracker | Old amplifier-specific |
| project_planner | Superseded by new amplifier agents |
| smart_decomposer | Superseded by new amplifier agents |
| tips_synthesizer | Low use |
| knowledge_curator | Overlaps with `do knowledge` |
| tools/*.py | Old amplifier utilities |

## Usage

```bash
# Transcription
do transcribe https://youtube.com/watch?v=...
do transcribe podcast.mp3
do transcribe video1.mp4 --resume

# Web capture
do web2md https://example.com/article
do web2md https://site1.com https://site2.com --no-images
```

## Output Locations

| Tool | Output |
|------|--------|
| transcribe | `~/switchboard/transcripts/` |
| web2md | `~/switchboard/sites/` |

## Notes

- `~/amplifier` can now be archived - no longer needed for active use
- Each tool is a standalone Python module in `~/amp-sb/tools/`
- Tools use local dependencies (no amplifier imports)
