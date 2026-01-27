"""Push command implementation."""

from pathlib import Path

import typer
from rich.console import Console

from gda.errors import GDAError
from gda.models.manifest import Manifest
from gda.services.archive import ArchiveService
from gda.services.github import GitHubClient

console = Console()


def push(
    ctx: typer.Context,
    manifest_path: Path = typer.Option(
        Path("gda.yml"),
        "--manifest",
        "-m",
        help="Path to manifest file.",
    ),
    force: bool = typer.Option(
        False,
        "--force",
        "-f",
        help="Overwrite existing release assets.",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        "-n",
        help="Show what would be uploaded without uploading.",
    ),
) -> None:
    """Create archives and upload to GitHub Release.

    Builds deterministic ZIP archives from local directories and uploads
    them to the specified release.
    """
    try:
        _push_impl(manifest_path, force=force, dry_run=dry_run)
    except GDAError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _push_impl(manifest_path: Path, force: bool, dry_run: bool) -> None:
    """Implementation of push command."""
    console.print(f"[dim]Loading manifest from {manifest_path}...[/dim]")
    manifest = Manifest.load(manifest_path)

    working_dir = manifest_path.parent.resolve()
    archive = ArchiveService()
    build_dir = working_dir / ".gda" / "build"
    build_dir.mkdir(parents=True, exist_ok=True)

    # Build archives
    archives: dict[str, tuple[Path, str]] = {}

    console.print(f"\n[bold]Building {len(manifest.assets)} archives...[/bold]\n")

    for name, asset in manifest.assets.items():
        source_dir = working_dir / asset.source
        if not source_dir.exists():
            console.print(f"[yellow]⚠[/yellow] Skipping {name}: source not found")
            continue

        zip_path = build_dir / f"{asset.source}.zip"
        console.print(f"[dim]📦[/dim] Building {zip_path.name}...")

        sha256 = archive.create_zip(source_dir, zip_path, asset.excludes)
        archives[name] = (zip_path, sha256)
        console.print(f"[green]✓[/green] {zip_path.name} ({sha256[:16]}...)")

    if dry_run:
        console.print("\n[yellow]Dry run - no uploads performed[/yellow]")
        return

    if not archives:
        console.print("\n[yellow]No archives to upload[/yellow]")
        return

    # Upload to GitHub
    client = GitHubClient()
    try:
        console.print(
            f"\n[bold]Uploading to {manifest.repository}@{manifest.version}...[/bold]\n"
        )

        # Get or create release
        try:
            release = client.get_release(manifest.repository, manifest.version)
            console.print(f"[dim]Using existing release: {release.name}[/dim]")
        except GDAError:
            console.print(f"[dim]Creating release {manifest.version}...[/dim]")
            release = client.create_release(
                manifest.repository,
                manifest.version,
                manifest.version,
            )

        # Check existing assets
        existing = {asset.name for asset in release.assets}

        for _name, (zip_path, _sha256) in archives.items():
            asset_name = zip_path.name

            if asset_name in existing and not force:
                console.print(
                    f"[yellow]⚠[/yellow] {asset_name} already exists (use --force)"
                )
                continue

            console.print(f"[dim]↑[/dim] Uploading {asset_name}...")
            content = zip_path.read_bytes()

            client.upload_asset(
                manifest.repository,
                release.id,
                asset_name,
                content,
                "application/zip",
            )
            console.print(f"[green]✓[/green] Uploaded {asset_name}")

        console.print("\n[green]✓[/green] Push complete")

    finally:
        client.close()
