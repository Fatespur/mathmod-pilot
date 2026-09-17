# Pipeline Integration and Paper Workflow

## Contents

- Stage ownership
- Required inputs
- S6A content workflow
- S6B document workflow
- Outputs and handoff
- Failure routing

## Stage ownership

`mcm-paper-writing` owns paper synthesis and document production at S6. It consumes verified artifacts; it does not replace the upstream owners.

| Source | Required evidence | Route when missing |
|---|---|---|
| S1 | subproblems, method rationale, assumptions, hard assertions | `$problem-analyzer` |
| S2 | data dictionary, cleaning decisions, sample changes | `$data-processing` |
| S3 | model, algorithm, parameters, results, runnable code | `$mle-solver` |
| S4 | validation metrics, sensitivity, uncertainty, robustness | `$model-validation` |
| S5 | figures, captions, data snapshots, generation code | the responsible figure skill |
| AUX | verified references and `paper_macros.json` | `$reference-manager` or the originating stage |

Do not import hypothetical `pipeline`, `paper_reference`, or `mcm_paper` packages. Use `pipeline_manifest.json` and explicit skill handoffs.

## Required inputs

Before S6A, confirm:

- `pipeline_manifest.json` has schema version 1.0 and completed required upstream stages.
- Every declared input exists and every supplied SHA-256 digest matches.
- `paper_macros.json` passes `paper_number_validator.py --validate-macros-only`.
- References have retrievable source metadata; unknown citations are blocked, not invented.
- Figure/table/equation sources are present and linked to the claims they support.

Before S6B, additionally discover:

- current national rules supplied by the user;
- regional and school notices;
- commitment, numbering, and abstract pages;
- official DOCX templates;
- submission-system instructions or screenshots;
- code and supporting-material folders;
- declared participant identity terms for anonymity scanning;
- actual AI use records.

## S6A content workflow

1. Lock contest mode and language.
2. Create `section_evidence_map.json` with `claim_id`, source artifacts, macro keys, citations, and status.
3. Draft the abstract and paper sections from verified evidence.
4. Keep CUMCM and MCM/ICM structures, phrase banks, and citations isolated.
5. Extract equations and establish meaningful labels before document formatting.
6. Run number and citation audits after each major section and again after the full draft.
7. Freeze content only after claims, numbers, figures, tables, equations, and references agree.

Example evidence item:

```json
{
  "section": "六、模型检验",
  "claims": [
    {
      "claim_id": "C6-01",
      "source_artifacts": ["validation_metrics.json"],
      "macro_keys": ["validation.r2", "validation.rmse"],
      "citation_ids": [],
      "status": "ready"
    }
  ]
}
```

## S6B document workflow

1. Build a rule manifest in precedence order and record each rule as `OFFICIAL-MANDATORY`, `CONSERVATIVE-SAFETY`, or `RECOMMENDED-DEFAULT`.
2. Copy, never overwrite, any official template. Preserve official fixed pages.
3. Create the named Word styles and section/page-number scheme.
4. Validate Markdown math with equation-workflow.md; use a verified native OMML exporter for equations.
5. Create `paper_submission.docx` from the abstract onward.
6. Create `paper_print.docx` only when authentic official front matter is available and preserved.
7. Export `paper_submission.pdf`; verify that it matches the submission DOCX and is under the file limit.
8. Run structural, style, equation, citation, anonymity, AI disclosure, and supporting-material checks.
9. Render every PDF page to PNG and inspect all pages at 100%.
10. Fix, regenerate, rerun validation, and repeat the full render inspection. Complete at least two generation-render-review cycles.
11. Emit Chinese reports with `PASS`, `WARNING`, `FAIL`, or `NOT APPLICABLE` for every gate.

## Outputs and handoff

Content outputs:

- `paper.md`
- `section_evidence_map.json`
- `paper_number_report.json`
- `citation_audit.json`

Document outputs, when applicable:

- `paper_print.docx`
- `paper_submission.docx`
- `paper_submission.pdf`
- `equations.tex`
- `equation_mapping.json`
- `supporting_materials.zip` or `.rar`
- `AI工具使用详情.pdf` when AI was used
- `formatting_report.md`
- `validation_report.json`

Record paths, hashes, generation commands, rule sources, checks run, automatic fixes, and outstanding manual checks in `paper_manifest.json`. Mark S6 `completed` only when required deliverables exist and blocking gates pass. Then hand off to `$paper-review`.

## Failure routing

- Number mismatch: return to the stage that first produced the value; do not hand-edit it in the paper.
- Figure/text mismatch: verify S3/S4 results, then regenerate S5 before updating S6.
- Missing or unverifiable reference: ask `$reference-manager`; remove or rewrite the claim if no real source exists.
- Missing validation evidence: return to S4; do not hide the gap with vague prose.
- Missing official front matter: generate only the electronic variant and report the print variant as blocked; never imitate official pages.
- Native converter unavailable: retain canonical Markdown and report WORD_NATIVE_EXPORT_PIPELINE = NOT_PRESENT; do not use a manual-conversion layout.
- Identity finding: stop delivery until the finding is classified and resolved; do not delete legitimate reference authors.
- Render defect: repair the DOCX and restart the render-review cycle.
