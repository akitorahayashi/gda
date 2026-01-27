"""Unit tests for manifest model."""

from pathlib import Path

import pytest

from gda.errors import ManifestNotFoundError, ManifestValidationError
from gda.models.manifest import Asset, Manifest


class TestManifest:
    """Tests for Manifest loading and validation."""

    def test_load_valid_manifest(self, tmp_path: Path) -> None:
        """Test loading a valid manifest file."""
        manifest_path = tmp_path / "gda.yml"
        manifest_path.write_text("""
repository: "owner/repo"
version: "v1.0.0"

assets:
  raw-data:
    source: "raw-data"
    destination: "data/raw"
    excludes: ["**/.DS_Store"]
""")

        manifest = Manifest.load(manifest_path)

        assert manifest.repository == "owner/repo"
        assert manifest.version == "v1.0.0"
        assert "raw-data" in manifest.assets
        assert manifest.assets["raw-data"].source == "raw-data"
        assert manifest.assets["raw-data"].destination == "data/raw"
        assert manifest.assets["raw-data"].excludes == ["**/.DS_Store"]

    def test_load_manifest_not_found(self, tmp_path: Path) -> None:
        """Test loading a non-existent manifest raises error."""
        manifest_path = tmp_path / "missing.yaml"

        with pytest.raises(ManifestNotFoundError) as exc_info:
            Manifest.load(manifest_path)

        assert "missing.yaml" in exc_info.value.path

    def test_load_manifest_missing_repository(self, tmp_path: Path) -> None:
        """Test manifest without repository field raises error."""
        manifest_path = tmp_path / "gda.yml"
        manifest_path.write_text("""
version: "v1.0.0"
assets: {}
""")

        with pytest.raises(ManifestValidationError) as exc_info:
            Manifest.load(manifest_path)

        assert "repository" in str(exc_info.value)

    def test_load_manifest_missing_version(self, tmp_path: Path) -> None:
        """Test manifest without version field raises error."""
        manifest_path = tmp_path / "gda.yml"
        manifest_path.write_text("""
repository: "owner/repo"
assets: {}
""")

        with pytest.raises(ManifestValidationError) as exc_info:
            Manifest.load(manifest_path)

        assert "version" in str(exc_info.value)

    def test_load_manifest_missing_asset_destination(self, tmp_path: Path) -> None:
        """Test asset without destination field raises error."""
        manifest_path = tmp_path / "gda.yml"
        manifest_path.write_text("""
repository: "owner/repo"
version: "v1.0.0"
assets:
  data:
    source: "data"
""")

        with pytest.raises(ManifestValidationError) as exc_info:
            Manifest.load(manifest_path)

        assert "destination" in str(exc_info.value)

    def test_load_manifest_default_source(self, tmp_path: Path) -> None:
        """Test that source defaults to asset name."""
        manifest_path = tmp_path / "gda.yml"
        manifest_path.write_text("""
repository: "owner/repo"
version: "v1.0.0"
assets:
  my-data:
    destination: "data/output"
""")

        manifest = Manifest.load(manifest_path)

        assert manifest.assets["my-data"].source == "my-data"

    def test_save_manifest(self, tmp_path: Path) -> None:
        """Test saving a manifest to file."""
        manifest = Manifest(
            repository="owner/repo",
            version="v2.0.0",
            assets={
                "data": Asset(
                    name="data",
                    source="raw",
                    destination="output/data",
                    excludes=["*.tmp"],
                )
            },
        )

        output_path = tmp_path / "gda.yml"
        manifest.save(output_path)

        # Reload and verify
        loaded = Manifest.load(output_path)
        assert loaded.repository == "owner/repo"
        assert loaded.version == "v2.0.0"
        assert loaded.assets["data"].destination == "output/data"
