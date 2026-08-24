"""Form validation for the desktop client.

Deliberately free of Qt so it can be unit-tested with no display at all —
this is the "GUI logic" the CI tests without ever opening a window.
"""
from __future__ import annotations

METHODS = ("HF", "B3LYP", "MP2")


def validate(molecule: str, method: str, basis: str, conv_tol: str, grid: str) -> list[str]:
    """Return a list of problems. An empty list means the form may be submitted."""
    problems: list[str] = []
    if not molecule.strip():
        problems.append("molecule is empty")
    if method not in METHODS:
        problems.append(f"method must be one of {', '.join(METHODS)}")
    if not basis.strip():
        problems.append("basis is empty")
    try:
        tol = float(conv_tol)
        if not 0 < tol < 1:
            problems.append("conv_tol must be between 0 and 1")
    except ValueError:
        problems.append("conv_tol is not a number")
    try:
        level = int(grid)
        if not 0 <= level <= 9:
            problems.append("grid must be 0-9")
    except ValueError:
        problems.append("grid is not an integer")
    return problems
