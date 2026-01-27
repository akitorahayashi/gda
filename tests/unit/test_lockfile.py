"""Unit tests for lockfile model."""

from pathlib import Path

import pytest

from gda.errors import LockfileCorruptedError, LockfileNotFoundError
from gda.models.lockfile import LockedAsset, Lockfile


class TestLockfile:
    """Tests for Lockfile loading and serialization."""

    def test_load_valid_lockfile(self, tmp_path: Path) -> None:
        """Test loading a valid lockfile."""
        lockfile_path = tmp_path / "gda.lock"
        lockfile_path.write_text("""{
  "version": "v1.0.0",
  "assets": {
    "raw-data": {
      "url": "https://github.com/owner/repo/releases/download/v1.0.0/raw-data.zip",
      "sha256": "abc123def456",
      "files": ["file1.txt", "dir/file2.png"]
    }
  }
}
""")

        lockfile = Lockfile.load(lockfile_path)

        assert lockfile.version == "v1.0.0"
        assert "raw-data" in lockfile.assets
        assert lockfile.assets["raw-data"].sha256 == "abc123def456"
        assert lockfile.assets["raw-data"].files == ["file1.txt", "dir/file2.png"]

    def test_load_lockfile_not_found(self, tmp_path: Path) -> None:
        """Test loading a non-existent lockfile raises error."""
        lockfile_path = tmp_path / "missing.lock"

        with pytest.raises(LockfileNotFoundError) as exc_info:
            Lockfile.load(lockfile_path)

        assert "missing.lock" in exc_info.value.path

    def test_load_lockfile_invalid_json(self, tmp_path: Path) -> None:
        """Test loading invalid JSON raises error."""
        lockfile_path = tmp_path / "gda.lock"
        lockfile_path.write_text("{ invalid json }")

        with pytest.raises(LockfileCorruptedError) as exc_info:
            Lockfile.load(lockfile_path)

        assert "JSON parse error" in str(exc_info.value)

    def test_load_lockfile_missing_version(self, tmp_path: Path) -> None:
        """Test lockfile without version field raises error."""
        lockfile_path = tmp_path / "gda.lock"
        lockfile_path.write_text('{"assets": {}}')

        with pytest.raises(LockfileCorruptedError) as exc_info:
            Lockfile.load(lockfile_path)

        assert "version" in str(exc_info.value)

    def test_load_lockfile_missing_asset_url(self, tmp_path: Path) -> None:
        """Test asset without url field raises error."""
        lockfile_path = tmp_path / "gda.lock"
        lockfile_path.write_text("""{
  "version": "v1.0.0",
  "assets": {
    "data": {
      "sha256": "abc123"
    }
  }
}
""")

        with pytest.raises(LockfileCorruptedError) as exc_info:
            Lockfile.load(lockfile_path)

        assert "url" in str(exc_info.value)

    def test_save_lockfile(self, tmp_path: Path) -> None:
        """Test saving a lockfile to file."""
        lockfile = Lockfile(
            version="v2.0.0",
            assets={
                "data": LockedAsset(
                    name="data",
                    url="https://example.com/data.zip",
                    sha256="abc123",
                    files=["file1.txt"],
                )
            },
        )

        output_path = tmp_path / "gda.lock"
        lockfile.save(output_path)

        # Reload and verify
        loaded = Lockfile.load(output_path)
        assert loaded.version == "v2.0.0"
        assert loaded.assets["data"].url == "https://example.com/data.zip"

    def test_lockfile_empty_files_list(self, tmp_path: Path) -> None:
        """Test lockfile with empty files list."""
        lockfile_path = tmp_path / "gda.lock"
        lockfile_path.write_text("""{
  "version": "v1.0.0",
  "assets": {
    "data": {
      "url": "https://example.com/data.zip",
      "sha256": "abc123"
    }
  }
}
""")

        lockfile = Lockfile.load(lockfile_path)
        assert lockfile.assets["data"].files == []
