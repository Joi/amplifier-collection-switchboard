"""Storage for reading queue data.

Reads/writes reading-queue.json from switchboard data directory.
Compatible with existing obs-dailynotes format.
"""

import json
import os
from datetime import datetime
from pathlib import Path


def get_data_path() -> Path:
    """Get path to reading queue data file."""
    data_dir = os.environ.get('SWITCHBOARD_DATA_PATH')
    if data_dir:
        data_dir = os.path.expanduser(data_dir)
    else:
        data_dir = Path.home() / "switchboard" / "data"
    
    return Path(data_dir) / "reading-queue.json"


def load_reading_queue() -> dict:
    """Load reading queue from JSON file.
    
    Returns:
        Dict with 'version', 'items', 'nextId'
    """
    path = get_data_path()
    
    if not path.exists():
        initial = {
            'version': '1.0',
            'items': [],
            'nextId': 1
        }
        save_reading_queue(initial)
        return initial
    
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {'version': '1.0', 'items': [], 'nextId': 1}


def save_reading_queue(data: dict):
    """Save reading queue to JSON file."""
    path = get_data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def generate_id(next_id: int) -> str:
    """Generate unique reading ID."""
    date_str = datetime.now().strftime('%Y%m%d')
    id_num = str(next_id).zfill(3)
    return f"read-{date_str}-{id_num}"


def detect_type(input_str: str) -> str:
    """Detect if input is URL or file path."""
    if input_str.startswith('http://') or input_str.startswith('https://'):
        return 'url'
    if input_str.endswith('.pdf'):
        return 'pdf'
    if '://' in input_str or 'www.' in input_str:
        return 'url'
    return 'pdf'
