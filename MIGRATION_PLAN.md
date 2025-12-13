# Tool Migration Plan

Migration from `~/amplifier` (old system) to `~/amp-sb` (switchboard collection).

## Current State

| Location | Purpose | Status |
|----------|---------|--------|
| `~/amplifier` | Old scenarios/tools | Archive |
| `~/micro-blog` | Notion→micro.blog | Active, standalone |
| `~/amp-sb` | New `do` CLI | Active |

## High Priority

### 1. transcribe
**Source:** `~/amplifier/scenarios/transcribe`
**Target:** `do transcribe <url>`
**Purpose:** YouTube/audio → searchable transcript with timestamps

Features to migrate:
- YouTube audio download (yt-dlp)
- Whisper API transcription
- Timestamp formatting
- AI summaries/key quotes

### 2. blog_writer  
**Source:** `~/amplifier/scenarios/blog_writer`
**Target:** `do blog write <idea.md>`
**Purpose:** Transform rough ideas into blog posts matching your voice

Features to migrate:
- Style extraction from existing writings
- Multi-stage drafting pipeline
- Review/refinement loops

### 3. micro-blog integration
**Source:** `~/micro-blog`
**Target:** `do blog export` / `do blog publish`
**Purpose:** Notion→markdown→micro.blog pipeline

Features to integrate:
- `notion_blog/` - Export posts from Notion
- `scripts/import_posts.py` - Publish to micro.blog via Micropub
- Support for tea.ito.com (English) and cha.ito.com (Japanese)

## Medium Priority

### 4. web_to_md
**Source:** `~/amplifier/scenarios/web_to_md`
**Target:** `do web2md <url>`
**Purpose:** Convert web pages to clean markdown

Features:
- Paywall detection
- Image downloading
- AI markdown cleanup

## Skip (Archive Only)

| Tool | Reason |
|------|--------|
| article_illustrator | No longer needed |
| blog_poster | Superseded by micro-blog |
| ideas_tracker | Old amplifier-specific |
| project_planner | Superseded by new amplifier agents |
| smart_decomposer | Superseded by new amplifier agents |
| tips_synthesizer | Low use |
| knowledge_curator | Overlaps with `do knowledge` |
| tools/*.py | Old amplifier utilities |

## Proposed `do` Commands

```bash
# Transcription
do transcribe https://youtube.com/watch?v=...
do transcribe podcast.mp3

# Blogging
do blog write idea.md                    # AI draft from idea
do blog export --blog tea-journey        # Notion → markdown
do blog publish --dir content/english    # markdown → micro.blog

# Web capture
do web2md https://example.com/article
```

## Migration Order

1. **transcribe** - Independent, high value
2. **blog commands** - Integrate micro-blog repo
3. **web2md** - Nice to have

## Notes

- Keep `~/micro-blog` as-is for now, add `do` wrappers
- `~/amplifier` stays for reference, stop active use
- Each migrated tool becomes a Python module in `~/amp-sb/tools/`
