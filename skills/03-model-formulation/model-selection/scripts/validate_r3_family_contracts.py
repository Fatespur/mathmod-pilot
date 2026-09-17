"""Deterministic R3 family-registry and case-contract checks; no model fitting."""
from __future__ import annotations
import json
from pathlib import Path

ROOT = Path.home() / ".codex" / "skills"
REGISTRY = ROOT / "model-selection" / "references" / "model_family_registry.v2.json"
CASES = ROOT / "model-selection" / "references" / "r3_family_cases.v1.json"
FAMILY_IDS = {"NETWORK_ROUTING", "SPATIAL", "SIMULATION_QUEUE_DES_ABM", "DYNAMIC_STATE_SPACE_INVERSE", "HYBRID_MODELING"}
REQUIRED = {"family_id","family_version","mathematical_structure","preconditions","reject_conditions","data_requirements","identifiability_risks","baselines","candidate_methods","alternatives","solver_hierarchy","exact_methods","approximate_methods","validation_requirements","failure_modes","replacement_triggers","coverage_status","packs"}

class R3ContractError(ValueError): pass

def load(path: Path): return json.loads(path.read_text(encoding="utf-8"))

def validate_registry(registry=None):
    registry = registry or load(REGISTRY)
    if registry.get("authority_chain") != ["problem-analyzer","model-selection","mle-solver","model-validation"]:
        raise R3ContractError("AUTHORITY_CHAIN_CHANGED")
    families = registry.get("families", [])
    if {f.get("family_id") for f in families} != FAMILY_IDS:
        raise R3ContractError("CORE_FAMILY_SET_MISMATCH")
    for family in families:
        missing = REQUIRED - family.keys()
        if missing: raise R3ContractError(f"MISSING_FIELDS:{family.get('family_id')}:{sorted(missing)}")
        for key in ("baselines","solver_hierarchy","validation_requirements","failure_modes","replacement_triggers"):
            if not family[key]: raise R3ContractError(f"EMPTY_CONTRACT:{family['family_id']}:{key}")
        if len(family["solver_hierarchy"]) < 2: raise R3ContractError("SOLVER_HIERARCHY_TOO_SHALLOW")
        if set(family["packs"]) != {"selection","solver","validation"}: raise R3ContractError(f"THREE_PACK_CONTRACT_REQUIRED:{family['family_id']}")
        registry_dir = REGISTRY.parent
        for stage, rel in family["packs"].items():
            path = (registry_dir / rel).resolve()
            expected_root = (ROOT / {"selection":"model-selection","solver":"mle-solver","validation":"model-validation"}[stage]).resolve()
            if expected_root not in path.parents: raise R3ContractError(f"PACK_PATH_ESCAPES_STAGE:{family['family_id']}:{stage}")
            if not path.is_file(): raise R3ContractError(f"MISSING_PACK:{family['family_id']}:{stage}")
            content=path.read_text(encoding="utf-8").casefold()
            family_token={"NETWORK_ROUTING":"network_routing","SPATIAL":"spatial","SIMULATION_QUEUE_DES_ABM":"simulation_queue_des_abm","DYNAMIC_STATE_SPACE_INVERSE":"dynamic_state_space_inverse","HYBRID_MODELING":"hybrid_modeling"}[family["family_id"]]
            if family_token.casefold() not in content.replace(" ","_") or f"{stage} contract v2" not in content:
                raise R3ContractError(f"PACK_CONTENT_CONTRACT_MISMATCH:{family['family_id']}:{stage}")
    return registry

def route(f):
    if f.get("graph") and f.get("depot") and f.get("demand") and f.get("capacity"): return "CVRP"
    if f.get("graph") and f.get("supply_demand") and f.get("flow_conservation"): return "MIN_COST_FLOW"
    if f.get("graph") and f.get("visit_all") and f.get("small_instance"): return "TSP_EXACT_FIRST"
    if f.get("source_destination") and f.get("nonnegative_weights") and not any(f.get(k) for k in ("capacity","depot","demand","visit_all")): return "SHORTEST_PATH"
    if f.get("coordinates") and (f.get("projection_error") or f.get("crs_valid")) and (f.get("region_prediction") or f.get("spatial_dependence")): return "SPATIAL"
    if f.get("coordinates") and not f.get("residual_spatial_autocorrelation") and not f.get("region_prediction"): return "NON_SPATIAL_BASELINE"
    if all(f.get(k) for k in ("queue_structure","poisson_arrivals","exponential_service","stationary","independent","servers_defined")): return "M_M_C"
    if f.get("queue_structure") and (f.get("heavy_tail_service") or f.get("time_varying_arrivals")): return "G_G_C_OR_DES"
    if f.get("des"): return "DES"
    if f.get("abm"): return "ABM"
    if f.get("latent_state") and f.get("noisy_measurements"): return "STATE_SPACE_FILTERING"
    if f.get("univariate_trend") and not f.get("latent_state_basis") and not f.get("mechanism_basis"): return "TIME_SERIES_BASELINE"
    if f.get("ode"): return "DYNAMIC_INVERSE"
    if f.get("redundant_components") or (f.get("training_gain") and not f.get("test_material_gain")): return "SIMPLE_COMPONENT"
    if f.get("hybrid") or f.get("prediction_to_optimization"): return "HYBRID"
    return "NO_FAMILY_ROUTE"

def contract_effect(f):
    """Test oracle describing the required stage effect; never an S4 verdict issuer."""
    if f.get("projection_error"): return "REQUIRE_S4_FAIL"
    if f.get("locations_shuffled") and f.get("spatial_dependence"): return "REQUIRE_S4_REVISE"
    if f.get("random_kfold") and f.get("spatial_dependence"): return "REQUIRE_S4_REVISE"
    if f.get("coordinates") and not f.get("residual_spatial_autocorrelation") and not f.get("region_prediction"): return "REJECT_COMPLEXITY_AT_SELECTION"
    if (f.get("des") or f.get("abm")) and (not f.get("seeds") or not f.get("replications")): return "REQUIRE_S4_REVISE"
    if f.get("des") and not f.get("warmup_checked"): return "REQUIRE_S4_REVISE"
    if f.get("abm") and not f.get("rules_calibrated"): return "REQUIRE_S4_LIMIT_OR_REVISE"
    if f.get("identifiable") is False and f.get("purpose") in ("PARAMETER_INFERENCE","MECHANISM_INTERPRETATION"): return "REQUIRE_S4_REVISE_OR_FAIL"
    if f.get("identifiable") is False and f.get("purpose") == "PREDICTION_ONLY" and f.get("prediction_stable"): return "REQUIRE_S4_LIMIT_CLAIMS"
    if f.get("univariate_trend") and not f.get("latent_state_basis"): return "REJECT_FAMILY_AT_SELECTION"
    if f.get("training_gain") and not f.get("test_material_gain"): return "REJECT_COMPLEXITY_AT_SELECTION"
    if f.get("prediction_to_optimization") and (not f.get("uncertainty_propagated") or not f.get("policy_stable")): return "REQUIRE_S4_REVISE"
    if f.get("redundant_components"): return "REQUIRE_SIMPLIFICATION"
    return "ELIGIBLE_FOR_SELECTION"

def multiobjective_solver_choice(f):
    if f.get("family") != "MULTIOBJECTIVE" or f.get("linear_integral") is not True: return "NO_DECISION"
    return "EXACT_EPSILON_OR_ENUMERATION" if f.get("scale") == "small" else "DECOMPOSITION_OR_BOUNDED_APPROXIMATION"

def validate_case(case):
    actual=(route(case["facts"]),contract_effect(case["facts"]))
    expected=(case["expected_route"],case["expected_contract_effect"])
    if actual != expected: raise R3ContractError(f"CASE_MISMATCH:{case['id']}:{actual}!={expected}")
    return actual

def validate_portfolio(candidate):
    for key in ("baseline","alternative","validation_requirements","failure_modes","replacement_triggers","solver_hierarchy"):
        if not candidate.get(key): raise R3ContractError(f"CANDIDATE_MISSING:{key}")
    if candidate.get("routing_basis") in ("KEYWORD","CONTEST_LABEL","PRESTIGE","SAMPLE_BAND"):
        raise R3ContractError("TEMPLATE_ROUTE")
    if candidate.get("family_id") not in FAMILY_IDS or candidate.get("family_version") != "2.0": raise R3ContractError("UNKNOWN_FAMILY_CONTRACT")
    hierarchy=candidate.get("solver_hierarchy",[])
    allowed=["ANALYTICAL","CONVEX_EXACT","DISCRETE_EXACT","DECOMPOSITION","DETERMINISTIC_NUMERICAL","APPROXIMATION","METAHEURISTIC"]
    if any(level not in allowed for level in hierarchy) or hierarchy != sorted(hierarchy,key=allowed.index): raise R3ContractError("INVALID_SOLVER_HIERARCHY")
    if hierarchy and hierarchy[-1]=="METAHEURISTIC" and not candidate.get("exact_infeasibility_evidence"): raise R3ContractError("UNSUPPORTED_SOLVER_ESCALATION")
    if candidate.get("solver_escalation") == "UNSUPPORTED": raise R3ContractError("UNSUPPORTED_SOLVER_ESCALATION")
    if candidate.get("family_id") == "HYBRID_MODELING" and not candidate.get("ablation_plan"): raise R3ContractError("HYBRID_ABLATION_MISSING")
    return "ALLOW_FORMULATION_CANDIDATE"

if __name__ == "__main__":
    validate_registry()
    cases=load(CASES)["cases"]
    for case in cases: validate_case(case)
    print(f"R3 registry PASS; cases {len(cases)}/{len(cases)}; deceptive {sum(bool(c['deceptive']) for c in cases)}")
