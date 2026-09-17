---
name: mle-solver
title: Mathematical Model Solver & Heuristics
category: algorithms-and-solving
stage: S3
description: "数学模型方程映射、变量与约束组装、求解器配置（LP/MILP/ODE/PDE/图论）与启发式优化算法（GA/PSO/SA）执行"
inputs: ["candidate_portfolio.json", "selection_verdict.json", "problem_structure.json"]
outputs: ["model_spec.json", "solver_manifest.json", "paper_macro_candidates.json", "validation_handoff.json", "results/"]
dependencies: ["model-selection"]
---

# MLE-Solver — S3 formulation and execution

S3 implements an accepted selection; it does not own model-family selection or model release authority.

## Entry gate

Require all of:

- `problem_structure.json`, valid under the R1 canonical schema;
- `candidate_portfolio.json`, containing baseline, primary, serious alternative, and fallback or valid `N/A` records; an R3 family requires `candidate_portfolio.schema.v2` with a validated v1 projection and family contract;
- `selection_verdict.json`, consistent with the portfolio and declaring `ALLOW_FORMULATION` plus `PROCEED_TO_SOLVER`; an R3 family requires `selection_verdict.schema.v2` whose selected family id/version matches the primary candidate;
- S2 data artifacts when the selected candidate needs observed data.

If the verdict is `REVISE_SELECTION` or `REJECT_TEMPLATE_ROUTE`, do not formulate code. Return to `model-selection`. If formulation exposes a violated/unknown precondition, missing structural fact, infeasible family, or invalid complexity claim, emit a blocking reason and return to `model-selection`; do not substitute a different family locally.

## Workflow

1. Verify hashes, schemas, gate verdict, units, assertions, expected ranges, data availability, and runtime.
2. Translate the selected candidate into a full mathematical specification with traceable variables, objective, constraints, parameters, assumptions, and solver class.
   For an R3 family, verify the portfolio's `family_id` and eligibility evidence against registry v2, then load only `references/family_packs/<family>_solver.md`. A missing pack, unsupported solver escalation, or violated pack precondition is `RETURN_TO_MODEL_SELECTION`; S3 must not select a replacement.
3. Follow the hierarchy: analytical/closed-form check → exact/convex/LP/MILP/DP/CP-SAT check → decomposition or relaxation → approximation with a bound → metaheuristic only after documented earlier-stage infeasibility or intractability.
4. Implement modular, rerunnable code. Derive every constant from data, formulation, or a stated assumption; retain commands, environment, versions, logs, and seeds.
5. Execute and check syntax/runtime, hard assertions, feasibility, dimensions, boundaries, physical/statistical plausibility, baseline comparison, and independent limiting-case or cross-method evidence.
6. Route implementation failures to `systematic-debugging`; route selection/formulation incompatibility back to `model-selection`.

## Required artifacts

- `model_spec.json`
- `src/`
- `results/`
- `solver_manifest.json`
- `paper_macro_candidates.json` containing only actually executed results
- `validation_handoff.json` containing exact `problem_id`, `model_id`, model/data/candidate-portfolio/selection-verdict SHA-256 hashes, artifact paths, solver environment, seeds, and the proposed validation purpose. S3 may not mark any of these artifacts as validated.

## Completion gate

- Input gate was `ALLOW_FORMULATION`; artifact hashes remain traceable.
- Code reruns without hidden manual steps or magic numbers.
- All hard assertions and feasibility checks pass; warnings are explained.
- Baseline and selected-candidate evidence are reported, including gap/bound evidence when applicable.
- Solver success is not treated as proof that the model is correct.
- The family solver pack may define implementation assertions and evidence to hand off, but it cannot issue an S4 verdict or weaken a family validation requirement.
- A successful S3 run ends in `WAITING_FOR_MODEL_VALIDATION`, not presentation-ready or released. S4 independently owns `MODEL_VALIDATION_GATE`; only its hash-bound `PASS` or `PASS_WITH_LIMITATIONS` verdict can authorize S5–S7, and limitations must propagate to every downstream claim.
- `REVISE` or `FAIL` returns the revision token and required action to the named owner stage. S3 must not self-certify, suppress, overwrite, or reinterpret the S4 verdict.

## References

Read [references/pipeline-contract.md](references/pipeline-contract.md), then load only implementation references relevant to the accepted family. [references/model_selection_guide.md](references/model_selection_guide.md) and named-method defaults in other legacy references are historical implementation notes, not selection authority. The canonical registry, portfolio contract, gate, and exact-first policy live in [../model-selection/SKILL.md](../model-selection/SKILL.md).
