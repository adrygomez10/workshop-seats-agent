"""Workshop selector built with LangChain's Anthropic integration."""

from langchain.chat_models import init_chat_model
from langchain_core.language_models import LanguageModelInput
from langchain_core.runnables import Runnable

from workshop_seats.adapters.langgraph.workshop_selection import (
    WorkshopSelection,
)


def create_anthropic_selector(
    model_name: str,
) -> Runnable[LanguageModelInput, object]:
    """Return a model configured to answer with a ``WorkshopSelection``."""
    model = init_chat_model(
        model_name,
        model_provider="anthropic",
        timeout=20.0,
        max_retries=0,
        max_tokens=256,
    )
    return model.with_structured_output(
        WorkshopSelection,
        method="json_schema",
    )
