"""Port for the component that interprets availability questions."""

from typing import Protocol

from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


class AvailabilityAssistant(Protocol):
    """Interpret a question and consult the catalog to answer it."""

    def ask(
        self,
        question: str,
        catalog: WorkshopCatalog,
    ) -> AvailabilityReport | ClarificationRequest:
        """Return the reported seats or a question for the person."""
        ...
