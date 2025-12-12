"""Storage for knowledge gap detection state."""

import json
from pathlib import Path
from datetime import datetime
from typing import Optional

# Default paths
DEFAULT_VAULT_PATH = Path.home() / "switchboard"
DEFAULT_DATA_PATH = Path.home() / ".data" / "knowledge_curator"


def ensure_data_dirs(data_path: Path = DEFAULT_DATA_PATH) -> None:
    """Ensure data directories exist."""
    (data_path / "gaps").mkdir(parents=True, exist_ok=True)
    (data_path / "gaps" / "history").mkdir(parents=True, exist_ok=True)
    (data_path / "staged" / "pending").mkdir(parents=True, exist_ok=True)
    (data_path / "staged" / "approved").mkdir(parents=True, exist_ok=True)
    (data_path / "staged" / "rejected").mkdir(parents=True, exist_ok=True)


def load_gaps(data_path: Path = DEFAULT_DATA_PATH) -> dict:
    """Load current gap report."""
    gaps_file = data_path / "gaps" / "current.json"
    if not gaps_file.exists():
        return {
            "vault": str(DEFAULT_VAULT_PATH),
            "domain": None,
            "generated_at": None,
            "gaps": [],
            "summary": {
                "total": 0,
                "by_type": {},
                "by_severity": {}
            }
        }
    
    with open(gaps_file) as f:
        return json.load(f)


def save_gaps(data: dict, data_path: Path = DEFAULT_DATA_PATH) -> None:
    """Save gap report."""
    ensure_data_dirs(data_path)
    gaps_file = data_path / "gaps" / "current.json"
    
    # Archive previous if exists
    if gaps_file.exists():
        old_data = json.loads(gaps_file.read_text())
        if old_data.get("generated_at"):
            timestamp = old_data["generated_at"].replace(":", "-").replace(".", "-")
            history_file = data_path / "gaps" / "history" / f"{timestamp}.json"
            history_file.write_text(json.dumps(old_data, indent=2))
    
    with open(gaps_file, "w") as f:
        json.dump(data, f, indent=2)


def load_dismissed(data_path: Path = DEFAULT_DATA_PATH) -> dict:
    """Load dismissed gaps."""
    dismissed_file = data_path / "gaps" / "dismissed.json"
    if not dismissed_file.exists():
        return {"dismissed": []}
    
    with open(dismissed_file) as f:
        return json.load(f)


def save_dismissed(data: dict, data_path: Path = DEFAULT_DATA_PATH) -> None:
    """Save dismissed gaps."""
    ensure_data_dirs(data_path)
    dismissed_file = data_path / "gaps" / "dismissed.json"
    with open(dismissed_file, "w") as f:
        json.dump(data, f, indent=2)


def dismiss_gap(gap_id: str, reason: str, data_path: Path = DEFAULT_DATA_PATH) -> bool:
    """Dismiss a gap with reason."""
    dismissed = load_dismissed(data_path)
    
    # Check if already dismissed
    for d in dismissed["dismissed"]:
        if d["id"] == gap_id:
            return False
    
    dismissed["dismissed"].append({
        "id": gap_id,
        "reason": reason,
        "dismissed_at": datetime.now().isoformat() + "Z"
    })
    
    save_dismissed(dismissed, data_path)
    return True


def is_dismissed(gap_id: str, data_path: Path = DEFAULT_DATA_PATH) -> bool:
    """Check if a gap is dismissed."""
    dismissed = load_dismissed(data_path)
    return any(d["id"] == gap_id for d in dismissed["dismissed"])
