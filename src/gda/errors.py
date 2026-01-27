"""Application errors for GDA."""


class GDAError(Exception):
    """Base error for GDA operations."""

    pass


class ManifestNotFoundError(GDAError):
    """Raised when gda.yml is not found."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Manifest not found: {path}")


class ManifestValidationError(GDAError):
    """Raised when gda.yml is invalid."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Invalid manifest: {message}")


class LockfileNotFoundError(GDAError):
    """Raised when gda.lock is not found."""

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Lockfile not found: {path}. Run 'gda resolve' first.")


class LockfileCorruptedError(GDAError):
    """Raised when gda.lock is corrupted."""

    def __init__(self, message: str) -> None:
        super().__init__(f"Corrupted lockfile: {message}")


class AssetNotFoundError(GDAError):
    """Raised when an asset is not found."""

    def __init__(self, asset_name: str) -> None:
        self.asset_name = asset_name
        super().__init__(f"Asset not found: {asset_name}")


class HashMismatchError(GDAError):
    """Raised when a downloaded asset's hash does not match."""

    def __init__(self, asset_name: str, expected: str, actual: str) -> None:
        self.asset_name = asset_name
        self.expected = expected
        self.actual = actual
        super().__init__(
            f"Hash mismatch for {asset_name}: expected {expected[:16]}..., got {actual[:16]}..."
        )


class GitHubAPIError(GDAError):
    """Raised when a GitHub API call fails."""

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        super().__init__(f"GitHub API error ({status_code}): {message}")


class ReleaseNotFoundError(GDAError):
    """Raised when a release is not found."""

    def __init__(self, repo: str, version: str) -> None:
        self.repo = repo
        self.version = version
        super().__init__(f"Release not found: {repo}@{version}")
