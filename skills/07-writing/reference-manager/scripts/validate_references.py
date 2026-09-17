#!/usr/bin/env python3
"""V2.1 reference integrity gate: graph closure, identity, and online policy.

Usage: validate_references.py --in-text citations.json --bibliography bibliography.json
       --paper paper.md [--require-online] [--output reference_validation.json]

`--require-online` is a hard authorization requirement. Offline-only identity
never yields render_authorized=true in that mode. Exit 0 PASS, 1 FAIL, 2 input.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path


DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
URL_RE = re.compile(r"^https?://\S+$")


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def option(args: list[str], name: str) -> str | None:
    if name not in args:
        return None
    index = args.index(name)
    return args[index + 1] if index + 1 < len(args) else None


def identity(entry: dict) -> str:
    explicit = entry.get("identity_status") or entry.get("_source_identity")
    if explicit == "ONLINE_VERIFIED":
        return explicit
    identifier = str(entry.get("identifier") or entry.get("doi") or entry.get("url") or "")
    if identifier.startswith("10."):
        return "OFFLINE_STRUCTURALLY_VALID" if DOI_RE.match(identifier) else "INVALID"
    if identifier.startswith(("http://", "https://")):
        return "OFFLINE_STRUCTURALLY_VALID" if URL_RE.match(identifier) else "INVALID"
    return "OFFLINE_STRUCTURALLY_VALID" if entry.get("title") and entry.get("authors") and entry.get("year") and identifier else "UNVERIFIED"


def main(argv: list[str]) -> int:
    args = argv[1:]
    in_text_value = option(args, "--in-text")
    bibliography_value = option(args, "--bibliography")
    paper_value = option(args, "--paper")
    if not in_text_value or not bibliography_value or not paper_value:
        print("INPUT_ERROR --in-text, --bibliography, and --paper are required")
        print(__doc__)
        return 2
    in_text_path = Path(in_text_value).resolve()
    bibliography_path = Path(bibliography_value).resolve()
    paper_path = Path(paper_value).resolve()
    if not all(path.is_file() for path in (in_text_path, bibliography_path, paper_path)):
        print("INPUT_ERROR one or more input files are missing")
        return 2
    try:
        citations_doc = json.loads(in_text_path.read_text(encoding="utf-8-sig"))
        bibliography_doc = json.loads(bibliography_path.read_text(encoding="utf-8-sig"))
    except Exception as exc:
        print("INPUT_ERROR", exc)
        return 2
    citations = citations_doc if isinstance(citations_doc, list) else citations_doc.get("in_text_citations", [])
    references = bibliography_doc if isinstance(bibliography_doc, list) else bibliography_doc.get("references", [])
    if not isinstance(citations, list) or not isinstance(references, list) or not references:
        print("INPUT_ERROR citations/references must be nonempty lists")
        return 2
    errors: list[str] = []
    warnings: list[str] = []
    identifiers: list[str] = []
    identity_states: list[str] = []
    for entry in references:
        reference_id = entry.get("reference_id") or entry.get("key")
        if not reference_id:
            errors.append("reference entry missing reference_id")
            continue
        identifiers.append(reference_id)
        missing = [field for field in ("title", "authors", "year") if not entry.get(field)]
        if missing:
            errors.append(f"{reference_id}: missing metadata {missing}")
        state = identity(entry)
        identity_states.append(state)
        if state == "INVALID":
            errors.append(f"{reference_id}: invalid identifier syntax")
        elif state == "UNVERIFIED":
            warnings.append(f"{reference_id}: identity unverified")
    duplicates = sorted({item for item in identifiers if identifiers.count(item) > 1})
    if duplicates:
        errors.append("duplicate reference ids " + ",".join(duplicates))
    known = set(identifiers)
    for citation in citations:
        if citation not in known:
            errors.append(f"in-text citation {citation!r} missing from bibliography")
    for reference_id in known:
        if reference_id not in citations:
            warnings.append(f"unused reference {reference_id!r}")
    require_online = "--require-online" in args
    online_verified = bool(identity_states) and all(state == "ONLINE_VERIFIED" for state in identity_states)
    if require_online and not online_verified:
        errors.append("ONLINE_VERIFICATION_REQUIRED: at least one reference is not ONLINE_VERIFIED")
    graph_valid = not errors
    result = {
        "schema_version": "reference_validation.schema.v2_1",
        "reference_graph_valid": graph_valid,
        "render_authorized": graph_valid and (online_verified or not require_online),
        "citation_ids": sorted(known),
        "online_required": require_online,
        "online_verified": online_verified,
        "bibliography_sha256": sha256(bibliography_path),
        "paper_sha256": sha256(paper_path),
        "errors": errors,
        "warnings": warnings,
    }
    output_value = option(args, "--output")
    output = Path(output_value).resolve() if output_value else bibliography_path.parent / "reference_validation.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for error in errors:
        print("REFERENCE_FAIL", error)
    for warning in warnings[:12]:
        print("REFERENCE_WARN", warning)
    print("REFERENCE_GRAPH_VALID" if result["render_authorized"] else "REFERENCE_GRAPH_FAIL", "->", output)
    return 0 if result["render_authorized"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
