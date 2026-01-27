# typ-tmpl

## Overview

Minimal Typer CLI template with item CRUD functionality, protocol-based DI, and filesystem-backed item storage.

## CLI Commands

| Command | Alias | Description |
|---------|-------|-------------|
| `typ-tmpl add <id> -c <content>` | `a` | Add a new item |
| `typ-tmpl list` | `ls` | List all items |
| `typ-tmpl delete <id>` | `rm` | Delete an item |

## Package Structure

```
src/typ_tmpl/
├── main.py                 # Typer CLI + container setup
├── context.py              # AppContext dataclass (DI container)
├── errors.py               # Application errors
├── commands/               # CLI command implementations
├── models/                 # Item data models
├── protocols/              # Service protocols
├── services/               # Service implementations
└── __main__.py             # Module entry point

dev/
└── mocks/                  # Mock implementations for testing
```

## Dependency Injection

`ctx.obj` holds `AppContext` with `item_storage`.

## Protocols and Services

`ItemStorageProtocol` defines the interface used by `ItemStorage` and `MockItemStorage`.
Item IDs are validated to reject path separators.

## Testing

`MockItemStorage` lives in `dev/mocks/` and the `app_with_mock_item_storage` fixture injects it. Unit tests use `tmp_path` for `ItemStorage`.
