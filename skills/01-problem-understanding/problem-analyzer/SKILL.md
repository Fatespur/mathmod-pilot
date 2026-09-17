---
name: problem-analyzer
title: Problem Analyzer & Task Decomposition
category: problem-understanding
stage: S1
description: "赛题形式化分解，抽取数学结构、物理实体、变量单位、目标函数、硬软约束与边界条件，生成可执行的问题依赖图与断言集"
inputs: ["run_inputs.json", "competition_problem.pdf/txt"]
outputs: ["problem_structure.json", "problem_graph.json", "variables_and_units.json", "hard_assertions.json", "assumption_risk_register.json", "expected_output_ranges.json", "analysis_report.md"]
dependencies: []
---

# Problem Analyzer — S1 problem formulation

Own the question **only through mathematical formulation**. S1 must not name, recommend, rank, or finalize a model or solver. `model-selection` owns candidate generation and selection after S1 and, when relevant, S2 data evidence.

## Workflow

1. Read the complete problem and attachments. Separate source facts, inferences, and unresolved ambiguities.
2. Build the problem graph and extract purpose, estimand/decision, sets, indices, variables, parameters, objectives, constraints, and boundary/initial conditions.
3. Describe sample, temporal, spatial, group, and network structure explicitly. For networks, record capacity, demand, vehicle, depot, time-window, flow, subtour, commodity, and dynamic-state facts before any subtype inference.
4. Record every assumption as typed evidence: necessity, risk, falsifier, evidence, and downstream dependency.
5. Audit units, extrema, conservation, domains, discreteness, nonsmoothness, identifiability, data availability, and expected ranges.
6. Emit the required artifacts and validate `problem_structure.json` against the canonical schema.

## Canonical contract

- Schema: [../model-selection/references/problem_structure.schema.v1.json](../model-selection/references/problem_structure.schema.v1.json)
- Validator: import `validate_problem_structure` from `../model-selection/scripts/validate_selection.py`.
- Any named-model field or value is `PREMATURE_MODEL_SELECTION`; remove it and retain only the structural fact that motivated it.
- Sample size may change uncertainty, identifiability, or complexity budget. It must not select a model family.
- Contest letter, wording, historical similarity, sponsor preference, popularity, and perceived sophistication have no selection authority.

## Required artifacts

- `problem_structure.json`
- `problem_graph.json`
- `variables_and_units.json`
- `hard_assertions.json`
- `assumption_risk_register.json`
- `expected_output_ranges.json`
- `analysis_report.md`

`method_routing.json` is retired in R1 and is not an S1 output or an authority source.

## Completion gate

- Every subproblem has inputs, outputs, objectives, constraints, dependencies, and unresolved ambiguities.
- Every consequential simplification has a typed assumption, falsifier, evidence need, risk, and downstream dependency.
- Discrete/nonsmooth structure, time order, network structure, units, physical bounds, and identifiability risks are explicit.
- `problem_structure.json` passes schema and semantic purity validation.
- Handoff target is S2 for data work and `model-selection` for candidate selection; no named model appears in S1 artifacts.

## References

Read [references/pipeline-contract.md](references/pipeline-contract.md) for manifest rules. Use [references/capabilities-and-physical-analysis.md](references/capabilities-and-physical-analysis.md), [references/problem-and-method-routing.md](references/problem-and-method-routing.md), and [references/antipatterns-and-downstream-contract.md](references/antipatterns-and-downstream-contract.md) only as legacy structural-analysis knowledge; their historical named-method routes are explicitly non-authoritative under R1.
