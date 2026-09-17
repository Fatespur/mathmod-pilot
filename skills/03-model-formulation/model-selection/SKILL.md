---
name: model-selection
title: Model Selection & Family Portfolio
category: model-formulation
stage: S2B
description: "基于数学结构构建基线/主选/备选模型组合，执行反套路门禁（Anti-template gate），评估参数可识别性与求解器可行性"
inputs: ["problem_structure.json", "data_dictionary.json", "preprocessing_report.md"]
outputs: ["candidate_portfolio.json", "selection_verdict.json"]
dependencies: ["problem-analyzer", "data-processing"]
---

# Model Selection — structure-first candidate screening

Own the boundary between `$problem-analyzer` and `$mle-solver`. Consume `problem_structure.json` plus available S2 data profile; emit `candidate_portfolio.json` and `selection_verdict.json`. Never implement model code.

The R1 selection verdict authorizes formulation only. It is neither evidence that the fitted model works nor permission for S5–S7. After S3, the independent R2 `$model-validation` gate must bind the current artifacts and issue `PASS`, `PASS_WITH_LIMITATIONS`, `REVISE`, or `FAIL`; model-selection must not predeclare or override that verdict.

## Invariants

- `STRUCTURE_FIRST`, `MODEL_NAME_LATE`, `BASELINE_MANDATORY`, `ALTERNATIVES_MANDATORY`, `WHY_NOT_REQUIRED`.
- A keyword, sample-count band, contest category, historical habit, popularity, or “advanced” reputation may raise a question; it cannot select a model.
- Screen in this order: validity → structural compatibility → data compatibility → identifiability → baseline → alternatives → complexity → solver feasibility → validation feasibility.
- Do not compress the screening matrix into an unsupported weighted total.
- Metaheuristics are last-resort candidates after analytical, exact/convex, discrete exact, decomposition, deterministic numerical, and approximation/surrogate routes are screened.

## Required workflow

1. Validate `problem_structure.json` against [problem_structure.schema.v1.json](references/problem_structure.schema.v1.json). Reject premature named models with `PREMATURE_MODEL_SELECTION` and return `REVISE_FORMULATION`.
2. Read frozen [model_family_registry.v1.json](references/model_family_registry.v1.json) as the universal compact registry. For an eligible R3 target family, overlay [model_family_registry.v2.json](references/model_family_registry.v2.json); it upgrades only the five named entries and does not remove other v1 families. Treat all entries as preconditioned candidate knowledge, never defaults. Load exactly one matching `references/family_packs/*_selection.md` only after its preconditions remain plausible. If multiple families remain eligible, load each eligible selection pack and preserve them as competing candidates.
3. Generate four roles: `BASELINE`, `PRIMARY`, `ALTERNATIVE`, `FALLBACK`. A role may be `N/A` only with a specific `na_reason`; baseline `N/A` cannot pass the anti-template gate.
4. Complete every candidate field in [candidate_portfolio.schema.v1.json](references/candidate_portfolio.schema.v1.json), including failure signatures, validation plan, why-use, why-not, and replacement trigger. If any portfolio candidate uses an R3 target family, emit `candidate_portfolio.schema.v2` and `selection_verdict.schema.v2`; the v2 validator first validates an exact v1 projection, then enforces family id/version, registry eligibility evidence, rejected neighbors and family-specific validation linkage.
5. Build a criterion-by-candidate screening matrix. Preserve dimensions rather than inventing aggregate weights.
6. Execute [ANTI_TEMPLATE_GATE.v1](references/anti-template-gate.md). Only `ALLOW_FORMULATION` permits solver handoff.
7. Write `selection_verdict.json` using [selection_verdict.schema.v1.json](references/selection_verdict.schema.v1.json), or [selection_verdict.schema.v2.json](references/selection_verdict.schema.v2.json) for an R3 target portfolio.

## Family-specific routing

Read [selection-reasoning.md](references/selection-reasoning.md) for general reasoning. For R3 families, never route from a family word: use registry facts, then progressively disclose the corresponding selection pack. A selected R3 family must record `family_id`, `family_version`, satisfied preconditions, rejected near-neighbors, baseline, serious alternative, solver hierarchy, family validation requirements, failure modes, and replacement triggers in the portfolio.

## Failure routing

- Missing/unknown precondition, baseline, serious alternative, or why-not → `REVISE_SELECTION`.
- Primary basis is keyword, sample band, contest label, habit, popularity, or prestige → `REJECT_TEMPLATE_ROUTE`.
- Structural ambiguity changes variables, constraints, estimand, or intended decision → return to `$problem-analyzer`.
- Solver discovers a family-level defect → accept `RETURN_TO_MODEL_SELECTION`; never let S3 silently replace the family.

## Verification

Run `python scripts/test_r1_contracts.py`, then `python scripts/test_r3_family_coverage.py` when registry v2 or any R3 family is in scope. The deterministic validators check v1 projection compatibility, v2 family/hash linkage, premature-model purity, gate verdicts, family screening invariance, solver hierarchy, pack contracts and frozen R1/R2 regression.
