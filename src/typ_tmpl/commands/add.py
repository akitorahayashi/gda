"""Add command implementation."""

import typer
from rich.console import Console

from typ_tmpl.context import AppContext
from typ_tmpl.errors import ItemExistsError
from typ_tmpl.models.item import Item

console = Console()


def add(
    ctx: typer.Context,
    id: str = typer.Argument(..., help="Unique identifier for the item."),
    content: str = typer.Option(..., "--content", "-c", help="Content of the item."),
) -> None:
    """Add a new item.

    Examples:
        typ-tmpl add note1 -c "My first note"
        typ-tmpl a note2 --content "Another note"
    """
    app_ctx: AppContext = ctx.obj

    try:
        app_ctx.item_storage.add(Item(id=id, content=content))
        console.print(f"[green]Added '{id}'[/]")
    except ValueError as exc:
        console.print(f"[red]Error: {exc}[/]")
        raise typer.Exit(1)
    except ItemExistsError:
        console.print(f"[red]Error: Item '{id}' already exists[/]")
        raise typer.Exit(1)
