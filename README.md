# Weeks 3–4 — Containers, Service-Runners & Desktop Clients

[![CI](../../actions/workflows/ci.yml/badge.svg)](../../actions/workflows/ci.yml)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](./Dockerfile)
[![Cross-Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-success)](./docker-compose.yml)
[![PySCF](https://img.shields.io/badge/PySCF-2.4.0-orange)](https://pyscf.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-009688)](./app.py)

A pinned PySCF environment in a container, a typed JSON service in front of it, and a
native desktop client that talks to that service over HTTP — so the compute runs where
PySCF exists, and the interface runs where the user is.

> **Course context.** Computational Chemistry, Chulalongkorn University. Weeks 1–2 were
> Git and reproducibility and needed no calculations. This repository is **Weeks 3 and 4**:
> Week 3 is the container and the batch scripts; Week 4 is the same image behind an HTTP
> contract, plus a desktop client and CI. Slide references in the code (`slide 5`, `slide 7`)
> point at the lecture deck, which is distributed in class.

## 🧭 The one idea

Two things cannot live in the same place, and that fact shapes the whole repository:

- **PySCF has no Windows build.** No `win_amd64` wheel for any version, no conda-forge
  `win-64` package. It runs on Linux and macOS only.
- **`python:3.10-slim` has no Qt libraries.** A desktop GUI cannot run in the image.

So each half runs where it can, and they meet only at a JSON contract:

```
   HOST  (Windows / macOS / Linux)                CONTAINER  (Linux, pinned)
 ┌──────────────────────────────────┐          ┌────────────────────────────────────┐
 │  gui/main.py    — PySide6 window │          │  uvicorn                           │
 │  browser        — /docs          │  HTTP    │   └── app.py     JobSpec validates  │
 │  curl           — POST /jobs     │  +JSON   │        └── runner.py                │
 │                                  │ ───────► │             └── from pyscf import … │
 │  pytest tests/  — no PySCF here  │ ◄─────── │                  └── PySCF 2.4.0    │
 └──────────────────────────────────┘          └────────────────────────────────────┘
              ▲                                                   │
              └────────  results/  ◄── bind mount ────────────────┘
```

Nothing on the host ever imports PySCF. That is why `pytest`, the service process and the
GUI all start on Windows, and why only *submitting a job* needs the container.

## 🚦 Which path am I on?

| I want to… | Path | I need | Section |
| --- | --- | --- | --- |
| Reproduce a reference energy | `docker compose run --rm pyscf scripts/…` | Docker only | [Week 3](#week-3) |
| Drive PySCF over HTTP | `docker compose up api` | Docker + curl or a browser | [Week 4](#week-4) |
| Click a form instead of typing curl | `python gui/main.py` | Host Python **and** a running service | [Desktop client](#desktop-client) |
| Check the code without running chemistry | `pytest tests/` | Host Python only — no Docker | [Tests](#tests) |

> **Run every command from the repository root** — the directory containing
> `docker-compose.yml`. The scripts, the service and the freeze all write to paths relative
> to your current directory.

## 🎯 Learning Objectives

**Week 3 — containers**

1. **Explain** why containers matter for computational reproducibility in quantum chemistry
2. **Build and run** a Docker image that executes PySCF jobs deterministically
3. **Predict** the formal cost ordering of HF, B3LYP and MP2 on the same water geometry,
   then **measure** it — and explain why the measurement disagrees, and why their total
   energies cannot be ranked for accuracy against each other
4. **Read and set** the SCF convergence and basis-set options a PySCF job is actually using
5. **Record** a container's provenance — digest-pinned base, pinned packages, and package
   versions written into the results JSON — so a clean clone of your tagged release
   rebuilds to the same energy

**Week 4 — services and clients**

6. **Expose** a calculation as a typed HTTP contract, and explain why a Pydantic `JobSpec`
   rejects a bad request before a single SCF cycle runs
7. **Separate** interface from compute: a client that never imports PySCF and speaks only
   JSON, which is what makes a native Windows GUI possible at all
8. **Explain** why the only PySCF import in the service is lazy, and what that buys
9. **Verify** the contract with pytest and a GitHub Actions pipeline that never runs chemistry

## 🔧 Prerequisites

**Week 3 — the container**

- Docker Desktop/Engine with `docker compose` v2
- `git`
- Basic command line familiarity

**Week 4 adds a host Python**

- Python 3.10+ on the host, with `pip`. It need not match the image: the image is
  **3.10.21**, CI pins **3.10**, and the host venv is verified on **3.12.10**.
- curl, or any browser, for `http://127.0.0.1:8000/docs`

**Quick verification**

```bash
docker --version
docker compose version
docker run hello-world
git --version
python --version
```

## 🚀 Quick Start

### 0. Fork first

Everything downstream — tag, release, submission — happens on **your** copy.
Press **Fork** (top right), then clone *your* fork:

```bash
git clone https://github.com/<your-username>/CompChem-PySCF.git
cd CompChem-PySCF
git remote -v          # origin must point at <your-username>, not yyods
```

### 1. Build

```bash
docker compose build pyscf
```

First build downloads the pinned wheel set and is the slow step; later runs start in seconds.

### 2. Run a calculation

```bash
docker compose run --rm pyscf scripts/optimize_water.py

cat results/water_opt.xyz     # the optimised geometry
cat results/water_opt.json    # energy, geometry, package versions
```

`results/` does not exist in a fresh clone — Docker creates it as a bind-mount target on
first run, along with `jobs/`.

### 3. Explore methods

```bash
docker compose run --rm pyscf scripts/water_hf.py      # Hartree-Fock
docker compose run --rm pyscf scripts/water_dft.py     # B3LYP
docker compose run --rm pyscf scripts/water_mp2.py     # MP2
docker compose run --rm pyscf scripts/co2_test.py      # CO₂ single point
```

### 4. Start the service

```bash
docker compose up api          # http://127.0.0.1:8000/docs
```

<a id="week-3"></a>

## 🐳 Week 3 — the container

### The three compose commands

| Command | What it does |
| --- | --- |
| `docker compose run --rm pyscf scripts/<name>.py` | One calculation; the container exits when it finishes |
| `docker compose up api` | The service only; stays up until Ctrl-C (`-d` for background, `docker compose down` to stop) |
| `docker compose build` | Builds **both** images |

> ⚠️ **`docker compose up` with no service name starts both.** The `pyscf` service carries
> `command: scripts/optimize_water.py`, so the bare form runs a geometry optimisation *and*
> a web server at once. Always name the service.

### Reference energies

Produced by this container with `OMP_NUM_THREADS=1`. Use them to check your own setup —
small differences in the last digits across BLAS libraries and thread counts are expected,
and that is a Week 3 discussion.

| Script | Method | Energy / Hartree |
| --- | --- | --- |
| `water_hf.py` | RHF/def2-SVP | -75.960975166983 |
| `water_dft.py` | B3LYP/def2-SVP | -76.358149490137 |
| `water_mp2.py` | MP2/def2-SVP | -76.164590031811 |
| `co2_test.py` | B3LYP/def2-SVP | -188.442995139098 |
| `co2_sp.py` | B3LYP/def2-SVP | -188.442995139098 — *the same calculation as `co2_test.py`, written to a different filename* |
| `water_B3LYP_631Gd.py` | B3LYP/6-31G(d) | -76.406814700655 |
| `optimize_water.py` | B3LYP/def2-SVP at the optimised geometry | -76.358315782804 |

The last row is worth a moment: it sits **1.66 × 10⁻⁴ Ha (0.10 kcal mol⁻¹) below** the
`water_dft.py` single point. Same method, same basis — the difference is relaxation energy,
the reward for letting the geometry move.

### ⚠️ Why the pin matters

PySCF prints this on every DFT run in this repository:

> Since PySCF-2.3, B3LYP (and B3P86) are changed to the VWN-RPA variant … the same as the
> B3LYP functional in Gaussian. To restore the VWN5 definition, set `B3LYP_WITH_VWN5 = True`.

Measured here, on this water geometry, with everything else identical:

| Definition | Energy / Hartree |
| --- | --- |
| `B3LYP` (VWN-RPA, PySCF ≥ 2.3) | -76.358149490137 |
| `B3LYP5` (VWN5, the pre-2.3 meaning) | -76.321000538465 |

**0.0371 Hartree — 23.3 kcal mol⁻¹.** Same input file, same basis, same grid, same
convergence threshold; a different package version, a different answer, and no error
message anywhere. This is the entire argument for `pyscf==2.4.0` in one number.

### Method comparison

| Method | Formal cost | MAE, atomization energies\* | Where it is used here |
| --- | --- | --- | --- |
| **HF** | O(N⁴) | ~75 | `water_hf.py` — the reference determinant MP2 starts from |
| **B3LYP** (hybrid) | O(N⁴) | ~3 | `water_dft.py`, `co2_test.py`, `co2_sp.py`, `water_B3LYP_631Gd.py` — single points; `optimize_water.py` — geometry optimisation |
| **MP2** | O(N⁵) | ~7 | `water_mp2.py` — correlation energy on top of the HF reference |

*N* = number of **basis functions** (def2-SVP: 24 for H₂O, 42 for CO₂). These are formal
integral counts, with no screening or density fitting, and none of them includes the DFT
quadrature grid.

\* kcal mol⁻¹ vs experiment, G2-type sets at 6-311+G(3df,2p). These are **three separate
studies on sets of different size** — read them as orders of magnitude, not a controlled
series, and check the lecture deck for the exact sources before quoting them.

These three methods are exactly what the Week 4 service accepts. Anything else is rejected
with a 422 before PySCF is ever imported.

#### Formal cost is not measured cost

Objective 3 asks you to measure. Here is what this repository actually does — water,
def2-SVP, 24 basis functions, `OMP_NUM_THREADS=1`, best of five:

| Method | Wall clock |
| --- | --- |
| HF | 0.047 s |
| MP2 | 0.042 s |
| B3LYP | 0.444 s |

**MP2 is the fastest, and B3LYP is ten times slower than either.** That is not a
contradiction of the O(N⁵) column — it is what O(N⁵) means at N = 24. The MP2 step on top
of a converged HF reference is negligible at this size, while B3LYP pays for a numerical
integration grid that the scaling column does not describe at all. Formal scaling tells you
which method wins as the molecule grows; it says nothing about which wins today.

The three water scripts run the same geometry in the same basis, so comparing them is at
least well-posed. Their total energies come out E(B3LYP) < E(MP2) < E(HF). That is **not**
an accuracy ranking — only HF is variational, MP2 adds a non-variational correction that
can overshoot, and a DFT total energy is not on the same scale as either. Cost buys
accuracy *within* a hierarchy (HF → MP2 → CCSD(T)), not across families.

### Convergence and basis settings

Every script sets `mf.conv_tol = 1e-9` and, for DFT, `mf.grids.level = 3`. Both are already
the PySCF 2.4.0 defaults for `scf.RHF` and `dft.RKS` — the lines are documentation, not
changes. Making a default explicit is good practice: it survives a version bump that
changes it.

What is *not* tight by default is the gradient criterion. `conv_tol_grad` is `None`, which
PySCF resolves to `sqrt(conv_tol)` = 3.2 × 10⁻⁵. For gradients and properties, set both.

- **Quick screening (DFT)**: `def2-SVP`, `grids.level=3` (the default grid) — conformer
  search only; do not report energetics
- **Production (DFT)**: `def2-TZVP`, `grids.level=4`, and tighten `conv_tol` toward `1e-10`
- **Converged single points (DFT)**: `def2-QZVPP`, `grids.level=5` — near the basis-set
  limit, but still not CBS
- **Correlated wavefunctions (MP2/CCSD(T))**: `cc-pVTZ` / `cc-pVQZ`, then two-point X⁻³
  extrapolation of the correlation energy (Halkier 1998); extrapolate the HF reference
  separately

### What a run writes

Every calculation writes into `results/`, which is **gitignored in full** — all of it is
generated output. The reproducibility record is the pinned `Dockerfile` plus the `versions`
block written into every JSON.

| Producer | Files | Record |
| --- | --- | --- |
| `water_hf.py` | `water_hf.txt`, `water_hf.json` | `_record.py` schema |
| `water_dft.py` | `water_b3lyp.txt`, `water_b3lyp.json` | + `grid_level` |
| `water_mp2.py` | `water_mp2.txt`, `water_mp2.json` | + `scf_energy` |
| `co2_test.py` | `co2_b3lyp.txt`, `co2_b3lyp.json` | + `grid_level` |
| `co2_sp.py` | `co2_energy.txt`, `co2_energy.json` | + `grid_level` |
| `optimize_water.py` | `water_opt.xyz`, `water_opt.json` | + `optimizer` |
| `water_B3LYP_631Gd.py` | `water_b3lyp_631gd.txt`, `water_b3lyp_631gd.json` | *own hand-rolled schema — no `geometry_angstrom`* |
| `POST /jobs` | `job_<id>.json` | service schema — adds `timings_seconds`, `environment` |

`scripts/_record.py` is the shared writer six of the seven scripts import. It records the
energy, the geometry in Ångström, the basis, `OMP_NUM_THREADS` and the versions of PySCF,
NumPy, SciPy and Python. It lives in `scripts/`, which is bind-mounted — so adding a script
needs no image rebuild.

### Container architecture

```dockerfile
FROM python:3.10-slim
# Chemistry: numpy==1.26.4  scipy==1.13.1  pyscf==2.4.0
#            geometric==1.0.0  pyberny==0.6.3        (geometry optimisers)
# Service:   fastapi==0.141.1  uvicorn==0.52.4  pydantic==2.13.4
# No Qt on purpose: the desktop client runs on the HOST and reaches this over HTTP.
# No COPY: scripts arrive by bind mount, so editing one needs no rebuild.
WORKDIR /workspace
RUN mkdir -p /workspace/results /workspace/scripts /workspace/jobs
ENTRYPOINT ["/usr/local/bin/python"]
```

The `ENTRYPOINT` is why compose commands read as bare arguments — `scripts/water_hf.py`
and `-m uvicorn app:api …` are both just argv for `python`.

**One build, two services.** `docker-compose.yml` defines both from the same context:

```yaml
pyscf:                                     # batch runner        image: week3/pyscf:1.0
  volumes:
    - ./scripts:/workspace/scripts:rw      # live script editing
    - ./results:/workspace/results:rw
    - ./jobs:/workspace/jobs:rw
  command: scripts/optimize_water.py
  environment: [OMP_NUM_THREADS=1, PYTHONUNBUFFERED=1, PYTHONPATH=/workspace]

api:                                       # Service-Runner      image: week4/pyscf:1.1
  volumes:
    - ./app.py:/workspace/app.py:ro        # read-only: the container never rewrites the contract
    - ./runner.py:/workspace/runner.py:ro
    - ./scripts:/workspace/scripts:rw
    - ./results:/workspace/results:rw      # no ./jobs — the service writes to results/
  command: -m uvicorn app:api --host 0.0.0.0 --port 8000
  ports: ["8000:8000"]
```

The two tags share every layer — `docker images` listing 900 MB twice is one image, not two.

**Live editing is not uniform.** `scripts/` genuinely is live: every `docker compose run`
starts a new interpreter that re-reads the file. `app.py` and `runner.py` are **not** —
uvicorn has no `--reload`, so it reads them once at startup. After editing either, run
`docker compose restart api`.

### What it costs, and cleaning up

```bash
docker compose down                                   # stop the service
docker image rm week3/pyscf:1.0 week4/pyscf:1.1       # ~900 MB back
docker system df                                      # what Docker is actually holding
```

## 🌉 From a script to a service

You can already run every calculation in this repository. So why Week 4?

Look at what the Week 3 scripts actually are. The molecule is a **literal inside the file**
(`water_hf.py` lines 6–10), so a new geometry means editing Python. Every setting is an
assignment statement. Every run pays a fresh container start. Nothing records how long
anything took — no Week 3 script imports `time`. And a chemist who does not read Python
cannot drive any of it.

Week 4 changes **none of the physics** — same image, same pins, same `OMP_NUM_THREADS=1`,
same numbers to twelve decimals. It changes the *door*: the molecule becomes an input, the
settings become a validated schema, timings come back with every result, and a colleague on
another machine can submit a job through a form.

<a id="week-4"></a>

## 🌐 Week 4 — the Service-Runner

```bash
docker compose up api
```

Then open **http://127.0.0.1:8000/docs** — FastAPI generates that page from the same model
the endpoints validate against.

### The contract

Two calls, and one thing to know about them:

| Call | Returns |
| --- | --- |
| `POST /jobs` | `201` and `{"job_id": "…"}` |
| `GET /jobs/{id}/result` | `200` and the full record |
| `GET /health` | `{"status":"ok","methods":["HF","B3LYP","MP2"]}` — needs no PySCF, so it answers anywhere |

**It is synchronous.** `POST /jobs` runs the calculation *before* it returns the id, so the
201 arrives only once the SCF has finished and the result is ready the instant you have the
id. There is no queue and no status field — the two-call shape is the *shape* of a job
service, honestly implemented as the simplest thing that works. Endpoints are plain `def`,
so FastAPI runs them in a threadpool and a long SCF does not block other requests. Turning
this into a real queue is the honest next step, not something Week 4 pretends to have done.

```bash
curl -s -X POST http://127.0.0.1:8000/jobs \
  -H 'Content-Type: application/json' \
  -d '{"molecule":"O 0 0 0; H 0 -0.757 0.587; H 0 0.757 0.587","method":"HF"}'
# {"job_id":"b6984f1be8bf"}

curl -s http://127.0.0.1:8000/jobs/b6984f1be8bf/result
```

### The request — `JobSpec`

| Field | Type | Default | Bounds |
| --- | --- | --- | --- |
| `molecule` | string | **required** | any geometry `gto.M` accepts — `;` or newline separated |
| `method` | enum | `"HF"` | `HF` \| `B3LYP` \| `MP2` |
| `basis` | string | `"def2-svp"` | any name PySCF accepts — **not** checked by the schema |
| `grid` | int | `3` | `0 ≤ grid ≤ 9`; read only by B3LYP |
| `conv_tol` | float | `1e-9` | `0 < conv_tol < 1` |
| `charge` | int | `0` | — |
| `spin` | int | `0` | `≥ 0` |

### The result

```json
{
  "energy_hartree": -75.960975166983,
  "method": "HF",  "basis": "def2-svp",  "grid": 3,  "conv_tol": 1e-09,
  "timings_seconds": { "build": 0.0031, "solve": 0.0569 },
  "versions": {
    "python": "3.10.21",
    "platform": "Linux-6.6.87.2-microsoft-standard-WSL2-x86_64-with-glibc2.41",
    "pyscf": "2.4.0", "numpy": "1.26.4", "scipy": "1.13.1"
  },
  "environment": { "OMP_NUM_THREADS": "1" },
  "job_id": "b6984f1be8bf"
}
```

Four parts, and each is a claim: **the number**, **the cost**, **the provenance**, and
**the one setting most likely to change the last digits between two machines**. A result
record is a reproducibility claim, not just a float.

### When it says no

| Status | Meaning |
| --- | --- |
| `422` | The spec failed validation. **No compute was attempted** — pydantic rejects it before `runner` is called, which is why the test for this is named `test_invalid_specs_are_rejected_before_any_compute` |
| `404` | No job with that id **in this process** |
| `500` | The spec was legal but PySCF failed on it — e.g. a `molecule` string that is valid JSON but not a parsable geometry, since `basis` and `molecule` are not checked by the schema |

### Where results go

Job ids live in a plain in-memory dict, so **they die with the container** and a restart
turns every old id into a 404. Every successful result is *also* written to
`results/job_<id>.json`, which is bind-mounted — so it is readable from the host the moment
the call returns, and `cat results/job_<id>.json` is the way to re-read a job the API has
forgotten. A rejected spec writes nothing.

### 🔒 What this is not

Said plainly, because the code says it plainly:

- **No authentication**, and `ports: "8000:8000"` publishes on *every* interface with
  uvicorn on `0.0.0.0`. On a shared network, anyone who can reach port 8000 can queue
  calculations on your machine. In a classroom that is the point — it is how
  `SERVICE_URL=http://<classmate-ip>:8000` works. To keep it local, publish
  `"127.0.0.1:8000:8000"` instead. Windows will prompt for a firewall exception; allow it
  on private networks only.
- **No CORS middleware** — a browser page from another origin cannot call it. curl, the
  GUI and `/docs` itself are unaffected.
- **No queue, no cancel, no job list.** `POST` blocks for the length of the calculation, and
  the files under `results/` are the only record of anything the process has forgotten.

This is a single-process teaching service and is honest about it.

<a id="desktop-client"></a>

## 🖥️ The desktop client

The client runs on the **host**, never in the container. It never imports PySCF; it speaks
JSON over HTTP. That is what lets it run natively on Windows.

### Set up the host environment

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt -r requirements-gui.txt
```

```bash
python3 -m venv .venv && source .venv/bin/activate
python -m pip install -r requirements-dev.txt -r requirements-gui.txt
```

| File | Contents | Where it belongs |
| --- | --- | --- |
| `requirements.txt` | fastapi, uvicorn, pydantic | already in the image; install on the host only to run uvicorn outside Docker |
| `requirements-dev.txt` | the above + pytest, httpx | host, to run the tests |
| `requirements-gui.txt` | PySide6, pyinstaller | **host only** — `python:3.10-slim` has no Qt libraries |

> This virtualenv deliberately contains **no PySCF, NumPy or SciPy** — which is exactly why
> it installs cleanly on native Windows. `python scripts/water_hf.py` from it fails
> immediately with `ModuleNotFoundError: No module named 'pyscf'`, and that is the expected
> result, not a broken install. The scripts run in the container, or in a Linux/macOS
> environment where PySCF is installed.

The image pins its packages inline in the `Dockerfile` rather than installing
`requirements.txt`, so the two lists can drift. They currently agree exactly; if you bump
one, bump the other.

### Run it

Two terminals — the service, then the client:

```bash
docker compose up api                       # terminal 1
```

```powershell
.\.venv\Scripts\python.exe gui\main.py      # terminal 2  (Windows)
```

```bash
python gui/main.py                          # terminal 2  (macOS / Linux)
```

Point it somewhere else with `SERVICE_URL`:

```powershell
$env:SERVICE_URL = "http://192.168.1.50:8000"
```

### The form

**Run stays disabled until the form is valid.** `gui/validate.py` holds the rules —
molecule non-empty, method in the enum, basis non-empty, `0 < conv_tol < 1`, `0 ≤ grid ≤ 9`
— and the problems appear in the status line. The same constraints exist twice on purpose:
in `validate.py` for instant feedback, and in `app.py`'s Pydantic model as the authority. A
bad request is stopped at the form *and* would be rejected with 422 if it ever arrived.
`validate.py` is deliberately Qt-free, which is why it is unit-tested with no display.

Two limits worth knowing: the form exposes five of `JobSpec`'s seven fields — `charge` and
`spin` are in the contract but have no widget, so use `/docs` or curl for ions and
open-shell species. And the client is single-threaded: during a long job the window stops
repainting and the OS may call it unresponsive. It is not hung, it is waiting on the HTTP
call (300 s timeout).

<a id="tests"></a>

## 🧪 Tests

```bash
python -m pytest tests/ -q      # 13 passed
```

| File | Tests | Proves |
| --- | --- | --- |
| `test_service.py` | 8 | The HTTP contract — 201 on submit, 404 on unknown, 422 on every invalid spec, and the four keys of the result record |
| `test_validate.py` | 4 | The form rules, with no Qt and no display |
| `test_gui_smoke.py` | 1 | The window constructs and the Run button tracks validity, offscreen |

**None of them runs a calculation.** `test_service.py` monkeypatches `runner.run_job` with a
stub, and the real `from pyscf import …` sits inside the function body of `runner.run_job`,
so it never executes. The whole suite therefore passes on native Windows in about two
seconds. The teaching point is the boundary: these tests prove the *contract*, not the
physics. The physics is proved by the reference energies above, in the container.

Without the GUI extras installed, `test_gui_smoke.py` skips rather than fails.

<a id="qt-trap"></a>

### ⚠️ The `QT_QPA_PLATFORM` trap

Qt's `offscreen` platform is what lets a window construct and paint with no display server —
CI, or a bare WSL shell. `test_gui_smoke.py` sets it for its own process, and CI sets it for
that one step (on Linux, Qt still needs `libegl1`, `libgl1`, `libxkbcommon-x11-0`,
`libdbus-1-3` and `libglib2.0-0` even offscreen).

**Do not export it in your own shell.** If `QT_QPA_PLATFORM=offscreen` is set when you launch
`gui/main.py`, the client starts, validates, submits and returns results — with no window
ever appearing. It looks like a broken GUI and is not.

```powershell
Remove-Item Env:\QT_QPA_PLATFORM -ErrorAction SilentlyContinue
```

## ⚙️ Continuous integration

`.github/workflows/ci.yml` runs on every push and pull request. Neither job installs PySCF —
that is the point.

| Job | Runs | Proves |
| --- | --- | --- |
| `tests` | pytest on `test_service.py` + `test_validate.py`, Python 3.10 | The JSON contract holds without any chemistry stack |
| `gui-smoke` | Qt libs, offscreen smoke test, then PyInstaller | The client launches headlessly and freezes into a runnable binary |

`gui-smoke` uploads `dist/compchem-client` as the artifact `compchem-client-linux`
(14-day retention).

> On your fork, Actions are **disabled until you enable them** — open the **Actions** tab
> once and confirm. Until then the badge shows no status; that is not a failing build.

### Freeze the client

```bash
pyinstaller --noconfirm --clean --name compchem-client --onedir gui/main.py
```

Produces `dist/compchem-client/compchem-client` (~1.9 MB on Windows), plus a `build/`
scratch tree and `compchem-client.spec`. All three are gitignored build products — the
deliverable is the CI artifact or a release asset, never a committed binary.

The executable is small because it bundles only the Qt client. It still needs a running
service to talk to: freezing the interface does not freeze the chemistry.

## 📁 Project structure

```
CompChem-PySCF/
├── 🐳 Dockerfile              # Python 3.10 + PySCF + FastAPI — one build, two roles (no Qt, deliberately)
├── 🔧 docker-compose.yml      # two services: pyscf (batch) and api (:8000)
├── 🙈 .dockerignore           # trims the build context
├── 🙈 .gitignore              # results/, jobs/, .venv/, build artefacts — everything generated
├── 🌐 app.py                  # FastAPI Service-Runner — POST /jobs, GET /jobs/{id}/result
├── ⚛️ runner.py               # the ONLY module that imports PySCF, and it does so lazily
├── 📌 requirements.txt        # service runtime — fastapi, uvicorn, pydantic
├── 📌 requirements-dev.txt    # + pytest, httpx (FastAPI's TestClient transport)
├── 📌 requirements-gui.txt    # PySide6, pyinstaller — host only
├── 📜 scripts/                # calculation scripts — bind-mounted, so edits need no rebuild
│   ├── _record.py             # shared writer: results/<name>.json + package versions
│   ├── optimize_water.py      # B3LYP/def2-SVP geometry optimisation (geomeTRIC)
│   ├── water_hf.py            # RHF/def2-SVP
│   ├── water_dft.py           # B3LYP/def2-SVP, same geometry as water_hf/water_mp2
│   ├── water_mp2.py           # MP2/def2-SVP
│   ├── water_B3LYP_631Gd.py   # B3LYP/6-31G(d) — hand-rolled record, not _record.py
│   ├── co2_test.py            # CO₂ B3LYP/def2-SVP → results/co2_b3lyp.*   (used by the assignment)
│   └── co2_sp.py              # the same calculation → results/co2_energy.*
├── 🖥️ gui/                    # PySide6 desktop client — runs on the HOST
│   ├── main.py                # JobForm; SERVICE_URL, default 127.0.0.1:8000
│   └── validate.py            # Qt-free form rules, unit-tested with no display
├── 🧪 tests/                  # 13 tests, none of which import PySCF
│   ├── test_service.py        # API contract, runner stubbed
│   ├── test_validate.py       # form logic
│   └── test_gui_smoke.py      # offscreen does-it-launch
├── ⚙️ .github/workflows/ci.yml # tests + headless GUI smoke + PyInstaller freeze
├── 📊 results/                # generated output — gitignored in full, absent from a clean clone
├── 📋 jobs/                   # empty bind-mount target — gitignored; service results go to results/
├── 📄 LICENSE                 # MIT
└── 📚 docs/
    ├── local_MacOS.md         # Apple Silicon setup
    ├── local_Windows.md       # Windows / WSL2 setup
    └── local_original.md      # superseded standalone walkthrough
```

## 🌍 Environment variables

| Variable | Set where | Effect | Do I set it? |
| --- | --- | --- | --- |
| `OMP_NUM_THREADS` | `docker-compose.yml`, both services | BLAS threading — the main source of last-digit drift | Already set to `1`. Set it yourself only outside Docker |
| `PYTHONUNBUFFERED` | `docker-compose.yml` | Container output appears in real time | No |
| `PYTHONPATH` | `docker-compose.yml` | Module resolution inside `/workspace` | No |
| `SERVICE_URL` | your shell | Where the GUI sends jobs (default `http://127.0.0.1:8000`) | The one knob you normally touch |
| `QT_QPA_PLATFORM` | the test file, and CI | `offscreen` renders with no display server | **Never export it in your own shell** |
| `SMOKE_TEST` | your shell | Makes `gui/main.py` construct, paint and exit 0 | Only to check the GUI launches |

## 🛠️ Platform setup

- 🍎 **macOS (Apple Silicon)** — [docs/local_MacOS.md](./docs/local_MacOS.md)
- 🪟 **Windows / WSL2** — [docs/local_Windows.md](./docs/local_Windows.md)
- 🐧 **Linux** — Docker Engine via `curl -fsSL https://get.docker.com | sudo sh`. For a
  local PySCF instead, follow [docs/local_Windows.md](./docs/local_Windows.md) Route A from
  the `python3 -m venv` step — it is plain Ubuntu and applies verbatim.
- 📜 [docs/local_original.md](./docs/local_original.md) — superseded Week 3-era walkthrough,
  kept for reference

## 📦 Assignment — Containerise a Calculation

**Due before Session 4. Submitted as a tagged release URL — no registry push.**

CO₂ single-point energy, B3LYP/def2-SVP. The screening-quality basis is
deliberate: the deliverable is the container, not the number.

1. **Run it** (bind mount — nothing is baked into the image):

   ```bash
   docker compose build pyscf
   docker compose run --rm pyscf scripts/co2_test.py
   cat results/co2_b3lyp.json
   ```

2. **Pin the environment**: every package version pinned, and the base image
   pinned by digest — `FROM python:3.10-slim@sha256:<digest>`. Get the digest
   with `docker buildx imagetools inspect python:3.10-slim` and take the
   top-level `Digest:` (the multi-arch index), not a per-platform one.

3. **Write `RESULTS.md`**: method, basis, grid level, `conv_tol`, and threads
   (`OMP_NUM_THREADS`, set to 1 in `docker-compose.yml`).

4. **Tag and submit**:

   ```bash
   git tag -a week3 -m "Week 3" && git push --tags
   ```

   then draft a release from the tag and submit its URL.

### 📋 Deliverables

| Deliverable                                                          | Points |
| -------------------------------------------------------------------- | ------ |
| a tagged release URL that a marker can clone and build                | 4      |
| `results/co2_b3lyp.json` + `RESULTS.md` — energy, geometry, versions  | 4      |
| `Dockerfile` — packages pinned, base pinned by digest                 | 2      |

Marking is by re-running you: your release is cloned into an empty directory
and built. If it builds and reproduces the energy, the 4 points are yours.

> **Not this week:** pushing to GitHub Container Registry. Registries and
> automated builds are Week 4 — you need no Personal Access Token, and an image
> pushed from a private fork could not be pulled by the marker anyway.

## 🧩 Make it yours

| You want to add… | What to do | Rebuild? |
| --- | --- | --- |
| A new calculation | Copy `scripts/water_hf.py`, change the geometry or method, keep `from _record import record` | **No** — `scripts/` is bind-mounted |
| A new method in the service | Edit the enum where it lives — `runner.SUPPORTED_METHODS`, the branch in `runner.run_job`, `JobSpec.method`, and `gui/validate.METHODS` — then `docker compose restart api` | **No** — but restart, since uvicorn has no `--reload` |
| A new Python package | Add the pin to the `Dockerfile` **and** the matching `requirements*.txt`, then `docker compose build` | **Yes** |

The method enum lives in four places on purpose: the service is the authority, the client
gets instant feedback, and the test suite proves they agree.

## 🐛 Troubleshooting

**Python version compatibility**

- **Week 3 needs no local Python** — the container provides it on every platform.
- **Week 4 does**: the tests, the desktop client and the freeze all run on the host. It need
  not match the image (image 3.10.21, CI 3.10, host venv verified on 3.12.10), because
  nothing on the host imports PySCF.
- **Windows**: there is no native PySCF build — no `win_amd64` wheel for any version, no
  conda-forge `win-64` package, so `pip install pyscf` falls back to a source build and dies
  at CMake. Use WSL2 ([docs/local_Windows.md](./docs/local_Windows.md)) or the container.
  PySide6 *does* ship Windows wheels, which is the whole reason the GUI is on the host.

**The GUI runs but no window appears** — `QT_QPA_PLATFORM=offscreen` is set in your shell.
See [the trap above](#qt-trap).

**`docker compose up` seems to run a calculation** — it does. Name the service.

**Reporting a problem with this repository** — open an issue upstream. Coursework is
submitted as a release on your own fork, never as a pull request.

## 📚 Additional resources

- **PySCF**: https://pyscf.org/user.html
- **Basis Set Exchange**: https://www.basissetexchange.org/
- **Docker build best practices**: https://docs.docker.com/build/building/best-practices/
- **FastAPI**: https://fastapi.tiangolo.com/
- **PySide6**: https://doc.qt.io/qtforpython-6/
- **pytest**: https://docs.pytest.org/
- **GitHub Actions**: https://docs.github.com/actions

## 📄 License

MIT. See [LICENSE](./LICENSE).

---

**🎓 Course**: Computational Chemistry
**📅 Module**: Weeks 3–4 — Containers, Services & Desktop Clients
**👨‍🏫 Instructor**: Viwat Vchirawongkwin
**🏫 Institution**: Chulalongkorn University
