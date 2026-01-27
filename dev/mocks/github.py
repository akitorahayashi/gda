"""Mock GitHub client for testing."""

import hashlib
from pathlib import Path

from gda.errors import ReleaseNotFoundError
from gda.protocols.github import AssetInfo, ReleaseInfo


class MockGitHubClient:
    """Mock implementation of GitHubClientProtocol for testing."""

    def __init__(self) -> None:
        """Initialize mock client with empty state."""
        self.releases: dict[tuple[str, str], ReleaseInfo] = {}
        self.assets: dict[str, bytes] = {}
        self.upload_history: list[tuple[str, str, str, bytes]] = []

    def add_release(
        self,
        repo: str,
        tag: str,
        assets: list[tuple[str, bytes]] | None = None,
        release_id: int = 1,
    ) -> ReleaseInfo:
        """Add a mock release.

        Args:
            repo: Repository in "owner/repo" format.
            tag: Release tag name.
            assets: List of (name, content) tuples.
            release_id: Mock release ID.

        Returns:
            Created release info.
        """
        asset_list = []
        for name, content in assets or []:
            url = f"https://github.com/{repo}/releases/download/{tag}/{name}"
            self.assets[url] = content
            asset_list.append(
                AssetInfo(
                    name=name,
                    url=url,
                    size=len(content),
                    content_type="application/zip",
                )
            )

        release = ReleaseInfo(id=release_id, tag_name=tag, name=tag, assets=asset_list)
        self.releases[(repo, tag)] = release
        return release

    def get_release(self, repo: str, tag: str) -> ReleaseInfo:
        """Get release information by tag.

        Args:
            repo: Repository in "owner/repo" format.
            tag: Release tag name.

        Returns:
            Release metadata.

        Raises:
            ReleaseNotFoundError: If the release does not exist.
        """
        key = (repo, tag)
        if key not in self.releases:
            raise ReleaseNotFoundError(repo, tag)
        return self.releases[key]

    def download_asset(self, url: str, dest: Path) -> None:
        """Download a release asset.

        Args:
            url: Asset download URL.
            dest: Destination file path.
        """
        content = self.assets.get(url, b"")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(content)

    def get_asset_hash(self, url: str) -> str:
        """Get SHA256 hash of a remote asset.

        Args:
            url: Asset download URL.

        Returns:
            SHA256 hex digest.
        """
        content = self.assets.get(url, b"")
        return hashlib.sha256(content).hexdigest()

    def create_release(self, repo: str, tag: str, name: str) -> ReleaseInfo:
        """Create a new release.

        Args:
            repo: Repository in "owner/repo" format.
            tag: Release tag name.
            name: Release name.

        Returns:
            Created release metadata.
        """
        release = ReleaseInfo(id=1, tag_name=tag, name=name, assets=[])
        self.releases[(repo, tag)] = release
        return release

    def upload_asset(
        self, repo: str, release_id: int, name: str, content: bytes, content_type: str
    ) -> AssetInfo:
        """Upload an asset to a release.

        Args:
            repo: Repository in "owner/repo" format.
            release_id: Release ID (ignored in mock).
            name: Asset filename.
            content: Asset content bytes.
            content_type: MIME type.

        Returns:
            Uploaded asset metadata.
        """
        self.upload_history.append((repo, str(release_id), name, content))
        url = f"https://github.com/{repo}/releases/download/mock/{name}"
        self.assets[url] = content

        return AssetInfo(
            name=name,
            url=url,
            size=len(content),
            content_type=content_type,
        )

    def close(self) -> None:
        """Close the mock client (no-op)."""
        pass
