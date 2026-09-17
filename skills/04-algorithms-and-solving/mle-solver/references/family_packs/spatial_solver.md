# SPATIAL solver contract v2

Transform coordinates into an appropriate declared CRS before distance/area operations. Preserve support and adjacency provenance; never invent a weights matrix. Implement the selected likelihood/interpolator/optimizer with positive-definiteness and dimension assertions. Solver hierarchy: analytical/simple non-spatial baseline → exact sparse/convex likelihood where available → deterministic numerical/sparse approximation → stochastic approximation with seeds.

Emit CRS metadata, geometry validity, neighbor graph diagnostics, residual spatial diagnostics, spatial block/leave-region-out split definitions, coverage/extrapolation flags, numerical conditioning, baseline evidence and prediction uncertainty. Invalid projection or support mismatch blocks execution and returns upstream.

