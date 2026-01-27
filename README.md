# typ-tmpl

Minimal Python CLI template using Typer with item CRUD functionality.

## Installation

pipx installation is supported.

```sh
pipx install git+https://github.com/akitorahayashi/typ-tmpl.git
```

Example CLI usage:

```sh
typ-tmpl --version
typ-tmpl --help
typ-tmpl add note1 -c "My first note"
typ-tmpl list
typ-tmpl delete note1
```

## Development

Local development uses uv and the justfile tasks.

### Setup

Setup commands commonly used:

```sh
git clone https://github.com/akitorahayashi/typ-tmpl.git
cd typ-tmpl
uv sync
```

### Run

Example commands:

```sh
uv run typ-tmpl --help
uv run typ-tmpl add note1 -c "Hello"
uv run typ-tmpl a note2 --content "World"  # alias
uv run typ-tmpl list
uv run typ-tmpl ls                          # alias
uv run typ-tmpl delete note1
uv run typ-tmpl rm note2                    # alias
```

### Test and Lint

Common tasks:

```sh
just test    # run tests
just check   # ruff format --check, ruff check, mypy
just fix     # auto-format
```

## Project Structure

```
typ-tmpl/
├── src/typ_tmpl/
│   ├── __init__.py
│   ├── __main__.py       # module entry point
│   ├── main.py           # Typer app + container setup
│   ├── context.py        # AppContext for DI
│   ├── errors.py         # Application errors
│   ├── commands/         # CLI command implementations
│   ├── models/           # Item data models
│   ├── protocols/        # Service protocols
│   └── services/         # Service implementations
├── dev/
│   └── mocks/            # Mock implementations for testing
├── tests/
├── justfile
└── pyproject.toml
```

## Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `typ-tmpl add <id> -c <content>` | `a` | Add a new item |
| `typ-tmpl list` | `ls` | List all items |
| `typ-tmpl delete <id>` | `rm` | Delete an item |

## Storage

Items are stored in `~/.config/typ-tmpl/items/` as individual `.txt` files via the `ItemStorage` service.
Item IDs do not contain path separators.
