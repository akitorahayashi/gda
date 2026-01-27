# GDA - GitHub Data Assets

CLI tool for managing large data assets using GitHub Releases as a backend.

## Installation

```sh
pipx install git+https://github.com/akitorahayashi/gda.git
```

## Usage

### Configuration

Create a `gda.yaml` manifest in your project:

```yaml
repository: "owner/repo"
version: "v1.0.0"

assets:
  raw-data:
    source: "raw-data"
    destination: "data/raw"
    excludes: ["**/.DS_Store"]
```

### Commands

| Command | Description |
|---------|-------------|
| `gda resolve` | Resolve dependencies and update gda.lock |
| `gda pull` | Synchronize local filesystem to match gda.lock |
| `gda push` | Create archives and upload to GitHub Release |

### Workflow

```sh
# 1. Resolve: Fetch release metadata and create lockfile
gda resolve

# 2. Pull: Download and extract assets
gda pull

# 3. Push: Upload local changes to GitHub Release
gda push --dry-run  # Preview
gda push            # Upload
```

### Options

```sh
gda resolve --manifest path/to/gda.yaml
gda pull --force              # Force re-download
gda pull --no-prune           # Keep untracked files
gda push --dry-run            # Preview without uploading
gda push --force              # Overwrite existing assets
```

## File Structure

- `gda.yaml` - User-defined manifest (version, repository, assets)
- `gda.lock` - System-generated lockfile (URLs, hashes)
- `.gda/cache/` - Downloaded asset cache
- `.gda/build/` - Built archives for upload

## Development

```sh
git clone https://github.com/akitorahayashi/gda.git
cd gda
uv sync
uv run gda --help
```

### Testing

```sh
just test           # Run all tests
just unit-test      # Unit tests only
just intg-test      # Integration tests only
just check          # Lint and type check
```

## Project Structure

```
gda/
├── src/gda/
│   ├── __init__.py
│   ├── __main__.py       # module entry point
│   ├── main.py           # Typer app + container setup
│   ├── context.py        # AppContext for DI
│   ├── errors.py         # Application errors
│   ├── commands/         # resolve, pull, push
│   ├── models/           # Manifest, Lockfile
│   ├── protocols/        # GitHubClient, ArchiveService
│   └── services/         # Service implementations
├── dev/
│   └── mocks/            # Mock implementations for testing
├── tests/
├── justfile
└── pyproject.toml
```
