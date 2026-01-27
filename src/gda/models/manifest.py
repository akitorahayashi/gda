"""Manifest model representing gda.yaml configuration."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from gda.errors import ManifestNotFoundError, ManifestValidationError


@dataclass
class Asset:
    """Asset definition in the manifest."""

    name: str
    source: str
    destination: str
    excludes: list[str] = field(default_factory=list)


@dataclass
class Manifest:
    """Manifest configuration from gda.yaml."""

    repository: str
    version: str
    assets: dict[str, Asset]

    @classmethod
    def load(cls, path: Path) -> "Manifest":
        """Load manifest from a YAML file.

        Args:
            path: Path to gda.yaml.

        Returns:
            Parsed Manifest.

        Raises:
            ManifestNotFoundError: If the file does not exist.
            ManifestValidationError: If the file is invalid.
        """
        if not path.exists():
            raise ManifestNotFoundError(str(path))

        try:
            content = path.read_text(encoding="utf-8")
            data = yaml.safe_load(content)
        except yaml.YAMLError as e:
            raise ManifestValidationError(f"YAML parse error: {e}")

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Any) -> "Manifest":
        """Parse manifest from dictionary.

        Args:
            data: Parsed YAML data.

        Returns:
            Manifest instance.

        Raises:
            ManifestValidationError: If required fields are missing.
        """
        if not isinstance(data, dict):
            raise ManifestValidationError("Root must be a mapping")

        repository = data.get("repository")
        if not repository:
            raise ManifestValidationError("Missing required field: repository")

        version = data.get("version")
        if not version:
            raise ManifestValidationError("Missing required field: version")

        raw_assets = data.get("assets", {})
        if not isinstance(raw_assets, dict):
            raise ManifestValidationError("assets must be a mapping")

        assets: dict[str, Asset] = {}
        for name, spec in raw_assets.items():
            if not isinstance(spec, dict):
                raise ManifestValidationError(f"Asset '{name}' must be a mapping")

            source = spec.get("source") or name
            destination = spec.get("destination")
            if not destination:
                raise ManifestValidationError(
                    f"Asset '{name}' missing required field: destination"
                )

            excludes = spec.get("excludes", [])
            if not isinstance(excludes, list):
                raise ManifestValidationError(f"Asset '{name}' excludes must be a list")

            assets[name] = Asset(
                name=name,
                source=source,
                destination=destination,
                excludes=excludes,
            )

        return cls(repository=repository, version=version, assets=assets)

    def save(self, path: Path) -> None:
        """Save manifest to a YAML file.

        Args:
            path: Path to write gda.yaml.
        """
        data = {
            "repository": self.repository,
            "version": self.version,
            "assets": {
                name: {
                    "source": asset.source,
                    "destination": asset.destination,
                    **({"excludes": asset.excludes} if asset.excludes else {}),
                }
                for name, asset in self.assets.items()
            },
        }
        path.write_text(
            yaml.dump(data, default_flow_style=False, allow_unicode=True),
            encoding="utf-8",
        )
