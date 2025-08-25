# Week 3 — GUI-Driven Quantum Chemistry with FastAPI & Agile Development

[![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?logo=fastapi)](https://fastapi.tiangolo.com)
[![PySide6](https://img.shields.io/badge/PySide6-6.0+-red?logo=qt)](https://doc.qt.io/qtforpython/)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions-blue?logo=github)](https://github.com/features/actions)

Transform Week 2's containerized PySCF workflows into a production-ready desktop GUI application with microservice architecture, automated testing, and data visualization capabilities using modern Agile development practices.

## 🎯 Learning Outcomes

By completing Week 3, students will:

1. **Design** microservice architectures separating GUI clients from computational backends
2. **Implement** REST APIs using FastAPI with proper request/response schemas
3. **Develop** native desktop applications using PySide6 for scientific computing
4. **Apply** Agile methodologies with sprint planning, story boards, and Definition of Done
5. **Build** CI/CD pipelines for automated testing, artifact generation, and data visualization
6. **Create** data analysis workflows aggregating computational results into CSV and plots
7. **Deploy** containerized services with Docker Compose for local development environments

## 📋 Prerequisites

### Required Software

| Component | Version | Platform | Installation |
|-----------|---------|----------|--------------|
| **Python** | 3.10+ | All | [python.org](https://python.org/downloads) |
| **Docker** | Engine 20+ | All | [docs.docker.com](https://docs.docker.com/get-docker/) |
| **Git** | 2.30+ | All | [git-scm.com](https://git-scm.com/downloads) |
| **VS Code** | Latest | All | [code.visualstudio.com](https://code.visualstudio.com/) |

### Platform-Specific Notes

- **Windows**: Use PowerShell or WSL2 for command execution
- **macOS**: Ensure Xcode Command Line Tools installed (`xcode-select --install`)
- **Linux**: Install development packages (`sudo apt install python3-dev build-essential`)

### Account Requirements

- GitHub account with repository access
- Basic understanding of quantum chemistry concepts (HF, DFT, basis sets)

## 🚀 Quick Start (5 Minutes)

### 1. Clone and Setup

```bash
# Clone the repository
git clone https://github.com/yyods/CompChem-PySCF.git
cd CompChem-PySCF

# Switch to Week 3 branch
git checkout week3

# Verify Docker installation
docker --version
docker compose version
```

### 2. Build and Start Service

```bash
# Build the FastAPI service container
docker compose build pyscf_service

# Start the service in background
docker compose up -d pyscf_service

# Verify service health
curl http://localhost:8000/health
# Expected: {"ok": true}
```

### 3. Install and Run GUI

```bash
# Navigate to GUI application
cd apps/pyscf_gui

# Install dependencies (virtual environment recommended)
pip install -r requirements.txt

# Launch the GUI application
python -m gui.main
```

### 4. Run Your First Calculation

1. **In the GUI:**
   - Paste water molecule XYZ:
     ```
     3

     O 0.0000 0.0000 0.0000
     H 0.7571 0.0000 0.5861
     H -0.7571 0.0000 0.5861
     ```
   - Select Method: `HF`
   - Set Basis: `def2-SVP`
   - Click **Run**

2. **Verify Results:**
   ```bash
   # Check service logs
   docker compose logs pyscf_service

   # View result JSON
   ls results/
   cat results/<job_id>.json
   ```

Expected energy: approximately `-75.98` Hartree for water HF/def2-SVP.

## 🏗️ Step-by-Step Lab Guide

### Lab 1: Service Architecture Setup

**Objective**: Understand microservice separation and REST API design.

#### 1.1 Explore Service Structure

```bash
# Examine service directory
tree services/pyscf_service/
```

```
services/pyscf_service/
├── Dockerfile              # Python 3.10 + PySCF environment
├── requirements.txt         # FastAPI, Pydantic, PySCF dependencies
└── app/
    ├── __init__.py
    ├── main.py             # FastAPI application entry point
    ├── runner.py           # PySCF computation engine
    └── schemas.py          # Request/response data models
```

#### 1.2 Test API Endpoints

```bash
# Health check
curl -X GET http://localhost:8000/health

# Submit job (copy-paste as single command)
curl -X POST "http://localhost:8000/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "molecule_xyz": "3\n\nO 0 0 0\nH 0 0.757 0.586\nH 0 -0.757 0.586\n",
    "method": "HF",
    "basis": "def2-SVP",
    "grid_level": 3,
    "conv_tol": 1e-9,
    "spin": 0,
    "charge": 0
  }'
# Expected: {"job_id": "uuid-string", "status": "done"}

# Retrieve result (replace JOB_ID)
curl -X GET "http://localhost:8000/jobs/JOB_ID/result"
```

#### 1.3 Understand Data Schemas

Examine `services/pyscf_service/app/schemas.py`:

```python
# Key data structures
class JobRequest(BaseModel):
    molecule_xyz: str       # XYZ format geometry
    method: str            # HF | B3LYP | MP2
    basis: str             # def2-SVP, def2-TZVP, etc.
    grid_level: int = 3    # DFT grid quality (0-9)
    conv_tol: float = 1e-9 # SCF convergence threshold
    spin: int = 0          # Spin multiplicity
    charge: int = 0        # Molecular charge

class JobResult(BaseModel):
    job_id: str
    system_id: str         # SHA1 hash of geometry
    method: str
    basis: str
    energy_hartree: float  # Total electronic energy
    timings: dict         # Performance metrics
    env: dict             # Environment versions
    ts: float             # Unix timestamp
```

### Lab 2: GUI Development with PySide6

**Objective**: Build responsive desktop interfaces for scientific applications.

#### 2.1 Examine GUI Architecture

```bash
# Navigate to GUI application
cd apps/pyscf_gui
tree .
```

```
apps/pyscf_gui/
├── pyproject.toml          # Project metadata and dependencies
├── requirements.txt        # PySide6, requests dependencies
├── core/
│   ├── __init__.py
│   ├── client.py          # HTTP client for service communication
│   └── schema.py          # GUI data models
└── gui/
    ├── __init__.py
    └── main.py            # Main application window
```

#### 2.2 Run GUI Components

```bash
# Install GUI dependencies
pip install PySide6 requests pydantic

# Start GUI with debug output
python -m gui.main --debug
```

#### 2.3 GUI Feature Testing

**Input Validation Tests:**

1. **Valid Input**: Enter water XYZ, select HF method → "Run" button enabled
2. **Invalid Input**: Clear XYZ field → "Run" button disabled
3. **Invalid Method**: Type random text in method field → validation error

**Job Submission Flow:**

1. Submit job → Progress indicator appears
2. Job completes → Results panel updates with energy value
3. Check `results/` directory → New JSON file created

### Lab 3: Data Analysis and Visualization

**Objective**: Process computational results into scientific insights.

#### 3.1 Generate Multiple Results

Run calculations for method comparison:

```bash
# Through GUI or API, submit jobs for:
# 1. Water HF/def2-SVP
# 2. Water B3LYP/def2-SVP  
# 3. Water MP2/def2-SVP
# 4. Water HF/def2-TZVP

# Verify 4 result files exist
ls results/*.json | wc -l
# Expected: 4
```

#### 3.2 Run Analysis Pipeline

```bash
# Navigate to analysis directory
cd analysis/

# Install analysis dependencies
pip install -r requirements.txt

# Generate summary CSV
python aggregate.py
# Creates: analysis_out/summary.csv

# Generate visualization plots
python plots.py
# Creates: analysis_out/energy_by_method_basis.png
#         analysis_out/deltaE_by_system_method.png

# View results
head analysis_out/summary.csv
```

#### 3.3 Interpret Results

**Summary CSV Columns:**

| Column | Description | Units |
|--------|-------------|-------|
| `job_id` | Unique calculation identifier | UUID |
| `system_id` | Geometry fingerprint | SHA1-10 |
| `method` | Quantum method | HF/B3LYP/MP2 |
| `basis` | Basis set | def2-SVP/TZVP |
| `energy_ha` | Total energy | Hartree |
| `dE_kjmol` | Relative energy vs. minimum | kJ/mol |

**Expected Trends:**
- HF energy: ~-75.98 Ha (highest/least stable)
- B3LYP energy: ~-76.23 Ha (intermediate)
- MP2 energy: ~-76.27 Ha (lowest/most stable)

### Lab 4: Agile Development Workflow

**Objective**: Apply professional software development practices.

#### 4.1 Explore Project Board

1. **Visit GitHub Repository** → Projects tab
2. **Examine Columns**: Backlog → In Progress → In Review → Done
3. **Review Labels**: `feat`, `fix`, `docs`, `test`, `infra`, `ux`, `experiment`

#### 4.2 Practice Story Development

**Exercise**: Implement MP2 method toggle in GUI

1. **Create Issue**:
   ```markdown
   Title: Add MP2 method support to GUI dropdown
   Labels: feat, ux
   
   As a computational chemist
   I want MP2 method available in the GUI
   So that I can compare correlation effects
   
   Acceptance Criteria:
   - [ ] MP2 option in method dropdown
   - [ ] Validation accepts MP2 input
   - [ ] Service processes MP2 jobs correctly
   ```

2. **Create Feature Branch**:
   ```bash
   git checkout -b feat/mp2-gui-support
   ```

3. **Implement Changes** (minimal example):
   ```python
   # In gui/main.py, update method dropdown
   self.method_combo.addItems(["HF", "B3LYP", "MP2"])
   ```

4. **Test Changes**:
   ```bash
   # Run GUI and verify MP2 appears in dropdown
   python -m gui.main
   ```

5. **Create Pull Request** using template checklist

#### 4.3 Review Definition of Done

Check `docs/DoD.md` requirements:

- [ ] **Tests pass**: Unit tests green locally and in CI
- [ ] **Code quality**: Linting and formatting standards met
- [ ] **Documentation**: README updated for new features
- [ ] **Review**: At least one peer review completed
- [ ] **Functionality**: Acceptance criteria verified

## ⚙️ CI/CD Pipeline

### Pipeline Jobs

The GitHub Actions workflow (`.github/workflows/ci.yml`) runs three parallel jobs:

#### 1. Tests Job (`tests`)

```yaml
- name: Run Tests
  env:
    PYSCF_DRYRUN: 1  # Fast mode for CI
  run: |
    pytest tests/ -v
    # Tests service endpoints and GUI core logic
```

**What it tests:**
- FastAPI endpoint responses (`test_service.py`)
- GUI input validation (`test_gui_core.py`)
- Schema validation and error handling

#### 2. GUI Artifact Job (`gui-artifact`)

```yaml
- name: Build GUI Artifact
  run: |
    cd apps/pyscf_gui
    zip -r ../../PySCF-GUI-sources.zip .
```

**Artifacts produced:**
- `PySCF-GUI-sources.zip`: Complete GUI source code package

#### 3. Visualization Job (`viz`)

```yaml
- name: Generate Analysis
  run: |
    cd analysis
    python aggregate.py
    python plots.py
```

**Artifacts produced:**
- `analysis_out/summary.csv`: Aggregated calculation results
- `analysis_out/*.png`: Energy comparison plots

### Reading Pipeline Results

1. **Go to**: Repository → Actions tab → Latest workflow run
2. **Check Status**: All three jobs should show green checkmarks
3. **Download Artifacts**: Click on artifact names to download ZIP files
4. **View Logs**: Click job names to see detailed execution logs

### Pipeline Triggers

- **Push** to any branch: Runs all jobs
- **Pull Request**: Runs tests and checks
- **Manual**: Repository dispatch via "Run workflow" button

## 🐛 Troubleshooting

### Service Issues

**Problem**: Service won't start (`docker compose up fails`)

```bash
# Check service logs
docker compose logs pyscf_service

# Common fixes:
# 1. Port 8000 already in use
docker compose down
pkill -f "8000"  # Kill process using port
docker compose up -d

# 2. Container build fails
docker compose build --no-cache pyscf_service
```

**Problem**: Jobs fail with PySCF errors

```bash
# Check specific job logs
docker compose exec pyscf_service tail -f /var/log/pyscf.log

# Verify dry run mode works
PYSCF_DRYRUN=1 docker compose up -d pyscf_service
curl -X POST localhost:8000/jobs -d '{"molecule_xyz":"...", "method":"HF", "basis":"def2-SVP"}'
```

### GUI Issues

**Problem**: GUI won't start (`python -m gui.main` fails)

```bash
# Check Python and PySide6 installation
python --version  # Must be 3.10+
python -c "import PySide6; print(PySide6.__version__)"

# Platform-specific fixes:

# macOS: Install system dependencies
brew install qt@6

# Windows: Use conda for reliable Qt installation
conda install pyside6

# Linux: Install system Qt libraries
sudo apt-get install qt6-base-dev python3-pyside6
```

**Problem**: GUI can't connect to service

```bash
# Verify service is running
curl http://localhost:8000/health

# Check firewall/network:
# Windows: Add firewall exception for port 8000
# macOS: Check System Preferences → Security & Privacy
# Linux: Configure iptables if needed

# Test with explicit IP
curl http://127.0.0.1:8000/health
```

### Analysis Issues

**Problem**: No plots generated (`analysis/plots.py` fails)

```bash
# Check Python plotting backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Install GUI backend:
# Linux
sudo apt-get install python3-tk

# macOS  
pip install PyQt5

# Windows (usually works by default)
pip install matplotlib --force-reinstall
```

**Problem**: Empty summary.csv

```bash
# Verify result files exist
ls results/*.json
file results/*.json  # Should show "JSON data"

# Check JSON format
python -c "import json; print(json.load(open('results/FILENAME.json')))"

# Regenerate analysis
cd analysis
rm -rf analysis_out/
python aggregate.py
```

### CI/CD Issues

**Problem**: Tests fail in CI but pass locally

```bash
# Run tests with exact CI environment
PYSCF_DRYRUN=1 pytest tests/ -v

# Check Python version consistency
python --version  # Should match CI (3.10+)

# Update test dependencies
pip install -r requirements.txt --upgrade
```

**Problem**: Artifacts not uploading

- **Check**: GitHub Actions permissions in repository settings
- **Verify**: Artifact paths exist in runner environment
- **Solution**: Add debug steps to workflow:

```yaml
- name: Debug Artifacts
  run: |
    ls -la analysis_out/
    ls -la apps/pyscf_gui/
```

## ❓ FAQ

### Technical Questions

**Q: Can I run multiple GUI instances?**  
A: Yes, but they share the same service instance. Each job gets a unique ID, so results won't conflict.

**Q: How do I add new quantum chemistry methods?**  
A: 1) Update `schemas.py` to include the method, 2) Add implementation in `runner.py`, 3) Update GUI dropdown, 4) Add tests.

**Q: What's the maximum molecule size?**  
A: Limited by PySCF and available memory. Recommend ≤20 atoms for this educational setup.

**Q: How do I change the service port?**  
A: Edit `docker-compose.yml` ports mapping and update `client.py` base URL.

### Workflow Questions

**Q: How do I create a new sprint?**  
A: Follow the backlog templates in `docs/Week3/sprint-X-backlog.md`. Create issues, assign story points, set sprint milestone.

**Q: What if CI tests are too slow?**  
A: Increase `PYSCF_DRYRUN=1` usage, mock external dependencies, reduce test molecule sizes.

**Q: How do I review pull requests effectively?**  
A: Check DoD criteria, run tests locally, verify acceptance criteria, test GUI functionality manually.

## 📚 References

### Internal Documentation

- **[Technical Specification](./specifications.md)**: Complete system requirements and architecture
- **[Sprint Backlogs](./sprint-backlog-master.md)**: Detailed user stories and task breakdown
- **[Story Implementations](./stories/README.md)**: Step-by-step implementation strategies
- **[Definition of Done](./DoD.md)**: Quality gates and completion criteria
- **[Root README](../../README.md)**: Week 2 containerization foundation

### External Resources

- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **PySide6 Tutorial**: [doc.qt.io/qtforpython](https://doc.qt.io/qtforpython/)
- **PySCF User Guide**: [pyscf.org/user.html](https://pyscf.org/user.html)
- **Docker Compose Reference**: [docs.docker.com/compose](https://docs.docker.com/compose/)
- **GitHub Actions Guide**: [docs.github.com/actions](https://docs.github.com/en/actions)
- **Agile Methodologies**: [agilemanifesto.org](https://agilemanifesto.org/)

### Scientific Background

- **Hartree-Fock Theory**: [atkins-chemistry.com](https://global.oup.com/academic/product/molecular-quantum-mechanics-9780199541423)
- **Density Functional Theory**: [dft.org](http://dft.org/)
- **Basis Set Exchange**: [basissetexchange.org](https://www.basissetexchange.org/)

## 📖 Appendix: Glossary

**API (Application Programming Interface)**: Set of defined methods for communication between software components.

**Agile Development**: Iterative software development methodology emphasizing collaboration, flexibility, and rapid delivery.

**Basis Set**: Mathematical functions used to represent molecular orbitals in quantum chemistry calculations.

**CI/CD (Continuous Integration/Continuous Deployment)**: Automated practices for testing, building, and deploying code changes.

**Container**: Lightweight, portable environment that packages applications with their dependencies.

**DFT (Density Functional Theory)**: Quantum mechanical method for investigating electronic structure using electron density.

**Docker Compose**: Tool for defining and running multi-container Docker applications.

**FastAPI**: Modern Python web framework for building APIs with automatic documentation generation.

**Hartree**: Atomic unit of energy (1 Ha = 2625.5 kJ/mol).

**HF (Hartree-Fock)**: Fundamental quantum chemistry method providing a mean-field approximation.

**JSON (JavaScript Object Notation)**: Lightweight data interchange format.

**Microservice**: Architectural approach structuring applications as loosely coupled, independently deployable services.

**MP2 (Møller-Plesset 2nd order)**: Post-Hartree-Fock method including electron correlation effects.

**PySCF**: Python-based quantum chemistry package for electronic structure calculations.

**PySide6**: Python bindings for Qt6 framework, enabling native GUI development.

**REST (Representational State Transfer)**: Architectural style for designing networked applications using HTTP methods.

**SCF (Self-Consistent Field)**: Iterative method for solving quantum mechanical equations.

**Sprint**: Time-boxed iteration in Agile development, typically 1-4 weeks.

**Story Points**: Relative estimation unit for measuring development effort in Agile methodologies.

**UUID (Universally Unique Identifier)**: 128-bit identifier used for uniquely identifying information.

**XYZ Format**: Simple molecular geometry file format specifying atomic coordinates.

---

**📚 Course**: Computational Chemistry  
**📅 Module**: Week 3 - GUI & Microservice Architecture  
**👨‍🏫 Instructor**: Viwat Vchirawongkwin  
**🏫 Institution**: Chulalongkorn University  
**⏱️ Estimated Reading Time**: 11 minutes
