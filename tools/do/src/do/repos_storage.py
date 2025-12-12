"""Storage for repository configuration."""

import json
from pathlib import Path
from datetime import datetime

# Default repos.json location
DEFAULT_REPOS_PATH = Path.home() / "switchboard" / "amplifier" / "repos.json"


def load_repos(repos_path: Path = DEFAULT_REPOS_PATH) -> dict:
    """Load repos configuration from JSON file."""
    if not repos_path.exists():
        return {
            "lastScanned": None,
            "lastSynced": None,
            "repos": []
        }
    
    with open(repos_path) as f:
        return json.load(f)


def save_repos(data: dict, repos_path: Path = DEFAULT_REPOS_PATH) -> None:
    """Save repos configuration to JSON file."""
    repos_path.parent.mkdir(parents=True, exist_ok=True)
    with open(repos_path, "w") as f:
        json.dump(data, f, indent=2)


def update_last_scanned(repos_path: Path = DEFAULT_REPOS_PATH) -> None:
    """Update the lastScanned timestamp."""
    data = load_repos(repos_path)
    data["lastScanned"] = datetime.now().isoformat() + "Z"
    save_repos(data, repos_path)


def update_last_synced(repos_path: Path = DEFAULT_REPOS_PATH) -> None:
    """Update the lastSynced timestamp."""
    data = load_repos(repos_path)
    data["lastSynced"] = datetime.now().isoformat() + "Z"
    save_repos(data, repos_path)
