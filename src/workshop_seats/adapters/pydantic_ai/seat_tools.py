"""Operations that the agent may request from the application."""

from pydantic_ai import RunContext

from workshop_seats.adapters.pydantic_ai.workshop_name import WorkshopName
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


def get_available_seats(
    ctx: RunContext[WorkshopCatalog],
    workshop_name: WorkshopName,
) -> int:
    """Read available seats for a supported workshop without reserving."""
    return ctx.deps.seats_for(workshop_name)
