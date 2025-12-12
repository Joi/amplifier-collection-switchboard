"""CLI for repository management."""

import click
from pathlib import Path

from .service import (
    check_all_repos,
    sync_all_repos,
    generate_dashboard,
    pull_repo,
    push_repo,
)
from .storage import DEFAULT_REPOS_PATH


@click.group()
def cli():
    """Multi-repository sync and status tracking."""
    pass


@cli.command()
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def status(as_json: bool):
    """Show status of all repositories."""
    results = check_all_repos()
    
    if as_json:
        import json
        click.echo(json.dumps(results, indent=2))
        return
    
    # Categorize
    needs_attention = []
    clean = []
    archived = []
    
    for repo in results:
        if repo.get("archived"):
            archived.append(repo)
        elif repo.get("error"):
            needs_attention.append((repo, f"❌ {repo['error']}"))
        elif not repo.get("workingTreeClean"):
            needs_attention.append((repo, f"📝 {repo.get('uncommittedCount', 0)} uncommitted"))
        elif repo.get("syncStatus") == "ahead":
            needs_attention.append((repo, f"⬆️  {repo.get('ahead', 0)} to push"))
        elif repo.get("syncStatus") == "behind":
            needs_attention.append((repo, f"⬇️  {repo.get('behind', 0)} to pull"))
        elif repo.get("syncStatus") == "diverged":
            needs_attention.append((repo, f"↕️  diverged"))
        else:
            clean.append(repo)
    
    # Print results
    total = len(results)
    click.echo(f"📊 Repository Status ({total} repos)\n")
    
    if needs_attention:
        click.echo("⚠️  NEEDS ATTENTION\n")
        for repo, issue in needs_attention:
            branch = repo.get("branch", "?")
            click.echo(f"  {repo['name']} ({branch}) - {issue}")
        click.echo()
    
    if clean:
        click.echo("✅ CLEAN\n")
        for repo in clean:
            branch = repo.get("branch", "?")
            commit = repo.get("localCommit", "?")[:7]
            click.echo(f"  {repo['name']} ({branch} @ {commit})")
        click.echo()
    
    if archived:
        click.echo(f"📦 ARCHIVED ({len(archived)})\n")
        for repo in archived[:3]:  # Show first 3
            click.echo(f"  {repo['name']}")
        if len(archived) > 3:
            click.echo(f"  ... and {len(archived) - 3} more")
        click.echo()
    
    # Summary
    click.echo(f"Summary: {len(clean)} clean, {len(needs_attention)} need attention, {len(archived)} archived")


@cli.command()
@click.option("--dry-run", is_flag=True, help="Show what would be synced without syncing")
def sync(dry_run: bool):
    """Sync all repositories (pull then push)."""
    if dry_run:
        click.echo("🔍 Dry run - checking what needs sync...\n")
        results = check_all_repos()
        
        to_sync = []
        for repo in results:
            if repo.get("archived") or repo.get("error"):
                continue
            if repo.get("syncStatus") != "synced" or not repo.get("workingTreeClean"):
                to_sync.append(repo)
        
        if not to_sync:
            click.echo("✅ All repos are synced!")
        else:
            click.echo(f"Would sync {len(to_sync)} repos:")
            for repo in to_sync:
                status = repo.get("syncStatus", "unknown")
                click.echo(f"  - {repo['name']} ({status})")
        return
    
    click.echo("🔄 Syncing all repositories...\n")
    results = sync_all_repos()
    
    success = 0
    failed = 0
    
    for result in results:
        name = result["name"]
        
        if result.get("error"):
            click.echo(f"❌ {name}: {result['error']}")
            failed += 1
            continue
        
        pull_ok = result.get("pull", {}).get("success", False)
        push_ok = result.get("push", {}).get("success", False)
        
        if pull_ok and push_ok:
            click.echo(f"✅ {name}")
            success += 1
        elif pull_ok:
            push_msg = result.get("push", {}).get("message", "")
            click.echo(f"⚠️  {name}: push failed - {push_msg}")
            failed += 1
        else:
            pull_msg = result.get("pull", {}).get("message", "")
            click.echo(f"❌ {name}: pull failed - {pull_msg}")
            failed += 1
    
    click.echo(f"\n📊 Synced: {success} success, {failed} failed")


@cli.command()
def pull():
    """Pull all repositories."""
    click.echo("⬇️  Pulling all repositories...\n")
    
    from .storage import load_repos
    data = load_repos()
    
    success = 0
    failed = 0
    
    for repo in data.get("repos", []):
        if repo.get("archived"):
            continue
        
        local_path = Path(repo["localPath"])
        if not local_path.exists():
            click.echo(f"❌ {repo['name']}: directory not found")
            failed += 1
            continue
        
        ok, msg = pull_repo(local_path)
        if ok:
            if "Already up to date" in msg:
                click.echo(f"✅ {repo['name']}: up to date")
            else:
                click.echo(f"✅ {repo['name']}: pulled")
            success += 1
        else:
            click.echo(f"❌ {repo['name']}: {msg}")
            failed += 1
    
    click.echo(f"\n📊 Pull: {success} success, {failed} failed")


@cli.command()
def push():
    """Push all repositories with commits."""
    click.echo("⬆️  Pushing repositories with local commits...\n")
    
    results = check_all_repos()
    
    to_push = [r for r in results if r.get("ahead", 0) > 0]
    
    if not to_push:
        click.echo("✅ No repositories have commits to push")
        return
    
    success = 0
    failed = 0
    
    for repo in to_push:
        local_path = Path(repo["localPath"])
        ok, msg = push_repo(local_path)
        
        if ok:
            click.echo(f"✅ {repo['name']}: pushed {repo.get('ahead', 0)} commits")
            success += 1
        else:
            click.echo(f"❌ {repo['name']}: {msg}")
            failed += 1
    
    click.echo(f"\n📊 Push: {success} success, {failed} failed")


@cli.command()
@click.option("--output", "-o", type=click.Path(), help="Output file path")
def dashboard(output: str):
    """Generate markdown dashboard."""
    md = generate_dashboard()
    
    if output:
        output_path = Path(output).expanduser()
        output_path.write_text(md)
        click.echo(f"✅ Dashboard written to {output_path}")
    else:
        click.echo(md)


@cli.command()
def stats():
    """Show repository statistics."""
    from .storage import load_repos
    data = load_repos()
    
    repos = data.get("repos", [])
    total = len(repos)
    archived = sum(1 for r in repos if r.get("archived"))
    active = total - archived
    
    synced = sum(1 for r in repos if r.get("syncStatus") == "synced" and not r.get("archived"))
    dirty = sum(1 for r in repos if not r.get("workingTreeClean", True) and not r.get("archived"))
    
    click.echo("📊 Repository Statistics\n")
    click.echo(f"Total: {total}")
    click.echo(f"Active: {active}")
    click.echo(f"Archived: {archived}")
    click.echo(f"Synced: {synced}")
    click.echo(f"Dirty: {dirty}")
    click.echo(f"\nLast Scanned: {data.get('lastScanned', 'Never')}")
    click.echo(f"Last Synced: {data.get('lastSynced', 'Never')}")


if __name__ == "__main__":
    cli()
