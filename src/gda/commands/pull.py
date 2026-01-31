"""Pull command implementation."""

from pathlib import Path

import typer
from rich.console import Console

from gda.commands.resolve import _resolve_impl
from gda.context import AppContext
from gda.errors import GDAError, LockfileNotFoundError
from gda.models.lockfile import Lockfile
from gda.models.manifest import Manifest
from gda.services.archive import ArchiveService
from gda.services.github import GitHubClient
from gda.services.sync import SyncService

console = Console()


def pull(
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
        help="Force re-download even if files exist.",
    ),
    no_prune: bool = typer.Option(
        False,
        "--no-prune",
        help="Do not remove untracked files.",
    ),
) -> None:
    """Synchronize local filesystem to match gda.lock.

    Downloads and extracts assets, verifying hashes against the lockfile.
    """
    try:
        _pull_impl(ctx, manifest_path, force=force, prune=not no_prune)
    except GDAError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _pull_impl(
    ctx: typer.Context, manifest_path: Path, force: bool, prune: bool
) -> None:
    """Implementation of pull command."""
    lockfile_path = manifest_path.parent / "gda.lock"

    console.print(f"[dim]Loading manifest from {manifest_path}...[/dim]")
    manifest = Manifest.load(manifest_path)

    console.print(f"[dim]Loading lockfile from {lockfile_path}...[/dim]")
    try:
        lockfile = Lockfile.load(lockfile_path)
    except LockfileNotFoundError:
        console.print(
            "[dim]Lockfile missing. Resolving release metadata...[/dim]"
        )
        _resolve_impl(ctx, manifest_path)
        lockfile = Lockfile.load(lockfile_path)

    if lockfile.version != manifest.version:
        console.print(
            "[dim]Lockfile version mismatch. Resolving release metadata...[/dim]"
        )
        _resolve_impl(ctx, manifest_path)
        lockfile = Lockfile.load(lockfile_path)

    # Build destination map
    working_dir = manifest_path.parent.resolve()
    destinations = {
        name: working_dir / asset.destination for name, asset in manifest.assets.items()
    }

    context = ctx.obj if isinstance(ctx.obj, AppContext) else None
    if context is None:
        client = GitHubClient()
        archive = ArchiveService()
        owns_client = True
    else:
        client = context.github_client
        archive = context.archive_service
        owns_client = False
    sync = SyncService(client, archive, working_dir)

    lockfile_updated = False
    try:
        console.print(f"\n[bold]Pulling {len(lockfile.assets)} assets...[/bold]\n")

        for name, asset in lockfile.assets.items():
            dest = destinations.get(name)
            if dest is None:
                console.print(f"[yellow]⚠[/yellow] Skipping {name}: not in manifest")
                continue

            if not force and sync.verify_asset(asset, dest):
                console.print(f"[dim]✓[/dim] {name} (up to date)")
                continue

            console.print(f"[dim]↓[/dim] Downloading {name}...")
            files = sync.pull_asset(asset, dest, force=force)
            console.print(f"[green]✓[/green] {name} ({len(files)} files)")

            # Update lockfile with extracted files
            if asset.files != files:
                asset.files = files
                lockfile_updated = True

            if prune:
                sync._prune_directory(dest, set(files))

        # Persist updated lockfile
        if lockfile_updated:
            lockfile.save(lockfile_path)
            console.print("[dim]Updated lockfile with file lists[/dim]")

        console.print("\n[green]✓[/green] Pull complete")

    finally:
        if owns_client and hasattr(client, "close"):
            client.close()
