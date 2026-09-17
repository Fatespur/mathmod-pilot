import copy
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from validate_r2_gate import (
    CHECK_IDS, MANDATORY_CHECKS, ValidationContractError, build_gate, canonical_hash, compare_validation_plans,
    downstream_transition, make_revision_record, register_validation_plan, required_revalidation, validate_evidence,
    validate_gate, validate_manifest_extension, validate_plan, validation_plan_hash,
)


FIXTURE_DIR = Path(tempfile.gettempdir()) / "cumcm_r2_contract_fixtures"
FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
UPSTREAM_PATHS = {}
H = {}
for role in ("model","data","portfolio","selection","baseline"):
    path=FIXTURE_DIR / f"{role}.json"; path.write_text(json.dumps({"artifact_role":role,"fixture":"r2-contract"},sort_keys=True),encoding="utf-8"); UPSTREAM_PATHS[role]=path; H[role]=hashlib.sha256(path.read_bytes()).hexdigest()
VALIDATION_ARTIFACT = FIXTURE_DIR / "validation-results.json"
REGISTRY_DIR = FIXTURE_DIR / f"registry-{os.getpid()}"
REGISTRY_DIR.mkdir(parents=True, exist_ok=True)


def valid_plan(*, ident_purpose="PARAMETER_INFERENCE"):
    plan = {
        "schema_version":"validation_plan.schema.v1","problem_id":"r2fixture","model_id":"primary-prediction" if ident_purpose == "PREDICTION_ONLY" else "primary",
        "model_artifact_hash":H["model"],"data_artifact_hash":H["data"],"candidate_portfolio_hash":H["portfolio"],"selection_verdict_hash":H["selection"],
        "validation_objective":"Determine whether the selected model can support its preregistered claims.",
        "intended_claims":[{"claim_id":"C1","target":"target y","scope":"registered forecast horizon","purpose":"PREDICTION"}] if ident_purpose == "PREDICTION_ONLY" else [{"claim_id":"C1","target":"physical parameters","scope":"registered observation domain","purpose":"PARAMETER_INFERENCE"}],
        "applicable_checks":list(CHECK_IDS),"non_applicable_checks":[],
        "metrics":[{"metric_id":"m1","check_id":"V03_BASELINE_SUPERIORITY","name":"decision loss","direction":"LOWER_BETTER","practical_threshold":0.05,"uncertainty_method":"paired bootstrap"}],
        "baselines":[{"baseline_id":"baseline","artifact_hash":H["baseline"],"information_set":"same covariates","split_id":"temporal","target":"y","loss":"decision loss","constraints":["hard capacity"],"horizon":"next period","smallest_effect_of_practical_interest":0.05}],
        "data_splits":[{"split_id":"temporal","type":"TEMPORAL_ROLLING","rationale":"Preserve time order for future prediction.","leakage_boundary":"Training timestamps precede every validation timestamp."}],
        "holdouts":["final temporal origin"],"backtests":["rolling origin"],
        "perturbation_ranges":[{"parameter":"sensor error","lower":-0.02,"upper":0.02,"basis":"MEASUREMENT_ACCURACY"}],
        "uncertainty_sources":["measurement error"],"stability_runs":["seeds 1 through 10"],"ablation_plan":["remove complex component"],
        "identifiability_plan":{"applicable":True,"purpose":ident_purpose,"methods":["PROFILE_LIKELIHOOD","MULTISTART_RECOVERY"],"rationale":"The intended claim requires unique parameters or stable prediction under ambiguity.","blocking_if_failed":ident_purpose != "PREDICTION_ONLY"},
        "failure_tests":[{"test_id":"FT1","description":"Force boundary and high-noise operating conditions.","risk":"HIGH"}],
        "blocking_rules":[{"check_id":"V01_MATHEMATICAL_CORRECTNESS","condition":"Any hard mathematical inconsistency is structural.","failure_class":"STRUCTURAL","owner_stage":"SOLVER","required_action":"CHANGE_MODEL"}],
        "claim_restriction_rules":["Do not extrapolate beyond the tested horizon."],"created_at":"2026-08-24T00:00:00+08:00","plan_hash":"0"*64,
    }
    plan["plan_hash"] = validation_plan_hash(plan)
    return plan


PASS_VALUES = {
    "V01_MATHEMATICAL_CORRECTNESS":{"mathematical_validity":True,"hard_constraint_satisfied":True},
    "V02_DATA_COMPATIBILITY":{"data_leakage":False,"information_boundary_verified":True,"sampling_compatible":True},
    "V03_BASELINE_SUPERIORITY":{"comparison_type":"BASELINE_SUPERIORITY","baseline_id":"baseline","baseline_artifact_hash":H["baseline"],"metric_id":"m1","primary_metric":0.8,"baseline_metric":1.0,"uncertainty_supports_materiality":True,"same_information_set":True,"same_split":True,"same_target":True,"same_loss":True,"same_constraints":True,"same_horizon":True,"primary_worse":False,"primary_more_complex":True,"material_improvement":True},
    "V04_OUT_OF_SAMPLE_VALIDITY":{"temporal_problem":True,"split_type":"TEMPORAL_ROLLING","dependence_structure_matched":True,"underpowered":False},
    "V05_SENSITIVITY":{"decision_reversal":False,"decision_risk":"HIGH","perturbation_basis_verified":True},
    "V06_ROBUSTNESS":{"shared_bias":False,"same_estimand":True,"independent_assumptions_reviewed":True,"agreement_difference":0.19},
    "V07_UNCERTAINTY":{"decision_chain":True,"uncertainty_propagated":True},
    "V08_INTERPRETABILITY_DOMAIN_SENSE":{"identifiable":True,"observable":True,"prediction_stable":True},
    "V09_CONSTRAINT_SATISFACTION":{"hard_constraint_satisfied":True},
    "V10_FAILURE_ENVELOPE":{"failure_tests_executed":True,"executed_test_ids":["FT1"]},
    "V11_STABILITY_ABLATION":{"decision_reversal_across_seeds":False,"complex_component_material_contribution":True},
}


def evidence_bundle(plan=None):
    plan = plan or valid_plan(); records=[]
    for index, check_id in enumerate(CHECK_IDS, 1):
        records.append({"evidence_id":f"E{index:02d}","check_id":check_id,"source_artifact":"validation-results.json","artifact_sha256":"0"*64,"result_pointer":f"/evidence/E{index:02d}","producer_stage":"S4","method":"executed deterministic diagnostic","input_scope":"registered validation sample","output_scope":"raw metric and diagnostic","metric":f"metric_{index}","observed_value":copy.deepcopy(PASS_VALUES[check_id]),"reference_or_expected_range":{"registered":True},"status":"PASS","notes":"raw output retained","created_at":"2026-08-24T00:05:00+08:00"})
    bundle={"schema_version":"validation_evidence.schema.v1","problem_id":plan["problem_id"],"model_id":plan["model_id"],"validation_plan_hash":plan["plan_hash"],"evidence":records}
    _sync_evidence_artifact(bundle)
    return bundle


def failure_envelope(plan=None):
    plan=plan or valid_plan()
    return {"schema_version":"failure_envelope.schema.v1","problem_id":plan["problem_id"],"model_id":plan["model_id"],"model_artifact_hash":plan["model_artifact_hash"],"failures":[{"failure_id":"F1","test_id":"FT1","condition":"Measurement noise exceeds registered sensor bounds.","mechanism":"Signal information becomes insufficient for stable recovery.","observable_signature":"Residual dispersion exceeds the preregistered diagnostic range.","severity":"HIGH","detectability":"HIGH","downstream_impact":"Prediction and parameter interpretation become unreliable.","recommended_action":"LIMIT_CLAIM","test_status":"TESTED_NOT_TRIGGERED"}]}


def _sync_evidence_artifact(bundle):
    document={"run_id":"r2-contract-run","producer_version":"R2_TEST_FIXTURE.v1","command":"python test_r2_contracts.py","input_hashes":{"model":H["model"],"data":H["data"],"candidate_portfolio":H["portfolio"],"selection_verdict":H["selection"],"validation_plan":bundle["validation_plan_hash"]},"evidence":{record["evidence_id"]:record["observed_value"] for record in bundle["evidence"]}}
    VALIDATION_ARTIFACT.write_text(json.dumps(document,ensure_ascii=False,sort_keys=True),encoding="utf-8")
    digest=hashlib.sha256(VALIDATION_ARTIFACT.read_bytes()).hexdigest()
    for record in bundle["evidence"]: record["artifact_sha256"]=digest


def artifacts(plan=None):
    plan=plan or valid_plan(); registration=register_validation_plan(plan,REGISTRY_DIR)
    validation_hash=hashlib.sha256(VALIDATION_ARTIFACT.read_bytes()).hexdigest()
    return {
        "@model":{"path":str(UPSTREAM_PATHS["model"]),"sha256":H["model"],"kind":"MODEL_ARTIFACT"},
        "@data":{"path":str(UPSTREAM_PATHS["data"]),"sha256":H["data"],"kind":"DATA_ARTIFACT"},
        "@candidate_portfolio":{"path":str(UPSTREAM_PATHS["portfolio"]),"sha256":H["portfolio"],"kind":"CANDIDATE_PORTFOLIO"},
        "@selection_verdict":{"path":str(UPSTREAM_PATHS["selection"]),"sha256":H["selection"],"kind":"SELECTION_VERDICT"},
        "@baseline:baseline":{"path":str(UPSTREAM_PATHS["baseline"]),"sha256":H["baseline"],"kind":"BASELINE_ARTIFACT"},
        "@registered_plan":registration,
        "validation-results.json":{"path":str(VALIDATION_ARTIFACT),"sha256":validation_hash,"kind":"VALIDATION_OUTPUT","producer_stage":"S4"},
    }


def mutate_record(bundle, check_id, value, status="PASS"):
    record=next(item for item in bundle["evidence"] if item["check_id"]==check_id)
    record["observed_value"].update(value); record["status"]=status; _sync_evidence_artifact(bundle)


def verdict_for(plan=None,bundle=None,envelope=None):
    plan=plan or valid_plan(); bundle=bundle or evidence_bundle(plan); envelope=envelope or failure_envelope(plan)
    gate=build_gate(plan,bundle,envelope,artifacts(plan)); validate_gate(gate,plan,bundle,envelope,artifacts(plan)); return gate


class ContractTests(unittest.TestCase):
    def test_valid_pass_record_accepted(self): self.assertEqual(verdict_for()["verdict"],"PASS")
    def test_pass_with_warn_cannot_be_declared_pass(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V05_SENSITIVITY",{},"WARN"); g=build_gate(p,b,failure_envelope(p),artifacts()); self.assertEqual(g["verdict"],"PASS_WITH_LIMITATIONS")
        g["verdict"]="PASS"
        with self.assertRaisesRegex(ValidationContractError,"INCONSISTENT_AGGREGATION"): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_pass_with_blocking_fail_rejected(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V09_CONSTRAINT_SATISFACTION",{"hard_constraint_satisfied":False}); g=build_gate(p,b,failure_envelope(p),artifacts()); self.assertEqual(g["verdict"],"FAIL")
    def test_fail_without_allowed_action_rejected(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V09_CONSTRAINT_SATISFACTION",{"hard_constraint_satisfied":False}); g=build_gate(p,b,failure_envelope(p),artifacts()); g["required_action"]="IGNORE"
        with self.assertRaises(ValidationContractError): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_revise_has_revision_token(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"material_improvement":False,"primary_metric":0.99}); g=build_gate(p,b,failure_envelope(p),artifacts()); self.assertEqual(g["verdict"],"REVISE"); self.assertTrue(g["revision_token"].startswith("R2REV-"))
    def test_revise_without_revision_token_rejected(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"material_improvement":False,"primary_metric":0.99}); g=build_gate(p,b,failure_envelope(p),artifacts()); g["revision_token"]=None
        with self.assertRaises(ValidationContractError): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_na_without_rationale_rejected(self):
        p=valid_plan(); p["applicable_checks"].remove("V07_UNCERTAINTY"); p["non_applicable_checks"]=[{"check_id":"V07_UNCERTAINTY","rationale":"not tested"}]; p["plan_hash"]=validation_plan_hash(p)
        with self.assertRaises(ValidationContractError): validate_plan(p)
    def test_stale_artifact_hash_rejected(self):
        p=valid_plan(); b=evidence_bundle(p); g=build_gate(p,b,failure_envelope(p),artifacts()); g["artifact_hashes"]["model"]="0"*64
        with self.assertRaisesRegex(ValidationContractError,"STALE_VALIDATION_EVIDENCE"): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_gate_identity_must_match_plan(self):
        p=valid_plan(); b=evidence_bundle(p); g=build_gate(p,b,failure_envelope(p),artifacts()); g["model_id"]="another-model"
        with self.assertRaisesRegex(ValidationContractError,"GATE_IDENTITY_MISMATCH"): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_revision_token_must_be_deterministic(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"material_improvement":False,"primary_metric":0.99}); g=build_gate(p,b,failure_envelope(p),artifacts()); g["revision_token"]="R2REV-forged"
        with self.assertRaisesRegex(ValidationContractError,"REVISION_TOKEN_MISMATCH"): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_revision_sequence_produces_distinct_token(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"material_improvement":False,"primary_metric":0.99}); e=failure_envelope(p)
        self.assertNotEqual(build_gate(p,b,e,artifacts(),revision_sequence=1)["revision_token"], build_gate(p,b,e,artifacts(),revision_sequence=2)["revision_token"])
    def test_changed_plan_detected(self):
        a=valid_plan(); b=copy.deepcopy(a); b["metrics"][0]["practical_threshold"]=0.001; b["plan_hash"]=validation_plan_hash(b)
        self.assertEqual(compare_validation_plans(a,b,"observed failure")["minimum_verdict"],"REVISE")
    def test_posthoc_plan_cannot_replace_anchored_registration(self):
        original=valid_plan(); evidence_bundle(original); index=artifacts(original); changed=copy.deepcopy(original); changed["metrics"][0]["practical_threshold"]=0.001; changed["plan_hash"]=validation_plan_hash(changed); b=evidence_bundle(changed); index["validation-results.json"]["sha256"]=hashlib.sha256(VALIDATION_ARTIFACT.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValidationContractError,"VALIDATION_PLAN_CHANGED"): build_gate(changed,b,failure_envelope(changed),index)
        with self.assertRaisesRegex(ValidationContractError,"VALIDATION_PLAN_CHANGED"): build_gate(changed,b,failure_envelope(changed),artifacts(changed))
    def test_claim_purpose_cannot_be_downgraded_parallel_to_claim(self):
        p=valid_plan(); p["identifiability_plan"]["purpose"]="PREDICTION_ONLY"; p["identifiability_plan"]["blocking_if_failed"]=False; p["plan_hash"]=validation_plan_hash(p)
        with self.assertRaisesRegex(ValidationContractError,"IDENTIFIABILITY_PURPOSE_DOWNGRADE"): validate_plan(p)
    def test_unsupported_prose_cannot_pass(self):
        p=valid_plan(); b=evidence_bundle(p); b["evidence"][0]["observed_value"]="模型表现良好"
        with self.assertRaisesRegex(ValidationContractError,"UNBOUND_EVIDENCE"): validate_evidence(b,p,artifacts())
    def test_model_artifact_cannot_masquerade_as_validation_output(self):
        p=valid_plan(); b=evidence_bundle(p); index=artifacts(p); index["validation-results.json"]["kind"]="MODEL_ARTIFACT"
        with self.assertRaisesRegex(ValidationContractError,"UNBOUND_EVIDENCE"): validate_evidence(b,p,index)
    def test_minimal_pass_dictionary_cannot_satisfy_check(self):
        p=valid_plan(); b=evidence_bundle(p); next(item for item in b["evidence"] if item["check_id"]=="V02_DATA_COMPATIBILITY")["observed_value"]={"looks_good":True}; _sync_evidence_artifact(b); g=build_gate(p,b,failure_envelope(p),artifacts(p))
        self.assertEqual(g["verdict"],"REVISE")
    def test_baseline_missing_cannot_pass(self):
        p=valid_plan(); p["baselines"]=[]; p["plan_hash"]=validation_plan_hash(p)
        with self.assertRaises(ValidationContractError): validate_plan(p)
    def test_revise_and_fail_block_downstream(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"primary_worse":True}); g=build_gate(p,b,failure_envelope(p),artifacts())
        with self.assertRaisesRegex(ValidationContractError,"DOWNSTREAM_BLOCKED"): downstream_transition(g,"PAPER_WRITING",plan=p,bundle=b,envelope=failure_envelope(p),artifact_index=artifacts())
    def test_manifest_cannot_claim_pass_against_revise_gate(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"material_improvement":False,"primary_metric":0.99}); e=failure_envelope(p); g=build_gate(p,b,e,artifacts())
        payload={"stage":"S4","execution_status":"completed","release_status":"PASS","validation_plan":p,"evidence_bundle":b,"failure_envelope":e,"model_validation_gate":g,"downstream_authorization":{"allowed_stages":["S5","S6","S7"],"claim_restrictions_acknowledged":[]}}
        with self.assertRaises(ValidationContractError): validate_manifest_extension(payload,artifacts())
    def test_manifest_pass_authorizes_all_presentation_stages(self):
        p=valid_plan(); b=evidence_bundle(p); e=failure_envelope(p); g=build_gate(p,b,e,artifacts()); payload={"stage":"S4","execution_status":"completed","release_status":"PASS","validation_plan":p,"evidence_bundle":b,"failure_envelope":e,"model_validation_gate":g,"downstream_authorization":{"allowed_stages":["S5","S6","S7"],"claim_restrictions_acknowledged":[]}}
        self.assertEqual(validate_manifest_extension(payload,artifacts())["release_status"],"PASS")
    def test_raw_gate_dictionary_cannot_authorize_transition(self):
        with self.assertRaises((TypeError,ValidationContractError)):
            downstream_transition({"verdict":"PASS","claim_restrictions":[]},"PAPER_WRITING")
    def test_foreign_failure_envelope_rejected(self):
        p=valid_plan(); b=evidence_bundle(p); e=failure_envelope(p); e["problem_id"]="other"
        with self.assertRaisesRegex(ValidationContractError,"FOREIGN_FAILURE_ENVELOPE"): build_gate(p,b,e,artifacts())
    def test_failure_envelope_must_map_registered_test_ids(self):
        p=valid_plan(); b=evidence_bundle(p); e=failure_envelope(p); e["failures"][0]["test_id"]="OTHER"
        with self.assertRaisesRegex(ValidationContractError,"FAILURE_TEST_MAPPING_MISMATCH"): build_gate(p,b,e,artifacts(p))
    def test_string_false_cannot_pass_mathematical_checks(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V01_MATHEMATICAL_CORRECTNESS",{"mathematical_validity":"false","hard_constraint_satisfied":"false"}); self.assertEqual(build_gate(p,b,failure_envelope(p),artifacts())["verdict"],"FAIL")
    def test_failure_test_false_cannot_pass(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V10_FAILURE_ENVELOPE",{"failure_tests_executed":False}); self.assertEqual(build_gate(p,b,failure_envelope(p),artifacts())["verdict"],"REVISE")
    def test_contradictory_baseline_record_cannot_be_hidden_by_order(self):
        p=valid_plan(); b=evidence_bundle(p); bad=copy.deepcopy(next(item for item in b["evidence"] if item["check_id"]=="V03_BASELINE_SUPERIORITY")); bad["evidence_id"]="E03B"; bad["result_pointer"]="/evidence/E03B"; bad["observed_value"].update(primary_worse=True,material_improvement=False,primary_metric=1.2)
        b["evidence"].append(bad); _sync_evidence_artifact(b); self.assertEqual(build_gate(p,b,failure_envelope(p),artifacts(p))["verdict"],"REVISE"); b["evidence"].reverse(); _sync_evidence_artifact(b); self.assertEqual(build_gate(p,b,failure_envelope(p),artifacts(p))["verdict"],"REVISE")
    def test_mandatory_checks_cannot_be_mass_na(self):
        p=valid_plan(); p["applicable_checks"]=["V10_FAILURE_ENVELOPE"]; p["non_applicable_checks"]=[{"check_id":cid,"reason_code":"STRUCTURALLY_NOT_APPLICABLE","rationale":"The check is claimed structurally irrelevant to this task."} for cid in CHECK_IDS if cid!="V10_FAILURE_ENVELOPE"]; p["plan_hash"]=validation_plan_hash(p)
        with self.assertRaisesRegex(ValidationContractError,"MANDATORY_CHECK_NA"): validate_plan(p)
    def test_prediction_claim_cannot_na_oos_robustness_or_stability(self):
        p=valid_plan(ident_purpose="PREDICTION_ONLY"); keep=set(MANDATORY_CHECKS); p["applicable_checks"]=[cid for cid in CHECK_IDS if cid in keep]; p["non_applicable_checks"]=[{"check_id":cid,"reason_code":"STRUCTURALLY_NOT_APPLICABLE","rationale":"The check is claimed structurally irrelevant to this task."} for cid in CHECK_IDS if cid not in keep]; p["plan_hash"]=validation_plan_hash(p)
        with self.assertRaisesRegex(ValidationContractError,"CLAIM_CONTRADICTS_NA"): validate_plan(p)
    def test_raw_baseline_inferiority_overrides_declared_flag(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"primary_metric":2.0,"baseline_metric":1.0,"primary_worse":False,"primary_more_complex":False}); self.assertEqual(build_gate(p,b,failure_envelope(p),artifacts(p))["verdict"],"REVISE")
    def test_baseline_materiality_threshold_is_authoritative(self):
        p=valid_plan(); p["baselines"][0]["smallest_effect_of_practical_interest"]=0.10; p["plan_hash"]=validation_plan_hash(p); p["model_id"]="threshold-mismatch"; p["plan_hash"]=validation_plan_hash(p); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"primary_metric":0.94,"baseline_metric":1.0,"material_improvement":True}); self.assertEqual(build_gate(p,b,failure_envelope(p),artifacts(p))["verdict"],"REVISE")


class AdversarialCases(unittest.TestCase):
    def test_case_a_shared_bias_agreement(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V06_ROBUSTNESS",{"shared_bias":True,"agreement_difference":0.001}); self.assertEqual(verdict_for(p,b)["verdict"],"FAIL")
    def test_case_b_training_fit_trap(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"material_improvement":False,"primary_metric":0.99}); self.assertEqual(verdict_for(p,b)["verdict"],"REVISE")
    def test_case_c_leakage_trap(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V02_DATA_COMPATIBILITY",{"data_leakage":True,"accuracy":0.999}); self.assertEqual(verdict_for(p,b)["verdict"],"FAIL")
    def test_case_d_nonidentifiable_ode(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V08_INTERPRETABILITY_DOMAIN_SENSE",{"identifiable":False,"prediction_stable":True}); self.assertEqual(verdict_for(p,b)["verdict"],"FAIL")
    def test_case_e_prediction_despite_nonidentifiability(self):
        p=valid_plan(ident_purpose="PREDICTION_ONLY"); b=evidence_bundle(p); mutate_record(b,"V08_INTERPRETABILITY_DOMAIN_SENSE",{"identifiable":False,"prediction_stable":True}); g=verdict_for(p,b); self.assertEqual(g["verdict"],"PASS_WITH_LIMITATIONS"); self.assertTrue(g["claim_restrictions"])
    def test_case_f_random_kfold_time_series(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V04_OUT_OF_SAMPLE_VALIDITY",{"split_type":"RANDOM_KFOLD"}); self.assertEqual(verdict_for(p,b)["verdict"],"REVISE")
    def test_case_g_seed_instability(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V11_STABILITY_ABLATION",{"decision_reversal_across_seeds":True}); self.assertEqual(verdict_for(p,b)["verdict"],"REVISE")
    def test_case_h_sensitivity_reversal(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V05_SENSITIVITY",{"decision_reversal":True,"decision_risk":"MEDIUM"}); self.assertEqual(verdict_for(p,b)["verdict"],"PASS_WITH_LIMITATIONS")
    def test_case_i_stale_validation(self):
        p=valid_plan(); b=evidence_bundle(p); g=build_gate(p,b,failure_envelope(p),artifacts()); g["artifact_hashes"]["model"]=canonical_hash("model_v2")
        with self.assertRaisesRegex(ValidationContractError,"STALE_VALIDATION_EVIDENCE"): validate_gate(g,p,b,failure_envelope(p),artifacts())
    def test_case_j_baseline_wins(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V03_BASELINE_SUPERIORITY",{"primary_worse":True,"material_improvement":False,"primary_metric":1.2}); self.assertEqual(verdict_for(p,b)["verdict"],"REVISE")
    def test_case_k_invalid_hard_constraint(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V09_CONSTRAINT_SATISFACTION",{"hard_constraint_satisfied":False}); self.assertEqual(verdict_for(p,b)["verdict"],"FAIL")
    def test_case_l_wrong_estimand_agreement(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V06_ROBUSTNESS",{"same_estimand":False,"agreement_difference":0.01}); self.assertEqual(verdict_for(p,b)["verdict"],"FAIL")
    def test_case_m_underpowered_generalization(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V04_OUT_OF_SAMPLE_VALIDITY",{"underpowered":True}); self.assertEqual(verdict_for(p,b)["verdict"],"PASS_WITH_LIMITATIONS")
    def test_case_n_posthoc_edit(self):
        p=valid_plan(); q=copy.deepcopy(p); q["perturbation_ranges"][0]["lower"]=-0.001; q["perturbation_ranges"][0]["upper"]=0.001; q["plan_hash"]=validation_plan_hash(q)
        result=compare_validation_plans(p,q,"sensitivity failed"); self.assertTrue(result["substantive"]); self.assertEqual(result["minimum_verdict"],"REVISE")


class MetamorphicTests(unittest.TestCase):
    def test_mt1_accuracy_does_not_override_leakage(self):
        verdicts=[]
        for accuracy in (0.8,0.9999):
            p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V02_DATA_COMPATIBILITY",{"data_leakage":True,"accuracy":accuracy}); verdicts.append(verdict_for(p,b)["verdict"])
        self.assertEqual(verdicts,["FAIL","FAIL"])
    def test_mt2_model_prestige_name_no_effect(self):
        verdicts=[]
        for note in ("linear model","state-of-the-art hybrid model"):
            p=valid_plan(); b=evidence_bundle(p); b["evidence"][0]["notes"]=note; verdicts.append(verdict_for(p,b)["verdict"])
        self.assertEqual(verdicts,["PASS","PASS"])
    def test_mt3_agreement_threshold_no_flip(self):
        verdicts=[]
        for difference in (0.19,0.21):
            p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V06_ROBUSTNESS",{"agreement_difference":difference}); verdicts.append(verdict_for(p,b)["verdict"])
        self.assertEqual(verdicts,["PASS","PASS"])
    def test_mt4_parameter_relabeling(self):
        verdicts=[]
        for names in (["theta1","theta2"],["theta2","theta1"]):
            p=valid_plan(ident_purpose="PREDICTION_ONLY"); b=evidence_bundle(p); mutate_record(b,"V08_INTERPRETABILITY_DOMAIN_SENSE",{"identifiable":False,"prediction_stable":True,"parameter_names":names}); verdicts.append(verdict_for(p,b)["verdict"])
        self.assertEqual(verdicts,["PASS_WITH_LIMITATIONS","PASS_WITH_LIMITATIONS"])
    def test_mt5_seed_ordering(self):
        p=valid_plan(); a=evidence_bundle(p); b=copy.deepcopy(a); b["evidence"]=list(reversed(b["evidence"])); self.assertEqual(verdict_for(p,a)["verdict"],verdict_for(p,b)["verdict"])
    def test_mt6_title_change_no_model_revalidation(self):
        result=required_revalidation("PRESENTATION_ONLY",canonical_hash("title1"),canonical_hash("title2")); self.assertFalse(result["revalidation_required"])
    def test_mt7_equation_change_requires_revalidation(self):
        result=required_revalidation("MODEL_EQUATION",canonical_hash("eq1"),canonical_hash("eq2")); self.assertTrue(result["revalidation_required"]); self.assertIn("V01_MATHEMATICAL_CORRECTNESS",result["stale_checks"])


class RevisionAndRegressionTests(unittest.TestCase):
    def test_revision_record_has_unique_traceable_token(self):
        a=make_revision_record(problem_id="p",model_id="m",sequence=1,old_hash=H["model"],new_hash=canonical_hash("v2"),failed_checks=["V03"],actions=["SIMPLIFY"],owner_stage="MODEL_VALIDATION",change_type="MODEL_EQUATION",summary="Changed equation after validation failure.",plan_changes=[])
        b=make_revision_record(problem_id="p",model_id="m",sequence=2,old_hash=H["model"],new_hash=canonical_hash("v2"),failed_checks=["V03"],actions=["SIMPLIFY"],owner_stage="MODEL_VALIDATION",change_type="MODEL_EQUATION",summary="Changed equation after validation failure.",plan_changes=[])
        self.assertNotEqual(a["revision_token"],b["revision_token"])
    def test_pass_with_limitations_requires_claim_propagation(self):
        p=valid_plan(); b=evidence_bundle(p); mutate_record(b,"V05_SENSITIVITY",{},"WARN"); g=build_gate(p,b,failure_envelope(p),artifacts())
        with self.assertRaisesRegex(ValidationContractError,"CLAIM_RESTRICTIONS_NOT_PROPAGATED"): downstream_transition(g,"PAPER_WRITING",[],plan=p,bundle=b,envelope=failure_envelope(p),artifact_index=artifacts())
        self.assertEqual(downstream_transition(g,"PAPER_WRITING",g["claim_restrictions"],plan=p,bundle=b,envelope=failure_envelope(p),artifact_index=artifacts()),"ALLOW_DOWNSTREAM")
        with self.assertRaisesRegex(ValidationContractError,"CLAIM_ARTIFACTS_INCOMPLETE"): downstream_transition(g,"FINAL_RELEASE",g["claim_restrictions"],plan=p,bundle=b,envelope=failure_envelope(p),artifact_index=artifacts(),claim_artifacts={})
    def test_r1_suite_still_passes(self):
        path=Path.home()/".codex"/"skills"/"model-selection"/"scripts"/"test_r1_contracts.py"
        env=dict(os.environ); env["PYTHONDONTWRITEBYTECODE"]="1"; env["PYTHONUTF8"]="1"
        result=subprocess.run([sys.executable,str(path)],capture_output=True,text=True,env=env)
        self.assertEqual(result.returncode,0,result.stdout+result.stderr)


if __name__ == "__main__": unittest.main(verbosity=2)
