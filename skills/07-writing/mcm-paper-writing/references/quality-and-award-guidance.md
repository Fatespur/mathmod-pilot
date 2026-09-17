# Evidence and Award-Quality Guidance

## Contents

- Hard evidence gates
- Quality heuristics
- Abstract and conclusion
- Figures and tables
- Ethics and reproducibility

## Hard evidence gates

These are workflow gates, not claims about an award outcome.

1. Back every numerical claim with a model/data artifact and `paper_macros.json`.
2. Keep the abstract standalone and consistent with the body.
3. Justify every model assumption and method choice.
4. Define notation and use it consistently.
5. Cite and interpret every figure and table.
6. Match validation methods to the model and claim; report actual metrics, samples, and uncertainty.
7. Verify every citation and DOI/URL; never fabricate metadata.
8. Keep contest modes isolated.
9. Preserve complete runnable code and provenance.
10. Pass document, anonymity, AI disclosure, and visual-render gates before delivery.

Reject unsupported phrases such as “模型效果良好”“充分证明”“显著优于” unless the immediately surrounding text supplies the appropriate verified comparison, metric, statistical evidence, or uncertainty.

## Quality heuristics and anti-padding guidelines

Treat historical winning-paper patterns as `RECOMMENDED-DEFAULT` empirical planning priors (such as from `award_writing_profile.json`), never as rigid quotas. Use them to maintain balanced narrative depth and prevent either defensive under-writing or artificial padding.

- **Scientific Depth vs. True Padding**:
  - **What is NOT padding (High-Value Scientific Substance)**:
    - Mechanistic modeling derivations, coordinate transformations, and intermediate algebraic transition steps (prohibiting lone final formulas).
    - Algorithm convergence properties, hyperparameter selection rationale, and computational complexity analysis.
    - Result analysis: RESULT / MECHANISM / EVIDENCE / ADVANTAGE; limitations only where omission materially misleads, with systemic detail disclosed once.
    - Purposeful figure/table interpretation: flexible length by narrative role; no sentence quota or filler.
  - **What IS true padding (Strictly Prohibited)**:
    - Empty boilerplate text, repetitive praise without data (e.g. “具有重大意义”“效果极佳”), re-copying the original problem statement verbatim, or inserting oversized floating figures solely to consume blank page height.
- Prefer one coherent modeling narrative to unrelated method stacking.
- Explain why each method is necessary and what evidence it contributes.
- Expose assumptions, limitations, identifiability, and failure conditions.
- Compare against a meaningful baseline when the claim is comparative.
- Connect sensitivity or uncertainty results to decisions, not only plots.
- Make the model reproducible from the appendix and supporting materials.
- Allocate space by subproblem importance score and proof burden governed by `paper_plan.json`.

## Abstract and conclusion

For CUMCM, write the abstract as continuous Chinese prose and keep it to one page. Cover each subproblem with the named method and central quantitative result, then include validation and robustness evidence. Do not cite figures, tables, or long derivations in the abstract.

Write conclusions as coherent prose unless the problem explicitly calls for a list. Preserve the same numerical facts as the abstract/body without copying sentences verbatim or adding new claims.

For MCM/ICM, use the current official Summary Sheet requirements. A useful heuristic is to include the problem, integrated approach, methodological contribution, key results, validation, and practical implications. Do not hard-code historical word counts or revision counts as requirements.

## Figures and tables

- Use figures and tables only when they reduce explanation cost or support a decision.
- Bind each visual to its source data, generation code, caption, in-text citation, and claim.
- Prefer accessible, grayscale-robust encodings and do not rely only on color.
- Do not prohibit multi-panel figures categorically; use them when panels form one comparison and remain legible. Preserve each panel's labeling and source.
- Do not mandate a fixed DPI as official. Use sufficient effective resolution for the final print size and prefer vector formats for diagrams.
- Use native Word tables for ordinary tabular data; do not insert spreadsheet screenshots.
- Treat three-line tables as a professional default, not an official CUMCM mandate.

## Ethics and reproducibility

Address privacy, fairness, environmental impact, safety, or policy tradeoffs when they are materially relevant to the problem. Do not add a generic ethics paragraph solely for appearance.

Record:

- data provenance and permitted use;
- model and code versions;
- randomness, seeds, and environment details;
- rejected assumptions or failed approaches when they affect interpretation;
- human decisions made after AI-generated suggestions;
- actual AI use in the form required by the applicable rules.

Pass S6 to `$paper-review` only after the latest content and document artifacts share the same hashes and the final validation report contains no unresolved blocking failures.
