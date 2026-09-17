#!/usr/bin/env python3
"""R6-B verification suite (Level1 invariants + Level2 routing) + sidecar generator."""
import json, os, subprocess, sys, hashlib, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # orchestrator skill root
ORCH = os.path.join(ROOT, "scripts", "orchestrator.py")
SKILLS = os.path.dirname(ROOT)
PROJ = os.path.abspath(os.path.join(ROOT, "..", ".."))
RESULTS = []

def check(name, ok, detail=""):
    RESULTS.append((name, bool(ok), detail))

# ---------------- sidecar generator (B4) ----------------
def gen_sidecars():
    outdir = os.path.join(ROOT, "references", "family_pack_sidecars")
    os.makedirs(outdir, exist_ok=True)
    fams = ["network_routing", "spatial", "simulation", "dynamic_state_space_inverse", "hybrid"]
    stages = {"model-selection": "selection", "mle-solver": "solver", "model-validation": "validation"}
    n = 0
    for skill, stage in stages.items():
        pdir = os.path.join(SKILLS, skill, "references", "family_packs")
        for f in sorted(os.listdir(pdir)):
            if not f.endswith(".md"):
                continue
            src = os.path.join(pdir, f)
            txt = open(src, encoding="utf-8-sig").read()
            fam = f.rsplit("_" + stage, 1)[0]
            fid = fam.upper()
            sc = {
                "sidecar_version": "r6b.v1", "family_id": fid, "stage": stage,
                "authority": "ADVISORY_ONLY",
                "source_file": os.path.abspath(src),
                "source_sha256": hashlib.sha256(open(src, "rb").read()).hexdigest(),
                "eligibility": "see source: Eligible structure section",
                "preconditions": "see source bullet list",
                "assumptions": "per source", "baseline_candidates": "per source Baselines/Baseline line",
                "serious_alternatives": "per source Alternatives/Alternative line",
                "formulation_patterns": "per source (solver/selection contracts)",
                "solver_options": "per source solver hierarchy (where present)",
                "validation_requirements": "per source preregistered checks (validation packs)",
                "failure_modes": "per source Failure modes/Failure triggers",
                "known_limitations": "per source Replacement triggers / limitations",
                "sovereignty": "NONE - advisory knowledge bound by hash into selection verdict v2",
            }
            with open(os.path.join(outdir, f + ".sidecar.json"), "w", encoding="utf-8") as fh:
                json.dump(sc, fh, indent=1)
            n += 1
    return n

# ------------- fixture-driven routing tests (Level 2) -------------
def run_orch(*args):
    p = subprocess.run([sys.executable, ORCH, *args], capture_output=True, text=True)
    return p.returncode, p.stdout + p.stderr

def mkfix(base, files):
    os.makedirs(base, exist_ok=True)
    for name, obj in files.items():
        with open(os.path.join(base, name), "w", encoding="utf-8") as fh:
            json.dump(obj, fh)

def wsel(allow=True, action=None):
    d = {"schema_version": "selection_verdict.schema.v1",
         "anti_template_gate": {"verdict": "ALLOW_FORMULATION" if allow else "REVISE_SELECTION"}}
    if action: d["required_action"] = action
    return d

def wrel(verdict, action="NONE", scope="FULL"):
    return {"schema_version": "model_validation_gate.schema.v3", "verdict": verdict,
            "required_action": action, "release_scope": scope,
            "limitations": ["x"] if verdict == "PASS_WITH_LIMITATIONS" else [],
            "material_sensitivity": {"present": False, "material_to_conclusion": False}}

def scenario(name, fn):
    try:
        detail = fn()
        RESULTS.append((name, True, detail or ""))
    except AssertionError as e:
        RESULTS.append((name, False, str(e)))
    except SystemExit as e:
        RESULTS.append((name, e.code in (0,), "exit=%s" % e.code))

def t_pass_path():
    wd = tempfile.mkdtemp(prefix="l2_pass_")
    run_orch("init", "T_PASS", wd)
    run_orch("register", wd, "01_problem_structure", mkfile(wd, "01.json"))
    run_orch("register", wd, "03_candidate_portfolio", mkfile(wd, "03.json"))
    run_orch("register", wd, "04_selection_verdict", mkfile(wd, "04.json", wsel(True)))
    run_orch("register", wd, "05_model_formulation", mkfile(wd, "05.json"))
    for _ in range(4): run_orch("advance", wd)   # PA->MS->FORM->NUM
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] == "NUMERICAL_EXECUTION", st["current_stage"]
    run_orch("register", wd, "06_solver_result", mkfile(wd, "06.json"))
    run_orch("advance", wd)                       # ->VALIDATION
    run_orch("register", wd, "07_validation_evidence", mkfile(wd, "07.json"))
    run_orch("register", wd, "08_release_decision", mkfile(wd, "08.json", wrel("PASS")))
    run_orch("advance", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] == "FINALIZE", st
    return "PASS->FINALIZE ok"

def t_pwl():
    wd = tempfile.mkdtemp(prefix="l2_pwl_")
    run_orch("init", "T_PWL", wd); seed_full(wd)
    run_orch("register", wd, "07_validation_evidence", mkfile(wd, "07.json"))
    run_orch("register", wd, "08_release_decision", mkfile(wd, "08.json", wrel("PASS_WITH_LIMITATIONS")))
    run_orch("advance", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] == "FINALIZE_LIMITED"; return "PWL->FINALIZE_LIMITED ok"

def t_sel_refusal():
    wd = tempfile.mkdtemp(prefix="l2_ref_")
    run_orch("init", "T_REF", wd)
    run_orch("advance", wd)  # START -> PROBLEM_ANALYSIS
    run_orch("register", wd, "01_problem_structure", mkfile(wd, "01.json"))
    run_orch("register", wd, "03_candidate_portfolio", mkfile(wd, "03.json"))
    run_orch("register", wd, "04_selection_verdict", mkfile(wd, "04.json", wsel(False)))
    run_orch("advance", wd)  # PA -> MODEL_SELECTION
    run_orch("advance", wd)  # MODEL_SELECTION consumes verdict -> refusal
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] == "REVISION" and st["resume_stage"] == "MODEL_SELECTION"
    assert st["selection_authorized"] is False; return "refusal->REVISION(MS) ok"

def t_solver_unauthorized():
    wd = tempfile.mkdtemp(prefix="l2_unauth_")
    run_orch("init", "T_UA", wd); run_orch("advance", wd)  # START->PA
    # jump state to FORMULATION without authorization
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    st["current_stage"] = "FORMULATION"; json.dump(st, open(os.path.join(wd, "workflow_state.json"), "w"))
    rc, _ = run_orch("advance", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["error_state"]["type"] == "SOLVER_ERROR"; return "unauthorized entry blocked"

def t_revise_to_formulation():
    wd = tempfile.mkdtemp(prefix="l2_revf_"); run_orch("init", "T_RF", wd); seed_full(wd)
    run_orch("register", wd, "07_validation_evidence", mkfile(wd, "07.json"))
    run_orch("register", wd, "08_release_decision", mkfile(wd, "08.json", wrel("REVISE", "REVISE_FORMULATION", "NONE")))
    run_orch("advance", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] == "REVISION" and st["revision_history"][-1]["revision_target"] == "MODEL_FORMULATION"
    inv = st["invalidated_artifacts"]
    assert "05_model_formulation" in inv and "06_solver_result" in inv and "01_problem_structure" not in inv
    assert st["resume_stage"] == "FORMULATION"; return "local revision + invalidation DAG ok"

def t_fail_blocked():
    wd = tempfile.mkdtemp(prefix="l2_fail_"); run_orch("init", "T_FL", wd); seed_full(wd)
    run_orch("register", wd, "07_validation_evidence", mkfile(wd, "07.json"))
    run_orch("register", wd, "08_release_decision", mkfile(wd, "08.json", wrel("FAIL", "CHANGE_MODEL", "NONE")))
    run_orch("advance", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] == "FAILED_BLOCKED" and st["release_scope"] == "NONE"
    return "FAIL blocks terminal"

def t_integrity_stop():
    wd = tempfile.mkdtemp(prefix="l2_integ_"); run_orch("init", "T_IN", wd)
    run_orch("advance", wd)  # START -> PROBLEM_ANALYSIS (checks 01 on next advance)
    p = mkfile(wd, "01.json"); run_orch("register", wd, "01_problem_structure", p)
    open(p, "w").write("{}")  # mutate
    rc, _ = run_orch("advance", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["error_state"]["type"] == "INTEGRITY_ERROR"; return "integrity hard stop"

def t_resume_and_loop_guard():
    wd = tempfile.mkdtemp(prefix="l2_res_"); run_orch("init", "T_RS", wd); seed_full(wd)
    run_orch("resume", wd)
    st = json.load(open(os.path.join(wd, "workflow_state.json")))
    assert st["current_stage"] in ("FORMULATION", "NUMERICAL_EXECUTION", "VALIDATION")
    # loop guard
    st["revision_count"] = 3
    st["revision_history"] = [{"revision_target": "MODEL_FORMULATION"}] * 3
    json.dump(st, open(os.path.join(wd, "workflow_state.json"), "w"))
    import importlib, io, contextlib
    sys.path.insert(0, os.path.join(ROOT, "scripts"))
    import orchestrator as O
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        O.route_revision(st, wd, None, "VALIDATION_ERROR", "again", wrel("REVISE", "REVISE_FORMULATION", "NONE"))
    assert st["current_stage"] == "TERMINAL_REVIEW_REQUIRED"; return "resume+loop-guard ok"

def mkfile(wd, name, obj=None):
    p = os.path.join(wd, name)
    with open(p, "w", encoding="utf-8") as fh:
        json.dump(obj if obj is not None else {"schema_version": "fixture"}, fh)
    return p

def seed_full(wd):
    run_orch("register", wd, "01_problem_structure", mkfile(wd, "01.json"))
    run_orch("register", wd, "02_data_profile", mkfile(wd, "02.json"))
    run_orch("register", wd, "03_candidate_portfolio", mkfile(wd, "03.json"))
    run_orch("register", wd, "04_selection_verdict", mkfile(wd, "04.json", wsel(True)))
    run_orch("register", wd, "05_model_formulation", mkfile(wd, "05.json"))
    for _ in range(5): run_orch("advance", wd)   # ->NUMERICAL_EXECUTION
    assert json.load(open(os.path.join(wd,"workflow_state.json")))["current_stage"]=="NUMERICAL_EXECUTION"
    run_orch("register", wd, "06_solver_result", mkfile(wd, "06.json"))
    run_orch("advance", wd)                       # ->VALIDATION

SCENARIOS = [t_pass_path, t_pwl, t_sel_refusal, t_solver_unauthorized,
             t_revise_to_formulation, t_fail_blocked, t_integrity_stop, t_resume_and_loop_guard]

def main():
    n_side = gen_sidecars()
    print("SIDECARS_GENERATED =", n_side)
    for fn in SCENARIOS:
        scenario(fn.__name__, fn)
    ok = sum(1 for _, o, _ in RESULTS if o)
    for name, o, det in RESULTS:
        print(("PASS " if o else "FAIL ") + name + ("  | " + det if det else ""))
    print("L2_ROUTING_TESTS = %d/%d" % (ok, len(RESULTS)))

if __name__ == "__main__":
    main()
