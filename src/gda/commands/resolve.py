"""Resolve command implementation."""

from pathlib import Path

import typer
from rich.console import Console

from gda.context import AppContext
from gda.errors import GDAError
from gda.models.lockfile import LockedAsset, Lockfile
from gda.models.manifest import Manifest
from gda.services.github import GitHubClient

console = Console()


def resolve(
    ctx: typer.Context,
    manifest_path: Path = typer.Option(
        Path("gda.yml"),
        "--manifest",
        "-m",
        help="Path to manifest file.",
    ),
) -> None:
    """Resolve dependencies and update gda.lock.

    Fetches release metadata from GitHub and creates/updates the lockfile
    with exact URLs and hashes for each asset.
    """
    try:
        _resolve_impl(ctx, manifest_path)
    except GDAError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)


def _resolve_impl(ctx: typer.Context, manifest_path: Path) -> None:
    """Implementation of resolve command."""
    console.print(f"[dim]Loading manifest from {manifest_path}...[/dim]")
    manifest = Manifest.load(manifest_path)

    console.print(f"[dim]Resolving {manifest.repository}@{manifest.version}...[/dim]")

    context = ctx.obj if isinstance(ctx.obj, AppContext) else None
    if context is None:
        client = GitHubClient()
        owns_client = True
    else:
        client = context.github_client
        owns_client = False
    try:
        release = client.get_release(manifest.repository, manifest.version)
        console.print(f"[green]✓[/green] Found release: {release.name}")

        # Build asset map from release
        release_assets = {asset.name: asset for asset in release.assets}

        locked_assets: dict[str, LockedAsset] = {}

        for name, asset in manifest.assets.items():
            zip_name = f"{name}.zip"

            if zip_name not in release_assets:
                console.print(
                    f"[yellow]⚠[/yellow] Asset '{zip_name}' not found in release"
                )
                continue

            remote_asset = release_assets[zip_name]
            console.print(f"[dim]  Fetching hash for {zip_name}...[/dim]")
            sha256 = client.get_asset_hash(remote_asset.url)

            locked_assets[name] = LockedAsset(
                name=name,
                url=remote_asset.url,
                sha256=sha256,
                files=[],  # Populated during pull
            )
            console.print(f"[green]✓[/green] Locked: {name} ({sha256[:16]}...)")

        lockfile = Lockfile(version=manifest.version, assets=locked_assets)
        lockfile_path = manifest_path.parent / "gda.lock"
        lockfile.save(lockfile_path)

        console.print(f"\n[green]✓[/green] Wrote {lockfile_path}")

    finally:
        if owns_client and hasattr(client, "close"):
            client.close()
