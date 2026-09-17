#!/usr/bin/env python3
"""R4.1-B artifact lint (B7). Exit 0 = valid; exit 2 = SCHEMA_INVALID (write must be rejected).

Usage: python lint_validation_artifact.py <artifact.json>
Checks: canonical verdict enum; required_action enum; release_scope enum;
validation_stage enum; per-check applicability_reason_code presence & enum;
coherence matrix (verdict x scope x action); material-sensitivity propagation.
No case identifiers; generic for any modeling artifact.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from validation_stage_semantics import (
    CANONICAL_VERDICTS, REQUIRED_ACTIONS, RELEASE_SCOPES, VALIDATION_STAGES,
    GATE_IDS, check_coherence,
)

APPLICABILITY_REASON_CODES = {
    "EXECUTED_EMPIRICAL_PIPELINE_PRESENT", "DESIGN_STAGE_NO_OBSERVED_DATA",
    "DESIGN_STAGE_NO_EXECUTED_BASELINE", "DESIGN_STAGE_NO_EMPIRICAL_MODEL",
    "DESIGN_STAGE_NO_INDEPENDENT_ESTIMAND_TEST", "DETERMINISTIC_DESIGN_NO_UNCERTAINTY_CLAIM",
    "DESIGN_STAGE_NO_FITTED_COMPONENT", "CLAIM_HAS_NO_IDENTIFICATION_MEANING",
    "CLAIM_SCOPE_EXCLUDES_GENERALIZATION", "REGISTERED_PLAN_MARKS_NOT_APPLICABLE",
}


def lint(artifact: dict):
    errors = []

    def err(code, detail=""):
        errors.append("SCHEMA_INVALID %s %s" % (code, detail))

    verdict = artifact.get("verdict")
    action = artifact.get("required_action")
    scope = artifact.get("release_scope")
    stage = artifact.get("validation_stage")

    # v2-compat artifacts may omit release_scope/validation_stage; treat as legacy-empirical
    if stage is None and scope is None:
        stage, scope = "EMPIRICAL_STAGE", ("FULL" if verdict == "PASS" else "NONE")
        artifact = dict(artifact)
        artifact["validation_stage"], artifact["release_scope"] = stage, scope

    if verdict not in CANONICAL_VERDICTS:
        err("NONCANONICAL_VERDICT", repr(verdict))
    if action is not None and action not in REQUIRED_ACTIONS:
        err("INVALID_REQUIRED_ACTION", repr(action))
    if scope not in RELEASE_SCOPES:
        err("INVALID_RELEASE_SCOPE", repr(scope))
    if stage not in VALIDATION_STAGES:
        err("INVALID_VALIDATION_STAGE", repr(stage))

    checks = artifact.get("checks")
    if isinstance(checks, list):
        ids_seen = set()
        for c in checks:
            cid = c.get("check_id")
            ids_seen.add(cid)
            if cid in GATE_IDS and "applicable" in c:
                code = c.get("applicability_reason_code") or c.get("applicability_reason")
                if not code:
                    err("MISSING_APPLICABILITY_REASON", str(cid))
                elif code not in APPLICABILITY_REASON_CODES:
                    err("UNKNOWN_APPLICABILITY_REASON", "%s:%s" % (cid, code))
            else:
                err("MALFORMED_CHECK", repr(cid))
        missing = [g for g in GATE_IDS if g not in ids_seen]
        if missing:
            err("MISSING_GATES", ",".join(missing))

    ms = artifact.get("material_sensitivity") or {}
    reversal = bool(ms.get("present")) and bool(ms.get("material_to_conclusion"))
    limits = artifact.get("limitations") or []
    v = check_coherence(verdict if verdict in CANONICAL_VERDICTS else "?",
                        action or "NONE", scope, limits, stage,
                        material_reversal_present=reversal,
                        claims_empirical_performance_under_design=False)
    for code, detail in v:
        err(code, str(detail))
    return errors


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 1
    path = Path(argv[1])
    try:
        artifact = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # unreadable artifact can never pass a write gate
        print("SCHEMA_INVALID UNREADABLE_ARTIFACT %s" % exc)
        return 2
    errors = lint(artifact)
    if errors:
        for e in errors:
            print(e)
        print("ARTIFACT_WRITE_REJECTED (%d violation(s))" % len(errors))
        return 2
    print("SCHEMA_VALID %s" % path.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
