"""GitHub client implementation using httpx."""

import hashlib
import os
from pathlib import Path
from typing import Any

import httpx

from gda.errors import GitHubAPIError, ReleaseNotFoundError
from gda.protocols.github import AssetInfo, ReleaseInfo


class GitHubClient:
    """GitHub API client using httpx."""

    GITHUB_API_URL = "https://api.github.com"

    def __init__(self, token: str | None = None) -> None:
        """Initialize GitHub client.

        Args:
            token: GitHub personal access token. If None, reads from
                   GITHUB_TOKEN or GH_TOKEN environment variables.
        """
        self.token = (
            token or os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
        )
        self._client: httpx.Client | None = None

    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
            if self.token:
                headers["Authorization"] = f"Bearer {self.token}"
            self._client = httpx.Client(
                headers=headers, timeout=30.0, follow_redirects=True
            )
        return self._client

    def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            self._client.close()
            self._client = None

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
        url = f"{self.GITHUB_API_URL}/repos/{repo}/releases/tags/{tag}"
        response = self.client.get(url)

        if response.status_code == 404:
            raise ReleaseNotFoundError(repo, tag)
        if response.status_code != 200:
            raise GitHubAPIError(response.status_code, response.text)

        data = response.json()
        return self._parse_release(data)

    def _parse_release(self, data: dict[str, Any]) -> ReleaseInfo:
        """Parse release data from API response."""
        assets = [
            AssetInfo(
                name=asset["name"],
                url=asset["browser_download_url"],
                size=asset["size"],
                content_type=asset["content_type"],
            )
            for asset in data.get("assets", [])
        ]
        return ReleaseInfo(
            tag_name=data["tag_name"],
            name=data.get("name") or data["tag_name"],
            assets=assets,
        )

    def download_asset(self, url: str, dest: Path) -> None:
        """Download a release asset.

        Args:
            url: Asset download URL.
            dest: Destination file path.

        Raises:
            GitHubAPIError: If the download fails.
        """
        dest.parent.mkdir(parents=True, exist_ok=True)

        with self.client.stream("GET", url) as response:
            if response.status_code != 200:
                raise GitHubAPIError(response.status_code, f"Failed to download {url}")

            with open(dest, "wb") as f:
                for chunk in response.iter_bytes(chunk_size=8192):
                    f.write(chunk)

    def get_asset_hash(self, url: str) -> str:
        """Get SHA256 hash of a remote asset.

        Args:
            url: Asset download URL.

        Returns:
            SHA256 hex digest.

        Raises:
            GitHubAPIError: If the request fails.
        """
        hasher = hashlib.sha256()

        with self.client.stream("GET", url) as response:
            if response.status_code != 200:
                raise GitHubAPIError(response.status_code, f"Failed to fetch {url}")

            for chunk in response.iter_bytes(chunk_size=8192):
                hasher.update(chunk)

        return hasher.hexdigest()

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
        url = f"{self.GITHUB_API_URL}/repos/{repo}/releases"
        response = self.client.post(
            url,
            json={"tag_name": tag, "name": name},
        )

        if response.status_code not in (200, 201):
            raise GitHubAPIError(response.status_code, response.text)

        return self._parse_release(response.json())

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
        url = f"https://uploads.github.com/repos/{repo}/releases/{release_id}/assets"
        response = self.client.post(
            url,
            params={"name": name},
            content=content,
            headers={"Content-Type": content_type},
        )

        if response.status_code not in (200, 201):
            raise GitHubAPIError(response.status_code, response.text)

        data = response.json()
        return AssetInfo(
            name=data["name"],
            url=data["browser_download_url"],
            size=data["size"],
            content_type=data["content_type"],
        )
