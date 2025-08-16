from pyscf import gto, dft
from pathlib import Path
import json, platform, sys

# Geometry (Å)
mol = gto.M(
    atom = """
      O  0.0000  0.0000  0.0000
      H  0.0000 -0.7570  0.5870
      H  0.0000  0.7570  0.5870
    """,
    basis = "6-31g(d)",   # alias of 6-31G*; both work in PySCF
    unit  = "Angstrom",
    verbose = 4
)

mf = dft.RKS(mol)
mf.xc = "B3LYP"
mf.grids.level = 3      # sensible default grid
mf.conv_tol = 1e-9      # tight SCF
mf.max_cycle = 100

E = mf.kernel()

# Persist results
Path("results").mkdir(exist_ok=True)
txt = Path("results/water_b3lyp_631gd.txt")
txt.write_text(f"{E:.12f}\n")

meta = {
  "method": "B3LYP",
  "basis": "6-31G(d)",
  "grid_level": 3,
  "scf_conv_tol": 1e-9,
  "energy_hartree": E,
  "python": sys.version.split()[0],
  "platform": platform.platform(),
}
json_path = Path("results/water_b3lyp_631gd.json")
json_path.write_text(json.dumps(meta, indent=2))

print(f"E(RKS-B3LYP/6-31G(d)) = {E:.10f} Ha")
print(f"Wrote {txt} and {json_path}")
