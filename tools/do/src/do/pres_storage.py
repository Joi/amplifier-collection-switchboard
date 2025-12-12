"""Storage for presentations data.

Reads/writes presentations.json from switchboard data directory.
Compatible with existing obs-dailynotes format.
"""

import json
import os
from datetime import datetime
from pathlib import Path


def get_data_path() -> Path:
    """Get path to presentations data file."""
    # Check env var first (same as obs-dailynotes)
    data_dir = os.environ.get('SWITCHBOARD_DATA_PATH')
    if data_dir:
        data_dir = os.path.expanduser(data_dir)
    else:
        data_dir = Path.home() / "switchboard" / "data"
    
    return Path(data_dir) / "presentations.json"


def load_presentations() -> dict:
    """Load presentations from JSON file.
    
    Returns:
        Dict with 'version', 'presentations', 'nextId'
    """
    path = get_data_path()
    
    if not path.exists():
        # Create initial structure
        initial = {
            'version': '1.0',
            'presentations': [],
            'nextId': 1
        }
        save_presentations(initial)
        return initial
    
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError:
        return {'version': '1.0', 'presentations': [], 'nextId': 1}


def save_presentations(data: dict):
    """Save presentations to JSON file."""
    path = get_data_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2) + '\n')


def generate_id(next_id: int) -> str:
    """Generate unique presentation ID."""
    date_str = datetime.now().strftime('%Y%m%d')
    id_num = str(next_id).zfill(3)
    return f"pres-{date_str}-{id_num}"


def validate_slides_url(url: str) -> bool:
    """Validate Google Slides URL."""
    return 'docs.google.com/presentation' in url
