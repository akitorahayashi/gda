"""List command implementation."""

import typer
from rich.console import Console

from typ_tmpl.context import AppContext

console = Console()


def list_items(
    ctx: typer.Context,
) -> None:
    """List all items.

    Examples:
        typ-tmpl list
        typ-tmpl ls
    """
    app_ctx: AppContext = ctx.obj

    items = app_ctx.item_storage.list()
    if not items:
        console.print("[dim]No items found[/]")
        return

    for item in items:
        console.print(f"  {item.id}")
