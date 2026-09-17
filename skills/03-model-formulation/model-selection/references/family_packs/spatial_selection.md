# SPATIAL selection contract v2

Eligible structure: georeferenced units/processes where distance, adjacency, support, spatial field, spillover, interpolation, or region-level deployment can affect the estimand or errors. Coordinates alone are insufficient. Require CRS/projection, spatial unit/support, scale, neighborhood/distance definition, sampling design, target region and residual-dependence evidence.

- Baseline: corresponding non-spatial model plus residual spatial-autocorrelation diagnostic.
- Candidates: spatial error/lag/regression, CAR/SAR/GWR only with defensible semantics, Gaussian process/kriging for fields, spatial point/process or spatial optimization as structure demands.
- Reject/downgrade: no residual dependence and no spatial target after baseline; invalid projection; arbitrary weights matrix; random split that leaks neighboring units.
- Alternatives: non-spatial statistical/ML, network, spatiotemporal/dynamic family.
- Failure modes: CRS distortion, MAUP/support mismatch, boundary leakage, nonstationarity, extrapolation outside sampled support, invalid covariance/weights.
- Replacement triggers: spatial effect disappears after covariates; deployment geography changes; projection/support invalid; block-CV shows no material benefit.

