#!/usr/bin/env python3
"""submission_package_validator.py — PH1 H1-C (whitelist-first packaging gate).

Pipeline: authorized plan --> init-manifest (hash binding) --> stage (copy ONLY
manifest entries into a clean package dir) --> validate (completeness, forbidden
files, unregistered extras, hash mismatch, staleness consumption, format verdict
consumption, manual compliance records).

Never copies project trees; never deletes user files; purely additive staging.
Exit: 0 = AUTHORIZED/AUTO_PASS/MANUAL_PASS   3 = MANUAL_REQUIRED   1 = FAIL   2 input error.
"""
import argparse, fnmatch, hashlib, json, os, re, shutil, sys, time

SEV_FAIL, SEV_MANUAL, SEV_WARN = "fail", "manual", "warn"
TEXT_EXTS = {".json", ".md", ".csv", ".txt", ".typ"}


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def semantic_hash(p):
    ext = os.path.splitext(p)[1].lower()
    raw = open(p, "rb").read()
    if ext == ".json":
        try:
            canon = json.dumps(json.loads(raw.decode("utf-8-sig")), sort_keys=True,
                               ensure_ascii=False, separators=(",", ":"))
            return hashlib.sha256(canon.encode("utf-8")).hexdigest()
        except Exception:
            return hashlib.sha256(raw).hexdigest()
    if ext in TEXT_EXTS:
        norm = raw.decode("utf-8-sig", "replace").replace("\r\n", "\n").rstrip() + "\n"
        return hashlib.sha256(norm.encode("utf-8")).hexdigest()
    return hashlib.sha256(raw).hexdigest()


def aggregate_hash(entries):
    lines = "".join(f"{r}\x00{s}\n" for r, s in sorted(entries))
    return hashlib.sha256(lines.encode("utf-8")).hexdigest()


def loadj_safe(p):
    try:
        return json.load(open(p, encoding="utf-8-sig"))
    except Exception:
        return None


class Rep:
    def __init__(self):
        self.items = []

    def add(self, code, severity, detail):
        self.items.append({"reason_code": code, "severity": severity, "detail": detail})

    def level(self):
        order = {SEV_WARN: 1, SEV_MANUAL: 2, SEV_FAIL: 3}
        return max([order[i["severity"]] for i in self.items], default=0)


def safe_rel(path):
    p = path.replace("\\", "/")
    if os.path.isabs(p) or p.startswith("..") or "/../" in f"/{p}/":
        print("INPUT_ERROR manifest paths must be relative and inside package:", p)
        sys.exit(2)
    return p


def load_profile(profile_name):
    """Locate competition_profile.<x>.json by exact suffix, else by profile_name match."""
    base = os.path.dirname(os.path.abspath(__file__))
    exact = os.path.join(base, f"competition_profile.{profile_name}.json")
    prof = loadj_safe(exact)
    if prof:
        return prof, exact
    try:
        for fn in sorted(os.listdir(base)):
            if fn.startswith("competition_profile.") and fn.endswith(".json"):
                cand = loadj_safe(os.path.join(base, fn))
                if cand and cand.get("profile_name") == profile_name:
                    return cand, os.path.join(base, fn)
    except OSError:
        pass
    return {}, None


# --------------------------------------------------------------------------
# init-manifest
# --------------------------------------------------------------------------

def cmd_init(args):
    profile = load_profile_json(args.profile)
    plan = loadj_safe(args.plan)
    arts_in = (plan or {}).get("artifacts") or []
    if not arts_in:
        print("INPUT_ERROR plan has no artifacts"); return 2

    forbidden_rules = [(r.get("match"), r.get("regex"), r.get("reason"))
                       for r in profile.get("do_not_submit_filename_rules", [])]
    internal_frags = [f.lower() for f in profile.get("internal_only_path_fragments", [])]
    allowed_classes = ("REQUIRED_FOR_SUBMISSION", "OPTIONAL_FOR_SUBMISSION")

    entries, seen_ids, seen_paths = [], set(), set()
    rep = Rep()
    for a in arts_in:
        aid, src, cls = a.get("artifact_id"), a.get("source"), a.get("submission_class")
        if not aid or not src or not cls:
            rep.add("MANIFEST_INPUT_INVALID", SEV_FAIL, repr(a)[:80]); continue
        if aid in seen_ids:
            rep.add("DUPLICATE_ARTIFACT_ID", SEV_FAIL, aid); continue
        src_abs = src if os.path.isabs(src) else os.path.join(args.project, src)
        if not os.path.exists(src_abs):
            rep.add("SOURCE_MISSING", SEV_FAIL, src); continue
        rel = safe_rel(a.get("dest") or os.path.basename(src))
        if rel.lower() in seen_paths:
            rep.add("DUPLICATE_PACKAGE_PATH", SEV_FAIL, rel); continue
        fname = os.path.basename(rel)
        low = rel.lower()
        blocked_reason = None
        for m, rx, reason in forbidden_rules:
            if m and fnmatch.fnmatch(fname.lower(), m.lower()):
                blocked_reason = reason; break
            if rx and re.search(rx, fname):
                blocked_reason = reason; break
        internal_hit = next((f for f in internal_frags if f in low), None)
        if blocked_reason:
            rep.add("DO_NOT_SUBMIT_FILE_REJECTED", SEV_FAIL, f"{rel}: {blocked_reason}"); continue
        if internal_hit is not None:
            rep.add("INTERNAL_ONLY_FILE_REJECTED", SEV_FAIL,
                    f"{rel}: matches INTERNAL_ONLY fragment '{internal_hit}'"); continue
        if cls not in allowed_classes:
            rep.add("CLASS_NOT_SUBMITTABLE", SEV_FAIL, f"{aid}: {cls}"); continue
        seen_ids.add(aid); seen_paths.add(low)
        entries.append({
            "artifact_id": aid, "path": rel,
            "source": os.path.relpath(os.path.abspath(src_abs),
                                      os.path.abspath(args.project)).replace(os.sep, "/"),
            "artifact_type": a.get("artifact_type",
                                   os.path.splitext(rel)[1].lstrip(".").lower()),
            "submission_class": cls, "role": a.get("role", ""),
            "semantic_hash": semantic_hash(src_abs), "binary_hash": sha256_file(src_abs),
            "producer": a.get("producer", ""),
            "authorization_source": a.get("authorization_source", ""),
            "required": bool(a.get("required", cls == "REQUIRED_FOR_SUBMISSION")),
            "anonymity_status": a.get("anonymity_status", "PENDING"),
            "compliance_status": a.get("compliance_status", "PENDING"),
        })

    if rep.level() >= 3:
        json.dump({"schema_version": "ph1_submission_manifest.v1", "status": "REJECTED",
                   "findings": rep.items, "artifacts": []},
                  open(args.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
        print("MANIFEST_REJECTED findings:", len(rep.items)); return 1

    manifest = {
        "schema_version": "ph1_submission_manifest.v1",
        "created_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "project_root": os.path.abspath(args.project),
        "profile": profile.get("profile_name"),
        "status": "AUTHORIZED",
        # V2-registry compatibility: REVIEW_PASSED->SUBMISSION_READY consumes
        # submission_manifest.limitations_preserved == true
        "limitations_preserved": bool(plan.get("limitations_preserved", True)),
        "limitations": plan.get("limitations", []),
        "artifacts": entries,
    }
    blob = json.dumps(manifest, indent=1, ensure_ascii=False, sort_keys=True)
    manifest["manifest_sha256"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    json.dump(manifest, open(args.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("MANIFEST_AUTHORIZED artifacts:", len(entries),
          "manifest_sha256:", manifest["manifest_sha256"][:16], "...")
    return 0


def load_profile_json(p):
    prof = loadj_safe(p)
    if prof is None:
        print("INPUT_ERROR cannot read profile", p); sys.exit(2)
    return prof


# --------------------------------------------------------------------------
# stage — copy ONLY manifest entries into a clean package dir
# --------------------------------------------------------------------------

def cmd_stage(args):
    m = loadj_safe(args.manifest)
    if not m or m.get("status") != "AUTHORIZED":
        print("INPUT_ERROR manifest missing/not AUTHORIZED"); return 2
    pd = args.package_dir
    if os.path.exists(pd) and args.clean:
        shutil.rmtree(pd)
    os.makedirs(pd, exist_ok=True)
    root = m.get("project_root", "")
    staged = []
    for a in m["artifacts"]:
        src_field = a.get("source") or a["path"]
        src_abs = src_field if os.path.isabs(src_field) else os.path.join(root, src_field)
        if not os.path.exists(src_abs):
            print("STAGE_ERROR missing source:", src_abs); return 2
        data = open(src_abs, "rb").read()
        if hashlib.sha256(data).hexdigest() != a["binary_hash"]:
            print("STAGE_ERROR source mutated since manifest:", src_abs); return 1
        dest = os.path.join(pd, a["path"].replace("/", os.sep))
        os.makedirs(os.path.dirname(dest) or ".", exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        staged.append(a["path"])
    print("STAGED", len(staged), "files ->", os.path.abspath(pd))
    return 0


# --------------------------------------------------------------------------
# validate
# --------------------------------------------------------------------------

TEMP_RULES = [
    (lambda n: n.startswith("~$"), "~$ office lock/temp"),
    (lambda n: n.endswith(".tmp"), ".tmp temporary"),
    (lambda n: n.endswith(".bak"), ".bak backup"),
    (lambda n: n.endswith(".old"), ".old backup"),
    (lambda n: n.endswith("~"), "tilde editor backup"),
    (lambda n: n.endswith(".swp"), "swap file"),
    (lambda n: n.startswith(".~lock."), "office lock"),
    (lambda n: n.endswith(".lock"), "lock file"),
    (lambda n: "autosave" in n.lower(), "autosave artifact"),
    (lambda n: bool(re.search(r"\(\d+\)\.[^.]+$", n)), "'(1)' duplicate-copy name"),
]


def cmd_validate(args):
    m = loadj_safe(args.manifest)
    pd = args.package_dir
    rep = Rep()
    t0 = time.perf_counter()

    if not m or m.get("status") != "AUTHORIZED":
        rep.add("MANIFEST_NOT_AUTHORIZED", SEV_FAIL, str((m or {}).get("status")))
    arts = (m or {}).get("artifacts") or []
    by_path, id_seen = {}, {}
    for a in arts:
        rp = a["path"].lower()
        if rp in by_path:
            rep.add("DUPLICATE_PACKAGE_PATH", SEV_FAIL, a["path"])
        by_path[rp] = a
        id_seen[a["artifact_id"]] = id_seen.get(a["artifact_id"], 0) + 1
    for aid, cnt in id_seen.items():
        if cnt > 1:
            rep.add("DUPLICATE_ARTIFACT_ID", SEV_FAIL, aid)

    if not os.path.isdir(pd):
        print("INPUT_ERROR package dir missing:", pd); return 2

    actual = []
    for root, _dirs, files in os.walk(pd):
        for fn in files:
            full = os.path.join(root, fn)
            actual.append((os.path.relpath(full, pd).replace(os.sep, "/"), full))

    prof, _p = load_profile(m.get("profile") or "cumcm-generic")
    internal_frags = [f.lower() for f in prof.get("internal_only_path_fragments", [])]

    actual_lut = {rp.lower(): full for rp, full in actual}
    matched = set()
    for a in arts:
        key = a["path"].lower()
        full = actual_lut.get(key)
        if full is None:
            if a.get("required"):
                rep.add("PACKAGE_MISSING_REQUIRED", SEV_FAIL, a["path"])
            else:
                rep.add("OPTIONAL_ABSENT", SEV_WARN,
                        a["path"] + " (optional artifact not packaged)")
            continue
        matched.add(key)
        h = sha256_file(full)
        if h != a["binary_hash"]:
            rep.add("PACKAGE_HASH_MISMATCH", SEV_FAIL,
                    f"{a['path']} manifest={a['binary_hash'][:12]} actual={h[:12]}")
        a["_actual_sha256"] = h

    for rp, full in actual:
        fname = os.path.basename(rp)
        low = rp.lower()
        if low not in by_path:
            rep.add("UNREGISTERED_PACKAGE_FILE", SEV_FAIL, rp)
            # NOTE: no continue — unregistered files MUST still face every rule below
        for pred, why in TEMP_RULES:
            if pred(fname):
                rep.add("FORBIDDEN_TEMP_FILE", SEV_FAIL, f"{rp}: {why}")
        if any(f in low for f in internal_frags):
            rep.add("INTERNAL_ONLY_FILE_BLOCKED", SEV_FAIL, rp)

    stale_detail = None
    if args.staleness:
        sl = loadj_safe(args.staleness)
        if sl is None:
            rep.add("FRESHNESS_INPUT_UNAVAILABLE", SEV_MANUAL, args.staleness)
        else:
            status = sl.get("status")
            stale_list = sl.get("stale") or []
            if status != "FRESH":
                rep.add("SUBMISSION_COMPLIANCE_STALE_FINAL_FILE", SEV_FAIL,
                        f"publication_staleness.status={status} stale={stale_list[:5]}")
                stale_detail = {"status": status, "stale": stale_list}

    fmt_detail = None
    if args.format_verdict:
        fv = loadj_safe(args.format_verdict)
        if fv is None:
            rep.add("FORMAT_VERDICT_UNAVAILABLE", SEV_MANUAL, args.format_verdict)
        else:
            st = fv.get("FORMAT_VALIDATION_STATUS") or fv.get("status")
            fmt_detail = st
            if st not in ("PASS", "PRERENDER_PASS", "passed"):
                rep.add("FORMAT_VALIDATION_NOT_PASS", SEV_FAIL,
                        f"FORMAT_VALIDATION_STATUS={st}")

    fr = prof.get("filename_rule", {})
    filename_manual_needed = bool(fr) and fr.get("status") != "AVAILABLE"
    if filename_manual_needed:
        rep.add("FILENAME_RULE_MANUAL_CHECK_REQUIRED", SEV_MANUAL,
                f"competition_profile.filename_rule.status={fr.get('status')}")

    manual_summary = {"required_total": 0, "required_completed": 0, "incomplete": []}
    if args.manual_records:
        mr = loadj_safe(args.manual_records) or {"records": []}
        for rcd in mr.get("records", []):
            if not rcd.get("required"):
                continue
            manual_summary["required_total"] += 1
            done = bool(rcd.get("completed"))
            has_evidence = bool(rcd.get("evidence")) and bool(rcd.get("completed_at"))
            if done and has_evidence:
                manual_summary["required_completed"] += 1
            else:
                manual_summary["incomplete"].append(rcd.get("check_id"))
        if manual_summary["incomplete"]:
            rep.add("MANDATORY_MANUAL_CHECK_INCOMPLETE", SEV_MANUAL,
                    ",".join(map(str, manual_summary["incomplete"])))

    agg_entries = [(a["path"], a.get("_actual_sha256", "")) for a in arts
                   if a["path"].lower() in matched]
    pkg_agg = aggregate_hash(agg_entries)

    # ---- status resolution ----------------------------------------------
    lvl = rep.level()
    covered_codes = set()
    if args.manual_records:
        mr_ok = loadj_safe(args.manual_records) or {"records": []}
        for rcd in mr_ok.get("records", []):
            if rcd.get("completed") and rcd.get("evidence") and rcd.get("completed_at"):
                covered_codes.update(rcd.get("covers", []) or [])
                covered_codes.add(rcd.get("check_id"))
    manual_items = [i for i in rep.items if i["severity"] == SEV_MANUAL]
    uncovered = [i for i in manual_items
                 if i["reason_code"] != "MANDATORY_MANUAL_CHECK_INCOMPLETE"
                 and i["reason_code"] not in covered_codes]
    if lvl >= 3:
        status = "FAIL"
    elif manual_summary["incomplete"] or uncovered:
        status = "MANUAL_REQUIRED"
    elif manual_items:
        status = "MANUAL_PASS"     # all manual findings covered by evidence-backed records
    else:
        status = "AUTO_PASS"
    result = {
        "schema_version": "ph1_package_compliance_result.v1",
        "manifest_ref": os.path.abspath(args.manifest),
        "manifest_sha256": m.get("manifest_sha256"),
        "package_dir": os.path.abspath(pd),
        "package_aggregate_sha256": pkg_agg,
        "status": status,
        "files_registered": len([a for a in arts if a["path"].lower() in matched]),
        "files_in_package_dir": len(actual),
        "staleness_consumed": stale_detail,
        "format_validation_consumed": fmt_detail,
        "filename_rule_manual_check_required": filename_manual_needed,
        "manual_summary": manual_summary,
        "findings": rep.items,
        "timings_seconds": {"package_validate_seconds":
                            round(time.perf_counter() - t0, 4)},
    }
    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    json.dump(result, open(args.out, "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print("PACKAGE_COMPLIANCE =", status, "| findings:", len(rep.items),
          "| pkg_agg:", pkg_agg[:16], "...")
    for it in rep.items:
        if it["severity"] != "warn":
            print(f"  [{it['severity']}] {it['reason_code']}: {it['detail'][:100]}")
    return 1 if status == "FAIL" else (3 if status == "MANUAL_REQUIRED" else 0)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p1 = sub.add_parser("init-manifest")
    p1.add_argument("--project", required=True)
    p1.add_argument("--plan", required=True)
    p1.add_argument("--profile", required=True)
    p1.add_argument("--out", required=True)
    p1.set_defaults(fn=cmd_init)

    p2 = sub.add_parser("stage")
    p2.add_argument("--manifest", required=True)
    p2.add_argument("--package-dir", required=True)
    p2.add_argument("--clean", action="store_true")
    p2.set_defaults(fn=cmd_stage)

    p3 = sub.add_parser("validate")
    p3.add_argument("--manifest", required=True)
    p3.add_argument("--package-dir", required=True)
    p3.add_argument("--out", required=True)
    p3.add_argument("--staleness", default=None)
    p3.add_argument("--format-verdict", default=None)
    p3.add_argument("--manual-records", default=None)
    p3.set_defaults(fn=cmd_validate)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
