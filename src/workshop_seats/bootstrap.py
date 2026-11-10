"""Console entry point that assembles the catalog, assistant and use case."""

import argparse
import os
import sys
from collections.abc import Sequence
from typing import Final

from pydantic_ai.exceptions import AgentRunError

from workshop_seats.adapters.langgraph.anthropic_selector import (
    create_anthropic_selector,
)
from workshop_seats.adapters.langgraph.demo_selector import (
    create_demo_selector,
)
from workshop_seats.adapters.langgraph.lang_graph_assistant import (
    LangGraphAssistant,
)
from workshop_seats.adapters.langgraph.workflow_errors import WORKFLOW_ERRORS
from workshop_seats.adapters.pydantic_ai.demo_responses import (
    create_demo_model,
)
from workshop_seats.adapters.pydantic_ai.pydantic_ai_assistant import (
    PydanticAiAssistant,
)
from workshop_seats.application.availability_assistant import (
    AvailabilityAssistant,
)
from workshop_seats.application.check_availability import CheckAvailability
from workshop_seats.application.inconsistent_report_error import (
    InconsistentReportError,
)
from workshop_seats.catalog_data import DEMO_SEATS_BY_WORKSHOP
from workshop_seats.console_output import format_answer
from workshop_seats.domain.unknown_workshop_error import UnknownWorkshopError
from workshop_seats.domain.workshop_catalog import WorkshopCatalog

DEFAULT_QUESTION = "¿Cuántas plazas quedan para Fotografía nocturna?"
PYDANTIC_AI_ENGINE = "pydantic-ai"
LANGGRAPH_ENGINE = "langgraph"
CONFIGURATION_ERROR = 2
ANSWER_ERRORS: Final[tuple[type[Exception], ...]] = (
    AgentRunError,
    *WORKFLOW_ERRORS,
    InconsistentReportError,
    UnknownWorkshopError,
)


def main(argv: Sequence[str] | None = None) -> int:
    """Answer one question and return the process exit code."""
    os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")
    arguments = _parse_arguments(argv)
    assistant = _create_assistant(arguments.engine, demo=arguments.demo)
    if assistant is None:
        print(
            "Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL, or use --demo.",
            file=sys.stderr,
        )
        return CONFIGURATION_ERROR

    catalog = WorkshopCatalog(DEMO_SEATS_BY_WORKSHOP)
    use_case = CheckAvailability(assistant, catalog)
    try:
        answer = use_case.execute(arguments.question)
    except ANSWER_ERRORS as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(format_answer(answer))
    return 0


def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    """Read the question, the engine and the model mode."""
    parser = argparse.ArgumentParser(
        description="Ask how many seats are left in a workshop.",
    )
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--engine",
        choices=(PYDANTIC_AI_ENGINE, LANGGRAPH_ENGINE),
        default=PYDANTIC_AI_ENGINE,
        help="library that interprets the question",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="use scripted responses instead of a real model",
    )
    return parser.parse_args(argv)


def _create_assistant(
    engine: str,
    *,
    demo: bool,
) -> AvailabilityAssistant | None:
    """Return the assistant of the chosen engine, or None if unconfigured."""
    if demo:
        if engine == LANGGRAPH_ENGINE:
            return LangGraphAssistant(create_demo_selector())
        return PydanticAiAssistant(create_demo_model())

    model_name = _configured_model_name()
    if model_name is None:
        return None
    if engine == LANGGRAPH_ENGINE:
        return LangGraphAssistant(create_anthropic_selector(model_name))
    return PydanticAiAssistant(f"anthropic:{model_name}")


def _configured_model_name() -> str | None:
    """Return the Anthropic model name when the key is also configured."""
    model_name = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if not model_name or not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    return model_name


if __name__ == "__main__":
    raise SystemExit(main())
