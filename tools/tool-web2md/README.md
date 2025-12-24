# Web2MD

Convert web pages to clean, organized markdown files.

## Features

- **Fetch & Convert** - Downloads pages and converts HTML to markdown
- **Paywall Detection** - Automatically detects paywalled content
- **Image Handling** - Downloads and saves images locally
- **Domain Organization** - Organizes pages by domain
- **Resume Support** - Can resume interrupted sessions
- **Index Generation** - Creates an index of all converted pages

## Installation

```bash
cd ~/amp-sb/tools/tool-web2md
uv sync
```

## Usage

Via `do` CLI (recommended):
```bash
do web2md https://example.com/article
do web2md https://example.com --no-images
```

Direct:
```bash
web2md https://example.com
web2md https://example.com https://another.com
web2md https://example.com --output ./my-sites
web2md https://example.com --resume
```

## Options

- `--output, -o` - Custom output directory
- `--resume` - Resume from saved state (skip already processed)
- `--no-images` - Skip downloading images
- `--verbose, -v` - Show detailed output

## Output

Pages are saved to `~/switchboard/sites/`:

```
~/switchboard/sites/
├── index.md              # Auto-generated index
├── example.com/
│   ├── article.md        # Converted page
│   └── images/           # Downloaded images
│       └── img_abc123.jpg
└── another-site.org/
    └── post.md
```

Each markdown file includes YAML frontmatter with:
- Original URL
- Title
- Domain
- Retrieval timestamp

## Requirements

- Python 3.11+
- No API keys required (basic enhancement only)
