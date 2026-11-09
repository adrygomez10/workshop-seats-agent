"""Model responses that exercise failure paths of the agent."""

from pydantic_ai.messages import ModelMessage, ModelResponse, ToolCallPart
from pydantic_ai.models.function import AgentInfo


def negative_seats_response(
    messages: list[ModelMessage],
    info: AgentInfo,
) -> ModelResponse:
    """Propose a final answer that breaks the output rules."""
    arguments = {"workshop_name": "Cerámica", "available_seats": -1}
    output_tool = info.output_tools[0].name
    return ModelResponse(parts=[ToolCallPart(output_tool, arguments)])


def endless_tool_response(
    messages: list[ModelMessage],
    info: AgentInfo,
) -> ModelResponse:
    """Keep requesting the tool instead of finishing."""
    arguments = {"workshop_name": "Cerámica"}
    return ModelResponse(
        parts=[ToolCallPart("get_available_seats", arguments)]
    )
