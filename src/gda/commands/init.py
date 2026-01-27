"""Init command implementation."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

console = Console()

_MANIFEST_TEMPLATE = """repository: "{repository}"
version: "{version}"

assets:
  # Example asset configuration
  # dataset-name:
  #   source: "path/to/source"
  #   destination: "path/to/dest"
"""

_GITIGNORE_BLOCK = """# GDA cache and build artifacts
.gda/
"""


def _render_manifest(repository: str, version: str) -> str:
    return _MANIFEST_TEMPLATE.format(repository=repository, version=version)


def _write_manifest(path: Path, content: str, overwrite: bool) -> bool:
    if path.exists() and not overwrite:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _gitignore_has_gda(content: str) -> bool:
    for line in content.splitlines():
        if line.strip() in {".gda", ".gda/"}:
            return True
    return False


def _ensure_gitignore(path: Path) -> bool:
    content = path.read_text(encoding="utf-8") if path.exists() else ""
    if _gitignore_has_gda(content):
        return False

    updated = content
    if updated and not updated.endswith("\n"):
        updated += "\n"
    if updated:
        updated += "\n"
    updated += _GITIGNORE_BLOCK

    path.write_text(updated, encoding="utf-8")
    return True


def init(
    ctx: typer.Context,
    repository: Optional[str] = typer.Option(
        None,
        "--repository",
        "-r",
        help="GitHub repository name (owner/repo).",
    ),
    version: Optional[str] = typer.Option(
        None,
        "--version",
        "-v",
        help="Initial version.",
    ),
    yes: bool = typer.Option(
        False,
        "--yes",
        "-y",
        help="Skip confirmation prompts.",
    ),
) -> None:
    """Initialize GDA in the current directory."""
    _ = ctx
    manifest_path = Path("gda.yml")

    if repository is None:
        repository = typer.prompt("Repository (owner/repo)")

    if version is None:
        version = typer.prompt("Version", default="0.1.0")

    overwrite = True
    if manifest_path.exists() and not yes:
        overwrite = typer.confirm(
            "gda.yml already exists. Overwrite?",
            default=False,
        )

    content = _render_manifest(repository, version)
    if not _write_manifest(manifest_path, content, overwrite=overwrite):
        console.print("[yellow]Skipped writing gda.yml[/yellow]")
        raise typer.Exit()

    console.print(f"[green]✓[/green] Wrote {manifest_path}")

    if _ensure_gitignore(Path(".gitignore")):
        console.print("[green]✓[/green] Updated .gitignore")
    else:
        console.print("[dim].gitignore already contains .gda/[/dim]")
