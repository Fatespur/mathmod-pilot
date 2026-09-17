# DYNAMIC_STATE_SPACE_INVERSE solver contract v2

Encode transition/differential equations, observation operator, noise model, units, initial/boundary conditions and the declared purpose. Solver hierarchy: analytical/limiting case → deterministic integration/filtering and exact linear-Gaussian recursions → constrained likelihood/adjoint/sensitivity estimation → particle/ensemble/Bayesian approximations when nonlinear/non-Gaussian evidence requires them.

Emit convergence and discretization checks, synthetic recovery, multistart/profile or rank diagnostics, observability/identifiability evidence appropriate to purpose, residual innovations, uncertainty, baseline, and exact seeds. S3 must report non-unique parameter sets; it cannot relabel convergence as identifiability.

