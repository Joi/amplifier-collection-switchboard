"""File organization - saves pages in domain-based directory structure."""

import re
import time
from pathlib import Path
from urllib.parse import urlparse

from .logger import get_logger

logger = get_logger(__name__)


def write_file(path: Path, content: str, encoding: str = "utf-8") -> None:
    """Write file with retry logic for cloud sync issues."""
    max_retries = 3
    retry_delay = 0.5

    for attempt in range(max_retries):
        try:
            with open(path, "w", encoding=encoding) as f:
                f.write(content)
            return
        except OSError as e:
            if e.errno == 5 and attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                raise


def save_page(url: str, content: str, base_dir: Path) -> Path:
    """Save markdown content to domain-organized directory.
    
    Args:
        url: Original URL of the page
        content: Markdown content to save
        base_dir: Base directory for saving
        
    Returns:
        Path to saved file
    """
    domain_dir = get_domain_dir(url, base_dir)
    filename = url_to_filename(url)
    file_path = domain_dir / filename

    domain_dir.mkdir(parents=True, exist_ok=True)
    write_file(file_path, content)

    logger.info(f"Saved {url} to {file_path}")
    return file_path


def get_domain_dir(url: str, base_dir: Path) -> Path:
    """Get domain-based directory for a URL.
    
    Args:
        url: URL to extract domain from
        base_dir: Base directory for sites
        
    Returns:
        Path to domain directory
    """
    parsed = urlparse(url)
    domain = parsed.netloc or "unknown"

    if domain.startswith("www."):
        domain = domain[4:]

    domain = domain.replace(":", "_")

    return base_dir / domain


def url_to_filename(url: str) -> str:
    """Convert URL to safe filename.
    
    Args:
        url: URL to convert
        
    Returns:
        Safe filename with .md extension
    """
    parsed = urlparse(url)

    if parsed.path and parsed.path != "/":
        path = parsed.path.strip("/")
        filename = path.replace("/", "_")
    else:
        filename = "index"

    if parsed.query:
        query_part = parsed.query[:20].replace("&", "_").replace("=", "_")
        filename = f"{filename}_{query_part}"

    filename = re.sub(r'[<>:"|?*]', "_", filename)

    if "." in filename:
        filename = filename.rsplit(".", 1)[0]

    if len(filename) > 100:
        filename = filename[:100]

    if not filename or filename == "_":
        filename = "page"

    return f"{filename}.md"
