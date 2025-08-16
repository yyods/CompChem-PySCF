from pyscf import gto, dft
mol = gto.M(
    atom = "C 0 0 0; O 0 0 1.160; O 0 0 -1.160",  # ~eq. CO2 bond in Å
    unit = "Angstrom",
    basis = "def2-svp",
    charge = 0, spin = 0, verbose = 4,
)
mf = dft.RKS(mol).set(xc="B3LYP")
mf.grids.level = 3
mf.conv_tol = 1e-9
E = mf.kernel()
print(f"E_total (B3LYP/def2-SVP) = {E:.10f} Hartree")
with open("results/co2_energy.txt","w") as f: f.write(f"{E:.12f}\n")
