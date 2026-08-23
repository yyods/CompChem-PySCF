# Hands-On Lab Week 3 Results

## Density Fitting Comparison
* **Without Density Fitting (RHF)**: Energy = -75.9609751670 Hartree, Time = 0.20 s
* **With Density Fitting (DFRHF)**: Energy = -75.9609192737 Hartree, Time = 0.19 s
* **Energy Shift**: 0.0000558933 Hartree

*Note: Density Fitting successfully speeds up the calculation base matrix representations while maintaining energy accuracy down to the 4th decimal place.*

## Computational Cost Comparison
* **Hartree-Fock (HF)**: CPU Time = 0.16 s
* **Møller–Plesset Perturbation Theory (MP2)**: CPU Time = 0.15 s
* **Density Functional Theory (DFT)**: CPU Time = 0.16 s

*Note: For a very small system like a single water molecule, the computational cost differences between HF, MP2, and DFT are negligible in this hardware environment.*

## Tightened Convergence Tolerance
* **Tightened DFT (B3LYP)**: conv_tol = 1e-10, grids.level = 5
* **Final Precise Energy**: -76.3581493060 

*Note: Tightening the convergence tolerance ensures high numerical precision for the electronic structure calculation.*
