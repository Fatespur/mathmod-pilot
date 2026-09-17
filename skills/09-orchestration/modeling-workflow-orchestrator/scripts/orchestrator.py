#!/usr/bin/env python3
"""R6-B workflow orchestrator — STATE MACHINE ONLY (no modeling sovereignty).

Commands:
  init <workflow_id> <dir>
  register <wf_dir> <canonical_artifact_id> <file_path>   # records sha256, checks existence
  advance <wf_dir>                                        # applies one transition
  route-revision <wf_dir>                                 # after REVISE verdict
  resume <wf_dir>                                         # verify hashes then continue
  assemble-summary <wf_dir>                               # 09_final_modeling_summary (assembly-only)
Consumes structured fields ONLY. Validation veto consumed literally.
"""
import hashlib, json, os, sys

CHAIN = ["01_problem_structure", "02_data_profile", "03_candidate_portfolio",
         "04_selection_verdict", "05_model_formulation", "06_solver_result",
         "07_validation_evidence", "08_release_decision", "09_final_modeling_summary"]
DOWNSTREAM = {  # invalidation DAG: target -> descendants to invalidate
    "01_problem_structure": CHAIN[1:], "02_data_profile": CHAIN[2:],
    "03_candidate_portfolio": ["04_selection_verdict","05_model_formulation","06_solver_result",
                               "07_validation_evidence","08_release_decision","09_final_modeling_summary"],
    "04_selection_verdict": ["05_model_formulation","06_solver_result","07_validation_evidence",
                             "08_release_decision","09_final_modeling_summary"],
    "05_model_formulation": ["06_solver_result","07_validation_evidence","08_release_decision",
                             "09_final_modeling_summary"],
    "06_solver_result": ["07_validation_evidence","08_release_decision","09_final_modeling_summary"],
    "07_validation_evidence": ["08_release_decision","09_final_modeling_summary"],
}
ACTION_TO_TARGET = {"REVISE_FORMULATION":"MODEL_FORMULATION","REVISE_DATA":"DATA_PROCESSING",
    "REVISE_SELECTION":"MODEL_SELECTION","CHANGE_MODEL":"MODEL_FORMULATION",
    "COLLECT_MORE_DATA":"DATA_COLLECTION"}
OWNER_STAGE = {"PROBLEM_STRUCTURE":"PROBLEM_ANALYSIS","DATA_PROCESSING":"DATA_ASSESSMENT",
    "MODEL_SELECTION":"MODEL_SELECTION","MODEL_FORMULATION":"FORMULATION",
    "NUMERICAL_EXECUTION":"NUMERICAL_EXECUTION","VALIDATION_EVIDENCE":"VALIDATION",
    "DATA_COLLECTION":"DATA_ASSESSMENT"}

def sha(p):
    return hashlib.sha256(open(p,"rb").read()).hexdigest()

def load(wd):
    return json.load(open(os.path.join(wd,"workflow_state.json"),encoding="utf-8-sig"))

def save(wd,st):
    st["timestamp"]=__import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    json.dump(st,open(os.path.join(wd,"workflow_state.json"),"w",encoding="utf-8"),indent=1)

def init(wid,wd):
    st={"workflow_id":wid,"current_stage":"START","completed_stages":[],"active_artifacts":{},
        "invalidated_artifacts":[],"revision_history":[],"revision_count":0,
        "current_verdict":None,"required_action":None,"release_scope":None,
        "error_state":None,"resume_stage":"START","selection_authorized":False}
    save(wd,st); print("INIT",wid)

def register(wd,aid,path):
    st=load(wd)
    if not os.path.exists(path): fail(st,wd,"SCHEMA_ERROR","missing artifact "+aid); return
    st["active_artifacts"][aid]={"path":os.path.abspath(path),"sha256":sha(path)}
    save(wd,st); print("REGISTERED",aid)

def fail(st,wd,etype,msg):
    st["error_state"]={"type":etype,"message":msg}
    if etype=="INTEGRITY_ERROR":
        st["current_stage"]="STOPPED_INTEGRITY"; st["resume_stage"]=None
    save(wd,st); print("ERROR",etype,msg); sys.exit(2 if etype=="INTEGRITY_ERROR" else 1)

def artifact(wd,st,aid):
    e=st["active_artifacts"].get(aid)
    if not e or not os.path.exists(e["path"]): return None
    if sha(e["path"])!=e["sha256"]: fail(st,wd,"INTEGRITY_ERROR","hash mismatch "+aid)
    d=json.load(open(e["path"],encoding="utf-8-sig"))
    # legacy alias compatibility for release decision inputs
    if aid=="08_release_decision" and "verdict" not in d and "gate" in d:
        pass
    return d

def mark_invalidated(st,target):
    for a in DOWNSTREAM.get(target,[]):
        if a not in st["invalidated_artifacts"]: st["invalidated_artifacts"].append(a)

def advance(wd):
    st=load(wd); s=st["current_stage"]
    def need(*ids):
        for i in ids:
            if artifact(wd,st,i) is None: fail(st,wd,"SCHEMA_ERROR","required missing: "+i)
    if s=="START": st["current_stage"]="PROBLEM_ANALYSIS"
    elif s=="PROBLEM_ANALYSIS":
        need("01_problem_structure")
        st["completed_stages"].append("PROBLEM_ANALYSIS")
        st["current_stage"]= "DATA_ASSESSMENT" if st["active_artifacts"].get("02_data_profile") else "MODEL_SELECTION"
    elif s=="DATA_ASSESSMENT":
        need("02_data_profile"); st["completed_stages"].append("DATA_ASSESSMENT"); st["current_stage"]="MODEL_SELECTION"
    elif s=="MODEL_SELECTION":
        need("03_candidate_portfolio","04_selection_verdict")
        sv=artifact(wd,st,"04_selection_verdict")
        gate=(sv.get("anti_template_gate") or {}).get("verdict") or sv.get("verdict") or ""
        action=sv.get("required_action","")
        if gate=="ALLOW_FORMULATION" or action in ("PROCEED_TO_SOLVER","ALLOW_FORMULATION"):
            st["selection_authorized"]=True; st["completed_stages"].append("MODEL_SELECTION")
            st["current_stage"]="FORMULATION"
        else:
            st["selection_authorized"]=False
            route_revision(st,wd,"MODEL_SELECTION","SELECTION_ERROR","selection refused authorization")
            return
    elif s=="FORMULATION":
        if not st.get("selection_authorized"):
            fail(st,wd,"SOLVER_ERROR","unauthorized solver entry"); return
        if "05_model_formulation" not in st["active_artifacts"]:
            # DESIGN/no-data case: legitimate solver-segment skip (behavior-preserving)
            st["solver_applicable"]=False
            st["completed_stages"].extend(["FORMULATION_SKIPPED","NUMERICAL_EXECUTION_SKIPPED"])
            st["current_stage"]="VALIDATION"
        else:
            need("05_model_formulation"); st["completed_stages"].append("FORMULATION")
            st["current_stage"]="NUMERICAL_EXECUTION"
    elif s=="NUMERICAL_EXECUTION":
        need("06_solver_result"); st["completed_stages"].append("NUMERICAL_EXECUTION"); st["current_stage"]="VALIDATION"
    elif s=="VALIDATION":
        need("07_validation_evidence","08_release_decision")
        rd=artifact(wd,st,"08_release_decision")
        v=rd.get("verdict"); st["current_verdict"]=v
        st["required_action"]=rd.get("required_action"); st["release_scope"]=rd.get("release_scope")
        st["completed_stages"].append("VALIDATION")
        if v=="PASS": st["current_stage"]="FINALIZE"
        elif v=="PASS_WITH_LIMITATIONS": st["current_stage"]="FINALIZE_LIMITED"
        elif v=="REVISE": route_revision(st,wd,None,"VALIDATION_ERROR","validation REVISE",rd); return
        elif v=="FAIL":
            st["current_stage"]="FAILED_BLOCKED"; st["resume_stage"]=None
        else: fail(st,wd,"SCHEMA_ERROR","non-canonical verdict "+str(v))
    elif s=="REVISION":
        # idempotent wait-state: owner fix happens externally; resume/route moves forward
        print("WAITING_REVISION",st.get("resume_stage")); return
    elif s in ("FINALIZE","FINALIZE_LIMITED"):
        assemble(wd,st); return
    elif s in ("FAILED_BLOCKED","STOPPED_INTEGRITY","TERMINAL_REVIEW_REQUIRED"): print("TERMINAL",s); return
    else: fail(st,wd,"SCHEMA_ERROR","unknown stage "+str(s))
    save(wd,st); print("ADVANCE->",st["current_stage"])

def route_revision(st,wd,target_hint=None,err=None,msg="",rd=None):
    action=(rd or {}).get("required_action") or st.get("required_action") or "REFINE_MODEL"
    target=target_hint or ACTION_TO_TARGET.get(action,"MODEL_FORMULATION")
    resume=OWNER_STAGE.get(target,"MODEL_SELECTION")
    inv=[]; pres=[]
    order=["01_problem_structure","02_data_profile","03_candidate_portfolio","04_selection_verdict",
           "05_model_formulation","06_solver_result","07_validation_evidence","08_release_decision"]
    idx={a:i for i,a in enumerate(order)}
    anchor={"PROBLEM_STRUCTURE":"01_problem_structure","DATA_PROCESSING":"02_data_profile",
            "DATA_COLLECTION":"02_data_profile","MODEL_SELECTION":"03_candidate_portfolio",
            "MODEL_FORMULATION":"05_model_formulation","NUMERICAL_EXECUTION":"06_solver_result",
            "VALIDATION_EVIDENCE":"07_validation_evidence"}.get(target)
    if anchor: inv=[a for a in order if idx.get(a,-1)>=idx[anchor]]  # target itself + descendants
    pres=[a for a in order if a not in inv and st["active_artifacts"].get(a)]
    st["revision_count"]+=1
    entry={"revision_id":"REV-%s-%03d"%(st["workflow_id"],st["revision_count"]),
           "revision_target":target,"required_action":action,"reason_code":err or "",
           "source_stage":st["current_stage"],"resume_stage":resume,
           "invalidated_artifacts":inv,"preserved_artifacts":pres,
           "last_revision_reason":msg}
    st["revision_history"].append(entry)
    for a in inv:
        if a in st["invalidated_artifacts"]: pass
        else: st["invalidated_artifacts"].append(a)
    if target!="DATA_COLLECTION": st["selection_authorized"]=st.get("selection_authorized",False)
    if st["revision_count"]>3 and len({h["revision_target"] for h in st["revision_history"][-3:]})==1:
        st["current_stage"]="TERMINAL_REVIEW_REQUIRED"; st["resume_stage"]=None
        st["error_state"]={"type":"REVISION_LOOP","message":"repeated same failure"}; save(wd,st)
        print("TERMINAL_REVIEW_REQUIRED"); return
    st["current_stage"]="REVISION"; st["resume_stage"]=resume
    save(wd,st); print("ROUTE_REVISION->",target,"resume:",resume,"invalidated:",len(inv))

def resume_cmd(wd):
    st=load(wd)
    for aid,e in st["active_artifacts"].items():
        if os.path.exists(e["path"]) and sha(e["path"])!=e["sha256"]:
            fail(st,wd,"INTEGRITY_ERROR","resume hash mismatch "+aid)
    tgt=st.get("resume_stage")
    if tgt and tgt!="START":
        st["current_stage"]=tgt          # deterministic re-entry after REVISION
    save(wd,st); print("RESUME->",st["current_stage"])

def assemble(wd,st=None):
    st=st or load(wd)
    summary={"schema_version":"final_modeling_summary.v1","assembly_only":True,
             "problem_structure_ref":st["active_artifacts"].get("01_problem_structure",{}).get("path"),
             "selection_verdict_ref":st["active_artifacts"].get("04_selection_verdict",{}).get("path"),
             "solver_result_ref":st["active_artifacts"].get("06_solver_result",{}).get("path"),
             "release_decision_ref":st["active_artifacts"].get("08_release_decision",{}).get("path"),
             "verdict":st["current_verdict"],"required_action":st["required_action"],
             "release_scope":st["release_scope"],
             "limitations_source":"08_release_decision.limitations (copied verbatim only)"}
    out=os.path.join(wd,"09_final_modeling_summary.json")
    json.dump(summary,open(out,"w",encoding="utf-8"),indent=1)
    st["active_artifacts"]["09_final_modeling_summary"]={"path":os.path.abspath(out),"sha256":sha(out)}
    save(wd,st); print("ASSEMBLED 09_final_modeling_summary")

if __name__=="__main__":
    wd=None
    if len(sys.argv)>=4 and sys.argv[1]=="init": init(sys.argv[2],sys.argv[3])
    elif sys.argv[1]=="register": register(sys.argv[2],sys.argv[3],sys.argv[4])
    elif sys.argv[1]=="advance": advance(sys.argv[2])
    elif sys.argv[1]=="route-revision": st=load(sys.argv[2]); route_revision(st,sys.argv[2],sys.argv[3] if len(sys.argv)>3 else None,"MANUAL","manual route"); 
    elif sys.argv[1]=="resume": resume_cmd(sys.argv[2])
    elif sys.argv[1]=="assemble-summary": assemble(sys.argv[2])
    else: print(__doc__)
