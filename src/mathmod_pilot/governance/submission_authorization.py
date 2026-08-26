#!/usr/bin/env python3
"""submission_authorization.py — PH1 H1-E (authorization binding + freeze integrity).

External compliance wrapper over the FROZEN orchestrator_v2 state machine. This
tool never modifies orchestrator_v2.py / v2_transition_registry.json / owner
routing / schemas. It binds SUBMISSION_READY authorization to concrete content
hashes and detects tampering of the CLOSED record.

Commands:
  bind      Bind a candidate SUBMISSION_READY authorization at REVIEW_PASSED.
            Refuses unless: declared stage matches, anonymity verdict acceptable,
            package compliance acceptable, mandatory manual records complete,
            review verdict PASS/PASS_WITH_LIMITATIONS, freshness contract FRESH.
  verify    Recompute every bound hash; AUTHORIZATION_STALE on any drift.
  audit-transition  If declared state is SUBMISSION_READY/CLOSED, a valid
            authorization MUST cover it (forged-transition detection).
  pre-close-seal   At SUBMISSION_READY: seal authorization + pre-close state so
            that post-CLOSED tamper checks are possible without touching V2 core.
  freeze-check     Post-CLOSED integrity verification (CLOSED_RECORD_INVALID /
            FREEZE_RECORD_TAMPERED detection).

Exit: 0 ok | 1 blocked/invalid | 2 input error.
"""
import argparse, hashlib, json, os, sys, time


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def loadj(p):
    try:
        return json.load(open(p, encoding="utf-8-sig"))
    except Exception:
        return None


def savej(p, obj):
    d = os.path.dirname(os.path.abspath(p))
    os.makedirs(d, exist_ok=True)
    json.dump(obj, open(p, "w", encoding="utf-8"), indent=1, ensure_ascii=False)


def st_path(wd):
    return os.path.join(wd, "workflow_state.json")


def auth_path(wd):
    return os.path.join(wd, "submission_authorization.json")


def seal_path(wd):
    return os.path.join(wd, "ph1_freeze_seal.json")


def frz_path(wd):
    return os.path.join(wd, "release_freeze_record.json")


def fail(msg, code=1):
    print(msg)
    return code


# --------------------------------------------------------------------------
# bind
# --------------------------------------------------------------------------

def cmd_bind(a):
    wd = a.wf_dir
    st = loadj(st_path(wd))
    if not st:
        return fail("INPUT_ERROR no workflow_state", 2)
    if st.get("current_stage") != a.expect_stage:
        return fail(f"BIND_REFUSED current_stage={st.get('current_stage')} != {a.expect_stage}")
    anon = loadj(a.anonymity_result)
    comp = loadj(a.compliance_result)
    review = loadj(a.review_verdict)
    manual = loadj(a.manual_records) or {"records": []}
    if not anon or not comp or not review:
        return fail("INPUT_ERROR anonymity/compliance/review artifacts unreadable", 2)

    anon_status = anon.get("status")
    if anon_status not in ("PASS", "PASS_WITH_MANUAL_REVIEW"):
        return fail(f"BIND_REFUSED anonymity status={anon_status}")

    # every manual-review reason code must be covered by a completed manual record
    covered = set()
    for r in manual.get("records", []):
        if r.get("completed") and r.get("evidence") and r.get("completed_at"):
            covered.update(r.get("covers", []) or [])
            covered.add(r.get("check_id"))
    uncovered = [c for c in anon.get("manual_review_check_ids_needed", [])
                 if c not in covered]
    if uncovered:
        return fail("BIND_REFUSED anonymity MANUAL_REVIEW uncovered by completed "
                    f"manual records: {uncovered}")

    comp_status = comp.get("status")
    if comp_status not in ("AUTO_PASS", "MANUAL_PASS"):
        return fail(f"BIND_REFUSED package compliance status={comp_status}")
    ms = comp.get("manual_summary") or {}
    if ms.get("incomplete"):
        return fail("BIND_REFUSED mandatory manual checks incomplete: "
                    + ",".join(map(str, ms["incomplete"])))

    verdict = review.get("verdict")
    if verdict not in ("PASS", "PASS_WITH_LIMITATIONS"):
        return fail(f"BIND_REFUSED review verdict={verdict}")

    sl = loadj(a.staleness) if a.staleness else None
    if a.staleness:
        if sl is None:
            return fail("INPUT_ERROR staleness artifact unreadable", 2)
        if sl.get("status") != "FRESH":
            return fail(f"BIND_REFUSED freshness contract status={sl.get('status')}")

    final_hashes = {}
    for p in a.final_doc or []:
        if not os.path.exists(p):
            return fail("INPUT_ERROR final doc missing: " + p, 2)
        final_hashes[os.path.basename(p)] = sha256_file(p)

    auth = {
        "schema_version": "ph1_submission_authorization.v1",
        "workflow_id": st.get("workflow_id"),
        "state_at_binding": st.get("current_stage"),
        "bound_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "bindings": {
            "submission_manifest_hash": (sha256_file(a.manifest)
                                         if os.path.exists(a.manifest) else None),
            "anonymity_result_hash": sha256_file(a.anonymity_result),
            "compliance_result_hash": sha256_file(a.compliance_result),
            "manual_records_hash": sha256_file(a.manual_records)
                                   if a.manual_records and os.path.exists(a.manual_records) else None,
            "review_verdict_hash": sha256_file(a.review_verdict),
            "staleness_hash": sha256_file(a.staleness) if a.staleness else None,
            "final_document_hashes": final_hashes,
            # verification hints (internal; absolute paths like orchestrator artifacts)
            "_paths": {
                "manifest": os.path.abspath(a.manifest),
                "anonymity": os.path.abspath(a.anonymity_result),
                "compliance": os.path.abspath(a.compliance_result),
                "manual": (os.path.abspath(a.manual_records)
                           if a.manual_records and os.path.exists(a.manual_records) else None),
                "review": os.path.abspath(a.review_verdict),
                "staleness": os.path.abspath(a.staleness) if a.staleness else None,
            },
            "_final_dirs": [os.path.dirname(os.path.abspath(p)) for p in (a.final_doc or [])],
        },
        "accepts": {
            "anonymity_status": anon_status,
            "package_compliance_status": comp_status,
            "review_verdict": verdict,
        },
        "authorized_transition": "REVIEW_PASSED->SUBMISSION_READY",
    }
    out = a.out or auth_path(wd)
    savej(out, auth)
    print("SUBMISSION_AUTHORIZATION_BOUND ->", os.path.abspath(out))
    return 0


# --------------------------------------------------------------------------
# verify
# --------------------------------------------------------------------------

def recompute_bindings(b, wd=None):
    drift = []
    def chk(label, path, expect):
        if expect is None:
            return
        if not path or not os.path.exists(path):
            drift.append((label, "MISSING")); return
        cur = sha256_file(path)
        if cur != expect:
            drift.append((label, f"{expect[:12]} -> {cur[:12]}"))
    chk("manifest", b.get("_paths", {}).get("manifest"), b.get("submission_manifest_hash"))
    chk("anonymity_result", b.get("_paths", {}).get("anonymity"), b.get("anonymity_result_hash"))
    chk("compliance_result", b.get("_paths", {}).get("compliance"), b.get("compliance_result_hash"))
    chk("manual_records", b.get("_paths", {}).get("manual"), b.get("manual_records_hash"))
    chk("review_verdict", b.get("_paths", {}).get("review"), b.get("review_verdict_hash"))
    chk("staleness", b.get("_paths", {}).get("staleness"), b.get("staleness_hash"))
    for name, h in (b.get("final_document_hashes") or {}).items():
        if b.get("_final_dirs"):
            cand = [os.path.join(d, name) for d in b["_final_dirs"]]
            found = next((c for c in cand if os.path.exists(c)), None)
            if found is None:
                drift.append(("final_document:" + name, "MISSING"))
            else:
                cur = sha256_file(found)
                if cur != h:
                    drift.append(("final_document:" + name, f"{h[:12]} -> {cur[:12]}"))
    return drift


def cmd_verify(a):
    auth = loadj(a.authorization or auth_path(a.wf_dir))
    if not auth:
        return fail("INPUT_ERROR no authorization record", 2)
    drift = recompute_bindings(auth.get("bindings", {}), a.wf_dir)
    if drift:
        print("AUTHORIZATION_STALE_OR_INVALID")
        for lbl, d in drift:
            print("  DRIFT:", lbl, d)
        return 1
    print("AUTHORIZATION_VALID bound_at=", auth.get("bound_at_utc"),
          "state=", auth.get("state_at_binding"))
    return 0


# --------------------------------------------------------------------------
# audit-transition — forged SUBMISSION_READY/CLOSED detection
# --------------------------------------------------------------------------

ALLOWED_WITHOUT_AUTH = {"INIT", "PROBLEM_ANALYZED", "DATA_READY", "DATA_NOT_REQUIRED",
                        "FORMULATION_AUTHORIZED", "SOLVED", "VALIDATED", "FIGURES_READY",
                        "CONTENT_READY", "EVIDENCE_BOUND", "DOCUMENT_READY", "REVIEW_PASSED"}


def cmd_audit_transition(a):
    st = loadj(st_path(a.wf_dir))
    if not st:
        return fail("INPUT_ERROR no workflow_state", 2)
    stage = st.get("current_stage")
    if stage in ALLOWED_WITHOUT_AUTH:
        print("TRANSITION_AUDIT_OK stage=", stage, "(no authorization required)")
        return 0
    auth = loadj(auth_path(a.wf_dir))
    if not auth:
        print("FORGED_TRANSITION_DETECTED stage=", stage,
              "| no submission_authorization.json covers it")
        return 1
    drift = recompute_bindings(auth.get("bindings", {}), a.wf_dir)
    if drift:
        print("FORGED_TRANSITION_DETECTED stage=", stage,
              "| authorization stale:", drift[:4])
        return 1
    hist = [h for h in st.get("history", [])
            if h.get("to") == "SUBMISSION_READY" or h.get("from") == "SUBMISSION_READY"]
    if not hist:
        print("FORGED_TRANSITION_DETECTED stage=", stage,
              "| history lacks REVIEW_PASSED->SUBMISSION_READY entry")
        return 1
    print("TRANSITION_AUDIT_OK stage=", stage, "| authorization covers it")
    return 0


# --------------------------------------------------------------------------
# pre-close-seal / freeze-check
# --------------------------------------------------------------------------

def cmd_pre_close_seal(a):
    wd = a.wf_dir
    st = loadj(st_path(wd))
    if not st:
        return fail("INPUT_ERROR no workflow_state", 2)
    if st.get("current_stage") != "SUBMISSION_READY":
        return fail(f"SEAL_REFUSED requires SUBMISSION_READY, got={st.get('current_stage')}")
    auth = loadj(auth_path(wd))
    if not auth:
        return fail("SEAL_REFUSED no submission_authorization.json")
    if cmd_verify(argparse.Namespace(wf_dir=wd, authorization=auth_path(wd))) != 0:
        return fail("SEAL_REFUSED authorization invalid/stale")
    seal = {
        "schema_version": "ph1_freeze_seal.v1",
        "sealed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pre_close_state": {
            "current_stage": "SUBMISSION_READY",
            "history_len": len(st.get("history", [])),
            "last_history_entry": (st.get("history") or [{}])[-1],
        },
        "authorization_sha256": sha256_file(auth_path(wd)),
        "bindings_snapshot": auth.get("bindings", {}),
        "workflow_state_declared_sha256": None,
        "note": "declared-state hash intentionally excluded: workflow_state.json mutates "
                "legitimately during close; integrity is enforced via artifact hashes.",
    }
    savej(seal_path(wd), seal)
    print("PH1_FREEZE_SEALED ->", os.path.abspath(seal_path(wd)))
    return 0


def cmd_freeze_check(a):
    wd = a.wf_dir
    st = loadj(st_path(wd))
    if not st:
        return fail("INPUT_ERROR no workflow_state", 2)
    problems = []
    if st.get("current_stage") != "CLOSED":
        problems.append(f"EFFECTIVE_STATE_NOT_CLOSED current_stage={st.get('current_stage')}"
                        f" state_status={st.get('state_status')}")
    frz = loadj(frz_path(wd))
    if frz is None:
        problems.append("FREEZE_RECORD_MISSING")
    else:
        if frz.get("schema_version") != "release_freeze_record.v1":
            problems.append("FREEZE_RECORD_SCHEMA_UNEXPECTED "
                            + str(frz.get("schema_version")))
        hist_close = [h for h in st.get("history", [])
                      if h.get("from") == "SUBMISSION_READY" and h.get("to") == "CLOSED"
                      and h.get("trigger") == "freeze_close"]
        if not hist_close:
            problems.append("CLOSED_RECORD_INVALID history lacks legal "
                            "SUBMISSION_READY->CLOSED(freeze_close) transition")
        elif len(hist_close) > 1:
            problems.append("CLOSED_RECORD_INVALID duplicate close transitions")
        closed_at = (hist_close[-1].get("timestamp") if hist_close
                     else frz.get("closed_at"))
        if closed_at and frz.get("closed_at"):
            # orchestrator writes freeze record and history entry in two separate
            # now() calls; allow small clock skew instead of exact equality
            try:
                from datetime import datetime
                t1 = datetime.fromisoformat(str(closed_at).replace("Z", "+00:00"))
                t2 = datetime.fromisoformat(str(frz.get("closed_at")).replace("Z", "+00:00"))
                if abs((t1 - t2).total_seconds()) > 5.0:
                    problems.append("CLOSED_RECORD_INVALID freeze_record.closed_at does "
                                    "not match close transition timestamp")
            except ValueError:
                problems.append("CLOSED_RECORD_INVALID unparsable close timestamps")
    seal = loadj(seal_path(wd))
    if seal is None:
        print("FREEZE_CHECK = UNSEALED (pre-PH1 style close; PH1 binding absent)")
        for p in problems:
            print("  PROBLEM:", p)
        return 1 if problems else 0
    # seal exists → full verification
    auth = loadj(auth_path(wd))
    if auth is None:
        problems.append("CLOSED_RECORD_INVALID authorization file missing but sealed")
    else:
        if sha256_file(auth_path(wd)) != seal.get("authorization_sha256"):
            problems.append("CLOSED_RECORD_INVALID authorization mutated after seal")
        drift = recompute_bindings(auth.get("bindings", {}), wd)
        for lbl, d in drift:
            problems.append(f"CLOSED_RECORD_INVALID frozen content drifted: {lbl} ({d})")
    if problems:
        print("CLOSED_RECORD_INVALID")
        for p in problems:
            print("  PROBLEM:", p)
        return 1
    print("FREEZE_CHECK = VALID_CLOSED_AND_SEALED")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    pb = sub.add_parser("bind")
    pb.add_argument("--wf-dir", required=True)
    pb.add_argument("--expect-stage", default="REVIEW_PASSED")
    pb.add_argument("--manifest", required=True)
    pb.add_argument("--anonymity-result", required=True)
    pb.add_argument("--compliance-result", required=True)
    pb.add_argument("--manual-records", default=None)
    pb.add_argument("--review-verdict", required=True)
    pb.add_argument("--staleness", default=None)
    pb.add_argument("--final-doc", action="append", default=[])
    pb.add_argument("--out", default=None)
    pb.set_defaults(fn=cmd_bind)

    pv = sub.add_parser("verify")
    pv.add_argument("--wf-dir", required=True)
    pv.add_argument("--authorization", default=None)
    pv.set_defaults(fn=cmd_verify)

    pa = sub.add_parser("audit-transition")
    pa.add_argument("--wf-dir", required=True)
    pa.set_defaults(fn=cmd_audit_transition)

    ps = sub.add_parser("pre-close-seal")
    ps.add_argument("--wf-dir", required=True)
    ps.set_defaults(fn=cmd_pre_close_seal)

    pf = sub.add_parser("freeze-check")
    pf.add_argument("--wf-dir", required=True)
    pf.set_defaults(fn=cmd_freeze_check)

    args = ap.parse_args(argv)
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
