"""Deterministic R2 validation authority, evidence binding, and revalidation rules."""

from __future__ import annotations

import copy
import hashlib
import json
import math
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"
CHECK_IDS = [
    "V01_MATHEMATICAL_CORRECTNESS", "V02_DATA_COMPATIBILITY", "V03_BASELINE_SUPERIORITY",
    "V04_OUT_OF_SAMPLE_VALIDITY", "V05_SENSITIVITY", "V06_ROBUSTNESS", "V07_UNCERTAINTY",
    "V08_INTERPRETABILITY_DOMAIN_SENSE", "V09_CONSTRAINT_SATISFACTION", "V10_FAILURE_ENVELOPE",
    "V11_STABILITY_ABLATION",
]
MANDATORY_CHECKS = {"V01_MATHEMATICAL_CORRECTNESS", "V02_DATA_COMPATIBILITY", "V03_BASELINE_SUPERIORITY", "V09_CONSTRAINT_SATISFACTION", "V10_FAILURE_ENVELOPE"}
NA_REASON_CODES = {
    "V04_OUT_OF_SAMPLE_VALIDITY": {"NO_EMPIRICAL_GENERALIZATION_CLAIM", "STRUCTURALLY_NOT_APPLICABLE"},
    "V05_SENSITIVITY": {"STRUCTURALLY_NOT_APPLICABLE"},
    "V06_ROBUSTNESS": {"STRUCTURALLY_NOT_APPLICABLE"},
    "V07_UNCERTAINTY": {"NO_DECISION_CHAIN", "STRUCTURALLY_NOT_APPLICABLE"},
    "V08_INTERPRETABILITY_DOMAIN_SENSE": {"NO_PARAMETER_OR_STATE_CLAIM", "STRUCTURALLY_NOT_APPLICABLE"},
    "V11_STABILITY_ABLATION": {"DETERMINISTIC_NO_RANDOMNESS", "NO_COMPLEX_COMPONENT", "STRUCTURALLY_NOT_APPLICABLE"},
}
UNSUPPORTED_PROSE = re.compile(
    r"(?i)^\s*(model performs well|residuals? (?:are )?small|parameters? (?:are )?stable|"
    r"no obvious anomalies|consistent with theory|looks reasonable|模型表现良好|残差较小|参数稳定|没有明显异常|与理论一致)\s*[.!。]?$"
)
PRESENTATION_STAGES = {"S5", "S6", "S7", "INTERPRETATION", "FIGURES", "PAPER_WRITING", "PAPER_REVIEW", "FINAL_RELEASE"}


class ValidationContractError(ValueError):
    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _load(name: str) -> dict[str, Any]:
    return json.loads((REFS / name).read_text(encoding="utf-8"))


PLAN_SCHEMA = _load("validation_plan.schema.v1.json")
EVIDENCE_SCHEMA = _load("validation_evidence.schema.v1.json")
FAILURE_SCHEMA = _load("failure_envelope.schema.v1.json")
REVISION_SCHEMA = _load("revision_record.schema.v1.json")
GATE_SCHEMA = _load("model_validation_gate.schema.v2.json")
MANIFEST_EXTENSION_SCHEMA = _load("model_validation_manifest_extension.schema.v2.json")


def canonical_hash(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validation_plan_hash(plan: dict[str, Any]) -> str:
    payload = {key: value for key, value in plan.items() if key != "plan_hash"}
    return canonical_hash(payload)


def register_validation_plan(plan: dict[str, Any], trusted_registry_root: Path) -> dict[str, Any]:
    """First-writer-wins plan registration for one orchestrator-controlled run root."""
    validate_plan(plan)
    trusted_registry_root.mkdir(parents=True, exist_ok=True)
    safe_name = re.sub(r"[^A-Za-z0-9._-]", "-", f"{plan['problem_id']}--{plan['model_id']}.json")
    path = trusted_registry_root / safe_name
    encoded = json.dumps(plan, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    try:
        with path.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
    except FileExistsError:
        existing = json.loads(path.read_text(encoding="utf-8"))
        if canonical_hash(existing) != canonical_hash(plan):
            raise ValidationContractError("VALIDATION_PLAN_CHANGED", "trusted plan registry is first-writer-wins")
    return {"path":str(path),"sha256":hashlib.sha256(path.read_bytes()).hexdigest(),"kind":"REGISTERED_VALIDATION_PLAN","plan_hash":plan["plan_hash"]}


def _validate_schema(value: dict[str, Any], schema: dict[str, Any], code: str) -> None:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(value), key=lambda e: list(e.absolute_path))
    if errors:
        error = errors[0]
        path = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
        raise ValidationContractError(code, f"{path}: {error.message}")


def _parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _resolve_json_pointer(document: Any, pointer: str) -> Any:
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current


def _verified_file(entry: dict[str, Any], label: str) -> Path:
    path = Path(entry.get("path", ""))
    if not path.is_file():
        raise ValidationContractError("ARTIFACT_MISSING", label)
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != entry.get("sha256"):
        raise ValidationContractError("ARTIFACT_HASH_MISMATCH", label)
    return path


def validate_upstream_artifacts(plan: dict[str, Any], artifact_index: dict[str, Any]) -> None:
    roles = {
        "@model": ("model_artifact_hash", "MODEL_ARTIFACT"),
        "@data": ("data_artifact_hash", "DATA_ARTIFACT"),
        "@candidate_portfolio": ("candidate_portfolio_hash", "CANDIDATE_PORTFOLIO"),
        "@selection_verdict": ("selection_verdict_hash", "SELECTION_VERDICT"),
    }
    for role, (hash_field, kind) in roles.items():
        entry = artifact_index.get(role)
        if not isinstance(entry, dict) or entry.get("kind") != kind:
            raise ValidationContractError("UPSTREAM_ARTIFACT_UNBOUND", role)
        _verified_file(entry, role)
        if entry["sha256"] != plan[hash_field]:
            raise ValidationContractError("UPSTREAM_ARTIFACT_UNBOUND", role)
    for baseline in plan["baselines"]:
        role = f"@baseline:{baseline['baseline_id']}"; entry = artifact_index.get(role)
        if not isinstance(entry, dict) or entry.get("kind") != "BASELINE_ARTIFACT":
            raise ValidationContractError("BASELINE_ARTIFACT_UNBOUND", role)
        _verified_file(entry, role)
        if entry["sha256"] != baseline["artifact_hash"]:
            raise ValidationContractError("BASELINE_ARTIFACT_UNBOUND", role)
    registered = artifact_index.get("@registered_plan")
    if not isinstance(registered, dict) or registered.get("kind") != "REGISTERED_VALIDATION_PLAN":
        raise ValidationContractError("PLAN_NOT_PREREGISTERED", plan["plan_hash"])
    registered_path = _verified_file(registered, "@registered_plan")
    registered_plan = json.loads(registered_path.read_text(encoding="utf-8"))
    if registered.get("plan_hash") != plan["plan_hash"] or canonical_hash(registered_plan) != canonical_hash(plan):
        raise ValidationContractError("VALIDATION_PLAN_CHANGED", "current plan differs from immutable registered plan")


def validate_plan(plan: dict[str, Any], *, temporal_problem: bool = False, grouped_problem: bool = False) -> dict[str, Any]:
    _validate_schema(plan, PLAN_SCHEMA, "INVALID_VALIDATION_PLAN")
    applicable = set(plan["applicable_checks"])
    na_ids = [item["check_id"] for item in plan["non_applicable_checks"]]
    if len(na_ids) != len(set(na_ids)) or applicable & set(na_ids) or applicable | set(na_ids) != set(CHECK_IDS):
        raise ValidationContractError("INVALID_APPLICABILITY_MATRIX", "11 checks must be partitioned exactly once")
    if not MANDATORY_CHECKS.issubset(applicable):
        raise ValidationContractError("MANDATORY_CHECK_NA", ",".join(sorted(MANDATORY_CHECKS - applicable)))
    for item in plan["non_applicable_checks"]:
        if item["reason_code"] not in NA_REASON_CODES.get(item["check_id"], set()):
            raise ValidationContractError("INVALID_NA_REASON", item["check_id"])
    if plan["plan_hash"] != validation_plan_hash(plan):
        raise ValidationContractError("VALIDATION_PLAN_HASH_MISMATCH", "plan_hash does not bind plan semantics")
    if "V03_BASELINE_SUPERIORITY" in applicable and not plan["baselines"]:
        raise ValidationContractError("BASELINE_MISSING", "V03 requires a preregistered baseline")
    split_types = {item["type"] for item in plan["data_splits"]}
    if temporal_problem and split_types & {"RANDOM", "STRATIFIED"}:
        raise ValidationContractError("REJECT_SPLIT", "temporal problems cannot use random/stratified validation as the release split")
    if grouped_problem and not split_types & {"GROUP", "EXTERNAL"}:
        raise ValidationContractError("REJECT_SPLIT", "group dependence requires group-aware or external holdout")
    if plan["identifiability_plan"]["applicable"] and not plan["identifiability_plan"]["methods"]:
        raise ValidationContractError("IDENTIFIABILITY_PLAN_MISSING", "applicable identifiability needs a preregistered method")
    if not plan["identifiability_plan"]["applicable"]:
        if plan["identifiability_plan"]["purpose"] != "NOT_APPLICABLE" or "not tested" in plan["identifiability_plan"]["rationale"].casefold():
            raise ValidationContractError("INVALID_IDENTIFIABILITY_NA", "N/A must be purpose-based, not untested")
    purposes = {item["purpose"] for item in plan["intended_claims"]}
    purpose_required_checks = set()
    if "PREDICTION" in purposes:
        purpose_required_checks |= {"V04_OUT_OF_SAMPLE_VALIDITY", "V05_SENSITIVITY", "V06_ROBUSTNESS", "V07_UNCERTAINTY", "V08_INTERPRETABILITY_DOMAIN_SENSE", "V11_STABILITY_ABLATION"}
    if "DECISION" in purposes:
        purpose_required_checks |= {"V05_SENSITIVITY", "V06_ROBUSTNESS", "V07_UNCERTAINTY", "V11_STABILITY_ABLATION"}
    if purposes & {"PARAMETER_INFERENCE", "STATE_RECONSTRUCTION", "MECHANISM_INTERPRETATION"}:
        purpose_required_checks |= {"V05_SENSITIVITY", "V06_ROBUSTNESS", "V07_UNCERTAINTY", "V08_INTERPRETABILITY_DOMAIN_SENSE"}
    if not purpose_required_checks.issubset(applicable):
        raise ValidationContractError("CLAIM_CONTRADICTS_NA", ",".join(sorted(purpose_required_checks - applicable)))
    ident_purpose = plan["identifiability_plan"]["purpose"]
    required_ident = purposes & {"PARAMETER_INFERENCE", "STATE_RECONSTRUCTION", "MECHANISM_INTERPRETATION"}
    if required_ident and (not plan["identifiability_plan"]["applicable"] or ident_purpose not in required_ident):
        raise ValidationContractError("IDENTIFIABILITY_PURPOSE_DOWNGRADE", ",".join(sorted(required_ident)))
    if purposes == {"PREDICTION"} and plan["identifiability_plan"]["applicable"] and ident_purpose != "PREDICTION_ONLY":
        raise ValidationContractError("IDENTIFIABILITY_PURPOSE_MISMATCH", ident_purpose)
    return plan


def compare_validation_plans(old: dict[str, Any], new: dict[str, Any], change_reason: str) -> dict[str, Any]:
    old_hash = validation_plan_hash(old); new_hash = validation_plan_hash(new)
    ignored = {"created_at", "plan_hash"}
    changed = sorted(key for key in set(old) | set(new) if key not in ignored and old.get(key) != new.get(key))
    substantive = bool(changed)
    return {
        "event": "VALIDATION_PLAN_CHANGED" if old_hash != new_hash else "VALIDATION_PLAN_UNCHANGED",
        "old_plan_hash": old_hash, "new_plan_hash": new_hash, "changed_fields": changed,
        "substantive": substantive, "change_reason": change_reason,
        "minimum_verdict": "REVISE" if substantive else "UNCHANGED",
    }


def validate_evidence(bundle: dict[str, Any], plan: dict[str, Any], artifact_index: dict[str, Any]) -> dict[str, Any]:
    validate_plan(plan)
    validate_upstream_artifacts(plan, artifact_index)
    _validate_schema(bundle, EVIDENCE_SCHEMA, "INVALID_EVIDENCE_BUNDLE")
    if bundle["problem_id"] != plan["problem_id"] or bundle["model_id"] != plan["model_id"]:
        raise ValidationContractError("ARTIFACT_LINK_MISMATCH", "plan and evidence identities differ")
    if bundle["validation_plan_hash"] != plan["plan_hash"]:
        raise ValidationContractError("STALE_VALIDATION_PLAN", "evidence is not bound to preregistered plan hash")
    ids: set[str] = set(); plan_time = _parse_time(plan["created_at"])
    applicable = set(plan["applicable_checks"])
    for record in bundle["evidence"]:
        if record["evidence_id"] in ids:
            raise ValidationContractError("DUPLICATE_EVIDENCE_ID", record["evidence_id"])
        ids.add(record["evidence_id"])
        if record["check_id"] not in applicable:
            raise ValidationContractError("EVIDENCE_FOR_NA_CHECK", record["check_id"])
        source = artifact_index.get(record["source_artifact"])
        if not isinstance(source, dict):
            raise ValidationContractError("UNBOUND_EVIDENCE", f"untyped artifact index entry for {record['source_artifact']}")
        if source.get("sha256") != record["artifact_sha256"]:
            raise ValidationContractError("UNBOUND_EVIDENCE", f"hash mismatch for {record['source_artifact']}")
        source_path = _verified_file(source, record["source_artifact"])
        if source.get("kind") not in {"VALIDATION_OUTPUT", "DIAGNOSTIC_OUTPUT", "TEST_LOG"}:
            raise ValidationContractError("UNBOUND_EVIDENCE", f"source is not an executed validation artifact: {record['source_artifact']}")
        if source.get("producer_stage") != record["producer_stage"]:
            raise ValidationContractError("UNBOUND_EVIDENCE", f"producer mismatch for {record['source_artifact']}")
        try:
            raw_document = json.loads(source_path.read_text(encoding="utf-8"))
            expected_inputs = {"model":plan["model_artifact_hash"],"data":plan["data_artifact_hash"],"candidate_portfolio":plan["candidate_portfolio_hash"],"selection_verdict":plan["selection_verdict_hash"],"validation_plan":plan["plan_hash"]}
            if raw_document.get("input_hashes") != expected_inputs or not raw_document.get("run_id") or not raw_document.get("producer_version") or not raw_document.get("command"):
                raise ValidationContractError("UNBOUND_EVIDENCE", f"diagnostic provenance missing or mismatched for {record['evidence_id']}")
            extracted = _resolve_json_pointer(raw_document, record["result_pointer"])
        except (OSError, UnicodeError, json.JSONDecodeError, KeyError, IndexError, ValueError, TypeError) as exc:
            raise ValidationContractError("UNBOUND_EVIDENCE", f"invalid result pointer for {record['evidence_id']}: {exc}") from exc
        if canonical_hash(extracted) != canonical_hash(record["observed_value"]):
            raise ValidationContractError("UNBOUND_EVIDENCE", f"observed value is not extracted from {record['source_artifact']}")
        if _parse_time(record["created_at"]) < plan_time:
            raise ValidationContractError("PRE_PLAN_EVIDENCE", record["evidence_id"])
        if isinstance(record["observed_value"], str) and UNSUPPORTED_PROSE.match(record["observed_value"]):
            raise ValidationContractError("UNBOUND_EVIDENCE", f"unsupported prose in {record['evidence_id']}")
        if not record["method"].strip() or not record["metric"].strip():
            raise ValidationContractError("UNBOUND_EVIDENCE", record["evidence_id"])
    return bundle


def validate_failure_envelope(envelope: dict[str, Any], plan: dict[str, Any]) -> dict[str, Any]:
    _validate_schema(envelope, FAILURE_SCHEMA, "INVALID_FAILURE_ENVELOPE")
    if envelope["problem_id"] != plan["problem_id"] or envelope["model_id"] != plan["model_id"]:
        raise ValidationContractError("FOREIGN_FAILURE_ENVELOPE", "failure envelope identity differs from plan")
    if envelope["model_artifact_hash"] != plan["model_artifact_hash"]:
        raise ValidationContractError("STALE_FAILURE_ENVELOPE", "failure envelope belongs to another model artifact")
    planned_ids = {item["test_id"] for item in plan["failure_tests"]}
    envelope_ids = {item["test_id"] for item in envelope["failures"]}
    if planned_ids != envelope_ids:
        raise ValidationContractError("FAILURE_TEST_MAPPING_MISMATCH", "envelope must cover every registered failure test exactly")
    for item in envelope["failures"]:
        if item["test_status"] == "NOT_TESTED" and re.search(r"(?i)no failure found|没有发现失败", item["observable_signature"]):
            raise ValidationContractError("UNTESTED_FAILURE_CLAIM", item["failure_id"])
    return envelope


def _records(bundle: dict[str, Any], check_id: str) -> list[dict[str, Any]]:
    return [item for item in bundle["evidence"] if item["check_id"] == check_id]


def _dict_values(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    return [item["observed_value"] for item in records if isinstance(item["observed_value"], dict)]


def derive_check(check_id: str, records: list[dict[str, Any]], plan: dict[str, Any], envelope: dict[str, Any]) -> dict[str, str | bool]:
    """Derive a check outcome; declared evidence status cannot override hard facts."""
    if not records:
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"No artifact-bound evidence"}
    values = _dict_values(records)
    if not values:
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Observed evidence is not structured"}
    required_facts = {
        "V01_MATHEMATICAL_CORRECTNESS": {"mathematical_validity", "hard_constraint_satisfied"},
        "V02_DATA_COMPATIBILITY": {"data_leakage", "information_boundary_verified", "sampling_compatible"},
        "V03_BASELINE_SUPERIORITY": {"comparison_type", "baseline_id", "baseline_artifact_hash", "metric_id", "primary_metric", "baseline_metric", "uncertainty_supports_materiality", "same_information_set", "same_split", "same_target", "same_loss", "same_constraints", "same_horizon", "primary_worse", "primary_more_complex", "material_improvement"},
        "V04_OUT_OF_SAMPLE_VALIDITY": {"split_type", "dependence_structure_matched", "underpowered"},
        "V05_SENSITIVITY": {"decision_reversal", "decision_risk", "perturbation_basis_verified"},
        "V06_ROBUSTNESS": {"shared_bias", "same_estimand", "independent_assumptions_reviewed"},
        "V07_UNCERTAINTY": {"decision_chain", "uncertainty_propagated"},
        "V08_INTERPRETABILITY_DOMAIN_SENSE": {"identifiable", "observable", "prediction_stable"},
        "V09_CONSTRAINT_SATISFACTION": {"hard_constraint_satisfied"},
        "V10_FAILURE_ENVELOPE": {"failure_tests_executed", "executed_test_ids"},
        "V11_STABILITY_ABLATION": {"decision_reversal_across_seeds", "complex_component_material_contribution"},
    }
    if not any(required_facts[check_id].issubset(value) for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Required structured facts are missing"}
    boolean_facts = {
        "V01_MATHEMATICAL_CORRECTNESS": {"mathematical_validity", "hard_constraint_satisfied"},
        "V02_DATA_COMPATIBILITY": {"data_leakage", "information_boundary_verified", "sampling_compatible"},
        "V03_BASELINE_SUPERIORITY": {"uncertainty_supports_materiality", "same_information_set", "same_split", "same_target", "same_loss", "same_constraints", "same_horizon", "primary_worse", "primary_more_complex", "material_improvement"},
        "V04_OUT_OF_SAMPLE_VALIDITY": {"dependence_structure_matched", "underpowered"},
        "V05_SENSITIVITY": {"decision_reversal", "perturbation_basis_verified"},
        "V06_ROBUSTNESS": {"shared_bias", "same_estimand", "independent_assumptions_reviewed"},
        "V07_UNCERTAINTY": {"decision_chain", "uncertainty_propagated"},
        "V08_INTERPRETABILITY_DOMAIN_SENSE": {"identifiable", "observable", "prediction_stable"},
        "V09_CONSTRAINT_SATISFACTION": {"hard_constraint_satisfied"},
        "V10_FAILURE_ENVELOPE": {"failure_tests_executed"},
        "V11_STABILITY_ABLATION": {"decision_reversal_across_seeds", "complex_component_material_contribution"},
    }
    for value in values:
        if any(type(value.get(key)) is not bool for key in boolean_facts[check_id]):
            failure_class = "STRUCTURAL" if check_id in {"V01_MATHEMATICAL_CORRECTNESS", "V02_DATA_COMPATIBILITY", "V09_CONSTRAINT_SATISFACTION"} else "CORRECTABLE"
            return {"status":"FAIL", "blocking":True, "failure_class":failure_class, "severity":"CRITICAL" if failure_class == "STRUCTURAL" else "HIGH", "reason":"Required facts must use strict boolean types"}
    declared_fail = any(item["status"] == "FAIL" for item in records)
    declared_warn = any(item["status"] == "WARN" for item in records)
    if check_id == "V02_DATA_COMPATIBILITY" and any(value.get("data_leakage") is True for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"STRUCTURAL", "severity":"CRITICAL", "reason":"Data leakage detected"}
    if check_id == "V02_DATA_COMPATIBILITY" and any(value.get("information_boundary_verified") is not True or value.get("sampling_compatible") is not True for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Data information boundary or sampling compatibility is unverified"}
    if check_id == "V03_BASELINE_SUPERIORITY":
        comparisons = [value for value in values if value.get("comparison_type") == "BASELINE_SUPERIORITY"]
        if not comparisons:
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Baseline comparison absent"}
        baseline_index = {item["baseline_id"]: item for item in plan["baselines"]}
        metric_index = {item["metric_id"]: item for item in plan["metrics"]}
        for comparison in sorted(comparisons, key=lambda item: (str(item.get("baseline_id")), str(item.get("metric_id")))):
            baseline = baseline_index.get(comparison.get("baseline_id")); metric = metric_index.get(comparison.get("metric_id"))
            if baseline is None or comparison.get("baseline_artifact_hash") != baseline["artifact_hash"] or metric is None:
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Baseline comparison is not bound to the preregistered baseline/metric"}
            same_basis = all(comparison.get(key) is True for key in ("same_information_set","same_split","same_target","same_loss","same_constraints","same_horizon"))
            if not same_basis:
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Baseline evaluated on a different basis"}
            primary, base = comparison.get("primary_metric"), comparison.get("baseline_metric")
            if not isinstance(primary, (int, float)) or isinstance(primary, bool) or not isinstance(base, (int, float)) or isinstance(base, bool):
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Baseline raw metrics are missing"}
            direction = metric["direction"]; threshold = baseline["smallest_effect_of_practical_interest"]
            if metric["practical_threshold"] != threshold:
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Metric and baseline materiality thresholds disagree"}
            improvement = (base - primary) if direction == "LOWER_BETTER" else (primary - base) if direction == "HIGHER_BETTER" else None
            if improvement is None or not all(math.isfinite(float(item)) for item in (primary, base)):
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Baseline direction or raw metric is invalid"}
            computed_worse = improvement < 0
            if comparison.get("primary_worse") is not computed_worse:
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Declared baseline ordering contradicts raw metrics"}
            material = isinstance(threshold, (int, float)) and not isinstance(threshold, bool) and improvement >= threshold and comparison.get("uncertainty_supports_materiality") is True
            if computed_worse:
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Primary is inferior to baseline"}
            if comparison.get("primary_more_complex") is True and not material:
                return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Complexity not justified by computed preregistered material benefit"}
    if check_id == "V04_OUT_OF_SAMPLE_VALIDITY":
        if any(value.get("dependence_structure_matched") is not True for value in values):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Validation split does not match dependence structure"}
        if any(value.get("temporal_problem") is True and value.get("split_type") in {"RANDOM_KFOLD","RANDOM","STRATIFIED"} for value in values):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Random split invalid for temporal data"}
        if any(value.get("underpowered") is True for value in values):
            return {"status":"WARN", "blocking":False, "failure_class":"NONE", "severity":"MEDIUM", "reason":"Generalization evidence is underpowered"}
    if check_id == "V05_SENSITIVITY" and any(value.get("decision_reversal") is True for value in values):
        high = any(value.get("decision_risk") in {"HIGH","CRITICAL"} for value in values)
        return {"status":"FAIL" if high else "WARN", "blocking":high, "failure_class":"CORRECTABLE" if high else "NONE", "severity":"HIGH" if high else "MEDIUM", "reason":"Plausible perturbation reverses the decision"}
    if check_id == "V05_SENSITIVITY" and any(value.get("perturbation_basis_verified") is not True for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Perturbation range lacks a registered evidence basis"}
    if check_id == "V06_ROBUSTNESS" and any(value.get("shared_bias") is True or value.get("same_estimand") is False for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"STRUCTURAL", "severity":"HIGH", "reason":"Agreement is invalid because bias/estimand is shared or mismatched"}
    if check_id == "V06_ROBUSTNESS" and any(value.get("independent_assumptions_reviewed") is not True for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Robustness evidence did not audit shared assumptions"}
    if check_id == "V07_UNCERTAINTY" and any(value.get("decision_chain") is True and value.get("uncertainty_propagated") is not True for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Uncertainty was not propagated to decision"}
    if check_id in {"V01_MATHEMATICAL_CORRECTNESS","V09_CONSTRAINT_SATISFACTION"} and any(value.get("hard_constraint_satisfied") is not True or (check_id == "V01_MATHEMATICAL_CORRECTNESS" and value.get("mathematical_validity") is not True) for value in values):
        return {"status":"FAIL", "blocking":True, "failure_class":"STRUCTURAL", "severity":"CRITICAL", "reason":"Mathematical or hard-constraint failure"}
    if check_id == "V10_FAILURE_ENVELOPE":
        if any(value.get("failure_tests_executed") is not True for value in values):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Registered failure tests were not executed"}
        planned_ids = {item["test_id"] for item in plan["failure_tests"]}
        if any(set(value.get("executed_test_ids", [])) != planned_ids for value in values):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Executed failure-test IDs do not match the preregistered set"}
        if not envelope["failures"] or all(item["test_status"] == "NOT_TESTED" for item in envelope["failures"]):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Failure envelope was not exercised"}
    if check_id == "V11_STABILITY_ABLATION":
        if any(value.get("decision_reversal_across_seeds") is True for value in values):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Seed instability reverses conclusion"}
        if any(value.get("complex_component_material_contribution") is False for value in values):
            return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"MEDIUM", "reason":"Ablation does not justify complex component"}
    if declared_fail:
        return {"status":"FAIL", "blocking":True, "failure_class":"CORRECTABLE", "severity":"HIGH", "reason":"Bound evidence failed"}
    if declared_warn:
        return {"status":"WARN", "blocking":False, "failure_class":"NONE", "severity":"MEDIUM", "reason":"Bound evidence warns"}
    return {"status":"PASS", "blocking":False, "failure_class":"NONE", "severity":"INFO", "reason":"Bound evidence passed declared test"}


def derive_identifiability(plan: dict[str, Any], bundle: dict[str, Any]) -> dict[str, Any]:
    spec = plan["identifiability_plan"]
    if not spec["applicable"]:
        return {"applicable":False,"purpose":"NOT_APPLICABLE","status":"NA","methods":[],"evidence_ids":[],"rationale":spec["rationale"],"claim_restrictions":[]}
    records = _records(bundle, "V08_INTERPRETABILITY_DOMAIN_SENSE")
    relevant = [item for item in records if isinstance(item["observed_value"], dict) and "identifiable" in item["observed_value"]]
    if not relevant:
        return {"applicable":True,"purpose":spec["purpose"],"status":"FAIL","methods":spec["methods"],"evidence_ids":[],"rationale":"No artifact-bound identifiability or observability evidence was produced.","claim_restrictions":[]}
    identifiable = all(item["observed_value"].get("identifiable") is True for item in relevant)
    observable = all(item["observed_value"].get("observable", True) is True for item in relevant)
    ids = [item["evidence_id"] for item in relevant]
    if identifiable and observable:
        return {"applicable":True,"purpose":spec["purpose"],"status":"PASS","methods":spec["methods"],"evidence_ids":ids,"rationale":"Registered recovery/rank evidence supports the required claim.","claim_restrictions":[]}
    if spec["purpose"] == "PREDICTION_ONLY" and all(item["observed_value"].get("prediction_stable") is True for item in relevant):
        return {"applicable":True,"purpose":spec["purpose"],"status":"WARN","methods":spec["methods"],"evidence_ids":ids,"rationale":"Prediction is stable although parameters are not uniquely identified.","claim_restrictions":["Do not interpret or report unique parameter mechanisms."]}
    return {"applicable":True,"purpose":spec["purpose"],"status":"FAIL","methods":spec["methods"],"evidence_ids":ids,"rationale":"Required parameters or latent states are not identifiable/observable.","claim_restrictions":["Do not make the requested parameter/state interpretation claim."]}


def _revision_token(problem_id: str, model_id: str, sequence: int, seed: str) -> str:
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:10]
    safe = re.sub(r"[^A-Za-z0-9._-]", "-", f"{problem_id}-{model_id}-{sequence}-{digest}")
    return f"R2REV-{safe}"


def aggregate(plan: dict[str, Any], bundle: dict[str, Any], envelope: dict[str, Any], *, revision_sequence: int = 1) -> dict[str, Any]:
    applicable = set(plan["applicable_checks"]); na = {item["check_id"]:item["rationale"] for item in plan["non_applicable_checks"]}
    checks = []
    for check_id in CHECK_IDS:
        if check_id not in applicable:
            checks.append({"check_id":check_id,"applicable":False,"status":"NA","evidence_ids":[],"rationale":na[check_id],"blocking":False,"severity":"INFO","failure_class":"NONE"})
            continue
        records = _records(bundle, check_id); result = derive_check(check_id, records, plan, envelope)
        checks.append({"check_id":check_id,"applicable":True,"status":result["status"],"evidence_ids":[item["evidence_id"] for item in records],"rationale":result["reason"],"blocking":result["blocking"],"severity":result["severity"],"failure_class":result["failure_class"]})
    ident = derive_identifiability(plan, bundle)
    if ident["applicable"]:
        v08 = next(item for item in checks if item["check_id"] == "V08_INTERPRETABILITY_DOMAIN_SENSE")
        if ident["status"] == "FAIL": v08.update(status="FAIL", blocking=True, severity="CRITICAL", failure_class="STRUCTURAL", rationale=ident["rationale"])
        elif ident["status"] == "WARN" and v08["status"] == "PASS": v08.update(status="WARN", blocking=False, severity="HIGH", rationale=ident["rationale"])
    structural = [item for item in checks if item["status"] == "FAIL" and item["blocking"] and item["failure_class"] == "STRUCTURAL"]
    correctable = [item for item in checks if item["status"] == "FAIL" and item["blocking"] and item["failure_class"] == "CORRECTABLE"]
    nonblocking = [item for item in checks if item["status"] in {"WARN","FAIL"} and not item["blocking"]]
    restrictions = list(ident["claim_restrictions"])
    if structural:
        verdict, action, owner = "FAIL", "REJECT_MODEL", "MODEL_VALIDATION"
    elif correctable:
        verdict, action, owner = "REVISE", "RERUN_VALIDATION", "MODEL_VALIDATION"
    elif nonblocking:
        verdict, action, owner = "PASS_WITH_LIMITATIONS", "NONE", "MODEL_VALIDATION"
        restrictions.extend(item["rationale"] for item in nonblocking)
    else:
        verdict, action, owner = "PASS", "NONE", "MODEL_VALIDATION"
    token = _revision_token(plan["problem_id"], plan["model_id"], revision_sequence, plan["plan_hash"] + verdict) if verdict in {"REVISE","FAIL"} else None
    return {"checks":checks,"identifiability_observability":ident,"verdict":verdict,"blocking_failures":[item["check_id"] for item in structural+correctable],"limitations":[item["rationale"] for item in nonblocking],"claim_restrictions":list(dict.fromkeys(restrictions)),"required_action":action,"owner_stage":owner,"revision_token":token,"revalidation_required":verdict in {"REVISE","FAIL"}}


def validate_gate(gate: dict[str, Any], plan: dict[str, Any], bundle: dict[str, Any], envelope: dict[str, Any], artifact_index: dict[str, Any]) -> dict[str, Any]:
    validate_plan(plan); validate_evidence(bundle, plan, artifact_index); validate_failure_envelope(envelope, plan)
    _validate_schema(gate, GATE_SCHEMA, "INVALID_MODEL_VALIDATION_GATE")
    if gate["problem_id"] != plan["problem_id"] or gate["model_id"] != plan["model_id"]:
        raise ValidationContractError("GATE_IDENTITY_MISMATCH", "gate identity does not match validation plan")
    expected_hashes = {
        "model":plan["model_artifact_hash"],"data":plan["data_artifact_hash"],"candidate_portfolio":plan["candidate_portfolio_hash"],"selection_verdict":plan["selection_verdict_hash"],
        "validation_plan":canonical_hash(plan),"evidence_bundle":canonical_hash(bundle),"failure_envelope":canonical_hash(envelope),
    }
    if gate["artifact_hashes"] != expected_hashes or gate["validation_plan_hash"] != plan["plan_hash"]:
        raise ValidationContractError("STALE_VALIDATION_EVIDENCE", "gate hash chain does not bind current artifacts")
    expected = aggregate(plan, bundle, envelope, revision_sequence=gate["revision_sequence"])
    fields = ("checks","identifiability_observability","verdict","blocking_failures","limitations","claim_restrictions","required_action","owner_stage","revalidation_required")
    for field in fields:
        if gate[field] != expected[field]:
            raise ValidationContractError("INCONSISTENT_AGGREGATION", f"{field} differs from deterministic result")
    if expected["verdict"] in {"REVISE","FAIL"}:
        if gate["revision_token"] != expected["revision_token"]:
            raise ValidationContractError("REVISION_TOKEN_MISMATCH", expected["verdict"])
    elif gate["revision_token"] is not None:
        raise ValidationContractError("UNEXPECTED_REVISION_TOKEN", expected["verdict"])
    return gate


REVALIDATION_MAP = {
    "PRESENTATION_ONLY": [],
    "DATA_SPLIT": ["V02_DATA_COMPATIBILITY","V03_BASELINE_SUPERIORITY","V04_OUT_OF_SAMPLE_VALIDITY","V11_STABILITY_ABLATION"],
    "OBJECTIVE": ["V01_MATHEMATICAL_CORRECTNESS","V03_BASELINE_SUPERIORITY","V05_SENSITIVITY","V06_ROBUSTNESS","V09_CONSTRAINT_SATISFACTION","V10_FAILURE_ENVELOPE"],
    "MODEL_EQUATION": [item for item in CHECK_IDS if item != "V02_DATA_COMPATIBILITY"],
    "FEATURE_SET": ["V02_DATA_COMPATIBILITY","V03_BASELINE_SUPERIORITY","V04_OUT_OF_SAMPLE_VALIDITY","V05_SENSITIVITY","V06_ROBUSTNESS","V07_UNCERTAINTY","V11_STABILITY_ABLATION"],
    "SOLVER": ["V01_MATHEMATICAL_CORRECTNESS","V05_SENSITIVITY","V06_ROBUSTNESS","V09_CONSTRAINT_SATISFACTION","V11_STABILITY_ABLATION"],
    "PARAMETER_ESTIMATION": ["V01_MATHEMATICAL_CORRECTNESS","V04_OUT_OF_SAMPLE_VALIDITY","V05_SENSITIVITY","V06_ROBUSTNESS","V07_UNCERTAINTY","V08_INTERPRETABILITY_DOMAIN_SENSE","V11_STABILITY_ABLATION"],
    "VALIDATION_PLAN": CHECK_IDS,
}


def required_revalidation(change_type: str, old_hash: str, new_hash: str) -> dict[str, Any]:
    if change_type not in REVALIDATION_MAP:
        raise ValidationContractError("UNKNOWN_CHANGE_TYPE", change_type)
    if old_hash == new_hash:
        return {"artifact_changed":False,"stale_checks":[],"revalidation_required":False,"status":"CURRENT"}
    checks = REVALIDATION_MAP[change_type]
    return {"artifact_changed":True,"stale_checks":checks,"revalidation_required":bool(checks),"status":"STALE" if checks else "NO_MODEL_REVALIDATION_REQUIRED"}


def make_revision_record(*, problem_id: str, model_id: str, sequence: int, old_hash: str, new_hash: str | None, failed_checks: list[str], actions: list[str], owner_stage: str, change_type: str, summary: str, plan_changes: list[str]) -> dict[str, Any]:
    seed = old_hash + (new_hash or "pending") + change_type + str(sequence)
    token = _revision_token(problem_id, model_id, sequence, seed)
    revalidation = required_revalidation(change_type, old_hash, new_hash or old_hash)
    record = {"schema_version":"revision_record.schema.v1","revision_sequence":sequence,"revision_token":token,"problem_id":problem_id,"model_id":model_id,"old_artifact_hash":old_hash,"failed_checks":failed_checks,"required_actions":actions,"owner_stage":owner_stage,"new_artifact_hash":new_hash,"change_type":change_type,"change_summary":summary,"validation_plan_changes":plan_changes,"revalidation_checks":revalidation["stale_checks"],"revalidation_status":"PENDING","created_at":"2026-08-24T00:00:00+08:00"}
    _validate_schema(record, REVISION_SCHEMA, "INVALID_REVISION_RECORD")
    return record


def downstream_transition(
    gate: dict[str, Any], requested_stage: str, acknowledged_restrictions: list[str] | None = None, *,
    plan: dict[str, Any], bundle: dict[str, Any], envelope: dict[str, Any], artifact_index: dict[str, Any], claim_artifacts: dict[str, Any] | None = None,
) -> str:
    validate_gate(gate, plan, bundle, envelope, artifact_index)
    if requested_stage not in PRESENTATION_STAGES:
        return "ALLOW_NON_PRESENTATION_TRANSITION"
    if gate["verdict"] in {"REVISE","FAIL"}:
        raise ValidationContractError("DOWNSTREAM_BLOCKED", gate["verdict"])
    if gate["verdict"] == "PASS_WITH_LIMITATIONS":
        if set(gate["claim_restrictions"]) != set(acknowledged_restrictions or []):
            raise ValidationContractError("CLAIM_RESTRICTIONS_NOT_PROPAGATED", requested_stage)
        if requested_stage == "FINAL_RELEASE":
            validate_downstream_claim_artifacts(gate, claim_artifacts or {})
    return "ALLOW_DOWNSTREAM"


def validate_downstream_claim_artifacts(gate: dict[str, Any], claim_artifacts: dict[str, Any]) -> None:
    if gate["verdict"] != "PASS_WITH_LIMITATIONS":
        return
    required_roles = {"FIGURE_CAPTIONS", "ABSTRACT", "PAPER_BODY", "CONCLUSION", "REVIEW_HANDOFF"}
    if set(claim_artifacts) != required_roles:
        raise ValidationContractError("CLAIM_ARTIFACTS_INCOMPLETE", ",".join(sorted(required_roles - set(claim_artifacts))))
    for role, entry in claim_artifacts.items():
        path = _verified_file(entry, role)
        content = path.read_text(encoding="utf-8")
        missing = [restriction for restriction in gate["claim_restrictions"] if restriction not in content]
        if missing:
            raise ValidationContractError("CLAIM_RESTRICTIONS_NOT_PROPAGATED", f"{role}: {missing[0]}")


def validate_manifest_extension(payload: dict[str, Any], artifact_index: dict[str, Any]) -> dict[str, Any]:
    """Validate S4 completion and release authorization as separate state."""
    _validate_schema(payload, MANIFEST_EXTENSION_SCHEMA, "INVALID_MODEL_VALIDATION_MANIFEST")
    plan = payload["validation_plan"]
    bundle = payload["evidence_bundle"]
    envelope = payload["failure_envelope"]
    gate = payload["model_validation_gate"]
    validate_gate(gate, plan, bundle, envelope, artifact_index)
    if payload["release_status"] != gate["verdict"]:
        raise ValidationContractError("MANIFEST_GATE_MISMATCH", "release_status differs from signed gate")
    authorization = payload.get("downstream_authorization", {"allowed_stages": [], "claim_restrictions_acknowledged": []})
    allowed = set(authorization["allowed_stages"])
    acknowledged = authorization["claim_restrictions_acknowledged"]
    if payload["execution_status"] != "completed" and allowed:
        raise ValidationContractError("EXECUTION_NOT_COMPLETE", "incomplete S4 cannot release downstream")
    if gate["verdict"] in {"REVISE", "FAIL"} and allowed:
        raise ValidationContractError("DOWNSTREAM_BLOCKED", gate["verdict"])
    if gate["verdict"] in {"PASS", "PASS_WITH_LIMITATIONS"}:
        if allowed != {"S5", "S6", "S7"}:
            raise ValidationContractError("INCOMPLETE_DOWNSTREAM_AUTHORIZATION", gate["verdict"])
        for stage in allowed:
            downstream_transition(gate, stage, acknowledged, plan=plan, bundle=bundle, envelope=envelope, artifact_index=artifact_index)
    return payload


def build_gate(plan: dict[str, Any], bundle: dict[str, Any], envelope: dict[str, Any], artifact_index: dict[str, Any], *, revision_sequence: int = 1, created_at: str = "2026-08-24T00:10:00+08:00") -> dict[str, Any]:
    validate_evidence(bundle, plan, artifact_index); validate_failure_envelope(envelope, plan)
    result = aggregate(plan, bundle, envelope, revision_sequence=revision_sequence)
    return {"schema_version":"model_validation_gate.schema.v2","gate":"MODEL_VALIDATION_GATE","problem_id":plan["problem_id"],"model_id":plan["model_id"],"artifact_hashes":{"model":plan["model_artifact_hash"],"data":plan["data_artifact_hash"],"candidate_portfolio":plan["candidate_portfolio_hash"],"selection_verdict":plan["selection_verdict_hash"],"validation_plan":canonical_hash(plan),"evidence_bundle":canonical_hash(bundle),"failure_envelope":canonical_hash(envelope)},"validation_plan_hash":plan["plan_hash"],"revision_sequence":revision_sequence,**result,"validator_version":"R2_VALIDATOR.v1","created_at":created_at}
