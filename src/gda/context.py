"""Application context for dependency injection."""

from dataclasses import dataclass, field
from pathlib import Path

from gda.protocols.archive import ArchiveServiceProtocol
from gda.protocols.github import GitHubClientProtocol


@dataclass
class AppContext:
    """Application context holding dependencies."""

    github_client: GitHubClientProtocol
    archive_service: ArchiveServiceProtocol
    working_dir: Path = field(default_factory=Path.cwd)
