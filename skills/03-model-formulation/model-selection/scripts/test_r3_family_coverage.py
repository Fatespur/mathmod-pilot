import copy, hashlib, json, os, subprocess, sys, unittest
from pathlib import Path
from validate_r3_family_contracts import *
from validate_selection import REGISTRY as R1_REGISTRY, ContractError, sha256_json, validate_portfolio_v2, validate_selection_verdict_v2
from test_r1_contracts import valid_portfolio, valid_structure

class RegistryAndCases(unittest.TestCase):
    def test_registry(self): self.assertEqual(len(validate_registry()["families"]),5)
    def test_twenty_cases_four_per_family(self):
        cases=load(CASES)["cases"]; self.assertEqual(len(cases),20)
        self.assertEqual(len({c["id"] for c in cases}),len(cases))
        prefixes={"NETWORK_ROUTING":"N","SPATIAL":"S","SIMULATION_QUEUE_DES_ABM":"Q","DYNAMIC_STATE_SPACE_INVERSE":"D","HYBRID_MODELING":"H"}
        self.assertTrue(all(c["id"].startswith(prefixes[c["family"]]) for c in cases))
        for fid in FAMILY_IDS: self.assertGreaterEqual(sum(c["family"]==fid for c in cases),4)
        self.assertGreaterEqual(sum(bool(c["deceptive"]) for c in cases),10)
    def test_all_cases(self):
        for case in load(CASES)["cases"]: self.assertEqual(validate_case(case),(case["expected_route"],case["expected_contract_effect"]))
    def test_three_stage_pack_keys_are_mandatory(self):
        r=copy.deepcopy(validate_registry()); r["families"][0]["packs"].pop("validation")
        self.assertRaises(R3ContractError,validate_registry,r)
    def test_route_preconditions_cannot_be_omitted(self):
        self.assertEqual(route({"depot":True,"demand":True,"capacity":True}),"NO_FAMILY_ROUTE")
        self.assertEqual(route({"coordinates":True,"region_prediction":True}),"NO_FAMILY_ROUTE")

class MetamorphicTests(unittest.TestCase):
    def test_mt1_route_word_rename(self): self.assertEqual(route({"graph":True,"depot":True,"demand":True,"capacity":True}),route({"graph":True,"depot":True,"demand":True,"capacity":True,"title":"logistics"}))
    def test_mt2_remove_capacity_changes_subtype(self): self.assertNotEqual(route({"graph":True,"depot":True,"demand":True,"capacity":True}),route({"graph":True,"source_destination":True,"nonnegative_weights":True}))
    def test_mt3_coordinate_field_rename(self):
        a={"coordinates":True,"region_prediction":True,"crs_valid":True,"coordinate_field":"xy"}; b={**a,"coordinate_field":"location"}; self.assertEqual(route(a),"SPATIAL"); self.assertEqual(route(a),route(b))
    def test_mt4_shuffle_locations_changes_validation_effect_not_family(self):
        a={"coordinates":True,"region_prediction":True,"spatial_dependence":True,"crs_valid":True,"locations_shuffled":False}; b={**a,"locations_shuffled":True}; self.assertEqual(route(a),route(b)); self.assertNotEqual(contract_effect(a),contract_effect(b))
    def test_mt5_remove_queue_word_preserves_structure_route(self):
        a={"queue_structure":True,"poisson_arrivals":True,"exponential_service":True,"stationary":True,"independent":True,"servers_defined":True,"title":"queue planning"}; b={k:v for k,v in a.items() if k!="title"}; self.assertEqual(route(a),route(b))
    def test_mt6_exponential_to_heavytail(self): self.assertNotEqual(route({"queue_structure":True,"poisson_arrivals":True,"exponential_service":True,"stationary":True,"independent":True,"servers_defined":True}),route({"queue_structure":True,"heavy_tail_service":True,"time_varying_arrivals":True}))
    def test_mt7_parameter_rename(self):
        a={"ode":True,"identifiable":False,"prediction_stable":True,"purpose":"PREDICTION_ONLY","parameters":["a","b"]}; b={**a,"parameters":["theta1","theta2"]}; self.assertEqual((route(a),contract_effect(a)),(route(b),contract_effect(b)))
    def test_mt8_component_rename(self):
        a={"hybrid":True,"test_material_gain":True,"ablation":True,"all_components_material":True,"uncertainty_propagated":True,"policy_stable":True,"names":["A","B"]}; b={**a,"names":["encoder","optimizer"]}; self.assertEqual((route(a),contract_effect(a)),(route(b),contract_effect(b)))
    def test_mt9_multiobjective_scale_changes_solver_not_family(self):
        small={"family":"MULTIOBJECTIVE","linear_integral":True,"scale":"small"}; large={**small,"scale":"large"}; self.assertNotEqual(multiobjective_solver_choice(small),multiobjective_solver_choice(large))
    def test_mt10_advanced_ai_phrase_no_effect(self):
        a={"univariate_trend":True,"latent_state_basis":False,"mechanism_basis":False}; b={**a,"title":"advanced AI model"}; self.assertEqual((route(a),contract_effect(a)),(route(b),contract_effect(b)))

class ContractTests(unittest.TestCase):
    def good(self): return {"family_id":"NETWORK_ROUTING","family_version":"2.0","baseline":["greedy"],"alternative":["generic optimization"],"validation_requirements":["feasibility"],"failure_modes":["subtour"],"replacement_triggers":["new capacity facts"],"solver_hierarchy":["CONVEX_EXACT","DISCRETE_EXACT"],"routing_basis":"STRUCTURE"}
    def test_good(self): self.assertEqual(validate_portfolio(self.good()),"ALLOW_FORMULATION_CANDIDATE")
    def test_no_baseline_rejected(self): x=self.good(); x["baseline"]=[]; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_no_alternative_rejected(self): x=self.good(); x["alternative"]=[]; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_no_validation_rejected(self): x=self.good(); x["validation_requirements"]=[]; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_no_failure_modes_rejected(self): x=self.good(); x["failure_modes"]=[]; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_no_replacement_trigger_rejected(self): x=self.good(); x["replacement_triggers"]=[]; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_no_solver_hierarchy_rejected(self): x=self.good(); x["solver_hierarchy"]=[]; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_keyword_route_rejected(self): x=self.good(); x["routing_basis"]="KEYWORD"; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_unsupported_escalation_rejected(self): x=self.good(); x["solver_escalation"]="UNSUPPORTED"; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_hybrid_no_ablation_revise(self): x=self.good(); x["family_id"]="HYBRID_MODELING"; self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_spatial_random_cv_revise(self): self.assertEqual(contract_effect({"spatial_dependence":True,"random_kfold":True}),"REQUIRE_S4_REVISE")
    def test_simulation_no_seed_replication_cannot_pass(self):
        x={"des":True,"warmup_checked":True,"seeds":False,"replications":False}; self.assertEqual(contract_effect(x),"REQUIRE_S4_REVISE")
    def test_unknown_or_missing_family_rejected(self):
        x=self.good(); x["family_id"]="NOT_REAL"; self.assertRaises(R3ContractError,validate_portfolio,x)
        x=self.good(); x.pop("family_id"); self.assertRaises(R3ContractError,validate_portfolio,x)
    def test_bad_hierarchy_rejected(self):
        x=self.good(); x["solver_hierarchy"]=["METAHEURISTIC","UNKNOWN"]; self.assertRaises(R3ContractError,validate_portfolio,x)

class CanonicalV2Contract(unittest.TestCase):
    def make_portfolio(self):
        p=valid_portfolio(); p["schema_version"]="candidate_portfolio.schema.v2"; c=p["primary"]; c["model_family"]="network_routing"; c["specific_method_if_known"]="capacitated route candidate"
        required=next(f["required_preconditions"] for f in R1_REGISTRY["families"] if f["family"]=="network_routing"); c["required_preconditions"]=list(required); c["supported_preconditions"]=list(required); c["problem_structure_match"]=["graph with capacity depot and demand"]
        f=next(x for x in validate_registry()["families"] if x["family_id"]=="NETWORK_ROUTING"); c["validation_plan"]=list(f["validation_requirements"])
        c["family_contract"]={"family_id":"NETWORK_ROUTING","family_version":"2.0","eligibility_evidence":["NETWORK_GRAPH_PRESENT","CAPACITATED_ROUTING_FACTS_PRESENT"],"rejected_near_neighbors":["pure shortest path lacks fleet constraints"],"family_validation_requirements":list(f["validation_requirements"]),"replacement_triggers":[f["replacement_triggers"][0]]}
        return p
    def test_v2_projection_and_family_contract_pass(self): self.assertEqual(validate_portfolio_v2(self.make_portfolio())["schema_version"],"candidate_portfolio.schema.v2")
    def test_v2_missing_family_contract_rejected(self):
        p=self.make_portfolio(); p["primary"].pop("family_contract"); self.assertRaises(ContractError,validate_portfolio_v2,p)
    def test_v2_unknown_family_id_rejected(self):
        p=self.make_portfolio(); p["primary"]["family_contract"]["family_id"]="NOT_REAL"; self.assertRaises(ContractError,validate_portfolio_v2,p)
    def test_v2_ungrounded_eligibility_rejected(self):
        s=valid_structure(["NETWORK"]); p=self.make_portfolio(); p["problem_structure_sha256"]=sha256_json(s)
        primary,baseline,alternative=p["primary"],p["baseline"],p["alternative"]; gate={"version":"ANTI_TEMPLATE_GATE.v1","verdict":"ALLOW_FORMULATION","q1_structure":f"{primary['candidate_id']} {primary['model_family']} matches {primary['problem_structure_match'][0]} mathematical structure","q2_baseline":f"{baseline['candidate_id']} is insufficient: {baseline['why_not']}","q3_alternative":f"{alternative['candidate_id']} {alternative['model_family']} {alternative['specific_method_if_known']} is serious","q4_why_not_alternative":f"{alternative['candidate_id']} rejected because {alternative['why_not']}","q5_preconditions":"; ".join(primary["required_preconditions"]),"q6_replacement_observation":primary["replacement_trigger"],"selection_basis":["MATHEMATICAL_STRUCTURE","DATA_COMPATIBILITY"]}
        family=next(x for x in validate_registry()["families"] if x["family_id"]=="NETWORK_ROUTING"); hashes={stage:hashlib.sha256((REGISTRY.parent/rel).resolve().read_bytes()).hexdigest() for stage,rel in family["packs"].items()}
        v={"schema_version":"selection_verdict.schema.v2","problem_id":"fixture","selected_candidate":"primary","baseline_candidate":"baseline","serious_alternative":"alternative","fallback_candidate":"fallback","anti_template_gate":gate,"precondition_summary":"claimed","why_primary":"claimed network fit","why_not_baseline":"baseline insufficient for claimed route","why_not_alternative":"alternative lacks graph constraints","replacement_trigger":primary["replacement_trigger"],"known_limitations":[],"family_coverage_status":"SUPPORTED","artifact_hashes":{"problem_structure":sha256_json(s),"candidate_portfolio":sha256_json(p)},"blocking_reason":None,"owner_stage":"MODEL_SELECTION","required_action":"PROCEED_TO_SOLVER","revision_id":"r3-bad","selected_family_id":"NETWORK_ROUTING","selected_family_version":"2.0","family_pack_hashes":hashes}
        self.assertRaisesRegex(ContractError,"FAMILY_ELIGIBILITY_UNBOUND",validate_selection_verdict_v2,v,p,s)
    def test_v2_hash_bound_verdict_passes_canonical_chain(self):
        s=valid_structure(["NETWORK"]); s["network_structure"].update({"present":True,"weighted":True,"capacities":True,"demands":True,"vehicles":True,"depots":True}); p=self.make_portfolio(); p["problem_structure_sha256"]=sha256_json(s)
        primary,baseline,alternative=p["primary"],p["baseline"],p["alternative"]
        gate={"version":"ANTI_TEMPLATE_GATE.v1","verdict":"ALLOW_FORMULATION","q1_structure":f"{primary['candidate_id']} {primary['model_family']} matches {primary['problem_structure_match'][0]} mathematical structure","q2_baseline":f"{baseline['candidate_id']} is insufficient: {baseline['why_not']}","q3_alternative":f"{alternative['candidate_id']} {alternative['model_family']} {alternative['specific_method_if_known']} is the serious candidate","q4_why_not_alternative":f"{alternative['candidate_id']} rejected because {alternative['why_not']}","q5_preconditions":"; ".join(primary["required_preconditions"]),"q6_replacement_observation":primary["replacement_trigger"],"selection_basis":["MATHEMATICAL_STRUCTURE","DATA_COMPATIBILITY","SOLVER_FEASIBILITY","VALIDATION_FEASIBILITY"]}
        family=next(x for x in validate_registry()["families"] if x["family_id"]=="NETWORK_ROUTING"); hashes={stage:hashlib.sha256((REGISTRY.parent/rel).resolve().read_bytes()).hexdigest() for stage,rel in family["packs"].items()}
        v={"schema_version":"selection_verdict.schema.v2","problem_id":"fixture","selected_candidate":"primary","baseline_candidate":"baseline","serious_alternative":"alternative","fallback_candidate":"fallback","anti_template_gate":gate,"precondition_summary":"all graph and operational preconditions are supported","why_primary":"primary matches the supported network structure","why_not_baseline":"baseline leaves material routing constraints unmodeled","why_not_alternative":"alternative adds unsupported temporal assumptions","replacement_trigger":primary["replacement_trigger"],"known_limitations":["static edge costs"],"family_coverage_status":"SUPPORTED","artifact_hashes":{"problem_structure":sha256_json(s),"candidate_portfolio":sha256_json(p)},"blocking_reason":None,"owner_stage":"MODEL_SELECTION","required_action":"PROCEED_TO_SOLVER","revision_id":"r3","selected_family_id":"NETWORK_ROUTING","selected_family_version":"2.0","family_pack_hashes":hashes}
        self.assertEqual(validate_selection_verdict_v2(v,p,s)["required_action"],"PROCEED_TO_SOLVER")

class FrozenRegression(unittest.TestCase):
    def run_suite(self,path):
        env=dict(os.environ); env["PYTHONDONTWRITEBYTECODE"]="1"; env["PYTHONUTF8"]="1"
        r=subprocess.run([sys.executable,str(path)],capture_output=True,text=True,env=env); self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_r1(self): self.run_suite(ROOT/"model-selection"/"scripts"/"test_r1_contracts.py")
    def test_r2(self): self.run_suite(ROOT/"model-validation"/"scripts"/"test_r2_contracts.py")

if __name__ == "__main__": unittest.main(verbosity=2)
