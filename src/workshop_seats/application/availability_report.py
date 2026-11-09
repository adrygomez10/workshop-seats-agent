"""Answer that reports the seats of one workshop."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class AvailabilityReport:
    """Seats that the assistant reports for a workshop."""

    workshop_name: str
    available_seats: int
