# Minimal Example: Small-scale Supply Chain Optimization

## 1. Problem Description
A logistics center needs to distribute vaccines to 3 regional hospitals ($H_1, H_2, H_3$) under cold-chain constraints:
- Hospital demands: $D = [120, 80, 150]$ (vials)
- Transport cost per vial: $C = [2.5, 4.0, 3.2]$ (CNY/km)
- Available capacity: 400 vials total.
- Objective: Minimize total transport cost while strictly meeting demands and cold-chain shelf-life limits.

## 2. Invoked Skills Workflow
1. `$problem-analyzer`: Extract variables ($x_i$), objective function ($\min \sum C_i D_i$), and boundary conditions ($x_i \ge D_i$).
2. `$model-selection`: Formulate as a Mixed-Integer Linear Program (MILP), select Linear baseline + Simplex solver.
3. `$mle-solver`: Execute numerical solver with SciPy `scipy.optimize.linprog`.
4. `$model-validation`: Perform sensitivity check on transport cost variation $\pm 10\%$.
5. `$mcm-paper-writing`: Generate standardized Markdown report.
