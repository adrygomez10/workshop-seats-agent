"""Run the Pydantic AI agent with scripted models instead of a real one."""

import unittest

from pydantic_ai.exceptions import UnexpectedModelBehavior, UsageLimitExceeded
from pydantic_ai.messages import ToolReturnPart
from pydantic_ai.models.function import FunctionModel

from tests.recording_model import RecordingModel
from tests.scripted_responses import (
    endless_tool_response,
    negative_seats_response,
)
from workshop_seats.adapters.pydantic_ai.demo_responses import (
    CLARIFICATION,
    scripted_response,
)
from workshop_seats.adapters.pydantic_ai.pydantic_ai_assistant import (
    PydanticAiAssistant,
)
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


class PydanticAiAssistantTests(unittest.TestCase):
    """Follow the tool request, its result and the validated output."""

    def setUp(self) -> None:
        """Use counts that differ from the demo data to prove the lookup."""
        self.catalog = WorkshopCatalog(
            {"Fotografía nocturna": 7, "Cerámica": 0}
        )
        self.recorder = RecordingModel(scripted_response)
        self.assistant = PydanticAiAssistant(FunctionModel(self.recorder))

    def test_reports_the_seats_read_from_the_catalog(self) -> None:
        """Make two model requests around one catalog lookup."""
        answer = self.assistant.ask(
            "¿Cuántas plazas quedan para Fotografía nocturna?",
            self.catalog,
        )

        self.assertEqual(AvailabilityReport("Fotografía nocturna", 7), answer)
        self.assertEqual(2, len(self.recorder.requests))
        tool_returns = [
            part
            for message in self.recorder.requests[1]
            for part in message.parts
            if isinstance(part, ToolReturnPart)
        ]
        self.assertEqual([7], [part.content for part in tool_returns])

    def test_model_receives_a_description_without_the_context(self) -> None:
        """Expose the name, docstring and argument, but not ``ctx``."""
        self.assistant.ask("¿Quedan plazas para Cerámica?", self.catalog)

        (tool,) = self.recorder.infos[0].function_tools
        self.assertEqual("get_available_seats", tool.name)
        self.assertEqual(
            "Read available seats for a supported workshop without reserving.",
            tool.description,
        )
        properties = tool.parameters_json_schema["properties"]
        self.assertEqual(["workshop_name"], list(properties))
        self.assertEqual(
            ["Fotografía nocturna", "Cerámica"],
            properties["workshop_name"]["enum"],
        )

    def test_zero_seats_is_a_valid_report(self) -> None:
        """Report a full workshop instead of treating it as an error."""
        answer = self.assistant.ask(
            "¿Quedan plazas para Cerámica?", self.catalog
        )

        self.assertEqual(AvailabilityReport("Cerámica", 0), answer)

    def test_returns_a_clarification_without_using_the_tool(self) -> None:
        """Ask for the workshop instead of inventing one."""
        answer = self.assistant.ask("¿Cuántas plazas quedan?", self.catalog)

        self.assertEqual(ClarificationRequest(CLARIFICATION), answer)
        self.assertEqual(1, len(self.recorder.requests))

    def test_rejects_an_output_that_breaks_its_rules(self) -> None:
        """Fail instead of returning negative seats."""
        assistant = PydanticAiAssistant(FunctionModel(negative_seats_response))

        with self.assertRaises(UnexpectedModelBehavior):
            assistant.ask("¿Quedan plazas para Cerámica?", self.catalog)

    def test_stops_a_model_that_keeps_requesting_tools(self) -> None:
        """Apply the request and tool call limits."""
        assistant = PydanticAiAssistant(FunctionModel(endless_tool_response))

        with self.assertRaises(UsageLimitExceeded):
            assistant.ask("¿Quedan plazas para Cerámica?", self.catalog)
