"""Sync service for verifying and synchronizing local state."""

import shutil
from pathlib import Path

from gda.errors import HashMismatchError
from gda.models.lockfile import LockedAsset, Lockfile
from gda.protocols.archive import ArchiveServiceProtocol
from gda.protocols.github import GitHubClientProtocol


class SyncService:
    """Service for synchronizing local filesystem with lockfile state."""

    def __init__(
        self,
        github_client: GitHubClientProtocol,
        archive_service: ArchiveServiceProtocol,
        working_dir: Path,
    ) -> None:
        """Initialize sync service.

        Args:
            github_client: GitHub API client.
            archive_service: Archive service for extraction.
            working_dir: Working directory (where gda.yml lives).
        """
        self.github_client = github_client
        self.archive_service = archive_service
        self.working_dir = working_dir
        self._cache_dir = working_dir / ".gda" / "cache"

    def verify_asset(self, asset: LockedAsset, dest_dir: Path) -> bool:
        """Verify that local files match the locked asset.

        Args:
            asset: Locked asset to verify.
            dest_dir: Destination directory.

        Returns:
            True if all files exist and match, False otherwise.
        """
        if not asset.files:
            return False
        if not dest_dir.exists():
            return False

        for file in asset.files:
            file_path = dest_dir / file
            if not file_path.exists():
                return False

        return True

    def pull_asset(
        self,
        asset: LockedAsset,
        dest_dir: Path,
        force: bool = False,
    ) -> list[str]:
        """Pull and extract an asset.

        Args:
            asset: Locked asset to pull.
            dest_dir: Destination directory.
            force: Skip verification and re-download.

        Returns:
            List of extracted files.

        Raises:
            HashMismatchError: If downloaded content doesn't match hash.
        """
        # Check if already in sync
        if not force and self.verify_asset(asset, dest_dir):
            return asset.files

        # Download to cache
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        zip_name = f"{asset.name}.zip"
        zip_path = self._cache_dir / zip_name

        self.github_client.download_asset(asset.url, zip_path)

        # Verify hash
        actual_hash = self.archive_service.compute_hash(zip_path)
        if actual_hash != asset.sha256:
            zip_path.unlink()
            raise HashMismatchError(asset.name, asset.sha256, actual_hash)

        # Clean destination and extract
        if dest_dir.exists():
            shutil.rmtree(dest_dir)

        try:
            extracted = self.archive_service.extract_zip(zip_path, dest_dir)
        finally:
            if zip_path.exists():
                zip_path.unlink()
            if self._cache_dir.exists() and not any(self._cache_dir.iterdir()):
                self._cache_dir.rmdir()
        return extracted

    def pull_all(
        self,
        lockfile: Lockfile,
        asset_destinations: dict[str, Path],
        force: bool = False,
        prune: bool = True,
    ) -> dict[str, list[str]]:
        """Pull all assets from lockfile.

        Args:
            lockfile: Lockfile with asset definitions.
            asset_destinations: Map of asset name to destination directory.
            force: Skip verification and re-download.
            prune: Remove files not governed by lockfile.

        Returns:
            Map of asset name to list of extracted files.
        """
        results: dict[str, list[str]] = {}

        for name, asset in lockfile.assets.items():
            dest_dir = asset_destinations.get(name)
            if dest_dir is None:
                continue

            files = self.pull_asset(asset, dest_dir, force=force)
            results[name] = files

            if prune:
                self._prune_directory(dest_dir, set(files))

        return results

    def _prune_directory(self, directory: Path, keep_files: set[str]) -> None:
        """Remove files not in the keep set.

        Args:
            directory: Directory to prune.
            keep_files: Set of relative file paths to keep.
        """
        if not directory.exists():
            return

        for file_path in directory.rglob("*"):
            if not file_path.is_file():
                continue

            rel_path = str(file_path.relative_to(directory))
            if rel_path not in keep_files:
                file_path.unlink()

        # Remove empty directories
        for dir_path in sorted(directory.rglob("*"), reverse=True):
            if dir_path.is_dir() and not any(dir_path.iterdir()):
                dir_path.rmdir()
