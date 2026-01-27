"""Unit tests for AppContext."""

from typ_tmpl.context import AppContext


class TestAppContext:
    """Tests for AppContext."""

    def test_context_holds_storage(self) -> None:
        """Test that context can hold a storage instance."""
        from dev.mocks.item_storage import MockItemStorage

        mock = MockItemStorage()
        ctx = AppContext(item_storage=mock)

        assert ctx.item_storage is mock
