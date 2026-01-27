"""Application context for dependency injection."""

from dataclasses import dataclass

from typ_tmpl.protocols.item_storage import ItemStorageProtocol


@dataclass
class AppContext:
    """Application context holding dependencies."""

    item_storage: ItemStorageProtocol
