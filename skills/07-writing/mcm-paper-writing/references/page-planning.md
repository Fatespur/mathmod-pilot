# Pre-draft page and information planning

Required sequence: Problem Complexity Assessment → PAPER_ARCHITECTURE →
PRE_DRAFT_PAGE_PLAN → PRE_DRAFT_VISUAL_PLAN → Drafting → Rendered Page Review →
Targeted Content Gap Revision → Freeze. Complete and validate `paper_page_plan.json`
before long-form prose. It is internal planning state, not a submission attachment.
Existing `paper_plan.json` remains an upstream input; it does not replace this contract.
Legacy character/award-prior planners are advisory only and cannot satisfy this gate.

## Configuration and scope

PAGE_TARGET = SOFT; PAGE_LIMIT = HARD. CUMCM defaults: target 25, soft range
[23, 27], `official_page_limit` 30. These are user-configured defaults, not a
claim that the current rules were verified. Record contest/year, rule source and
`page_count_scope`; current official rules override defaults, including scope.
Do not transfer CUMCM limits to MCM/ICM. Plan the complete paper from abstract to
references (restatement, analysis, assumptions, notation, each model, results,
validation, evaluation, conclusion included); treat appendices and official front
matter separately. Record actual official-scope count separately when it differs.
Never count appendix pages toward the 25-page target.

Assess LOW / MEDIUM / HIGH / VERY_HIGH using subproblems, datasets, model stages,
optimization, prediction, sensitivity/robustness, comparisons, derivations,
result visuals and independent validation. Explain the assessment from artifacts;
do not select complexity by contest letter alone. Suggested ranges: LOW 18–21,
MEDIUM 21–24, HIGH 23–27, VERY_HIGH 25–28. Typical complex A/B: target about 25.
Adjust target/range to actual content and the configured hard limit.

## Architecture and visuals

Use `paper_page_plan.schema.json`. Each section records purpose, information_role,
core_model, core_results, planned_pages, planned_figures, planned_tables and
validation_role. Every planned page must carry a stated technical contribution:
derivation, mechanism, algorithm design, result, comparison, data/parameter visual,
sensitivity, robustness, error analysis, validation or task closure. Bind claims
and visuals to verified evidence or explicitly record an upstream evidence gap.
The sum of section budgets must equal the target; visual totals must agree with
the unique planned IDs. No blank purpose or placeholder claims.

For a complex three-question paper, initial reference ranges (not a template):
abstract 1; restatement 0.8–1.2; analysis/framework 1.5–2; assumptions/notation
1–1.5; Q1 3.5–4.5; Q2 5–6.5; Q3 5–6.5; evaluation 1–1.5;
conclusion 0.5–1; references 1–1.5. Choose and reconcile actual allocations;
do not sum all upper bounds. Embed results and validation in appropriate sections.

Plan framework, data distribution, mechanism, algorithm, core results, comparison,
sensitivity and robustness visuals before drafting, only where useful. For complex
A/B, 6–10 major figures and 4–8 core tables are suggestions, never count gates.
If subproblem_count >= 3 OR model_stage_count >= 3 OR multiple_models OR
cross_subproblem_dependency, framework_figure_expected defaults true. A false
decision requires an explicit value-based waiver. Pseudocode is not a framework.
Route diagrams to cumcm-academic-flowchart and data charts to scipilot-figure-cumcm.

## Checkpoints and rendered review

At 25%, 50%, 80% drafting, record CONTENT_COVERAGE, SECTION_BALANCE and
PAGE_BUDGET_DRIFT with evidence. Estimates are not rendered page counts. A short
section may already be sufficient; only an identified content gap permits expansion.
After first PDF rendering, run PAGE_AND_CONTENT_GAP_REVIEW, never PAGE_PADDING.
For the default target: 23–27 IDEAL; 20–22 SHORT_BUT_ACCEPTABLE; <20
CONTENT_GAP_REVIEW_REQUIRED; 28–30 NEAR_LIMIT; > configured official limit
PAGE_LIMIT_VIOLATION = CRITICAL (use the official counting scope for this gate).
For adapted complexity targets use the planned range; low complexity is not
automatically deficient. No renderer: rendered counts/deviation remain null and
page compliance unverified. Record render path/hash and counting boundaries.

Only expand missing derivation, mechanism diagram, baseline, comparison,
robustness, sensitivity, independent validation, result visualization,
interpretation, subproblem closure or error analysis. Route missing scientific
evidence upstream under existing approval gates; never manufacture experiments.
For 20–22 pages without a gap, keep the complete draft. <20 triggers review,
not “add five pages”. Near the limit remove repetition, textbook explanations,
low-value implementation details and move suitable material to the appendix.

POST_HOC_PAGE_PADDING_FORBIDDEN = YES. No long background, duplicated restatement,
textbook algorithms, repeated formula explanations/limitations/conclusions,
defensive caveats, generic advantages/future work, duplicated visuals or ordinary
code details to fill pages. No enlarged fonts/spacing/figures, forced page breaks,
split formulas or oversized equations to inflate length. Seek sufficient total
information AND high information density. A competition-complete paper provides
sufficient derivations, visual/tabular evidence for core conclusions, supported
advantages, closure for every question and appropriate comparison/reliability
evidence; neither minimal length nor 25 pages proves quality.

Review PAGE_PLANNING_QUALITY, SECTION_BALANCE, INFORMATION_DENSITY, CONTENT_GAP
and PAGE_PADDING semantically. Distinguish genuine underdevelopment from efficient
completeness; the latter cannot receive REVISE solely for missing the soft target.
Missing pre-draft history is a planning-process finding: never backdate a plan.
Freeze only after applicable existing scientific and publication gates are met.
