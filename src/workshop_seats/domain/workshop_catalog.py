"""Workshop seats known by the application."""

from collections.abc import Mapping
from types import MappingProxyType

from workshop_seats.domain.unknown_workshop_error import UnknownWorkshopError


class WorkshopCatalog:
    """Read-only availability for the workshops offered by the application."""

    def __init__(self, seats_by_workshop: Mapping[str, int]) -> None:
        """Copy the catalog after checking its names and seat counts."""
        if not seats_by_workshop:
            raise ValueError("The catalog needs at least one workshop.")
        for name, seats in seats_by_workshop.items():
            if not name.strip():
                raise ValueError("Workshop names cannot be blank.")
            if isinstance(seats, bool) or seats < 0:
                raise ValueError(f"Seats for {name} must be zero or more.")

        self._seats_by_workshop = MappingProxyType(dict(seats_by_workshop))

    @property
    def workshop_names(self) -> tuple[str, ...]:
        """Return the supported names in catalog order."""
        return tuple(self._seats_by_workshop)

    def seats_for(self, workshop_name: str) -> int:
        """Return the available seats without reserving any of them."""
        if workshop_name not in self._seats_by_workshop:
            raise UnknownWorkshopError(workshop_name)

        return self._seats_by_workshop[workshop_name]
