# NETWORK_ROUTING solver contract v2

Implement only the selected subtype. Encode node/arc indexing, direction, objective, conservation, capacity, depot, visit, time-window and subtour constraints explicitly. Solver hierarchy: graph exact algorithm → LP/MILP/DP/CP-SAT → decomposition/cut generation → approximation with bound → validated heuristic/metaheuristic after documented scale evidence.

Required evidence: feasibility assertion per constraint family; connectivity and duplicate-visit audit; objective recomputation; exact certificate or lower bound/gap where feasible; runtime/scale trace; deterministic seeds for approximate solvers; baseline on identical data and constraints. Unsupported escalation or a subtype mismatch returns to selection.

