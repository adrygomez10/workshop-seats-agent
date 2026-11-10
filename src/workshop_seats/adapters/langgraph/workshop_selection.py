"""Structured selection that the model returns in the LangGraph flow."""

from pydantic import BaseModel, ConfigDict

from workshop_seats.adapters.workshop_name import WorkshopName


class WorkshopSelection(BaseModel):
    """A supported workshop name, or no selection."""

    model_config = ConfigDict(extra="forbid", strict=True)

    workshop_name: WorkshopName | None
