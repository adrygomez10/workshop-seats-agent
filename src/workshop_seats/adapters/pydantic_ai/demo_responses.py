"""Scripted model responses for running the workshop without an account.

The rules below are not a language model. They only look for a workshop
name in the question, request the tool and build the final answer with
the number that the tool returned. This lets the agent, its tool and the
output validation run without network access or an API key.
"""

from typing import Any

from pydantic_ai.messages import (
    ModelMessage,
    ModelRequest,
    ModelResponse,
    TextPart,
    ToolCallPart,
    ToolReturnPart,
    UserPromptPart,
)
from pydantic_ai.models.function import AgentInfo, FunctionModel

SEATS_TOOL = "get_available_seats"
CLARIFICATION = "¿De qué taller quieres consultar las plazas?"


def create_demo_model() -> FunctionModel:
    """Return the scripted model used by the ``--demo`` option."""
    return FunctionModel(scripted_response, model_name="demo")


def scripted_response(
    messages: list[ModelMessage],
    info: AgentInfo,
) -> ModelResponse:
    """Imitate the two model steps of the article with fixed rules."""
    returned = _returned_seats(messages)
    if returned is not None:
        workshop_name, seats = returned
        output_tool = info.output_tools[0].name
        arguments = {"workshop_name": workshop_name, "available_seats": seats}
        return ModelResponse(parts=[ToolCallPart(output_tool, arguments)])

    mentioned = _mentioned_workshop(_question(messages), info)
    if mentioned is None:
        return ModelResponse(parts=[TextPart(CLARIFICATION)])
    arguments = {"workshop_name": mentioned}
    return ModelResponse(parts=[ToolCallPart(SEATS_TOOL, arguments)])


def _question(messages: list[ModelMessage]) -> str:
    """Return the text that the person sent in the first request."""
    for message in messages:
        if not isinstance(message, ModelRequest):
            continue
        for part in message.parts:
            if isinstance(part, UserPromptPart) and isinstance(
                part.content, str
            ):
                return part.content
    return ""


def _mentioned_workshop(question: str, info: AgentInfo) -> str | None:
    """Find a supported workshop name written in the question."""
    tool = next(t for t in info.function_tools if t.name == SEATS_TOOL)
    schema: dict[str, Any] = tool.parameters_json_schema
    names: list[str] = schema["properties"]["workshop_name"]["enum"]
    for name in names:
        if name.casefold() in question.casefold():
            return name
    return None


def _returned_seats(messages: list[ModelMessage]) -> tuple[str, int] | None:
    """Pair the requested workshop with the seats returned by the tool."""
    requested: dict[str, str] = {}
    for message in messages:
        for part in message.parts:
            if isinstance(part, ToolCallPart) and part.tool_name == SEATS_TOOL:
                arguments = part.args_as_dict()
                requested[part.tool_call_id] = arguments["workshop_name"]
            elif isinstance(part, ToolReturnPart) and isinstance(
                part.content, int
            ):
                workshop_name = requested[part.tool_call_id]
                return workshop_name, part.content
    return None
