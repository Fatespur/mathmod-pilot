# Error taxonomy -> owner -> recovery
INPUT_ERROR->PA->re-input ; DATA_ERROR->DP->reclean ; STRUCTURE_ERROR->PA->REVISE_FORMULATION ;
SELECTION_ERROR->MS->re-screen/portfolio fix ; FORMULATION_ERROR->S3->refix formulation ;
SOLVER_ERROR->S3(+DBG if runtime) ; NUMERIC_ERROR->S3/DBG by cause ; VALIDATION_ERROR->S4 rerun checks ;
SCHEMA_ERROR->PRODUCING stage fix+relint ; RUNTIME_ERROR->systematic-debugging->RETURN responsible stage ;
INTEGRITY_ERROR->ORCHESTRATOR HARD STOP (no auto-continue).
DBG boundary locked: runtime/dependency/filesystem/syntax/env ONLY; then return to responsible stage.
