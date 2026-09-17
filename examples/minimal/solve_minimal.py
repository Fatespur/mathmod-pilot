import numpy as np
from scipy.optimize import linprog

# Costs and demands
c = np.array([2.5, 4.0, 3.2])
demands = np.array([120, 80, 150])

# Problem: min c^T x s.t. x >= demands, sum(x) <= 400
# Transform to -x <= -demands
A_ub = np.vstack([-np.eye(3), np.ones((1, 3))])
b_ub = np.hstack([-demands, 400])

res = linprog(c, A_ub=A_ub, b_ub=b_ub, bounds=(0, None), method='highs')
print(f"Status: {res.message}")
print(f"Optimal Allocation: {res.x}")
print(f"Minimum Total Cost: {res.fun:.2f} CNY")
