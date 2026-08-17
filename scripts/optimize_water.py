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
Path("results").mkdir(exist_ok=True)
xyz_file = Path("results/water_opt.xyz")
with xyz_file.open("w") as f:
    f.write(f"{mol_opt.natm}\nOptimized H2O (B3LYP/def2-SVP), coordinates in Angstrom\n")
    # atom_coords() returns BOHR by default; .xyz is Angstrom by convention.
    for i, (x, y, z) in enumerate(mol_opt.atom_coords(unit='Angstrom')):
        symbol = mol_opt.atom_symbol(i)
        f.write(f"{symbol:2s} {x:.8f} {y:.8f} {z:.8f}\n")

print(f"Optimized geometry saved to {xyz_file}")
