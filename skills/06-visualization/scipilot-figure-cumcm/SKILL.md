---
name: scipilot-figure-cumcm
title: Competition Scientific Data Visualization Planner
category: visualization
stage: S5A
description: "数模竞赛论证图表规划器：将核心结论与证据映射为高质量图型，严禁无效凑数图，控制篇幅信息增益与审阅抓手"
inputs: ["validation_evidence.json", "results/", "paper_claim_register.json"]
outputs: ["figure_plan.json", "figure_manifest.json", "figures/final/*.png", "figures/final/*.svg"]
dependencies: ["model-validation"]
---

## Codex execution contract

- **Language:** Match the requested deliverable language. Default CUMCM labels and captions to `zh-CN` and MCM/ICM to `en-US`; preserve symbols, units, column names, schema keys, paths, and code identifiers.
- **Inspect first:** Validate upstream results, data dictionaries, validation evidence, and the paper claim before selecting a chart.
- **Progressive disclosure:** Keep detailed Chinese chart-routing knowledge in `references/`; load only the route required by the active conclusion and data type.
- **Run, render, inspect:** Execute plotting code, render previews, inspect them visually, and never report a candidate or unrendered figure as final.
- **Evidence and privacy:** Trace every mark to a data snapshot; use local backends unless external use is explicitly authorized.
- **Handoff:** Use `pipeline_manifest.json`; on first use read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json). Record figure purpose, source data, code, exports, QA, warnings, and provenance.
- **Routing:** Send method diagrams to `$cumcm-academic-flowchart`, MATLAB-only work to `$matlab-figure`, and chart-selection analysis to `$scipilot-figure-skill`.
- **Completion:** Mark a figure final only after semantic, numerical, typography, crop, color, and grayscale checks pass.

# SciPilot Figure CUMCM — 竞赛数据可视化调度

负责 S5 数据图表：根据论证目标和数据结构选择、生成并筛选论文图。流程图交给 `$cumcm-academic-flowchart`，MATLAB 专属图交给 `$matlab-figure`，投稿级科研图可交给 `$nature-figure`。

## 核心流程

1. 读取 S1–S4 的问题结构、数据字典、结果和验证结论。
2. 剖析数据并拦截错误图型；仅在确有通用图型能力缺口时，按生产 routing manifest 使用 `$scipilot-figure-skill`，不重复承担同一图任务。
3. 为每条论文结论建立“结论—证据—图型”映射。
4. 生成必要图和少量有明确用途的候选图；不得为凑数量生成所有可用图型。
5. 实际渲染并检查字体、裁切、比例、色盲、灰度和数值一致性。
6. 保存源代码、数据快照、PNG/SVG/PDF 和 figure manifest。

## 按需读取

- 竞赛候选图机制与问题类型路由：读 [references/candidates-and-chart-routing.md](references/candidates-and-chart-routing.md)。
- CUMCM/MCM 配置、配色、高级图和数量建议：读 [references/styling-and-advanced-charts.md](references/styling-and-advanced-charts.md)。
- 硬规则、地理/交互/网络/MATLAB/系统动力学路由：读 [references/backends-and-rules.md](references/backends-and-rules.md)。

## 必需产物

- `figure_plan.json`
- `figures/final/`
- `figures/candidates/`（仅有明确替代方案时）
- `figure_manifest.json`
- 每图对应的源代码与数据快照

## 完成门禁

- 每张最终图服务于一个明确结论，正文能够引用和解释。
- 坐标、单位、误差、样本量和统计口径完整。
- 禁用误导性双 Y 轴、彩虹色图、无基线截断和不当连线。
- 候选图不以数量为目标；优先信息增益和论文篇幅效率。

## Production V4 integration

In RELEASE_V4, this is the primary data/result figure owner. scipilot-figure-skill is an allowed alternative only for a documented generic-chart capability need or an explicitly requested generic chart route, with the same evidence/export/QA contract. Assign one owner per figure ID. Frameworks belong to cumcm-academic-flowchart; MATLAB-native requirements to matlab-figure. Nature-style journal assembly is not a CUMCM default. Do not invoke another data-figure workflow merely for coverage.
