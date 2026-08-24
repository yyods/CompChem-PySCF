"""Service contract tests. PySCF is never imported: runner.run_job is replaced
by a stub, so these run on any machine — including Windows, where PySCF has no
native build."""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as app_module  # noqa: E402

WATER = "O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587"


@pytest.fixture()
def client(monkeypatch, tmp_path):
    def fake_run(spec):
        return {
            "energy_hartree": -76.02, "method": spec["method"], "basis": spec["basis"],
            "grid": spec["grid"], "conv_tol": spec["conv_tol"],
            "charge": spec["charge"], "spin": spec["spin"],
            "timings_seconds": {"build": 0.01, "solve": 0.02},
            "versions": {"pyscf": "2.4.0", "numpy": "1.26.4", "scipy": "1.13.1", "python": "3.10.0"},
            "environment": {"OMP_NUM_THREADS": "1"},
        }
    monkeypatch.setattr(app_module.runner, "run_job", fake_run)
    monkeypatch.setattr(app_module, "RESULTS", tmp_path / "results")
    app_module._JOBS.clear()
    return TestClient(app_module.api)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_submit_then_fetch_result(client):
    r = client.post("/jobs", json={"molecule": WATER, "method": "HF"})
    assert r.status_code == 201
    job_id = r.json()["job_id"]

    r2 = client.get(f"/jobs/{job_id}/result")
    assert r2.status_code == 200
    body = r2.json()
    # the four things slide 5 promises the result carries
    assert body["energy_hartree"] == pytest.approx(-76.02, abs=1e-6)
    assert set(body["timings_seconds"]) == {"build", "solve"}
    assert body["versions"]["pyscf"] == "2.4.0"
    assert "OMP_NUM_THREADS" in body["environment"]


def test_result_is_persisted_as_json(client, tmp_path):
    job_id = client.post("/jobs", json={"molecule": WATER}).json()["job_id"]
    written = list((tmp_path / "results").glob("job_*.json"))
    assert [p.name for p in written] == [f"job_{job_id}.json"]


def test_unknown_job_is_404(client):
    assert client.get("/jobs/deadbeef/result").status_code == 404


@pytest.mark.parametrize("payload,reason", [
    ({}, "molecule is required"),
    ({"molecule": WATER, "method": "CCSD(T)"}, "method not in the enum"),
    ({"molecule": WATER, "grid": 99}, "grid out of range"),
    ({"molecule": WATER, "conv_tol": 0}, "conv_tol must be > 0"),
])
def test_invalid_specs_are_rejected_before_any_compute(client, payload, reason):
    assert client.post("/jobs", json=payload).status_code == 422, reason
