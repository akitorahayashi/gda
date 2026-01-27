"""Typer CLI application entry point for typ-tmpl."""

from importlib import metadata
from typing import Optional

import typer
from rich.console import Console

from typ_tmpl.commands import add, delete, list_items
from typ_tmpl.context import AppContext
from typ_tmpl.services.item_storage import ItemStorage

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
        version = get_safe_version("typ-tmpl")
        console.print(f"typ-tmpl version: {version}")
        raise typer.Exit()


app = typer.Typer(
    name="typ-tmpl",
    help="A minimal Python CLI template using Typer.",
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
    """typ-tmpl - A minimal Python CLI template."""
    if ctx.obj is None:
        ctx.obj = AppContext(item_storage=ItemStorage())


# Register add command and alias
app.command(name="add", help=r"Add a new item. \[aliases: a]")(add)
app.command(name="a", hidden=True)(add)

# Register list command and alias
app.command(name="list", help=r"List all items. \[aliases: ls]")(list_items)
app.command(name="ls", hidden=True)(list_items)

# Register delete command and alias
app.command(name="delete", help=r"Delete an item. \[aliases: rm]")(delete)
app.command(name="rm", hidden=True)(delete)


if __name__ == "__main__":
    app()
