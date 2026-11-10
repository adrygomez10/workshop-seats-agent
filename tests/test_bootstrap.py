"""Run the console entry point as a workshop participant would."""

import io
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

from workshop_seats.bootstrap import CONFIGURATION_ERROR, main


class BootstrapTests(unittest.TestCase):
    """Check the printed answer and the exit code of each path."""

    def run_main(self, *arguments: str) -> tuple[int, str, str]:
        """Call ``main`` and capture both output streams."""
        stdout = io.StringIO()
        stderr = io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            exit_code = main(list(arguments))
        return exit_code, stdout.getvalue(), stderr.getvalue()

    def test_demo_prints_the_default_question_answer(self) -> None:
        """Answer the article's question with the demo catalog."""
        exit_code, output, _ = self.run_main("--demo")

        self.assertEqual(0, exit_code)
        self.assertEqual(
            "Taller: Fotografía nocturna\nPlazas disponibles: 3\n",
            output,
        )

    def test_demo_prints_a_clarification(self) -> None:
        """Show the question back when no workshop is named."""
        exit_code, output, _ = self.run_main("--demo", "¿Quedan plazas?")

        self.assertEqual(0, exit_code)
        self.assertTrue(output.startswith("Aclaración: "))

    def test_langgraph_demo_prints_the_default_question_answer(self) -> None:
        """Answer the same question with the LangGraph workflow."""
        exit_code, output, _ = self.run_main("--engine", "langgraph", "--demo")

        self.assertEqual(0, exit_code)
        self.assertEqual(
            "Taller: Fotografía nocturna\nPlazas disponibles: 3\n",
            output,
        )

    def test_langgraph_demo_prints_its_fixed_clarification(self) -> None:
        """Show the clarification written by the workflow."""
        exit_code, output, _ = self.run_main(
            "--engine", "langgraph", "--demo", "¿Quedan plazas?"
        )

        self.assertEqual(0, exit_code)
        self.assertEqual(
            "Aclaración: Indica el taller: Fotografía nocturna o Cerámica.\n",
            output,
        )

    def test_real_mode_requires_model_configuration(self) -> None:
        """Explain the missing variables instead of calling a provider."""
        with patch.dict("os.environ", {}, clear=True):
            exit_code, output, errors = self.run_main()

        self.assertEqual(CONFIGURATION_ERROR, exit_code)
        self.assertEqual("", output)
        self.assertIn("ANTHROPIC_MODEL", errors)
