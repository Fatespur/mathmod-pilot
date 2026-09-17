import copy
import unittest

from validate_selection import (
    REGISTRY, ContractError, anti_template_verdict, queue_route, screen_structure,
    sha256_json, solver_hierarchy, validate_portfolio, validate_problem_structure,
    validate_selection_verdict,
)


def valid_structure(task_type=None):
    return {
        "schema_version": "problem_structure.schema.v1", "problem_id": "fixture",
        "task_type": task_type or ["FORECASTING"],
        "purpose": "estimate a contest-relevant quantity", "estimand_or_decision": "future response",
        "sets": [], "indices": [{"name": "t", "meaning": "time index"}],
        "decision_variables": [{"name": "x", "meaning": "output", "unit": "1", "domain": "real"}],
        "state_variables": [], "observed_variables": [{"name": "y", "meaning": "observation", "unit": "1", "domain": "real"}],
        "parameters": [], "objectives": [{"id": "o1", "sense": "PREDICT", "quantity": "future response", "decision_relevance": "supports planning"}],
        "hard_constraints": [{"id": "c1", "statement": "observations are finite", "source": "data contract"}], "soft_constraints": [],
        "boundary_conditions": [], "initial_conditions": [],
        "data_dependencies": [{"name": "observations", "role": "input", "availability": "AVAILABLE", "leakage_risk": "future timestamps"}],
        "sample_structure": {"n": 100, "p": 2, "sampling_unit": "day", "dependency": "temporal", "missingness": "none", "imbalance": "not applicable"},
        "temporal_structure": {"present": True, "features": ["ordered observations"], "risks": ["drift"]},
        "spatial_structure": {"present": False, "features": [], "risks": []},
        "group_structure": {"present": False, "features": [], "risks": []},
        "network_structure": {"present": False, "directed": False, "weighted": False, "capacities": False, "demands": False, "vehicles": False, "depots": False, "time_windows": False, "flow_conservation": False, "subtour_risk": False, "multiple_commodities": False, "dynamic_state": False},
        "uncertainty_sources": [{"id": "u1", "source": "measurement", "kind": "MEASUREMENT", "decision_impact": "changes interval width"}],
        "assumptions": [{"id": "a1", "statement": "sampling is consistent", "type": "DATA", "necessity": "needed for comparable records", "risk": "HIGH", "falsifier": "timestamp audit fails", "evidence": ["timestamps"], "downstream_dependency": ["forecast validation"]}],
        "identifiability_risks": [{"id": "r1", "statement": "short horizon", "impact": "weak separation", "resolution": "report uncertainty"}],
        "expected_ranges": [{"quantity": "prediction", "lower": None, "upper": None, "unit": "1", "basis": "not yet bounded"}],
        "unresolved_ambiguities": [],
    }


def candidate(role, cid):
    family = {"BASELINE": "statistical", "PRIMARY": "statistical", "ALTERNATIVE": "time_series", "FALLBACK": "machine_learning"}[role]
    method = {"BASELINE": "simple baseline", "PRIMARY": "regularized estimate", "ALTERNATIVE": "dynamic alternative", "FALLBACK": "fallback predictor"}[role]
    required = list(next(item["required_preconditions"] for item in REGISTRY["families"] if item["family"] == family))
    return {"status": "CANDIDATE", "candidate_id": cid, "role": role, "model_family": family, "specific_method_if_known": method,
            "problem_structure_match": ["continuous outcome"], "required_preconditions": required, "supported_preconditions": list(required), "violated_preconditions": [], "unknown_preconditions": [],
            "assumptions": ["stable relation"], "data_requirements": ["observations"], "identifiability_requirements": ["variation"], "formulation_sketch": "estimate relation from observations", "solver_class": "CONVEX_EXACT", "solver_hierarchy_evidence": {"screened_levels": ["ANALYTICAL", "CONVEX_EXACT"], "metaheuristic_allowed": False, "exact_infeasibility_evidence": None}, "expected_complexity": "low", "interpretability": "high",
            "expected_failure_modes": ["misspecification"], "failure_signatures": ["structured residuals"], "validation_plan": ["held-out residual audit"], "advantages": ["auditable baseline"], "limitations": ["limited nonlinearity"],
            "why_use": "matches the explicit mathematical structure", "why_not": "reject if residual structure remains material", "replacement_trigger": "replace when residual audit shows systematic failure"}


def valid_portfolio():
    roles = [("baseline", "BASELINE"), ("primary", "PRIMARY"), ("alternative", "ALTERNATIVE"), ("fallback", "FALLBACK")]
    criteria = ["STRUCTURE_MATCH", "PRECONDITIONS", "DATA_COMPATIBILITY", "IDENTIFIABILITY_RISK", "CONSTRAINT_HANDLING", "EXPECTED_ACCURACY", "ROBUSTNESS_POTENTIAL", "INTERPRETABILITY", "COMPUTATIONAL_COST", "VALIDATION_FEASIBILITY"]
    result = {"schema_version": "candidate_portfolio.schema.v1", "problem_id": "fixture", "problem_structure_sha256": "a" * 64}
    for key, role in roles:
        result[key] = candidate(role, key)
    result["screening_matrix"] = [{"criterion": item, "baseline": "ok", "primary": "ok", "alternative": "ok", "fallback": "ok", "evidence": ["fixture"]} for item in criteria]
    return result


ANSWERS = {
    "q1": "primary statistical matches the continuous outcome mathematical structure",
    "q2": "baseline is insufficient: reject if residual structure remains material",
    "q3": "alternative time_series dynamic alternative is the serious competing candidate",
    "q4": "alternative was rejected: reject if residual structure remains material",
    "q5": "sampling unit defined; dependence structure addressed; estimand and error assumptions explicit",
    "q6": "replace when residual audit shows systematic failure",
}
ALLOWED = ["MATHEMATICAL_STRUCTURE", "DATA_COMPATIBILITY", "ASSUMPTION_COMPATIBILITY"]


class SchemaAndGateTests(unittest.TestCase):
    def test_valid_problem_structure_accepted(self):
        self.assertEqual(validate_problem_structure(valid_structure())["problem_id"], "fixture")

    def test_problem_structure_rejects_named_model_field(self):
        value = valid_structure(); value["selected_model"] = "ARIMA"
        with self.assertRaisesRegex(ContractError, "PREMATURE_MODEL_SELECTION"): validate_problem_structure(value)

    def test_problem_structure_rejects_named_model_in_value(self):
        value = valid_structure(); value["open_questions"] = ["Should we use TOPSIS?"]
        with self.assertRaisesRegex(ContractError, "PREMATURE_MODEL_SELECTION"): validate_problem_structure(value)

    def test_missing_baseline_rejected(self):
        value = valid_portfolio(); del value["baseline"]
        with self.assertRaisesRegex(ContractError, "INVALID_CANDIDATE_PORTFOLIO"): validate_portfolio(value)

    def test_missing_primary_rejected(self):
        value = valid_portfolio(); del value["primary"]
        with self.assertRaisesRegex(ContractError, "INVALID_CANDIDATE_PORTFOLIO"): validate_portfolio(value)

    def test_missing_why_not_rejected(self):
        value = valid_portfolio(); del value["primary"]["why_not"]
        with self.assertRaisesRegex(ContractError, "INVALID_CANDIDATE_PORTFOLIO"): validate_portfolio(value)

    def test_invalid_na_rejected(self):
        value = valid_portfolio(); value["fallback"] = {"status": "N/A", "role": "FALLBACK", "na_reason": "short"}
        with self.assertRaisesRegex(ContractError, "INVALID_CANDIDATE_PORTFOLIO"): validate_portfolio(value)

    def test_gate_allows_evidence_route(self):
        self.assertEqual(anti_template_verdict(valid_portfolio(), ALLOWED, ANSWERS), "ALLOW_FORMULATION")

    def test_gate_rejects_keyword_route(self):
        self.assertEqual(anti_template_verdict(valid_portfolio(), ["KEYWORD"], ANSWERS), "REJECT_TEMPLATE_ROUTE")

    def test_gate_rejects_sample_band_route(self):
        self.assertEqual(anti_template_verdict(valid_portfolio(), ["SAMPLE_SIZE_BAND"], ANSWERS), "REJECT_TEMPLATE_ROUTE")

    def test_gate_revises_na_baseline(self):
        value = valid_portfolio(); value["baseline"] = {"status": "N/A", "role": "BASELINE", "na_reason": "For fixture, no defensible simple comparator has yet been constructed."}
        self.assertEqual(anti_template_verdict(value, ALLOWED, ANSWERS), "REVISE_SELECTION")

    def test_gate_revises_na_serious_alternative(self):
        value = valid_portfolio(); value["alternative"] = {"status": "N/A", "role": "ALTERNATIVE", "na_reason": "For fixture, no serious competing family has yet passed structural screening."}
        self.assertEqual(anti_template_verdict(value, ALLOWED, ANSWERS), "REVISE_SELECTION")

    def test_gate_revises_unknown_precondition(self):
        value = valid_portfolio(); moved = value["primary"]["supported_preconditions"].pop(); value["primary"]["unknown_preconditions"] = [moved]
        self.assertEqual(anti_template_verdict(value, ALLOWED, ANSWERS), "REVISE_SELECTION")

    def test_gate_revises_unlinked_boilerplate_answers(self):
        answers = {f"q{i}": f"generic answer with sufficient character count {i}" for i in range(1, 7)}
        self.assertEqual(anti_template_verdict(valid_portfolio(), ALLOWED, answers), "REVISE_SELECTION")

    def test_duplicate_candidate_ids_rejected(self):
        value = valid_portfolio(); value["alternative"]["candidate_id"] = value["primary"]["candidate_id"]
        with self.assertRaisesRegex(ContractError, "candidate_id values must be unique"): validate_portfolio(value)

    def test_empty_matrix_evidence_rejected(self):
        value = valid_portfolio(); value["screening_matrix"][0]["evidence"] = []
        with self.assertRaisesRegex(ContractError, "INVALID_CANDIDATE_PORTFOLIO"): validate_portfolio(value)

    def test_metaheuristic_without_escalation_evidence_rejected(self):
        value = valid_portfolio(); value["primary"]["solver_class"] = "METAHEURISTIC"
        with self.assertRaisesRegex(ContractError, "HEURISTIC_ESCALATION_UNJUSTIFIED"): validate_portfolio(value)

    def test_differential_evolution_and_incomplete_hierarchy_rejected(self):
        value = valid_portfolio(); value["primary"]["solver_class"] = "METAHEURISTIC"; value["primary"]["specific_method_if_known"] = "differential evolution"
        value["primary"]["solver_hierarchy_evidence"] = {"screened_levels": ["METAHEURISTIC"], "metaheuristic_allowed": True, "exact_infeasibility_evidence": "exact solver route was not actually investigated in this fixture"}
        with self.assertRaisesRegex(ContractError, "HEURISTIC_ESCALATION_UNJUSTIFIED"): validate_portfolio(value)

    def test_normalized_metaheuristic_with_per_level_evidence_accepted(self):
        value = valid_portfolio(); value["primary"]["solver_class"] = "METAHEURISTIC"; value["primary"]["specific_method_if_known"] = "ant colony optimization"
        levels = ["ANALYTICAL", "CONVEX_EXACT", "DISCRETE_EXACT", "DECOMPOSITION", "DETERMINISTIC_NUMERICAL", "APPROXIMATION", "METAHEURISTIC"]
        evidence = "; ".join(f"{level}: fixture-specific audit found this level cannot preserve the documented discontinuous feasible structure" for level in levels[:-1])
        value["primary"]["solver_hierarchy_evidence"] = {"screened_levels": levels, "metaheuristic_allowed": True, "exact_infeasibility_evidence": evidence}
        self.assertEqual(validate_portfolio(value)["primary"]["solver_class"], "METAHEURISTIC")

    def test_preconditions_must_be_complete_partition(self):
        value = valid_portfolio(); value["primary"]["required_preconditions"].append("stationarity proven")
        with self.assertRaisesRegex(ContractError, "PRECONDITION_PARTITION_INVALID"): validate_portfolio(value)

    def test_alternative_must_differ_from_primary(self):
        value = valid_portfolio(); value["alternative"]["model_family"] = value["primary"]["model_family"]; value["alternative"]["specific_method_if_known"] = value["primary"]["specific_method_if_known"]
        value["alternative"]["required_preconditions"] = value["primary"]["required_preconditions"]; value["alternative"]["supported_preconditions"] = value["primary"]["supported_preconditions"]
        with self.assertRaisesRegex(ContractError, "serious alternative must differ from the primary"): validate_portfolio(value)

    def test_alternative_clone_casing_is_rejected(self):
        value = valid_portfolio(); value["alternative"]["model_family"] = value["primary"]["model_family"]; value["alternative"]["specific_method_if_known"] = " Regularized Estimate "
        value["alternative"]["required_preconditions"] = list(value["primary"]["required_preconditions"]); value["alternative"]["supported_preconditions"] = list(value["primary"]["supported_preconditions"])
        with self.assertRaises(ContractError): validate_portfolio(value)

    def test_blank_substantive_evidence_rejected(self):
        value = valid_portfolio(); value["primary"]["validation_plan"] = [""]
        with self.assertRaisesRegex(ContractError, "blank evidence"): validate_portfolio(value)

    def test_popularity_rationale_rejected_even_if_basis_is_misreported(self):
        value = valid_portfolio(); value["primary"]["why_use"] = "selected because it is popular in competitions"
        with self.assertRaisesRegex(ContractError, "TEMPLATE_BASIS_DECLARED"): anti_template_verdict(value, ALLOWED, ANSWERS)

    def test_fashionable_winning_paper_rationale_in_matrix_rejected(self):
        value = valid_portfolio(); value["screening_matrix"][0]["primary"] = "selected because fashionable in winning papers"; value["screening_matrix"][0]["evidence"] = ["widely used contest winner"]
        with self.assertRaisesRegex(ContractError, "TEMPLATE_BASIS_DECLARED"): validate_portfolio(value)

    def test_precise_named_method_detection_has_no_arima_substring_false_positive(self):
        value = valid_structure(); value["purpose"] = "Study the Marimar coastal site"
        self.assertEqual(validate_problem_structure(value)["purpose"], "Study the Marimar coastal site")

    def test_additional_named_methods_rejected(self):
        for method in ("support vector machine", "neural network", "DEA", "AHP", "PCA", "Prophet", "K-means", "SARIMAX", "LightGBM", "CatBoost", "CNN", "BERT", "Holt-Winters", "exponential smoothing", "Kalman filter", "Gaussian process", "Monte Carlo", "ResNet", "ridge regression", "LASSO", "decision tree", "k-nearest neighbors", "SIR model"):
            value = valid_structure(); value["purpose"] = f"Use {method} for the final answer"
            with self.subTest(method=method), self.assertRaisesRegex(ContractError, "PREMATURE_MODEL_SELECTION"):
                validate_problem_structure(value)

    def test_domain_transformer_is_not_neural_model_false_positive(self):
        value = valid_structure(); value["purpose"] = "optimize transformer loading under capacity limits"
        self.assertEqual(validate_problem_structure(value)["problem_id"], "fixture")

    def test_gate_rejects_popularity_hidden_in_answers(self):
        answers = dict(ANSWERS); answers["q1"] = "primary statistical matches continuous outcome but is popular in every contest"
        self.assertEqual(anti_template_verdict(valid_portfolio(), ALLOWED, answers), "REJECT_TEMPLATE_ROUTE")


class MetamorphicTests(unittest.TestCase):
    def test_m1_paraphrase_does_not_change_cvrp_route(self):
        value = valid_structure(["NETWORK", "OPTIMIZATION"])
        value["network_structure"].update({"present": True, "capacities": True, "demands": True, "vehicles": True, "depots": True})
        a_value = copy.deepcopy(value); b_value = copy.deepcopy(value)
        a_value["purpose"] = "shortest delivery"; b_value["purpose"] = "minimize travel"
        a = screen_structure(a_value); b = screen_structure(b_value)
        self.assertEqual(a, b); self.assertEqual(a["structural_subtype"], "CAPACITATED_VEHICLE_ROUTING")

    def test_m2_sample_threshold_does_not_flip_family(self):
        a = valid_structure(); b = copy.deepcopy(a); a["sample_structure"]["n"] = 19; b["sample_structure"]["n"] = 21
        self.assertEqual(screen_structure(a)["eligible_families"], screen_structure(b)["eligible_families"])

    def test_m3_sponsor_preference_cannot_enter_structure(self):
        value = valid_structure(["CLASSIFICATION"])
        a = screen_structure(value, presentation_context="classify a small table")
        b = screen_structure(value, presentation_context="the sponsor asks for a neural network")
        self.assertEqual(a, b); self.assertNotIn("deep_learning", b["eligible_families"])

    def test_m4_indicator_rename_does_not_change_family(self):
        a = valid_structure(["EVALUATION"]); b = copy.deepcopy(a)
        a["observed_variables"][0]["name"] = "indicator_A"; b["observed_variables"][0]["name"] = "renamed_17"
        self.assertEqual(screen_structure(a)["eligible_families"], screen_structure(b)["eligible_families"])

    def test_m5_multiobjective_phrase_does_not_change_hierarchy(self):
        value = valid_structure(["MULTI_OBJECTIVE", "OPTIMIZATION"])
        value["objectives"].append({"id": "o2", "sense": "MINIMIZE", "quantity": "cost", "decision_relevance": "competes with service"})
        a = screen_structure(value, presentation_context="multi-objective")
        b = screen_structure(value, presentation_context="two competing objectives")
        self.assertEqual(a, b); self.assertIn("multi_objective", a["eligible_families"])


class TargetedRegressionLocks(unittest.TestCase):
    def test_t01_t18_evaluation_not_forced_to_topsis(self):
        route = screen_structure(valid_structure(["EVALUATION"]))
        self.assertEqual(set(route["eligible_families"]), {"evaluation_decision", "statistical"})

    def test_t02_forecasting_not_forced_to_grey_model(self):
        route = screen_structure(valid_structure())
        self.assertEqual(set(route["eligible_families"]), {"time_series", "statistical", "machine_learning"})

    def test_t04_vehicle_routing_not_shortest_path(self):
        value = valid_structure(["NETWORK", "OPTIMIZATION"]); value["network_structure"].update({"present": True, "capacities": True, "demands": True, "vehicles": True})
        self.assertEqual(screen_structure(value)["structural_subtype"], "CAPACITATED_VEHICLE_ROUTING")

    def test_t11_mmc_requires_distributional_assumptions(self):
        self.assertFalse(queue_route("UNKNOWN", "HEAVY_TAILED", True)["mmc_eligible"])
        self.assertTrue(queue_route("POISSON", "EXPONENTIAL", True)["mmc_eligible"])

    def test_t12_exact_multiobjective_route_precedes_metaheuristic(self):
        route = solver_hierarchy({"multi_objective": True, "exact_infeasible_evidence": True})
        self.assertLess(route.index("EXACT_SCALARIZATION_OR_EPSILON_CONSTRAINT"), route.index("METAHEURISTIC_WITH_BASELINE_AND_GAP_EVIDENCE"))

    def test_t17_named_deep_model_request_has_no_authority(self):
        value = valid_structure(["CLASSIFICATION"])
        ordinary = screen_structure(value, presentation_context="tabular classification")
        requested = screen_structure(value, presentation_context="use neural network because the sponsor requests AI")
        self.assertEqual(ordinary, requested)

    def test_t07_integer_route_keeps_exact_check(self):
        self.assertIn("EXACT_SOLVER_CHECK", solver_hierarchy({"integer": True}))

    def test_t20_mechanism_route_preserved(self):
        value = valid_structure(["MECHANISM"])
        value["state_variables"] = [{"name": "z", "meaning": "physical state", "domain": "real", "unit": "1"}]
        value["initial_conditions"] = ["z(0) is observed"]
        self.assertEqual(screen_structure(value)["eligible_families"], ["dynamic_ode", "simulation"])

    def test_task_label_without_structure_does_not_route(self):
        value = valid_structure(["NETWORK"])
        self.assertNotIn("network_routing", screen_structure(value)["eligible_families"])

    def test_description_and_causal_registry_coverage(self):
        self.assertIn("statistical", screen_structure(valid_structure(["DESCRIPTION"]))["eligible_families"])
        self.assertIn("statistical", screen_structure(valid_structure(["CAUSAL"]))["eligible_families"])


class VerdictIntegrityTests(unittest.TestCase):
    def make_artifacts(self):
        structure = valid_structure(); portfolio = valid_portfolio()
        portfolio["problem_structure_sha256"] = sha256_json(structure)
        gate = {"version": "ANTI_TEMPLATE_GATE.v1", "verdict": "ALLOW_FORMULATION", "q1_structure": ANSWERS["q1"], "q2_baseline": ANSWERS["q2"], "q3_alternative": ANSWERS["q3"], "q4_why_not_alternative": ANSWERS["q4"], "q5_preconditions": ANSWERS["q5"], "q6_replacement_observation": ANSWERS["q6"], "selection_basis": ALLOWED}
        verdict = {"schema_version": "selection_verdict.schema.v1", "problem_id": "fixture", "selected_candidate": "primary", "baseline_candidate": "baseline", "serious_alternative": "alternative", "fallback_candidate": "fallback", "anti_template_gate": gate, "precondition_summary": "required evidence is supported", "why_primary": "primary matches the supported structure", "why_not_baseline": "baseline leaves structured residual failure", "why_not_alternative": "alternative adds unsupported dynamic assumptions", "replacement_trigger": "replace when residual audit shows systematic failure", "known_limitations": ["misspecification"], "family_coverage_status": "SUPPORTED", "artifact_hashes": {"problem_structure": sha256_json(structure), "candidate_portfolio": sha256_json(portfolio)}, "blocking_reason": None, "owner_stage": "MODEL_SELECTION", "required_action": "PROCEED_TO_SOLVER", "revision_id": "r1"}
        return structure, portfolio, verdict

    def test_linked_verdict_accepted(self):
        structure, portfolio, verdict = self.make_artifacts()
        self.assertEqual(validate_selection_verdict(verdict, portfolio, structure)["required_action"], "PROCEED_TO_SOLVER")

    def test_nonexistent_selected_candidate_rejected(self):
        structure, portfolio, verdict = self.make_artifacts(); verdict["selected_candidate"] = "ghost"
        with self.assertRaisesRegex(ContractError, "ARTIFACT_LINK_MISMATCH"): validate_selection_verdict(verdict, portfolio, structure)

    def test_fake_portfolio_hash_rejected(self):
        structure, portfolio, verdict = self.make_artifacts(); verdict["artifact_hashes"]["candidate_portfolio"] = "0" * 64
        with self.assertRaisesRegex(ContractError, "ARTIFACT_HASH_MISMATCH"): validate_selection_verdict(verdict, portfolio, structure)

    def test_structurally_ineligible_primary_rejected(self):
        structure, portfolio, verdict = self.make_artifacts()
        portfolio["primary"] = candidate("PRIMARY", "primary"); portfolio["primary"]["model_family"] = "spatial"; portfolio["primary"]["specific_method_if_known"] = "spatial candidate"
        required = next(item["required_preconditions"] for item in REGISTRY["families"] if item["family"] == "spatial")
        portfolio["primary"]["required_preconditions"] = required; portfolio["primary"]["supported_preconditions"] = required
        portfolio["problem_structure_sha256"] = sha256_json(structure)
        verdict["family_coverage_status"] = "COVERAGE_LIMITED"; verdict["artifact_hashes"]["candidate_portfolio"] = sha256_json(portfolio)
        verdict["anti_template_gate"]["q1_structure"] = "primary spatial matches the continuous outcome mathematical structure"
        verdict["anti_template_gate"]["q5_preconditions"] = "; ".join(required)
        with self.assertRaisesRegex(ContractError, "STRUCTURAL_FAMILY_INELIGIBLE"): validate_selection_verdict(verdict, portfolio, structure)


if __name__ == "__main__":
    unittest.main(verbosity=2)
