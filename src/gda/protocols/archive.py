"""Archive service protocol definition."""

from pathlib import Path
from typing import Protocol


class ArchiveServiceProtocol(Protocol):
    """Protocol for deterministic archive operations."""

    def create_zip(
        self,
        source_dir: Path,
        output_path: Path,
        excludes: list[str] | None = None,
    ) -> str:
        """Create a deterministic ZIP archive.

        Args:
            source_dir: Directory to archive.
            output_path: Path for output ZIP file.
            excludes: Glob patterns to exclude.

        Returns:
            SHA256 hash of the created archive.

        Note:
            File timestamps are reset to epoch for reproducibility.
            Filenames are encoded as UTF-8.
        """
        ...

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> list[str]:
        """Extract a ZIP archive.

        Args:
            zip_path: Path to ZIP file.
            dest_dir: Destination directory.

        Returns:
            List of extracted file paths (relative to dest_dir).
        """
        ...

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file.

        Args:
            file_path: Path to file.

        Returns:
            SHA256 hex digest.
        """
        ...

    def list_zip_contents(self, zip_path: Path) -> list[str]:
        """List contents of a ZIP archive.

        Args:
            zip_path: Path to ZIP file.

        Returns:
            List of file paths in the archive.
        """
        ...
