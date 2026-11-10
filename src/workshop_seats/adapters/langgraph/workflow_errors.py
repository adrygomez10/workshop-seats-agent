"""Failures that the LangGraph workflow may raise while answering."""

from typing import Final

from anthropic import APIError
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from workshop_seats.adapters.langgraph.unexpected_selection_error import (
    UnexpectedSelectionError,
)

WORKFLOW_ERRORS: Final[tuple[type[Exception], ...]] = (
    APIError,
    OutputParserException,
    ValidationError,
    UnexpectedSelectionError,
)
