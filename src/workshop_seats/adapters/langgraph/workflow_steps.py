"""Decision and answer steps of the LangGraph workflow."""

from typing import Literal

from langgraph.runtime import Runtime

from workshop_seats.adapters.langgraph.workflow_context import WorkflowContext
from workshop_seats.adapters.langgraph.workshop_state import WorkshopState
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)

CLARIFICATION = "Indica el taller: Fotografía nocturna o Cerámica."


def choose_next_step(state: WorkshopState) -> Literal["answer", "clarify"]:
    """Choose a path based on whether a workshop was selected."""
    if state["workshop_name"] is None:
        return "clarify"
    return "answer"


def answer_availability(
    state: WorkshopState,
    runtime: Runtime[WorkflowContext],
) -> dict[str, AvailabilityReport]:
    """Read the seats of the selected workshop from the catalog."""
    workshop_name = state["workshop_name"]
    if workshop_name is None:
        raise ValueError("A workshop must be selected before reading seats.")

    seats = runtime.context.catalog.seats_for(workshop_name)
    return {"answer": AvailabilityReport(workshop_name, seats)}


def ask_for_workshop(state: WorkshopState) -> dict[str, ClarificationRequest]:
    """Ask the person to name one of the supported workshops."""
    return {"answer": ClarificationRequest(CLARIFICATION)}
