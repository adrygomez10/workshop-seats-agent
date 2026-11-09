"""Verify that the organization check rejects structural regressions."""

import unittest
from pathlib import Path

from scripts.check_structure import inspect_source


class StructureTests(unittest.TestCase):
    """Exercise explicit class-per-module rules for every declared type."""

    def test_one_class_and_imported_dependencies_are_allowed(self) -> None:
        """Count declarations, not imported classes."""
        source = "from decimal import Decimal\nclass Money:\n    pass\n"
        self.assertEqual(
            (),
            inspect_source(
                source,
                Path("money.py"),
                enforce_name=True,
            ),
        )

    def test_multiple_classes_are_rejected(self) -> None:
        """Reject grouped declarations even if they have related names."""
        source = "class First:\n    pass\nclass Second:\n    pass\n"
        findings = inspect_source(source, Path("first.py"), enforce_name=True)
        self.assertIn("PYORG001", findings[0])

    def test_nested_classes_are_not_an_exception(self) -> None:
        """Apply the same rule to classes declared inside another class."""
        source = "class Outer:\n    class Inner:\n        pass\n"
        findings = inspect_source(source, Path("outer.py"), enforce_name=True)
        self.assertIn("PYORG001", findings[0])

    def test_filename_identifies_the_declared_class(self) -> None:
        """Require a concrete snake_case filename for production types."""
        findings = inspect_source(
            "class ExpensePolicy:\n    pass\n",
            Path("models.py"),
            enforce_name=True,
        )
        self.assertIn("expense_policy.py", findings[0])

    def test_class_modules_do_not_mix_in_top_level_functions(self) -> None:
        """Keep projection and CLI functions in their own focused modules."""
        findings = inspect_source(
            "class Money:\n    pass\ndef helper():\n    pass\n",
            Path("money.py"),
            enforce_name=True,
        )
        self.assertIn("PYORG003", findings[0])

    def test_package_initializers_do_not_define_classes(self) -> None:
        """Keep package initialization independent of concrete declarations."""
        findings = inspect_source(
            "class Money:\n    pass\n",
            Path("__init__.py"),
            enforce_name=True,
        )
        self.assertIn("PYORG002", findings[0])

    def test_functions_and_alias_modules_are_allowed(self) -> None:
        """Permit focused modules that do not declare classes."""
        self.assertEqual(
            (),
            inspect_source(
                "def main():\n    pass\n",
                Path("bootstrap.py"),
                enforce_name=True,
            ),
        )
