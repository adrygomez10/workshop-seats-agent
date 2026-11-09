"""Enforce one class per module for application, test and tooling code."""

import ast
import re
import sys
from pathlib import Path


def module_name(class_name: str) -> str:
    """Convert a declared type name to its required snake_case module."""
    words = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", class_name)

    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", words).lower()


def inspect_source(
    source: str,
    path: Path,
    *,
    enforce_name: bool,
) -> tuple[str, ...]:
    """Report structural violations without importing or running modules."""
    tree = ast.parse(source, filename=str(path))
    classes = [
        node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
    ]
    if len(classes) > 1:
        names = ", ".join(node.name for node in classes)
        return (f"{path}: PYORG001: declare one class per module: {names}",)
    if not classes:
        return ()

    declared = classes[0]
    findings: list[str] = []
    if path.name == "__init__.py":
        findings.append(
            f"{path}: PYORG002: package initializers cannot define classes"
        )
    elif enforce_name and path.stem != module_name(declared.name):
        expected = module_name(declared.name) + ".py"
        findings.append(
            f"{path}: PYORG002: place {declared.name} in {expected}"
        )

    functions = (ast.FunctionDef, ast.AsyncFunctionDef)
    if any(isinstance(node, functions) for node in tree.body):
        findings.append(
            f"{path}: PYORG003: move module functions out of the class module"
        )

    return tuple(findings)


def main() -> int:
    """Check sources without touching environments or generated files."""
    root = Path(__file__).resolve().parents[1]
    findings: list[str] = []
    for folder in ("src", "tests", "scripts"):
        for path in sorted((root / folder).rglob("*.py")):
            findings.extend(
                inspect_source(
                    path.read_text(encoding="utf-8"),
                    path,
                    enforce_name=folder == "src",
                )
            )

    if findings:
        print("\n".join(findings), file=sys.stderr)
        return 1

    print("Module structure passed: one class per module.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
