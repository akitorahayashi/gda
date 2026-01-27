"""Unit tests for item storage implementations."""

from pathlib import Path

import pytest

from typ_tmpl.errors import ItemExistsError, ItemNotFoundError
from typ_tmpl.models.item import Item
from typ_tmpl.services.item_storage import ItemStorage


class TestItemStorage:
    """Tests for ItemStorage."""

    @pytest.fixture
    def item_storage(self, tmp_path: Path) -> ItemStorage:
        """Create an ItemStorage with a temp directory."""
        return ItemStorage(base_dir=tmp_path)

    def test_add_creates_file(self, item_storage: ItemStorage) -> None:
        """Test that add creates a file."""
        item_storage.add(Item(id="test-item", content="Test content"))

        assert (item_storage.base_dir / "test-item.txt").exists()
        assert (item_storage.base_dir / "test-item.txt").read_text() == "Test content"

    def test_add_duplicate_raises_error(self, item_storage: ItemStorage) -> None:
        """Test that adding duplicate item raises ItemExistsError."""
        item_storage.add(Item(id="item", content="Content"))

        with pytest.raises(ItemExistsError) as exc_info:
            item_storage.add(Item(id="item", content="New content"))

        assert exc_info.value.id == "item"

    def test_add_rejects_path_separators(self, item_storage: ItemStorage) -> None:
        """Test that add rejects item IDs with path separators."""
        with pytest.raises(ValueError, match="contains path separators"):
            item_storage.add(Item(id="bad/item", content="Content"))

    def test_list_returns_items(self, item_storage: ItemStorage) -> None:
        """Test that list returns items."""
        item_storage.add(Item(id="item1", content="Content 1"))
        item_storage.add(Item(id="item2", content="Content 2"))

        items = item_storage.list()

        assert items == [
            Item(id="item1", content="Content 1"),
            Item(id="item2", content="Content 2"),
        ]

    def test_list_empty(self, item_storage: ItemStorage) -> None:
        """Test that list returns empty list when no items."""
        items = item_storage.list()

        assert items == []

    def test_delete_removes_file(self, item_storage: ItemStorage) -> None:
        """Test that delete removes the file."""
        item_storage.add(Item(id="to-delete", content="Content"))
        assert item_storage.exists("to-delete")

        item_storage.delete("to-delete")

        assert not item_storage.exists("to-delete")

    def test_delete_nonexistent_raises_error(self, item_storage: ItemStorage) -> None:
        """Test that deleting nonexistent item raises ItemNotFoundError."""
        with pytest.raises(ItemNotFoundError) as exc_info:
            item_storage.delete("nonexistent")

        assert exc_info.value.id == "nonexistent"

    def test_exists_true(self, item_storage: ItemStorage) -> None:
        """Test that exists returns True for existing item."""
        item_storage.add(Item(id="existing", content="Content"))

        assert item_storage.exists("existing") is True

    def test_exists_false(self, item_storage: ItemStorage) -> None:
        """Test that exists returns False for nonexistent item."""
        assert item_storage.exists("nonexistent") is False

    def test_get_returns_item(self, item_storage: ItemStorage) -> None:
        """Test that get returns item content."""
        item_storage.add(Item(id="item", content="Test content"))

        item = item_storage.get("item")

        assert item == Item(id="item", content="Test content")

    def test_get_nonexistent_returns_none(self, item_storage: ItemStorage) -> None:
        """Test that get returns None for nonexistent item."""
        item = item_storage.get("nonexistent")

        assert item is None
