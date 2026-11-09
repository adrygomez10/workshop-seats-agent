"""Check how the use case accepts or rejects the assistant's answers."""

import unittest

from tests.fake_assistant import FakeAssistant
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.check_availability import CheckAvailability
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.application.inconsistent_report_error import (
    InconsistentReportError,
)
from workshop_seats.domain.unknown_workshop_error import UnknownWorkshopError
from workshop_seats.domain.workshop_catalog import WorkshopCatalog

QUESTION = "¿Cuántas plazas quedan para Fotografía nocturna?"


class CheckAvailabilityTests(unittest.TestCase):
    """Verify reports against the catalog before returning them."""

    def setUp(self) -> None:
        """Prepare the catalog used by every case."""
        self.catalog = WorkshopCatalog(
            {"Fotografía nocturna": 3, "Cerámica": 0}
        )

    def test_returns_a_report_that_matches_the_catalog(self) -> None:
        """Pass the question and catalog to the assistant."""
        report = AvailabilityReport("Fotografía nocturna", 3)
        assistant = FakeAssistant(report)

        answer = CheckAvailability(assistant, self.catalog).execute(QUESTION)

        self.assertEqual(report, answer)
        self.assertEqual([QUESTION], assistant.questions)
        self.assertEqual([self.catalog], assistant.catalogs)

    def test_returns_a_clarification_unchanged(self) -> None:
        """Accept a question back when the workshop is not identified."""
        clarification = ClarificationRequest("¿De qué taller?")
        use_case = CheckAvailability(
            FakeAssistant(clarification), self.catalog
        )

        self.assertEqual(clarification, use_case.execute("¿Quedan plazas?"))

    def test_rejects_a_valid_report_with_other_seats(self) -> None:
        """Do not accept thirty seats when the catalog has three."""
        report = AvailabilityReport("Fotografía nocturna", 30)
        use_case = CheckAvailability(FakeAssistant(report), self.catalog)

        with self.assertRaises(InconsistentReportError) as raised:
            use_case.execute(QUESTION)
        self.assertEqual(3, raised.exception.catalog_seats)
        self.assertEqual(report, raised.exception.report)

    def test_rejects_a_report_for_an_unknown_workshop(self) -> None:
        """Keep the catalog as the authority on supported workshops."""
        report = AvailabilityReport("Pintura", 2)
        use_case = CheckAvailability(FakeAssistant(report), self.catalog)

        with self.assertRaises(UnknownWorkshopError):
            use_case.execute("¿Quedan plazas para Pintura?")

    def test_rejects_a_blank_question_before_calling_the_assistant(
        self,
    ) -> None:
        """Avoid a model call when there is nothing to answer."""
        assistant = FakeAssistant(ClarificationRequest("¿De qué taller?"))

        with self.assertRaises(ValueError):
            CheckAvailability(assistant, self.catalog).execute("  ")
        self.assertEqual([], assistant.questions)
