"""Scripted selection for running the workflow without an account.

The rule below is not a language model. It only looks for a supported
workshop name in the person's message. The graph, its decision and the
catalog lookup run as they would with a real model.
"""

from typing import get_args

from langchain_core.language_models import LanguageModelInput
from langchain_core.prompt_values import PromptValue
from langchain_core.runnables import Runnable, RunnableLambda

from workshop_seats.adapters.langgraph.workshop_selection import (
    WorkshopSelection,
)
from workshop_seats.adapters.workshop_name import WorkshopName


def create_demo_selector() -> Runnable[LanguageModelInput, object]:
    """Return the scripted selector used by the ``--demo`` option."""
    return RunnableLambda(select_mentioned_workshop)


def select_mentioned_workshop(
    messages: LanguageModelInput,
) -> WorkshopSelection:
    """Select the supported workshop written in the message, if any."""
    question = _human_text(messages).casefold()
    for name in get_args(WorkshopName):
        if name.casefold() in question:
            return WorkshopSelection(workshop_name=name)
    return WorkshopSelection(workshop_name=None)


def _human_text(messages: LanguageModelInput) -> str:
    """Return the text written by the person."""
    if isinstance(messages, str):
        return messages
    if isinstance(messages, PromptValue):
        return messages.to_string()

    texts = [
        str(message[1])
        for message in messages
        if isinstance(message, tuple) and message[0] == "human"
    ]
    return " ".join(texts)
