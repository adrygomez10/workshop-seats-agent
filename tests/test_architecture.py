"""Enforce inward dependencies with Python's AST."""

import ast
import subprocess
import sys
import unittest
from pathlib import Path

PACKAGE = "workshop_seats"
SOURCE = Path(__file__).resolve().parents[1] / "src" / PACKAGE


class ArchitectureTests(unittest.TestCase):
    """Keep the AI libraries and the console outside the core."""

    def test_core_layers_depend_only_on_inner_layers(self) -> None:
        """Allow the standard library and inner project layers only."""
        for layer, allowed in (
            ("domain", {"domain"}),
            ("application", {"domain", "application"}),
        ):
            for path in sorted((SOURCE / layer).rglob("*.py")):
                for module in self.imported_modules(path):
                    with self.subTest(path=path.name, module=module):
                        if module.startswith(PACKAGE + "."):
                            self.assertIn(module.split(".")[1], allowed)
                        else:
                            self.assertIn(
                                module.split(".")[0],
                                sys.stdlib_module_names,
                            )

    def test_adapters_do_not_depend_on_the_entry_point(self) -> None:
        """Keep the composition at the outer edge of the application."""
        outer = {f"{PACKAGE}.bootstrap", f"{PACKAGE}.console_output"}
        for path in sorted((SOURCE / "adapters").rglob("*.py")):
            with self.subTest(path=path.name):
                self.assertFalse(outer & set(self.imported_modules(path)))

    def test_importing_modules_does_not_build_or_run_an_agent(self) -> None:
        """Import every module in a fresh interpreter with agents blocked."""
        names = []
        for path in sorted(SOURCE.rglob("*.py")):
            relative = path.relative_to(SOURCE.parent).with_suffix("")
            names.append(".".join(relative.parts).removesuffix(".__init__"))
        program = (
            "import importlib, sys\n"
            "from unittest.mock import patch\n"
            "blocked = AssertionError('agent built on import')\n"
            "with (\n"
            "    patch('pydantic_ai.Agent.__init__', side_effect=blocked),\n"
            "    patch('langgraph.graph.StateGraph.compile',"
            " side_effect=blocked),\n"
            "    patch('langchain.chat_models.init_chat_model',"
            " side_effect=blocked),\n"
            "):\n"
            "    for name in sys.argv[1:]:\n"
            "        importlib.import_module(name)\n"
        )

        result = subprocess.run(
            [sys.executable, "-c", program, *names],
            capture_output=True,
            check=False,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stderr)

    def imported_modules(self, path: Path) -> list[str]:
        """Return absolute imports and reject relative ones."""
        tree = ast.parse(path.read_text(encoding="utf-8"))
        modules: list[str] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                self.assertEqual(0, node.level, str(path))
                modules.append(node.module or "")
        return modules
