# MathMod-Pilot

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Code Style: Ruff](https://img.shields.io/badge/Code%20Style-Ruff-261230.svg)](https://docs.astral.sh/ruff/)
[![Skills: 15](https://img.shields.io/badge/Skills-15-success.svg)](#skill-matrix)
[![Pipeline: S0–S7](https://img.shields.io/badge/Pipeline-S0%E2%80%93S7-informational.svg)](#system-architecture)
[![Website](https://img.shields.io/badge/Website-GitHub%20Pages-6366f1.svg)](https://fatespur.github.io/mathmod-pilot/)

> 🌐 **Project Showcase**: Visit our interactive website at
> **<https://fatespur.github.io/mathmod-pilot/>** for a visual tour of the
> library's architecture, skill matrix, and Generate-Verify-Revise mechanism.

**[English](#english)** | **[中文](#中文)**

---

<!-- ==================== ENGLISH ==================== -->

<a id="english"></a>

# MathMod-Pilot

> An Agent-Native skill library for mathematical modelling competitions
> (CUMCM / MCM), covering the full pipeline from problem analysis to paper
> review.

MathMod-Pilot packages **15 specialised skills** — each a self-contained folder with
a native `SKILL.md` prompt and a Python entry point — into a single installable
library. Skills are discovered dynamically at run-time: dropping a new folder
into `src/mathmod_pilot/skills/` is all that is needed to extend the agent.

## Table of Contents

- [System Architecture](#system-architecture)
- [Skill Matrix](#skill-matrix)
- [Installation](#installation)
- [Quickstart](#quickstart)
- [The mle-solver Generate-Verify-Revise Mechanism](#the-mle-solver-generate-verify-revise-mechanism)
- [Acknowledgements & Credits](#acknowledgements--credits)
- [Citation](#citation)

---

## System Architecture

MathMod-Pilot follows a **dynamic plugin architecture**: the core agent does not
hard-code any skill. Instead, it scans `src/mathmod_pilot/skills/` at import time,
imports each skill's `skill.py`, and registers the first `BaseSkill` subclass
it finds.

### Directory Layout

```
mathmod-pilot/
├── src/mathmod_pilot/
│   ├── __init__.py              # version & lazy exports
│   ├── core/
│   │   └── agent.py             # MathModPilotAgent — registry + pipeline runner
│   └── skills/
│       ├── base.py              # BaseSkill (ABC) + PromptSkill
│       ├── __init__.py          # discover_skills() — dynamic scanner
│       └── <skill_folder>/      # ×15 — one folder per skill
│           ├── SKILL.md         # native prompt (preserved verbatim)
│           └── skill.py         # Python entry point (BaseSkill subclass)
├── examples/
├── tests/
├── pyproject.toml
├── CITATION.cff
├── ACKNOWLEDGEMENTS.md
└── README.md
```

### How Skills Are Loaded

1. **`BaseSkill`** (`skills/base.py`) defines the abstract contract: every
   skill must implement `execute(self, inputs: dict) -> dict`. It also parses
   the `SKILL.md` YAML front-matter to populate a `SkillMeta` dataclass
   (name, description, version, stage, tier).

2. **`discover_skills()`** (`skills/__init__.py`) iterates every sub-directory
   of `skills/` that contains a `SKILL.md`. If a `skill.py` is present, it is
   imported and the first `BaseSkill` subclass is instantiated. Directories
   without `skill.py` fall back to a `PromptSkill` wrapper so that even
   pure-markdown skills remain callable.

3. **`MathMod-PilotAgent`** (`core/agent.py`) holds the registry and provides two
   execution modes:
   - `run_skill(name, inputs)` — invoke a single skill.
   - `run_pipeline(inputs, stages)` — chain skills S0 → S7, threading the
     context dictionary forward so each stage receives the previous stage's
     output.

### Core Pipeline Stages

| Stage | Skill | Responsibility |
|:-----:|-------|----------------|
| S0 | `brainstorming` | Requirement exploration & pipeline initialisation |
| S1 | `problem-analyzer` | Problem decomposition, method routing, hard-assertion generation |
| S2 | `data-processing` | Multi-format data loading, cleaning, physical-constraint validation |
| S3 | `mle-solver` | Model code generation, execution, iterative revision |
| S4 | `model-validation` | Sensitivity analysis, Monte-Carlo uncertainty, residual diagnostics |
| S5 | `scipilot-figure` | Publication-grade visualisation (S5 dispatcher) |
| S6 | `mcm-paper-writing` | Contest paper drafting (CUMCM / MCM dual-mode) |
| S7 | `paper-review` | Nine-dimension final review benchmarked against award winners |

---

## Skill Matrix

Skills are grouped into three tiers: **Tier 1** (core pipeline), **Tier 2**
(visualisation specialists), and **Tier 3** (writing & review aids).

| # | Skill | Directory | Tier | Stage | Ver. | Core Function | Key Dependencies |
|---|-------|-----------|:----:|:-----:|:----:|---------------|-------------------|
| 1 | brainstorming | `brainstorming/` | 1 | S0 | 2.0.0 | Requirement exploration & pipeline init | — |
| 2 | problem-analyzer | `problem-analyzer/` | 1 | S1 | 14.0.0 | 15-type routing, hard assertions, first-principles audit | — |
| 3 | data-processing | `data-processing/` | 1 | S2 | 4.0.0 | Excel/CSV/JSON loading, outlier detection, constraint validation | pandas |
| 4 | mle-solver | `mle-solver/` | 1 | S3 | 9.0.0 | Generate-Verify-Revise code loop; GA/PSO/SA/DE optimisers | numpy, scipy |
| 5 | model-validation | `model-validation/` | 1 | S4 | 8.0.0 | OAT/Morris/Sobol sensitivity, Monte-Carlo, residual diagnostics | SALib, statsmodels |
| 6 | scipilot-figure | `scipilot-figure/` | 1 | S5 | 2.0.0 | CUMCM/MCM visualisation dispatcher with chart-type routing | matplotlib, seaborn |
| 7 | mcm-paper-writing | `mcm-paper-writing/` | 1 | S6 | 5.0.0 | CUMCM (Chinese) / MCM (English) dual-mode, macro-variable driven | — |
| 8 | paper-review | `paper-review/` | 1 | S7 | 4.0.0 | Nine-dimension review, award-paper benchmarking, repair routing | — |
| 9 | scipilot-figure-skill | `scipilot-figure-skill/` | 2 | S5 | 2.1.0 | Visualisation advisor: data profiling → chart recommendation → rendering | matplotlib, seaborn, plotly |
| 10 | diagram-generator | `diagram-generator/` | 2 | S5 | 1.0.0 | Algorithm flowcharts, framework & architecture diagrams | matplotlib |
| 11 | matlab-figure | `matlab-figure/` | 2 | S5 | 1.0.0 | MATLAB 3-D surfaces (surf/mesh), vector fields (quiver), Simulink | MATLAB |
| 12 | nature-figure | `nature-figure/` | 2 | S5 | 1.0.0 | Nature/Science journal-grade figures; Python/R dual backend; AI schematics | matplotlib, requests |
| 13 | winning-paper-analysis | `winning-paper-analysis/` | 3 | S6 | 1.0.0 | Award-winning paper structure, section proportion & writing patterns | — |
| 14 | reference-manager | `reference-manager/` | 3 | S6 | 1.0.0 | GB/T 7714 (CUMCM) & APA (MCM) formatting, DOI completeness checks | — |
| 15 | systematic-debugging | `systematic-debugging/` | 3 | aux | 3.0.0 | Anti-pattern library, automatic error-repair routing | — |

---

## Installation

```bash
# Core only (prompt loading & agent — no heavy scientific deps)
pip install -e .

# Full installation (all optional scientific dependencies)
pip install -e ".[full]"

# Selective extras
pip install -e ".[solver,viz,validation]"
```

> **Python 3.10+** is required. Only `PyYAML` is a hard dependency; all
> scientific libraries are optional extras so that skills degrade gracefully
> when their backends are absent.

---

## Quickstart

### Load a single skill

```python
from mathmod_pilot.core import MathMod-PilotAgent

agent = MathMod-PilotAgent()

# List all registered skills
print(agent.list_skills())
# ['brainstorming', 'data-processing', ..., 'systematic-debugging']

# Retrieve the problem-analyzer prompt
result = agent.run_skill("problem-analyzer", {
    "problem_text": "Determine the optimal layout of solar mirrors...",
})
print(result["prompt"][:200])   # the native SKILL.md prompt
```

### Run the full pipeline

```python
from mathmod_pilot.core import MathMod-PilotAgent, PIPELINE

agent = MathMod-PilotAgent()

# S0 → S7 in sequence; context is threaded forward automatically
results = agent.run_pipeline({
    "problem_text": "2023 CUMCM Problem A: ...",
    "data_path": "data.xlsx",
})

for skill_name, output in results.items():
    print(f"{skill_name:25s} -> {output.get('status', 'n/a')}")
```

### Call a skill directly (bypass the agent)

```python
from mathmod_pilot.skills import get_skill

skill = get_skill("mle-solver")
if skill is not None:
    # Invoke the heuristic optimiser directly
    import numpy as np
    result = skill.execute({
        "optimization": {
            "objective_func": lambda x: float(np.sum(x**2)),
            "bounds": [(-5, 5), (-5, 5)],
            "method": "GA",
        }
    })
    print(result.get("optimization_result"))
```

---

## The mle-solver Generate-Verify-Revise Mechanism

The `mle-solver` skill (S3, v9.0.0) is the computational heart of MathMod-Pilot.
Its `SKILL.md` prompt defines an **iterative self-correction loop** that
cycles through three phases — **Generate**, **Verify**, and **Revise** —
until all hard assertions pass.

```
 ┌──────────────────────────────────────────────────────────┐
 │                    mle-solver (S3)                        │
 │                                                          │
 │  ┌──────────┐     ┌─────────────┐     ┌──────────────┐  │
 │  │ Generate │────▶│   Verify    │────▶│    Revise    │  │
 │  │          │     │             │     │              │  │
 │  │ Produce  │     │ Run code    │     │ Feed errors  │  │
 │  │ executable│    │ Capture     │     │ back into    │  │
 │  │ model    │     │ errors &    │     │ Generate     │  │
 │  │ code     │     │ assertions  │     │              │  │
 │  └──────────┘     └──────┬──────┘     └──────┬───────┘  │
 │       ▲                  │                   │          │
 │       │           PASS? ─┤─ NO ──────────────┘          │
 │       │                  │                              │
 │       │                 YES                             │
 │       └──────────────────┘                              │
 │          (return solution + validation report)          │
 └──────────────────────────────────────────────────────────┘
```

**Phase 1 — Generate.** Translates the mathematical model into executable
Python code (regression, optimisation, ODE solving, evaluation methods, etc.),
routed by the problem type received from `problem-analyzer`.

**Phase 2 — Verify.** Runs the generated code and checks three layers of
assertions:
- **S1 hard assertions** — physical consistency, equal-X constraints,
  smoothness requirements forwarded from the problem-analyzer.
- **Physical consistency** — dimensional homogeneity, boundary feasibility,
  monotonicity where expected.
- **Model-reality cross-validation** — comparison against external benchmarks
  (e.g. PS10 / Gemasolar for solar-concentration problems).

**Phase 3 — Revise.** When verification fails, the captured error trace and
assertion violations are fed back into the Generate phase. The loop continues
until all assertions pass or a maximum revision count is reached. If the
failure pattern matches a known anti-pattern (magic numbers, method mismatch,
threshold masking, over-smoothing, assumption drift), the `systematic-debugging`
skill is invoked for targeted repair.

The `extensions/heuristic_algorithms.py` module provides self-contained
**GA / PSO / SA / DE** optimisers with a unified `solve_optimization()` entry
point, enabling the solver to handle non-convex and discontinuous objective
functions without external solvers.

---

## Acknowledgements & Credits

MathMod-Pilot builds upon and integrates work from multiple open-source projects
and research contributions. The full attribution table — including original
sources, authors, licenses, and modification notes for every skill — is
available in [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md).

We gratefully acknowledge the following projects and authors:

- **Haojae** for the [scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill)
  visualisation advisor (MIT License), whose original Python modules are shipped
  unmodified in `skills/scipilot-figure-skill/scripts/`.
- **Chen Liu** (Yale University) for the
  [figures4papers](https://github.com/ChenLiu-1996/figures4papers) repository,
  whose publication-grade matplotlib scripts from *Nature Machine Intelligence*,
  *ICML*, *NeurIPS*, and *ECCV* papers served as pattern references for the
  `nature-figure` skill.
- **personqianduixue** for the
  [Math_Model](https://github.com/personqianduixue/Math_Model) repository
  (6.3k+ stars), cited as a data source for award-winning CUMCM/MCM papers in
  the `winning-paper-analysis` skill.
- The maintainers of NumPy, SciPy, scikit-learn, matplotlib, seaborn, plotly,
  pandas, SALib, statsmodels, and SciencePlots — the scientific Python stack
  that powers MathMod-Pilot's computational and visualisation capabilities.

> **Compliance note:** Two upstream projects (`figures4papers` and `Math_Model`)
> do not carry explicit open-source licenses. See the
> [Compliance Notes](ACKNOWLEDGEMENTS.md#compliance-notes) section in
> `ACKNOWLEDGEMENTS.md` for details and recommended actions.

---

## Citation

If you use MathMod-Pilot in academic work or a modelling competition, please cite it
as follows:

```bibtex
@software{mathmodpilot2026,
  title        = {MathMod-Pilot: An Agent-Native Skill Library for Mathematical
                  Modelling Competitions},
  author       = {{MathMod-Pilot Contributors}},
  year         = 2026,
  version      = {1.0.0},
  license      = {MIT},
  url          = {https://github.com/Fatespur/mathmod-pilot},
}
```

A machine-readable citation file is provided as [`CITATION.cff`](CITATION.cff).

---

## License

Released under the [MIT License](LICENSE). Third-party skills retain their
original copyright notices.

---

<!-- ==================== CHINESE ==================== -->

<a id="中文"></a>

# MathMod-Pilot（中文文档）

> 面向数学建模竞赛（CUMCM / MCM）的 Agent-Native 技能库，覆盖从问题分析
> 到论文评审的全流程。

> 🌐 **项目展示页**：访问 **<https://fatespur.github.io/mathmod-pilot/>**
> 查看库的架构、技能矩阵和 Generate-Verify-Revise 机制的交互式可视化介绍。

MathMod-Pilot 将 **15 个专业技能**——每个技能都是一个独立的文件夹，包含原生
`SKILL.md` 提示词和 Python 执行入口——打包为一个可安装的库。技能在运行时
动态发现：只需将新文件夹放入 `src/mathmod_pilot/skills/` 即可扩展 Agent。

## 目录

- [系统架构](#系统架构)
- [技能矩阵](#技能矩阵)
- [安装](#安装)
- [快速开始](#快速开始)
- [mle-solver 的 Generate-Verify-Revise 机制](#mle-solver-的-generate-verify-revise-机制)
- [致谢与归因](#致谢与归因)
- [引用](#引用-1)

---

## 系统架构

MathMod-Pilot 采用**动态插件架构**：核心 Agent 不硬编码任何技能。而是在导入时
扫描 `src/mathmod_pilot/skills/` 目录，导入每个技能的 `skill.py`，并注册找到的
第一个 `BaseSkill` 子类。

### 目录结构

```
mathmod-pilot/
├── src/mathmod_pilot/
│   ├── __init__.py              # 版本号与延迟导出
│   ├── core/
│   │   └── agent.py             # MathModPilotAgent — 注册表 + 流水线运行器
│   └── skills/
│       ├── base.py              # BaseSkill (ABC) + PromptSkill
│       ├── __init__.py          # discover_skills() — 动态扫描器
│       └── <skill_folder>/      # ×15 — 每个技能一个文件夹
│           ├── SKILL.md         # 原生提示词（完整保留）
│           └── skill.py         # Python 执行入口（BaseSkill 子类）
├── examples/
├── tests/
├── pyproject.toml
├── CITATION.cff
├── ACKNOWLEDGEMENTS.md
└── README.md
```

### 技能加载机制

1. **`BaseSkill`**（`skills/base.py`）定义抽象契约：每个技能必须实现
   `execute(self, inputs: dict) -> dict`。同时解析 `SKILL.md` 的 YAML
   front-matter，填充 `SkillMeta` 数据类（名称、描述、版本、阶段、梯队）。

2. **`discover_skills()`**（`skills/__init__.py`）遍历 `skills/` 下每个包含
   `SKILL.md` 的子目录。如果存在 `skill.py`，则导入并实例化其中的第一个
   `BaseSkill` 子类。没有 `skill.py` 的目录会回退到 `PromptSkill` 包装器，
   确保纯 Markdown 技能也可调用。

3. **`MathMod-PilotAgent`**（`core/agent.py`）持有注册表，提供两种执行模式：
   - `run_skill(name, inputs)` — 调用单个技能。
   - `run_pipeline(inputs, stages)` — 串联 S0 → S7 技能，将上下文字典
     向前传递，使每个阶段接收上一阶段的输出。

### 核心流水线阶段

| 阶段 | 技能 | 职责 |
|:----:|------|------|
| S0 | `brainstorming` | 需求探索与流水线初始化 |
| S1 | `problem-analyzer` | 问题分解、方法路由、硬断言生成 |
| S2 | `data-processing` | 多格式数据加载、清洗、物理约束验证 |
| S3 | `mle-solver` | 模型代码生成、执行、迭代修正 |
| S4 | `model-validation` | 灵敏度分析、蒙特卡洛不确定性、残差诊断 |
| S5 | `scipilot-figure` | 出版级可视化（S5 调度器） |
| S6 | `mcm-paper-writing` | 竞赛论文撰写（CUMCM / MCM 双模式） |
| S7 | `paper-review` | 九维终审，对标获奖论文 |

---

## 技能矩阵

技能分为三个梯队：**Tier 1**（核心流水线）、**Tier 2**（可视化专家）、
**Tier 3**（写作与评审辅助）。

| # | 技能 | 目录 | 梯队 | 阶段 | 版本 | 核心功能 | 关键依赖 |
|---|------|------|:----:|:----:|:----:|---------|---------|
| 1 | brainstorming | `brainstorming/` | 1 | S0 | 2.0.0 | 需求探索与流水线初始化 | — |
| 2 | problem-analyzer | `problem-analyzer/` | 1 | S1 | 14.0.0 | 15 种类型路由、硬断言、第一性原理审查 | — |
| 3 | data-processing | `data-processing/` | 1 | S2 | 4.0.0 | Excel/CSV/JSON 加载、异常值检测、约束验证 | pandas |
| 4 | mle-solver | `mle-solver/` | 1 | S3 | 9.0.0 | Generate-Verify-Revise 代码循环；GA/PSO/SA/DE 优化器 | numpy, scipy |
| 5 | model-validation | `model-validation/` | 1 | S4 | 8.0.0 | OAT/Morris/Sobol 灵敏度、蒙特卡洛、残差诊断 | SALib, statsmodels |
| 6 | scipilot-figure | `scipilot-figure/` | 1 | S5 | 2.0.0 | CUMCM/MCM 可视化调度器，图表类型路由 | matplotlib, seaborn |
| 7 | mcm-paper-writing | `mcm-paper-writing/` | 1 | S6 | 5.0.0 | CUMCM（中文）/ MCM（英文）双模式，宏变量驱动 | — |
| 8 | paper-review | `paper-review/` | 1 | S7 | 4.0.0 | 九维评审、获奖论文对标、修复路由 | — |
| 9 | scipilot-figure-skill | `scipilot-figure-skill/` | 2 | S5 | 2.1.0 | 可视化顾问：数据剖析 → 图表推荐 → 渲染 | matplotlib, seaborn, plotly |
| 10 | diagram-generator | `diagram-generator/` | 2 | S5 | 1.0.0 | 算法流程图、框架与架构图 | matplotlib |
| 11 | matlab-figure | `matlab-figure/` | 2 | S5 | 1.0.0 | MATLAB 三维曲面（surf/mesh）、矢量场（quiver）、Simulink | MATLAB |
| 12 | nature-figure | `nature-figure/` | 2 | S5 | 1.0.0 | Nature/Science 期刊级图表；Python/R 双后端；AI 示意图 | matplotlib, requests |
| 13 | winning-paper-analysis | `winning-paper-analysis/` | 3 | S6 | 1.0.0 | 获奖论文结构、章节比例与写作模式分析 | — |
| 14 | reference-manager | `reference-manager/` | 3 | S6 | 1.0.0 | GB/T 7714（国赛）与 APA（美赛）格式化，DOI 完整性检查 | — |
| 15 | systematic-debugging | `systematic-debugging/` | 3 | aux | 3.0.0 | 反模式库、自动错误修复路由 | — |

---

## 安装

```bash
# 仅核心（提示词加载与 Agent — 不安装重型科学计算依赖）
pip install -e .

# 完整安装（所有可选科学计算依赖）
pip install -e ".[full]"

# 按需安装
pip install -e ".[solver,viz,validation]"
```

> **需要 Python 3.10+**。仅 `PyYAML` 为硬依赖；所有科学计算库均为可选
> 依赖，确保技能在后端缺失时优雅降级。

---

## 快速开始

### 加载单个技能

```python
from mathmod_pilot.core import MathMod-PilotAgent

agent = MathMod-PilotAgent()

# 列出所有已注册技能
print(agent.list_skills())
# ['brainstorming', 'data-processing', ..., 'systematic-debugging']

# 获取 problem-analyzer 提示词
result = agent.run_skill("problem-analyzer", {
    "problem_text": "确定定日镜场的最优布局...",
})
print(result["prompt"][:200])   # 原生 SKILL.md 提示词
```

### 运行完整流水线

```python
from mathmod_pilot.core import MathMod-PilotAgent, PIPELINE

agent = MathMod-PilotAgent()

# S0 → S7 顺序执行；上下文自动向前传递
results = agent.run_pipeline({
    "problem_text": "2023 国赛 A 题：...",
    "data_path": "data.xlsx",
})

for skill_name, output in results.items():
    print(f"{skill_name:25s} -> {output.get('status', 'n/a')}")
```

### 直接调用技能（绕过 Agent）

```python
from mathmod_pilot.skills import get_skill

skill = get_skill("mle-solver")
if skill is not None:
    # 直接调用启发式优化器
    import numpy as np
    result = skill.execute({
        "optimization": {
            "objective_func": lambda x: float(np.sum(x**2)),
            "bounds": [(-5, 5), (-5, 5)],
            "method": "GA",
        }
    })
    print(result.get("optimization_result"))
```

---

## mle-solver 的 Generate-Verify-Revise 机制

`mle-solver` 技能（S3, v9.0.0）是 MathMod-Pilot 的计算核心。其 `SKILL.md`
提示词定义了一个**迭代自纠正循环**，依次经过三个阶段——**Generate**
（生成）、**Verify**（验证）、**Revise**（修正）——直到所有硬断言通过。

```
 ┌──────────────────────────────────────────────────────────┐
 │                    mle-solver (S3)                        │
 │                                                          │
 │  ┌──────────┐     ┌─────────────┐     ┌──────────────┐  │
 │  │ Generate │────▶│   Verify    │────▶│    Revise    │  │
 │  │          │     │             │     │              │  │
 │  │ 生成     │     │ 运行代码    │     │ 将错误反馈   │  │
 │  │ 可执行   │     │ 捕获错误    │     │ 回 Generate  │  │
 │  │ 模型代码 │     │ 与断言      │     │              │  │
 │  └──────────┘     └──────┬──────┘     └──────┬───────┘  │
 │       ▲                  │                   │          │
 │       │           通过? ─┤─ 否 ──────────────┘          │
 │       │                  │                              │
 │       │                  是                              │
 │       └──────────────────┘                              │
 │          （返回解 + 验证报告）                            │
 └──────────────────────────────────────────────────────────┘
```

**阶段 1 — Generate（生成）。** 将数学模型转化为可执行的 Python 代码
（回归、优化、ODE 求解、评价方法等），根据 `problem-analyzer` 接收的问题
类型进行方法路由。

**阶段 2 — Verify（验证）。** 运行生成的代码，检查三层断言：
- **S1 硬断言** — 物理一致性、等 X 约束、光滑性要求（由 problem-analyzer
  转发）。
- **物理一致性** — 量纲齐次性、边界可行性、预期的单调性。
- **模型-现实交叉验证** — 与外部基准对比（如太阳能聚光问题的 PS10 /
  Gemasolar）。

**阶段 3 — Revise（修正）。** 当验证失败时，将捕获的错误回溯和断言违规
反馈回 Generate 阶段。循环持续进行，直到所有断言通过或达到最大修正次数。
如果失败模式匹配已知反模式（魔法数字、方法不匹配、阈值掩盖、过度平滑、
假设漂移），则调用 `systematic-debugging` 技能进行针对性修复。

`extensions/heuristic_algorithms.py` 模块提供自包含的 **GA / PSO / SA / DE**
优化器，统一入口为 `solve_optimization()`，使求解器能够处理非凸和不连续
目标函数而无需外部求解器。

---

## 致谢与归因

MathMod-Pilot 整合了多个开源项目和研究贡献。完整的归因表——包括每个技能的
原始来源、作者、协议和修改说明——见 [ACKNOWLEDGEMENTS.md](ACKNOWLEDGEMENTS.md)。

我们衷心感谢以下项目和作者：

- **Haojae** 提供的 [scipilot-figure-skill](https://github.com/Haojae/scipilot-figure-skill)
  可视化顾问（MIT 协议），其原始 Python 模块完整保留在
  `skills/scipilot-figure-skill/scripts/` 中。
- **Chen Liu**（耶鲁大学）的 [figures4papers](https://github.com/ChenLiu-1996/figures4papers)
  仓库，其来自 *Nature Machine Intelligence*、*ICML*、*NeurIPS*、*ECCV*
  论文的出版级 matplotlib 脚本为 `nature-figure` 技能提供了模式参考。
- **personqianduixue** 的 [Math_Model](https://github.com/personqianduixue/Math_Model)
  仓库（6.3k+ stars），在 `winning-paper-analysis` 技能中作为获奖 CUMCM/MCM
  论文的数据来源被引用。
- NumPy、SciPy、scikit-learn、matplotlib、seaborn、plotly、pandas、SALib、
  statsmodels、SciencePlots 的维护者——科学 Python 栈为 MathMod-Pilot 的计算
  与可视化能力提供了基础。

> **合规提示：** 两个上游项目（`figures4papers` 和 `Math_Model`）未附带
> 明确的开源协议。详见 `ACKNOWLEDGEMENTS.md` 中的
> [合规说明](ACKNOWLEDGEMENTS.md#compliance-notes) 部分。

---

## 引用

如果您在学术工作或建模竞赛中使用了 MathMod-Pilot，请按以下格式引用：

```bibtex
@software{mathmodpilot2026,
  title        = {MathMod-Pilot: An Agent-Native Skill Library for Mathematical
                  Modelling Competitions},
  author       = {{MathMod-Pilot Contributors}},
  year         = 2026,
  version      = {1.0.0},
  license      = {MIT},
  url          = {https://github.com/Fatespur/mathmod-pilot},
}
```

机器可读的引用文件见 [`CITATION.cff`](CITATION.cff)。

---

## 许可证

基于 [MIT 协议](LICENSE) 发布。第三方技能保留其原始版权声明。
