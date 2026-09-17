---
name: model-validation
title: Independent Model Validation & Sensitivity Gate
category: validation
stage: S4
description: "独立模型放行门禁：预注册验证计划、基线超越性检验、参数灵敏度分析、鲁棒性压力测试、扰动分析与误差包络评估"
inputs: ["model_spec.json", "solver_manifest.json", "validation_handoff.json", "results/"]
outputs: ["validation_plan.json", "validation_evidence.json", "failure_envelope.json", "model_validation_gate.json", "validation_artifact_index.json", "validation_report.md"]
dependencies: ["mle-solver"]
---

# Model Validation — independent S4 release authority

Own the release verdict after S3. `model-selection` and `mle-solver` cannot certify their own output; solver convergence, fit, agreement, popularity, or a plausible plot is never sufficient proof.

## Validation stage first (R4.1-B)

Before evaluating any gate, resolve `VALIDATION_STAGE` deterministically: `EMPIRICAL_STAGE` when observed data plus an executed model artifact exist; otherwise `DESIGN_STAGE` (plan/formulation only). Stage decides which of the 11 checks are applicable, each with an explicit machine-readable `applicability_reason_code`; a non-applicable check is recorded N/A with its reason and never silently converted into blocking. In DESIGN_STAGE the validator examines formulation correctness, constraint completeness, assumption disclosure, identifiability/observability risk, data requirements, baseline design, decision sensitivity, and the design's failure envelope — it must not block solely because empirical evidence does not yet exist, unless the artifact claims empirical performance anyway (fabrication ⇒ FAIL). Verdict remains the canonical four states {PASS, PASS_WITH_LIMITATIONS, REVISE, FAIL}; selection-gate labels and intents such as ALLOW_FORMULATION or COLLECT_MORE_DATA are expressed via `required_action`/upstream fields, never as verdicts. Separate `release_scope` ({FULL, DESIGN_ONLY, FORMULATION_ONLY, PROVISIONAL, NONE}) from the verdict: e.g., `PASS_WITH_LIMITATIONS + release_scope=DESIGN_ONLY + required_action=COLLECT_MORE_DATA` is a legal design-stage release. Any discovered decision/ranking reversal classified MATERIAL_TO_CONCLUSION must appear in `limitations` (minimum verdict then PASS_WITH_LIMITATIONS). Normative details and the coherence matrix: [validation-stages-and-release-semantics.md](references/validation-stages-and-release-semantics.md). Enforce with `scripts/lint_validation_artifact.py` before writing any gate artifact.

## Entry contract

Require exact hashes for the model, data, candidate portfolio, selection verdict, and solver outputs. Before inspecting final validation outcomes:

1. Write `validation_plan.json` against [validation_plan.schema.v1.json](references/validation_plan.schema.v1.json), then register its file in the orchestrator-owned immutable artifact index as `@registered_plan` before any S4 result exists. Never regenerate that trusted index from post-result files.
2. Register the intended claims, 11-check applicability partition, metrics and practical thresholds, same-basis baseline, structure-aware splits, perturbation bases, uncertainty, stability/ablation, identifiability/observability, failure tests, blocking rules, and claim restrictions.
3. Compute `plan_hash` over canonical plan content excluding `plan_hash`. Never overwrite a registered plan. A substantive change creates `VALIDATION_PLAN_CHANGED`, a revision token, and at least `REVISE`.

## Evidence and verdict workflow

1. Execute only purpose-relevant checks; retain raw outputs, commands, scopes, seeds, and artifacts.
   For an R3 family, load only `references/family_packs/<family>_validation.md` after checking the hash-bound selected `family_id`. Merge its mandatory checks into the preregistered plan; absence of the matching pack or any mandatory family check is at least `REVISE`.
2. Bind every formal result with [validation_evidence.schema.v1.json](references/validation_evidence.schema.v1.json). Each record must JSON-point to the exact value inside an on-disk validation output; the validator recomputes its hash and all upstream role hashes. A model/source file, caller-only label, or unsupported prose cannot satisfy a check.
3. Compare primary and baseline on the same information, split, target, loss, constraints, and horizon using a preregistered material-effect threshold.
4. Apply the purpose-aware identifiability/observability gate. Stable prediction may survive parameter non-identifiability only as `PASS_WITH_LIMITATIONS` with parameter-interpretation claims prohibited.
5. Exercise and record the failure domain with [failure_envelope.schema.v1.json](references/failure_envelope.schema.v1.json). Untested is `NOT_TESTED`, never “no failure found.”
6. Run `scripts/validate_r2_gate.py` to deterministically aggregate the 11 checks into [model_validation_gate.schema.v2.json](references/model_validation_gate.schema.v2.json).

## Authority rules

- `PASS`: all applicable checks pass, no material unresolved limitation, no action, no revalidation.
- `PASS_WITH_LIMITATIONS`: no blocking failure; limitations and claim restrictions must propagate unchanged downstream.
- `REVISE`: correctable blocking failure; owner/action/revision token required; S5+ blocked until revalidation.
- `FAIL`: structural failure; only change/reject model or collect more data; S5+ blocked.
- Agreement is evidence about agreement, not correctness. There is no universal 20% agreement threshold.
- A family pack supplies tests, never release authority. It cannot convert an R2 blocking fact into PASS or self-certify evidence produced by S3.
- Sensitivity ranges must come from measurement, domain, history, estimated uncertainty, or an explicit stress scenario—not a universal ±10%/±20%.

## Revision and revalidation

Use [revision_record.schema.v1.json](references/revision_record.schema.v1.json). Any substantive artifact change makes dependent evidence stale. Revalidate only affected checks using the dependency map in `scripts/validate_r2_gate.py`; presentation-only changes do not rerun the model, while equation, feature, objective, split, estimator, or solver changes do.

## Required outputs

- `validation_plan.json`
- `validation_evidence.json`
- `failure_envelope.json`
- `model_validation_gate.json`
- `validation_report.md` and executed diagnostic artifacts
- `revision_record.json` when `REVISE` or a substantive artifact/plan change occurs

When updating the pipeline manifest, validate the S4 release payload against [references/model_validation_manifest_extension.schema.v2.json](references/model_validation_manifest_extension.schema.v2.json). Execution completion and downstream release are distinct fields.

## Completion gate

- All artifact and plan hashes match exact validated versions.
- Every applicable blocking check has executed, artifact-bound evidence.
- Baseline, identifiability/observability, failure envelope, uncertainty, stability, and applicability rules are satisfied or explicitly adjudicated.
- Deterministic verdict matches the record; `REVISE`/`FAIL` block downstream, and limitations constrain claims.

Read [r2-validation-authority.md](references/r2-validation-authority.md) for check semantics and routing. Read legacy method references only after the plan selects a relevant diagnostic; their historical thresholds cannot issue the release verdict.
