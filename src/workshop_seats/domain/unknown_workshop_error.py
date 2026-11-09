"""Error for workshop names that the catalog does not contain."""


class UnknownWorkshopError(LookupError):
    """Raised when a workshop name is not present in the catalog."""

    def __init__(self, workshop_name: str) -> None:
        """Keep the rejected name for the caller."""
        super().__init__(f"Unknown workshop: {workshop_name}")
        self.workshop_name = workshop_name
