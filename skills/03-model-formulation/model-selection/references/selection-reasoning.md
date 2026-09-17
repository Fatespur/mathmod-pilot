# Structure-first selection reasoning

## Forecasting

Extract horizon, trend, seasonality, breaks, covariates and their future availability, frequency, autocorrelation, stationarity/regimes, missingness, effective sample, and uncertainty. Sample size constrains parameter/complexity budgets and validation uncertainty; it never selects a family. Always include naive/seasonal-naive/drift or simple regression as applicable.

## Evaluation

First distinguish construct measurement, subjective preference, ranking, efficiency, distance-to-ideal, dimension reduction, and multi-criteria choice. Correlated objective indicators raise latent-structure candidates; genuine preferences raise value/outranking candidates; efficiency requires input/output semantics. Entropy weighting, TOPSIS, AHP, PCA/factor, DEA, simple scores, and rank aggregation are examples whose prerequisites must be screened.

## Network/routing

Extract nodes, edges, direction, weights, capacities, demands, vehicles, depots, time windows, conservation, subtour risk, commodities, and dynamics. Only a graph without fleet/demand/capacity/time constraints can collapse to an ordinary shortest-path problem. Otherwise screen flow, matching, TSP/VRP variants, or network design.

## Queues/simulation

Test arrival/service distributions, independence, stationarity, server count, priority, balking/reneging, capacity, and time-varying rates. M/M/c is eligible only when its Poisson/exponential/stationary assumptions are supported. Otherwise screen analytical approximations, empirical replay, or simulation; disclose `COVERAGE_LIMITED` for DES/ABM depth.

## Multi-objective

Check size, linearity, convexity, integrality, objective count, exact solvability, enumeration and epsilon-constraint feasibility, and scalarization limitations. Prefer exact anchors/epsilon-constraint/Pareto enumeration for tractable discrete problems. Evolutionary methods require explicit evidence that exact/deterministic routes are infeasible or inadequate.

## Solver hierarchy

Use the first adequate class: analytical → convex/exact → LP/MILP/DP/graph exact → decomposition → deterministic numerical → approximation/surrogate → metaheuristic. A method lower in the hierarchy needs a written rejection of every applicable earlier class.

General principle: structural facts are invariant to paraphrases and arbitrary sample thresholds. Counterexample: a sample-size change can legitimately change feasibility after an effective-sample/parameter calculation, but crossing a fixed integer boundary alone cannot change the family. Protect this with metamorphic tests.
