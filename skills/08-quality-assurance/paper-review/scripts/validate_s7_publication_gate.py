#!/usr/bin/env python3
"""Independent V2.1 S7 publication gate (fail closed).

This validator consumes the signed V2.1 workflow state and its active owner
receipts. It does not reinterpret S4 science; it verifies literal verdict and
limitation propagation plus S5/S6/S7 publication evidence.

Usage:
  validate_s7_publication_gate.py --workflow-state <workflow_state.json>
      [--output <s7_publication_gate.json>]

Optional legacy path flags are accepted only as identity assertions; when
provided, each must name the exact active artifact recorded in workflow state.
Exit: 0 PASS/PASS_WITH_LIMITATIONS; 1 blocked; 2 input/integrity error.
"""
from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ORCHESTRATOR = Path.home() / ".codex" / "skills" / "modeling-workflow-orchestrator" / "scripts" / "orchestrator_v2_1.py"
ARTIFACT_IDS = {
    "--pipeline-manifest": "00_pipeline_manifest",
    "--s4-decision": "08_release_decision",
    "--figure-provenance": "09_figure_provenance",
    "--paper-text": "10_paper_source",
    "--number-report": "11_number_report",
    "--claim-gate": "11_claim_gate",
    "--reference-result": "11_reference_validation",
    "--docx": "12_paper_docx",
    "--pdf": "12_paper_pdf",
    "--render-validation": "12_render_validation",
    "--s7-review-report": "13_s7_review_report",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_orchestrator():
    if not ORCHESTRATOR.is_file():
        raise RuntimeError(f"V2.1 orchestrator missing: {ORCHESTRATOR}")
    spec = importlib.util.spec_from_file_location("cumcm_control_plane_v2_1", ORCHESTRATOR)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {ORCHESTRATOR}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def owner_detail(code: str, message: str) -> dict[str, str]:
    owner_map = {
        "VALIDATION_": ("model-validation", "S4"),
        "FIGURE_": ("scipilot-figure-cumcm", "S5_EVIDENCE_READY"),
        "NUMERIC_": ("mcm-paper-writing", "S6_CONTENT_BOUND"),
        "CLAIM_": ("mcm-paper-writing", "S6_CONTENT_BOUND"),
        "REFERENCE_": ("reference-manager", "S6_CONTENT_BOUND"),
        "RENDER_": ("mcm-paper-writing", "S6_DOCUMENT_READY"),
        "REVIEW_": ("paper-review", "S7"),
        "LIMITATION_": ("model-validation->mcm-paper-writing", "S6_CONTENT_BOUND"),
        "STATE_": ("modeling-workflow-orchestrator", "control-plane"),
        "STRUCTURAL_": ("paper-review->mcm-paper-writing", "S6_CONTENT_BOUND"),
        "ILLEGAL_": ("mcm-paper-writing", "S6_DOCUMENT_READY"),
        "UNDERWRITTEN": ("paper-review->mcm-paper-writing", "S6_CONTENT_BOUND"),
    }
    owner, route = "paper-review", "S7"
    for prefix, target in owner_map.items():
        if code.startswith(prefix):
            owner, route = target
            break
    return {"reason_code": code, "message": message, "owner": owner, "route_back": route}


def input_hashes(state: dict[str, Any]) -> dict[str, str]:
    required = [
        "00_pipeline_manifest", "08_release_decision", "09_figure_provenance",
        "11_number_report", "11_claim_gate", "11_reference_validation",
        "12_paper_docx", "12_paper_pdf", "12_render_validation", "13_s7_review_report",
    ]
    missing = [artifact_id for artifact_id in required if artifact_id not in state["active_artifacts"]]
    if missing:
        raise ValueError(f"missing active S7 dependencies: {missing}")
    return {artifact_id: state["active_artifacts"][artifact_id]["sha256"] for artifact_id in required}


def build_gate(control, workflow_dir: Path, state: dict[str, Any], validated_at: str | None = None) -> dict[str, Any]:
    reasons: list[dict[str, str]] = []
    add = lambda code, message: reasons.append(owner_detail(code, message))
    if state.get("current_stage") != "S6_DOCUMENT_READY":
        add("STATE_NOT_DOCUMENT_READY", f"current stage is {state.get('current_stage')!r}")
    s4 = control.artifact_doc(state, "08_release_decision")
    fig = control.artifact_doc(state, "09_figure_provenance")
    number = control.artifact_doc(state, "11_number_report")
    claim = control.artifact_doc(state, "11_claim_gate")
    reference = control.artifact_doc(state, "11_reference_validation")
    render = control.artifact_doc(state, "12_render_validation")
    review = control.artifact_doc(state, "13_s7_review_report")
    verdict = s4.get("verdict")
    if verdict not in {"PASS", "PASS_WITH_LIMITATIONS", "REVISE", "FAIL"}:
        add("VALIDATION_VERDICT_INVALID", f"unknown S4 verdict {verdict!r}")
    elif verdict == "FAIL":
        add("VALIDATION_S4_FAIL", "S4 FAIL is a terminal publication block")
    elif verdict == "REVISE":
        add("VALIDATION_S4_REVISE", "S4 revision is unresolved")
    if state.get("validation_verdict") != verdict:
        add("VALIDATION_STATE_MISMATCH", "workflow state and release decision differ")
    if fig.get("status") != "PASS" or fig.get("errors") or fig.get("evidence_bearing_count", 0) < 1:
        add("FIGURE_PROVENANCE_FAIL", "figure provenance is not a nonempty PASS")
    if number.get("status") != "passed" or number.get("summary", {}).get("unknown", 1) != 0:
        add("NUMERIC_PROVENANCE_FAIL", "paper numbers are not fully macro-bound")
    if claim.get("gate") != "PASS" or not claim.get("render_authorized") or claim.get("blocked") or claim.get("unresolved"):
        add("CLAIM_GATE_FAIL", "claim gate is blocked, unresolved, or unauthorized")
    if not reference.get("reference_graph_valid") or not reference.get("render_authorized"):
        add("REFERENCE_GATE_FAIL", "reference graph is invalid or unauthorized")
    if reference.get("online_required") and not reference.get("online_verified"):
        add("REFERENCE_ONLINE_REQUIRED", "online-required reference validation was not performed")
    if render.get("status") != "PASS" or render.get("visual_qa") != "PASS" or render.get("errors"):
        add("RENDER_INTEGRITY_FAIL", "render/visual QA did not pass")
    if review.get("status") not in {"PASS", "PASS_WITH_LIMITATIONS"} or review.get("blocking_findings") != 0:
        add("REVIEW_CONTENT_FAIL", "independent content review has blocking findings")
    limitations = s4.get("limitations") or []
    restrictions = s4.get("claim_restrictions") or []
    if state.get("limitations") != limitations or review.get("propagated_limitations") != limitations:
        add("LIMITATION_PROPAGATION_FAIL", "S4 limitations were not preserved exactly")
    if state.get("claim_restrictions") != restrictions or review.get("propagated_claim_restrictions") != restrictions:
        add("LIMITATION_CLAIM_RESTRICTION_FAIL", "S4 claim restrictions were not preserved exactly")

    # Structural Underwriting and False Page Inflation Gate
    pdf_entry = state.get("active_artifacts", {}).get("12_paper_pdf")
    pdf_path = Path(pdf_entry["path"]) if pdf_entry and "path" in pdf_entry else None
    if not pdf_path or not pdf_path.is_file():
        for cand_name in ("final.pdf", "paper.pdf"):
            if (workflow_dir / cand_name).is_file():
                pdf_path = workflow_dir / cand_name
                break
            if (workflow_dir / "latex" / cand_name).is_file():
                pdf_path = workflow_dir / "latex" / cand_name
                break

    if pdf_path and pdf_path.is_file():
        try:
            total_pdf_pages = 0
            all_text = ""
            try:
                import fitz
                doc = fitz.open(str(pdf_path))
                total_pdf_pages = len(doc)
                all_text = "".join(page.get_text() for page in doc)
            except Exception:
                pass
            import re
            cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", all_text))

            if total_pdf_pages > 0:
                if total_pdf_pages <= 3:
                    add("STRUCTURAL_UNDERWRITING_FAIL", f"paper total pages ({total_pdf_pages}) is underwritten (<= 3 pages toy paper)")
                elif total_pdf_pages > 3 and cjk_chars < 6000:
                    add("STRUCTURAL_UNDERWRITING_FAIL", f"paper text depth ({cjk_chars} Chinese characters) is underwritten (< 6000 chars)")

            if total_pdf_pages > 0 and re.search(r"目\s*录", all_text) and ("......" in all_text or "…" in all_text or len(re.findall(r"\d+\s*$", all_text, re.M)) >= 3):
                add("ILLEGAL_TOC_DETECTED", "paper contains illegal table of contents, violating CUMCM competition rules")
        except Exception:
            pass

    release_ready = not reasons and verdict in {"PASS", "PASS_WITH_LIMITATIONS"}
    output_verdict = verdict if release_ready else ("REVISE" if verdict == "REVISE" and len(reasons) == 1 else "FAIL")
    return {
        "schema_version": "s7_publication_gate.schema.v2_1",
        "verdict": output_verdict,
        "reason_codes": [item["reason_code"] for item in reasons],
        "details": reasons,
        "release_ready": release_ready,
        "input_hashes": input_hashes(state),
        "limitations": limitations,
        "claim_restrictions": restrictions,
        "validator_version": "S7_PUBLICATION_VALIDATOR.v2_1",
        "validated_at": validated_at or utc_now(),
    }


def validate_declared_gate(document: dict[str, Any], workflow_dir: Path, state: dict[str, Any]) -> list[str]:
    control = load_orchestrator()
    expected = build_gate(control, workflow_dir, state, document.get("validated_at"))
    if document != expected:
        fields = [name for name in expected if document.get(name) != expected.get(name)]
        raise control.ControlPlaneError("S7_GATE_RECOMPUTATION_MISMATCH", ",".join(fields))
    return ["owner_validator:s7_recomputed", "literal_s4_propagation", "render_and_review_evidence_checked"]


def option(args: list[str], name: str) -> str | None:
    if name not in args:
        return None
    index = args.index(name)
    return args[index + 1] if index + 1 < len(args) else None


def main(argv: list[str]) -> int:
    args = argv[1:]
    state_value = option(args, "--workflow-state")
    if not state_value:
        print("INPUT_ERROR --workflow-state is required")
        print(__doc__)
        return 2
    try:
        control = load_orchestrator()
        state_file = Path(state_value).resolve()
        workflow_dir = state_file.parent
        if state_file != control.state_path(workflow_dir).resolve():
            raise ValueError("workflow-state must be the canonical workflow_state.json")
        state = control.load_state(workflow_dir)
        fresh, why = control.effective_check(workflow_dir, state, persist_failure=False)
        if not fresh:
            raise ValueError(f"effective state invalid: {why}")
        for flag, artifact_id in ARTIFACT_IDS.items():
            asserted = option(args, flag)
            if asserted and Path(asserted).resolve() != Path(state["active_artifacts"][artifact_id]["path"]).resolve():
                raise ValueError(f"{flag} does not match active artifact {artifact_id}")
        gate = build_gate(control, workflow_dir, state)
        schema = control.load_schema_ref("$LOCAL/canonical_artifacts.schema.v2_1.json#/$defs/s7_publication_gate", workflow_dir)
        control.validate_schema(gate, schema, "S7_GATE_SCHEMA_INVALID")
        output_value = option(args, "--output")
        output = Path(output_value).resolve() if output_value else workflow_dir / "s7_publication_gate.json"
        control.atomic_json(output, gate)
        for item in gate["details"]:
            print(item["reason_code"], "|", item["owner"], "->", item["route_back"], "|", item["message"])
        print("S7_VERDICT =", gate["verdict"], "->", output)
        return 0 if gate["release_ready"] else 1
    except Exception as exc:
        print(f"INPUT_OR_INTEGRITY_ERROR: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
