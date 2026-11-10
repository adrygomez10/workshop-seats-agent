"""Check the structured selection accepted from the model."""

import unittest

from pydantic import ValidationError

from workshop_seats.adapters.langgraph.workshop_selection import (
    WorkshopSelection,
)


class WorkshopSelectionTests(unittest.TestCase):
    """Accept a supported name or no selection, and nothing else."""

    def test_accepts_an_empty_selection(self) -> None:
        """Represent a missing workshop with ``None``."""
        selection = WorkshopSelection.model_validate({"workshop_name": None})

        self.assertIsNone(selection.workshop_name)

    def test_rejects_an_unsupported_workshop(self) -> None:
        """Refuse a name that is not in the catalog."""
        with self.assertRaises(ValidationError):
            WorkshopSelection.model_validate({"workshop_name": "Yoga"})
