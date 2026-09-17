#!/usr/bin/env python3
"""F1 Numeric Bridge: paper_macro_candidates.json -> paper_macros.json (P0-01 fix).

Promotes ONLY schema-valid, provenance-complete, non-rejected candidates.
Any invalid candidate => EXIT 1 and NO macros authorized. Deterministic output
(no wall-clock fields); provenance chain preserved end-to-end.
Exit: 0 PASS | 1 VALIDATION_FAIL | 2 INPUT_ERROR
"""
import json, math, os, sys

REQUIRED = ["macro_id", "value", "source", "source_artifact", "source_locator"]
EXIT_OK, EXIT_FAIL, EXIT_INPUT = 0, 1, 2

def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)

def pointer_get(document, pointer):
    if not isinstance(pointer, str) or not pointer.startswith("/"):
        raise ValueError("source_locator must be a JSON pointer")
    current = document
    for raw in pointer.split("/")[1:]:
        token = raw.replace("~1", "/").replace("~0", "~")
        current = current[int(token)] if isinstance(current, list) else current[token]
    return current

def main(argv):
    if len(argv) < 3:
        print(__doc__); return EXIT_INPUT
    cand_path = os.path.abspath(argv[1]); out_path = os.path.abspath(argv[2])
    try:
        doc = json.load(open(cand_path, encoding="utf-8-sig"))
    except Exception as e:
        print("INPUT_ERROR unreadable candidates:", e); return EXIT_INPUT
    cands = doc.get("candidates")
    if not isinstance(cands, list) or not cands:
        print("VALIDATION_FAIL no candidates array"); return EXIT_FAIL
    base_dir = os.path.dirname(cand_path)
    macros, errors, skipped, seen = {}, [], [], {}
    cand_sha = hashlib_file(cand_path)
    for i, c in enumerate(cands):
        cid = c.get("macro_id") or ("<idx%d>" % i)
        miss = [k for k in REQUIRED if k not in c or c[k] in (None, "")]
        if miss:
            errors.append(f"{cid}: missing {miss}"); continue
        v = c["value"]
        if not is_num(v):
            errors.append(f"{cid}: value not finite numeric ({v!r})"); continue
        src_art = os.path.join(base_dir, c["source_artifact"]) \
            if not os.path.isabs(c["source_artifact"]) else c["source_artifact"]
        if not os.path.exists(src_art):
            errors.append(f"{cid}: source_artifact nonexistent: {c['source_artifact']}"); continue
        try:
            source_doc = json.load(open(src_art, encoding="utf-8-sig"))
            source_value = pointer_get(source_doc, c["source_locator"])
        except Exception as e:
            errors.append(f"{cid}: source locator cannot be resolved ({e})"); continue
        tolerance = c.get("tolerance", 0.0)
        if not isinstance(tolerance, (int, float)) or tolerance < 0:
            errors.append(f"{cid}: tolerance must be nonnegative numeric"); continue
        if not is_num(source_value) or abs(float(source_value) - float(v)) > float(tolerance):
            errors.append(f"{cid}: source value mismatch ({source_value!r} != {v!r})"); continue
        status = str(c.get("status", "APPROVED")).upper()
        if status in ("REJECTED", "BLOCKED"):
            skipped.append(cid); continue
        if status not in ("APPROVED", "UNRESOLVED"):
            errors.append(f"{cid}: unknown status {status}"); continue
        prev = seen.get(cid)
        if prev is not None and (prev["value"] != v or prev["source"] != c["source"]):
            errors.append(f"{cid}: conflicting duplicate (value/source differ)"); continue
        seen[cid] = {"value": v, "source": c["source"]}
        prec = c.get("precision")
        entry = {
            "value": v,
            "source": os.path.relpath(src_art, os.path.dirname(out_path)).replace("\\", "/") + "#" + c["source_locator"],
            "source_artifact": os.path.relpath(src_art, base_dir).replace("\\", "/"),
            "source_locator": c["source_locator"],
            "candidate_index": i,
            "tolerance": tolerance,
        }
        # number-validator contract: precision must be int 0-15 when present; omit otherwise
        if isinstance(prec, int) and not isinstance(prec, bool) and 0 <= prec <= 15:
            entry["precision"] = prec
        macros[cid] = entry
    if errors:
        for e in errors: print("VALIDATION_FAIL", e)
        print("BRIDGE_RESULT = REJECTED (%d error(s)); paper_macros NOT authorized" % len(errors))
        return EXIT_FAIL
    out = {
        "schema_version": "1.0",
        "macros": macros,
        "_bridge": {"tool": "build_paper_macros.py", "candidates_sha256": cand_sha,
                    "promoted": len(macros), "skipped_rejected": len(skipped)},
    }
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=1, ensure_ascii=False)
    print("BRIDGE_RESULT = AUTHORIZED macros=%d skipped=%d -> %s" % (len(macros), len(skipped), out_path))
    return EXIT_OK

def hashlib_file(p):
    import hashlib
    return hashlib.sha256(open(p, "rb").read()).hexdigest()

if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
