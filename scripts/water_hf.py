from pyscf import gto, scf
from _record import record
from pathlib import Path

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
Path("results").mkdir(exist_ok=True)
with open("results/water_hf.txt", "w") as f:
    f.write(f"{energy:.12f}\n")
record("water_hf", energy, mol, method="RHF", conv_tol=mf.conv_tol)
