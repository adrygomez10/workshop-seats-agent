"""Test double that returns a prepared answer."""

from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


class FakeAssistant:
    """Record each question and return the same prepared answer."""

    def __init__(
        self,
        answer: AvailabilityReport | ClarificationRequest,
    ) -> None:
        """Keep the answer that every call will return."""
        self.answer = answer
        self.questions: list[str] = []
        self.catalogs: list[WorkshopCatalog] = []

    def ask(
        self,
        question: str,
        catalog: WorkshopCatalog,
    ) -> AvailabilityReport | ClarificationRequest:
        """Record the call and return the prepared answer."""
        self.questions.append(question)
        self.catalogs.append(catalog)
        return self.answer
