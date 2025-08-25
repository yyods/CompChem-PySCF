# Week 3 — Technical Specification (v1.0)

## 0. Scope & Goals

**Goal.** Extend Week-2’s PySCF container into a **local desktop GUI** (PySide6) that submits jobs to a **containerized FastAPI service**, with Agile workflow discipline and CI that tests, builds a GUI artifact, and generates basic **data & visualisation** artifacts from run JSONs.

**Out of scope.** Cloud deployment, registries/publishing, long/expensive calculations, user auth, remote clusters.

---

## 1. High-Level Requirements

1. **Architecture**

   * Service: FastAPI container (`pyscf_service`) exposes `POST /jobs`, `GET /jobs/{id}/result`, writes `results/*.json`.
   * GUI: PySide6 native app posts job specs to `http://127.0.0.1:8000`.
   * Analysis: local scripts aggregate `results/*.json` → `analysis_out/summary.csv` + PNG plots.

2. **Agile workflow**

   * Labels: `feat`, `fix`, `docs`, `test`, `infra`, `ux`, `experiment`.
   * Board: *Backlog → In Progress → In Review → Done*.
   * PR template + **Definition of Done (DoD)** enforced.

3. **CI**

   * `tests`: unit tests (service + GUI core logic) w/ `PYSCF_DRYRUN=1`.
   * `gui-artifact`: zip the GUI sources (local-first artifact).
   * `viz`: aggregate & plot from any committed `results/*.json`.

4. **Reproducibility**

   * Stable `system_id` per molecule geometry.
   * Result JSON includes method/basis/grid/conv\_tol/charge/spin, timings, environment versions.
   * `OMP_NUM_THREADS=1` and dependency pins.

5. **Data & Visualisation**

   * `analysis/aggregate.py` produces `summary.csv` with ΔE (kJ/mol) relative to min per system.
   * `analysis/plots.py` creates `energy_by_method_basis.png` and `deltaE_by_system_method.png`.

---

## 2. Repository Layout (authoritative)

```
week3/
  README.md
  docker-compose.yml
  results/                # service writes JSON here (ignored by git)
  analysis/               # data+viz
    aggregate.py
    plots.py
    requirements.txt
  docs/
    DoD.md
    spec.md               # (this document)
  .github/
    PULL_REQUEST_TEMPLATE.md
    workflows/ci.yml
  services/
    pyscf_service/
      Dockerfile
      requirements.txt
      app/
        __init__.py
        main.py
        runner.py
        schemas.py
  apps/
    pyscf_gui/
      pyproject.toml
      requirements.txt
      core/
        __init__.py
        client.py
        schema.py
      gui/
        __init__.py
        main.py
  tests/
    test_service.py
    test_gui_core.py
```

---

## 3. Interface Control Document (ICD)

### 3.1 HTTP Endpoints (Service)

**Base URL:** `http://127.0.0.1:8000`

**POST `/jobs`**
Request (JSON; required unless noted):

```json
{
  "molecule_xyz": "3\n\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n",
  "method": "HF | B3LYP | MP2",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "spin": 0,
  "charge": 0
}
```

Response:

```json
{ "job_id": "UUID", "status": "done|queued|running" }
```

Errors: `400` invalid schema; `500` compute failure (message string).

**GET `/jobs/{job_id}/result`**
Response (`results/{job_id}.json` payload):

```json
{
  "job_id": "UUID",
  "system_id": "sha1-10",
  "method": "HF",
  "basis": "def2-SVP",
  "grid_level": 3,
  "conv_tol": 1e-9,
  "charge": 0,
  "spin": 0,
  "energy_hartree": -75.983742,
  "timings": { "wall_s": 0.42 },
  "env": { "dryrun": false, "numpy": "1.26.4", "pyscf": "2.4.0" },
  "ts": 1724470000.0
}
```

Errors: `404` unknown job/result not ready.

**GET `/health`** → `{ "ok": true }`

### 3.2 GUI → Service Client

* `submit_job(spec: dict) -> job_id: str`
* `get_result(job_id: str) -> dict` (same as result JSON)
* **Validation:** GUI refuses “Run” if `molecule_xyz` or `basis` empty; `method` ∈ {HF,B3LYP,MP2}; `grid_level` ∈ \[0..9]; `conv_tol` ∈ \[1e-12..1e-2].

### 3.3 Data Contracts

* **`system_id`**: `sha1(molecule_xyz.strip())[:10]`.
* **Hartree→kJ/mol**: 2625.49962 (constant in analysis).
* ΔE per system computed against the **minimum** energy within that system group.

---

## 4. Functional Requirements

FR-1. The service shall accept a job, compute energy (real PySCF in container; DRYRUN in CI), and write `results/{job_id}.json`.
FR-2. The GUI shall submit a job and display method/basis and energy.
FR-3. The analysis scripts shall produce `analysis_out/summary.csv` and two PNG plots when at least one result exists.
FR-4. CI shall (a) run tests with DRYRUN, (b) upload a GUI sources ZIP, (c) aggregate/plot and upload `viz` artifacts if results exist.
FR-5. The repo shall include DoD and a PR checklist; PRs must go green before merge.

---

## 5. Non-Functional Requirements

NFR-1. **Local-first**: no container/image publishing; no cloud dependencies.
NFR-2. **Determinism (CI)**: `PYSCF_DRYRUN=1`; tests finish ≤ 5 min total on GH Ubuntu runner.
NFR-3. **Security**: GUI never accesses Docker socket; service only writes to bind-mounted `results/`.
NFR-4. **Portability**: macOS/Windows/Linux; Python ≥ 3.10 (GUI); Docker Engine v2 compose (service).
NFR-5. **Observability**: failures return HTTP codes with message; runner writes JSON atomically.

---

## 6. Configuration

| Key               | Where                 | Default   | Purpose                         |
| ----------------- | --------------------- | --------- | ------------------------------- |
| `OMP_NUM_THREADS` | service env / compose | `1`       | Reproducible single-thread runs |
| `PYSCF_DRYRUN`    | CI env / tests        | `1` in CI | Fast stubbed compute in CI      |
| `SERVICE_PORT`    | compose mapping       | `8000`    | Local HTTP port                 |

---

## 7. Build & CI/CD Specification

### 7.1 Jobs (GitHub Actions)

* **`tests`**

  * Env: `PYSCF_DRYRUN=1`
  * Installs: `pytest httpx fastapi pydantic requests PySide6`
  * Runs: `pytest -q` (service & GUI core tests)

* **`gui-artifact`**

  * Zips `apps/pyscf_gui` sources → uploads `PySCF-GUI-sources.zip`.

* **`viz`**

  * Installs: `pandas matplotlib` (from `analysis/requirements.txt`)
  * Runs `analysis/aggregate.py` → optional `analysis/plots.py` if CSV exists
  * Uploads `analysis_out/` artifacts.

### 7.2 Time budgets

* `tests` ≤ 3 min; `gui-artifact` ≤ 1 min; `viz` ≤ 2 min.

---

## 8. Data & Visualisation Specification

### 8.1 `analysis_out/summary.csv` columns

| Column      | Type  | Notes                                  |
| ----------- | ----- | -------------------------------------- |
| job\_id     | str   | UUID                                   |
| system\_id  | str   | sha1-10                                |
| method      | str   | HF/B3LYP/MP2                           |
| basis       | str   | e.g., def2-SVP                         |
| grid\_level | int   | nullable                               |
| conv\_tol   | float | nullable                               |
| energy\_ha  | float | total energy (Hartree)                 |
| wall\_s     | float | elapsed seconds (may be NaN in DRYRUN) |
| dryrun      | bool  | true in CI                             |
| ts          | float | epoch seconds                          |
| dE\_kjmol   | float | ΔE vs system min (kJ/mol)              |

### 8.2 Plots

* `energy_by_method_basis.png` — bar chart of mean `energy_ha` grouped by `(method,basis)`.
* `deltaE_by_system_method.png` — scatter (jittered) of `dE_kjmol` by `method`.

---

## 9. Test Plan (V\&V)

**Unit tests**

* `test_service.py`

  * `/health` → 200 {ok\:true}
  * `POST /jobs` with valid spec → 200 + `job_id` (with `PYSCF_DRYRUN=1`)
  * `GET /jobs/{id}/result` → has `energy_hartree`, `method` echoed back
* `test_gui_core.py`

  * `JobSpec` validation passes for nominal values
  * (Optional) invalid `method` rejected

**Integration (manual/local)**

* Run service via compose; run GUI; submit HF & B3LYP; confirm 2 JSON files in `results/`.
* `python analysis/aggregate.py && python analysis/plots.py` produces CSV + two PNGs.

**Acceptance criteria (must all pass)**

1. CI all green on `tests`, `gui-artifact`, `viz`.
2. Two local runs (HF & B3LYP) produce two JSONs and a `summary.csv` with ΔE column.
3. DoD checklist present; PR merges only with green checks.

---

## 10. UX Specification (GUI)

**Layout**

* Inputs: multiline XYZ (required), Method dropdown (HF/B3LYP/MP2), Basis text (default `def2-SVP`), Grid level \[0..9], conv\_tol `1e-12..1e-2`, Charge (-5..5), Spin (0..10).
* “Run” button disabled unless XYZ & Basis non-empty and Method valid.
* Output pane shows job\_id, method/basis, energy (Hartree), key params, env snippet, and saved JSON path.

**Error handling**

* Validation errors → modal with message; no request sent.
* HTTP/network errors → modal “Run failed” with reason.

---

## 11. Risks & Mitigations

* **PySCF install weight** (service image size) → keep in container; CI uses DRYRUN.
* **Path issues on Windows** → bind mounts only in service; GUI runs native.
* **Non-deterministic floating error** → enforce single thread; compare energies qualitatively for education.

---

## 12. Milestones (Week-3 cadence)

* **M3.1 (T+30 min)**: Board + labels + DoD committed; CI triggers.
* **M3.2 (T+90 min)**: Service & GUI core tests pass in CI.
* **M3.3 (T+120 min)**: Local HF/B3LYP runs; JSONs appear.
* **M3.4 (T+150 min)**: `summary.csv` + plots locally; CI `viz` uploads artifacts.
* **M3.5 (T+180 min)**: Mini-feature PR (e.g., MP2 toggle UX) merged with green checks.

---

## 13. Definition of Done (DoD) — Week 3

* Tests (service + GUI core) **green locally and in CI**
* `results/*.json` contains required fields incl. `system_id` and `env`
* `analysis_out/summary.csv` exists (after at least one run); plots generated locally or via CI `viz`
* README/RESULTS updated for any new method/UX; PR uses checklist; semantic commits

---

## 14. Future Extensions (not required)

* Queue/async jobs in service; progress streaming.
* In-GUI Analysis tab (renders latest PNG).
* Param sweep runner with CSV batch import.

---

