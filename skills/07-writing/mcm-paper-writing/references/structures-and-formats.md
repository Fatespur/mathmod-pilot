# Competition Structures and Problem-Type Adaptation

## Contents

- Contest-mode isolation
- CUMCM structure
- CUMCM problem-type adaptation
- MCM/ICM structure
- Writing controls

## Contest-mode isolation

Select one contest before drafting.

| Mode | Language | Front matter | Default references | Rule source |
|---|---|---|---|---|
| CUMCM | Chinese | official CUMCM pages; no TOC | sequential numbering, GB/T 7714 as a recommended default | current CUMCM files or bundled 2026 baseline |
| MCM/ICM | English | current COMAP Summary Sheet and any current required reports | current COMAP requirements and a consistent English citation style | current COMAP files actually read |

Never transfer CUMCM commitment/numbering pages, Chinese-only legends, or GB/T conventions into MCM/ICM. Never transfer Team Control Number headers, English Summary Sheet furniture, or COMAP-specific reports into CUMCM.

## CUMCM structure

The official page order and limits are defined in [cumcm-rules-2026.md](cumcm-rules-2026.md). Use the following content structure as `RECOMMENDED-DEFAULT`, adapting it to the problem instead of forcing empty sections:

1. 摘要：标题、连续摘要正文、关键词；严格一页，不生成英文摘要。
2. 一、问题重述。
3. 二、问题分析：按子问题解释数学本质、候选方法及选择理由。
4. 三、模型假设：只保留必要、可解释、可验证的假设。
5. 四、符号说明：定义实际使用的符号和单位。
6. 五、模型建立与求解：按子问题组织数据、模型、算法、结果与局部验证。
7. 六、模型检验：汇总全局验证、敏感性、不确定性或稳健性证据。
8. 七、模型评价与改进：优点须有证据，缺点对应可执行改进。
9. 结论：仅在题目和篇幅需要时设置；不得重复摘要或引入新结果。
10. 参考文献。
11. 附录：支撑材料清单、完整程序、交互命令和必要补充说明。

Do not create a table of contents. Do not mechanically require a five-subsection template for every model; organize around the evidence and the problem's actual dependencies.

### Abstract content gate

Cover each subproblem's object, preprocessing, core model, algorithm, key parameter or result, validation evidence, and robustness conclusion where applicable. Replace vague claims such as “结果良好” with named methods and verified metrics. When it overflows one page, shorten background and repetition before altering readable typography.

### Appendix gate

Include the supporting-material file list and every complete program used for preprocessing, training, solving, output, and plotting. Include Excel/SPSS interaction commands when applicable. Never write “代码过长，略” or replace used code with pseudocode.

## CUMCM problem-type adaptation

The labels A/B/C do not guarantee a fixed method family. Classify the actual task and adapt the emphasis.

### Physical or engineering task

- Derive the model from physical principles and state dimensions, directions, conservation laws, and hard constraints.
- Report numerical method, step size, convergence criteria, initialization, and physical plausibility checks.
- Use trajectory, phase, field, spectrum, or constraint-validation figures only when they support a claim.

### Social, economic, management, evaluation, or optimization task

- Explain why the selected method fits the decision structure and why plausible alternatives were rejected.
- Report objective, constraints, weight/parameter provenance, algorithm convergence, and robustness.
- For econometric claims, include the diagnostics appropriate to the data rather than a fixed checklist.

### Data-driven prediction or classification task

- Report data quality, leakage prevention, train/validation/test splits, feature engineering, tuning, and uncertainty.
- Match metrics to imbalance and decision cost. Do not mandate SMOTE or a specific model unless justified by the data.
- Show distributions, calibration/error, important features, and predicted-versus-observed evidence as appropriate.

### Evidence-based length, Section Depth Contracts, and figure use

Paper generation is governed by `paper_plan.json` (derived from empirical priors in `award_writing_profile.json` and problem-adaptive subproblem importance scores).
- **Prohibition of Illegal Table of Contents**: CUMCM strictly forbids a table of contents. Never emit `\tableofcontents` or generate front-matter TOC pages.
- **Section Depth Contracts**:
  - Model formulation must include physical/geometric motivation and step-by-step intermediate equation derivations (never lone final formulas).
  - Model results cover RESULT / MECHANISM / EVIDENCE / ADVANTAGE; limitations are conditional.
  - Visuals must adhere to visual budget: maximum single figure page height ratio $\le 0.40$, with purposeful interpretation of flexible length, never a sentence quota.
- Respect official page boundaries (configured official_page_limit (CUMCM default 30; counting scope from current rules); abstract strictly 1 page) and allocate space according to subproblem importance scores.

## MCM/ICM structure

Read the current COMAP instructions before use; do not assume a previous year's page limit or AI-report rule is current. A common evidence-driven structure is:

1. Summary Sheet.
2. Introduction and problem restatement.
3. Assumptions and notation.
4. Model development and solution by subproblem.
5. Validation, sensitivity, uncertainty, or robustness.
6. Strengths, limitations, and improvements.
7. Conclusion and any requested communication artifact.
8. References and permitted appendices/reports.

Only include a table of contents, AI report, memo, letter, or other special artifact when the current official problem/rules call for it.

## Writing controls

- Every claim has evidence in `section_evidence_map.json`.
- Every result number matches `paper_macros.json` or an explicit structural/allowlist rule.
- Every figure and table is introduced and interpreted in the text.
- Every important numbered equation has a meaningful label and a valid reference mapping.
- Every assumption has a rationale and impact statement.
- Notation is consistent and defined at first use.
- Conclusions do not add results absent from the body.
- Citations are bidirectionally complete and real.
