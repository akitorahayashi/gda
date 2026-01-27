"""Item storage protocol definition."""

from typing import Protocol

from typ_tmpl.models.item import Item


class ItemStorageProtocol(Protocol):
    """Storage abstraction for item persistence."""

    def add(self, item: Item) -> None:
        """Add a new item.

        Args:
            item: Item to store.
        """
        ...

    def list(self) -> list[Item]:
        """List all items.

        Returns:
            List of items sorted by ID.
        """
        ...

    def delete(self, item_id: str) -> None:
        """Delete an item.

        Args:
            item_id: Identifier of the item to delete.
        """
        ...

    def exists(self, item_id: str) -> bool:
        """Check if an item exists.

        Args:
            item_id: Identifier to check.

        Returns:
            True if item exists, False otherwise.
        """
        ...

    def get(self, item_id: str) -> Item | None:
        """Get an item.

        Args:
            item_id: Identifier of the item.

        Returns:
            Item if found, otherwise None.
        """
        ...
