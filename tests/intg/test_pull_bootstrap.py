"""Integration tests for pull bootstrap flow."""

import json
from pathlib import Path

from typer import Typer
from typer.testing import CliRunner

from dev.mocks.github import MockGitHubClient
from gda.services.archive import ArchiveService


def test_pull_bootstraps_lock_and_cleans_cache(
    cli_runner: CliRunner,
    tmp_path: Path,
    app_with_mocks: Typer,
    mock_github_client: MockGitHubClient,
    archive_service: ArchiveService,
) -> None:
    """Pull without lockfile resolves, installs, and cleans cache."""
    manifest_path = tmp_path / "gda.yml"
    manifest_path.write_text(
        """
repository: "owner/repo"
version: "v1.0.0"
assets:
  data:
    source: "source"
    destination: "output"
""".lstrip()
    )

    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "file.txt").write_text("content", encoding="utf-8")

    zip_path = tmp_path / "data.zip"
    archive_service.create_zip(source_dir, zip_path)
    mock_github_client.add_release(
        "owner/repo",
        "v1.0.0",
        assets=[("data.zip", zip_path.read_bytes())],
    )

    result = cli_runner.invoke(app_with_mocks, ["pull", "-m", str(manifest_path)])

    assert result.exit_code == 0
    assert (tmp_path / "output" / "file.txt").read_text(encoding="utf-8") == "content"

    lockfile_path = tmp_path / "gda.lock"
    assert lockfile_path.exists()
    lock_data = json.loads(lockfile_path.read_text(encoding="utf-8"))
    assert "file.txt" in lock_data["assets"]["data"]["files"]

    cache_dir = tmp_path / ".gda" / "cache"
    assert not cache_dir.exists()
