"""Availability assistant implemented with a LangGraph workflow."""

from langchain_core.language_models import LanguageModelInput
from langchain_core.runnables import Runnable
from langgraph.graph import END, START, StateGraph

from workshop_seats.adapters.langgraph.unexpected_selection_error import (
    UnexpectedSelectionError,
)
from workshop_seats.adapters.langgraph.workflow_context import WorkflowContext
from workshop_seats.adapters.langgraph.workflow_steps import (
    answer_availability,
    ask_for_workshop,
    choose_next_step,
)
from workshop_seats.adapters.langgraph.workshop_selection import (
    WorkshopSelection,
)
from workshop_seats.adapters.langgraph.workshop_state import WorkshopState
from workshop_seats.application.availability_report import (
    AvailabilityReport,
)
from workshop_seats.application.clarification_request import (
    ClarificationRequest,
)
from workshop_seats.domain.workshop_catalog import WorkshopCatalog

SELECTION_INSTRUCTIONS = (
    "Identify the workshop explicitly requested. Supported names: "
    "Fotografía nocturna, Cerámica. Set workshop_name to null "
    "if the workshop is missing, unsupported, or ambiguous. "
    "Do not guess a workshop."
)


class LangGraphAssistant:
    """Let the model select the workshop and the graph choose the path."""

    def __init__(self, selector: Runnable[LanguageModelInput, object]) -> None:
        """Connect the selection, decision and answer steps."""
        self._selector = selector
        builder = StateGraph(WorkshopState, context_schema=WorkflowContext)
        builder.add_node("identify", self._identify_workshop)
        builder.add_node("answer", answer_availability)
        builder.add_node("clarify", ask_for_workshop)

        builder.add_edge(START, "identify")
        builder.add_conditional_edges(
            "identify",
            choose_next_step,
            {"answer": "answer", "clarify": "clarify"},
        )
        builder.add_edge("answer", END)
        builder.add_edge("clarify", END)
        self._workflow = builder.compile()

    def ask(
        self,
        question: str,
        catalog: WorkshopCatalog,
    ) -> AvailabilityReport | ClarificationRequest:
        """Run the workflow once and return the answer of its last step."""
        result = self._workflow.invoke(
            {"message": question, "workshop_name": None, "answer": None},
            context=WorkflowContext(catalog),
        )

        answer: AvailabilityReport | ClarificationRequest = result["answer"]
        return answer

    def _identify_workshop(
        self, state: WorkshopState
    ) -> dict[str, str | None]:
        """Ask the model to identify a supported workshop."""
        selection = self._selector.invoke(
            [
                ("system", SELECTION_INSTRUCTIONS),
                ("human", state["message"]),
            ]
        )
        if not isinstance(selection, WorkshopSelection):
            raise UnexpectedSelectionError(selection)

        return {"workshop_name": selection.workshop_name}
