"""Typer CLI application entry point for GDA."""

from importlib import metadata
from typing import Optional

import typer
from rich.console import Console

from gda.commands import pull, push, resolve
from gda.context import AppContext
from gda.services.archive import ArchiveService
from gda.services.github import GitHubClient

console = Console()


def get_safe_version(package_name: str, fallback: str = "0.1.0") -> str:
    """Safely get the version of a package.

    Args:
        package_name: Name of the package.
        fallback: Default version if retrieval fails.

    Returns:
        Version string.
    """
    try:
        return metadata.version(package_name)
    except metadata.PackageNotFoundError:
        return fallback


def version_callback(value: Optional[bool]) -> None:
    """Print version and exit."""
    if value:
        version = get_safe_version("gda")
        console.print(f"gda version: {version}")
        raise typer.Exit()


app = typer.Typer(
    name="gda",
    help="GitHub Data Assets - Manage large data assets using GitHub Releases.",
    no_args_is_help=True,
)


@app.callback()
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        callback=version_callback,
        is_eager=True,
        help="Show version and exit.",
    ),
) -> None:
    """GDA - GitHub Data Assets manager."""
    if ctx.obj is None:
        ctx.obj = AppContext(
            github_client=GitHubClient(),
            archive_service=ArchiveService(),
        )


# Register resolve command
app.command(name="resolve", help="Resolve dependencies and update gda.lock.")(resolve)

# Register pull command
app.command(name="pull", help="Synchronize local filesystem to match gda.lock.")(pull)

# Register push command
app.command(name="push", help="Create archives and upload to GitHub Release.")(push)


if __name__ == "__main__":
    app()
