---
name: paper-review
title: End-to-End Paper Quality & Consistency Audit
category: quality-assurance
stage: S7
description: "论文终稿全方位审查：数值宏前后溯源一致性、公式符号未定义扫描、假设与结论契合度审计、匿名合规检查与提交就绪裁决"
inputs: ["PAPER_FINAL.md", "render_manifest.json", "paper_macros.json", "validation_report.md"]
outputs: ["paper_review_report.json", "anonymity_report.json", "consistency_audit_receipt.json"]
dependencies: ["mcm-paper-writing", "reference-manager"]
---

## Page architecture and Word-native formula contract

Read [page planning](../mcm-paper-writing/references/page-planning.md) and [formula compatibility](../mcm-paper-writing/references/equation-workflow.md) before drafting or review. These contracts supersede legacy length quotas and manual formula conversion guidance, while all scientific, numerical, validation, citation and anonymity gates remain unchanged.

PRE_DRAFT_PAGE_PLAN = REQUIRED; PRE_DRAFT_VISUAL_PLAN = REQUIRED. Complete `paper_page_plan.json` and PAPER_ARCHITECTURE before prose; validate with the writing skill's `scripts/page_plan_validator.py`. Default CUMCM target 25, soft range 23–27, configurable official hard limit 30. Check coverage/balance/drift at 25%, 50%, 80%; first rendered review checks missing content, never missing pages alone.

Review PAGE_PLANNING_QUALITY, SECTION_BALANCE, INFORMATION_DENSITY, CONTENT_GAP, PAGE_PADDING and formula compatibility separately. Efficient completeness below target is acceptable. FORMULA_AS_IMAGE is CRITICAL unless a documented special graphical exception applies. Static lint does not establish OMML or Word editability.

Canonical final text: `PAPER_FINAL.md`; retain `paper.md` as the existing workflow alias with matching content hashes. Standard Pandoc-compatible LaTeX remains in Markdown; native DOCX equation target is OMML. No raw OMML in Markdown and no manual MathType requirement.

## Codex Execution Contract

- **Input Artifact**: Strictly audit `paper.md`. LaTeX documents (`paper.tex`), compiler outputs (`xelatex`), are deprecated; derived PDF rendering is used for page/content review.
- **Language**: Review in the paper’s contest language: default CUMCM to `zh-CN` and MCM/ICM to `en-US`. Preserve quotations, equations, variable names, citation keys, schema keys, paths, and code identifiers.
- **Inspect First**: Validate `paper.md` SHA256, S1–S6 manifests, macros, citations, figures, tables, and math equations before reviewing.
- **Evidence**: Distinguish official violations from evidence defects, observed winning-paper patterns, and stylistic suggestions. Do not turn page, figure, model, or reference counts into unsupported gates.
- **Repair Scope**: Edit only when the user requests optimization; preserve the original and never change model data or conclusions to make the review pass.
- **Routing**: Return numerical, model, validation, figure, citation, or analysis defects to the skill that first produced them.
- **Completion**: Mark S7 passed only when all applicable critical findings are resolved and `paper.md` is fully verified.


## 与 Skill 组的关系

| Skill | 阶段 | 关系 |
|-------|:----:|------|
| mcm-paper-writing | S6 | 上游：审阅 mcm-paper-writing 产出的 paper.md |
| scipilot-figure-cumcm | S5 | 路由回：图表问题路由回 S5 重新生成 |
| reference-manager | 辅助 | 路由回：参考文献格式问题 |
| model-validation | S4 | 路由回：内容缺失/经济计量诊断问题 |
| mle-solver | S3 | 路由回：模型问题/验证缺失 |
| problem-analyzer | S1 | 路由回：问题类型不匹配 |
| data-processing | S2 | 路由回：经济建模数据问题 |
| winning-paper-analysis | 辅助 | 条件支持：首次完整链冻结后且授权 EXTERNAL_AUDIT 才加载获奖论文 |

**职责边界**：本 skill 是 Pipeline 的 S7 质量守门员，不负责论文生成（那是 mcm-paper-writing 的职责），只负责审阅和路由修复。

# Paper-Review：论文终审与质量优化（v5 Markdown-Only）

你是使用官方规则、可追溯产物和优秀论文观察进行对标的**论文审阅专家**。核心能力是审阅 `mcm-paper-writing` 产出的 `paper.md`，发现排版、内容、证据、公式和语言问题，并在授权范围内修复或路由，而不是保证获奖。

## 角色定位

你是流水线的**质量守门员**（S7 阶段），在论文写作完成后执行：
- 审阅 `paper.md`，发现 **10 类问题**
- 对每类问题给出优化建议
- 如果问题可自动修复，直接修复
- 如果问题需要上游 Skill 处理，标记问题并路由回对应 Skill
- 输出最终优化后的 `paper.md` + 审阅报告

---

## 审阅维度（10 类）

### 维度 1：Markdown 结构与排版规范

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 标题层级 | 标准 `#` -> `##` -> `###`，无跳级，无重复大标题 | HIGH |
| 目录限制 | 严禁包含任何目录标题（`# 目录`）或 `[TOC]` 标记 | CRITICAL |
| 数学公式完整性 | 行内 `$..$` 与行间 `$$..$$` 正确闭合，无损坏数学块 | CRITICAL |
| 表格语法与表注 | Markdown 表格具备完整表头与分隔线，含统一表注 | HIGH |
| 插图引用与存在性 | `![图注](figures/xxx.png)` 本地文件真实存在 | CRITICAL |
| 插图深度解读 | 核心趋势、结论与有证据的优势有有效解读；句数为弹性建议，不设配额 | HIGH |
| 空章节与信息密度 | 无实质内容空洞的章节（< 20 字），无大段放图少文字的视觉膨胀 | CRITICAL |
| 参考文献格式 | GB/T 7714 纯文本引用，正文与列表双向严格对应 | CRITICAL |

### 维度 2：图表质量

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 图中文字可读 | 字号清晰，无模糊/锯齿 | CRITICAL |
| 图例完整性 | 每张图有图注；误差类型与 n 仅在适用时说明 | CRITICAL |
| 色盲友好 | 灰度预览可区分 | HIGH |
| 表格格式 | 标准三线表语义，无错位列 | HIGH |
| 图表解读覆盖率 | 核心图表 100% 具备与其功能匹配的实质解释：数据/性能/灵敏度图应尽量定量解释；框架图/流程图/示意图根据任务解释结构或意义，不强制配数值 | CRITICAL |

### 维度 3：语言质量

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| AI 风格表达 | 无"深入探讨""充分证明""显著提升"等空洞表述 | HIGH |
| 证据支撑 | 每个核心经验性/定量推断必须有可追溯证据；解析结论、数学推导、结构性质和定性机理不强制配数值 | CRITICAL |
| 机械句式重复 | 连续多段采用相同句法框架、每段以固定模式开头、每个小问使用同一模板、每个图使用固定"由图可知…说明…表明…"三连句 | MEDIUM |
| 术语一致性 | 同一概念全文使用统一术语与符号；术语一致性优先于词汇多样性，不因避免重复而随意改变稳定术语 | HIGH |

### 维度 4：内容完整性与结果证据链

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 摘要 | 严格交代背景、关键方法、核心量化结果与结论 | CRITICAL |
| 假设 | 每条假设有理由，标注高风险假设 | HIGH |
| 结果证据链 | 每个核心问题应具有与问题性质相匹配的 RESULT / MECHANISM / EVIDENCE 功能；ADVANTAGE 仅在存在比较证据、决策收益或明确结构性收益时适用。上述功能不要求固定标题、固定段落、固定顺序或固定数量（SIMPLE_MODEL_CAN_BE_THE_FINAL_MODEL = TRUE） | HIGH |
| 灵敏度与稳健性 | 方法与题型、模型、数据和上游验证要求匹配；不因缺少 Sobol 或 Monte Carlo 判失败 | HIGH |
| 模型评价 | 包含优缺点客观评价 + 改进方向 | HIGH |
| 参考文献 | 真实来源，无伪造文献 | CRITICAL |

### 维度 5：一致性

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 公式编号 | 连续编号或行内引用无断链 | HIGH |
| 图表编号 | 连续编号，正文中引用的图表编号均真实存在 | HIGH |
| 假设与模型 | 假设在模型中实际使用 | MEDIUM |
| 宏定义绑定 | 数值与 `paper_macros.json` 严格一致 | CRITICAL |

### 维度 6：获奖论文对标

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 结构 | 章节功能完整，与优秀论文结构进行启发式对标 | MEDIUM |
| 表达 | 清晰、具体、证据化；不复制固定套话 | MEDIUM |
| 深度 | 机理推导步骤完整，无直接跨越至最终结果 | HIGH |

### 维度 7：模型验证完整性

```text
VALIDATION_REQUIREMENTS = TASK_MATCHED
```

以下检查仅在相应数学、物理或工程结构适用时触发。不适用项目记为 N/A，不得因为某题不涉及物理守恒、量纲关系或边界机理而降低论文评级。

- 物理/机理模型 → 量纲、物理合理性、边界、守恒等适用检查
- 优化模型 → feasibility、constraint residual、目标值合理性、情景/扰动等
- 统计/计量模型 → diagnostic、uncertainty、residual、inference 等适用检查
- 预测/机器学习模型 → holdout/CV、generalization、error analysis、calibration 等适用检查
- 解析/确定性简单模型 → 已知解、边界情况、数学一致性、必要扰动即可

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 硬断言验证 | 论文中包含基本物理/数学约束的验证结果 | CRITICAL |
| 物理合理性检查 | 论文中包含物理直觉检查结果 | HIGH |
| 模型-现实交叉检查 | 论文中包含量纲一致性、边界行为、守恒律验证 | HIGH |

### 维度 8：问题类型对齐

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 问题类型分类正确性 | 论文中隐含的问题类型与 S1 分类结果一致 | HIGH |
| 方法选择与类型匹配 | 建模方法符合问题类型的最佳实践 | HIGH |
| 检验策略与类型对齐 | 检验方法覆盖该问题类型的所有必做检验 | CRITICAL |

### 维度 9：经济建模完整性

| 检查项 | 标准 | 严重程度 |
|--------|------|---------|
| 数据来源与预处理声明 | 说明数据来源、频率、时间范围、通胀调整方式 | CRITICAL |
| 平稳性检验报告 | 包含 ADF/KPSS 检验结果，非平稳序列是否处理 | CRITICAL |
| 计量诊断报告 | 包含自相关、异方差、多重共线性检验 | CRITICAL |
| 稳健性检验 | 采用足以检验核心结论稳定性的、与当前模型和推断目标匹配的稳健性策略；方法数量由科学需要决定，不设统一最低数量 | CRITICAL |

**条件化说明**：上述经济建模检查仅当模型属于相应计量/时间序列问题且检查在当前模型假设下适用时触发。不得因为题目包含"时间""价格""经济指标"或序列数据就自动要求完整 ADF/KPSS + 异方差 + 共线性组合。稳健性方法数量由科学需要决定，一种强而直接的验证可能优于两种形式化验证（TWO_ROBUSTNESS_METHODS = NOT_UNIVERSAL）。

---

## 维度 10：Competition Narrative Quality

| 检查项 | 标准 | 严重程度 |
|---|---|---|
| 核心答案可见性 | 每问最终答案快速可定位 | CRITICAL |
| 优势突出 | 最强且有证据的3–5项优势充分曝光，不凑数 | HIGH |
| Result-first | 结果先于免责声明，答案不埋在方法后 | HIGH |
| 视觉框架 | 复杂模型有总体框架图或等价视觉结构 | HIGH |
| 图表覆盖 | 关键流程和结果有充分视觉支持，不按数量裁决 | HIGH |
| 防御性重复 | 无重复完整披露或连续否定性自我削弱 | HIGH |
| 局限集中 | 系统局限集中于模型评价与改进 | HIGH |
| 信息层级 | 核心答案、支持信息、复现细节清晰分层 | HIGH |
| 竞赛可读性 | 快速浏览可理解方法、答案和价值 | HIGH |
| 模板对称性 | 各段/各小问不存在无必要的镜像结构或固定套路模板；不因追求结构整齐而牺牲自然阅读 | HIGH |
| 过渡词过密 | 机械过渡词（首先/其次/此外/同时/值得注意的是/综上所述）因语义需要而使用，不是语言连贯的硬性要求 | MEDIUM |
| 审计语言泄露 | 正文不得出现 Gate/PASS/FAIL/hash/artifact/manifest/freeze/pipeline/validation verdict 等内部治理词汇（除非本身是科学内容） | HIGH |
| 模型展示炫耀 | 模型介绍篇幅与回答赛题直接相关，不花大量篇幅介绍模型名称、算法历史或复杂模块而与解题无直接关系 | HIGH |

按下文诊断执行 OVER_DEFENSIVE_WRITING、UNDERSELLING 和 FIGURE_NARRATIVE_INSUFFICIENT 以及新增的 TEMPLATE_SYMMETRY、TRANSITION_OVERUSE、AUDIT_LANGUAGE_LEAKAGE、MODEL_SHOWCASING；不得奖励 limitation 数量。只读 dry-run 输出发现与路由，不修改论文，也不改写上游科学裁决。


## Competition Writing Policy — evidence-bound confidence

Review these as authoring criteria. In review-only mode, report missing artifacts and route their creation to the named owner; do not generate or rewrite paper assets. The writing self-check below is evaluated against the submitted draft.

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

Lead the narrative with ANSWER → MODEL → QUANTITATIVE RESULT → VISUAL EVIDENCE → VALIDATION → INTERPRETATION. Within each question, explain the difficulty, how the chosen model addresses it, the answer, and the evidence. State the answer before extended derivation or disclaimers; do not hide it behind two method paragraphs.

Use **RESULT / MECHANISM / EVIDENCE / ADVANTAGE** as four functions, not four mandatory headings or sentence quotas: give the answer (including analytical answers), explain its mathematical/physical cause, cite the strongest actual evidence, and identify the supported benefit when available. ADVANTAGE may be N/A with reason—simple models that suffice are valid final models. Do not fabricate a baseline, improvement, stability, efficiency, novelty or generalizability. If comparative evidence is absent or shows no meaningful difference, describe a demonstrated structural benefit or omit the advantage claim entirely.

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

### Visual-First Competition Writing

Before drafting, during PRE_DRAFT_VISUAL_PLAN, record `NEEDS_FRAMEWORK_FIGURE = YES/NO` with a reason. More than two stages or submodels, multiple sources, multi-step optimization or dependencies between questions normally imply YES. If YES, create an overall modeling framework (or equivalent visual structure), preferably immediately after problem analysis, via `$cumcm-academic-flowchart`. A prose algorithm alone is not an equivalent overview. If NO, record why a simple structure needs no diagram.

Actively consider visuals for data/features, model and parameter relationships, optimization, comparisons, sensitivity, robustness, prediction errors and scenarios. Route quantitative plots to `$scipilot-figure-cumcm`. Consider a framework, data plot, core result, comparison and relevant robustness visual; 6–10 purposeful major figures and 4–8 core tables can aid a complex paper, but no absolute figure-count gate or filler figures. Every figure needs a narrative purpose and verified source.

Interpret the clearest trend, supported conclusion and evidenced advantage first. Figure/table interpretation length is determined by information density, importance of the conclusion, and whether mechanism explanation is needed. A simple result table may need only one sentence; a core figure may warrant multiple sentences or paragraphs. Never add filler prose. Explain error sources locally only when they affect the conclusion.

### Task-matched validation presentation

Select sensitivity/robustness evidence appropriate to the question, model and available data: parameter perturbation, Bootstrap/resampling, holdout, cross-validation, scenarios, ablation, Monte Carlo, Sobol, boundary tests or another justified method. Missing Sobol or Monte Carlo is never itself failure. Preserve applicable upstream validation obligations and their verdicts; do not invent new experiments or substitute style checks for science.

### Diagnostics and final self-check

Read [competition diagnostics](references/competition-diagnostics.md) for semantic checks. Write `writing_metrics.json` using the [metrics schema](references/writing_metrics.schema.json); unknown/unreviewed values are null, not zero or PASS. Metrics are internal quality diagnostics (METRICS_ARE_DIAGNOSTIC_NOT_OBJECTIVES), not official competition rules or targets to game.

Answer internally: Q1 does the abstract state every question's model and answer? Q2 can core results be found in 30–60 seconds? Q3 are supported strengths obvious? Q4 is the required framework present (N/A only with a justified NO assessment)? Q5 are there long negative disclaimers? Q6 are limitations repeated? Q7 is audit detail misplaced? Q8 do visuals carry sufficient information? Q1–Q4 NO, Q5–Q7 YES, or Q8 NO requires narrative REVISION, not a scientific failure verdict. Prefer confident, specific “结果表明 / 由图可见 / 与基准相比 / 因此采用”; confidence must stop at the evidence boundary.

## 审核优先级

审阅过程中的优先级顺序如下，语言润色不得反向改变 1–8 的任何要求：

```text
STYLE_REPAIR_MUST_NOT_OVERRIDE_LEVEL_1_TO_8 = TRUE
```

```text
1. 官方规则与匿名要求
2. 科学真实性
3. 数值与证据一致性
4. 是否真正回答赛题
5. 模型—结果—结论逻辑一致
6. 核心答案是否快速可见
7. 图表是否有效传递信息
8. 论证是否清晰
9. 是否存在模板化 / 审计化 / 防御性写作
10. 一般语言润色
```

任何"去 AI 味"修改都不得：改数字、改结论、改模型、改公式意义、改证据范围、改术语、改科学裁决。

## 终审通过准则 (Gate S7 Approval)

1. 所有 CRITICAL 与 HIGH 级别的 Markdown 规范及科学一致性检查项全部 PASS；
2. `paper.md` 具有完整且适用的公式、有效图表、真实参考文献，以及针对各核心问题的完整答案—模型—证据—解释链；RESULT / MECHANISM / EVIDENCE / ADVANTAGE 按适用性覆盖，不要求固定四层结构；
3. 验证器未发现任何身份信息泄露；
4. 论文与 `paper_macros.json` 数值一致性 100%；
5. 最终生成 `paper_review_report.json` 并记录在案。

## Production V4 integration

For RELEASE_V4, review via the repository production manifest and orchestrator_v3.py; scripts/validate_s7_publication_gate.py is a legacy V2.1 adapter only and must not consume a V4 state. Use production.runtime.final_verify for V4 contract checks. Winning-paper benchmarking is conditional on FIRST_SOLUTION_FREEZE and EXTERNAL_AUDIT authorization, never a required pre-freeze activity. Route writing defects to S6-PRE/S6, framework defects to S5B, data figures to S5A, scientific/numeric defects to S4 and its named upstream owner. No paragraph-level limitation or fixed sentence/method quota.
