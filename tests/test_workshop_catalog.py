"""Check the rules that protect the workshop catalog."""

import unittest

from workshop_seats.domain.unknown_workshop_error import UnknownWorkshopError
from workshop_seats.domain.workshop_catalog import WorkshopCatalog


class WorkshopCatalogTests(unittest.TestCase):
    """Read seats and reject catalogs that break the invariants."""

    def test_returns_the_seats_of_a_known_workshop(self) -> None:
        """Return the stored count, including zero seats."""
        catalog = WorkshopCatalog({"Fotografía nocturna": 3, "Cerámica": 0})

        self.assertEqual(3, catalog.seats_for("Fotografía nocturna"))
        self.assertEqual(0, catalog.seats_for("Cerámica"))
        self.assertEqual(
            ("Fotografía nocturna", "Cerámica"),
            catalog.workshop_names,
        )

    def test_unknown_workshop_is_not_zero_seats(self) -> None:
        """Distinguish a missing workshop from a full one."""
        catalog = WorkshopCatalog({"Cerámica": 0})

        with self.assertRaises(UnknownWorkshopError) as raised:
            catalog.seats_for("Pintura")
        self.assertEqual("Pintura", raised.exception.workshop_name)

    def test_rejects_invalid_catalogs(self) -> None:
        """Require names, non-negative counts and at least one workshop."""
        for seats_by_workshop in (
            {},
            {" ": 2},
            {"Cerámica": -1},
            {"Cerámica": True},
        ):
            with (
                self.subTest(seats_by_workshop=seats_by_workshop),
                self.assertRaises(ValueError),
            ):
                WorkshopCatalog(seats_by_workshop)

    def test_later_changes_to_the_source_do_not_alter_the_catalog(
        self,
    ) -> None:
        """Copy the data so the catalog cannot be modified from outside."""
        source = {"Cerámica": 0}
        catalog = WorkshopCatalog(source)

        source["Cerámica"] = 9

        self.assertEqual(0, catalog.seats_for("Cerámica"))
