"""GUI form logic — no Qt, no display."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gui"))
from validate import validate  # noqa: E402

GOOD = dict(molecule="O 0 0 0", method="HF", basis="def2-svp", conv_tol="1e-9", grid="3")


def test_a_good_form_has_no_problems():
    assert validate(**GOOD) == []


def test_empty_molecule_blocks_run():
    assert "molecule is empty" in validate(**{**GOOD, "molecule": "   "})


def test_unknown_method_blocks_run():
    assert any("method must be" in p for p in validate(**{**GOOD, "method": "CCSD"}))


def test_bad_numbers_block_run():
    assert any("conv_tol" in p for p in validate(**{**GOOD, "conv_tol": "abc"}))
    assert any("grid" in p for p in validate(**{**GOOD, "grid": "12"}))
