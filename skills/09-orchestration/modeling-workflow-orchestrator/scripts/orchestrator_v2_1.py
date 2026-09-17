#!/usr/bin/env python3
"""CUMCM unified control plane V2.1 (state-machine only, fail closed).

The control plane does not choose, formulate, solve, or scientifically validate
models.  It dispatches the validator named by the canonical artifact registry,
records a signed validation receipt, verifies dependency freshness, and permits
only registry-declared transitions.

Commands:
  init <workflow_dir> <workflow_id>
  reg <workflow_dir> <artifact_id> <path>
  adv <workflow_dir>
  check <workflow_dir>
  route <workflow_dir> <exact_reason_code>
  resume <workflow_dir>
  migrate <workflow_dir>
  close <workflow_dir>
  status <workflow_dir>

Exit codes: 0 success; 1 blocked; 2 input/integrity/contract error.
"""
from __future__ import annotations

import hashlib
import hmac
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


OK, BLOCKED, INPUT = 0, 1, 2
HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SKILLS = ROOT.parent
SCHEMAS = ROOT / "schemas"
REFERENCES = ROOT / "references"
ARTIFACT_REGISTRY_PATH = REFERENCES / "canonical_artifact_registry.v2_1.json"
TRANSITION_REGISTRY_PATH = REFERENCES / "v2_1_transition_registry.json"
REASON_REGISTRY_PATH = REFERENCES / "v2_1_reason_registry.json"
DAG_PATH = REFERENCES / "artifact_invalidation_dag.v2_1.json"
STATE_SCHEMA_PATH = SCHEMAS / "workflow_state.schema.v2_1.json"
RECEIPT_SCHEMA_PATH = SCHEMAS / "artifact_validation_receipt.schema.v1.json"
ZERO_HASH = "0" * 64


class ControlPlaneError(RuntimeError):
    def __init__(self, code: str, detail: str, exit_code: int = INPUT):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.exit_code = exit_code


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def canonical_hash(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def source_sha256(path: Path) -> str:
    if path.is_file():
        return file_sha256(path)
    if path.is_dir():
        digest = hashlib.sha256()
        files = sorted(item for item in path.rglob("*") if item.is_file() and "__pycache__" not in item.parts)
        if not files:
            raise ControlPlaneError("VALIDATOR_SOURCE_MISSING", str(path))
        for item in files:
            digest.update(item.relative_to(path).as_posix().encode("utf-8"))
            digest.update(file_sha256(item).encode("ascii"))
        return digest.hexdigest()
    raise ControlPlaneError("VALIDATOR_SOURCE_MISSING", str(path))


def load_json(path: Path, code: str = "INVALID_JSON") -> dict[str, Any] | list[Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ControlPlaneError(code, f"{path}: {exc}") from exc
    if not isinstance(value, (dict, list)):
        raise ControlPlaneError(code, f"{path}: top level must be object or array")
    return value


def atomic_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def validate_schema(value: Any, schema: dict[str, Any], code: str) -> None:
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda item: list(item.absolute_path),
    )
    if errors:
        error = errors[0]
        location = "$" + "".join(f"[{part!r}]" for part in error.absolute_path)
        raise ControlPlaneError(code, f"{location}: {error.message}")


def project_root(workflow_dir: Path) -> Path:
    configured = os.environ.get("CUMCM_PROJECT_ROOT")
    if configured:
        return Path(configured).resolve()
    candidates = [Path.cwd().resolve(), workflow_dir.resolve(), *workflow_dir.resolve().parents]
    for candidate in candidates:
        if (candidate / "submission_governance").exists() and (candidate / "reports").exists():
            return candidate
    return Path.cwd().resolve()


def resolve_token(value: str, workflow_dir: Path) -> Path:
    if value.startswith("$LOCAL/"):
        return (SCHEMAS / value[len("$LOCAL/"):]).resolve()
    if value.startswith("$SKILLS/"):
        return (SKILLS / value[len("$SKILLS/"):]).resolve()
    if value.startswith("$PROJECT/"):
        return (project_root(workflow_dir) / value[len("$PROJECT/"):]).resolve()
    return Path(value).resolve()


def load_schema_ref(reference: str, workflow_dir: Path) -> dict[str, Any]:
    path_part, _, fragment = reference.partition("#")
    schema: Any = load_json(resolve_token(path_part, workflow_dir), "SCHEMA_UNREADABLE")
    if fragment:
        if not fragment.startswith("/"):
            raise ControlPlaneError("SCHEMA_REFERENCE_INVALID", reference)
        for raw in fragment.split("/")[1:]:
            token = raw.replace("~1", "/").replace("~0", "~")
            if not isinstance(schema, dict) or token not in schema:
                raise ControlPlaneError("SCHEMA_REFERENCE_INVALID", reference)
            schema = schema[token]
    if not isinstance(schema, dict):
        raise ControlPlaneError("SCHEMA_REFERENCE_INVALID", reference)
    return schema


def registry() -> dict[str, Any]:
    value = load_json(ARTIFACT_REGISTRY_PATH, "REGISTRY_INVALID")
    if not isinstance(value, dict) or value.get("registry_version") != "canonical_artifact_registry.v2.1.0":
        raise ControlPlaneError("REGISTRY_INVALID", str(ARTIFACT_REGISTRY_PATH))
    return value


def control_dir(workflow_dir: Path) -> Path:
    return workflow_dir / ".control_v2_1"


def key_path(workflow_dir: Path) -> Path:
    return control_dir(workflow_dir) / "control.key"


def state_path(workflow_dir: Path) -> Path:
    return workflow_dir / "workflow_state.json"


def get_key(workflow_dir: Path) -> bytes:
    path = key_path(workflow_dir)
    if not path.is_file():
        raise ControlPlaneError("STATE_KEY_MISSING", str(path))
    key = path.read_bytes()
    if len(key) != 32:
        raise ControlPlaneError("STATE_KEY_INVALID", str(path))
    return key


def make_key(workflow_dir: Path) -> None:
    directory = control_dir(workflow_dir)
    directory.mkdir(parents=True, exist_ok=True)
    path = key_path(workflow_dir)
    if path.exists():
        raise ControlPlaneError("STATE_KEY_ALREADY_EXISTS", str(path))
    with path.open("xb") as handle:
        handle.write(os.urandom(32))
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass


def hmac_value(key: bytes, value: dict[str, Any], omitted_field: str) -> str:
    payload = {name: item for name, item in value.items() if name != omitted_field}
    return hmac.new(key, canonical_bytes(payload), hashlib.sha256).hexdigest()


def append_event(
    state: dict[str, Any], from_stage: str | None, to_stage: str, trigger: str,
    owner: str, artifacts: list[str] | None = None,
) -> None:
    event = {
        "sequence": len(state["history"]) + 1,
        "from": from_stage,
        "to": to_stage,
        "timestamp": now(),
        "trigger": trigger,
        "owner": owner,
        "artifacts": artifacts or [],
        "previous_event_hash": state.get("history_head", ZERO_HASH),
    }
    event["event_hash"] = canonical_hash(event)
    state["history"].append(event)
    state["history_head"] = event["event_hash"]


def verify_history(state: dict[str, Any]) -> None:
    previous = ZERO_HASH
    for index, event in enumerate(state.get("history", []), 1):
        if event.get("sequence") != index or event.get("previous_event_hash") != previous:
            raise ControlPlaneError("STATE_HISTORY_CHAIN_INVALID", f"event {index}")
        expected = canonical_hash({name: value for name, value in event.items() if name != "event_hash"})
        if not hmac.compare_digest(str(event.get("event_hash", "")), expected):
            raise ControlPlaneError("STATE_HISTORY_CHAIN_INVALID", f"event {index} hash")
        previous = expected
    if not hmac.compare_digest(str(state.get("history_head", "")), previous):
        raise ControlPlaneError("STATE_HISTORY_HEAD_INVALID", "history_head")


def save_state(workflow_dir: Path, state: dict[str, Any]) -> None:
    state["updated_at"] = now()
    state["registry_version"] = "canonical_artifact_registry.v2.1.0"
    state["registry_sha256"] = file_sha256(ARTIFACT_REGISTRY_PATH)
    state["state_hmac"] = hmac_value(get_key(workflow_dir), state, "state_hmac")
    schema = load_json(STATE_SCHEMA_PATH, "STATE_SCHEMA_UNREADABLE")
    assert isinstance(schema, dict)
    validate_schema(state, schema, "WORKFLOW_STATE_SCHEMA_INVALID")
    verify_history(state)
    atomic_json(state_path(workflow_dir), state)


def load_state(workflow_dir: Path) -> dict[str, Any]:
    path = state_path(workflow_dir)
    if not path.is_file():
        raise ControlPlaneError("WORKFLOW_STATE_MISSING", str(path))
    value = load_json(path, "WORKFLOW_STATE_INVALID")
    if not isinstance(value, dict):
        raise ControlPlaneError("WORKFLOW_STATE_INVALID", "top level must be object")
    schema = load_json(STATE_SCHEMA_PATH, "STATE_SCHEMA_UNREADABLE")
    assert isinstance(schema, dict)
    validate_schema(value, schema, "WORKFLOW_STATE_SCHEMA_INVALID")
    if value.get("registry_sha256") != file_sha256(ARTIFACT_REGISTRY_PATH):
        raise ControlPlaneError("REGISTRY_CHANGED", "workflow was authorized against another artifact registry")
    expected = hmac_value(get_key(workflow_dir), value, "state_hmac")
    if not hmac.compare_digest(str(value.get("state_hmac", "")), expected):
        raise ControlPlaneError("STATE_HMAC_INVALID", "workflow_state.json was modified outside the control plane")
    verify_history(value)
    return value


def artifact_doc(state: dict[str, Any], artifact_id: str) -> Any:
    entry = state.get("active_artifacts", {}).get(artifact_id)
    if not entry:
        raise ControlPlaneError("ARTIFACT_NOT_REGISTERED", artifact_id)
    return load_json(Path(entry["path"]), f"ARTIFACT_INVALID:{artifact_id}")


def dependency_entries(contract: dict[str, Any], state: dict[str, Any]) -> dict[str, str]:
    active = state.get("active_artifacts", {})
    dependencies: dict[str, str] = {}
    for artifact_id in contract.get("dependencies", []):
        entry = active.get(artifact_id)
        if not entry:
            raise ControlPlaneError("DEPENDENCY_RECEIPT_MISSING", artifact_id)
        dependencies[artifact_id] = entry["sha256"]
    for alternatives in contract.get("dependencies_any", []):
        present = [artifact_id for artifact_id in alternatives if artifact_id in active]
        if len(present) != 1:
            raise ControlPlaneError("DEPENDENCY_BRANCH_INVALID", f"expected exactly one of {alternatives}, found {present}")
        dependencies[present[0]] = active[present[0]]["sha256"]
    return dependencies


def import_module(path: Path, label: str):
    name = f"cumcm_v2_1_{label}_{file_sha256(path)[:12]}"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ControlPlaneError("VALIDATOR_IMPORT_FAILED", str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pointer_get(document: Any, pointer: str) -> Any:
    if pointer == "":
        return document
    if not pointer.startswith("/"):
        raise ControlPlaneError("SOURCE_LOCATOR_INVALID", pointer)
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        try:
            current = current[int(token)] if isinstance(current, list) else current[token]
        except (KeyError, IndexError, TypeError, ValueError) as exc:
            raise ControlPlaneError("SOURCE_LOCATOR_INVALID", pointer) from exc
    return current


def value_matches(expected: Any, actual: Any, tolerance: float | None) -> bool:
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return abs(float(expected) - float(actual)) <= (tolerance or 0.0)
    return expected == actual


def iter_macros(node: Any, prefix: str = ""):
    if not isinstance(node, dict):
        return
    if "value" in node and "source" in node:
        yield prefix, node
        return
    for key, value in node.items():
        yield from iter_macros(value, f"{prefix}.{key}" if prefix else key)


def validate_macro_sources(document: dict[str, Any], path: Path) -> list[str]:
    count = 0
    for macro_id, macro in iter_macros(document.get("macros", {})):
        count += 1
        source = str(macro.get("source", ""))
        if source.startswith("derived from "):
            raise ControlPlaneError("MACRO_DERIVATION_UNBOUND", macro_id)
        file_part, marker, pointer = source.partition("#")
        if not marker:
            raise ControlPlaneError("MACRO_SOURCE_LOCATOR_MISSING", macro_id)
        source_path = Path(file_part)
        if not source_path.is_absolute():
            source_path = (path.parent / source_path).resolve()
        if not source_path.is_file():
            raise ControlPlaneError("MACRO_SOURCE_MISSING", f"{macro_id}: {source_path}")
        source_doc = load_json(source_path, "MACRO_SOURCE_INVALID")
        actual = pointer_get(source_doc, pointer)
        if not value_matches(macro.get("value"), actual, macro.get("tolerance")):
            raise ControlPlaneError("MACRO_VALUE_MISMATCH", macro_id)
    if count == 0:
        raise ControlPlaneError("MACRO_SET_EMPTY", str(path))
    return [f"macro_source_values_verified:{count}"]


def validate_figure_manifest(document: dict[str, Any], path: Path) -> list[str]:
    evidence_count = 0
    for figure in document.get("figures", []):
        if figure.get("figure_type") == "EVIDENCE_BEARING":
            evidence_count += 1
        for file_field, hash_field in (("source_data_artifact", "source_hash"), ("generator_source", "generator_hash"), ("output_file", "output_hash")):
            candidate = Path(figure[file_field])
            if not candidate.is_absolute():
                candidate = (path.parent / candidate).resolve()
            if not candidate.is_file() or file_sha256(candidate) != figure[hash_field]:
                raise ControlPlaneError("FIGURE_PROVENANCE_FAIL", f"{figure['figure_id']}:{file_field}")
    if evidence_count < 1:
        raise ControlPlaneError("FIGURE_EVIDENCE_EMPTY", str(path))
    return [f"figure_files_and_hashes_verified:{len(document['figures'])}", f"evidence_bearing:{evidence_count}"]


def validate_figure_report(document: dict[str, Any], state: dict[str, Any]) -> list[str]:
    manifest_entry = state["active_artifacts"]["09_figure_manifest"]
    manifest = artifact_doc(state, "09_figure_manifest")
    assert isinstance(manifest, dict)
    errors: list[str] = []
    try:
        validate_figure_manifest(manifest, Path(manifest_entry["path"]))
    except ControlPlaneError as exc:
        errors.append(f"{exc.code}:{exc.detail}")
    expected_status = "PASS" if not errors else "FAIL"
    evidence_count = sum(1 for item in manifest["figures"] if item["figure_type"] == "EVIDENCE_BEARING")
    if document.get("manifest_sha256") != manifest_entry["sha256"] or document.get("figures_checked") != len(manifest["figures"]) or document.get("evidence_bearing_count") != evidence_count:
        raise ControlPlaneError("FIGURE_REPORT_STALE", "manifest binding/count mismatch")
    if document.get("status") != expected_status or document.get("errors") != errors:
        raise ControlPlaneError("FIGURE_REPORT_INCONSISTENT", "declared report differs from recomputation")
    return ["figure_report_recomputed", f"figure_report_status:{expected_status}"]


def validate_hash_bound(document: dict[str, Any], dependencies: dict[str, str], artifact_id: str) -> list[str]:
    if document.get("input_hashes") != dependencies:
        raise ControlPlaneError("GATE_INPUT_HASH_MISMATCH", artifact_id)
    return ["dependency_hash_map_exact"]


def validate_reference_result(document: dict[str, Any], state: dict[str, Any]) -> list[str]:
    bibliography = artifact_doc(state, "10_bibliography")
    citations = artifact_doc(state, "11_in_text_citations")
    assert isinstance(bibliography, dict) and isinstance(citations, dict)
    known = [item["reference_id"] for item in bibliography["references"]]
    if sorted(document.get("citation_ids", [])) != sorted(known):
        raise ControlPlaneError("REFERENCE_IDENTITY_MISMATCH", "citation_ids do not match bibliography")
    if sorted(citations.get("in_text_citations", [])) != sorted(known):
        raise ControlPlaneError("REFERENCE_GRAPH_INCOMPLETE", "every bibliography id must be cited exactly through the canonical citation artifact")
    if document.get("online_required") and not document.get("online_verified"):
        raise ControlPlaneError("ONLINE_VERIFICATION_REQUIRED", "online-required task cannot authorize offline-only references")
    if document.get("bibliography_sha256") != state["active_artifacts"]["10_bibliography"]["sha256"] or document.get("paper_sha256") != state["active_artifacts"]["10_paper_source"]["sha256"]:
        raise ControlPlaneError("REFERENCE_RESULT_STALE", "paper/bibliography hash mismatch")
    return [f"reference_ids_verified:{len(known)}", "online_requirement_enforced"]


def validate_claim_result(document: dict[str, Any], state: dict[str, Any], dependencies: dict[str, str]) -> list[str]:
    if document.get("input_hashes") != dependencies:
        raise ControlPlaneError("CLAIM_GATE_INPUT_HASH_MISMATCH", "input_hashes")
    references = artifact_doc(state, "11_reference_validation")
    assert isinstance(references, dict)
    citation_ids = set(references.get("citation_ids", []))
    active_hashes = {entry["sha256"] for entry in state["active_artifacts"].values()}
    claim_ids: set[str] = set()
    for binding in document.get("claim_bindings", []):
        claim_id = binding["claim_id"]
        if claim_id in claim_ids:
            raise ControlPlaneError("DUPLICATE_CLAIM_ID", claim_id)
        claim_ids.add(claim_id)
        unknown_citations = set(binding["citation_ids"]) - citation_ids
        if unknown_citations:
            raise ControlPlaneError("UNKNOWN_CITATION_ID", f"{claim_id}:{sorted(unknown_citations)}")
        unknown_evidence = set(binding["evidence_hashes"]) - active_hashes
        if unknown_evidence:
            raise ControlPlaneError("UNKNOWN_EVIDENCE_HASH", f"{claim_id}:{sorted(unknown_evidence)}")
    if document.get("claims_total") != len(claim_ids):
        raise ControlPlaneError("CLAIM_COUNT_MISMATCH", str(document.get("claims_total")))
    return [f"claim_ids_unique:{len(claim_ids)}", "citation_ids_resolved", "evidence_hashes_resolved"]


def validate_submission_manifest(document: dict[str, Any], workflow_dir: Path, state: dict[str, Any]) -> list[str]:
    if document.get("workflow_id") != state["workflow_id"]:
        raise ControlPlaneError("SUBMISSION_WORKFLOW_MISMATCH", str(document.get("workflow_id")))
    seen: set[str] = set()
    for item in document.get("submission_files", []):
        artifact_id = item["artifact_id"]
        if artifact_id in seen or artifact_id not in state["active_artifacts"]:
            raise ControlPlaneError("SUBMISSION_FILE_UNBOUND", artifact_id)
        seen.add(artifact_id)
        entry = state["active_artifacts"][artifact_id]
        path = Path(item["path"])
        if not path.is_absolute():
            path = (workflow_dir / path).resolve()
        if not path.is_file() or file_sha256(path) != item["sha256"] or item["sha256"] != entry["sha256"] or item["size_bytes"] != path.stat().st_size:
            raise ControlPlaneError("SUBMISSION_FILE_HASH_MISMATCH", artifact_id)
    if not {"12_paper_docx", "12_paper_pdf"}.issubset(seen):
        raise ControlPlaneError("SUBMISSION_FILES_INCOMPLETE", "DOCX and PDF are required")
    return [f"submission_files_verified:{len(seen)}"]


def validation_artifact_index(state: dict[str, Any]) -> dict[str, Any]:
    plan = artifact_doc(state, "07_validation_plan")
    handoff = artifact_doc(state, "06_validation_handoff")
    evidence = artifact_doc(state, "07_validation_evidence")
    assert isinstance(plan, dict) and isinstance(handoff, dict) and isinstance(evidence, dict)
    data_id = "02_data_profile" if "02_data_profile" in state["active_artifacts"] else "02_data_not_required"
    role_map = {
        "@model": ("05_model_spec", "MODEL_ARTIFACT"),
        "@data": (data_id, "DATA_ARTIFACT"),
        "@candidate_portfolio": ("03_candidate_portfolio", "CANDIDATE_PORTFOLIO"),
        "@selection_verdict": ("04_selection_verdict", "SELECTION_VERDICT"),
    }
    index: dict[str, Any] = {}
    for role, (artifact_id, kind) in role_map.items():
        entry = state["active_artifacts"][artifact_id]
        index[role] = {"path": entry["path"], "sha256": entry["sha256"], "kind": kind}
    plan_entry = state["active_artifacts"]["07_validation_plan"]
    index["@registered_plan"] = {
        "path": plan_entry["path"], "sha256": plan_entry["sha256"],
        "kind": "REGISTERED_VALIDATION_PLAN", "plan_hash": plan["plan_hash"],
    }
    for role, entry in (handoff.get("validation_artifacts") or {}).items():
        index[role] = entry
    evidence_path = Path(state["active_artifacts"]["07_validation_evidence"]["path"])
    for record in evidence.get("evidence", []):
        name = record.get("source_artifact")
        if not name or name in index:
            continue
        source_path = Path(name)
        if not source_path.is_absolute():
            source_path = (evidence_path.parent / source_path).resolve()
        index[name] = {"path": str(source_path), "sha256": record.get("artifact_sha256"), "kind": "VALIDATION_OUTPUT", "producer_stage": "S4"}
    return index


def validate_owner_artifact(
    workflow_dir: Path, state: dict[str, Any], artifact_id: str, path: Path,
    contract: dict[str, Any], dependencies: dict[str, str], document: Any,
) -> tuple[list[str], str | None, list[str], list[str]]:
    checks: list[str] = []
    schema_ref = contract.get("schema")
    if schema_ref:
        validate_schema(document, load_schema_ref(schema_ref, workflow_dir), f"ARTIFACT_SCHEMA_INVALID:{artifact_id}")
        checks.append(f"schema:{contract['schema_id']}")
    validator = contract["validator"]
    if validator == "problem_structure":
        module = import_module(resolve_token(contract["validator_source"], workflow_dir), "selection")
        module.validate_problem_structure(document)
        checks.append("owner_validator:validate_problem_structure")
    elif validator == "candidate_portfolio":
        module = import_module(resolve_token(contract["validator_source"], workflow_dir), "selection")
        if document.get("schema_version") == "candidate_portfolio.schema.v2":
            module.validate_portfolio_v2(document)
        else:
            module.validate_portfolio(document)
        checks.append("owner_validator:validate_candidate_portfolio")
    elif validator == "selection_verdict":
        module = import_module(resolve_token(contract["validator_source"], workflow_dir), "selection")
        structure = artifact_doc(state, "01_problem_structure")
        portfolio = artifact_doc(state, "03_candidate_portfolio")
        if document.get("schema_version") == "selection_verdict.schema.v2":
            module.validate_selection_verdict_v2(document, portfolio, structure)
        else:
            module.validate_selection_verdict(document, portfolio, structure)
        checks.append("owner_validator:validate_selection_verdict")
    elif validator == "model_validation_gate":
        module = import_module(resolve_token(contract["validator_source"], workflow_dir), "validation")
        plan = artifact_doc(state, "07_validation_plan")
        evidence = artifact_doc(state, "07_validation_evidence")
        envelope = artifact_doc(state, "07_failure_envelope")
        module.validate_gate(document, plan, evidence, envelope, validation_artifact_index(state))
        checks.append("owner_validator:validate_r2_gate")
    elif validator == "figure_manifest":
        checks.extend(validate_figure_manifest(document, path))
    elif validator == "figure_provenance_report":
        checks.extend(validate_figure_report(document, state))
    elif validator == "paper_macros":
        checks.extend(validate_macro_sources(document, path))
    elif validator == "reference_validation":
        checks.extend(validate_reference_result(document, state))
    elif validator == "claim_gate":
        checks.extend(validate_claim_result(document, state, dependencies))
    elif validator == "pre_render_authorization":
        if document.get("input_hashes") != dependencies:
            raise ControlPlaneError("GATE_INPUT_HASH_MISMATCH", artifact_id)
        with tempfile.TemporaryDirectory(prefix="cumcm_v2_1_prerender_receipt_") as temp_value:
            output = Path(temp_value) / "pre_render_authorization.json"
            command = [
                sys.executable, str(resolve_token(contract["validator_source"], workflow_dir)),
                "--workflow-state", str(state_path(workflow_dir)), "--output", str(output),
            ]
            if document.get("production_mode") == "NON_PRODUCTION":
                command.append("--non-production")
            result = subprocess.run(command, capture_output=True, text=True)
            expected_exit = 0 if document.get("authorized") else 1
            if result.returncode != expected_exit or not output.is_file():
                raise ControlPlaneError("PRE_RENDER_REVALIDATION_FAILED", (result.stdout + result.stderr)[-500:])
            recomputed = load_json(output, "PRE_RENDER_OUTPUT_INVALID")
            left = {name: value for name, value in document.items() if name != "created_at"}
            right = {name: value for name, value in recomputed.items() if name != "created_at"}
            if left != right:
                raise ControlPlaneError("PRE_RENDER_RECOMPUTATION_MISMATCH", artifact_id)
        checks.extend(["owner_validator:pre_render_reexecuted", "dependency_hash_map_exact"])
    elif validator == "s7_publication_gate":
        if document.get("input_hashes") != dependencies:
            raise ControlPlaneError("GATE_INPUT_HASH_MISMATCH", artifact_id)
        module = import_module(resolve_token(contract["validator_source"], workflow_dir), "s7")
        checks.extend(module.validate_declared_gate(document, workflow_dir, state))
    elif validator == "hash_bound_gate":
        checks.extend(validate_hash_bound(document, dependencies, artifact_id))
        if artifact_id == "13_s7_publication_gate":
            if document.get("limitations") != state.get("limitations") or document.get("claim_restrictions") != state.get("claim_restrictions"):
                raise ControlPlaneError("LIMITATION_PROPAGATION_FAIL", artifact_id)
            if document.get("verdict") != state.get("validation_verdict"):
                raise ControlPlaneError("S7_VERDICT_MISMATCH", artifact_id)
        if artifact_id == "14_submission_manifest":
            checks.extend(validate_submission_manifest(document, workflow_dir, state))
        if artifact_id == "14_anonymity_record":
            scanner_output = Path(document.get("scanner_output_path", ""))
            if not scanner_output.is_file() or file_sha256(scanner_output) != document.get("scanner_output_sha256"):
                raise ControlPlaneError("ANONYMITY_SCANNER_OUTPUT_INVALID", str(scanner_output))
            checks.append("anonymity_scanner_output_hash_verified")
        if artifact_id == "14_package_authorization":
            package_dir = Path(document.get("package_directory", ""))
            if not package_dir.is_dir():
                raise ControlPlaneError("PACKAGE_DIRECTORY_MISSING", str(package_dir))
            declared = {item["name"]: item for item in document.get("package_files", [])}
            actual = {item.name: item for item in package_dir.iterdir() if item.is_file()}
            if set(declared) != set(actual) or set(declared) != {"paper_submission.docx", "paper_submission.pdf"}:
                raise ControlPlaneError("PACKAGE_WHITELIST_MISMATCH", str(package_dir))
            for name, item in declared.items():
                path = actual[name]
                if file_sha256(path) != item["sha256"] or path.stat().st_size != item["size_bytes"]:
                    raise ControlPlaneError("PACKAGE_FILE_HASH_MISMATCH", name)
            checks.append("package_whitelist_and_hashes_verified")
    elif validator == "nonempty_text":
        text = path.read_text(encoding="utf-8-sig")
        if len(text.strip()) < 100:
            raise ControlPlaneError("TEXT_ARTIFACT_EMPTY", artifact_id)
        checks.append(f"nonempty_text:{len(text.strip())}")
    elif validator == "docx":
        if path.stat().st_size < 100 or not zipfile.is_zipfile(path):
            raise ControlPlaneError("DOCX_CONTAINER_INVALID", str(path))
        with zipfile.ZipFile(path) as archive:
            if "word/document.xml" not in archive.namelist() or archive.getinfo("word/document.xml").file_size < 1:
                raise ControlPlaneError("DOCX_DOCUMENT_MISSING", str(path))
        checks.append("docx_container_and_document_xml")
    elif validator == "pdf":
        payload = path.read_bytes()
        if len(payload) < 100 or not payload.startswith(b"%PDF-") or b"%%EOF" not in payload[-1024:]:
            raise ControlPlaneError("PDF_DOCUMENT_INVALID", str(path))
        checks.append("pdf_header_body_eof")
    elif validator in {"json_schema", "pipeline_manifest"}:
        if validator == "pipeline_manifest" and document.get("workflow_id") != state["workflow_id"]:
            raise ControlPlaneError("MANIFEST_WORKFLOW_MISMATCH", str(document.get("workflow_id")))
    elif validator == "release_freeze":
        expected = hmac_value(get_key(workflow_dir), document, "freeze_signature")
        if not hmac.compare_digest(str(document.get("freeze_signature", "")), expected):
            raise ControlPlaneError("FREEZE_SIGNATURE_INVALID", str(path))
        checks.append("freeze_signature_verified")
    else:
        raise ControlPlaneError("UNKNOWN_VALIDATOR", validator)
    verdict = None
    if isinstance(document, dict):
        verdict = document.get("verdict") or document.get("gate") or document.get("status")
        limitations = document.get("limitations") or []
        restrictions = document.get("claim_restrictions") or []
    else:
        limitations, restrictions = [], []
    return list(dict.fromkeys(checks)), verdict, limitations, restrictions


def expected_physical_path(path: Path, contract: dict[str, Any]) -> bool:
    actual = path.resolve().as_posix().casefold()
    expected = str(contract["physical_filename"]).replace("\\", "/").casefold()
    return actual.endswith("/" + expected) or actual == expected


def create_receipt(
    workflow_dir: Path, state: dict[str, Any], artifact_id: str, path: Path,
    contract: dict[str, Any], dependencies: dict[str, str], checks: list[str],
    verdict: str | None, limitations: list[str], restrictions: list[str],
) -> dict[str, Any]:
    source = resolve_token(contract["validator_source"], workflow_dir)
    validated_at = now()
    receipt: dict[str, Any] = {
        "receipt_version": "artifact_validation_receipt.schema.v1",
        "receipt_id": "",
        "workflow_id": state["workflow_id"],
        "artifact_id": artifact_id,
        "artifact_path": str(path.resolve()),
        "artifact_sha256": file_sha256(path),
        "artifact_schema_id": contract["schema_id"],
        "producer": contract["owner"],
        "validator": contract["validator"],
        "validator_version": "CONTROL_PLANE_V2_1_VALIDATOR.v1",
        "validator_source": str(source),
        "validator_source_sha256": source_sha256(source),
        "registry_version": "canonical_artifact_registry.v2.1.0",
        "registry_sha256": file_sha256(ARTIFACT_REGISTRY_PATH),
        "input_artifacts": dependencies,
        "checks": checks,
        "validation_status": "VALIDATED",
        "artifact_verdict": verdict,
        "limitations": limitations,
        "claim_restrictions": restrictions,
        "validated_at": validated_at,
        "signature_algorithm": "HMAC-SHA256",
        "signature": ZERO_HASH,
    }
    identity_seed = {name: value for name, value in receipt.items() if name not in {"receipt_id", "signature"}}
    receipt["receipt_id"] = "RCPT-" + canonical_hash(identity_seed)[:24].upper()
    receipt["signature"] = hmac_value(get_key(workflow_dir), receipt, "signature")
    schema = load_json(RECEIPT_SCHEMA_PATH, "RECEIPT_SCHEMA_UNREADABLE")
    assert isinstance(schema, dict)
    validate_schema(receipt, schema, "RECEIPT_SCHEMA_INVALID")
    return receipt


def verify_receipt(
    workflow_dir: Path, state: dict[str, Any], artifact_id: str, entry: dict[str, Any],
    all_artifacts: dict[str, Any],
) -> None:
    contract = all_artifacts.get(artifact_id)
    if not contract:
        raise ControlPlaneError("UNKNOWN_ARTIFACT_ID", artifact_id)
    artifact_path_value = entry.get("path")
    receipt_path_value = entry.get("receipt_path")
    if not isinstance(artifact_path_value, str) or not isinstance(receipt_path_value, str):
        raise ControlPlaneError("ARTIFACT_ENTRY_INVALID", artifact_id)
    artifact_path = Path(artifact_path_value)
    receipt_path = Path(receipt_path_value)
    if not artifact_path.is_file() or file_sha256(artifact_path) != entry.get("sha256"):
        raise ControlPlaneError("ARTIFACT_HASH_MISMATCH", artifact_id)
    if not receipt_path.is_file() or file_sha256(receipt_path) != entry.get("receipt_sha256"):
        raise ControlPlaneError("RECEIPT_HASH_MISMATCH", artifact_id)
    receipt = load_json(receipt_path, "RECEIPT_INVALID")
    if not isinstance(receipt, dict):
        raise ControlPlaneError("RECEIPT_INVALID", artifact_id)
    schema = load_json(RECEIPT_SCHEMA_PATH, "RECEIPT_SCHEMA_UNREADABLE")
    assert isinstance(schema, dict)
    validate_schema(receipt, schema, f"RECEIPT_SCHEMA_INVALID:{artifact_id}")
    expected_signature = hmac_value(get_key(workflow_dir), receipt, "signature")
    if not hmac.compare_digest(str(receipt.get("signature", "")), expected_signature):
        raise ControlPlaneError("RECEIPT_SIGNATURE_INVALID", artifact_id)
    expected_source = resolve_token(contract["validator_source"], workflow_dir)
    exact = {
        "workflow_id": state["workflow_id"],
        "artifact_id": artifact_id,
        "artifact_path": str(artifact_path.resolve()),
        "artifact_sha256": entry["sha256"],
        "artifact_schema_id": contract["schema_id"],
        "producer": contract["owner"],
        "validator": contract["validator"],
        "validator_source": str(expected_source),
        "validator_source_sha256": source_sha256(expected_source),
        "registry_sha256": file_sha256(ARTIFACT_REGISTRY_PATH),
    }
    for field, expected in exact.items():
        if receipt.get(field) != expected:
            raise ControlPlaneError("RECEIPT_BINDING_MISMATCH", f"{artifact_id}:{field}")
    current_dependencies = dependency_entries(contract, state)
    if receipt.get("input_artifacts") != current_dependencies:
        raise ControlPlaneError("STALE_ARTIFACT_RECEIPT", artifact_id)


def descendants(root: str) -> set[str]:
    dag = load_json(DAG_PATH, "INVALIDATION_DAG_INVALID")
    assert isinstance(dag, dict)
    edges = dag.get("edges", {})
    pending = list(edges.get(root, []))
    result: set[str] = set()
    while pending:
        item = pending.pop()
        if item in result:
            continue
        result.add(item)
        pending.extend(edges.get(item, []))
    return result


def invalidate_ids(state: dict[str, Any], artifact_ids: set[str], reason: str) -> list[str]:
    invalidated: list[str] = []
    for artifact_id in sorted(artifact_ids):
        entry = state["active_artifacts"].pop(artifact_id, None)
        if not entry:
            continue
        state["invalidated_artifacts"].append({
            "artifact_id": artifact_id,
            "previous_sha256": entry["sha256"],
            "reason": reason,
            "invalidated_at": now(),
        })
        invalidated.append(artifact_id)
    return invalidated


STAGE_ORDER = [
    "INIT", "S0_BOOTSTRAPPED", "S1_STRUCTURED", "DATA_READY", "DATA_NOT_REQUIRED",
    "SELECTION_AUTHORIZED", "S3_EXECUTED", "S4_RELEASED", "S5_EVIDENCE_READY",
    "S6_CONTENT_BOUND", "S6_DOCUMENT_READY", "S7_REVIEWED", "SUBMISSION_AUTHORIZED",
    "CLOSED_AND_SEALED",
]


def stage_rank(stage: str) -> int:
    if stage == "FAILED_BLOCKED":
        return len(STAGE_ORDER)
    try:
        return STAGE_ORDER.index(stage)
    except ValueError as exc:
        raise ControlPlaneError("UNKNOWN_STAGE", stage) from exc


def data_branch_state(state: dict[str, Any]) -> str:
    if "02_data_profile" in state["active_artifacts"]:
        return "DATA_READY"
    if "02_data_not_required" in state["active_artifacts"]:
        return "DATA_NOT_REQUIRED"
    return "S1_STRUCTURED"


def rollback_for_artifact(state: dict[str, Any], artifact_id: str) -> str:
    prefix = artifact_id[:2]
    if artifact_id.startswith("00_"):
        return "INIT"
    if artifact_id.startswith("01_"):
        return "S0_BOOTSTRAPPED"
    if artifact_id.startswith("02_"):
        return "S1_STRUCTURED"
    if artifact_id.startswith(("03_", "04_")):
        return data_branch_state(state)
    if artifact_id.startswith(("05_", "06_")):
        return "SELECTION_AUTHORIZED"
    if artifact_id.startswith(("07_", "08_")):
        return "S3_EXECUTED"
    if artifact_id.startswith("09_"):
        return "S4_RELEASED"
    if artifact_id.startswith(("10_", "11_")):
        return "S5_EVIDENCE_READY"
    if artifact_id.startswith("12_"):
        return "S6_CONTENT_BOUND"
    if artifact_id.startswith("13_"):
        return "S6_DOCUMENT_READY"
    if artifact_id.startswith("14_"):
        return "S7_REVIEWED"
    if artifact_id.startswith("15_"):
        return "SUBMISSION_AUTHORIZED"
    raise ControlPlaneError("UNKNOWN_ARTIFACT_ID", artifact_id)


def rollback_completed(state: dict[str, Any], target: str) -> None:
    target_rank = stage_rank(target)
    state["completed_stages"] = [
        stage for stage in state["completed_stages"]
        if stage in STAGE_ORDER and stage_rank(stage) <= target_rank
    ]


def register_artifact(workflow_dir: Path, artifact_id: str, raw_path: str) -> int:
    state = load_state(workflow_dir)
    if state["current_stage"] in {"CLOSED_AND_SEALED", "FAILED_BLOCKED"}:
        raise ControlPlaneError("WORKFLOW_NOT_MUTABLE", state["current_stage"], BLOCKED)
    artifacts = registry()["artifacts"]
    contract = artifacts.get(artifact_id)
    if not contract:
        raise ControlPlaneError("UNKNOWN_ARTIFACT_ID", artifact_id)
    path = Path(raw_path).resolve()
    if not path.is_file() or path.stat().st_size == 0:
        raise ControlPlaneError("ARTIFACT_MISSING_OR_EMPTY", str(path))
    if not expected_physical_path(path, contract):
        raise ControlPlaneError("NONCANONICAL_PHYSICAL_FILENAME", f"{artifact_id} expects {contract['physical_filename']}")
    if contract["media_type"] == "application/json":
        document: Any = load_json(path, f"ARTIFACT_JSON_INVALID:{artifact_id}")
        if not isinstance(document, dict):
            raise ControlPlaneError("ARTIFACT_SCHEMA_INVALID", f"{artifact_id}: object required")
    else:
        document = None
    dependencies = dependency_entries(contract, state)
    checks, verdict, limitations, restrictions = validate_owner_artifact(
        workflow_dir, state, artifact_id, path, contract, dependencies, document,
    )
    receipt = create_receipt(
        workflow_dir, state, artifact_id, path, contract, dependencies,
        checks, verdict, limitations, restrictions,
    )
    previous = state["active_artifacts"].get(artifact_id)
    changed = bool(previous and previous["sha256"] != file_sha256(path))
    invalidated: list[str] = []
    if previous:
        invalidated.extend(invalidate_ids(state, {artifact_id}, f"replaced:{artifact_id}"))
    if changed:
        invalidated.extend(invalidate_ids(state, descendants(artifact_id), f"upstream_changed:{artifact_id}"))
    if artifact_id == "02_data_profile" and "02_data_not_required" in state["active_artifacts"]:
        invalidated.extend(invalidate_ids(state, {"02_data_not_required"} | descendants("02_data_not_required"), "data_branch_changed"))
    if artifact_id == "02_data_not_required" and "02_data_profile" in state["active_artifacts"]:
        invalidated.extend(invalidate_ids(state, {"02_data_profile"} | descendants("02_data_profile"), "data_branch_changed"))
    receipt_path = control_dir(workflow_dir) / "receipts" / f"{artifact_id}.receipt.json"
    atomic_json(receipt_path, receipt)
    state["active_artifacts"][artifact_id] = {
        "path": str(path),
        "sha256": file_sha256(path),
        "receipt_path": str(receipt_path.resolve()),
        "receipt_sha256": file_sha256(receipt_path),
        "producer": contract["owner"],
        "validated_at": receipt["validated_at"],
    }
    if changed and stage_rank(state["current_stage"]) > stage_rank(rollback_for_artifact(state, artifact_id)):
        old_stage = state["current_stage"]
        target = rollback_for_artifact(state, artifact_id)
        state["previous_stage"] = old_stage
        state["current_stage"] = target
        state["state_status"] = "INVALIDATED"
        state["pending_route"] = {
            "reason_code": "STALE_ARTIFACTS_PRESENT", "owner": contract["owner"],
            "rollback_target": target, "invalidated_artifacts": sorted(set(invalidated)),
        }
        rollback_completed(state, target)
        append_event(state, old_stage, target, f"UPSTREAM_REPLACED:{artifact_id}", contract["owner"], sorted(set(invalidated)))
    save_state(workflow_dir, state)
    print(f"REGISTERED_AND_VALIDATED {artifact_id} receipt={receipt['receipt_id']}")
    if invalidated:
        print("INVALIDATED", ",".join(sorted(set(invalidated))))
    return OK


def effective_check(workflow_dir: Path, state: dict[str, Any], *, persist_failure: bool = True) -> tuple[bool, str | None]:
    try:
        artifacts = registry()["artifacts"]
        for artifact_id, entry in state["active_artifacts"].items():
            verify_receipt(workflow_dir, state, artifact_id, entry, artifacts)
        if state["current_stage"] == "CLOSED_AND_SEALED":
            freeze = artifact_doc(state, "15_release_freeze_record")
            assert isinstance(freeze, dict)
            frozen = freeze.get("artifact_manifest", {})
            for artifact_id, item in frozen.items():
                entry = state["active_artifacts"].get(artifact_id)
                if not entry or item != {"sha256": entry["sha256"], "receipt_sha256": entry["receipt_sha256"]}:
                    raise ControlPlaneError("FREEZE_MANIFEST_MISMATCH", artifact_id)
        return True, None
    except ControlPlaneError as exc:
        if persist_failure and state.get("current_stage") != "CLOSED_AND_SEALED":
            state["state_status"] = "INVALIDATED"
            blocker = f"{exc.code}:{exc.detail}"
            if blocker not in state["release_blockers"]:
                state["release_blockers"].append(blocker)
            save_state(workflow_dir, state)
        return False, f"{exc.code}:{exc.detail}"


def consume_rule(state: dict[str, Any], rule: dict[str, Any]) -> tuple[bool, str]:
    document = artifact_doc(state, rule["artifact"])
    current: Any = document
    for part in rule["field"].split("."):
        if not isinstance(current, dict) or part not in current:
            return False, f"{rule['artifact']}:{rule['field']} absent"
        current = current[part]
    if "equals" in rule:
        okay = current == rule["equals"]
    else:
        okay = current in rule["in"]
    return okay, f"{rule['artifact']}:{rule['field']}={current!r}"


def exact_route(reason_code: str, state: dict[str, Any]) -> dict[str, Any]:
    routes = load_json(REASON_REGISTRY_PATH, "REASON_REGISTRY_INVALID")
    assert isinstance(routes, dict)
    route = (routes.get("exact_routes") or {}).get(reason_code)
    if not route:
        raise ControlPlaneError("UNKNOWN_REASON_CODE", reason_code)
    result = {"reason_code": reason_code, **route}
    if result["rollback_target"] == "DATA_BRANCH":
        result["rollback_target"] = data_branch_state(state)
    return result


REVISION_ROOT = {
    "REVISE_FORMULATION": "05_model_spec",
    "REVISE_DATA": "02_data_profile",
    "SIMPLIFY_MODEL": "05_model_spec",
    "CHANGE_MODEL": "03_candidate_portfolio",
    "REJECT_MODEL": "03_candidate_portfolio",
    "COLLECT_MORE_DATA": "02_data_profile",
    "RERUN_SOLVER": "05_solver_manifest",
    "RERUN_VALIDATION": "07_validation_plan",
}


def handle_validation_block(workflow_dir: Path, state: dict[str, Any], decision: dict[str, Any], why: str) -> int:
    verdict = decision.get("verdict")
    if verdict == "FAIL":
        route = exact_route("VALIDATION_S4_FAIL", state)
        old = state["current_stage"]
        state["previous_stage"] = old
        state["current_stage"] = "FAILED_BLOCKED"
        state["state_status"] = "FAILED_BLOCKED"
        state["validation_verdict"] = "FAIL"
        state["pending_route"] = {**route, "message": why}
        state["release_blockers"].append("VALIDATION_S4_FAIL")
        append_event(state, old, "FAILED_BLOCKED", "VALIDATION_S4_FAIL", route["owner"], ["08_release_decision"])
        save_state(workflow_dir, state)
        print("VALIDATION_S4_FAIL -> FAILED_BLOCKED")
        return BLOCKED
    if verdict != "REVISE":
        raise ControlPlaneError("VALIDATION_VERDICT_INVALID", str(verdict))
    token = decision.get("revision_token")
    action = decision.get("required_action")
    if not isinstance(token, str) or len(token) < 8:
        raise ControlPlaneError("REVISION_TOKEN_MISSING", str(token))
    if token in state["consumed_revision_tokens"]:
        raise ControlPlaneError("REVISION_TOKEN_REPLAY", token, BLOCKED)
    if action not in REVISION_ROOT:
        raise ControlPlaneError("REVISION_ACTION_INVALID", str(action))
    reason_code = "VALIDATION_" + action
    route = exact_route(reason_code, state)
    root = REVISION_ROOT[action]
    if action in {"REVISE_DATA", "COLLECT_MORE_DATA"} and "02_data_profile" not in state["active_artifacts"]:
        root = "02_data_not_required"
    invalidated = invalidate_ids(state, {root} | descendants(root), f"revision_token:{token}")
    old = state["current_stage"]
    target = route["rollback_target"]
    state["previous_stage"] = old
    state["current_stage"] = target
    state["state_status"] = "REVISION_REQUIRED"
    state["validation_verdict"] = "REVISE"
    state["pending_route"] = {**route, "revision_token": token, "required_action": action, "invalidated_artifacts": invalidated, "message": why}
    state["consumed_revision_tokens"].append(token)
    state["revision_history"].append({
        "revision_token": token, "required_action": action, "owner": route["owner"],
        "rollback_target": target, "invalidated_artifacts": invalidated, "routed_at": now(),
    })
    if stage_rank(target) < stage_rank("SELECTION_AUTHORIZED"):
        state["selection_authorized"] = False
    rollback_completed(state, target)
    append_event(state, old, target, reason_code, route["owner"], invalidated)
    save_state(workflow_dir, state)
    print(f"VALIDATION_REVISE token={token} action={action} -> {route['owner']} @ {target}")
    return BLOCKED


def advance(workflow_dir: Path) -> int:
    state = load_state(workflow_dir)
    okay, why = effective_check(workflow_dir, state)
    if not okay:
        print("EFFECTIVE_STATE_INVALIDATED", why)
        return BLOCKED
    if state["current_stage"] in {"CLOSED_AND_SEALED", "FAILED_BLOCKED"}:
        print("TRANSITION_DENIED terminal", state["current_stage"])
        return BLOCKED
    transitions_doc = load_json(TRANSITION_REGISTRY_PATH, "TRANSITION_REGISTRY_INVALID")
    assert isinstance(transitions_doc, dict)
    candidates = [item for item in transitions_doc["transitions"] if item["from"] == state["current_stage"]]
    if not candidates:
        print("TRANSITION_DENIED no legal transition from", state["current_stage"])
        return BLOCKED
    active = state["active_artifacts"]
    ready = [item for item in candidates if all(artifact_id in active for artifact_id in item["required"])]
    if not ready:
        missing_sets = [{artifact_id for artifact_id in item["required"] if artifact_id not in active} for item in candidates]
        print("TRANSITION_DENIED missing validated receipts", [sorted(item) for item in missing_sets])
        return BLOCKED
    transition = ready[0]
    rules = []
    if transition.get("consume"):
        rules.append(transition["consume"])
    rules.extend(transition.get("consume_all", []))
    for rule in rules:
        passed, detail = consume_rule(state, rule)
        if not passed:
            if transition["gate"] == "S4_DETERMINISTIC_RELEASE_RECEIPT":
                decision = artifact_doc(state, "08_release_decision")
                assert isinstance(decision, dict)
                return handle_validation_block(workflow_dir, state, decision, detail)
            reason = transition.get("on_fail_reason", "STALE_ARTIFACTS_PRESENT")
            route = exact_route(reason, state)
            state["pending_route"] = {**route, "message": detail}
            state["release_blockers"] = list(dict.fromkeys(state["release_blockers"] + [reason]))
            save_state(workflow_dir, state)
            print(f"GATE_BLOCKED {reason} -> {route['owner']} @ {route['rollback_target']}")
            return BLOCKED
    old = state["current_stage"]
    state["previous_stage"] = old
    state["current_stage"] = transition["to"]
    state["state_status"] = "VALID"
    state["pending_route"] = None
    state["release_blockers"] = []
    if transition["to"] not in state["completed_stages"]:
        state["completed_stages"].append(transition["to"])
    if transition["to"] == "SELECTION_AUTHORIZED":
        state["selection_authorized"] = True
    if transition["to"] == "S4_RELEASED":
        decision = artifact_doc(state, "08_release_decision")
        assert isinstance(decision, dict)
        state["validation_verdict"] = decision["verdict"]
        state["limitations"] = decision.get("limitations") or []
        state["claim_restrictions"] = decision.get("claim_restrictions") or []
    append_event(state, old, transition["to"], transition["gate"], transition["owner"], transition["required"])
    save_state(workflow_dir, state)
    print("ADVANCE ->", state["current_stage"])
    return OK


def check_command(workflow_dir: Path) -> int:
    state = load_state(workflow_dir)
    okay, why = effective_check(workflow_dir, state)
    print("EFFECTIVE_STATE", state["current_stage"], "FRESH" if okay else f"INVALID:{why}")
    return OK if okay else BLOCKED


def route_command(workflow_dir: Path, reason_code: str) -> int:
    state = load_state(workflow_dir)
    route = exact_route(reason_code, state)
    state["pending_route"] = route
    state["release_blockers"] = list(dict.fromkeys(state["release_blockers"] + [reason_code]))
    append_event(state, state["current_stage"], state["current_stage"], reason_code, route["owner"], [])
    save_state(workflow_dir, state)
    print(f"ROUTED {reason_code} -> {route['owner']} @ {route['rollback_target']}")
    return BLOCKED


def resume_command(workflow_dir: Path) -> int:
    state = load_state(workflow_dir)
    okay, why = effective_check(workflow_dir, state)
    if not okay:
        print("RESUME_BLOCKED", why)
        return BLOCKED
    pending = state.get("pending_route")
    if pending and pending.get("rollback_target") in STAGE_ORDER:
        target = pending["rollback_target"]
        old = state["current_stage"]
        if stage_rank(target) < stage_rank(old):
            state["previous_stage"] = old
            state["current_stage"] = target
            rollback_completed(state, target)
            append_event(state, old, target, f"RESUME:{pending['reason_code']}", pending["owner"], pending.get("invalidated_artifacts", []))
        state["state_status"] = "REVISION_REQUIRED"
    save_state(workflow_dir, state)
    print("RESUME ->", state["current_stage"])
    return OK


def close_command(workflow_dir: Path) -> int:
    state = load_state(workflow_dir)
    if state["current_stage"] != "SUBMISSION_AUTHORIZED":
        print("TRANSITION_DENIED close requires SUBMISSION_AUTHORIZED")
        return BLOCKED
    okay, why = effective_check(workflow_dir, state)
    if not okay:
        print("CLOSE_BLOCKED", why)
        return BLOCKED
    required = set(registry()["artifacts"]) - {"02_data_profile", "02_data_not_required", "15_release_freeze_record"}
    required.add("02_data_profile" if "02_data_profile" in state["active_artifacts"] else "02_data_not_required")
    missing = sorted(required - set(state["active_artifacts"]))
    if missing:
        print("CLOSE_BLOCKED missing canonical artifacts", missing)
        return BLOCKED
    canonical_completed = [
        "S0_BOOTSTRAPPED", "S1_STRUCTURED", data_branch_state(state), "SELECTION_AUTHORIZED",
        "S3_EXECUTED", "S4_RELEASED", "S5_EVIDENCE_READY", "S6_CONTENT_BOUND",
        "S6_DOCUMENT_READY", "S7_REVIEWED", "SUBMISSION_AUTHORIZED",
    ]
    if any(stage not in state["completed_stages"] for stage in canonical_completed):
        print("CLOSE_BLOCKED canonical history incomplete")
        return BLOCKED
    package = artifact_doc(state, "14_package_authorization")
    s7 = artifact_doc(state, "13_s7_publication_gate")
    assert isinstance(package, dict) and isinstance(s7, dict)
    if not package.get("authorized") or not package.get("human_checks_resolved"):
        print("CLOSE_BLOCKED submission authorization false")
        return BLOCKED
    if s7.get("verdict") != state["validation_verdict"] or s7.get("limitations") != state["limitations"] or s7.get("claim_restrictions") != state["claim_restrictions"]:
        print("CLOSE_BLOCKED S4/S7 propagation mismatch")
        return BLOCKED
    preclose_hash = canonical_hash({name: value for name, value in state.items() if name != "state_hmac"})
    freeze: dict[str, Any] = {
        "schema_version": "release_freeze_record.schema.v2_1",
        "workflow_id": state["workflow_id"],
        "closed_at": now(),
        "preclose_state_sha256": preclose_hash,
        "artifact_manifest": {
            artifact_id: {"sha256": entry["sha256"], "receipt_sha256": entry["receipt_sha256"]}
            for artifact_id, entry in sorted(state["active_artifacts"].items())
        },
        "validation_verdict": state["validation_verdict"],
        "limitations": state["limitations"],
        "claim_restrictions": state["claim_restrictions"],
        "package_authorization_sha256": state["active_artifacts"]["14_package_authorization"]["sha256"],
        "registry_sha256": file_sha256(ARTIFACT_REGISTRY_PATH),
        "freeze_signature": ZERO_HASH,
    }
    freeze["freeze_signature"] = hmac_value(get_key(workflow_dir), freeze, "freeze_signature")
    freeze_path = workflow_dir / "release_freeze_record.json"
    atomic_json(freeze_path, freeze)
    contract = registry()["artifacts"]["15_release_freeze_record"]
    dependencies = dependency_entries(contract, state)
    checks, verdict, limitations, restrictions = validate_owner_artifact(
        workflow_dir, state, "15_release_freeze_record", freeze_path, contract, dependencies, freeze,
    )
    receipt = create_receipt(
        workflow_dir, state, "15_release_freeze_record", freeze_path, contract, dependencies,
        checks, verdict, limitations, restrictions,
    )
    receipt_path = control_dir(workflow_dir) / "receipts" / "15_release_freeze_record.receipt.json"
    atomic_json(receipt_path, receipt)
    state["active_artifacts"]["15_release_freeze_record"] = {
        "path": str(freeze_path.resolve()), "sha256": file_sha256(freeze_path),
        "receipt_path": str(receipt_path.resolve()), "receipt_sha256": file_sha256(receipt_path),
        "producer": contract["owner"], "validated_at": receipt["validated_at"],
    }
    old = state["current_stage"]
    state["previous_stage"] = old
    state["current_stage"] = "CLOSED_AND_SEALED"
    state["state_status"] = "SEALED"
    state["completed_stages"].append("CLOSED_AND_SEALED")
    append_event(state, old, "CLOSED_AND_SEALED", "CLOSE_REVALIDATE_FREEZE_SEAL", "modeling-workflow-orchestrator", ["15_release_freeze_record"])
    save_state(workflow_dir, state)
    print("CLOSED_AND_SEALED")
    return OK


def new_state(workflow_id: str) -> dict[str, Any]:
    timestamp = now()
    state: dict[str, Any] = {
        "workflow_version": "V2.1",
        "workflow_id": workflow_id,
        "current_stage": "INIT",
        "previous_stage": None,
        "state_status": "VALID",
        "completed_stages": [],
        "active_artifacts": {},
        "invalidated_artifacts": [],
        "validation_verdict": None,
        "limitations": [],
        "claim_restrictions": [],
        "selection_authorized": False,
        "history": [],
        "history_head": ZERO_HASH,
        "pending_route": None,
        "revision_history": [],
        "consumed_revision_tokens": [],
        "release_blockers": [],
        "created_at": timestamp,
        "updated_at": timestamp,
        "registry_version": "canonical_artifact_registry.v2.1.0",
        "registry_sha256": file_sha256(ARTIFACT_REGISTRY_PATH),
        "state_hmac": ZERO_HASH,
    }
    append_event(state, None, "INIT", "INITIALIZE_V2_1", "modeling-workflow-orchestrator", [])
    return state


def init_command(workflow_dir: Path, workflow_id: str) -> int:
    workflow_dir.mkdir(parents=True, exist_ok=True)
    if state_path(workflow_dir).exists() or key_path(workflow_dir).exists():
        raise ControlPlaneError("WORKFLOW_ALREADY_EXISTS", str(workflow_dir))
    make_key(workflow_dir)
    save_state(workflow_dir, new_state(workflow_id))
    print("V2.1 INIT", workflow_id)
    return OK


def copy_for_migration(source: Path, destination: Path) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if file_sha256(destination) != file_sha256(source):
            raise ControlPlaneError("MIGRATION_DESTINATION_CONFLICT", str(destination))
    else:
        shutil.copy2(source, destination)
    return destination


def migrate_command(workflow_dir: Path) -> int:
    original_path = state_path(workflow_dir)
    if not original_path.is_file():
        raise ControlPlaneError("WORKFLOW_STATE_MISSING", str(original_path))
    original = load_json(original_path, "LEGACY_STATE_INVALID")
    if not isinstance(original, dict):
        raise ControlPlaneError("LEGACY_STATE_INVALID", "object required")
    if original.get("workflow_version") == "V2.1":
        state = load_state(workflow_dir)
        print("ALREADY_V2_1", state["current_stage"])
        return OK
    if "workflow_id" not in original or "current_stage" not in original or not isinstance(original.get("active_artifacts", {}), dict):
        raise ControlPlaneError("LEGACY_STATE_UNRECOGNIZED", "required v1/v2 fields missing")
    version = original.get("workflow_version") or "V1.1"
    if version not in {"V1.1", "v1", "v1.1", "v2", "V2"}:
        raise ControlPlaneError("LEGACY_VERSION_UNSUPPORTED", str(version))
    for artifact_id, entry in original.get("active_artifacts", {}).items():
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ControlPlaneError("LEGACY_ARTIFACT_ENTRY_INVALID", artifact_id)
        path = Path(entry["path"])
        if not path.is_file() or (entry.get("sha256") and file_sha256(path) != entry["sha256"]):
            raise ControlPlaneError("LEGACY_ARTIFACT_INTEGRITY_FAIL", artifact_id)
    backup = workflow_dir / "workflow_state.pre_v2_1.json"
    if backup.exists():
        raise ControlPlaneError("MIGRATION_BACKUP_ALREADY_EXISTS", str(backup))
    atomic_json(backup, original)
    if key_path(workflow_dir).exists():
        raise ControlPlaneError("MIGRATION_KEY_CONFLICT", str(key_path(workflow_dir)))
    make_key(workflow_dir)
    state = new_state(str(original["workflow_id"]))
    save_state(workflow_dir, state)
    artifacts = original.get("active_artifacts", {})
    problem_id = str(original["workflow_id"])
    structure_entry = artifacts.get("01_problem_structure")
    if structure_entry:
        try:
            structure_doc = load_json(Path(structure_entry["path"]), "LEGACY_STRUCTURE_INVALID")
            if isinstance(structure_doc, dict):
                problem_id = str(structure_doc.get("problem_id") or problem_id)
        except ControlPlaneError:
            pass
    task_brief_path = workflow_dir / "task_brief.json"
    if not task_brief_path.exists():
        atomic_json(task_brief_path, {
            "schema_version": "task_brief.schema.v2_1",
            "workflow_id": str(original["workflow_id"]),
            "problem_id": problem_id,
            "contest_mode": "TEST",
            "problem_scope": "Fail-closed migration of an existing mathematical-modeling workflow with preserved legacy evidence.",
            "deliverables": ["Migrate the highest stage provable by owner validators and signed receipts."],
            "success_criteria": ["No legacy artifact is authorized without current schema and owner-validator proof."],
            "source_type": "LEGACY_MIGRATION",
            "approved": True,
        })
    manifest_path = workflow_dir / "pipeline_manifest.json"
    if not manifest_path.exists():
        atomic_json(manifest_path, {
            "schema_version": "pipeline_manifest.schema.v2_1",
            "workflow_id": str(original["workflow_id"]),
            "control_plane_version": "V2.1",
            "artifact_registry_version": "canonical_artifact_registry.v2.1.0",
            "status_authority": "workflow_state.json",
            "canonical_stages": ["S0_BOOTSTRAPPED", "S1_STRUCTURED", "DATA_READY|DATA_NOT_REQUIRED", "SELECTION_AUTHORIZED", "S3_EXECUTED", "S4_RELEASED", "S5_EVIDENCE_READY", "S6_CONTENT_BOUND", "S6_DOCUMENT_READY", "S7_REVIEWED", "SUBMISSION_AUTHORIZED", "CLOSED_AND_SEALED"],
            "mode": "MIGRATION",
        })
    migration_steps: list[tuple[str, Path]] = [("00_task_brief", task_brief_path), ("00_pipeline_manifest", manifest_path)]
    legacy_map = {
        "01_problem_structure": "01_problem_structure",
        "02_data_profile": "02_data_profile",
        "03_candidate_portfolio": "03_candidate_portfolio",
        "04_selection_verdict": "04_selection_verdict",
        "05_model_formulation": "05_model_spec",
        "05_model_spec": "05_model_spec",
        "05_solver_manifest": "05_solver_manifest",
        "06_solver_result": "06_solver_result",
        "06_validation_handoff": "06_validation_handoff",
        "07_validation_plan": "07_validation_plan",
        "07_validation_evidence": "07_validation_evidence",
        "07_failure_envelope": "07_failure_envelope",
        "08_release_decision": "08_release_decision",
    }
    contract_registry = registry()["artifacts"]
    migration_dir = workflow_dir / "migrated_artifacts"
    for old_id, new_id in legacy_map.items():
        entry = artifacts.get(old_id)
        if not entry:
            continue
        destination = migration_dir / contract_registry[new_id]["physical_filename"]
        migration_steps.append((new_id, copy_for_migration(Path(entry["path"]), destination)))
    blocked_reason = None
    registered: list[str] = []
    for artifact_id, path in migration_steps:
        try:
            register_artifact(workflow_dir, artifact_id, str(path))
            registered.append(artifact_id)
            while advance(workflow_dir) == OK:
                pass
        except ControlPlaneError as exc:
            blocked_reason = f"{exc.code}:{exc.detail}"
            break
    migrated_state = load_state(workflow_dir)
    report = {
        "schema_version": "migration_report.v2_1",
        "source_version": version,
        "workflow_id": original["workflow_id"],
        "registered_artifacts": registered,
        "highest_provable_stage": migrated_state["current_stage"],
        "blocked_reason": blocked_reason,
        "legacy_state_backup": str(backup.resolve()),
        "completed_at": now(),
    }
    atomic_json(workflow_dir / "migration_report.json", report)
    print("MIGRATED_HIGHEST_PROVABLE_STAGE", migrated_state["current_stage"])
    if blocked_reason:
        print("MIGRATION_STOPPED_FAIL_CLOSED", blocked_reason)
        return BLOCKED
    return OK


def status_command(workflow_dir: Path) -> int:
    state = load_state(workflow_dir)
    okay, why = effective_check(workflow_dir, state, persist_failure=False)
    output = {
        "workflow_version": state["workflow_version"],
        "workflow_id": state["workflow_id"],
        "declared_stage": state["current_stage"],
        "effective_state_valid": okay,
        "effective_state_error": why,
        "state_status": state["state_status"],
        "validation_verdict": state["validation_verdict"],
        "limitations": state["limitations"],
        "claim_restrictions": state["claim_restrictions"],
        "selection_authorized": state["selection_authorized"],
        "active_artifact_count": len(state["active_artifacts"]),
        "pending_route": state["pending_route"],
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return OK if okay else BLOCKED


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return INPUT
    command = argv[1]
    try:
        if command == "init" and len(argv) == 4:
            return init_command(Path(argv[2]).resolve(), argv[3])
        if command in {"reg", "register"} and len(argv) == 5:
            return register_artifact(Path(argv[2]).resolve(), argv[3], argv[4])
        if command == "adv" and len(argv) == 3:
            return advance(Path(argv[2]).resolve())
        if command == "check" and len(argv) == 3:
            return check_command(Path(argv[2]).resolve())
        if command == "route" and len(argv) == 4:
            return route_command(Path(argv[2]).resolve(), argv[3])
        if command == "resume" and len(argv) == 3:
            return resume_command(Path(argv[2]).resolve())
        if command == "migrate" and len(argv) == 3:
            return migrate_command(Path(argv[2]).resolve())
        if command == "close" and len(argv) == 3:
            return close_command(Path(argv[2]).resolve())
        if command == "status" and len(argv) == 3:
            return status_command(Path(argv[2]).resolve())
        print(__doc__)
        return INPUT
    except ControlPlaneError as exc:
        print(f"{exc.code}: {exc.detail}")
        return exc.exit_code
    except Exception as exc:
        print(f"CONTROL_PLANE_INTERNAL_ERROR: {type(exc).__name__}: {exc}")
        return INPUT


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
