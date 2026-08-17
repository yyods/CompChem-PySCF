# Week 3 — Containers & Electronic-Structure Workflows

[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](./Dockerfile)
[![Cross-Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-success)](./docker-compose.yml)
[![PySCF](https://img.shields.io/badge/PySCF-2.4.0-orange)](https://pyscf.org/)

A complete containerized environment for quantum chemistry calculations using PySCF, demonstrating reproducible computational workflows across platforms.

## 🎯 Learning Objectives

By the end of this module, students will:

1. **Explain** why containers matter for computational reproducibility in quantum chemistry
2. **Build and run** a Docker image that executes PySCF jobs deterministically
3. **Compare** the wall-clock cost of HF, B3LYP and MP2 on the same water
   geometry, and explain why their total energies cannot be ranked for accuracy
   against each other
4. **Configure** SCF/geometry convergence and basis set options appropriately
5. **Record** a container's provenance — digest-pinned base, pinned packages,
   and package versions written into the results JSON — so a clean clone of your
   tagged release rebuilds to the same energy

## 🔧 Prerequisites

**Required Setup:**

- Docker Desktop/Engine with `docker compose` v2
- Basic command line familiarity

**Quick Verification:**

```bash
docker --version
docker compose version
docker run hello-world
```

## 🚀 Quick Start

### 1. Clone and Build

```bash
git clone https://github.com/yyods/CompChem-PySCF.git
cd CompChem-PySCF
docker compose build pyscf
```

### 2. Run Test Calculation

```bash
# B3LYP geometry optimization of water
docker compose run --rm pyscf scripts/optimize_water.py

# Check results
cat results/water_opt.xyz
```

### 3. Explore Methods

```bash
# Hartree-Fock calculation
docker compose run --rm pyscf scripts/water_hf.py

# DFT calculation
docker compose run --rm pyscf scripts/water_dft.py

# MP2 calculation
docker compose run --rm pyscf scripts/water_mp2.py

# CO₂ single-point energy
docker compose run --rm pyscf scripts/co2_test.py
```

## 📁 Project Structure

```
CompChem-PySCF/
├── 🐳 Dockerfile              # Python 3.10 + PySCF environment
├── 🔧 docker-compose.yml      # Cross-platform bind mounts
├── 📜 scripts/                # Calculation scripts
│   ├── optimize_water.py      # B3LYP geometry optimization
│   ├── co2_test.py           # CO₂ single-point energy
│   ├── water_B3LYP_631Gd.py # B3LYP/6-31G(d) calculation
│   ├── water_dft.py          # DFT demonstration
│   ├── water_hf.py           # Hartree-Fock calculation
│   └── water_mp2.py          # MP2 correlation energy
├── 📊 results/               # .txt/.xyz/.json committed as the record
├── 📋 jobs/                  # Batch job artifacts — gitignored
└── 📚 docs/                  # Platform-specific setup guides
    ├── local_MacOS.md        # Apple Silicon setup
    ├── local_Windows.md      # Windows / WSL2 setup
    └── local_original.md     # Superseded standalone walkthrough
```

`jobs/` and `resources/` are gitignored. Inside `results/`, the small structured
outputs (`.txt`, `.xyz`, `.json`) **are** committed — together with the Dockerfile
and `docker-compose.yml` they are the environment record. Anything else there
(checkpoints, logs) stays ignored.

## 🔬 Method Comparison

| Method             | Formal cost | MAE, atomization energies\* | Use in this repo                                                    |
| ------------------ | ----------- | --------------------------- | ------------------------------------------------------------------- |
| **HF**             | O(N⁴)       | ~75                         | `water_hf.py` — reference wavefunction, orbital analysis             |
| **B3LYP** (hybrid) | O(N⁴)       | ~3                          | `water_dft.py`, `co2_test.py`, `optimize_water.py` — geometries      |
| **MP2**            | O(N⁵)       | ~7                          | `water_mp2.py` — correlation demo; dispersion-bound complexes        |

\* kcal mol⁻¹ vs experiment, G2-type sets at 6-311+G(3df,2p). These are **three
separate studies on sets of different size** — read them as orders of magnitude,
not a controlled series.

Note the ordering for this property: MP2 costs more than B3LYP and is *less*
accurate. Cost buys accuracy *within* a hierarchy (HF → MP2 → CCSD(T)), not
across families. See the Week 2 slide "Cost vs Accuracy — Not One Ladder".

The three water scripts share a geometry and def2-SVP, so their total energies
sort as E(B3LYP) < E(MP2) < E(HF). That ordering is **not** an accuracy ranking:
total energies from different methods are not comparable to each other.

### Recommended Settings

- **Quick screening (DFT)**: `def2-SVP`, `grids.level=3` — conformer search only; do not report energetics
- **Production (DFT)**: `def2-TZVP` (`conv_tol=1e-9` is already the PySCF default; tighten toward `1e-10` for gradients and properties)
- **Converged single points (DFT)**: `def2-QZVPP` — near the basis-set limit, but still not CBS
- **Correlated wavefunctions (MP2/CCSD(T))**: `cc-pVTZ` / `cc-pVQZ`, then two-point X⁻³ extrapolation of the correlation energy (Halkier 1998); extrapolate the HF reference separately

## 🏗️ Container Architecture

### Cross-Platform Dockerfile

```dockerfile
FROM python:3.10-slim
# Pinned versions: numpy==1.26.4, scipy==1.13.1, pyscf==2.4.0
# No embedded scripts - pure bind mount approach
WORKDIR /workspace
ENTRYPOINT ["/usr/local/bin/python"]
```

### Bind Mount Strategy

```yaml
volumes:
  - ./scripts:/workspace/scripts:rw # Live script editing
  - ./results:/workspace/results:rw # Persistent outputs
  - ./jobs:/workspace/jobs:rw # Batch artifacts
```

## 🖥️ Platform-Specific Setup

### 🍎 macOS (Apple Silicon)

```bash
# See detailed guide
open docs/local_MacOS.md
```

### 🪟 Windows

```powershell
# See detailed guide
start docs/local_Windows.md
```

### 🐧 Linux

```bash
# Docker Engine installation
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

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

## 🐛 Troubleshooting

### Docker Desktop Path Issues (macOS)

```bash
# Move to accessible location if bind mounts fail
cp -r /path/to/project /Users/$USER/docker-projects/
cd /Users/$USER/docker-projects/CompChem-PySCF
```

### Python Version Compatibility

- **No local Python needed** — `docker compose build pyscf` provides it on every platform.
- **macOS/Linux**: for an optional local install, ordinary PyPI wheels with Python 3.10-3.11.
- **Windows**: there is no native PySCF build — no `win_amd64` wheel for any version and no
  conda-forge `win-64` package, so `pip install pyscf` falls back to a source build and dies at
  CMake. Use WSL2 (see `docs/local_Windows.md`) or the container.

### Memory Issues

```bash
# Increase Docker memory allocation
# Docker Desktop → Settings → Resources → Memory: 8GB+
```

## 📚 Additional Resources

- **PySCF Documentation**: https://pyscf.org/user.html
- **Basis Set Exchange**: https://www.basissetexchange.org/
- **Docker Best Practices**: https://docs.docker.com/develop/best-practices/

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/calculation-type`)
3. Commit changes (`git commit -am 'Add new calculation method'`)
4. Push to branch (`git push origin feature/calculation-type`)
5. Create Pull Request

## 📄 License

This educational content is available under MIT License. See `LICENSE` file for details.

---

**🎓 Course**: Computational Chemistry  
**📅 Module**: Week 3 - Container Workflows  
**👨‍🏫 Instructor**: Viwat Vchirawongkwin  
**🏫 Institution**: Chulalongkorn University
