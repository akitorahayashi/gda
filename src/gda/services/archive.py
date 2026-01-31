"""Deterministic archive service implementation."""

import fnmatch
import hashlib
import zipfile
from pathlib import Path

# Fixed timestamp for reproducible archives (2020-01-01 00:00:00)
FIXED_TIMESTAMP = (2020, 1, 1, 0, 0, 0)


class ArchiveService:
    """Service for creating and extracting deterministic ZIP archives."""

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
            File timestamps are reset for reproducibility.
            Filenames are encoded as UTF-8.
        """
        excludes = excludes or []
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Collect files, sorted for determinism
        files = self._collect_files(source_dir, excludes)

        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for file_path in files:
                rel_path = file_path.relative_to(source_dir)
                # Create ZipInfo with fixed timestamp and UTF-8 encoding
                info = zipfile.ZipInfo(
                    filename=str(rel_path).replace("\\", "/"),
                    date_time=FIXED_TIMESTAMP,
                )
                info.compress_type = zipfile.ZIP_DEFLATED

                with open(file_path, "rb") as f:
                    zf.writestr(info, f.read())

        return self.compute_hash(output_path)

    def _collect_files(self, source_dir: Path, excludes: list[str]) -> list[Path]:
        """Collect files to archive, respecting excludes.

        Args:
            source_dir: Source directory.
            excludes: Glob patterns to exclude.

        Returns:
            Sorted list of file paths.
        """
        files: list[Path] = []

        for file_path in source_dir.rglob("*"):
            if not file_path.is_file():
                continue

            rel_path = str(file_path.relative_to(source_dir))
            if self._matches_exclude(rel_path, excludes):
                continue

            files.append(file_path)

        # Sort for deterministic ordering
        return sorted(files, key=lambda p: str(p.relative_to(source_dir)))

    def _matches_exclude(self, rel_path: str, excludes: list[str]) -> bool:
        """Check if path matches any exclude pattern.

        Args:
            rel_path: Relative file path.
            excludes: Glob patterns.

        Returns:
            True if path should be excluded.
        """
        for pattern in excludes:
            # Handle ** patterns by matching basename too
            if pattern.startswith("**/"):
                basename_pattern = pattern[3:]
                basename = rel_path.split("/")[-1]
                if fnmatch.fnmatch(basename, basename_pattern):
                    return True
            if fnmatch.fnmatch(rel_path, pattern):
                return True
        return False

    def extract_zip(self, zip_path: Path, dest_dir: Path) -> list[str]:
        """Extract a ZIP archive.

        Args:
            zip_path: Path to ZIP file.
            dest_dir: Destination directory.

        Returns:
            List of extracted file paths (relative to dest_dir).
        """
        dest_dir.mkdir(parents=True, exist_ok=True)
        extracted: list[str] = []

        with zipfile.ZipFile(zip_path, "r") as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue

                # Handle UTF-8 and CP932 encoding
                try:
                    name = info.filename.encode("cp437").decode("utf-8")
                except (UnicodeDecodeError, UnicodeEncodeError):
                    try:
                        name = info.filename.encode("cp437").decode("cp932")
                    except (UnicodeDecodeError, UnicodeEncodeError):
                        name = info.filename

                target = dest_dir / name
                target.parent.mkdir(parents=True, exist_ok=True)

                with zf.open(info) as src, open(target, "wb") as dst:
                    dst.write(src.read())

                extracted.append(name)

        return sorted(extracted)

    def compute_hash(self, file_path: Path) -> str:
        """Compute SHA256 hash of a file.

        Args:
            file_path: Path to file.

        Returns:
            SHA256 hex digest.
        """
        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def list_zip_contents(self, zip_path: Path) -> list[str]:
        """List contents of a ZIP archive.

        Args:
            zip_path: Path to ZIP file.

        Returns:
            List of file paths in the archive.
        """
        with zipfile.ZipFile(zip_path, "r") as zf:
            return sorted(info.filename for info in zf.infolist() if not info.is_dir())
