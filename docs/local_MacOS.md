# PySCF Setup Guide for Apple Silicon Macs

A step-by-step guide to install and test PySCF on M1/M2/M3 Macs.

> **Week 2 needs none of this.** Week 2 is Git and reproducibility — you fork,
> branch, commit, open a pull request and tag, without running a calculation.
> Set this up before Week 3, or use the container instead
> (`docker compose run --rm pyscf scripts/water_hf.py`).

## Step 1: Verify Your System

First, confirm you have an Apple Silicon Mac:

```bash
uname -m
```

You should see `arm64`. If needed, install Command Line Tools:

```bash
xcode-select --install
```

## Step 2: Create Python Environment

Clone the repository and set up an isolated environment inside it:

```bash
git clone https://github.com/yyods/CompChem-PySCF.git
cd CompChem-PySCF

# Create and activate a virtual environment in the current directory
python3 -m venv .venv
source .venv/bin/activate

# Upgrade packaging tools
python -m pip install --upgrade pip wheel setuptools
```

`.venv/` is gitignored, so it never ends up in a commit.

## Step 3: Install PySCF

Install PySCF and dependencies, pinned to the same versions as the container:

```bash
python -m pip install "numpy==1.26.4"
python -m pip install "scipy==1.13.1"
python -m pip install "pyscf==2.4.0"
python -m pip install "geometric==1.0.0"
```

## Step 4: Test Installation

```bash
python -c "
import sys, platform, numpy, pyscf
print('Python:', sys.version.split()[0])
print('Architecture:', platform.machine())
print('NumPy:', numpy.__version__)
print('PySCF:', pyscf.__version__)
print('✅ Installation successful!')
"
```

**Note**: Keep the virtual environment activated for every command below — you
should see `(.venv)` at the start of your prompt. `deactivate` leaves it.

## Step 5: Run the Calculations

The scripts are already in the repository — run them, do not retype them. Each
one creates `results/` on first write, and `results/` is gitignored.

`OMP_NUM_THREADS=1` pins BLAS to a single thread so a rerun reproduces the same
digits.

### Test 1: Water — RHF

```bash
OMP_NUM_THREADS=1 python scripts/water_hf.py
cat results/water_hf.txt
```

**Expected**: `-75.960975166983` (around -76 Hartree)

### Test 2: Water — B3LYP

```bash
OMP_NUM_THREADS=1 python scripts/water_dft.py
cat results/water_b3lyp.txt
```

**Expected**: `-76.358149490137`

### Test 3: Water — MP2

```bash
OMP_NUM_THREADS=1 python scripts/water_mp2.py
cat results/water_mp2.txt
```

**Expected**: `-76.164590031811`

> These three totals sort as B3LYP < MP2 < HF. That is **not** an accuracy
> ranking — total energies from different methods are not comparable to each
> other. See the Method Comparison table in the README.

### Test 4: Water — geometry optimisation

```bash
OMP_NUM_THREADS=1 python scripts/optimize_water.py
cat results/water_opt.xyz
```

**Expected**: an optimised geometry, slightly changed from the starting
structure.

### Test 5: CO₂ — B3LYP

```bash
OMP_NUM_THREADS=1 python scripts/co2_test.py
cat results/co2_b3lyp.txt
```

**Expected**: `-188.442995139098` (more negative — more electrons)

### Test 6: Water — B3LYP/6-31G(d) with metadata

```bash
OMP_NUM_THREADS=1 python scripts/water_B3LYP_631Gd.py
cat results/water_b3lyp_631gd.json
```

Writes both a `.txt` energy and a `.json` record of method, basis, grid,
convergence and platform — the shape of output Week 5 will plot.

## Troubleshooting

If a pip installation fails, conda-forge has arm64 builds:

```bash
# Install miniforge: https://github.com/conda-forge/miniforge
conda create -n pyscf-311 -c conda-forge python=3.11 pyscf=2.4 numpy=1.26 scipy=1.13 geometric=1.0
conda activate pyscf-311
```

If a script reports `FileNotFoundError` for `results/`, you are running an old
checkout — pull the latest `main`, where every script creates the directory
before writing.

## Clean Up

```bash
deactivate  # Exit virtual environment
```

## Summary

You have:

- ✅ Installed PySCF on Apple Silicon
- ✅ Run RHF, B3LYP and MP2 calculations
- ✅ Performed a geometry optimisation
- ✅ Written results to `results/`, which stays out of version control
