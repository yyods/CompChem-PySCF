"""Minimal PySide6 client for the Service-Runner.

It never imports pyscf. It speaks JSON to the service over HTTP — which is the
whole point: the interface and the compute meet only at the contract, so this
runs natively on Windows while PySCF runs in the container.

    python gui/main.py                       # talks to http://127.0.0.1:8000
    SERVICE_URL=http://host:8000 python gui/main.py
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from validate import METHODS, validate  # noqa: E402

from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QComboBox, QFormLayout, QLabel, QLineEdit, QPlainTextEdit,
    QPushButton, QVBoxLayout, QWidget,
)

SERVICE_URL = os.environ.get("SERVICE_URL", "http://127.0.0.1:8000")
DEFAULT_MOLECULE = "O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587"


class JobForm(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("CompChem Service-Runner")
        self.molecule = QPlainTextEdit(DEFAULT_MOLECULE)
        self.molecule.setFixedHeight(60)
        self.method = QComboBox(); self.method.addItems(METHODS)
        self.basis = QLineEdit("def2-svp")
        self.conv_tol = QLineEdit("1e-9")
        self.grid = QLineEdit("3")
        self.run = QPushButton("Run")
        self.status = QLabel("")
        self.output = QPlainTextEdit(); self.output.setReadOnly(True)

        form = QFormLayout()
        form.addRow("Molecule", self.molecule)
        form.addRow("Method", self.method)
        form.addRow("Basis", self.basis)
        form.addRow("conv_tol", self.conv_tol)
        form.addRow("Grid", self.grid)
        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self.run)
        layout.addWidget(self.status)
        layout.addWidget(self.output)

        for w in (self.molecule, self.basis, self.conv_tol, self.grid):
            sig = w.textChanged if hasattr(w, "textChanged") else w.textChanged
            sig.connect(self.revalidate)
        self.method.currentTextChanged.connect(self.revalidate)
        self.run.clicked.connect(self.submit)
        self.revalidate()

    def current(self) -> dict:
        return {
            "molecule": self.molecule.toPlainText(),
            "method": self.method.currentText(),
            "basis": self.basis.text(),
            "conv_tol": self.conv_tol.text(),
            "grid": self.grid.text(),
        }

    def revalidate(self) -> None:
        """Run stays disabled until the form is valid — the DoD on slide 7."""
        problems = validate(**self.current())
        self.run.setEnabled(not problems)
        self.status.setText("; ".join(problems) if problems else "ready")

    def submit(self) -> None:
        f = self.current()
        spec = {
            "molecule": f["molecule"], "method": f["method"], "basis": f["basis"],
            "conv_tol": float(f["conv_tol"]), "grid": int(f["grid"]),
        }
        try:
            self.status.setText("running…")
            QApplication.processEvents()
            job = self._post(f"{SERVICE_URL}/jobs", spec)
            record = self._get(f"{SERVICE_URL}/jobs/{job['job_id']}/result")
            self.output.setPlainText(json.dumps(record, indent=2))
            self.status.setText(f"E = {record['energy_hartree']:.10f} Hartree")
        except Exception as exc:  # a teaching client: show the failure plainly
            self.status.setText(f"failed: {exc}")

    @staticmethod
    def _post(url: str, payload: dict) -> dict:
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode(),
            headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=300) as r:
            return json.loads(r.read().decode())

    @staticmethod
    def _get(url: str) -> dict:
        with urllib.request.urlopen(url, timeout=300) as r:
            return json.loads(r.read().decode())


def main() -> int:
    app = QApplication(sys.argv)
    w = JobForm()
    w.resize(560, 520)
    w.show()
    if os.environ.get("SMOKE_TEST"):   # CI: prove it constructs and paints, then leave
        app.processEvents()
        return 0
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
