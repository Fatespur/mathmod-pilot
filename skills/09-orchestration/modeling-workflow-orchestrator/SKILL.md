---
name: modeling-workflow-orchestrator
title: Mathematical Modeling State-Machine Orchestrator
category: orchestration
stage: S0
description: "全流程状态机编排引擎：工件有向无环图（Artifact DAG）、状态跃迁控制、上游修改级联失效机制与审阅回退路由"
inputs: ["workflow_state.json", "run_inputs.json", "artifact_registration_events"]
outputs: ["workflow_state.json", "pipeline_manifest.json", "final_release_verification.json"]
dependencies: []
---

# Modeling Workflow Orchestrator — state machine only

Consume structured verdicts literally. Never reinterpret REVISE/FAIL into PASS classes.
Solver entry requires recorded SELECTION_AUTHORIZED (protects selection-stage refusal).
Integrity failures (hash mismatch/state corruption) hard-stop.

## Canonical artifact chain
01_problem_structure · 02_data_profile(opt) · 03_candidate_portfolio · 04_selection_verdict ·
05_model_formulation · 06_solver_result · 07_validation_evidence · 08_release_decision ·
09_final_modeling_summary(assembly-only). Legacy alias: model_validation_gate.json /
validation_verdict.json → read-compatible with 08_release_decision; new writes use canonical name.
Schema source of truth registry: schemas/SCHEMA_SOURCE_OF_TRUTH.md (pinned master + verified copies).

## State machine
START→PROBLEM_ANALYSIS→(02? DATA_ASSESSMENT:—)→MODEL_SELECTION→(authorized? FORMULATION:
REVISION[MODEL_SELECTION])→NUMERICAL_EXECUTION→VALIDATION→{PASS→FINALIZE; PWL→FINALIZE_LIMITED;
REVISE→REVISION(route owner); FAIL→FAILED_BLOCKED}. REVISION uses revision_target/invalidated set;
loop guard MAX_REVISION_DEPTH exceeded ⇒ TERMINAL_REVIEW_REQUIRED (no silent loops).

## Revision contract fields
revision_target ∈ {PROBLEM_STRUCTURE,DATA_PROCESSING,MODEL_SELECTION,MODEL_FORMULATION,
NUMERICAL_EXECUTION,VALIDATION_EVIDENCE,DATA_COLLECTION}; required_action,reason_code,source_stage,
resume_stage,invalidated_artifacts,preserved_artifacts,revision_depth,revision_id.
Invalidation = target + all downstream descendants (DAG in references/artifact_invalidation_dag.json).

## Error taxonomy & ownership
INPUT/DATA/STRUCTURE/SELECTION/FORMULATION/SOLVER/NUMERIC/VALIDATION/SCHEMA/RUNTIME/INTEGRITY →
owner map in references/error_taxonomy.md. RUNTIME→systematic-debugging then RETURN to responsible
stage (debugger never changes models/assumptions/verdicts). INTEGRITY→hard stop.

## Persistence / resume
workflow_state.json per schemas/workflow_state.schema.v1.json (workflow_id,current_stage,
completed_stages,active_artifacts+hashes,invalidated,revision_history,current_verdict,required_action,
release_scope,error_state,resume_stage,timestamp). Resume verifies hashes; mismatch=INTEGRITY stop.

## Family packs
Advisory knowledge only (machine-readable sidecars under references/family_pack_sidecars/).
Identifiability: MS screening = advisory indication; S4 gate = authoritative release judgment.

## Scripts
scripts/orchestrator.py — init|advance|resume|route-revision|assemble-summary|verify.
tests/ — B1 chain tests, B2 routing tests, Level-2 state-machine suite.
'
## Production V4 integration

For new runs in the modeling project, the production defaults and stage/owner contracts are in production/production_defaults.json and production/skill_routing_manifest.json. Use the repository orchestrator_v3.py CLI as the sole runtime authority; the filename is retained for compatibility. S0–S7 are semantic stages mapped to its existing HITL states. Installed standalone orchestrator scripts remain legacy-run readers, not a second controller for RELEASE_V4. Never write workflow_state or pipeline_manifest directly; register outputs and skill events through the runtime. Existing human Gates A/B/C/D and scientific vetoes remain binding.
