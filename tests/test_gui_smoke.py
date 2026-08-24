"""Does-it-launch smoke test. Runs offscreen: no display server needed."""
import os
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
pytest.importorskip("PySide6", reason="GUI extras not installed")
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gui"))


def test_window_constructs_and_run_button_follows_validity():
    from PySide6.QtWidgets import QApplication
    import main as gui_main

    app = QApplication.instance() or QApplication([])
    w = gui_main.JobForm()
    assert w.run.isEnabled(), "the default form is valid, so Run should be enabled"

    w.molecule.setPlainText("")          # invalidate
    assert not w.run.isEnabled(), "Run must be disabled while the form is invalid"

    w.molecule.setPlainText("O 0 0 0")   # repair
    assert w.run.isEnabled()
    app.processEvents()
