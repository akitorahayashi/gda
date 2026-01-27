"""GitHub client protocol definition."""

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol


@dataclass
class AssetInfo:
    """GitHub release asset metadata."""

    name: str
    url: str
    size: int
    content_type: str


@dataclass
class ReleaseInfo:
    """GitHub release metadata."""

    tag_name: str
    name: str
    assets: list[AssetInfo]


class GitHubClientProtocol(Protocol):
    """Protocol for GitHub API operations."""

    def get_release(self, repo: str, tag: str) -> ReleaseInfo:
        """Get release information by tag.

        Args:
            repo: Repository in "owner/repo" format.
            tag: Release tag name.

        Returns:
            Release metadata.

        Raises:
            ReleaseNotFoundError: If the release does not exist.
            GitHubAPIError: If the API call fails.
        """
        ...

    def download_asset(self, url: str, dest: Path) -> None:
        """Download a release asset.

        Args:
            url: Asset download URL.
            dest: Destination file path.

        Raises:
            GitHubAPIError: If the download fails.
        """
        ...

    def get_asset_hash(self, url: str) -> str:
        """Get SHA256 hash of a remote asset.

        Args:
            url: Asset download URL.

        Returns:
            SHA256 hex digest.

        Raises:
            GitHubAPIError: If the request fails.
        """
        ...

    def create_release(self, repo: str, tag: str, name: str) -> ReleaseInfo:
        """Create a new release.

        Args:
            repo: Repository in "owner/repo" format.
            tag: Release tag name.
            name: Release name.

        Returns:
            Created release metadata.

        Raises:
            GitHubAPIError: If the API call fails.
        """
        ...

    def upload_asset(
        self, repo: str, release_id: int, name: str, content: bytes, content_type: str
    ) -> AssetInfo:
        """Upload an asset to a release.

        Args:
            repo: Repository in "owner/repo" format.
            release_id: Release ID.
            name: Asset filename.
            content: Asset content bytes.
            content_type: MIME type.

        Returns:
            Uploaded asset metadata.

        Raises:
            GitHubAPIError: If the upload fails.
        """
        ...
