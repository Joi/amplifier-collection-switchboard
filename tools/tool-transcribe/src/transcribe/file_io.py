"""Defensive file I/O with retry logic for cloud sync issues."""

import json
import time
from pathlib import Path
from typing import Any

from .logger import get_logger

logger = get_logger(__name__)


def read_json_with_retry(path: Path, max_retries: int = 3, delay: float = 0.5) -> dict:
    """Read JSON file with retry logic for cloud sync issues.
    
    Args:
        path: Path to JSON file
        max_retries: Maximum retry attempts
        delay: Delay between retries in seconds
        
    Returns:
        Parsed JSON data
        
    Raises:
        FileNotFoundError: If file doesn't exist after retries
        json.JSONDecodeError: If file is not valid JSON
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, IOError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            raise
    
    raise last_error  # type: ignore


def write_json_with_retry(data: Any, path: Path, max_retries: int = 3, delay: float = 0.5) -> None:
    """Write JSON file with retry logic for cloud sync issues.
    
    Args:
        data: Data to write
        path: Path to JSON file
        max_retries: Maximum retry attempts
        delay: Delay between retries in seconds
        
    Raises:
        OSError: If write fails after retries
    """
    last_error = None
    
    for attempt in range(max_retries):
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return
        except (OSError, IOError) as e:
            last_error = e
            if attempt < max_retries - 1:
                time.sleep(delay)
                continue
            raise
    
    raise last_error  # type: ignore
