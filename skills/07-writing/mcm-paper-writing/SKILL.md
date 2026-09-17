---
name: mcm-paper-writing
title: Mathematical Modeling Paper Writing (Markdown-Only)
category: writing
stage: S6
description: "纯 Markdown 论文写作流水线：页码预算分配、Word 原生 OMML 数学公式规范、三线表排版、匿名合规审计与 Word 原生生成器"
inputs: ["figure_manifest.json", "framework_assessment.json", "model_spec.json", "validation_report.md", "paper_macros.json"]
outputs: ["paper_page_plan.json", "paper_macros.json", "pre_draft_numeric_evidence.json", "PAPER_FINAL.md", "paper.docx", "writing_metrics.json"]
dependencies: ["scipilot-figure-cumcm", "cumcm-academic-flowchart", "model-validation"]
---

# Mathematical Modeling Paper Writing (Markdown-Only Pipeline)

Operates during the **PAPER_DRAFTING** state in the V3 HITL production workflow (orchestrator_v3.py). Produce the paper exclusively in standard Markdown (`paper.md`) from verified upstream artifacts (canonical_model_spec.json, canonical result bundle, validation report, figure manifests); do not silently recompute models, invent data, fabricate citations, or promise awards.

```text
MARKDOWN_ONLY = YES
PRIMARY_PAPER_FORMAT = .md
LATEX_WRITING_SUPPORTED = NO
```


## Page architecture and Word-native formula contract

Read [page planning](references/page-planning.md) and [formula compatibility](references/equation-workflow.md) before drafting or review. These contracts supersede legacy length quotas and manual formula conversion guidance, while all scientific, numerical, validation, citation and anonymity gates remain unchanged.

PRE_DRAFT_PAGE_PLAN = REQUIRED; PRE_DRAFT_VISUAL_PLAN = REQUIRED. Complete `paper_page_plan.json` and PAPER_ARCHITECTURE before prose; validate with the writing skill's `scripts/page_plan_validator.py`. Default CUMCM target 25, soft range 23–27, configurable official hard limit 30. Check coverage/balance/drift at 25%, 50%, 80%; first rendered review checks missing content, never missing pages alone.

Review PAGE_PLANNING_QUALITY, SECTION_BALANCE, INFORMATION_DENSITY, CONTENT_GAP, PAGE_PADDING and formula compatibility separately. Efficient completeness below target is acceptable. FORMULA_AS_IMAGE is CRITICAL unless a documented special graphical exception applies. Static lint does not establish OMML or Word editability.

Canonical final text: `PAPER_FINAL.md`; retain `paper.md` as the existing workflow alias with matching content hashes. Standard Pandoc-compatible LaTeX remains in Markdown; native DOCX equation target is OMML. No raw OMML in Markdown and no manual MathType requirement.

## Codex Execution Contract

1. **Deliverable Format**: Canonical paper format is Markdown: working `paper.md`, final `PAPER_FINAL.md`. LaTeX document generation (`.tex`, `.cls`, `.sty`, `\documentclass`) and compiler toolchains (`xelatex`, `pdflatex`, `latexmk`) are permanently deprecated and removed.
2. **Language**: Default CUMCM narrative to `zh-CN` and MCM/ICM narrative to `en-US`. Preserve official wording, quotations, equations, variable names, citation keys, schema keys, paths, and code identifiers.
3. **Inspect First**: Inspect the problem, `paper_plan.json`, `pipeline_manifest.json`, figures, tables, math formulas, references, code, and supporting materials before writing.
4. **Traceability**: Keep every numerical claim traceable to `paper_macros.json`; run `scripts/paper_number_validator.py` before and after drafting.
5. **Markdown Math Notation**:
   - Math formulas MUST be written using Markdown-compatible math notation: inline `$...$` and display block `$$ ... $$`.
   - Math notation (e.g. `\alpha`, `\beta`, `\frac`, `\sum`, `\mathbf`, `\sqrt`) is fully supported within math delimiters.
   - LaTeX document-level commands (`\documentclass`, `\begin{document}`, `\section`) are strictly forbidden.
6. **Figures and Tables**:
   - Figures: `![图注](figures/xxx.png)` followed by standardized caption: `**图 1  图题说明。**`
   - Tables: Native Markdown tables `| 列1 | 列2 |` followed by standardized caption: `**表 1  表题说明。**`
   - Use purposeful figure/table interpretation with flexible length; follow Visual-First Competition Writing below.
7. **References**:
   - Formatted in pure Markdown under `## 参考文献` adhering to GB/T 7714 standard (e.g., `[1] 作者. 题名[J]. 刊名, 2024, 1(1): 1-10.`).
   - Bidirectional consistency: every `[n]` in prose must map to a valid entry in the reference list.
8. **Table of Contents Strictly Forbidden**:
   - CUMCM rules strictly forbid a Table of Contents (TOC). NEVER generate `# 目录` or `[TOC]`.

## Canonical Writing Workspace Structure

```text
paper/
├── paper.md                 # 唯一权威论文主体 (Canonical Paper Artifact)
├── paper_plan.json          # 论文深度与篇幅规划
├── figures/                 # 高清插图 (PNG / SVG / PDF)
├── tables/                  # 数据表
├── references.md            # 参考文献备用源
├── appendix.md              # 附录代码与辅助推导
└── writing_metrics.json     # 深度度量产物
```

## Markdown Heading Standard

Strictly use Markdown hierarchy:
- `# 论文题目` (Title)
- `## 摘要` (Abstract)
- `## 一、问题重述` (Section 1)
- `## 二、问题分析` (Section 2)
- `## 三、模型假设与符号说明` (Section 3)
- `## 四、模型的建立与求解` (Section 4 - Core Subproblems Q1-Q5)
- `## 五、模型检验与灵敏度分析` (Section 5)
- `## 六、模型评价与改进` (Section 6)
- `## 参考文献` (References)
- `## 附录` (Appendix)

## Deterministic Scripts

- `scripts/markdown_paper_validator.py`: Audit Markdown paper structure, heading hierarchy, unclosed math blocks, broken images, table formatting, reference consistency, and anonymity.
- `scripts/paper_number_validator.py`: Validate paper numbers against `paper_macros.json`.

## Non-negotiable CUMCM Quality Gates

- Strictly NO table of contents (`# 目录` or `[TOC]`).
- Abstract strictly focused on problem, method, quantitative results, and conclusions.
- Core subproblems should address RESULT / MECHANISM / EVIDENCE as semantic functions matched to problem requirements; ADVANTAGE is applicable only when supported by comparison evidence or structural benefit (SIMPLE_MODEL_CAN_BE_THE_FINAL_MODEL = TRUE). Limitations are conditional, never a mandatory result layer.
- All participant/school identity information excluded from text, code comments, metadata, and image filenames.
- Full runnable code preserved in the appendix; never replace actual code with pseudocode.
- Disclose actual AI use truthfully when AI was used.


## Competition Writing Policy — evidence-bound confidence

These narrative rules take precedence over older writing-style guidance; scientific scope, numerical truth, citations, anonymity, AI-use disclosure and upstream release decisions remain binding.

```text
COMPETITION_PAPER_STYLE = RESULT_ORIENTED
SCIENTIFIC_SCOPE = PRESERVED
AUDIT_STYLE_IN_MAIN_TEXT = FORBIDDEN
LIMITATION = CONDITIONAL
POSITIVE_SCOPE > NEGATIVE_DISCLAIMER
NO_AUDIT_DUMP
NO_IMPLEMENTATION_DUMP
NO_REPETITIVE_CAVEATS
```

### Problem-Driven Narrative

```text
PROBLEM_DRIVEN_NARRATIVE > MODEL_DRIVEN_NARRATIVE
```

The narrative logic follows: what the problem asks → why the difficulty → why this method → what the answer is → what it means → why it is credible. Do not organize sections as model-A introduction → model-B introduction → algorithm-C → parameters → answer buried at the end. For multi-question problems, make QUESTION → METHOD → ANSWER → KEY_EVIDENCE visible early (these are information requirements, not four fixed headings). Avoid generating mechanical four-paragraph blocks to satisfy this structure.

### Internal Workflow Language Isolation

The following terms belong to internal workflow metadata and must not appear in main text unless they are themselves the scientific content: Gate A/B/C/D, PASS/FAIL/REVISE, hash/SHA256, artifact, canonical bundle, manifest, freeze, pipeline state, skill routing, implementation contract, revision token, upstream/downstream, validation verdict. Replace them with direct scientific evidence. For example, do not write "the model passed R2 validation"; write "under ±5% parameter perturbation the objective changed by less than 1.7%".

```text
WRITE_EVIDENCE_NOT_WORKFLOW = TRUE
```

Lead the narrative with ANSWER → MODEL → QUANTITATIVE RESULT → VISUAL EVIDENCE → VALIDATION → INTERPRETATION. Within each question, explain the difficulty, how the chosen model addresses it, the answer, and the evidence. State the answer before extended derivation or disclaimers; do not hide it behind two method paragraphs.

Use **RESULT / MECHANISM / EVIDENCE / ADVANTAGE** as four functions, not four mandatory headings or sentence quotas: give the answer (including analytical answers), explain its mathematical/physical cause, cite the strongest actual evidence, and identify the supported benefit when available. ADVANTAGE may be N/A with reason—simple models that suffice are valid final models (SIMPLE_MODEL_CAN_BE_THE_FINAL_MODEL = TRUE). Do not fabricate a baseline, improvement, stability, efficiency, novelty or generalizability. If comparative evidence is absent or shows no meaningful difference, describe a demonstrated structural benefit or omit the advantage claim entirely.

### Strength-First Narrative and information hierarchy

Before completion, record internal `PAPER_STRENGTHS`: select the strongest 3–5 supported advantages when available; never invent extra strengths to fill a count. Bind each to an artifact and its claim scope, with locations in abstract, problem analysis, core sections, model evaluation and conclusion. Select 3–5 core results when available as recurring numerical/visual anchors. Each question should make its answer, effectiveness, strongest evidence, and any supported comparison or demonstrated benefit easy to find when applicable.

- Level A: final answers, strongest model contribution, key formula, comparison and robustness evidence. Make them prominent in body and visuals, summarize their meaning in abstract and conclusion (do not dump formulas into the abstract).
- Level B: parameter solving, algorithm logic, supporting comparisons and secondary sensitivity belong in normal prose.
- Level C: optimizer details, failed routes, exhaustive boundary tests, numerical diagnostics, full parameters and logs belong in appendices, validation evidence or supporting materials. Keep all evidence; summarize any defect that materially changes the answer in the main text.

Abstract: problem and core difficulty → main models → each question's final answer → strongest validation/comparison → method value. It should have the highest density of supported strengths, with at most one scope-qualification sentence. No workflow logs, failure inventories or repeated limitations. Conclusion: answer the task again, summarize core results, highlight method value; do not repeat the limitations section.

### One-Disclosure Rule and Positive Scope Rule

Explain a given systemic limitation in detail once, normally in **模型评价与改进**, organized as 模型优点 / 模型不足 / 改进方向. Strengths must cite actual quantities or structural evidence; limitations are concise, non-repetitive, usually 1–3 paragraphs. Preserve essential assumptions where the model is defined.

At a result, add one short qualification only when omission would cause a materially false or exaggerated reading. Prefer “在本文材料与标定条件下，多束修正对厚度结果影响很小” to lists of stronger claims that were not proved. Elsewhere use a short scope phrase or cross-reference. Never restore deleted duplicate caveats merely to satisfy a layer, sentence count or limitation frequency. Preserve exact upstream limitation/restriction records in review metadata and evidence; exact metadata propagation does not require verbatim repetition in prose.

Do not hide failed models, adverse comparisons, structural residuals or conditionality essential to the answer. For mixed holdout results retain unfavorable blocks and restrict advantage to the supported blocks. Compression changes presentation, not evidence or release verdicts.

### Content-Driven Natural Writing

```text
CONTENT_DETERMINES_STRUCTURE = TRUE
PARAGRAPH_LENGTH_QUOTA = NONE
SENTENCE_VARIATION_QUOTA = NONE
TRANSITION_WORD_QUOTA = NONE
SYMMETRIC_SECTION_LENGTH = NOT_REQUIRED
HUMAN_LIKE_RANDOMIZATION = FORBIDDEN
```

Paragraph and section length are determined by content, not templates. A key conclusion may be 1–2 sentences; an important derivation may span several paragraphs; a simple sub-question may be noticeably shorter. Do not force uniform paragraph/section lengths or apply a fixed "principle—model—solution—strengths—weaknesses" template to every model.

Do not add mechanical transition words (首先, 其次, 此外, 同时, 值得注意的是, 综上所述) unless the semantics require a transition. Prefer direct factual statements. Never randomize terminology, sentence structure, or word choice for "human-likeness". Professional writing is content-driven, specific, and evidence-bound.

```text
NATURAL_WRITING = CONTENT_DRIVEN + SPECIFIC + EVIDENCE_BOUND
```

### Visual-First Competition Writing

Before drafting, during PRE_DRAFT_VISUAL_PLAN, record `NEEDS_FRAMEWORK_FIGURE = YES/NO` with a reason. More than two stages or submodels, multiple sources, multi-step optimization or dependencies between questions normally imply YES. If YES, create an overall modeling framework (or equivalent visual structure), preferably immediately after problem analysis, via `$cumcm-academic-flowchart`. A prose algorithm alone is not an equivalent overview. If NO, record why a simple structure needs no diagram.

Actively consider visuals for data/features, model and parameter relationships, optimization, comparisons, sensitivity, robustness, prediction errors and scenarios. Route quantitative plots to `$scipilot-figure-cumcm`. Consider a framework, data plot, core result, comparison and relevant robustness visual; 6–10 purposeful major figures and 4–8 core tables can aid a complex paper, but no absolute figure-count gate or filler figures. Every figure needs a narrative purpose and verified source.

Interpret the clearest trend, supported conclusion and evidenced advantage first. Figure/table interpretation length is determined by information density, importance of the conclusion, and whether mechanism explanation is needed. A simple result table may need only one sentence; a core figure may warrant multiple sentences or paragraphs. Never add filler prose. Explain error sources locally only when they affect the conclusion.

### Task-matched validation presentation

Select sensitivity/robustness evidence appropriate to the question, model and available data: parameter perturbation, Bootstrap/resampling, holdout, cross-validation, scenarios, ablation, Monte Carlo, Sobol, boundary tests or another justified method. Missing Sobol or Monte Carlo is never itself failure. Preserve applicable upstream validation obligations and their verdicts; do not invent new experiments or substitute style checks for science.

### Diagnostics and final self-check

Read [competition diagnostics](references/competition-diagnostics.md) for semantic checks. Write `writing_metrics.json` using the [metrics schema](references/writing_metrics.schema.json); unknown/unreviewed values are null, not zero or PASS. Metrics are internal quality diagnostics, not official competition rules or targets to game.

Answer internally: Q1 does the abstract state every question's model and answer? Q2 can core results be found in 30–60 seconds? Q3 are supported strengths obvious? Q4 is the required framework present (N/A only with a justified NO assessment)? Q5 are there long negative disclaimers? Q6 are limitations repeated? Q7 is audit detail misplaced? Q8 do visuals carry sufficient information? Q1–Q4 NO, Q5–Q7 YES, or Q8 NO requires narrative REVISION, not a scientific failure verdict. Prefer confident, specific “结果表明 / 由图可见 / 与基准相比 / 因此采用”; confidence must stop at the evidence boundary.

## Handoff

On success, produce `PAPER_FINAL.md` from verified `paper.md` with matching SHA256; record the final path as an alias and retain `paper.md` and its SHA256 in `pipeline_manifest.json` and hand off to `$paper-review` for Markdown quality and scientific consistency audit.

## Production V4 integration

WRITING_CONTRACT = WRITING_V3 for RELEASE_V4 runs. production/skill_routing_manifest.json is the routing/contract authority. S6-PRE is mandatory and records page architecture plus approved numeric evidence before S6 begins. Use orchestrator_v3.py skill-event for receipts, not direct workflow-state/manifest writes. Old paper_planner/measure/rebalancer helpers are historical/advisory and cannot impose length or limitation quotas. Word-native export is BLOCKED until actual closure evidence exists; PDF may proceed independently. No legacy S6 JSON paper or legacy Word renderer is a canonical source.
