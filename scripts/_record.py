"""Write one results/<name>.json per calculation: the number, the geometry, and
enough of the environment to tell whether two runs are comparable.

Imported as `from _record import record` — scripts are run as
`python scripts/x.py`, so sys.path[0] is the scripts/ directory, and scripts/
is bind-mounted, so adding this file needs no image rebuild.
"""
import json
import os
import sys
from pathlib import Path

import numpy
import pyscf
import scipy


def record(name, energy, mol, **extra):
    """Persist a calculation record to results/<name>.json.

    extra is for whatever the method actually has: method, conv_tol,
    grid_level, optimizer, ... Pass grid_level only for DFT — scf.RHF and
    mp.MP2 objects have no .grids attribute.
    """
    Path("results").mkdir(exist_ok=True)
    data = {
        "energy_hartree": float(energy),
        # atom_coords() is Bohr by default; ask for Angstrom explicitly.
        "geometry_angstrom": [
            [mol.atom_symbol(i), *(float(c) for c in xyz)]
            for i, xyz in enumerate(mol.atom_coords(unit="Angstrom"))
        ],
        "basis": mol.basis,
        "omp_num_threads": os.environ.get("OMP_NUM_THREADS"),
        "versions": {
            "pyscf": pyscf.__version__,
            "numpy": numpy.__version__,
            "scipy": scipy.__version__,
            "python": sys.version.split()[0],
        },
        **extra,
    }
    out = Path(f"results/{name}.json")
    out.write_text(json.dumps(data, indent=2) + "\n")
    print(f"Wrote {out}")
    return out
