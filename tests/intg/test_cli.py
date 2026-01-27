"""Integration tests for CLI commands."""

from pathlib import Path

from typer.testing import CliRunner

from gda.main import app


class TestCLIIntegration:
    """Integration tests for CLI command interactions."""

    def test_version_flag_shows_version(self, cli_runner: CliRunner) -> None:
        """Test that --version flag shows version information."""
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "gda version:" in result.output

    def test_short_version_flag_shows_version(self, cli_runner: CliRunner) -> None:
        """Test that -V flag shows version information."""
        result = cli_runner.invoke(app, ["-V"])

        assert result.exit_code == 0
        assert "gda version:" in result.output

    def test_help_flag_shows_help(self, cli_runner: CliRunner) -> None:
        """Test that --help flag shows help information."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "gda" in result.output
        assert "resolve" in result.output
        assert "pull" in result.output
        assert "push" in result.output

    def test_no_args_shows_help(self, cli_runner: CliRunner) -> None:
        """Test that running without arguments shows help."""
        result = cli_runner.invoke(app, [])

        assert "Usage:" in result.output or "gda" in result.output


class TestResolveCommand:
    """Tests for the resolve command."""

    def test_resolve_missing_manifest(
        self, cli_runner: CliRunner, tmp_path: Path
    ) -> None:
        """Test resolve with missing manifest shows error."""
        result = cli_runner.invoke(
            app, ["resolve", "-m", str(tmp_path / "missing.yaml")]
        )

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "Error" in result.output


class TestPullCommand:
    """Tests for the pull command."""

    def test_pull_missing_manifest(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test pull with missing manifest shows error."""
        result = cli_runner.invoke(app, ["pull", "-m", str(tmp_path / "missing.yaml")])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "Error" in result.output

    def test_pull_missing_lockfile(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test pull with missing lockfile shows error."""
        manifest_path = tmp_path / "gda.yaml"
        manifest_path.write_text("""
repository: "owner/repo"
version: "v1.0.0"
assets:
  data:
    destination: "output"
""")

        result = cli_runner.invoke(app, ["pull", "-m", str(manifest_path)])

        assert result.exit_code == 1
        assert "resolve" in result.output.lower() or "lock" in result.output.lower()


class TestPushCommand:
    """Tests for the push command."""

    def test_push_missing_manifest(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test push with missing manifest shows error."""
        result = cli_runner.invoke(app, ["push", "-m", str(tmp_path / "missing.yaml")])

        assert result.exit_code == 1
        assert "not found" in result.output.lower() or "Error" in result.output

    def test_push_dry_run(self, cli_runner: CliRunner, tmp_path: Path) -> None:
        """Test push with dry-run doesn't upload."""
        manifest_path = tmp_path / "gda.yaml"
        manifest_path.write_text("""
repository: "owner/repo"
version: "v1.0.0"
assets:
  data:
    source: "source"
    destination: "output"
""")

        # Create source directory
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")

        result = cli_runner.invoke(app, ["push", "-m", str(manifest_path), "--dry-run"])

        assert result.exit_code == 0
        assert "dry run" in result.output.lower()
