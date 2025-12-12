"""CLI for knowledge vault gap detection."""

import click
from pathlib import Path

from .service import (
    run_gap_detection,
    get_vault_stats,
    detect_undefined_concepts,
    detect_stale_content,
    detect_orphan_pages,
    detect_thin_sections,
)
from .storage import (
    DEFAULT_VAULT_PATH,
    DEFAULT_DATA_PATH,
    load_gaps,
    dismiss_gap,
    load_dismissed,
)


@click.group()
def cli():
    """Knowledge vault gap detection and curation."""
    pass


@cli.command()
@click.option("--vault", "-v", type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH), help="Vault path")
@click.option("--domain", "-d", help="Subdomain to scan (e.g., 'chanoyu')")
@click.option("--stale-months", default=6, help="Months before content is considered stale")
@click.option("--min-words", default=100, help="Minimum words for thin section detection")
@click.option("--json", "as_json", is_flag=True, help="Output as JSON")
def gaps(vault: str, domain: str, stale_months: int, min_words: int, as_json: bool):
    """Run gap detection on vault."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"🔍 Scanning {vault_path}" + (f"/{domain}" if domain else "") + "...\n")
    
    report = run_gap_detection(
        vault_path=vault_path,
        domain=domain,
        stale_months=stale_months,
        min_words=min_words
    )
    
    if as_json:
        import json
        click.echo(json.dumps(report, indent=2))
        return
    
    summary = report["summary"]
    
    click.echo(f"📊 Gap Report ({summary['total']} gaps found)\n")
    
    if summary["total"] == 0:
        click.echo("✅ No gaps detected!")
        return
    
    # By type
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
    
    click.echo("\nBy Severity:")
    for severity, count in summary["by_severity"].items():
        click.echo(f"  {severity}: {count}")
    
    # Show top 10 gaps
    click.echo("\n📋 Top Gaps:\n")
    for gap in report["gaps"][:10]:
        icon = type_icons.get(gap["type"], "•")
        loc = gap["location"]
        file_path = loc.get("file", "?")
        click.echo(f"{icon} [{gap['id'][:12]}] {file_path}")
        click.echo(f"   {gap['description']}")
        click.echo()
    
    if len(report["gaps"]) > 10:
        click.echo(f"... and {len(report['gaps']) - 10} more gaps")
    
    click.echo(f"\n💾 Report saved to {DEFAULT_DATA_PATH / 'gaps' / 'current.json'}")


@cli.command()
@click.option("--vault", "-v", type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH), help="Vault path")
@click.option("--domain", "-d", help="Subdomain to scan")
def undefined(vault: str, domain: str):
    """Find undefined concepts (broken wikilinks)."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"🔍 Finding undefined concepts...\n")
    
    gaps = detect_undefined_concepts(vault_path, domain)
    
    if not gaps:
        click.echo("✅ No undefined concepts found!")
        return
    
    click.echo(f"🔴 Found {len(gaps)} undefined concepts:\n")
    
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  [[{loc['context'].strip('[]')}]] in {loc['file']}:{loc['line']}")
    
    if len(gaps) > 20:
        click.echo(f"\n... and {len(gaps) - 20} more")


@cli.command()
@click.option("--vault", "-v", type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH), help="Vault path")
@click.option("--domain", "-d", help="Subdomain to scan")
@click.option("--months", default=6, help="Months before content is considered stale")
def stale(vault: str, domain: str, months: int):
    """Find stale content (not updated in N months)."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"🔍 Finding content not updated in {months}+ months...\n")
    
    gaps = detect_stale_content(vault_path, domain, months)
    
    if not gaps:
        click.echo("✅ No stale content found!")
        return
    
    click.echo(f"🟡 Found {len(gaps)} stale files:\n")
    
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  {loc['file']} - {gap['description']}")
    
    if len(gaps) > 20:
        click.echo(f"\n... and {len(gaps) - 20} more")


@cli.command()
@click.option("--vault", "-v", type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH), help="Vault path")
@click.option("--domain", "-d", help="Subdomain to scan")
def orphans(vault: str, domain: str):
    """Find orphan pages (not linked from anywhere)."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"🔍 Finding orphan pages...\n")
    
    gaps = detect_orphan_pages(vault_path, domain)
    
    if not gaps:
        click.echo("✅ No orphan pages found!")
        return
    
    click.echo(f"🟠 Found {len(gaps)} orphan pages:\n")
    
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  {loc['file']}")
    
    if len(gaps) > 20:
        click.echo(f"\n... and {len(gaps) - 20} more")


@cli.command()
@click.option("--vault", "-v", type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH), help="Vault path")
@click.option("--domain", "-d", help="Subdomain to scan")
@click.option("--min-words", default=100, help="Minimum word count")
def thin(vault: str, domain: str, min_words: int):
    """Find thin sections (< N words)."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"🔍 Finding files with < {min_words} words...\n")
    
    gaps = detect_thin_sections(vault_path, domain, min_words)
    
    if not gaps:
        click.echo("✅ No thin sections found!")
        return
    
    click.echo(f"⚪ Found {len(gaps)} thin sections:\n")
    
    for gap in gaps[:20]:
        loc = gap["location"]
        click.echo(f"  {loc['file']} ({loc['word_count']} words)")
    
    if len(gaps) > 20:
        click.echo(f"\n... and {len(gaps) - 20} more")


@cli.command()
@click.argument("gap_id")
@click.option("--reason", "-r", required=True, help="Reason for dismissal")
def dismiss(gap_id: str, reason: str):
    """Dismiss a gap (won't appear in future reports)."""
    if dismiss_gap(gap_id, reason):
        click.echo(f"✅ Dismissed gap: {gap_id}")
        click.echo(f"   Reason: {reason}")
    else:
        click.echo(f"⚠️  Gap already dismissed or not found: {gap_id}")


@cli.command()
def dismissed():
    """List dismissed gaps."""
    data = load_dismissed()
    
    items = data.get("dismissed", [])
    
    if not items:
        click.echo("No dismissed gaps")
        return
    
    click.echo(f"📋 Dismissed Gaps ({len(items)}):\n")
    
    for item in items:
        click.echo(f"  {item['id'][:20]}...")
        click.echo(f"    Reason: {item['reason']}")
        click.echo(f"    Dismissed: {item['dismissed_at']}")
        click.echo()


@cli.command()
def report():
    """Show last gap report."""
    data = load_gaps()
    
    if not data.get("generated_at"):
        click.echo("No gap report found. Run 'knowledge gaps' first.")
        return
    
    click.echo(f"📊 Last Gap Report\n")
    click.echo(f"Vault: {data['vault']}")
    click.echo(f"Domain: {data.get('domain') or 'all'}")
    click.echo(f"Generated: {data['generated_at']}")
    click.echo()
    
    summary = data["summary"]
    click.echo(f"Total gaps: {summary['total']}")
    
    if summary["by_type"]:
        click.echo("\nBy Type:")
        for t, c in summary["by_type"].items():
            click.echo(f"  {t}: {c}")
    
    if summary["by_severity"]:
        click.echo("\nBy Severity:")
        for s, c in summary["by_severity"].items():
            click.echo(f"  {s}: {c}")


@cli.command()
@click.option("--vault", "-v", type=click.Path(exists=True), default=str(DEFAULT_VAULT_PATH), help="Vault path")
@click.option("--domain", "-d", help="Subdomain to analyze")
def stats(vault: str, domain: str):
    """Show vault statistics."""
    vault_path = Path(vault).expanduser()
    
    click.echo(f"📊 Vault Statistics\n")
    
    s = get_vault_stats(vault_path, domain)
    
    click.echo(f"Vault: {s['vault']}")
    if s['domain']:
        click.echo(f"Domain: {s['domain']}")
    click.echo(f"Files: {s['files']}")
    click.echo(f"Words: {s['words']:,}")
    click.echo(f"Wikilinks: {s['links']:,}")
    
    if s['files'] > 0:
        avg_words = s['words'] // s['files']
        avg_links = s['links'] / s['files']
        click.echo(f"\nAverage per file:")
        click.echo(f"  Words: {avg_words}")
        click.echo(f"  Links: {avg_links:.1f}")


if __name__ == "__main__":
    cli()
