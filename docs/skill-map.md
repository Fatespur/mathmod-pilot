# CUMCM Toolkit 技能拓扑与依赖图谱 (Skill Map)

本图谱详细列出了工具箱中全部 15 个核心 Skill 的分类、生命周期阶段、所有依赖关系与核心工件。

| 分类目录 | 技能名称 | 阶段标识 | 前置依赖 | 核心输入工件 | 核心输出工件 |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `01-problem-understanding` | `problem-analyzer` | S1 | None | `run_inputs.json` | `problem_structure.json`, `hard_assertions.json` |
| `02-data-analysis` | `data-processing` | S2A | `problem-analyzer` | `problem_structure.json`, 赛题数据 | `preprocessing_report.md`, `clean_data/` |
| `03-model-formulation` | `model-selection` | S2B | `problem-analyzer`, `data-processing` | `problem_structure.json`, 数据字典 | `candidate_portfolio.json`, `selection_verdict.json` |
| `04-algorithms-and-solving` | `mle-solver` | S3 | `model-selection` | `candidate_portfolio.json` | `model_spec.json`, `solver_manifest.json`, `results/` |
| `04-algorithms-and-solving` | `systematic-debugging` | S3-dbg | `mle-solver` | 求解器异常堆栈, 失败断言 | `debug_report.json`, 修复后模型规范 |
| `05-validation` | `model-validation` | S4 | `mle-solver` | `model_spec.json`, `results/` | `validation_plan.json`, `validation_report.md` |
| `06-visualization` | `scipilot-figure-cumcm` | S5A | `model-validation` | `validation_evidence.json`, 论证目标 | `figure_plan.json`, `figure_manifest.json` |
| `06-visualization` | `scipilot-figure-skill` | S5A | `scipilot-figure-cumcm` | 规整数据, 绘图规范 | `publication_figure.png`, 矢量 SVG, 质检报告 |
| `06-visualization` | `matlab-figure` | S5A | `mle-solver` | 空间曲面数据, 流场矩阵 | 三维曲面图, Parula 色标图 |
| `06-visualization` | `cumcm-academic-flowchart` | S5B | `model-validation`, `problem-analyzer` | `problem_structure.json`, `model_spec.json` | `diagram_primary.drawio`, 原生 SVG, 高清 PNG |
| `07-writing` | `mcm-paper-writing` | S6 | `scipilot-figure-cumcm`, `cumcm-academic-flowchart` | 论文各节图表, 数值宏清单 | `PAPER_FINAL.md`, `paper.docx`, 篇幅度量 |
| `07-writing` | `reference-manager` | PH2 | `mcm-paper-writing` | 正文引用标记, 原始文献源 | `citation_report.json`, GB/T 7714 文献库 |
| `08-quality-assurance` | `paper-review` | S7 | `mcm-paper-writing`, `reference-manager` | `PAPER_FINAL.md`, `paper_macros.json` | `paper_review_report.json`, 匿名安全报告 |
| `08-quality-assurance` | `winning-paper-analysis` | Benchmark | `problem-analyzer` | 论文初稿, 赛题类型 | 国奖对标建议, 黄金篇幅密度分析 |
| `09-orchestration` | `modeling-workflow-orchestrator` | S0 | None | 状态转移事件, 工件哈希 | `workflow_state.json`, `pipeline_manifest.json` |
