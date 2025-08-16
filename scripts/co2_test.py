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
