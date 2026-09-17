---
name: winning-paper-analysis
title: Historical Winning Paper Structure & Benchmark Analysis
category: quality-assurance
stage: Benchmark
description: "国奖优秀论文特征库对标：摘要黄金结构、正文篇幅密度分布、图表出现频次与放置策略、高分论述表达范式对比"
inputs: ["problem_structure.json", "draft_paper.md"]
outputs: ["benchmark_alignment_report.json", "structure_optimization_suggestions.md"]
dependencies: ["problem-analyzer"]
---

## Codex execution contract

- **Language:** Match the requested deliverable language. Default CUMCM guidance to `zh-CN` and MCM/ICM guidance to `en-US`; preserve quotations, official terms, schema keys, paths, and paper-specific terminology.
- **Inspect first:** Identify contest, year scope, problem type, active section, source corpus, and requested comparison before drawing conclusions.
- **Progressive disclosure:** Keep detailed Chinese paper observations in `references/`; load only the contest and section guidance needed for the request.
- **Evidence:** Label every recommendation as `official`, `observed`, `heuristic`, or `inference`; include source scope and uncertainty.
- **Privacy:** Do not upload supplied papers or unpublished drafts without explicit authorization.
- **Handoff:** Use `pipeline_manifest.json` when participating in S6/S7; on first use read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json).
- **Routing:** Supply guidance to `$mcm-paper-writing` or `$paper-review`; never overwrite verified model results.
- **Completion:** Finish only when advice is contest-specific, evidence-bound, and free of award guarantees or mechanical quotas.

# Winning Paper Analysis — 获奖论文写作对标

为 S6/S7 提供章节结构、表达、篇幅和评审风险的证据化参考。不直接撰写论文，也不把经验比例当作当前评审规则或获奖保证。

## 核心流程

1. 确认竞赛、题型、章节和用户需要的对标维度。
2. 区分正式规则、样本观察、经验建议和推断；标注适用年份与来源。
3. 返回章节目的、结构、篇幅区间、证据要求、常见错误和自检清单。
4. 将建议与当前论文和真实产物比对，不强制套用固定图表数或模型数。
5. 发现规则可能变化时，要求核对当前官方文件。

## 按需读取

- CUMCM 国一/国二差距、章节级写法和篇幅：读 [references/cumcm-section-guidance.md](references/cumcm-section-guidance.md)。
- 写作风格、评阅、协作、陷阱和论文库：读 [references/writing-review-and-collaboration.md](references/writing-review-and-collaboration.md)。
- MCM/ICM O奖要素、5+3 摘要、伦理、假设和清单：读 [references/mcm-award-guidance.md](references/mcm-award-guidance.md)。

## 输出格式

- `guidance_type`: official / observed / heuristic / inference
- `contest`、`year_scope`、`section`
- `purpose`、`recommended_structure`、`evidence_required`
- `length_range`、`common_mistakes`、`checklist`
- `source_or_basis`、`uncertainties`

## 完成门禁

- 不宣称未经证实的获奖率、评分权重或“必须”规则。
- 不鼓励为页数、公式数或图表数机械填充内容。
- 所有写作建议必须服务于可验证的模型论证和清晰表达。
