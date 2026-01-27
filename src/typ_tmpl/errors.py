"""Application error definitions."""


class AppError(Exception):
    """Base application error."""

    pass


class ItemNotFoundError(AppError):
    """Raised when an item is not found."""

    def __init__(self, id: str) -> None:
        self.id = id
        super().__init__(f"Item '{id}' not found")


class ItemExistsError(AppError):
    """Raised when an item already exists."""

    def __init__(self, id: str) -> None:
        self.id = id
        super().__init__(f"Item '{id}' already exists")
