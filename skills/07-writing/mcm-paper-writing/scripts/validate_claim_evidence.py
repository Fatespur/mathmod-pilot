#!/usr/bin/env python3
"""V2.1 claim gate with claim-id, citation-id, and evidence-hash closure.

Usage: validate_claim_evidence.py --workflow-state workflow_state.json
       --map section_evidence_map.json [--output claim_gate_result.json]

Every claim must have a unique id, resolve to active artifact ids, and resolve
all citation ids against the active reference-validation result. Exit 0/1/2.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path


ORCHESTRATOR = Path.home() / ".codex" / "skills" / "modeling-workflow-orchestrator" / "scripts" / "orchestrator_v2_1.py"
TYPES = {"empirical", "methodological", "theoretical", "literature", "limitation"}
STATUSES = {"VERIFIED", "BLOCKED", "UNRESOLVED", "NOT_APPLICABLE"}
DEPENDENCIES = ["08_release_decision", "09_figure_manifest", "10_paper_source", "11_paper_macros", "11_reference_validation", "11_section_evidence_map"]


def option(args: list[str], name: str) -> str | None:
    if name not in args:
        return None
    index = args.index(name)
    return args[index + 1] if index + 1 < len(args) else None


def load_control():
    spec = importlib.util.spec_from_file_location("cumcm_control_plane_v2_1", ORCHESTRATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ORCHESTRATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def macro_ids(document: dict) -> set[str]:
    result: set[str] = set()
    def walk(node, prefix=""):
        if not isinstance(node, dict):
            return
        if "value" in node and "source" in node:
            result.add(prefix)
            return
        for key, value in node.items():
            walk(value, f"{prefix}.{key}" if prefix else key)
    walk(document.get("macros", {}))
    return result


def main(argv: list[str]) -> int:
    args = argv[1:]
    state_value = option(args, "--workflow-state")
    map_value = option(args, "--map")
    if not state_value or not map_value:
        print("INPUT_ERROR --workflow-state and --map are required")
        print(__doc__)
        return 2
    try:
        control = load_control()
        state_path = Path(state_value).resolve()
        workflow_dir = state_path.parent
        state = control.load_state(workflow_dir)
        fresh, why = control.effective_check(workflow_dir, state, persist_failure=False)
        if not fresh:
            raise ValueError(f"invalid effective state: {why}")
        missing = [artifact_id for artifact_id in DEPENDENCIES if artifact_id not in state["active_artifacts"]]
        if missing:
            raise ValueError(f"missing claim dependencies: {missing}")
        mapping = json.loads(Path(map_value).read_text(encoding="utf-8-sig"))
        claims = mapping.get("claims") if isinstance(mapping, dict) else mapping
        if not isinstance(claims, list) or not claims:
            raise ValueError("claims[] must be nonempty")
        macros = control.artifact_doc(state, "11_paper_macros")
        figures = control.artifact_doc(state, "09_figure_manifest")
        references = control.artifact_doc(state, "11_reference_validation")
        known_macros = macro_ids(macros)
        known_figures = {item["figure_id"] for item in figures["figures"]}
        known_citations = set(references["citation_ids"])
        active = state["active_artifacts"]
        errors: list[str] = []
        bindings: list[dict] = []
        seen: set[str] = set()
        blocked = unresolved = 0
        for claim in claims:
            claim_id = claim.get("claim_id")
            if not isinstance(claim_id, str) or not claim_id:
                errors.append("claim missing claim_id")
                continue
            if claim_id in seen:
                errors.append(f"{claim_id}: duplicate claim_id")
                continue
            seen.add(claim_id)
            claim_type, status = claim.get("claim_type"), claim.get("status")
            if claim_type not in TYPES:
                errors.append(f"{claim_id}: invalid claim_type {claim_type!r}")
            if status not in STATUSES:
                errors.append(f"{claim_id}: invalid status {status!r}")
            evidence_ids = claim.get("evidence_ids") or []
            citation_ids = claim.get("citation_ids") or []
            declared_macros = claim.get("macro_ids") or []
            declared_figures = claim.get("figure_ids") or []
            if not evidence_ids:
                errors.append(f"{claim_id}: evidence_ids must be nonempty")
            unknown_evidence = [item for item in evidence_ids if item not in active]
            unknown_citations = [item for item in citation_ids if item not in known_citations]
            unknown_macros = [item for item in declared_macros if item not in known_macros]
            unknown_figures = [item for item in declared_figures if item not in known_figures]
            if unknown_evidence:
                errors.append(f"{claim_id}: unknown evidence ids {unknown_evidence}")
            if unknown_citations:
                errors.append(f"{claim_id}: unknown citation ids {unknown_citations}")
            if unknown_macros:
                errors.append(f"{claim_id}: unknown macro ids {unknown_macros}")
            if unknown_figures:
                errors.append(f"{claim_id}: unknown figure ids {unknown_figures}")
            if claim_type == "empirical" and not declared_macros:
                errors.append(f"{claim_id}: empirical claim requires macro_ids")
            if claim_type == "literature" and not citation_ids:
                errors.append(f"{claim_id}: literature claim requires citation_ids")
            if status == "BLOCKED":
                blocked += 1
                errors.append(f"{claim_id}: status BLOCKED")
            if status == "UNRESOLVED":
                unresolved += 1
                errors.append(f"{claim_id}: status UNRESOLVED")
            bindings.append({
                "claim_id": claim_id,
                "evidence_hashes": [active[item]["sha256"] for item in evidence_ids if item in active],
                "citation_ids": citation_ids,
                "status": "VERIFIED" if status == "VERIFIED" and not any((unknown_evidence, unknown_citations, unknown_macros, unknown_figures)) else "UNRESOLVED",
            })
        gate = "PASS" if not errors and blocked == 0 and unresolved == 0 else "FAIL"
        result = {
            "schema_version": "claim_gate.v2_1",
            "gate": gate,
            "render_authorized": gate == "PASS",
            "claims_total": len(seen),
            "blocked": blocked,
            "unresolved": unresolved,
            "claim_bindings": bindings,
            "errors": errors,
            "input_hashes": {artifact_id: active[artifact_id]["sha256"] for artifact_id in DEPENDENCIES},
        }
        output_value = option(args, "--output")
        output = Path(output_value).resolve() if output_value else Path(map_value).resolve().parent / "claim_gate_result.json"
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        for error in errors[:25]:
            print("CLAIM_FAIL", error)
        print("CLAIM_GATE_PASS" if gate == "PASS" else "CLAIM_GATE_FAIL", f"(blocked={blocked},unresolved={unresolved}) ->", output)
        return 0 if gate == "PASS" else 1
    except Exception as exc:
        print(f"INPUT_ERROR {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
