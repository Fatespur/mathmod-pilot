# NETWORK_ROUTING selection contract v2

Eligible structure: explicit nodes/edges plus path, flow, matching, tour, fleet, depot, demand, capacity, time-window, commodity, or network-design decisions. Extract direction, weights, conservation, subtour risk and dynamics before naming a subtype.

- Shortest path: only one/few source-destination paths, additive nonnegative edge cost, and no fleet, depot, visit-all, demand, capacity, time-window, or subtour structure.
- Min-cost flow: supplies/demands, arc capacities and flow conservation; distinguish single/multi-commodity.
- TSP/VRP: visit/tour decisions; capacity/depot/demand implies CVRP/VRP rather than shortest path. Small instances require exact/MILP/DP feasibility screening before heuristics.
- Baselines: feasible greedy route; shortest-path relaxation only when it is a valid lower-level relaxation; LP/flow relaxation or assignment/lower bound.
- Reject: coordinates alone; keyword-only “route”; missing graph/operational constraints; Dijkstra selected despite routing constraints.
- Alternatives: generic optimization, simulation for congestion/dynamics, robust/stochastic optimization for uncertain operations.
- Failure modes: disconnected graph, violated conservation/capacity/time windows, subtours, invalid distance metric, weak bound, scale/runtime collapse.
- Replacement triggers: newly discovered vehicle/visit constraints change subtype; exact route proves infeasible; stochastic congestion dominates static cost; no material gain over simpler feasible baseline.

