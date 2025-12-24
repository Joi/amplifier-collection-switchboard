"""State management - tracks processed URLs and supports resume."""

import json
from datetime import datetime
from pathlib import Path

from .logger import get_logger

logger = get_logger(__name__)


class WebToMdState:
    """Manages state for web_to_md conversion sessions."""

    def __init__(self, state_file: Path):
        """Initialize state manager.
        
        Args:
            state_file: Path to state persistence file
        """
        self.state_file = state_file
        self.processed_urls: set[str] = set()
        self.failed_urls: dict[str, str] = {}
        self.session_start = datetime.now().isoformat()
        self.last_update = None

        if state_file.exists():
            self.load()

    def load(self) -> None:
        """Load state from disk."""
        try:
            with open(self.state_file) as f:
                data = json.load(f)
                self.processed_urls = set(data.get("processed_urls", []))
                self.failed_urls = data.get("failed_urls", {})
                self.session_start = data.get("session_start", self.session_start)
                self.last_update = data.get("last_update")
                logger.info(f"Resumed state: {len(self.processed_urls)} processed, {len(self.failed_urls)} failed")
        except Exception as e:
            logger.warning(f"Could not load state: {e}")

    def save(self) -> None:
        """Save state to disk."""
        self.last_update = datetime.now().isoformat()
        data = {
            "processed_urls": list(self.processed_urls),
            "failed_urls": self.failed_urls,
            "session_start": self.session_start,
            "last_update": self.last_update,
        }

        self.state_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.state_file, "w") as f:
            json.dump(data, f, indent=2)

    def mark_processed(self, url: str) -> None:
        """Mark a URL as successfully processed."""
        self.processed_urls.add(url)
        self.failed_urls.pop(url, None)
        self.save()

    def mark_failed(self, url: str, error: str) -> None:
        """Mark a URL as failed with error message."""
        self.failed_urls[url] = error
        self.save()

    def is_processed(self, url: str) -> bool:
        """Check if a URL has already been processed."""
        return url in self.processed_urls

    def get_stats(self) -> dict[str, int]:
        """Get processing statistics."""
        return {
            "processed": len(self.processed_urls),
            "failed": len(self.failed_urls),
            "total": len(self.processed_urls) + len(self.failed_urls),
        }
