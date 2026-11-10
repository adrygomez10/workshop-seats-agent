"""Error for a selector that does not return a workshop selection."""


class UnexpectedSelectionError(RuntimeError):
    """Raised when the selector returns something other than a selection."""

    def __init__(self, selection: object) -> None:
        """Name the type that arrived instead of ``WorkshopSelection``."""
        super().__init__(
            f"The selector returned {type(selection).__name__} instead of "
            "WorkshopSelection."
        )
        self.selection = selection
