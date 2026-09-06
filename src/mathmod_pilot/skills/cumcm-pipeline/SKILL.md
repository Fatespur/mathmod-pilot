---
name: cumcm-pipeline
description: Full S0 to S7 end-to-end mathematical modeling competition pipeline orchestration (Task Setup, Mechanism Modeling, Data Audit, Solver, Validation, Visuals, Writing V2.1, Submission Gate).
version: 3.1.0
---

# CUMCM Full S0-S7 Pipeline

## Stage Architecture
- **S0 (INIT & Freeze)**: Input fingerprinting, asset registration, freeze manifest.
- **S1 (Problem Analysis)**: 3D kinematics, dynamic line-of-sight (LOS) ray tracing, cylindrical envelope sampling.
- **S2 (Data Audit)**: Excel template structure audit, unit system registry, data dictionary.
- **Model Selection Gate**: Reject template models (GM/TOPSIS/AHP), adopt continuous distance-guided differential evolution + simplex.
- **S3 (High-Performance Solver)**: Vectorized kinematics solver, multi-objective spatio-temporal relay optimization.
- **S4 (Independent Scientific Validation)**: Step size convergence, OAT/Sobol sensitivity, 5000-run Monte Carlo simulation.
- **S5 (Figure Governance)**: Publication-grade 300dpi figures (overview, geometry, response surface, gantt, radar/matrix).
- **S6 (Paper Writing V3)**: Markdown-Only writing pipeline (paper.md, Markdown Math, figure/table depth, no LaTeX).
- **S7 (Submission Governance)**: Anonymity verification, reference integrity, package signing.
