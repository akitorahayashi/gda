"""Integration tests for CLI commands."""

from typer import Typer
from typer.testing import CliRunner

from dev.mocks.item_storage import MockItemStorage
from typ_tmpl.main import app
from typ_tmpl.models.item import Item


class TestCLIIntegration:
    """Integration tests for CLI command interactions."""

    def test_version_flag_shows_version(self, cli_runner: CliRunner) -> None:
        """Test that --version flag shows version information."""
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "typ-tmpl version:" in result.output

    def test_short_version_flag_shows_version(self, cli_runner: CliRunner) -> None:
        """Test that -V flag shows version information."""
        result = cli_runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert "typ-tmpl version:" in result.output

    def test_help_flag_shows_help(self, cli_runner: CliRunner) -> None:
        """Test that --help flag shows help information."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "typ-tmpl" in result.output
        assert "add" in result.output
        assert "list" in result.output
        assert "delete" in result.output

    def test_no_args_shows_help(self, cli_runner: CliRunner) -> None:
        """Test that running without arguments shows help."""
        result = cli_runner.invoke(app, [])

        assert "Usage:" in result.output or "typ-tmpl" in result.output


class TestAddCommand:
    """Tests for the add command."""

    def test_add_item(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test adding an item."""
        result = cli_runner.invoke(
            app_with_mock_item_storage, ["add", "note1", "-c", "Test content"]
        )

        assert result.exit_code == 0
        assert "Added" in result.output and "note1" in result.output
        assert mock_item_storage.items["note1"].content == "Test content"

    def test_add_alias(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test that 'a' alias works."""
        result = cli_runner.invoke(
            app_with_mock_item_storage, ["a", "note2", "--content", "More content"]
        )

        assert result.exit_code == 0
        assert "Added" in result.output and "note2" in result.output

    def test_add_duplicate_fails(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test that adding duplicate item fails."""
        mock_item_storage.items["existing"] = Item(
            id="existing",
            content="Old content",
        )

        result = cli_runner.invoke(
            app_with_mock_item_storage, ["add", "existing", "-c", "New content"]
        )

        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_add_rejects_path_separators(
        self, cli_runner: CliRunner, app_with_mock_item_storage: Typer
    ) -> None:
        """Test that add rejects item IDs with path separators."""
        result = cli_runner.invoke(
            app_with_mock_item_storage, ["add", "bad/item", "-c", "Content"]
        )

        assert result.exit_code == 1
        assert "contains path separators" in result.output


class TestListCommand:
    """Tests for the list command."""

    def test_list_empty(
        self, cli_runner: CliRunner, app_with_mock_item_storage: Typer
    ) -> None:
        """Test listing when no items exist."""
        result = cli_runner.invoke(app_with_mock_item_storage, ["list"])

        assert result.exit_code == 0
        assert "No items found" in result.output

    def test_list_items(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test listing items."""
        mock_item_storage.items["note1"] = Item(id="note1", content="Content 1")
        mock_item_storage.items["note2"] = Item(id="note2", content="Content 2")

        result = cli_runner.invoke(app_with_mock_item_storage, ["list"])

        assert result.exit_code == 0
        assert "note1" in result.output
        assert "note2" in result.output

    def test_list_alias(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test that 'ls' alias works."""
        mock_item_storage.items["item1"] = Item(id="item1", content="Content")

        result = cli_runner.invoke(app_with_mock_item_storage, ["ls"])

        assert result.exit_code == 0
        assert "item1" in result.output


class TestDeleteCommand:
    """Tests for the delete command."""

    def test_delete_item(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test deleting an item."""
        mock_item_storage.items["to-delete"] = Item(
            id="to-delete",
            content="Content",
        )

        result = cli_runner.invoke(app_with_mock_item_storage, ["delete", "to-delete"])

        assert result.exit_code == 0
        assert "Deleted" in result.output and "to-delete" in result.output
        assert "to-delete" not in mock_item_storage.items

    def test_delete_alias(
        self,
        cli_runner: CliRunner,
        app_with_mock_item_storage: Typer,
        mock_item_storage: MockItemStorage,
    ) -> None:
        """Test that 'rm' alias works."""
        mock_item_storage.items["item"] = Item(id="item", content="Content")

        result = cli_runner.invoke(app_with_mock_item_storage, ["rm", "item"])

        assert result.exit_code == 0
        assert "Deleted" in result.output and "item" in result.output

    def test_delete_nonexistent_fails(
        self, cli_runner: CliRunner, app_with_mock_item_storage: Typer
    ) -> None:
        """Test that deleting nonexistent item fails."""
        result = cli_runner.invoke(
            app_with_mock_item_storage, ["delete", "nonexistent"]
        )

        assert result.exit_code == 1
        assert "not found" in result.output

    def test_delete_rejects_path_separators(
        self, cli_runner: CliRunner, app_with_mock_item_storage: Typer
    ) -> None:
        """Test that delete rejects item IDs with path separators."""
        result = cli_runner.invoke(app_with_mock_item_storage, ["delete", "bad/item"])

        assert result.exit_code == 1
        assert "contains path separators" in result.output
