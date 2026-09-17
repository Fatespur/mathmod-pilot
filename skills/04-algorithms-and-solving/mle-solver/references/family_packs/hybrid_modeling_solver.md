# HYBRID_MODELING solver contract v2

Implement each component and interface as separate, hashable artifacts. Prevent train/test and future-information leakage across interfaces. Propagate distributions/scenarios when downstream decisions depend on uncertainty; a point estimate needs a justified loss-equivalence argument. Solver hierarchy is component-wise exact-first, then interface-level joint/alternating optimization only when necessary.

Execute the best single-component baseline, full system, leave-one-component-out ablations, interface stress tests and seed/split stability. Log error and uncertainty propagation and recompute downstream decision loss. A component failure cannot be hidden by an end-to-end metric, and S3 cannot certify the hybrid.

