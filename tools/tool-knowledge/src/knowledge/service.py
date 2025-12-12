"""Knowledge gap detection service."""

import re
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from .storage import (
    DEFAULT_VAULT_PATH,
    DEFAULT_DATA_PATH,
    load_gaps,
    save_gaps,
    load_dismissed,
    is_dismissed,
)


def generate_gap_id(gap_type: str, location: str, term: str = "") -> str:
    """Generate a unique ID for a gap."""
    content = f"{gap_type}:{location}:{term}"
    return hashlib.sha256(content.encode()).hexdigest()[:8] + f":{gap_type}:{term[:20]}"


def find_markdown_files(vault_path: Path, domain: Optional[str] = None) -> list[Path]:
    """Find all markdown files in vault/domain."""
    search_path = vault_path / domain if domain else vault_path
    
    if not search_path.exists():
        return []
    
    # Skip certain directories
    skip_dirs = {".obsidian", ".git", "node_modules", ".trash", "templates"}
    
    files = []
    for f in search_path.rglob("*.md"):
        if any(skip in f.parts for skip in skip_dirs):
            continue
        files.append(f)
    
    return files


def extract_wikilinks(content: str) -> list[str]:
    """Extract [[wikilinks]] from content."""
    # Match [[link]] or [[link|alias]]
    pattern = r'\[\[([^\]|]+)(?:\|[^\]]+)?\]\]'
    return re.findall(pattern, content)


def detect_undefined_concepts(
    vault_path: Path,
    domain: Optional[str] = None,
    data_path: Path = DEFAULT_DATA_PATH
) -> list[dict]:
    """Detect terms mentioned but never defined.
    
    Looks for [[wikilinks]] that don't have corresponding files.
    """
    files = find_markdown_files(vault_path, domain)
    
    # Build set of existing file stems (without extension)
    existing = set()
    for f in files:
        # Normalize: lowercase, replace spaces
        stem = f.stem.lower().replace(" ", "-")
        existing.add(stem)
        existing.add(f.stem.lower())  # Also without dash replacement
    
    gaps = []
    
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        links = extract_wikilinks(content)
        
        for link in links:
            # Normalize link
            link_normalized = link.lower().replace(" ", "-")
            
            # Check if target exists
            if link_normalized not in existing and link.lower() not in existing:
                gap_id = generate_gap_id("undefined_concept", str(f), link)
                
                if is_dismissed(gap_id, data_path):
                    continue
                
                # Find line number
                line_num = 1
                for i, line in enumerate(content.splitlines(), 1):
                    if f"[[{link}" in line:
                        line_num = i
                        break
                
                gaps.append({
                    "id": gap_id,
                    "type": "undefined_concept",
                    "severity": "high",
                    "location": {
                        "file": str(f.relative_to(vault_path)),
                        "line": line_num,
                        "context": f"[[{link}]]"
                    },
                    "description": f"Concept '{link}' linked but no file exists",
                    "detected_at": datetime.now().isoformat() + "Z"
                })
    
    return gaps


def detect_stale_content(
    vault_path: Path,
    domain: Optional[str] = None,
    months: int = 6,
    data_path: Path = DEFAULT_DATA_PATH
) -> list[dict]:
    """Detect files not modified in N months."""
    files = find_markdown_files(vault_path, domain)
    cutoff = datetime.now() - timedelta(days=months * 30)
    
    gaps = []
    
    for f in files:
        mtime = datetime.fromtimestamp(f.stat().st_mtime)
        
        if mtime < cutoff:
            gap_id = generate_gap_id("stale_content", str(f), "")
            
            if is_dismissed(gap_id, data_path):
                continue
            
            age_days = (datetime.now() - mtime).days
            age_months = age_days // 30
            
            gaps.append({
                "id": gap_id,
                "type": "stale_content",
                "severity": "medium" if age_months < 12 else "high",
                "location": {
                    "file": str(f.relative_to(vault_path)),
                    "last_modified": mtime.isoformat()
                },
                "description": f"Not updated in {age_months} months",
                "detected_at": datetime.now().isoformat() + "Z"
            })
    
    return gaps


def detect_orphan_pages(
    vault_path: Path,
    domain: Optional[str] = None,
    data_path: Path = DEFAULT_DATA_PATH
) -> list[dict]:
    """Detect files not linked from anywhere."""
    files = find_markdown_files(vault_path, domain)
    
    # Build map of all links
    all_links = set()
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        links = extract_wikilinks(content)
        for link in links:
            all_links.add(link.lower())
            all_links.add(link.lower().replace(" ", "-"))
    
    gaps = []
    
    # Skip index/readme files
    skip_names = {"readme", "index", "start-here", "_index", "_structure"}
    
    for f in files:
        stem_lower = f.stem.lower()
        stem_dashed = stem_lower.replace(" ", "-")
        
        # Skip certain files
        if stem_lower in skip_names:
            continue
        
        # Check if file is linked from anywhere
        if stem_lower not in all_links and stem_dashed not in all_links:
            gap_id = generate_gap_id("orphan_page", str(f), "")
            
            if is_dismissed(gap_id, data_path):
                continue
            
            gaps.append({
                "id": gap_id,
                "type": "orphan_page",
                "severity": "low",
                "location": {
                    "file": str(f.relative_to(vault_path))
                },
                "description": "Not linked from any other file",
                "detected_at": datetime.now().isoformat() + "Z"
            })
    
    return gaps


def detect_thin_sections(
    vault_path: Path,
    domain: Optional[str] = None,
    min_words: int = 100,
    data_path: Path = DEFAULT_DATA_PATH
) -> list[dict]:
    """Detect files with very little content."""
    files = find_markdown_files(vault_path, domain)
    
    gaps = []
    
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        
        # Strip frontmatter
        if content.startswith("---"):
            end = content.find("---", 3)
            if end != -1:
                content = content[end + 3:]
        
        # Count words (rough)
        words = len(content.split())
        
        if words < min_words and words > 0:  # Skip empty files
            gap_id = generate_gap_id("thin_section", str(f), "")
            
            if is_dismissed(gap_id, data_path):
                continue
            
            gaps.append({
                "id": gap_id,
                "type": "thin_section",
                "severity": "low",
                "location": {
                    "file": str(f.relative_to(vault_path)),
                    "word_count": words
                },
                "description": f"Only {words} words (threshold: {min_words})",
                "detected_at": datetime.now().isoformat() + "Z"
            })
    
    return gaps


def run_gap_detection(
    vault_path: Path = DEFAULT_VAULT_PATH,
    domain: Optional[str] = None,
    data_path: Path = DEFAULT_DATA_PATH,
    stale_months: int = 6,
    min_words: int = 100
) -> dict:
    """Run full gap detection and return report."""
    
    all_gaps = []
    
    # Run all detectors
    all_gaps.extend(detect_undefined_concepts(vault_path, domain, data_path))
    all_gaps.extend(detect_stale_content(vault_path, domain, stale_months, data_path))
    all_gaps.extend(detect_orphan_pages(vault_path, domain, data_path))
    all_gaps.extend(detect_thin_sections(vault_path, domain, min_words, data_path))
    
    # Build summary
    by_type = defaultdict(int)
    by_severity = defaultdict(int)
    
    for gap in all_gaps:
        by_type[gap["type"]] += 1
        by_severity[gap["severity"]] += 1
    
    report = {
        "vault": str(vault_path),
        "domain": domain,
        "generated_at": datetime.now().isoformat() + "Z",
        "gaps": all_gaps,
        "summary": {
            "total": len(all_gaps),
            "by_type": dict(by_type),
            "by_severity": dict(by_severity)
        }
    }
    
    # Save report
    save_gaps(report, data_path)
    
    return report


def get_vault_stats(vault_path: Path = DEFAULT_VAULT_PATH, domain: Optional[str] = None) -> dict:
    """Get statistics about the vault."""
    files = find_markdown_files(vault_path, domain)
    
    total_words = 0
    total_links = 0
    
    for f in files:
        content = f.read_text(encoding="utf-8", errors="ignore")
        total_words += len(content.split())
        total_links += len(extract_wikilinks(content))
    
    return {
        "files": len(files),
        "words": total_words,
        "links": total_links,
        "vault": str(vault_path),
        "domain": domain
    }
