"""Run the same non-mutating quality gate from Git, CI and the console."""

import subprocess
import sys
from pathlib import Path


def main() -> int:
    """Run pinned project tools and stop at the first rejected check."""
    root = Path(__file__).resolve().parents[1]
    executable = (
        "Scripts/python.exe" if sys.platform == "win32" else "bin/python"
    )
    interpreter = root / ".venv" / executable
    if not interpreter.is_file():
        print(
            "Create the project environment with: uv sync --frozen",
            file=sys.stderr,
        )
        return 1

    commands = (
        ("scripts.check_structure",),
        ("ruff", "check", "."),
        ("ruff", "format", "--check", "."),
        ("mypy",),
        ("pytest",),
    )
    for command in commands:
        print("Running: " + " ".join(command), flush=True)
        result = subprocess.run(
            [str(interpreter), "-m", *command],
            cwd=root,
            check=False,
        )
        if result.returncode:
            return result.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
