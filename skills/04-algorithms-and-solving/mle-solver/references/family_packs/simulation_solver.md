# SIMULATION_QUEUE_DES_ABM solver contract v2

Implement a transparent event/rule specification with clocks, state transitions, resource discipline, termination, warm-up rule and output estimands. Solver hierarchy: analytical queue/approximation → empirical replay → DES/Monte Carlo → ABM only when agent heterogeneity/rules are necessary. Never use one stochastic run as evidence.

Required: independent reproducible seed stream; preregistered replication/precision rule; warm-up diagnostic; event invariant assertions; input-distribution fitting/traceability; convergence of mean and tail metrics; scenario and extreme tests; baseline; ABM rule calibration and component ablations. Missing seeds, replications or warm-up blocks handoff.

