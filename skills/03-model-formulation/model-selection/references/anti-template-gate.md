# ANTI_TEMPLATE_GATE.v1

The gate runs after a complete candidate portfolio and before mathematical formulation.

## Required answers

1. Why does the mathematical structure favor the primary family?
2. Why is the simplest plausible baseline insufficient for at least one predeclared benefit?
3. Which serious alternative was considered?
4. Why was that alternative not selected?
5. Which assumptions/data conditions does the primary require, and which are supported, violated, or unknown?
6. Which observation triggers abandonment or replacement?

## Verdict aggregation

- `REJECT_TEMPLATE_ROUTE`: any primary selection basis includes keyword, sample-size band, contest category, historical habit, popularity, or advanced reputation.
- `REVISE_SELECTION`: no baseline; no serious alternative; an answer is missing; a primary precondition is violated/unknown without an explicit collection or fallback plan; portfolio/schema mismatch.
- `ALLOW_FORMULATION`: structure match established, all material preconditions checked, baseline and serious alternative exist, why-not reasoning is complete, and no prohibited basis is present.

On a blocking verdict emit `blocking_reason`, `owner_stage=MODEL_SELECTION`, `required_action`, and a new `revision_id`. Only `ALLOW_FORMULATION` sets `required_action=PROCEED_TO_SOLVER`.
