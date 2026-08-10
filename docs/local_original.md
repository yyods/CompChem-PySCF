# Local PySCF Setup on Apple Silicon (M1/M2/M3)

> **Kept for reference; superseded by [local_MacOS.md](./local_MacOS.md).**
>
> This is a standalone walkthrough that builds its own sandbox in
> `~/chem/pyscf-test` and writes its own copies of the scripts. Run it from your
> home directory, **not** from inside a clone of this repository — its
> `cat > scripts/...` blocks would overwrite the tracked scripts.
>
> To work in the repository itself, follow `local_MacOS.md`, which runs the
> scripts that are already here.

# A. One-time checks (Apple Silicon + tooling)

```bash
# Confirm Apple Silicon (arm64)
uname -m
# -> arm64

# Optional but helpful if you’ve never installed it:
xcode-select --install   # Command Line Tools (ok to skip if already installed)
```

# B. Make an isolated Python env and install PySCF

I’ll pin versions known to work smoothly on macOS arm64 and force wheels (no compiling).

```bash
# Create a workspace
mkdir -p ~/chem/pyscf-test && cd ~/chem/pyscf-test

# Create & activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Upgrade packaging tools
python -m pip install --upgrade pip wheel setuptools

# Install pinned scientific stack + PySCF + geometry optimizer
# --only-binary=:all: avoids source builds on macOS
python -m pip install --only-binary=:all: \
  "numpy==1.26.4" "scipy==1.13.1" "pyscf==2.4.0" "geometric==1.0.0"
```

Quick sanity check:

```bash
python - <<'PY'
import sys, platform, numpy, pyscf
print("Python:", sys.version.split()[0])
print("Arch:", platform.machine())
print("NumPy:", numpy.__version__)
print("PySCF:", pyscf.__version__)
PY
```

> If the last command prints versions without errors, you’re good.

# C. Run three tiny calculations (HF, DFT, MP2)

Create a scripts folder and add test files:

```bash
mkdir -p scripts results
```

## 1) Single-point RHF on water

```bash
cat > scripts/water_hf.py <<'PY'
from pyscf import gto, scf
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)
mf = scf.RHF(mol)
mf.conv_tol = 1e-9
e = mf.kernel()
print(f"E(RHF/def2-SVP) = {e:.10f} Hartree")
open("results/water_hf.txt","w").write(f"{e:.12f}\n")
PY

# Run (set threads=1 for reproducibility)
OMP_NUM_THREADS=1 python scripts/water_hf.py
cat results/water_hf.txt
```

**What to expect:** a negative energy around −76 Hartree (exact value depends on basis and grid; the sign/magnitude is the sanity check).

## 2) Single-point B3LYP on water

```bash
cat > scripts/water_dft.py <<'PY'
from pyscf import gto, dft
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)
mf = dft.RKS(mol)
mf.xc = 'B3LYP'
mf.grids.level = 3
mf.conv_tol = 1e-9
e = mf.kernel()
print(f"E(RKS-B3LYP/def2-SVP) = {e:.10f} Hartree")
open("results/water_b3lyp.txt","w").write(f"{e:.12f}\n")
PY

OMP_NUM_THREADS=1 python scripts/water_dft.py
cat results/water_b3lyp.txt
```

**Expect:** similar ballpark to HF, often slightly different (DFT includes correlation implicitly).

## 3) Single-point MP2 on water

```bash
cat > scripts/water_mp2.py <<'PY'
from pyscf import gto, scf, mp
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)
mf = scf.RHF(mol).run(conv_tol=1e-9)
mp2 = mp.MP2(mf).run()
e_scf = mf.e_tot
e_mp2 = mp2.e_tot
print(f"E(RHF) = {e_scf:.10f} Hartree")
print(f"E(MP2) = {e_mp2:.10f} Hartree")
open("results/water_mp2.txt","w").write(f"{e_mp2:.12f}\n")
PY

OMP_NUM_THREADS=1 python scripts/water_mp2.py
cat results/water_mp2.txt
```

**Expect:** MP2 energy lower than RHF (correlation lowers the energy).

# D. Quick geometry optimization inside macOS (no Docker yet)

```bash
cat > scripts/water_opt_b3lyp.py <<'PY'
from pyscf import gto, dft
from pyscf.geomopt.geometric_solver import optimize
from pathlib import Path
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)
mf = dft.RKS(mol)
mf.xc = 'B3LYP'
mf.grids.level = 3
mf.conv_tol = 1e-9
mol_opt = optimize(mf, maxsteps=100)
# Save optimized geometry (XYZ)
xyz = Path("results/water_opt.xyz")
with xyz.open("w") as f:
  f.write(f"{mol_opt.natm}\nB3LYP/def2-SVP optimized H2O\n")
  for i, (x,y,z) in enumerate(mol_opt.atom_coords()):
    f.write(f"{mol_opt.atom_symbol(i):2s} {x:.8f} {y:.8f} {z:.8f}\n")
print("Wrote", xyz)
PY

OMP_NUM_THREADS=1 python scripts/water_opt_b3lyp.py
open results/water_opt.xyz
```

# E. One more: CO₂ single-point (for your later assignment)

```bash
cat > scripts/co2_sp_b3lyp.py <<'PY'
from pyscf import gto, dft
mol = gto.M(atom="C 0 0 0; O 0 0 1.160; O 0 0 -1.160",
            basis="def2-svp", unit="Angstrom", verbose=4)
mf = dft.RKS(mol)
mf.xc = "B3LYP"
mf.grids.level = 3
mf.conv_tol = 1e-9
e = mf.kernel()
print(f"E_total (B3LYP/def2-SVP, CO2) = {e:.10f} Hartree")
open("results/co2_b3lyp_sp.txt","w").write(f"{e:.12f}\n")
PY

OMP_NUM_THREADS=1 python scripts/co2_sp_b3lyp.py
cat results/co2_b3lyp_sp.txt
```

# F. If `pip install pyscf` fails on your Mac

Very occasionally a wheel mismatch causes trouble. The quickest fallback on Apple Silicon is conda-forge:

```bash
# Install miniforge if you don't have it: https://github.com/conda-forge/miniforge
conda create -n pyscf-311 -c conda-forge python=3.11 pyscf=2.4 numpy=1.26 scipy=1.13 geometric=1.0
conda activate pyscf-311
# Then run the same scripts as above
```

# G. Clean up

```bash
# Deactivate venv when done
deactivate
```

---

## What you’ve now validated

- PySCF imports and runs cleanly on your M-series Mac.
- You can compute RHF, B3LYP, and MP2 single-points and a small geometry optimization.
- You have reproducible runs (`OMP_NUM_THREADS=1`) and saved outputs under `results/`.
