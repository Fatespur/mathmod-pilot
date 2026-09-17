#!/usr/bin/env python3
"""Validate a V2.1 figure manifest and emit a formal provenance report.

Usage: validate_figure_provenance.py <figure_manifest.json> [--output report.json]
At least one EVIDENCE_BEARING figure is mandatory. Every declared source,
generator, and output hash is recomputed. Exit 0 PASS, 1 FAIL, 2 input error.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def resolve(base: Path, value: str) -> Path:
    path = Path(value)
    return path.resolve() if path.is_absolute() else (base / path).resolve()


def evaluate(manifest_path: Path) -> tuple[dict[str, Any], int]:
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        raise ValueError(f"unreadable manifest: {exc}") from exc
    if not isinstance(manifest, dict) or manifest.get("schema_version") != "figure_manifest.schema.v2_1" or not isinstance(manifest.get("figures"), list):
        raise ValueError("figure_manifest.schema.v2_1 with figures[] is required")
    errors: list[str] = []
    figures = manifest["figures"]
    evidence_count = 0
    ids: set[str] = set()
    for figure in figures:
        if not isinstance(figure, dict):
            errors.append("figure entry must be an object")
            continue
        figure_id = str(figure.get("figure_id") or "<missing-id>")
        if figure_id in ids:
            errors.append(f"{figure_id}: duplicate figure_id")
        ids.add(figure_id)
        figure_type = figure.get("figure_type")
        if figure_type not in {"EVIDENCE_BEARING", "EXPLANATORY"}:
            errors.append(f"{figure_id}: invalid figure_type")
            continue
        if figure_type == "EVIDENCE_BEARING":
            evidence_count += 1
        if not figure.get("claim_ids"):
            errors.append(f"{figure_id}: claim_ids must be nonempty")
        for path_field, hash_field in (
            ("source_data_artifact", "source_hash"),
            ("generator_source", "generator_hash"),
            ("output_file", "output_hash"),
        ):
            value, expected = figure.get(path_field), figure.get(hash_field)
            if not value or not expected:
                errors.append(f"{figure_id}: missing {path_field}/{hash_field}")
                continue
            path = resolve(manifest_path.parent, value)
            if not path.is_file():
                errors.append(f"{figure_id}: {path_field} does not exist")
            elif sha256(path) != expected:
                errors.append(f"{figure_id}: {hash_field} mismatch")
    if not figures:
        errors.append("figure manifest is empty")
    if evidence_count < 1:
        errors.append("at least one EVIDENCE_BEARING figure is required")
    report = {
        "schema_version": "figure_provenance_report.schema.v2_1",
        "status": "PASS" if not errors else "FAIL",
        "manifest_sha256": sha256(manifest_path),
        "figures_checked": len(figures),
        "evidence_bearing_count": evidence_count,
        "errors": errors,
        "validated_at": datetime.now(timezone.utc).isoformat(),
    }
    return report, 0 if not errors else 1


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    manifest_path = Path(argv[1]).resolve()
    output = None
    if "--output" in argv:
        index = argv.index("--output")
        output = Path(argv[index + 1]).resolve() if index + 1 < len(argv) else None
    if not manifest_path.is_file() or output is None and "--output" in argv:
        print("INPUT_ERROR missing manifest/output")
        return 2
    try:
        report, exit_code = evaluate(manifest_path)
    except ValueError as exc:
        print("INPUT_ERROR", exc)
        return 2
    output = output or manifest_path.parent / "figure_provenance_report.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("FIGURE_PROVENANCE", report["status"], f"(evidence_bearing={report['evidence_bearing_count']})", "->", output)
    for error in report["errors"][:20]:
        print("FIG_FAIL", error)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
