# Validation stages, verdict/action/scope separation, deterministic applicability (R4.1-B)

Normative since R4_1B_PRODUCTION_CANDIDATE. Additive to R2 authority; nothing here weakens an
existing veto. Canonical engine: `scripts/validation_stage_semantics.py`; enforcement:
`scripts/lint_validation_artifact.py`; schema: `model_validation_gate.schema.v3.json`.

## 1. Stage-first ordering

Resolve `VALIDATION_STAGE` BEFORE evaluating any gate. Pure function of artifact context:

| Input fact | Meaning |
|---|---|
| has_observed_data | registered data artifacts exist for this problem |
| model_executed | an on-disk executed model/solver artifact exists |
| claims_empirical_performance | any claim asserts measured/out-of-sample performance |

- `EMPIRICAL_STAGE` ⇔ has_observed_data ∧ model_executed.
- `DESIGN_STAGE` otherwise (plan/formulation exists; empirical evidence does not yet).

Forbidden: choosing N/A implicitly per gate; treating missing evidence as automatic blocking
without first asking whether that evidence SHOULD exist at the current stage.

## 2. Applicability matrix (deterministic)

EMPIRICAL_STAGE — v2 behavior unchanged: gates applicable per registered plan/purpose;
identifiability N/A only when the intended claim has no identification meaning
(reason `CLAIM_HAS_NO_IDENTIFICATION_MEANING`).

DESIGN_STAGE —

| Gate | Applicable | Evaluates | N/A reason when false |
|---|---|---|---|
| V01 | TRUE | formulation/mathematical correctness of the design | — |
| V02 | conditional | completeness + validity of DATA REQUIREMENTS | `DESIGN_STAGE_NO_OBSERVED_DATA` |
| V03 | FALSE | — | `DESIGN_STAGE_NO_EXECUTED_BASELINE` |
| V04 | FALSE | — | `DESIGN_STAGE_NO_EMPIRICAL_MODEL` |
| V05 | TRUE | decision-sensitivity of the design (registered perturbation bases) | — |
| V06 | FALSE | — | `DESIGN_STAGE_NO_INDEPENDENT_ESTIMAND_TEST` |
| V07 | conditional | uncertainty/identifiability-risk disclosure quality | `DETERMINISTIC_DESIGN_NO_UNCERTAINTY_CLAIM` |
| V08 | TRUE | identifiability/observability RISK disclosure | — |
| V09 | TRUE | constraint completeness/hard-constraint consistency | — |
| V10 | TRUE | failure envelope OF THE DESIGN (trigger conditions documented) | — |
| V11 | FALSE | — | `DESIGN_STAGE_NO_FITTED_COMPONENT` |

Hard rule: a DESIGN_STAGE run may never be blocked solely because empirical evidence is absent,
UNLESS the artifact claims empirical performance anyway (`claims_empirical_performance=true`
under DESIGN_STAGE ⇒ fabrication path ⇒ FAIL, reason `EMPIRICAL_CLAIM_WITHOUT_EVIDENCE`).

## 3. Canonical verdict universe (unchanged four states)

`PASS · PASS_WITH_LIMITATIONS · REVISE · FAIL`
Selection-gate labels (`ALLOW_FORMULATION`, …), intents (`COLLECT_MORE_DATA`, …), process words
(`CONTINUE`, `BLOCK`) are NEVER valid verdict values. See `LEGACY_LABEL_MAPPING` in the engine
module; mapping is analysis-only — historical artifacts are never rewritten.

## 4. Separated semantic fields (v3)

- `validation_stage`: EMPIRICAL_STAGE | DESIGN_STAGE
- `verdict`: canonical four
- `required_action`: v2 enum retained verbatim for compatibility
  ({NONE, REVISE_FORMULATION, REVISE_DATA, SIMPLIFY_MODEL, CHANGE_MODEL, REJECT_MODEL,
    COLLECT_MORE_DATA, RERUN_SOLVER, RERUN_VALIDATION})
- `release_scope`: FULL | DESIGN_ONLY | FORMULATION_ONLY | PROVISIONAL | NONE

Coherent combinations (enforced):

| verdict | release_scope | required_action |
|---|---|---|
| PASS | FULL | NONE |
| PASS_WITH_LIMITATIONS | FULL (material limits disclosed) or PROVISIONAL/DESIGN_ONLY/FORMULATION_ONLY | any incl. COLLECT_MORE_DATA |
| REVISE | NONE | ≠ NONE |
| FAIL | NONE | CHANGE_MODEL / REJECT_MODEL / COLLECT_MORE_DATA |

Illegal: PASS+non-FULL scope; PASS+action≠NONE; REVISE/FAIL+scope≠NONE; PWL with empty
limitations AND unrestricted scope; DESIGN_STAGE artifact with verdict=PASS (any scope).

## 5. Material sensitivity → limitations propagation

If validation discovers a decision reversal, ranking/policy reversal, or threshold-regime change
(e.g., a plan optimum flips under a registered perturbation), it MUST be classified
`MATERIAL_TO_CONCLUSION` true/false. If true, the item enters `limitations` verbatim-enough to
reconstruct it, and the minimum verdict is PASS_WITH_LIMITATIONS (upgrade to REVISE when the
registered practical effect is crossed). Generic rule; no thresholds or case identifiers embedded.

## 6. Sovereignty unchanged

Only model-validation issues these verdicts. Design-stage PWL remains an independent S4 release
decision bound to hashed plan/design artifacts — it is not self-certification by earlier stages.
