"""Text shown in the console for each kind of answer."""

from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)


def format_answer(answer: AvailabilityReport | ClarificationRequest) -> str:
    """Present a report or a clarification without changing its data."""
    if isinstance(answer, ClarificationRequest):
        return f"Aclaración: {answer.message}"

    return (
        f"Taller: {answer.workshop_name}\n"
        f"Plazas disponibles: {answer.available_seats}"
    )
