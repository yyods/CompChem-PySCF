# PySCF Setup Guide for Apple Silicon Macs

A simple step-by-step guide to install and test PySCF on M1/M2/M3 Macs.

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

Set up an isolated environment for PySCF in the current directory:

```bash
# Create and activate virtual environment in current directory
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip and tools
python -m pip install --upgrade pip wheel setuptools
```

## Step 3: Install PySCF

Install PySCF and dependencies (install individually to ensure success):

```bash
# Install packages one by one for reliability
python -m pip install "numpy==1.26.4"
python -m pip install "scipy==1.13.1" 
python -m pip install "pyscf==2.4.0"
python -m pip install "geometric==1.0.0"
```

## Step 4: Test Installation

Verify everything works (use full Python path):

```bash
/Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python -c "
import sys, platform, numpy, pyscf
print('Python:', sys.version.split()[0])
print('Architecture:', platform.machine())
print('NumPy:', numpy.__version__)
print('PySCF:', pyscf.__version__)
print('✅ Installation successful!')
"
```

**Note**: After configuring the environment, use the full Python path for all commands:
`/Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python` instead of just `python`

## Step 5: Run Test Calculations

Create directories for your scripts and results:

```bash
mkdir -p scripts results
```

### Test 1: Water Molecule - RHF Calculation

```bash
cat > scripts/water_hf.py << 'EOF'
from pyscf import gto, scf

# Define water molecule
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)

# Run Hartree-Fock calculation
mf = scf.RHF(mol)
mf.conv_tol = 1e-9
energy = mf.kernel()

print(f"RHF Energy = {energy:.10f} Hartree")
with open("results/water_hf.txt", "w") as f:
    f.write(f"{energy:.12f}\n")
EOF

# Run the calculation
OMP_NUM_THREADS=1 /Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python scripts/water_hf.py
cat results/water_hf.txt
```

**Expected result**: `-75.960975166983` (around -76 Hartree)

### Test 2: Water Molecule - DFT Calculation

```bash
cat > scripts/water_dft.py << 'EOF'
from pyscf import gto, dft

# Define water molecule
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)

# Run B3LYP DFT calculation
mf = dft.RKS(mol)
mf.xc = 'B3LYP'
mf.grids.level = 3
mf.conv_tol = 1e-9
energy = mf.kernel()

print(f"B3LYP Energy = {energy:.10f} Hartree")
with open("results/water_b3lyp.txt", "w") as f:
    f.write(f"{energy:.12f}\n")
EOF

# Run the calculation
OMP_NUM_THREADS=1 /Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python scripts/water_dft.py
cat results/water_b3lyp.txt
```

**Expected result**: `-76.358149490137` (similar to RHF, slightly different due to correlation)

### Test 3: Water Molecule - MP2 Calculation

```bash
cat > scripts/water_mp2.py << 'EOF'
from pyscf import gto, scf, mp

# Define water molecule
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)

# Run RHF first, then MP2
mf = scf.RHF(mol).run(conv_tol=1e-9)
mp2 = mp.MP2(mf).run()

print(f"RHF Energy = {mf.e_tot:.10f} Hartree")
print(f"MP2 Energy = {mp2.e_tot:.10f} Hartree")
with open("results/water_mp2.txt", "w") as f:
    f.write(f"{mp2.e_tot:.12f}\n")
EOF

# Run the calculation
OMP_NUM_THREADS=1 /Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python scripts/water_mp2.py
cat results/water_mp2.txt
```

**Expected result**: `-76.164590031811` (lower than RHF due to electron correlation)

## Step 6: Geometry Optimization

Optimize the water molecule geometry:

```bash
cat > scripts/water_optimize.py << 'EOF'
from pyscf import gto, dft
from pyscf.geomopt.geometric_solver import optimize
from pathlib import Path

# Define water molecule (starting geometry)
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)

# Set up B3LYP calculation
mf = dft.RKS(mol)
mf.xc = 'B3LYP'
mf.grids.level = 3
mf.conv_tol = 1e-9

# Optimize geometry
mol_opt = optimize(mf, maxsteps=100)

# Save optimized geometry
xyz_file = Path("results/water_opt.xyz")
with xyz_file.open("w") as f:
    f.write(f"{mol_opt.natm}\nOptimized H2O (B3LYP/def2-SVP)\n")
    for i, (x, y, z) in enumerate(mol_opt.atom_coords()):
        symbol = mol_opt.atom_symbol(i)
        f.write(f"{symbol:2s} {x:.8f} {y:.8f} {z:.8f}\n")

print(f"Optimized geometry saved to {xyz_file}")
EOF

# Run optimization
OMP_NUM_THREADS=1 /Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python scripts/water_optimize.py
cat results/water_opt.xyz
```

**Expected result**: Optimized geometry showing slight changes from starting structure

## Step 7: CO₂ Test Calculation

Test with a linear molecule (CO₂):

```bash
cat > scripts/co2_test.py << 'EOF'
from pyscf import gto, dft

# Define CO2 molecule (linear)
mol = gto.M(atom="C 0 0 0; O 0 0 1.160; O 0 0 -1.160",
            basis="def2-svp", unit="Angstrom", verbose=4)

# Run B3LYP calculation
mf = dft.RKS(mol)
mf.xc = "B3LYP"
mf.grids.level = 3
mf.conv_tol = 1e-9
energy = mf.kernel()

print(f"CO₂ B3LYP Energy = {energy:.10f} Hartree")
with open("results/co2_b3lyp.txt", "w") as f:
    f.write(f"{energy:.12f}\n")
EOF

# Run calculation
OMP_NUM_THREADS=1 /Users/vyv/Documents/Teaching/CompChem/2025/Week_2/.venv/bin/python scripts/co2_test.py
cat results/co2_b3lyp.txt
```

**Expected result**: `-188.442995139098` (much more negative due to more electrons)

## Expected Results

- **RHF Energy**: -75.96 Hartree (around -76 Hartree, negative value)
- **B3LYP Energy**: -76.36 Hartree (similar to RHF, slightly different due to correlation)
- **MP2 Energy**: -76.16 Hartree (lower than RHF, more negative due to electron correlation)
- **CO₂ Energy**: -188.44 Hartree (much more negative due to more electrons)

## Troubleshooting

If pip installation fails, try using conda instead:

```bash
# Install miniforge: https://github.com/conda-forge/miniforge
conda create -n pyscf-311 -c conda-forge python=3.11 pyscf=2.4 numpy=1.26 scipy=1.13 geometric=1.0
conda activate pyscf-311
```

## Clean Up

When finished:

```bash
deactivate  # Exit virtual environment
```

## Summary

You have successfully:

- ✅ Installed PySCF on Apple Silicon
- ✅ Run RHF, DFT, and MP2 calculations
- ✅ Performed geometry optimization
- ✅ Saved all results for reference

Your PySCF installation is ready for computational chemistry work!
