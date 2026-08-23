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
mf.grids.level = 5
mf.conv_tol = 1e-10
energy = mf.kernel()

print(f"B3LYP Energy = {energy:.10f} Hartree")
with open("results/water_b3lyp.txt", "w") as f:
    f.write(f"{energy:.12f}\n")
