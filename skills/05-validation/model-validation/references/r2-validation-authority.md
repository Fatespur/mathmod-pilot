# R2 validation authority

## Eleven checks

| ID | Release question | Typical blocking facts |
|---|---|---|
| V01 | Is the mathematics internally correct? | units/domain/conservation/formulation/solver-certificate failure |
| V02 | Is the data compatible with the claim? | leakage, invalid sampling boundary, dependence ignored |
| V03 | Does primary materially beat the baseline on the same basis? | different split/target/loss/horizon; baseline wins; complexity benefit absent |
| V04 | Does validation represent deployment/generalization? | random K-fold for temporal data; group leakage; invalid spatial split |
| V05 | Is the conclusion stable over plausible perturbations? | high-risk decision reversal |
| V06 | Is robustness independent and estimand-aligned? | shared bias; different estimands; agreement used as correctness |
| V07 | Is uncertainty propagated to the claimed decision? | point estimate silently used downstream |
| V08 | Are interpretation and domain claims defensible? | required parameter/state non-identifiability or non-observability |
| V09 | Are all hard constraints satisfied? | any hard violation despite solver success |
| V10 | Is a tested failure envelope available? | untested envelope or hidden failure trigger |
| V11 | Is output stable, and do complex components contribute materially? | seed/split reversal; useless component |

## Purpose-aware identifiability

Use only applicable diagnostics: symbolic/rank/Jacobian/observability/Fisher/condition/profile/multistart/recovery/perturbation/posterior methods. `NA` is allowed only when the intended claim has no parameter/state-identification meaning. “Not tested” is not an N/A rationale.

- Prediction-only + stable prediction + nonunique parameters: `PASS_WITH_LIMITATIONS`; prohibit unique parameter/mechanism claims.
- Parameter inference, state reconstruction, or mechanism interpretation + required non-identifiability/non-observability: blocking `REVISE` or `FAIL`.

## Baseline and materiality

The plan must preregister the baseline and smallest practical effect or decision-loss tolerance. Compare the same information, split, target, intended loss, constraints, and horizon. Training improvement, prettier output, or a 0.01 metric gain below the registered practical threshold does not justify complexity.

## Independent evidence

Every PASS check cites one or more records whose artifact hash is current and whose method, input/output scope, metric, observed value, expected range, producer stage, and timestamp are explicit. Natural-language conclusions may summarize evidence but cannot replace it.

## Routing

- Mathematical/constraint/irreparable compatibility/required-identifiability failure: `FAIL` and change/reject/collect.
- Correctable split, evidence, comparison, uncertainty, stability, or formulation failure: `REVISE` to the owning stage with a new token.
- Nonblocking uncertainty or scope limitation: `PASS_WITH_LIMITATIONS`, with restrictions copied to interpretation, figures, paper, review, and release.

