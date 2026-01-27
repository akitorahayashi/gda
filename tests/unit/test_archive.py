"""Unit tests for archive service."""

from pathlib import Path

import pytest

from gda.services.archive import ArchiveService


class TestArchiveService:
    """Tests for ArchiveService."""

    @pytest.fixture
    def archive_service(self) -> ArchiveService:
        """Create an archive service."""
        return ArchiveService()

    def test_create_zip_basic(
        self, archive_service: ArchiveService, tmp_path: Path
    ) -> None:
        """Test creating a basic ZIP archive."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "file1.txt").write_text("content 1")
        (source / "file2.txt").write_text("content 2")

        output = tmp_path / "output.zip"
        sha256 = archive_service.create_zip(source, output)

        assert output.exists()
        assert len(sha256) == 64  # SHA256 hex length
        assert archive_service.list_zip_contents(output) == ["file1.txt", "file2.txt"]

    def test_create_zip_with_subdirectories(
        self, archive_service: ArchiveService, tmp_path: Path
    ) -> None:
        """Test creating ZIP with nested directories."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "dir1").mkdir()
        (source / "dir1" / "file.txt").write_text("nested")
        (source / "root.txt").write_text("root")

        output = tmp_path / "output.zip"
        archive_service.create_zip(source, output)

        contents = archive_service.list_zip_contents(output)
        assert "dir1/file.txt" in contents
        assert "root.txt" in contents

    def test_create_zip_with_excludes(
        self, archive_service: ArchiveService, tmp_path: Path
    ) -> None:
        """Test creating ZIP with exclusion patterns."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "keep.txt").write_text("keep")
        (source / ".DS_Store").write_text("exclude")
        (source / "cache").mkdir()
        (source / "cache" / "temp.txt").write_text("exclude")

        output = tmp_path / "output.zip"
        archive_service.create_zip(source, output, excludes=["**/.DS_Store", "cache/*"])

        contents = archive_service.list_zip_contents(output)
        assert "keep.txt" in contents
        assert ".DS_Store" not in contents
        assert "cache/temp.txt" not in contents

    def test_create_zip_deterministic(
        self, archive_service: ArchiveService, tmp_path: Path
    ) -> None:
        """Test that ZIP creation is deterministic."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")

        output1 = tmp_path / "output1.zip"
        output2 = tmp_path / "output2.zip"

        hash1 = archive_service.create_zip(source, output1)
        hash2 = archive_service.create_zip(source, output2)

        assert hash1 == hash2
        assert output1.read_bytes() == output2.read_bytes()

    def test_extract_zip(self, archive_service: ArchiveService, tmp_path: Path) -> None:
        """Test extracting a ZIP archive."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "file1.txt").write_text("content 1")
        (source / "subdir").mkdir()
        (source / "subdir" / "file2.txt").write_text("content 2")

        zip_path = tmp_path / "archive.zip"
        archive_service.create_zip(source, zip_path)

        dest = tmp_path / "extracted"
        files = archive_service.extract_zip(zip_path, dest)

        assert "file1.txt" in files
        assert "subdir/file2.txt" in files
        assert (dest / "file1.txt").read_text() == "content 1"
        assert (dest / "subdir" / "file2.txt").read_text() == "content 2"

    def test_compute_hash(
        self, archive_service: ArchiveService, tmp_path: Path
    ) -> None:
        """Test computing file hash."""
        file_path = tmp_path / "test.txt"
        file_path.write_bytes(b"test content")

        hash1 = archive_service.compute_hash(file_path)
        hash2 = archive_service.compute_hash(file_path)

        assert hash1 == hash2
        assert len(hash1) == 64

    def test_list_zip_contents(
        self, archive_service: ArchiveService, tmp_path: Path
    ) -> None:
        """Test listing ZIP contents."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "a.txt").write_text("a")
        (source / "b.txt").write_text("b")
        (source / "dir").mkdir()
        (source / "dir" / "c.txt").write_text("c")

        zip_path = tmp_path / "archive.zip"
        archive_service.create_zip(source, zip_path)

        contents = archive_service.list_zip_contents(zip_path)

        assert contents == ["a.txt", "b.txt", "dir/c.txt"]
