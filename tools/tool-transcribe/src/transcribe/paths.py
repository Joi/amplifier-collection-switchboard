"""Path configuration for transcribe tool."""

from pathlib import Path


class Paths:
    """Manage paths for transcribe output."""
    
    def __init__(self):
        # Default to ~/switchboard/transcripts for content
        self.content_dir = Path.home() / "switchboard" / "transcripts"
        # Data/state goes to .data in the tool directory or home
        self.data_dir = Path.home() / ".local" / "share" / "transcribe"
    
    def get_all_content_paths(self) -> list[Path]:
        """Get content directories."""
        return [self.content_dir]


# Global instance
paths = Paths()
