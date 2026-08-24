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
mf = dft.RKS(mol).density_fit()
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
