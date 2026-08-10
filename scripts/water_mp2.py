from pyscf import gto, scf, mp
from pathlib import Path

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
Path("results").mkdir(exist_ok=True)
with open("results/water_mp2.txt", "w") as f:
    f.write(f"{mp2.e_tot:.12f}\n")
