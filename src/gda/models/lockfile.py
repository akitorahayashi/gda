"""Lockfile model representing gda.lock state."""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gda.errors import LockfileCorruptedError, LockfileNotFoundError


@dataclass
class LockedAsset:
    """Locked asset state."""

    name: str
    url: str
    sha256: str
    files: list[str] = field(default_factory=list)


@dataclass
class Lockfile:
    """Lockfile state from gda.lock."""

    version: str
    assets: dict[str, LockedAsset]

    @classmethod
    def load(cls, path: Path) -> "Lockfile":
        """Load lockfile from a JSON file.

        Args:
            path: Path to gda.lock.

        Returns:
            Parsed Lockfile.

        Raises:
            LockfileNotFoundError: If the file does not exist.
            LockfileCorruptedError: If the file is invalid.
        """
        if not path.exists():
            raise LockfileNotFoundError(str(path))

        try:
            content = path.read_text(encoding="utf-8")
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise LockfileCorruptedError(f"JSON parse error: {e}")

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: Any) -> "Lockfile":
        """Parse lockfile from dictionary.

        Args:
            data: Parsed JSON data.

        Returns:
            Lockfile instance.

        Raises:
            LockfileCorruptedError: If required fields are missing.
        """
        if not isinstance(data, dict):
            raise LockfileCorruptedError("Root must be an object")

        version = data.get("version")
        if not version:
            raise LockfileCorruptedError("Missing required field: version")

        raw_assets = data.get("assets", {})
        if not isinstance(raw_assets, dict):
            raise LockfileCorruptedError("assets must be an object")

        assets: dict[str, LockedAsset] = {}
        for name, spec in raw_assets.items():
            if not isinstance(spec, dict):
                raise LockfileCorruptedError(f"Asset '{name}' must be an object")

            url = spec.get("url")
            if not url:
                raise LockfileCorruptedError(
                    f"Asset '{name}' missing required field: url"
                )

            sha256 = spec.get("sha256")
            if not sha256:
                raise LockfileCorruptedError(
                    f"Asset '{name}' missing required field: sha256"
                )

            files = spec.get("files", [])
            if not isinstance(files, list):
                raise LockfileCorruptedError(f"Asset '{name}' files must be a list")

            assets[name] = LockedAsset(
                name=name,
                url=url,
                sha256=sha256,
                files=files,
            )

        return cls(version=version, assets=assets)

    def save(self, path: Path) -> None:
        """Save lockfile to a JSON file.

        Args:
            path: Path to write gda.lock.
        """
        data = {
            "version": self.version,
            "assets": {
                name: {
                    "url": asset.url,
                    "sha256": asset.sha256,
                    "files": asset.files,
                }
                for name, asset in self.assets.items()
            },
        }
        path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
