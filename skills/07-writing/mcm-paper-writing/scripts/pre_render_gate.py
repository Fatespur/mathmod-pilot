#!/usr/bin/env python3
"""V2.1 official pre-render authorization entry.

This gate re-executes the number, reference, and claim validators against the
currently signed workflow artifacts. It never authorizes from pre-existing
summary labels alone.

Usage: pre_render_gate.py --workflow-state workflow_state.json
       [--output pre_render_authorization.json] [--non-production]
       [--run-generator -- <cumcm_word_generator arguments>]

NON_PRODUCTION always emits authorized=false with a machine-readable label.
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
ORCHESTRATOR = Path.home() / ".codex" / "skills" / "modeling-workflow-orchestrator" / "scripts" / "orchestrator_v2_1.py"
NUMBER = HERE / "paper_number_validator.py"
CLAIM = HERE / "validate_claim_evidence.py"
REFERENCE = Path.home() / ".codex" / "skills" / "reference-manager" / "scripts" / "validate_references.py"
GENERATOR = HERE / "cumcm_word_generator.py"
DEPENDENCIES = [
    "08_release_decision", "11_in_text_citations", "11_paper_macros", "11_number_report",
    "11_reference_validation", "11_section_evidence_map", "11_claim_gate",
]


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


def run(command: list[str]) -> tuple[int, str]:
    result = subprocess.run(command, capture_output=True, text=True)
    return result.returncode, result.stdout + result.stderr


def stable_equal(left: dict, right: dict, fields: list[str]) -> bool:
    return all(left.get(field) == right.get(field) for field in fields)


def main(argv: list[str]) -> int:
    args = argv[1:]
    state_value = option(args, "--workflow-state")
    if not state_value:
        print("INPUT_ERROR --workflow-state is required")
        print(__doc__)
        return 2
    try:
        control = load_control()
        state_path = Path(state_value).resolve()
        workflow_dir = state_path.parent
        state = control.load_state(workflow_dir)
        fresh, why = control.effective_check(workflow_dir, state, persist_failure=False)
        if not fresh:
            raise ValueError(f"effective state invalid: {why}")
        if state["current_stage"] != "S6_CONTENT_BOUND":
            raise ValueError(f"pre-render requires S6_CONTENT_BOUND, got {state['current_stage']}")
        missing = [artifact_id for artifact_id in DEPENDENCIES if artifact_id not in state["active_artifacts"]]
        if missing:
            raise ValueError(f"missing pre-render dependencies: {missing}")
        active = state["active_artifacts"]
        non_production = "--non-production" in args or os.environ.get("R7B_NON_PRODUCTION") == "1"
        checks: list[str] = []
        authorized = False
        if non_production:
            checks.append("NON_PRODUCTION_BYPASS_BLOCKED_FROM_RELEASE")
        else:
            with tempfile.TemporaryDirectory(prefix="cumcm_v2_1_prerender_") as temp_value:
                temp_dir = Path(temp_value)
                number_output = temp_dir / "paper_number_report.json"
                rc, text = run([
                    sys.executable, str(NUMBER), "--paper", active["10_paper_source"]["path"],
                    "--macros", active["11_paper_macros"]["path"], "--report", str(number_output),
                ])
                if rc != 0:
                    raise ValueError("number revalidation failed: " + text[-500:])
                recomputed_number = json.loads(number_output.read_text(encoding="utf-8"))
                declared_number = control.artifact_doc(state, "11_number_report")
                if not stable_equal(recomputed_number, declared_number, ["status", "summary", "paper_sha256", "macros_sha256"]):
                    raise ValueError("number report differs from fresh revalidation")
                checks.append("number_validator_reexecuted")

                reference_output = temp_dir / "reference_validation.json"
                declared_reference = control.artifact_doc(state, "11_reference_validation")
                reference_command = [
                    sys.executable, str(REFERENCE),
                    "--in-text", active["11_in_text_citations"]["path"],
                    "--bibliography", active["10_bibliography"]["path"],
                    "--paper", active["10_paper_source"]["path"],
                    "--output", str(reference_output),
                ]
                if declared_reference.get("online_required"):
                    reference_command.append("--require-online")
                rc, text = run(reference_command)
                if rc != 0:
                    raise ValueError("reference revalidation failed: " + text[-500:])
                recomputed_reference = json.loads(reference_output.read_text(encoding="utf-8"))
                if recomputed_reference != declared_reference:
                    raise ValueError("reference result differs from fresh revalidation")
                checks.append("reference_validator_reexecuted")

                claim_output = temp_dir / "claim_gate_result.json"
                rc, text = run([
                    sys.executable, str(CLAIM), "--workflow-state", str(state_path),
                    "--map", active["11_section_evidence_map"]["path"], "--output", str(claim_output),
                ])
                if rc != 0:
                    raise ValueError("claim revalidation failed: " + text[-500:])
                recomputed_claim = json.loads(claim_output.read_text(encoding="utf-8"))
                declared_claim = control.artifact_doc(state, "11_claim_gate")
                if recomputed_claim != declared_claim:
                    raise ValueError("claim result differs from fresh revalidation")
                checks.append("claim_validator_reexecuted")
            checks.append("effective_receipt_freshness_rechecked")
            authorized = True
        result = {
            "schema_version": "pre_render_authorization.schema.v2_1",
            "authorized": authorized,
            "production_mode": "NON_PRODUCTION" if non_production else "PRODUCTION",
            "revalidated": True,
            "input_hashes": {artifact_id: active[artifact_id]["sha256"] for artifact_id in DEPENDENCIES},
            "checks": checks,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        output_value = option(args, "--output")
        output = Path(output_value).resolve() if output_value else workflow_dir / "pre_render_authorization.json"
        output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        if not authorized:
            print("PRE_RENDER_NON_PRODUCTION_BLOCKED ->", output)
            return 1
        print("PRE_RENDER_AUTHORIZED ->", output)
        if "--run-generator" in args:
            separator = args.index("--") if "--" in args else len(args)
            generator_args = args[separator + 1:] if separator < len(args) else []
            completed = subprocess.run([sys.executable, str(GENERATOR), *generator_args])
            return completed.returncode
        return 0
    except Exception as exc:
        print(f"PRE_RENDER_INPUT_OR_INTEGRITY_ERROR: {type(exc).__name__}: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
