"""Deterministic R1 contract checks for structure-first model selection."""

from __future__ import annotations

import hashlib
import json
import re
import copy
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
REFS = ROOT / "references"
FORBIDDEN_STRUCTURE_FIELDS = {
    "selected_model", "recommended_model", "default_model", "final_model",
    "selected_method", "recommended_method", "method_routing",
}
FORBIDDEN_STRUCTURE_PATTERNS = {
    "GM(1,1)": r"(?i)\bgm\s*\(\s*1\s*,\s*1\s*\)",
    "ARIMA-family": r"(?i)\b(?:s?arimax?)\b", "TOPSIS": r"(?i)\btopsis\b",
    "Dijkstra": r"(?i)\bdijkstra\b", "Floyd": r"(?i)\bfloyd(?:-warshall)?\b",
    "NSGA-II": r"(?i)\bnsga\s*[- ]?ii\b", "MOEA/D": r"(?i)\bmoea\s*/\s*d\b",
    "random forest": r"(?i)\brandom\s*forest\b", "XGBoost": r"(?i)\bxgboost\b",
    "LSTM": r"(?i)\blstm\b", "M/M/c": r"(?i)\bm\s*/\s*m\s*/\s*c\b",
    "SVM": r"(?i)\b(?:svm|support\s+vector\s+machine)\b",
    "neural network": r"(?i)\b(?:neural\s+network|gru|cnn|bert)\b|\b(?:use|apply|select|fit|model\s+with)\s+(?:a\s+)?transformer\b",
    "DEA": r"(?i)\bdea\b|数据包络分析", "AHP": r"(?i)\bahp\b|层次分析法",
    "PCA": r"(?i)\bpca\b|主成分分析", "Prophet": r"(?i)\bprophet\b",
    "K-means": r"(?i)\bk\s*[- ]?means\b", "DBSCAN": r"(?i)\bdbscan\b",
    "boosting model": r"(?i)\b(?:lightgbm|catboost)\b",
    "Holt-Winters/exponential smoothing": r"(?i)\bholt\s*[- ]?winters\b|\bexponential\s+smoothing\b",
    "Kalman filter": r"(?i)\bkalman\s+filter\b", "Gaussian process": r"(?i)\bgaussian\s+process\b",
    "Monte Carlo": r"(?i)\bmonte\s+carlo\b",
    "deep architecture": r"(?i)\b(?:resnet|u-net|yolo)\b",
    "penalized regression": r"(?i)\b(?:ridge\s+regression|lasso)\b",
    "tree/neighbor model": r"(?i)\bdecision\s+tree\b|\bk\s*[- ]?nearest\s+neighbors?\b|\bknn\b",
    "SIR model": r"(?i)\bsir\s+model\b",
    "grey model": r"(?i)\bgr[ae]y\s+model\b|灰色预测",
    "linear/logistic regression": r"(?i)\b(?:linear|logistic)\s+regression\b",
}
FORBIDDEN_SELECTION_BASES = {
    "KEYWORD", "SAMPLE_SIZE_BAND", "CONTEST_CATEGORY", "HISTORICAL_HABIT",
    "POPULARITY", "ADVANCED_REPUTATION",
}
SOLVER_LEVELS = ["ANALYTICAL", "CONVEX_EXACT", "DISCRETE_EXACT", "DECOMPOSITION", "DETERMINISTIC_NUMERICAL", "APPROXIMATION", "METAHEURISTIC"]
FORBIDDEN_RATIONALE_PATTERN = re.compile(
    r"(?i)\b(popular|prestigious|fashionable|state[ -]of[ -]the[ -]art|winning papers?|contest winners?|widely used|advanced reputation|keyword|contest category|historical habit)\b|样本量区间|关键词|竞赛类别|历史习惯|流行|获奖论文|先进性"
)


class ContractError(ValueError):
    """A stable error code plus a human-readable contract failure."""

    def __init__(self, code: str, detail: str):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail


def _load(name: str) -> dict[str, Any]:
    return json.loads((REFS / name).read_text(encoding="utf-8"))


PROBLEM_SCHEMA = _load("problem_structure.schema.v1.json")
PORTFOLIO_SCHEMA = _load("candidate_portfolio.schema.v1.json")
VERDICT_SCHEMA = _load("selection_verdict.schema.v1.json")
REGISTRY = _load("model_family_registry.v1.json")
PORTFOLIO_SCHEMA_V2 = _load("candidate_portfolio.schema.v2.json")
VERDICT_SCHEMA_V2 = _load("selection_verdict.schema.v2.json")
REGISTRY_V2 = _load("model_family_registry.v2.json")
R3_FAMILY_MAP = {
    "network_routing": "NETWORK_ROUTING", "spatial": "SPATIAL",
    "simulation": "SIMULATION_QUEUE_DES_ABM", "dynamic_ode": "DYNAMIC_STATE_SPACE_INVERSE",
    "hybrid": "HYBRID_MODELING",
}


def sha256_json(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _walk(value: Any, path: str = "$") -> Iterable[tuple[str, str | None, Any]]:
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}"
            yield child_path, key, child
            yield from _walk(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            child_path = f"{path}[{index}]"
            yield child_path, None, child
            yield from _walk(child, child_path)


def _schema_validate(instance: dict[str, Any], schema: dict[str, Any], code: str) -> None:
    errors = sorted(Draft202012Validator(schema).iter_errors(instance), key=lambda e: list(e.absolute_path))
    if errors:
        error = errors[0]
        location = "$" + "".join(f"[{item!r}]" for item in error.absolute_path)
        raise ContractError(code, f"{location}: {error.message}")


def _specific_text(value: str, problem_id: str | None = None) -> bool:
    text = value.strip().casefold()
    alnum = re.findall(r"[\w]+", text, flags=re.UNICODE)
    enough_diversity = len(set(alnum)) >= 4 and len(set(text)) >= 10
    return enough_diversity and (problem_id is None or problem_id.casefold() in text)


def validate_problem_structure(structure: dict[str, Any]) -> dict[str, Any]:
    """Reject named-model leakage before ordinary schema validation."""
    for path, key, value in _walk(structure):
        if key and key.casefold() in FORBIDDEN_STRUCTURE_FIELDS:
            raise ContractError("PREMATURE_MODEL_SELECTION", f"forbidden field at {path}")
        if isinstance(value, str):
            lowered = value.casefold()
            hit = next((name for name, pattern in FORBIDDEN_STRUCTURE_PATTERNS.items() if re.search(pattern, value)), None)
            if hit:
                raise ContractError("PREMATURE_MODEL_SELECTION", f"named method {hit!r} at {path}")
    _schema_validate(structure, PROBLEM_SCHEMA, "INVALID_PROBLEM_STRUCTURE")
    return structure


def validate_portfolio(portfolio: dict[str, Any]) -> dict[str, Any]:
    _schema_validate(portfolio, PORTFOLIO_SCHEMA, "INVALID_CANDIDATE_PORTFOLIO")
    portfolio_prose = " ".join(str(value) for _, _, value in _walk(portfolio) if isinstance(value, str))
    if FORBIDDEN_RATIONALE_PATTERN.search(portfolio_prose):
        raise ContractError("TEMPLATE_BASIS_DECLARED", "forbidden rationale appears in portfolio evidence")
    for property_name, role in (
        ("baseline", "BASELINE"), ("primary", "PRIMARY"),
        ("alternative", "ALTERNATIVE"), ("fallback", "FALLBACK"),
    ):
        if portfolio[property_name]["role"] != role:
            raise ContractError("INVALID_CANDIDATE_PORTFOLIO", f"{property_name}.role must be {role}")
        entry = portfolio[property_name]
        if entry["status"] == "N/A" and not _specific_text(entry["na_reason"], portfolio["problem_id"]):
            raise ContractError("INVALID_CANDIDATE_PORTFOLIO", f"{property_name}.na_reason is not specific")
    candidates = [portfolio[name] for name in ("baseline", "primary", "alternative", "fallback") if portfolio[name]["status"] == "CANDIDATE"]
    candidate_ids = [item["candidate_id"] for item in candidates]
    if len(candidate_ids) != len(set(candidate_ids)):
        raise ContractError("INVALID_CANDIDATE_PORTFOLIO", "candidate_id values must be unique across roles")
    registry_ids = {item["family"] for item in REGISTRY["families"]}
    registry_by_id = {item["family"]: item for item in REGISTRY["families"]}
    for item in candidates:
        if item["model_family"] not in registry_ids:
            raise ContractError("INVALID_CANDIDATE_PORTFOLIO", f"unknown model_family {item['model_family']!r}")
        required_evidence_fields = ("required_preconditions", "assumptions", "data_requirements", "identifiability_requirements")
        if any(not item[field] for field in required_evidence_fields):
            raise ContractError("INVALID_CANDIDATE_PORTFOLIO", f"{item['candidate_id']} has empty evidence fields")
        substantive_lists = required_evidence_fields + ("expected_failure_modes", "failure_signatures", "validation_plan", "advantages", "limitations")
        if any(any(not str(value).strip() for value in item[field]) for field in substantive_lists):
            raise ContractError("INVALID_CANDIDATE_PORTFOLIO", f"{item['candidate_id']} contains blank evidence")
        required = set(item["required_preconditions"])
        supported = set(item["supported_preconditions"])
        violated = set(item["violated_preconditions"])
        unknown = set(item["unknown_preconditions"])
        if (supported & violated) or (supported & unknown) or (violated & unknown) or required != (supported | violated | unknown):
            raise ContractError("PRECONDITION_PARTITION_INVALID", f"{item['candidate_id']} must partition every required precondition exactly once")
        missing_registry = set(registry_by_id[item["model_family"]]["required_preconditions"]) - required
        if missing_registry:
            raise ContractError("REGISTRY_PRECONDITION_MISSING", f"{item['candidate_id']} omits registry preconditions: {sorted(missing_registry)}")
        if item["solver_class"] not in SOLVER_LEVELS:
            raise ContractError("INVALID_SOLVER_CLASS", f"{item['candidate_id']} solver_class must be a normalized hierarchy level")
        hierarchy = item["solver_hierarchy_evidence"]
        is_metaheuristic = item["solver_class"] == "METAHEURISTIC"
        hierarchy_order = SOLVER_LEVELS
        levels = hierarchy["screened_levels"]
        if levels != sorted(levels, key=hierarchy_order.index):
            raise ContractError("HEURISTIC_ESCALATION_UNJUSTIFIED", f"{item['candidate_id']} hierarchy is out of order")
        if is_metaheuristic:
            required_levels = hierarchy_order[:-1]
            evidence = hierarchy["exact_infeasibility_evidence"] or ""
            per_level = {}
            for level in required_levels:
                match = re.search(rf"(?is)\b{re.escape(level)}\s*:\s*(.+?)(?=;\s*(?:{'|'.join(required_levels)})\s*:|$)", evidence)
                per_level[level] = match.group(1).strip() if match else ""
            if not hierarchy["metaheuristic_allowed"] or not all(level in levels for level in required_levels) or not all(_specific_text(per_level[level]) for level in required_levels):
                raise ContractError("HEURISTIC_ESCALATION_UNJUSTIFIED", f"{item['candidate_id']} lacks complete exact-route infeasibility evidence")
    if portfolio["primary"]["status"] == "CANDIDATE" and portfolio["alternative"]["status"] == "CANDIDATE":
        primary = portfolio["primary"]; alternative = portfolio["alternative"]
        primary_signature = (primary["model_family"].strip().casefold(), str(primary["specific_method_if_known"]).strip().casefold())
        alternative_signature = (alternative["model_family"].strip().casefold(), str(alternative["specific_method_if_known"]).strip().casefold())
        if primary_signature == alternative_signature:
            raise ContractError("INVALID_CANDIDATE_PORTFOLIO", "serious alternative must differ from the primary family or method")
    criteria = [row["criterion"] for row in portfolio["screening_matrix"]]
    if len(criteria) != len(set(criteria)) or set(criteria) != {
        "STRUCTURE_MATCH", "PRECONDITIONS", "DATA_COMPATIBILITY", "IDENTIFIABILITY_RISK",
        "CONSTRAINT_HANDLING", "EXPECTED_ACCURACY", "ROBUSTNESS_POTENTIAL", "INTERPRETABILITY",
        "COMPUTATIONAL_COST", "VALIDATION_FEASIBILITY",
    }:
        raise ContractError("INVALID_CANDIDATE_PORTFOLIO", "screening_matrix must contain each criterion exactly once")
    return portfolio


def _portfolio_v1_projection(portfolio: dict[str, Any]) -> dict[str, Any]:
    projected = copy.deepcopy(portfolio)
    projected["schema_version"] = "candidate_portfolio.schema.v1"
    for role in ("baseline", "primary", "alternative", "fallback"):
        projected[role].pop("family_contract", None)
    return projected


def validate_portfolio_v2(portfolio: dict[str, Any]) -> dict[str, Any]:
    """Preserve every R1 constraint, then enforce the R3 family overlay."""
    _schema_validate(portfolio, PORTFOLIO_SCHEMA_V2, "INVALID_CANDIDATE_PORTFOLIO_V2")
    validate_portfolio(_portfolio_v1_projection(portfolio))
    by_id = {item["family_id"]: item for item in REGISTRY_V2["families"]}
    for role in ("baseline", "primary", "alternative", "fallback"):
        item = portfolio[role]
        if item["status"] != "CANDIDATE":
            if "family_contract" in item:
                raise ContractError("INVALID_FAMILY_CONTRACT", f"{role} N/A cannot carry family_contract")
            continue
        expected_id = R3_FAMILY_MAP.get(item["model_family"])
        contract = item.get("family_contract")
        if expected_id is None:
            if contract is not None:
                raise ContractError("INVALID_FAMILY_CONTRACT", f"{role} non-R3 family cannot claim an R3 pack")
            continue
        if contract is None:
            raise ContractError("MISSING_FAMILY_CONTRACT", f"{role} requires {expected_id}")
        _schema_validate(contract, PORTFOLIO_SCHEMA_V2["$defs"]["family_contract"], "INVALID_FAMILY_CONTRACT")
        if contract["family_id"] != expected_id:
            raise ContractError("FAMILY_ID_MISMATCH", f"{role} model_family maps to {expected_id}")
        family = by_id[expected_id]
        if contract["family_version"] != family["family_version"]:
            raise ContractError("FAMILY_VERSION_MISMATCH", role)
        if not set(family["validation_requirements"]).issubset(set(contract["family_validation_requirements"])):
            raise ContractError("FAMILY_VALIDATION_MISSING", role)
        if not set(contract["family_validation_requirements"]).issubset(set(item["validation_plan"])):
            raise ContractError("FAMILY_VALIDATION_UNLINKED", role)
        if not set(family["replacement_triggers"]).intersection(set(contract["replacement_triggers"])):
            raise ContractError("REPLACEMENT_TRIGGER_UNLINKED", role)
    return portfolio


def validate_selection_verdict_v2(verdict: dict[str, Any], portfolio: dict[str, Any], structure: dict[str, Any]) -> dict[str, Any]:
    validate_portfolio_v2(portfolio)
    _schema_validate(verdict, VERDICT_SCHEMA_V2, "INVALID_SELECTION_VERDICT_V2")
    primary = portfolio["primary"]
    contract = primary.get("family_contract") if primary.get("status") == "CANDIDATE" else None
    if contract is None:
        raise ContractError("MISSING_FAMILY_CONTRACT", "R3 verdict requires an R3 primary")
    if (verdict["selected_family_id"], verdict["selected_family_version"]) != (contract["family_id"], contract["family_version"]):
        raise ContractError("FAMILY_ID_MISMATCH", "verdict and primary family contract differ")
    evidence = set(contract["eligibility_evidence"])
    network = structure["network_structure"]
    spatial_features = " ".join(structure["spatial_structure"]["features"]).casefold()
    structural_components = sum((bool(structure["observed_variables"]), structure["temporal_structure"]["present"], structure["spatial_structure"]["present"], network["present"], bool(structure["decision_variables"] and structure["objectives"]), bool(structure["state_variables"])))
    derived = set()
    if network["present"]: derived.add("NETWORK_GRAPH_PRESENT")
    if network["present"] and all(network[k] for k in ("capacities","demands","vehicles","depots")): derived.add("CAPACITATED_ROUTING_FACTS_PRESENT")
    if structure["spatial_structure"]["present"] and any(token in spatial_features for token in ("crs", "projection", "坐标系")): derived.add("SPATIAL_STRUCTURE_AND_CRS_PRESENT")
    if "SIMULATION" in structure["task_type"] and bool(structure["uncertainty_sources"]): derived.add("SIMULATION_STOCHASTIC_STRUCTURE_PRESENT")
    if structure["state_variables"] and structure["observed_variables"] and structure["temporal_structure"]["present"] and (structure["initial_conditions"] or structure["boundary_conditions"]): derived.add("DYNAMIC_STATE_OBSERVATION_STRUCTURE_PRESENT")
    if "HYBRID" in structure["task_type"] and structural_components >= 2: derived.add("HYBRID_MULTI_COMPONENT_STRUCTURE_PRESENT")
    required_by_family={"NETWORK_ROUTING":{"NETWORK_GRAPH_PRESENT"},"SPATIAL":{"SPATIAL_STRUCTURE_AND_CRS_PRESENT"},"SIMULATION_QUEUE_DES_ABM":{"SIMULATION_STOCHASTIC_STRUCTURE_PRESENT"},"DYNAMIC_STATE_SPACE_INVERSE":{"DYNAMIC_STATE_OBSERVATION_STRUCTURE_PRESENT"},"HYBRID_MODELING":{"HYBRID_MULTI_COMPONENT_STRUCTURE_PRESENT"}}[contract["family_id"]]
    method=(primary.get("specific_method_if_known") or "").casefold()
    if contract["family_id"]=="NETWORK_ROUTING" and any(token in method for token in ("capacitated", "cvrp", "vehicle route")): required_by_family=required_by_family|{"CAPACITATED_ROUTING_FACTS_PRESENT"}
    if not required_by_family.issubset(derived) or not required_by_family.issubset(evidence) or not evidence.issubset(derived):
        raise ContractError("FAMILY_ELIGIBILITY_UNBOUND", f"required={sorted(required_by_family)} derived={sorted(derived)} declared={sorted(evidence)}")
    projected_portfolio = _portfolio_v1_projection(portfolio)
    projected_verdict = copy.deepcopy(verdict)
    projected_verdict["schema_version"] = "selection_verdict.schema.v1"
    for key in ("selected_family_id", "selected_family_version", "family_pack_hashes"):
        projected_verdict.pop(key, None)
    projected_verdict["artifact_hashes"]["candidate_portfolio"] = sha256_json(projected_portfolio)
    validate_selection_verdict(projected_verdict, projected_portfolio, structure)
    if verdict["artifact_hashes"]["candidate_portfolio"] != sha256_json(portfolio):
        raise ContractError("ARTIFACT_HASH_MISMATCH", "v2 candidate_portfolio hash does not match canonical JSON")
    family = next(item for item in REGISTRY_V2["families"] if item["family_id"] == contract["family_id"])
    registry_dir = REFS
    for stage, expected_hash in verdict["family_pack_hashes"].items():
        path = (registry_dir / family["packs"][stage]).resolve()
        actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual_hash != expected_hash:
            raise ContractError("FAMILY_PACK_HASH_MISMATCH", f"{stage}: {path}")
    return verdict


def anti_template_verdict(
    portfolio: dict[str, Any], selection_basis: Iterable[str], answers: dict[str, str]
) -> str:
    """Aggregate the six-question gate without subjective weighting."""
    validate_portfolio(portfolio)
    bases = set(selection_basis)
    if bases & FORBIDDEN_SELECTION_BASES:
        return "REJECT_TEMPLATE_ROUTE"
    required_answers = {f"q{i}" for i in range(1, 7)}
    if set(answers) != required_answers or any(len(str(answers[key]).strip()) < 10 for key in required_answers):
        return "REVISE_SELECTION"
    if portfolio["baseline"]["status"] == "N/A" or portfolio["primary"]["status"] == "N/A":
        return "REVISE_SELECTION"
    if portfolio["alternative"]["status"] == "N/A":
        return "REVISE_SELECTION"
    primary = portfolio["primary"]
    baseline = portfolio["baseline"]
    alternative = portfolio["alternative"]
    if primary["violated_preconditions"] or primary["unknown_preconditions"]:
        return "REVISE_SELECTION"
    if not primary["why_not"].strip() or not primary["replacement_trigger"].strip():
        return "REVISE_SELECTION"
    normalized = {key: str(value).casefold() for key, value in answers.items()}
    answer_text = " ".join(normalized.values())
    if FORBIDDEN_RATIONALE_PATTERN.search(answer_text):
        return "REJECT_TEMPLATE_ROUTE"
    if any(not _specific_text(value) for value in answers.values()):
        return "REVISE_SELECTION"
    semantic_links = (
        (primary["candidate_id"].casefold() in normalized["q1"] or primary["model_family"].casefold() in normalized["q1"]) and any(item.casefold() in normalized["q1"] for item in primary["problem_structure_match"]),
        baseline["candidate_id"].casefold() in normalized["q2"] and baseline["why_not"].casefold() in normalized["q2"],
        alternative["candidate_id"].casefold() in normalized["q3"] and (alternative["model_family"].casefold() in normalized["q3"] or str(alternative["specific_method_if_known"]).casefold() in normalized["q3"]),
        alternative["candidate_id"].casefold() in normalized["q4"] and alternative["why_not"].casefold() in normalized["q4"],
        all(item.casefold() in normalized["q5"] for item in primary["required_preconditions"]),
        primary["replacement_trigger"].casefold() in normalized["q6"],
    )
    if not all(semantic_links):
        return "REVISE_SELECTION"
    return "ALLOW_FORMULATION"


def validate_selection_verdict(verdict: dict[str, Any], portfolio: dict[str, Any], structure: dict[str, Any]) -> dict[str, Any]:
    validate_portfolio(portfolio)
    _schema_validate(verdict, VERDICT_SCHEMA, "INVALID_SELECTION_VERDICT")
    gate = verdict["anti_template_gate"]
    answers = {f"q{i}": gate[name] for i, name in enumerate((
        "q1_structure", "q2_baseline", "q3_alternative", "q4_why_not_alternative",
        "q5_preconditions", "q6_replacement_observation",
    ), start=1)}
    computed = anti_template_verdict(portfolio, gate["selection_basis"], answers)
    if gate["verdict"] != computed:
        raise ContractError("INCONSISTENT_GATE_VERDICT", f"declared {gate['verdict']}, computed {computed}")
    if computed == "ALLOW_FORMULATION" and verdict["required_action"] != "PROCEED_TO_SOLVER":
        raise ContractError("INCONSISTENT_GATE_VERDICT", "ALLOW_FORMULATION requires PROCEED_TO_SOLVER")
    if computed != "ALLOW_FORMULATION" and verdict["required_action"] == "PROCEED_TO_SOLVER":
        raise ContractError("INCONSISTENT_GATE_VERDICT", "blocked gate cannot proceed to solver")
    if verdict["problem_id"] != portfolio["problem_id"]:
        raise ContractError("ARTIFACT_LINK_MISMATCH", "verdict and portfolio problem_id differ")
    role_links = (("selected_candidate", "primary"), ("baseline_candidate", "baseline"), ("serious_alternative", "alternative"), ("fallback_candidate", "fallback"))
    for verdict_field, portfolio_field in role_links:
        entry = portfolio[portfolio_field]
        expected = entry["candidate_id"] if entry["status"] == "CANDIDATE" else None
        if verdict[verdict_field] != expected:
            raise ContractError("ARTIFACT_LINK_MISMATCH", f"{verdict_field} does not link to {portfolio_field}")
    if verdict["artifact_hashes"]["candidate_portfolio"] != sha256_json(portfolio):
        raise ContractError("ARTIFACT_HASH_MISMATCH", "candidate_portfolio hash does not match canonical JSON")
    validate_problem_structure(structure)
    if structure["problem_id"] != portfolio["problem_id"]:
        raise ContractError("ARTIFACT_LINK_MISMATCH", "structure and portfolio problem_id differ")
    structure_hash = sha256_json(structure)
    if portfolio["problem_structure_sha256"] != structure_hash or verdict["artifact_hashes"]["problem_structure"] != structure_hash:
        raise ContractError("ARTIFACT_HASH_MISMATCH", "problem_structure hash chain is inconsistent")
    if computed == "ALLOW_FORMULATION":
        if verdict["owner_stage"] != "MODEL_SELECTION" or verdict["blocking_reason"] is not None:
            raise ContractError("INCONSISTENT_GATE_VERDICT", "allowed verdict must be owned by MODEL_SELECTION and have no blocking_reason")
        coverage = next(item["coverage"] for item in REGISTRY["families"] if item["family"] == portfolio["primary"]["model_family"])
        if verdict["family_coverage_status"] != coverage:
            raise ContractError("ARTIFACT_LINK_MISMATCH", "family coverage does not match registry")
        eligible = screen_structure(structure)["eligible_families"]
        if portfolio["primary"]["model_family"] not in eligible:
            raise ContractError("STRUCTURAL_FAMILY_INELIGIBLE", f"primary family is not eligible from structure: {eligible}")
    return verdict


def screen_structure(structure: dict[str, Any], presentation_context: str | None = None) -> dict[str, Any]:
    """Return eligibility from structure. Untrusted presentation_context has zero authority."""
    validate_problem_structure(structure)
    task_types = set(structure["task_type"])
    network = structure["network_structure"]
    families: list[str] = []
    subtype: str | None = None
    observed = bool(structure["observed_variables"])
    temporal = structure["temporal_structure"]["present"] or "temporal" in structure["sample_structure"]["dependency"].casefold()
    spatial = structure["spatial_structure"]["present"]
    network_present = network["present"]
    decision_structure = bool(structure["decision_variables"] and structure["objectives"] and structure["hard_constraints"])
    dynamic_structure = bool(structure["state_variables"] and (temporal or spatial) and (structure["initial_conditions"] or structure["boundary_conditions"]))
    if observed and task_types & {"DESCRIPTION", "REGRESSION", "CLASSIFICATION", "CAUSAL", "EVALUATION"}:
        families.append("statistical")
    if "FORECASTING" in task_types and temporal and observed:
        families.extend(["time_series", "statistical"])
    if ("EVALUATION" in task_types or "DECISION" in task_types) and observed:
        families.append("evaluation_decision")
    if "NETWORK" in task_types and network_present:
        families.append("network_routing")
        vehicle_routing = bool(network["vehicles"] and network["demands"] and network["capacities"])
        subtype = "CAPACITATED_VEHICLE_ROUTING" if vehicle_routing else "GRAPH_PATH_OR_FLOW"
    if task_types & {"OPTIMIZATION", "DECISION", "HYBRID"} and decision_structure:
        families.append("optimization")
    if "MULTI_OBJECTIVE" in task_types and decision_structure and len(structure["objectives"]) >= 2:
        families.append("multi_objective")
    if "MECHANISM" in task_types and dynamic_structure:
        families.extend(["dynamic_ode", "simulation"])
    if "SIMULATION" in task_types and (dynamic_structure or structure["uncertainty_sources"]):
        families.append("simulation")
    if observed and task_types & {"CLASSIFICATION", "REGRESSION", "FORECASTING"}:
        families.append("machine_learning")
    if "SPATIAL" in task_types and spatial:
        families.append("spatial")
    structural_components = sum((observed, temporal, spatial, network_present, decision_structure, dynamic_structure))
    if "HYBRID" in task_types and structural_components >= 2:
        families.append("hybrid")
    families = list(dict.fromkeys(families))
    registry_ids = {item["family"] for item in REGISTRY["families"]}
    return {
        "eligible_families": [family for family in families if family in registry_ids],
        "structural_subtype": subtype,
        "complexity_budget": complexity_budget(structure["sample_structure"]["n"]),
    }


def complexity_budget(n_observations: int | None) -> str:
    """Sample size changes evidence/complexity budget, never the family decision."""
    if n_observations is None:
        return "UNKNOWN_REQUIRES_SENSITIVITY"
    if n_observations < 30:
        return "LOW_WITH_STRONG_UNCERTAINTY_DISCLOSURE"
    if n_observations < 200:
        return "MODERATE_WITH_REGULARIZATION"
    return "DATA_SUPPORTS_BROADER_COMPLEXITY_SCREENING"


def queue_route(arrival_process: str, service_process: str, stationary: bool) -> dict[str, Any]:
    exact_assumptions = arrival_process == "POISSON" and service_process == "EXPONENTIAL" and stationary
    return {
        "mmc_eligible": exact_assumptions,
        "route": "QUEUEING_FORMULATION_ELIGIBLE" if exact_assumptions else "EMPIRICAL_OR_DISCRETE_EVENT_SIMULATION",
    }


def solver_hierarchy(facts: dict[str, Any]) -> list[str]:
    """Expose the mandatory exact-first escalation order for optimization."""
    route = ["ANALYTIC_OR_CLOSED_FORM_CHECK", "EXACT_SOLVER_CHECK"]
    if facts.get("multi_objective"):
        route.append("EXACT_SCALARIZATION_OR_EPSILON_CONSTRAINT")
    route.extend(["DECOMPOSITION_OR_RELAXATION", "DETERMINISTIC_NUMERICAL_OPTIMIZATION", "APPROXIMATION_WITH_BOUND"])
    if facts.get("exact_infeasible_evidence"):
        route.append("METAHEURISTIC_WITH_BASELINE_AND_GAP_EVIDENCE")
    return route
