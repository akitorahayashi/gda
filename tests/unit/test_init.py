"""Unit tests for init command helpers."""

from pathlib import Path

from gda.commands.init import _ensure_gitignore, _render_manifest, _write_manifest


class TestInitHelpers:
    """Tests for init helper functions."""

    def test_render_manifest_includes_values(self) -> None:
        content = _render_manifest("owner/repo", "0.1.0")

        assert 'repository: "owner/repo"' in content
        assert 'version: "0.1.0"' in content
        assert "assets:" in content

    def test_write_manifest_respects_overwrite(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "gda.yml"
        manifest_path.write_text("original", encoding="utf-8")

        written = _write_manifest(manifest_path, "new", overwrite=False)

        assert written is False
        assert manifest_path.read_text(encoding="utf-8") == "original"

        written = _write_manifest(manifest_path, "new", overwrite=True)

        assert written is True
        assert manifest_path.read_text(encoding="utf-8") == "new"

    def test_ensure_gitignore_appends_once(self, tmp_path: Path) -> None:
        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("dist/\n", encoding="utf-8")

        changed = _ensure_gitignore(gitignore)

        assert changed is True
        content = gitignore.read_text(encoding="utf-8")
        assert ".gda/" in content

        changed = _ensure_gitignore(gitignore)

        assert changed is False
        assert gitignore.read_text(encoding="utf-8") == content
        assert content.count(".gda/") == 1

    def test_ensure_gitignore_creates_file(self, tmp_path: Path) -> None:
        gitignore = tmp_path / ".gitignore"

        changed = _ensure_gitignore(gitignore)

        assert changed is True
        content = gitignore.read_text(encoding="utf-8")
        assert ".gda/" in content
