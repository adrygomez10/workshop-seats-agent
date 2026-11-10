"""Run the LangGraph workflow with scripted selections."""

import unittest

from langchain_core.runnables import RunnableLambda

from tests.recording_selector import RecordingSelector
from workshop_seats.adapters.langgraph.demo_selector import (
    select_mentioned_workshop,
)
from workshop_seats.adapters.langgraph.lang_graph_assistant import (
    SELECTION_INSTRUCTIONS,
    LangGraphAssistant,
)
from workshop_seats.adapters.langgraph.unexpected_selection_error import (
    UnexpectedSelectionError,
)
from workshop_seats.adapters.langgraph.workflow_steps import CLARIFICATION
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


class LangGraphAssistantTests(unittest.TestCase):
    """Follow the selection, the decision and the catalog lookup."""

    def setUp(self) -> None:
        """Use counts that differ from the demo data to prove the lookup."""
        self.catalog = WorkshopCatalog(
            {"Fotografía nocturna": 7, "Cerámica": 0}
        )
        self.selector = RecordingSelector(select_mentioned_workshop)
        self.assistant = LangGraphAssistant(RunnableLambda(self.selector))

    def test_reports_the_seats_read_from_the_catalog(self) -> None:
        """Select the workshop once and read its seats in the graph."""
        answer = self.assistant.ask(
            "¿Cuántas plazas quedan para Fotografía nocturna?",
            self.catalog,
        )

        self.assertEqual(AvailabilityReport("Fotografía nocturna", 7), answer)
        self.assertEqual(1, len(self.selector.inputs))

    def test_selector_receives_instructions_and_question(self) -> None:
        """Send the selection rules and the person's message."""
        self.assistant.ask("¿Quedan plazas para Cerámica?", self.catalog)

        self.assertEqual(
            [
                ("system", SELECTION_INSTRUCTIONS),
                ("human", "¿Quedan plazas para Cerámica?"),
            ],
            self.selector.inputs[0],
        )

    def test_zero_seats_is_a_valid_report(self) -> None:
        """Answer a full workshop instead of asking for clarification."""
        answer = self.assistant.ask(
            "¿Quedan plazas para Cerámica?", self.catalog
        )

        self.assertEqual(AvailabilityReport("Cerámica", 0), answer)

    def test_returns_the_fixed_clarification_without_a_workshop(self) -> None:
        """Follow the clarification path when nothing is selected."""
        answer = self.assistant.ask("¿Cuántas plazas quedan?", self.catalog)

        self.assertEqual(ClarificationRequest(CLARIFICATION), answer)

    def test_rejects_a_selector_that_returns_another_type(self) -> None:
        """Fail instead of reading an untyped answer."""
        assistant = LangGraphAssistant(
            RunnableLambda(lambda _: {"workshop_name": "Cerámica"})
        )

        with self.assertRaises(UnexpectedSelectionError):
            assistant.ask("¿Quedan plazas para Cerámica?", self.catalog)
