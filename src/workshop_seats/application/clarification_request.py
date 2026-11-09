"""Answer that asks the person which workshop they mean."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ClarificationRequest:
    """Question returned when the workshop cannot be identified."""

    message: str
