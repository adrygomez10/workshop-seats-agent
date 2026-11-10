"""Application data available to the workflow steps during one run."""

from dataclasses import dataclass

from workshop_seats.domain.workshop_catalog import WorkshopCatalog


@dataclass(frozen=True, slots=True)
class WorkflowContext:
    """Catalog that the answer step reads, supplied by the application."""

    catalog: WorkshopCatalog
