"""Test double that records the messages sent to the selector."""

from collections.abc import Callable

from langchain_core.language_models import LanguageModelInput


class RecordingSelector:
    """Keep each input and delegate the answer to a prepared function."""

    def __init__(
        self, respond: Callable[[LanguageModelInput], object]
    ) -> None:
        """Receive the function that builds each selection."""
        self.respond = respond
        self.inputs: list[LanguageModelInput] = []

    def __call__(self, messages: LanguageModelInput) -> object:
        """Record the messages and return the prepared answer."""
        self.inputs.append(messages)
        return self.respond(messages)
