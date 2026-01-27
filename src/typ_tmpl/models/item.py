"""Item data model."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Item:
    """Stored item representation."""

    id: str
    content: str
