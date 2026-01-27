"""Mock item storage implementation for testing."""

from dataclasses import dataclass, field
from typing import Any

from typ_tmpl.errors import ItemExistsError, ItemNotFoundError
from typ_tmpl.models.item import Item
from typ_tmpl.protocols.item_storage import ItemStorageProtocol


@dataclass
class MockItemStorage(ItemStorageProtocol):
    """Mock item storage for testing."""

    items: dict[str, Item] = field(default_factory=dict)
    calls: list[tuple[str, tuple[Any, ...]]] = field(default_factory=list)

    def _validate_item_id(self, item_id: str) -> None:
        if "/" in item_id or "\\" in item_id:
            raise ValueError(f"Invalid item ID '{item_id}': contains path separators.")

    def add(self, item: Item) -> None:
        """Add a new item."""
        self._validate_item_id(item.id)
        self.calls.append(("add", (item,)))
        if item.id in self.items:
            raise ItemExistsError(item.id)
        self.items[item.id] = item

    def list(self) -> list[Item]:
        """List all items."""
        self.calls.append(("list", ()))
        return [self.items[item_id] for item_id in sorted(self.items.keys())]

    def delete(self, item_id: str) -> None:
        """Delete an item."""
        self._validate_item_id(item_id)
        self.calls.append(("delete", (item_id,)))
        if item_id not in self.items:
            raise ItemNotFoundError(item_id)
        del self.items[item_id]

    def exists(self, item_id: str) -> bool:
        """Check if an item exists."""
        self._validate_item_id(item_id)
        self.calls.append(("exists", (item_id,)))
        return item_id in self.items

    def get(self, item_id: str) -> Item | None:
        """Get an item."""
        self._validate_item_id(item_id)
        self.calls.append(("get", (item_id,)))
        return self.items.get(item_id)
