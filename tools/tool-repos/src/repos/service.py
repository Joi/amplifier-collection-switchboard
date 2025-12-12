"""Repository operations service."""

import subprocess
from pathlib import Path
from datetime import datetime
from typing import Optional

from .storage import load_repos, save_repos, DEFAULT_REPOS_PATH


def run_git(repo_path: Path, *args) -> tuple[str, str, int]:
    """Run a git command in the specified repo."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", "Command timed out", 1
    except Exception as e:
        return "", str(e), 1


def get_repo_status(repo: dict) -> dict:
    """Get current status of a repository."""
    local_path = Path(repo["localPath"])
    
    if not local_path.exists():
        return {
            "exists": False,
            "error": "Directory not found"
        }
    
    # Get current branch
    branch, _, rc = run_git(local_path, "branch", "--show-current")
    if rc != 0:
        return {"exists": True, "error": "Not a git repository"}
    
    # Get local commit
    local_commit, _, _ = run_git(local_path, "rev-parse", "--short", "HEAD")
    
    # Check working tree status
    status_out, _, _ = run_git(local_path, "status", "--porcelain")
    is_clean = len(status_out) == 0
    uncommitted_count = len(status_out.splitlines()) if status_out else 0
    
    # Fetch to update remote refs (silent)
    run_git(local_path, "fetch", "--quiet")
    
    # Check ahead/behind
    ahead_behind, _, _ = run_git(local_path, "rev-list", "--left-right", "--count", f"HEAD...origin/{branch}")
    ahead, behind = 0, 0
    if ahead_behind:
        parts = ahead_behind.split()
        if len(parts) == 2:
            ahead, behind = int(parts[0]), int(parts[1])
    
    # Determine sync status
    if ahead > 0 and behind > 0:
        sync_status = "diverged"
    elif ahead > 0:
        sync_status = "ahead"
    elif behind > 0:
        sync_status = "behind"
    else:
        sync_status = "synced"
    
    return {
        "exists": True,
        "branch": branch,
        "localCommit": local_commit,
        "workingTreeClean": is_clean,
        "uncommittedCount": uncommitted_count,
        "ahead": ahead,
        "behind": behind,
        "syncStatus": sync_status
    }


def check_all_repos(repos_path: Path = DEFAULT_REPOS_PATH) -> list[dict]:
    """Check status of all repositories."""
    data = load_repos(repos_path)
    results = []
    
    for repo in data.get("repos", []):
        if repo.get("archived"):
            results.append({
                "id": repo["id"],
                "name": repo["name"],
                "archived": True,
                "reason": repo.get("archivedReason", "")
            })
            continue
        
        status = get_repo_status(repo)
        results.append({
            "id": repo["id"],
            "name": repo["name"],
            "localPath": repo["localPath"],
            "githubRepo": repo.get("githubRepo"),
            **status
        })
        
        # Update repo data
        if status.get("exists") and not status.get("error"):
            repo["currentBranch"] = status["branch"]
            repo["localCommit"] = status["localCommit"]
            repo["workingTreeClean"] = status["workingTreeClean"]
            repo["syncStatus"] = status["syncStatus"]
            repo["syncDetails"] = {
                "ahead": status["ahead"],
                "behind": status["behind"]
            }
            repo["lastChecked"] = datetime.now().isoformat() + "Z"
    
    # Save updated data
    data["lastScanned"] = datetime.now().isoformat() + "Z"
    save_repos(data, repos_path)
    
    return results


def pull_repo(repo_path: Path) -> tuple[bool, str]:
    """Pull changes for a repository."""
    stdout, stderr, rc = run_git(repo_path, "pull", "--ff-only")
    if rc == 0:
        return True, stdout or "Already up to date"
    return False, stderr or "Pull failed"


def push_repo(repo_path: Path) -> tuple[bool, str]:
    """Push changes for a repository."""
    stdout, stderr, rc = run_git(repo_path, "push")
    if rc == 0:
        return True, stdout or "Pushed successfully"
    return False, stderr or "Push failed"


def sync_repo(repo_path: Path) -> dict:
    """Sync a repository (pull then push)."""
    results = {"path": str(repo_path)}
    
    # Pull first
    pull_ok, pull_msg = pull_repo(repo_path)
    results["pull"] = {"success": pull_ok, "message": pull_msg}
    
    if not pull_ok:
        return results
    
    # Then push
    push_ok, push_msg = push_repo(repo_path)
    results["push"] = {"success": push_ok, "message": push_msg}
    
    return results


def sync_all_repos(repos_path: Path = DEFAULT_REPOS_PATH) -> list[dict]:
    """Sync all repositories."""
    data = load_repos(repos_path)
    results = []
    
    for repo in data.get("repos", []):
        if repo.get("archived"):
            continue
        
        local_path = Path(repo["localPath"])
        if not local_path.exists():
            results.append({
                "id": repo["id"],
                "name": repo["name"],
                "error": "Directory not found"
            })
            continue
        
        sync_result = sync_repo(local_path)
        results.append({
            "id": repo["id"],
            "name": repo["name"],
            **sync_result
        })
    
    # Update last synced
    data["lastSynced"] = datetime.now().isoformat() + "Z"
    save_repos(data, repos_path)
    
    return results


def generate_dashboard(repos_path: Path = DEFAULT_REPOS_PATH) -> str:
    """Generate a markdown dashboard of repository status."""
    results = check_all_repos(repos_path)
    data = load_repos(repos_path)
    
    lines = [
        "# Repository Dashboard",
        "",
        f"**Last Scanned:** {data.get('lastScanned', 'Never')}",
        f"**Last Synced:** {data.get('lastSynced', 'Never')}",
        "",
    ]
    
    # Categorize repos
    needs_attention = []
    clean = []
    archived = []
    
    for repo in results:
        if repo.get("archived"):
            archived.append(repo)
        elif repo.get("error"):
            needs_attention.append((repo, f"Error: {repo['error']}"))
        elif not repo.get("workingTreeClean"):
            needs_attention.append((repo, f"{repo.get('uncommittedCount', 0)} uncommitted changes"))
        elif repo.get("syncStatus") == "ahead":
            needs_attention.append((repo, f"{repo.get('ahead', 0)} commits to push"))
        elif repo.get("syncStatus") == "behind":
            needs_attention.append((repo, f"{repo.get('behind', 0)} commits to pull"))
        elif repo.get("syncStatus") == "diverged":
            needs_attention.append((repo, f"Diverged: {repo.get('ahead', 0)} ahead, {repo.get('behind', 0)} behind"))
        else:
            clean.append(repo)
    
    # Needs Attention section
    if needs_attention:
        lines.append("## ⚠️ Needs Attention")
        lines.append("")
        for repo, issue in needs_attention:
            lines.append(f"- **{repo['name']}**: {issue}")
        lines.append("")
    
    # Clean section
    if clean:
        lines.append("## ✅ Clean")
        lines.append("")
        for repo in clean:
            branch = repo.get("branch", "?")
            commit = repo.get("localCommit", "?")[:7]
            lines.append(f"- **{repo['name']}** (`{branch}` @ `{commit}`)")
        lines.append("")
    
    # Archived section
    if archived:
        lines.append("## 📦 Archived")
        lines.append("")
        for repo in archived:
            reason = repo.get("reason", "No reason given")
            lines.append(f"- **{repo['name']}**: {reason}")
        lines.append("")
    
    # Summary
    lines.append("---")
    lines.append("")
    lines.append(f"**Total:** {len(results)} repos | **Clean:** {len(clean)} | **Needs Attention:** {len(needs_attention)} | **Archived:** {len(archived)}")
    
    return "\n".join(lines)
