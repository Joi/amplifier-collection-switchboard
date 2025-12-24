"""CLI for web2md tool."""

import sys
from pathlib import Path

import click

from .logger import get_logger
from .fetcher import fetch_page
from .converter import html_to_markdown
from .validator import validate_content
from .image_handler import process_images
from .enhancer import enhance_markdown
from .organizer import save_page, get_domain_dir
from .indexer import generate_index
from .state import WebToMdState

logger = get_logger(__name__)

# Default output directory
DEFAULT_OUTPUT = Path.home() / "switchboard" / "sites"


def extract_title_from_markdown(markdown: str) -> str:
    """Extract title from markdown content."""
    lines = markdown.split("\n")
    for line in lines[:10]:
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def process_url(url: str, output_dir: Path, state: WebToMdState, no_images: bool = False) -> bool:
    """Process a single URL.
    
    Args:
        url: URL to process
        output_dir: Output directory for files
        state: State manager
        no_images: Skip downloading images
        
    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info(f"\n{'=' * 60}")
        logger.info(f"Processing: {url}")
        logger.info(f"{'=' * 60}")

        # Step 1: Fetch HTML and metadata
        logger.info("Step 1/6: Fetching page...")
        html, metadata = fetch_page(url)

        # Step 2: Convert to markdown
        logger.info("Step 2/6: Converting to markdown...")
        markdown = html_to_markdown(html, url)

        # Step 3: Validate content
        logger.info("Step 3/6: Validating content...")
        validation_result = validate_content(html, markdown, url)
        if not validation_result.is_valid:
            logger.error(f"✗ Content validation failed: {validation_result.reason}")
            logger.error(f"  Detected pattern: {validation_result.detected_pattern}")
            state.mark_failed(url, f"Validation failed: {validation_result.reason}")
            return False

        # Step 4: Process images
        domain_dir = get_domain_dir(url, output_dir)
        if not no_images:
            logger.info("Step 4/6: Processing images...")
            image_mappings = process_images(html, url, domain_dir)
        else:
            logger.info("Step 4/6: Skipping images...")
            image_mappings = []

        # Step 5: Enhance markdown
        logger.info("Step 5/6: Enhancing markdown...")
        metadata["title"] = extract_title_from_markdown(markdown)
        enhanced_markdown = enhance_markdown(markdown, metadata)

        # Update image references
        if image_mappings:
            for original_url, local_path in image_mappings:
                relative_path = f"images/{local_path.name}"
                enhanced_markdown = enhanced_markdown.replace(original_url, relative_path)

        # Step 6: Save the page
        logger.info("Step 6/6: Saving page...")
        saved_path = save_page(url, enhanced_markdown, output_dir)

        state.mark_processed(url)

        logger.info(f"✓ Successfully saved to: {saved_path}")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to process {url}: {e}")
        state.mark_failed(url, str(e))
        return False


@click.command()
@click.argument("urls", nargs=-1, required=True)
@click.option("--output", "-o", type=click.Path(path_type=Path), help="Output directory")
@click.option("--resume", is_flag=True, help="Resume from saved state")
@click.option("--no-images", is_flag=True, help="Skip downloading images")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
def cli(urls: tuple, output: Path | None, resume: bool, no_images: bool, verbose: bool):
    """Convert web pages to markdown with AI enhancement.

    Examples:
        web2md https://example.com
        web2md https://example.com https://another.com
        web2md https://example.com --output ./my-sites
        web2md https://example.com --resume
    """
    import logging
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Determine output directory
    output_dir = output or DEFAULT_OUTPUT
    logger.info(f"Output directory: {output_dir}")

    # Initialize state
    state_file = Path.home() / ".local" / "share" / "web2md" / "state.json"
    state = WebToMdState(state_file)

    # Process URLs
    urls_to_process = list(urls)
    processed_count = 0
    failed_count = 0
    skipped_count = 0

    for url_item in urls_to_process:
        if resume and state.is_processed(url_item):
            logger.info(f"Skipping (already processed): {url_item}")
            skipped_count += 1
            continue

        if process_url(url_item, output_dir, state, no_images=no_images):
            processed_count += 1
        else:
            failed_count += 1

    # Generate index
    if processed_count > 0 or (resume and state.processed_urls):
        logger.info("\nGenerating index...")
        index_content = generate_index(output_dir)
        index_path = output_dir / "index.md"

        with open(index_path, "w", encoding="utf-8") as f:
            f.write(index_content)

        logger.info(f"Index saved to: {index_path}")

    # Final statistics
    logger.info(f"\n{'=' * 60}")
    logger.info("Summary:")
    logger.info(f"  Processed: {processed_count}")
    logger.info(f"  Failed: {failed_count}")
    logger.info(f"  Skipped: {skipped_count}")

    stats = state.get_stats()
    logger.info(f"  Total in state: {stats['total']} ({stats['processed']} successful, {stats['failed']} failed)")
    logger.info(f"{'=' * 60}")

    if failed_count > 0:
        sys.exit(1)


def main():
    """Entry point for the CLI."""
    return cli()


if __name__ == "__main__":
    sys.exit(main())
