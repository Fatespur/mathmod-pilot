# Integration contracts (canonical chain / revision / identifiability / schema SoT)
CANONICAL CHAIN: see SKILL.md. Producers: 01 PA;02 DP;03/04 MS;05/06 S3;07/08 S4;09 ORCH(assembly-only).
Legacy alias: 08_release_decision <- model_validation_gate.json | validation_verdict.json (read-compat;
new authoritative writes use canonical single name; dual authoritative writes FORBIDDEN).
SCHEMA SOURCE OF TRUTH: masters live with owning stage (problem_structure.schema.v1.json in
model-selection/references; workflow_state here). pipeline_manifest.schema.json master pinned at
model-selection/references/pipeline_manifest.schema.json (ba3ab702...); copies in PA/S3/MV/DP are
VERIFIED-IDENTICAL VIEWS — sync enforced by scripts/check_schema_copies.py, no independent edits.
REVISION: fields per SKILL.md; MINIMUM_VALID_REENTRY_POINT = anchor artifact of target + descendants
invalidated, all preserved artifacts reused by hash. Loop guard: >3 consecutive same-target revisions
=> TERMINAL_REVIEW_REQUIRED.
IDENTIFIABILITY BOUNDARY: MS screening = ADVISORY risk indication feeding portfolio reasoning;
S4 identifiability/observability gate = AUTHORITATIVE release judgment (may veto). Screening can
never upgrade itself into a release veto; gate never delegated back to screening.
ERROR OWNERSHIP: see error_taxonomy.md.
