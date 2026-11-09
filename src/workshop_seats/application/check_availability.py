"""Use case that answers a question about workshop seats."""

from workshop_seats.application.availability_assistant import (
    AvailabilityAssistant,
)
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.application.inconsistent_report_error import (
    InconsistentReportError,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


class CheckAvailability:
    """Ask the assistant and accept only reports that match the catalog."""

    def __init__(
        self,
        assistant: AvailabilityAssistant,
        catalog: WorkshopCatalog,
    ) -> None:
        """Receive the assistant and the catalog it must consult."""
        self._assistant = assistant
        self._catalog = catalog

    def execute(
        self,
        question: str,
    ) -> AvailabilityReport | ClarificationRequest:
        """Return a verified report or the assistant's clarification."""
        if not question.strip():
            raise ValueError("The question cannot be blank.")

        answer = self._assistant.ask(question, self._catalog)
        if isinstance(answer, ClarificationRequest):
            return answer

        catalog_seats = self._catalog.seats_for(answer.workshop_name)
        if answer.available_seats != catalog_seats:
            raise InconsistentReportError(answer, catalog_seats)
        return answer
