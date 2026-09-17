---
name: cumcm-academic-flowchart
title: Academic Method Architecture & Flowchart Generator
category: visualization
stage: S5B
description: "竞赛级技术路线图与方法架构图引擎：支持双流布局、泳道分解、循环机理与 draw.io / 原生 SVG / 高清 PNG 矢量生成"
inputs: ["problem_structure.json", "candidate_portfolio.json", "model_spec.json"]
outputs: ["diagram_plan.json", "diagram_primary.drawio", "diagram_primary.svg", "diagram_primary.png", "framework_assessment.json"]
dependencies: ["model-validation", "problem-analyzer"]
---

# CUMCM Academic Flowchart

将赛题、方案、论文、代码与数据字段转为可复现的数学建模方法框架图。默认表达“研究对象/数据 → 方法模块 → 主方法 → 子方法或算法 → 验证 → 结果”的层级、分支和汇聚关系。核心后端完全离线，先构建 ModelingIR，再由同一 Scene Graph 生成 draw.io、SVG 与 PNG；禁止直接把原文拼成图，也禁止把十余个步骤排成一条线冒充框架图。

## Codex execution contract

- **Language:** Match the paper language. Default CUMCM labels to `zh-CN` and MCM/ICM labels to `en-US`; preserve method names, equations, symbols, schema keys, paths, and code identifiers.
- **Inspect first:** Read the relevant problem, solution, code, data fields, and upstream manifests before building diagram semantics.
- **Progressive disclosure:** Keep detailed Chinese modeling and visual rules in `references/`; load only references required by the active diagram and model type.
- **Run, render, inspect:** Use ModelingIR and the deterministic generators, render real PNG/SVG/draw.io outputs, and visually inspect both layouts.
- **Evidence and privacy:** Preserve explicit methods and provenance; do not invent models, results, or external calls in contest mode.
- **Handoff:** Read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json); record IR, layouts, exports, QA, warnings, and provenance in the S5 manifest.
- **Routing:** Return missing semantics to the responsible upstream skill and send ordinary quantitative charts to `$scipilot-figure-cumcm`.
- **Completion:** Finish only when semantic, geometry, visual, format, and dual-layout gates pass.

## 必须执行的工作流

1. 发现用户明确指定的输入；仅在必要范围内读取题面、方案、论文、源码和数据字段。
2. 按“最终输出目标”把每一小问唯一分类为优化、预测、评价、数理统计或机理分析；低置信度必须记录不确定性。
3. 提取目标、数据、假设、变量、目标函数、约束、参数、主方法、子方法、算法、验证、结果与小问依赖；保留论文中明确出现的方法名，并生成带 `framework_role/stage/module/branch/parent_id` 的稳定 `modeling_ir.json`。
4. 先生成 `diagram_plan.json`；围绕主方法组织数据基础、模型定义、求解策略、验证和结果模块。总体图压缩细节但必须保留主/子方法关系，复杂单问自动建议拆图。
5. 至少生成 4 个候选布局。多小问总体图默认使用 `question_architecture`：每一问内部必须呈现主方法、并行子方法、汇聚、验证与结果，而不是“一问一条横线”；其次才考虑层级树、方法框架和问题泳道。只有严格时序且节点很少时才允许线性布局。
6. 选择最高分主布局，并选择不同布局家族且 `layout_diversity_score >= 0.55` 的备用布局；禁止用旋转或轻微位移冒充备用方案。
7. 从同一布局与样式数据生成可编辑 draw.io、原生矢量 SVG、透明 PNG，以及布局 JSON、比较图、manifest 和报告。
8. 执行语义、几何、视觉、格式、双布局五类检查；方法框架必须含主方法、至少三个子方法/组件、至少四层语义深度，以及真实分支与汇聚。无论节点数量多少，只要某一问退化为单链就直接阻断。
9. 主方案须达到 92 分，备用方案须达到 88 分；阻断性错误未消除时不得宣称完成。
10. 实际渲染并检查 PNG；交付前确认 XML、像素尺寸、alpha、节点/边一致性和可重复性。

## 命令行入口

```powershell
python scripts/cumcm_flowchart.py `
  --input solution.md `
  --output figures/modeling_diagrams `
  --diagram auto `
  --layouts 2 `
  --theme journal-rich `
  --transparent `
  --png-dpi 300 `
  --png-long-edge 4800 `
  --seed 42 `
  --contest-mode
```

CLI 必须支持 `--input --output --diagram --question --layouts --primary-layout --alternative-layout --engine --theme --transparent --background --png-dpi --png-long-edge --svg-text-mode --target-width-mm --language --contest-mode --strict --overwrite --config --seed --debug`。Windows 中文路径必须通过 `pathlib` 处理。

## 输出契约

- 主/备：`diagram_primary.*`、`diagram_alternative.*`，各含 `.drawio/.svg/.png/.layout.json`。
- 比较：`diagram_comparison.svg/.png`。
- 数据与报告：`modeling_ir.json`、`diagram_plan.json`、`diagram_manifest.json`、`generation_report.md`、`quality_report.json`。
- SVG 是论文优先格式；PNG 是兼容格式；draw.io 是可编辑源格式。三者必须同时保留。
- PNG 默认透明、300 DPI、长边 4800 px；支持 600 DPI 和 3200/4800/6400 px，不得截图、低清放大或伪造。

## 竞赛模式

启用 `--contest-mode` 后完全离线：只读本地文件，不调用在线服务，不搜索或下载当届赛题答案，不输出身份/学校/赛区/账号，不记录绝对路径，标记推断内容，记录 AI 操作，并提醒人工复核数学逻辑。不得保证获奖或伪造数据、指标、实验结果。

## 团队路由与交接

- 读取 [references/pipeline-contract.md](references/pipeline-contract.md) 和 [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json)，把产物写回 S5 manifest。
- 上游语义缺失或冲突：返回 `$problem-analyzer`、`$data-processing`、`$mle-solver` 或 `$model-validation` 修复。
- 普通数据图表：路由 `$scipilot-figure-cumcm`；MATLAB 专属图：路由 `$matlab-figure`；投稿级复合科研图：可路由 `$nature-figure`。
- 论文写作阶段把 SVG、图题、布局选择依据和质量报告交给 `$mcm-paper-writing`，终稿交给 `$paper-review`。

## 按需读取

- 竞赛全流程与研究来源：[references/cumcm_workflow.md](references/cumcm_workflow.md)、[references/research_sources.md](references/research_sources.md)
- 五类题型与建模语义：[references/question_taxonomy.md](references/question_taxonomy.md)、[references/modeling_semantics.md](references/modeling_semantics.md)
- 图种、布局与选择规则：[references/diagram_taxonomy.md](references/diagram_taxonomy.md)、[references/layout_library.md](references/layout_library.md)、[references/layout_selection_rules.md](references/layout_selection_rules.md)
- 视觉、颜色、透明度和字体：[references/academic_visual_language.md](references/academic_visual_language.md)、[references/advanced_color_guide.md](references/advanced_color_guide.md)、[references/transparency_guide.md](references/transparency_guide.md)、[references/typography_guide.md](references/typography_guide.md)
- 输出后端：[references/drawio_xml_guide.md](references/drawio_xml_guide.md)、[references/svg_output_guide.md](references/svg_output_guide.md)、[references/png_rendering_guide.md](references/png_rendering_guide.md)
- 质量、合规与故障：[references/quality_rubric.md](references/quality_rubric.md)、[references/contest_compliance.md](references/contest_compliance.md)、[references/troubleshooting.md](references/troubleshooting.md)

## 完成门禁

- 所有输出非空且可解析；节点 ID 唯一、边引用正确，三种格式节点和关键边一致。
- 无明显重叠、严重裁切、箭头穿越节点、身份信息或不透明背景错误。
- 主备布局节点/边语义一致、空间结构明显不同，分数达到阈值。
- 每个建模问题至少有一个 `main_method`，并以 `submethod/component/validation` 形成可见的父子层级、并行分支或汇聚；不得退化为简单步骤链。
- 禁止绕过 ModelingIR 与质量门禁，直接用 Mermaid、Graphviz、Pillow、SVG 拼装或图像生成模型画最终框架图；临时草图也必须回灌为 ModelingIR 后再交付。
- CLI 返回码、随机种子可重复性、竞赛离线模式和中文路径均经测试。
- 无法验证的可选后端或视觉条件必须如实记录，不能用占位结果替代。

## 四个完整调用示例

总体技术路线：

```powershell
python scripts/cumcm_flowchart.py --input solution.md paper.docx --output figures/overall `
  --diagram overall_route --primary-layout question_architecture --alternative-layout hierarchical_tree `
  --layouts 2 --theme journal-rich --transparent --png-dpi 300 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```

回字形算法闭环：

```powershell
python scripts/cumcm_flowchart.py --input optimization.md --output figures/loop `
  --diagram algorithm_loop --primary-layout rectangular_loop --alternative-layout u_shaped `
  --theme teal-orange --transparent --png-dpi 300 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```

双数据流预测架构：

```powershell
python scripts/cumcm_flowchart.py --input multimodal.md model.py --output figures/dual `
  --diagram data_pipeline --primary-layout dual_stream --alternative-layout layered_architecture `
  --theme ocean-gradient --transparent --png-dpi 600 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```

优化已有 draw.io：

```powershell
python scripts/cumcm_flowchart.py --input existing.drawio --output figures/revised `
  --diagram auto --primary-layout layered_architecture --alternative-layout serpentine `
  --theme journal-rich --transparent --png-dpi 300 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```
