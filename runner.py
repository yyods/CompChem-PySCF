"""Run one PySCF single-point job.

This is the ONLY module that imports pyscf. Keeping the import here means the
service, the tests and the GUI can all be exercised without a quantum-chemistry
package installed — which matters, because PySCF has no native Windows build.
"""
from __future__ import annotations

import os
import platform
import sys
import time

SUPPORTED_METHODS = ("HF", "B3LYP", "MP2")


def versions() -> dict:
    """Package versions that could change a number. Imported lazily."""
    out = {"python": sys.version.split()[0], "platform": platform.platform()}
    for name in ("pyscf", "numpy", "scipy"):
        try:
            out[name] = __import__(name).__version__
        except Exception:
            out[name] = None
    return out


def run_job(spec: dict) -> dict:
    """Run the calculation described by spec and return a result record.

    spec keys: molecule, method, basis, grid, conv_tol, charge, spin.
    Raises ValueError for an unsupported method.
    """
    method = spec["method"].upper()
    if method not in SUPPORTED_METHODS:
        raise ValueError(f"unsupported method {method!r}; expected one of {SUPPORTED_METHODS}")

    from pyscf import gto, scf, dft, mp  # noqa: PLC0415 — deliberately lazy

    t0 = time.perf_counter()
    mol = gto.M(
        atom=spec["molecule"], basis=spec["basis"], unit="Angstrom",
        charge=spec.get("charge", 0), spin=spec.get("spin", 0), verbose=0,
    )
    t_build = time.perf_counter() - t0

    t1 = time.perf_counter()
    if method == "HF":
        mf = scf.RHF(mol)
        mf.conv_tol = spec["conv_tol"]
        energy = mf.kernel()
    elif method == "B3LYP":
        mf = dft.RKS(mol)
        mf.xc = "B3LYP"
        mf.grids.level = spec["grid"]
        mf.conv_tol = spec["conv_tol"]
        energy = mf.kernel()
    else:  # MP2
        mf = scf.RHF(mol).run(conv_tol=spec["conv_tol"])
        energy = mp.MP2(mf).run().e_tot
    t_scf = time.perf_counter() - t1

    return {
        "energy_hartree": float(energy),
        "method": method,
        "basis": spec["basis"],
        "grid": spec["grid"],
        "conv_tol": spec["conv_tol"],
        "charge": spec.get("charge", 0),
        "spin": spec.get("spin", 0),
        "timings_seconds": {"build": round(t_build, 4), "solve": round(t_scf, 4)},
        "versions": versions(),
        "environment": {"OMP_NUM_THREADS": os.environ.get("OMP_NUM_THREADS")},
    }
