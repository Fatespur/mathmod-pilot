"""
R4.1-B deterministic validation-stage semantics engine.

Single source of truth for:
  - VALIDATION_STAGE resolution (stage-first)
  - deterministic gate applicability with reason codes
  - verdict / required_action / release_scope coherence
  - material-sensitivity -> limitations propagation rule
  - LEGACY_LABEL_MAPPING (analysis-only; never rewrites history)

Pure functions only. No case identifiers, no benchmark-specific branches.
"""
from __future__ import annotations

CANONICAL_VERDICTS = ("PASS", "PASS_WITH_LIMITATIONS", "REVISE", "FAIL")
REQUIRED_ACTIONS = (
    "NONE", "REVISE_FORMULATION", "REVISE_DATA", "SIMPLIFY_MODEL", "CHANGE_MODEL",
    "REJECT_MODEL", "COLLECT_MORE_DATA", "RERUN_SOLVER", "RERUN_VALIDATION",
)
RELEASE_SCOPES = ("FULL", "DESIGN_ONLY", "FORMULATION_ONLY", "PROVISIONAL", "NONE")
VALIDATION_STAGES = ("EMPIRICAL_STAGE", "DESIGN_STAGE")

GATE_IDS = (
    "V01_MATHEMATICAL_CORRECTNESS", "V02_DATA_COMPATIBILITY", "V03_BASELINE_SUPERIORITY",
    "V04_OUT_OF_SAMPLE_VALIDITY", "V05_SENSITIVITY", "V06_ROBUSTNESS", "V07_UNCERTAINTY",
    "V08_INTERPRETABILITY_DOMAIN_SENSE", "V09_CONSTRAINT_SATISFACTION",
    "V10_FAILURE_ENVELOPE", "V11_STABILITY_ABLATION",
)

# ---------------------------------------------------------------- stage ------

def resolve_validation_stage(has_observed_data: bool, model_executed: bool,
                             claims_empirical_performance: bool = False):
    """Stage-first resolution. Deterministic; identical inputs -> identical output."""
    empirical = bool(has_observed_data) and bool(model_executed)
    return {
        "validation_stage": "EMPIRICAL_STAGE" if empirical else "DESIGN_STAGE",
        "reason_code": ("EXECUTED_EMPIRICAL_PIPELINE_PRESENT" if empirical
                        else "DESIGN_STAGE_NO_EMPIRICAL_MODEL"),
        "fabrication_risk": (not empirical) and bool(claims_empirical_performance),
    }

# ------------------------------------------------------- applicability -------

_DESIGN_APPLICABILITY = {
    "V01_MATHEMATICAL_CORRECTNESS":        (True,  "REGISTERED_PLAN_MARKS_NOT_APPLICABLE"),
    "V02_DATA_COMPATIBILITY":              (False, "DESIGN_STAGE_NO_OBSERVED_DATA"),
    "V03_BASELINE_SUPERIORITY":            (False, "DESIGN_STAGE_NO_EXECUTED_BASELINE"),
    "V04_OUT_OF_SAMPLE_VALIDITY":          (False, "DESIGN_STAGE_NO_EMPIRICAL_MODEL"),
    "V05_SENSITIVITY":                     (True,  "REGISTERED_PLAN_MARKS_NOT_APPLICABLE"),
    "V06_ROBUSTNESS":                      (False, "DESIGN_STAGE_NO_INDEPENDENT_ESTIMAND_TEST"),
    "V07_UNCERTAINTY":                     (True,  "DETERMINISTIC_DESIGN_NO_UNCERTAINTY_CLAIM"),
    "V08_INTERPRETABILITY_DOMAIN_SENSE":   (True,  "REGISTERED_PLAN_MARKS_NOT_APPLICABLE"),
    "V09_CONSTRAINT_SATISFACTION":         (True,  "REGISTERED_PLAN_MARKS_NOT_APPLICABLE"),
    "V10_FAILURE_ENVELOPE":                (True,  "REGISTERED_PLAN_MARKS_NOT_APPLICABLE"),
    "V11_STABILITY_ABLATION":              (False, "DESIGN_STAGE_NO_FITTED_COMPONENT"),
}

def applicable_gates(validation_stage: str, ident_claim_has_no_identification_meaning: bool = False):
    """Return {gate_id: (applicable, reason_code)} deterministically for the given stage."""
    out = {}
    if validation_stage == "DESIGN_STAGE":
        for gid, (appl, reason) in _DESIGN_APPLICABILITY.items():
            out[gid] = (appl, reason)
    elif validation_stage == "EMPIRICAL_STAGE":
        for gid in GATE_IDS:
            out[gid] = (True, "EXECUTED_EMPIRICAL_PIPELINE_PRESENT")
    else:
        raise ValueError("unknown stage: %r" % (validation_stage,))
    if ident_claim_has_no_identification_meaning:
        out["V08_INTERPRETABILITY_DOMAIN_SENSE"] = (False, "CLAIM_HAS_NO_IDENTIFICATION_MEANING")
    return out

# --------------------------------------------------------- coherence ---------

class CoherenceViolations(list):
    pass

def check_coherence(verdict: str, required_action: str, release_scope: str,
                    limitations, validation_stage: str,
                    material_reversal_present: bool = False,
                    claims_empirical_performance_under_design: bool = False):
    """Validate the legal combination space of section 4/5 of the semantics reference."""
    v = []
    if verdict not in CANONICAL_VERDICTS:
        v.append(("NONCANONICAL_VERDICT", verdict))
    if required_action not in REQUIRED_ACTIONS:
        v.append(("INVALID_REQUIRED_ACTION", required_action))
    if release_scope not in RELEASE_SCOPES:
        v.append(("INVALID_RELEASE_SCOPE", release_scope))
    if validation_stage not in VALIDATION_STAGES:
        v.append(("INVALID_VALIDATION_STAGE", validation_stage))
    if claims_empirical_performance_under_design and validation_stage == "DESIGN_STAGE":
        v.append(("EMPIRICAL_CLAIM_WITHOUT_EVIDENCE", "design-stage artifact asserts performance"))
    if verdict == "PASS":
        if release_scope != "FULL":
            v.append(("PASS_REQUIRES_FULL_SCOPE", release_scope))
        if required_action != "NONE":
            v.append(("PASS_REQUIRES_ACTION_NONE", required_action))
    if verdict == "PASS_WITH_LIMITATIONS":
        restricted = release_scope in ("PROVISIONAL", "DESIGN_ONLY", "FORMULATION_ONLY")
        if not limitations and not restricted:
            v.append(("PWL_NEEDS_LIMITATIONS_OR_RESTRICTED_SCOPE", ""))
    if verdict in ("REVISE", "FAIL"):
        if release_scope != "NONE":
            v.append(("BLOCKING_VERDICT_SCOPE_NOT_NONE", release_scope))
    if verdict == "REVISE" and required_action == "NONE":
        v.append(("REVISE_REQUIRES_ACTION", required_action))
    if validation_stage == "DESIGN_STAGE" and verdict == "PASS":
        v.append(("DESIGN_STAGE_CANNOT_BARE_PASS", verdict))
    # Material sensitivity propagation (generic rule; no thresholds embedded)
    if material_reversal_present and verdict == "PASS":
        v.append(("SENSITIVITY_NOT_PROPAGATED", "material reversal with bare PASS"))
    if material_reversal_present and verdict == "PASS_WITH_LIMITATIONS" and not limitations:
        v.append(("SENSITIVITY_NOT_PROPAGATED", "material reversal absent from limitations"))
    return CoherenceViolations(v)

# ------------------------------------------------------- legacy mapping ------

LEGACY_LABEL_MAPPING = {
    "ALLOW_FORMULATION": {"kind": "NOT_A_VERDICT",
                          "target_field": "selection_verdict.anti_template_gate.verdict",
                          "note": "selection-stage gate decision; never a validation verdict"},
    "COLLECT_MORE_DATA": {"kind": "REQUIRED_ACTION",
                          "target_field": "required_action",
                          "note": "intent field; verdict must still be canonical (typically PWL+DESIGN_ONLY or REVISE)"},
    "PASS_DIRECT":       {"kind": "VERDICT_EQUIVALENT",
                          "target_field": "verdict=PASS + release_scope=FULL",
                          "note": "valid only when evidence complete under EMPIRICAL_STAGE"},
    "REVISE_DESIGN":     {"kind": "VERDICT_PLUS_SCOPE",
                          "target_field": "verdict=REVISE + release_scope=DESIGN_ONLY->NONE",
                          "note": "split into verdict and scope fields"},
    "REVISE_PREFERENCES": {"kind": "VERDICT_PLUS_ACTION",
                           "target_field": "verdict=REVISE + required_action=REFINE_ASSUMPTIONS",
                           "note": "stakeholder-preference elicitation is an assumption refinement"},
    "REVISE_FORMULATION": {"kind": "VERDICT_PLUS_ACTION",
                           "target_field": "verdict=REVISE + required_action=REVISE_FORMULATION",
                           "note": "already split in schema v2 action enum"},
    "BLOCK":             {"kind": "NOT_A_VERDICT", "target_field": "release_scope=NONE",
                          "note": "blocking is expressed by REVISE/FAIL + NONE scope"},
    "CONTINUE":          {"kind": "NOT_A_VERDICT", "target_field": "-",
                          "note": "process word; no semantic target"},
}

def normalize_legacy_label(label: str):
    return LEGACY_LABEL_MAPPING.get(label)

# ------------------------------------------------ design-stage evaluation ----

def evaluate_design_stage(formulation_correct: bool, constraints_complete: bool,
                          assumptions_disclosed: bool, identifiability_risk_stated: bool,
                          data_requirements_specified: bool, baseline_designed: bool,
                          failure_envelope_documented: bool,
                          material_reversal_present: bool = False):
    """Deterministic DESIGN_STAGE rubric -> coherent triple (+blocking list)."""
    blocking = []
    if not formulation_correct:
        blocking.append("formulation incorrect")
    if not constraints_complete:
        blocking.append("constraint set incomplete")
    if not assumptions_disclosed:
        blocking.append("assumptions undisclosed")
    if not data_requirements_specified:
        blocking.append("data requirements unspecified")
    if not failure_envelope_documented:
        blocking.append("failure envelope undocumented")
    quality_flags = [identifiability_risk_stated, baseline_designed]

    if blocking:
        verdict, scope = "REVISE", "NONE"
        # Deterministic action mapping using ONLY the v2-compatible action enum.
        if any(("constraint" in b or "formulation" in b or "assumptions" in b) for b in blocking):
            action = "REVISE_FORMULATION"      # assumptions belong to formulation owner
        elif any("data requirements" in b for b in blocking):
            action = "REVISE_DATA"
        else:
            action = "COLLECT_MORE_DATA"
    else:
        # Sound design: release the DESIGN, never pretend empirical proof.
        limitations = []
        if material_reversal_present:
            limitations.append("registered perturbation reverses the recommended decision "
                               "(MATERIAL_TO_CONCLUSION)")
        if not all(quality_flags):
            limitations.append("identifiability risk / baseline rationale incompletely stated")
        limitations.append("design-stage result: no empirical performance demonstrated")
        verdict = "PASS_WITH_LIMITATIONS"
        scope = "DESIGN_ONLY"
        action = "COLLECT_MORE_DATA"
        blocking = []
        return {"verdict": verdict, "release_scope": scope, "required_action": action,
                "limitations": limitations, "blocking_failures": []}
    limits = ["design-stage result: no empirical performance demonstrated"]
    return {"verdict": verdict, "release_scope": scope, "required_action": action,
            "limitations": limits, "blocking_failures": blocking}
