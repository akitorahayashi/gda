# GDA - GitHub Data Assets

## Overview

CLI tool for managing large data assets using GitHub Releases as a backend. Functions as a package manager for data with reproducibility, idempotency, and separation of concerns.

## CLI Commands

| Command | Description |
|---------|-------------|
| `gda resolve` | Resolve dependencies from gda.yml, update gda.lock |
| `gda pull` | Synchronize local filesystem to match gda.lock |
| `gda push` | Create archives and upload to GitHub Release |

## Package Structure

```
src/gda/
├── main.py                 # Typer CLI + container setup
├── context.py              # AppContext dataclass (DI container)
├── errors.py               # Application errors
├── commands/               # resolve, pull, push
├── models/                 # Manifest (gda.yml), Lockfile (gda.lock)
├── protocols/              # GitHubClientProtocol, ArchiveServiceProtocol
└── services/               # GitHub, Archive, Sync implementations

dev/
└── mocks/                  # MockGitHubClient for testing
```

## Dependency Injection

`ctx.obj` holds `AppContext` with `github_client` and `archive_service`.

## Protocols and Services

- `GitHubClientProtocol`: GitHub API operations (releases, assets)
- `ArchiveServiceProtocol`: Deterministic ZIP creation/extraction

## Configuration Files

- `gda.yml`: User manifest (repository, version, assets)
- `gda.lock`: System lockfile (URLs, SHA256 hashes, file lists)

## Testing

`MockGitHubClient` in `dev/mocks/` provides isolated testing. Unit tests cover models and archive service. Integration tests cover CLI commands.
