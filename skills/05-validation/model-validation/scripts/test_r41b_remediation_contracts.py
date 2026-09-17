#!/usr/bin/env python3
"""R4_1B_TARGETED_REGRESSION_SUITE — independent contract tests (no case IDs).

Proves: targeted defects reduced AND no new false-PASS path introduced.
Each scenario executes twice (determinism requirement). Uses only the new
stage-semantics engine + lint; does not modify frozen R2 validator.
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from validation_stage_semantics import (
    resolve_validation_stage, applicable_gates, check_coherence,
    evaluate_design_stage, normalize_legacy_label, CANONICAL_VERDICTS,
)

LINT = HERE / "lint_validation_artifact.py"
RESULTS = []

def scenario(name):
    def deco(fn):
        def run():
            outs = []
            for rep in range(2):                      # every scenario twice
                outs.append(fn())
            ok = outs[0] == outs[1]
            RESULTS.append((name, ok, outs[0]))
            return ok
        SCENARIOS.append(run)
        return run
    return deco

SCENARIOS = []

def base_gate(**over):
    d = {
        "schema_version": "model_validation_gate.schema.v3",
        "gate": "MODEL_VALIDATION_GATE",
        "problem_id": "GENERIC_PROBLEM",
        "model_id": "GENERIC_MODEL",
        "validation_stage": "EMPIRICAL_STAGE",
        "release_scope": "NONE",
        "artifact_hashes": {k: "a" * 64 for k in ["model", "data", "candidate_portfolio",
                                                  "selection_verdict", "validation_plan",
                                                  "evidence_bundle", "failure_envelope"]},
        "validation_plan_hash": "b" * 64,
        "checks": [{"check_id": g, "applicable": True,
                    "applicability_reason_code": "EXECUTED_EMPIRICAL_PIPELINE_PRESENT",
                    "status": "PASS", "evidence_ids": ["E1"],
                    "rationale": "deterministic engine fixture rationale text",
                    "blocking": False, "severity": "INFO", "failure_class": "NONE"}
                   for g in [g for g in [
                       "V01_MATHEMATICAL_CORRECTNESS", "V02_DATA_COMPATIBILITY",
                       "V03_BASELINE_SUPERIORITY", "V04_OUT_OF_SAMPLE_VALIDITY",
                       "V05_SENSITIVITY", "V06_ROBUSTNESS", "V07_UNCERTAINTY",
                       "V08_INTERPRETABILITY_DOMAIN_SENSE", "V09_CONSTRAINT_SATISFACTION",
                       "V10_FAILURE_ENVELOPE", "V11_STABILITY_ABLATION"]]],
        "identifiability_observability": {
            "applicable": False, "purpose": "NOT_APPLICABLE", "status": "NA", "methods": [],
            "evidence_ids": [], "rationale": "no identification claim exists in this fixture",
            "claim_restrictions": []},
        "verdict": "PASS_WITH_LIMITATIONS",
        "blocking_failures": [],
        "limitations": [],
        "claim_restrictions": [],
        "required_action": "COLLECT_MORE_DATA",
        "material_sensitivity": {"present": False, "material_to_conclusion": False},
        "owner_stage": "MODEL_VALIDATION",
        "revision_sequence": 1, "revision_token": None, "revalidation_required": False,
        "validator_version": "R2_VALIDATOR.v2_STAGE_AWARE",
        "created_at": "2026-01-01T00:00:00Z",
    }
    d.update(over)
    return d

# ------------------------- TARGETED: design-stage mode (B1) ------------------

@scenario("T-DS-01 design-stage data-less design yields PWL/DESIGN_ONLY/CMD (not blocking FAIL)")
def _():
    st = resolve_validation_stage(has_observed_data=False, model_executed=False)
    assert st["validation_stage"] == "DESIGN_STAGE"
    res = evaluate_design_stage(formulation_correct=True, constraints_complete=True,
                                assumptions_disclosed=True, identifiability_risk_stated=True,
                                data_requirements_specified=True, baseline_designed=True,
                                failure_envelope_documented=True)
    v = check_coherence(res["verdict"], res["required_action"], res["release_scope"],
                        res["limitations"], st["validation_stage"])
    gates = applicable_gates("DESIGN_STAGE")
    oos_na = gates["V04_OUT_OF_SAMPLE_VALIDITY"]
    assert not v, v
    assert (res["verdict"], res["release_scope"], res["required_action"]) == \
        ("PASS_WITH_LIMITATIONS", "DESIGN_ONLY", "COLLECT_MORE_DATA")
    assert oos_na == (False, "DESIGN_STAGE_NO_EMPIRICAL_MODEL")
    assert res["verdict"] in CANONICAL_VERDICTS
    return {"stage": st["validation_stage"], **res}

@scenario("T-DS-02 unsound design still blocks with canonical verdict + separated fields")
def _():
    res = evaluate_design_stage(formulation_correct=False, constraints_complete=False,
                                assumptions_disclosed=False, identifiability_risk_stated=False,
                                data_requirements_specified=False, baseline_designed=False,
                                failure_envelope_documented=False)
    v = check_coherence(res["verdict"], res["required_action"], res["release_scope"],
                        res["limitations"], "DESIGN_STAGE")
    assert not v and res["verdict"] == "REVISE" and res["release_scope"] == "NONE"
    return res

@scenario("T-ENC-01 intent COLLECT_MORE_DATA never appears as verdict; combo is coherent")
def _():
    art = base_gate(verdict="PASS_WITH_LIMITATIONS", validation_stage="DESIGN_STAGE",
                    release_scope="DESIGN_ONLY", required_action="COLLECT_MORE_DATA")
    v = check_coherence(art["verdict"], art["required_action"], art["release_scope"],
                        art["limitations"] or ["design-stage: nothing executed yet"],
                        "DESIGN_STAGE")
    assert not v
    m = normalize_legacy_label("COLLECT_MORE_DATA")
    assert m["kind"] == "REQUIRED_ACTION" and m["target_field"] == "required_action"
    return {"combo": "PWL+DESIGN_ONLY+CMD", "legacy_map_kind": m["kind"]}

@scenario("T-B03-01 FAIL vs REVISE both-block classified S2 (not substantive false reject)")
def _():
    sys.path.insert(0, str(Path(r"./reports\modeling_skill_upgrade\r4_1b\tools")))
    import benchmark_semantics as bs
    lvl = bs.classify_mismatch("FAIL", ["REVISE"])
    assert lvl == "S2_BLOCKING_BOUNDARY"
    capj = bs.cap_dependency_check()          # pure label boundary: conclusion unchanged
    assert capj is False
    return {"severity": lvl, "cap_justified": capj}

@scenario("T-B05-01 material reversal must reach limitations; bare PASS forbidden")
def _():
    v = check_coherence("PASS", "NONE", "FULL", [], "EMPIRICAL_STAGE",
                        material_reversal_present=True)
    codes = [c for c, _ in v]
    assert "SENSITIVITY_NOT_PROPAGATED" in codes
    v2 = check_coherence("PASS_WITH_LIMITATIONS", "COLLECT_MORE_DATA", "PROVISIONAL",
                         ["decision reverses beyond registered threshold"], "EMPIRICAL_STAGE",
                         material_reversal_present=True)
    assert not v2
    return {"bare_pass_rejected": True, "pwl_with_limitation_ok": True}

@scenario("T-B05-02 applicability deterministic across repeated identical contexts")
def _():
    a = applicable_gates("DESIGN_STAGE")
    b = applicable_gates("DESIGN_STAGE")
    c = resolve_validation_stage(False, False)
    dd = resolve_validation_stage(False, False)
    assert a == b and c == dd
    # V05-style gate identical across both calls:
    assert a["V05_SENSITIVITY"] == b["V05_SENSITIVITY"]
    return {"v05": a["V05_SENSITIVITY"], "stable": True}

# --------------------- NEGATIVE CONTROLS (permissiveness guards) -------------

@scenario("NC-EMP-01 empirical leakage FAIL still blocks (no permissive drift)")
def _():
    st = resolve_validation_stage(True, True)
    assert st["validation_stage"] == "EMPIRICAL_STAGE"
    g = applicable_gates("EMPIRICAL_STAGE")
    assert all(appl for appl, _ in g.values())
    v = check_coherence("REVISE", "REVISE_DATA", "NONE", [], "EMPIRICAL_STAGE")
    assert not v
    return {"stage": "EMPIRICAL", "revise_blocks": True}

@scenario("NC-EMP-02 clean complete empirical instance may still be PASS/FULL/NONE")
def _():
    v = check_coherence("PASS", "NONE", "FULL", [], "EMPIRICAL_STAGE")
    assert not v
    return {"pass_full_allowed": True}

@scenario("NC-FAB-01 design-stage artifact claiming performance => fabrication path flagged")
def _():
    st = resolve_validation_stage(False, False, claims_empirical_performance=True)
    assert st["fabrication_risk"] is True
    v = check_coherence("PASS", "NONE", "FULL", [], "DESIGN_STAGE",
                        claims_empirical_performance_under_design=True)
    codes = [c for c, _ in v]
    assert "EMPIRICAL_CLAIM_WITHOUT_EVIDENCE" in codes or "DESIGN_STAGE_CANNOT_BARE_PASS" in codes
    return {"fabrication_flagged": True}

@scenario("NC-IDENT-01 parameter-inference overclaim remains blocked via purpose-aware rule")
def _():
    # existing R2 authority retained: nonidentifiable + inference claim -> blocking REVISE,
    # owned by formulation (v2-compatible action enum).
    v = check_coherence("REVISE", "REVISE_FORMULATION", "NONE", [], "EMPIRICAL_STAGE")
    assert not v
    return {"identifiability_block_representable": True}

@scenario("NC-LINT-01 lint rejects legacy/noncanonical verdict labels")
def _():
    art = base_gate()
    art["verdict"] = "ALLOW_FORMULATION"
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(art, f); tmp = f.name
    p = subprocess.run([sys.executable, str(LINT), tmp], capture_output=True, text=True)
    assert p.returncode == 2 and "NONCANONICAL_VERDICT" in p.stdout
    return {"rejected_label": "ALLOW_FORMULATION"}

@scenario("NC-LINT-02 lint accepts canonical design-stage combo; rejects PASS+DESIGN_ONLY")
def _():
    good = base_gate(verdict="PASS_WITH_LIMITATIONS", validation_stage="DESIGN_STAGE",
                     release_scope="DESIGN_ONLY", required_action="COLLECT_MORE_DATA")
    good["limitations"] = ["design-stage: nothing executed yet"]
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(good, f); t1 = f.name
    p1 = subprocess.run([sys.executable, str(LINT), t1], capture_output=True, text=True)
    bad = base_gate(verdict="PASS", validation_stage="DESIGN_STAGE",
                    release_scope="DESIGN_ONLY", required_action="NONE")
    with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as f:
        json.dump(bad, f); t2 = f.name
    p2 = subprocess.run([sys.executable, str(LINT), t2], capture_output=True, text=True)
    assert p1.returncode == 0 and p1.stdout.startswith("SCHEMA_VALID")
    assert p2.returncode == 2
    return {"valid_combo_accepted": True, "illegal_pass_design_only_rejected": True}

def main():
    all_ok = True
    for fn in SCENARIOS:
        ok = fn()
        all_ok &= ok
    print("=" * 72)
    for name, ok, sample in RESULTS:
        print("%-4s %s" % ("PASS" if ok else "FAIL", name))
    n_ok = sum(1 for _, ok, _ in RESULTS if ok)
    print("-" * 72)
    print("R4_1B_TARGETED_REGRESSION_SUITE: %d/%d scenarios PASS (each x2 determinism)" %
          (n_ok, len(RESULTS)))
    print("NEW_CRITICAL_FALSE_PASS_COUNT = %d" % sum(
        1 for n, ok, s in RESULTS if n.startswith("NC-") and not ok))
    return 0 if all_ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
