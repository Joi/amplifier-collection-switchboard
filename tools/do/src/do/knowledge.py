"""Knowledge vault gap detection."""

from pathlib import Path

import click

from .knowledge_service import (
    run_gap_detection,
    get_vault_stats,
    detect_undefined_concepts,
    detect_stale_content,
    detect_orphan_pages,
)
from .knowledge_storage import (
    DEFAULT_VAULT_PATH,
    load_gaps,
    dismiss_gap,
    load_dismissed,
)


@click.group()
def knowledge():
    """Knowledge vault gap detection and curation."""
    pass


@knowledge.command()
@click.option('--vault', '-v', type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH))
@click.option('--domain', '-d', help='Subdomain to scan (e.g., chanoyu)')
def gaps(vault: str, domain: str):
    """Run full gap detection on vault."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"🔍 Scanning {vault_path}" + (f"/{domain}" if domain else "") + "...\n")
    
    report = run_gap_detection(vault_path=vault_path, domain=domain)
    summary = report["summary"]
    
    click.echo(f"📊 Gap Report ({summary['total']} gaps found)\n")
    
    if summary["total"] == 0:
        click.echo("✅ No gaps detected!")
        return
    
    type_icons = {
        "undefined_concept": "🔴",
        "stale_content": "🟡",
        "orphan_page": "🟠",
        "thin_section": "⚪"
    }
    
    click.echo("By Type:")
    for gap_type, count in summary["by_type"].items():
        icon = type_icons.get(gap_type, "•")
        click.echo(f"  {icon} {gap_type}: {count}")
    
    click.echo("\n📋 Top Gaps:\n")
    for gap in report["gaps"][:10]:
        icon = type_icons.get(gap["type"], "•")
        loc = gap["location"]
        file_path = loc.get("file", "?")
        click.echo(f"{icon} {file_path}")
        click.echo(f"   {gap['description']}")


@knowledge.command()
@click.option('--vault', '-v', type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH))
@click.option('--domain', '-d', help='Subdomain to scan')
def undefined(vault: str, domain: str):
    """Find undefined concepts (broken wikilinks)."""
    vault_path = Path(vault).expanduser()
    gaps = detect_undefined_concepts(vault_path, domain)
    
    if not gaps:
        click.echo("✅ No undefined concepts found!")
        return
    
    click.echo(f"🔴 Found {len(gaps)} undefined concepts:\n")
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  [[{loc['context'].strip('[]')}]] in {loc['file']}")


@knowledge.command()
@click.option('--vault', '-v', type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH))
@click.option('--domain', '-d', help='Subdomain to scan')
@click.option('--months', default=6, help='Months threshold')
def stale(vault: str, domain: str, months: int):
    """Find stale content (not updated in N months)."""
    vault_path = Path(vault).expanduser()
    gaps = detect_stale_content(vault_path, domain, months)
    
    if not gaps:
        click.echo("✅ No stale content found!")
        return
    
    click.echo(f"🟡 Found {len(gaps)} stale files:\n")
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  {loc['file']} - {gap['description']}")


@knowledge.command()
@click.option('--vault', '-v', type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH))
@click.option('--domain', '-d', help='Subdomain to scan')
def orphans(vault: str, domain: str):
    """Find orphan pages (not linked from anywhere)."""
    vault_path = Path(vault).expanduser()
    gaps = detect_orphan_pages(vault_path, domain)
    
    if not gaps:
        click.echo("✅ No orphan pages found!")
        return
    
    click.echo(f"🟠 Found {len(gaps)} orphan pages:\n")
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  {loc['file']}")


@knowledge.command()
@click.option('--vault', '-v', type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH))
@click.option('--domain', '-d', help='Subdomain to analyze')
def stats(vault: str, domain: str):
    """Show vault statistics."""
    vault_path = Path(vault).expanduser()
    s = get_vault_stats(vault_path, domain)
    
    click.echo("📊 Vault Statistics\n")
    click.echo(f"Vault: {s['vault']}")
    if s['domain']:
        click.echo(f"Domain: {s['domain']}")
    click.echo(f"Files: {s['files']}")
    click.echo(f"Words: {s['words']:,}")
    click.echo(f"Wikilinks: {s['links']:,}")


@knowledge.command()
@click.argument('gap_id')
@click.option('--reason', '-r', required=True, help='Reason for dismissal')
def dismiss(gap_id: str, reason: str):
    """Dismiss a gap (won't appear in future reports)."""
    if dismiss_gap(gap_id, reason):
        click.echo(f"✅ Dismissed: {gap_id}")
    else:
        click.echo(f"⚠️ Already dismissed or not found: {gap_id}")
