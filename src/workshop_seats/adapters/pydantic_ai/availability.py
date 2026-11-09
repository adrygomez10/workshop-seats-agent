"""Structured output that the agent must return."""

from pydantic import BaseModel, ConfigDict, Field

from workshop_seats.adapters.pydantic_ai.workshop_name import WorkshopName


class Availability(BaseModel):
    """Availability for a supported workshop."""

    model_config = ConfigDict(extra="forbid", strict=True)

    workshop_name: WorkshopName
    available_seats: int = Field(ge=0)
