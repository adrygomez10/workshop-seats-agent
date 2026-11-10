"""Keep the names accepted by the agent aligned with the catalog data."""

import unittest
from typing import get_args

from workshop_seats.adapters.workshop_name import WorkshopName
from workshop_seats.catalog_data import DEMO_SEATS_BY_WORKSHOP


class WorkshopNameTests(unittest.TestCase):
    """Detect a workshop added to one list but not the other."""

    def test_literal_lists_the_catalog_workshops(self) -> None:
        """Compare the tool argument values with the catalog keys."""
        self.assertEqual(
            tuple(DEMO_SEATS_BY_WORKSHOP),
            get_args(WorkshopName),
        )
