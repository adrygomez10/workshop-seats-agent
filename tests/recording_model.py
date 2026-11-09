"""Callable that keeps what the agent sends to a scripted model."""

from collections.abc import Callable

from pydantic_ai.messages import ModelMessage, ModelResponse
from pydantic_ai.models.function import AgentInfo

Respond = Callable[[list[ModelMessage], AgentInfo], ModelResponse]


class RecordingModel:
    """Store the messages and tool descriptions of each model request."""

    def __init__(self, respond: Respond) -> None:
        """Delegate each answer to the given scripted function."""
        self._respond = respond
        self.requests: list[list[ModelMessage]] = []
        self.infos: list[AgentInfo] = []

    def __call__(
        self,
        messages: list[ModelMessage],
        info: AgentInfo,
    ) -> ModelResponse:
        """Record the request and return the scripted response."""
        self.requests.append(list(messages))
        self.infos.append(info)
        return self._respond(messages, info)
