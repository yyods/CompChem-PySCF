from pyscf import gto, scf

# Define water molecule
mol = gto.M(atom='''
O  0.0000  0.0000  0.0000
H  0.0000 -0.7570  0.5870
H  0.0000  0.7570  0.5870
''', basis='def2-svp', unit='Angstrom', verbose=4)

# Run Hartree-Fock calculation
mf = scf.RHF(mol)
mf = scf.RHF(mol).density_fit()
mf.conv_tol = 1e-9
energy = mf.kernel()

print(f"RHF Energy = {energy:.10f} Hartree")
with open("results/water_hf.txt", "w") as f:
    f.write(f"{energy:.12f}\n")
