"""Data shared by the steps of the LangGraph workflow."""

from typing import TypedDict

from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)


class WorkshopState(TypedDict):
    """Question, selected workshop and answer of one execution."""

    message: str
    workshop_name: str | None
    answer: AvailabilityReport | ClarificationRequest | None
