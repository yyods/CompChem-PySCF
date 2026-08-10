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
5. **Deploy** containerized calculations to GitHub Container Registry (GHCR)

## 🔧 Prerequisites

**Required Setup:**

- Docker Desktop/Engine with `docker compose` v2
- GitHub Personal Access Token with `write:packages` scope
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
├── 📊 results/               # Output files (.xyz, .txt, .json) — gitignored
├── 📋 jobs/                  # Batch job artifacts — gitignored
└── 📚 docs/                  # Platform-specific setup guides
    ├── local_MacOS.md        # Apple Silicon setup
    ├── local_Windows.md      # Windows / WSL2 setup
    └── local_original.md     # Original macOS guide
```

`results/`, `jobs/` and `resources/` are gitignored: they are created on first
run and never committed.

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

- **Quick screening**: `def2-SVP` basis, `grids.level=3`
- **Production**: `def2-TZVP` basis, `conv_tol=1e-9`
- **High accuracy**: `def2-QZVP` + CBS extrapolation

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

## 📦 Assignment: GHCR Deployment

**Objective**: Containerize CO₂ single-point calculation and push to GitHub Container Registry

### Steps:

1. **Build & Test Locally**

   ```bash
   docker compose run --rm pyscf scripts/co2_test.py
   cat results/co2_b3lyp.txt
   ```

2. **Authenticate to GHCR**

   ```bash
   echo $CR_PAT | docker login ghcr.io -u <USERNAME> --password-stdin
   ```

3. **Tag & Push**
   ```bash
   docker tag week3/pyscf:1.0 ghcr.io/<USERNAME>/pyscf-co2:week3
   docker push ghcr.io/<USERNAME>/pyscf-co2:week3
   ```

### 📋 Deliverables

- ✅ Git repository with complete codebase
- ✅ `RUNBOOK.md` with build/run instructions
- ✅ `RESULTS.md` with energy values and metadata
- ✅ GHCR image link with digest hash

## 🐛 Troubleshooting

### Docker Desktop Path Issues (macOS)

```bash
# Move to accessible location if bind mounts fail
cp -r /path/to/project /Users/$USER/docker-projects/
cd /Users/$USER/docker-projects/CompChem-PySCF
```

### Python Version Compatibility

- **macOS/Linux**: Python 3.10-3.11 supported
- **Windows**: Python 3.10 required (pre-built wheels limitation)

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
