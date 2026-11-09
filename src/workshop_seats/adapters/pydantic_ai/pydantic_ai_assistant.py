"""Availability assistant implemented with a Pydantic AI agent."""

from pydantic_ai import Agent
from pydantic_ai.models import Model
from pydantic_ai.usage import UsageLimits

from workshop_seats.adapters.pydantic_ai.availability import Availability
from workshop_seats.adapters.pydantic_ai.seat_tools import (
    get_available_seats,
)
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog

INSTRUCTIONS = (
    "Use get_available_seats before reporting workshop availability. "
    "Return Availability with the selected workshop and returned count. "
    "If the workshop is missing, unsupported, or ambiguous, ask for "
    "clarification in Spanish as plain text. Never claim a reservation."
)
DEFAULT_USAGE_LIMITS = UsageLimits(request_limit=3, tool_calls_limit=2)


class PydanticAiAssistant:
    """Let the model consult the catalog and validate its final answer."""

    def __init__(
        self,
        model: Model | str,
        usage_limits: UsageLimits = DEFAULT_USAGE_LIMITS,
    ) -> None:
        """Configure the agent, its tool and the usage limits per question."""
        self._agent: Agent[WorkshopCatalog, Availability | str] = Agent(
            model,
            deps_type=WorkshopCatalog,
            output_type=[Availability, str],
            instructions=INSTRUCTIONS,
            tools=[get_available_seats],
            model_settings={"timeout": 20.0},
            retries=0,
        )
        self._usage_limits = usage_limits

    def ask(
        self,
        question: str,
        catalog: WorkshopCatalog,
    ) -> AvailabilityReport | ClarificationRequest:
        """Run the agent once and translate its validated output."""
        result = self._agent.run_sync(
            question,
            deps=catalog,
            usage_limits=self._usage_limits,
        )

        output = result.output
        if isinstance(output, str):
            return ClarificationRequest(message=output)
        return AvailabilityReport(
            workshop_name=output.workshop_name,
            available_seats=output.available_seats,
        )
