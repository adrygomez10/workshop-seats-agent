"""Console entry point that assembles the catalog, agent and use case."""

import argparse
import os
import sys
from collections.abc import Sequence

from pydantic_ai.exceptions import AgentRunError
from pydantic_ai.models import Model

from workshop_seats.adapters.pydantic_ai.demo_responses import (
    create_demo_model,
)
from workshop_seats.adapters.pydantic_ai.pydantic_ai_assistant import (
    PydanticAiAssistant,
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
CONFIGURATION_ERROR = 2


def main(argv: Sequence[str] | None = None) -> int:
    """Answer one question and return the process exit code."""
    os.environ.setdefault("PYDANTIC_AI_NO_BANNER", "1")
    arguments = _parse_arguments(argv)
    model = _select_model(demo=arguments.demo)
    if model is None:
        print(
            "Set ANTHROPIC_API_KEY and ANTHROPIC_MODEL, or use --demo.",
            file=sys.stderr,
        )
        return CONFIGURATION_ERROR

    catalog = WorkshopCatalog(DEMO_SEATS_BY_WORKSHOP)
    assistant = PydanticAiAssistant(model)
    use_case = CheckAvailability(assistant, catalog)
    try:
        answer = use_case.execute(arguments.question)
    except (
        AgentRunError,
        InconsistentReportError,
        UnknownWorkshopError,
    ) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1

    print(format_answer(answer))
    return 0


def _parse_arguments(argv: Sequence[str] | None) -> argparse.Namespace:
    """Read the question and the model mode from the command line."""
    parser = argparse.ArgumentParser(
        description="Ask how many seats are left in a workshop.",
    )
    parser.add_argument("question", nargs="?", default=DEFAULT_QUESTION)
    parser.add_argument(
        "--demo",
        action="store_true",
        help="use scripted responses instead of a real model",
    )
    return parser.parse_args(argv)


def _select_model(*, demo: bool) -> Model | str | None:
    """Return the scripted model or the configured Anthropic model."""
    if demo:
        return create_demo_model()

    model_name = os.environ.get("ANTHROPIC_MODEL", "").strip()
    if not model_name or not os.environ.get("ANTHROPIC_API_KEY"):
        return None
    return f"anthropic:{model_name}"


if __name__ == "__main__":
    raise SystemExit(main())
