"""GDA protocols."""

from gda.protocols.archive import ArchiveServiceProtocol
from gda.protocols.github import AssetInfo, GitHubClientProtocol, ReleaseInfo

__all__ = [
    "GitHubClientProtocol",
    "ReleaseInfo",
    "AssetInfo",
    "ArchiveServiceProtocol",
]
