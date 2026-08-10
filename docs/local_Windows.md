# PySCF on Windows

**Short version: there is no native Windows build of PySCF.** Run it under WSL2
or in the container. Both routes are below.

## Week 2 needs none of this

Week 2 is Git and reproducibility. You fork this repository, branch, commit,
open a pull request and tag — no calculation is run, so **you do not need PySCF
installed to complete Week 2**. Set up one of the routes below before Week 3.

## Why not just `pip install pyscf`?

PySCF publishes wheels for Linux (`manylinux`) and macOS only. There is no
`win_amd64` wheel for **any** version — not 2.4.0, not the current release. On
Windows, `pip install pyscf` therefore falls back to the source tarball and
tries to build it, which fails within seconds:

```
CMake Error: CMAKE_C_COMPILER not set
```

Downgrading to Python 3.10 does not help, and neither does conda: conda-forge
builds PySCF for `linux-64`, `linux-aarch64`, `linux-ppc64le`, `osx-64` and
`osx-arm64` — there is no `win-64` package. If you have seen a guide claiming
otherwise, it is wrong.

## Route A — WSL2 (recommended if you want a local Python)

WSL2 gives you a real Linux userspace, so the ordinary Linux wheels install.

```powershell
# In an elevated PowerShell, once:
wsl --install -d Ubuntu
```

Reboot if prompted, then open the **Ubuntu** terminal and continue there:

```bash
sudo apt update && sudo apt install -y python3-venv
git clone https://github.com/yyods/CompChem-PySCF.git
cd CompChem-PySCF

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip wheel setuptools
python -m pip install "numpy==1.26.4" "scipy==1.13.1" "pyscf==2.4.0" "geometric==1.0.0"
```

Verify:

```bash
python -c "import numpy, pyscf; print('NumPy', numpy.__version__, '| PySCF', pyscf.__version__)"
```

Then run any script in the repository:

```bash
OMP_NUM_THREADS=1 python scripts/water_hf.py
cat results/water_hf.txt
```

Keep the repository inside the Linux filesystem (`~/CompChem-PySCF`) rather than
under `/mnt/c/...` — file access across the Windows boundary is slow.

## Route B — Docker Desktop (what Week 3 uses)

No Python setup at all; the pinned environment lives in the image.

```powershell
docker compose build pyscf
docker compose run --rm pyscf scripts/water_hf.py
Get-Content results\water_hf.txt
```

Docker Desktop needs the WSL2 backend, so Route A's `wsl --install` is worth
doing either way.

## Reference energies

Produced by the container; use them to check your own setup. Small differences
in the last digits across BLAS libraries and thread counts are expected —
that is a Week 3 discussion.

| Script                  | Method            | Energy / Hartree |
| ----------------------- | ----------------- | ---------------- |
| `water_hf.py`           | RHF/def2-SVP      | -75.960975166983 |
| `water_dft.py`          | B3LYP/def2-SVP    | -76.358149490137 |
| `water_mp2.py`          | MP2/def2-SVP      | -76.164590031811 |
| `co2_test.py`           | B3LYP/def2-SVP    | -188.442995139098 |

Set `OMP_NUM_THREADS=1` for run-to-run determinism (`$env:OMP_NUM_THREADS=1` in
PowerShell). The container sets it already.

## Windows-specific notes

**PowerShell execution policy** — if activating a virtual environment is
blocked:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**VS Code** — install the Python and WSL extensions, then `Ctrl+Shift+P` →
"WSL: Connect to WSL" and open the repository from inside Ubuntu. Selecting a
Windows interpreter will not find PySCF, because it cannot be installed there.

**Line endings** — Git for Windows checks files out with CRLF by default. That
is fine for Python, but if a script ever fails with a stray `\r`, run
`git config --global core.autocrlf input` inside WSL.

## Summary

- There is no native Windows PySCF; do not try to `pip install` it.
- Week 2 needs no PySCF at all.
- For Week 3, use WSL2 (Route A) or Docker Desktop (Route B).
