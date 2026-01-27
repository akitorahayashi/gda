"""Filesystem-based item storage implementation."""

from pathlib import Path

from typ_tmpl.errors import ItemExistsError, ItemNotFoundError
from typ_tmpl.models.item import Item
from typ_tmpl.protocols.item_storage import ItemStorageProtocol


class ItemStorage(ItemStorageProtocol):
    """Storage implementation using filesystem."""

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize filesystem item storage.

        Args:
            base_dir: Base directory for storing items.
                      Defaults to ~/.config/typ-tmpl/items
        """
        if base_dir is None:
            base_dir = Path.home() / ".config" / "typ-tmpl" / "items"
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _item_path(self, item_id: str) -> Path:
        """Get path for an item."""
        self._validate_item_id(item_id)
        return self.base_dir / f"{item_id}.txt"

    def _validate_item_id(self, item_id: str) -> None:
        """Validate item identifier for safe filesystem usage."""
        if "/" in item_id or "\\" in item_id:
            raise ValueError(f"Invalid item ID '{item_id}': contains path separators.")

    def add(self, item: Item) -> None:
        """Add a new item.

        Args:
            item: Item to store.

        Raises:
            ItemExistsError: If an item with the same ID already exists.
        """
        path = self._item_path(item.id)
        if path.exists():
            raise ItemExistsError(item.id)
        path.write_text(item.content)

    def list(self) -> list[Item]:
        """List all items.

        Returns:
            List of items sorted alphabetically by ID.
        """
        return [
            Item(id=path.stem, content=path.read_text())
            for path in sorted(self.base_dir.glob("*.txt"), key=lambda p: p.stem)
        ]

    def delete(self, item_id: str) -> None:
        """Delete an item.

        Args:
            item_id: Identifier of the item to delete.

        Raises:
            ItemNotFoundError: If the item does not exist.
        """
        path = self._item_path(item_id)
        if not path.exists():
            raise ItemNotFoundError(item_id)
        path.unlink()

    def exists(self, item_id: str) -> bool:
        """Check if an item exists.

        Args:
            item_id: Identifier to check.

        Returns:
            True if item exists, False otherwise.
        """
        return self._item_path(item_id).exists()

    def get(self, item_id: str) -> Item | None:
        """Get an item.

        Args:
            item_id: Identifier of the item.

        Returns:
            Item if found, otherwise None.
        """
        path = self._item_path(item_id)
        if path.exists():
            return Item(id=item_id, content=path.read_text())
        return None
