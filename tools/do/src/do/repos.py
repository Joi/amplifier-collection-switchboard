"""Multi-repository sync and status."""

from pathlib import Path

import click

from .repos_service import (
    check_all_repos,
    sync_all_repos,
    generate_dashboard,
)


@click.group()
def repos():
    """Multi-repository sync and status tracking."""
    pass


@repos.command()
def status():
    """Show status of all repositories."""
    results = check_all_repos()
    
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
        else:
            clean.append(repo)
    
    click.echo(f"📊 Repository Status ({len(results)} repos)\n")
    
    if needs_attention:
        click.echo("⚠️  NEEDS ATTENTION\n")
        for repo, issue in needs_attention:
            click.echo(f"  {repo['name']} - {issue}")
        click.echo()
    
    if clean:
        click.echo("✅ CLEAN\n")
        for repo in clean:
            branch = repo.get("branch", "?")
            click.echo(f"  {repo['name']} ({branch})")
        click.echo()
    
    click.echo(f"Summary: {len(clean)} clean, {len(needs_attention)} need attention, {len(archived)} archived")


@repos.command()
@click.option('--dry-run', is_flag=True, help='Show what would be synced')
def sync(dry_run: bool):
    """Sync all repositories (pull then push)."""
    if dry_run:
        click.echo("🔍 Checking what needs sync...\n")
        results = check_all_repos()
        
        to_sync = [r for r in results 
                   if not r.get("archived") and not r.get("error")
                   and (r.get("syncStatus") != "synced" or not r.get("workingTreeClean"))]
        
        if not to_sync:
            click.echo("✅ All repos are synced!")
        else:
            click.echo(f"Would sync {len(to_sync)} repos:")
            for repo in to_sync:
                click.echo(f"  - {repo['name']} ({repo.get('syncStatus', 'unknown')})")
        return
    
    click.echo("🔄 Syncing all repositories...\n")
    results = sync_all_repos()
    
    success = 0
    failed = 0
    
    for result in results:
        if result.get("error"):
            click.echo(f"❌ {result['name']}: {result['error']}")
            failed += 1
        elif result.get("pull", {}).get("success") and result.get("push", {}).get("success"):
            click.echo(f"✅ {result['name']}")
            success += 1
        else:
            click.echo(f"⚠️ {result['name']}: partial sync")
            failed += 1
    
    click.echo(f"\n📊 Synced: {success} success, {failed} failed")


@repos.command()
def pull():
    """Pull all repositories."""
    from .repos_service import pull_repo
    from .repos_storage import load_repos
    
    click.echo("⬇️  Pulling all repositories...\n")
    data = load_repos()
    
    success = 0
    for repo in data.get("repos", []):
        if repo.get("archived"):
            continue
        
        local_path = Path(repo["localPath"])
        if not local_path.exists():
            click.echo(f"❌ {repo['name']}: not found")
            continue
        
        ok, msg = pull_repo(local_path)
        if ok:
            click.echo(f"✅ {repo['name']}")
            success += 1
        else:
            click.echo(f"❌ {repo['name']}: {msg}")
    
    click.echo(f"\n📊 Pulled: {success} repos")


@repos.command()
@click.option('--output', '-o', type=click.Path(), help='Output file')
def dashboard(output: str):
    """Generate markdown dashboard."""
    md = generate_dashboard()
    
    if output:
        Path(output).expanduser().write_text(md)
        click.echo(f"✅ Dashboard written to {output}")
    else:
        click.echo(md)


@repos.command()
def stats():
    """Show repository statistics."""
    from .repos_storage import load_repos
    
    data = load_repos()
    repos_list = data.get("repos", [])
    
    total = len(repos_list)
    archived = sum(1 for r in repos_list if r.get("archived"))
    active = total - archived
    
    click.echo("📊 Repository Statistics\n")
    click.echo(f"Total: {total}")
    click.echo(f"Active: {active}")
    click.echo(f"Archived: {archived}")
    click.echo(f"\nLast Scanned: {data.get('lastScanned', 'Never')}")
    click.echo(f"Last Synced: {data.get('lastSynced', 'Never')}")
