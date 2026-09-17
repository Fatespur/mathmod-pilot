# Problem Analyzer & Task Decomposition (`problem-analyzer`)

> 所属分类：`01-problem-understanding` | 竞赛流水线阶段：`S1`

## 1. 技能概述 (Overview)

`problem-analyzer` 是 CUMCM 数学建模全生命周期中的核心技能模块。
**核心定位**：赛题形式化分解，抽取数学结构、物理实体、变量单位、目标函数、硬软约束与边界条件，生成可执行的问题依赖图与断言集。

## 2. 为什么需要它 (Why It Matters)

数学建模竞赛的起点门禁，决定后续所有数学抽象与数据准备的方向，纯粹服务于数模工作流。

在传统的数学建模中，建模人员或智能体容易陷入凭主观直觉盲目套用模型、缺少前后数据与断言契约、忽视物理与机理一致性等常见缺陷。本技能通过明确的输入输出契约、严格的反套路规则与自检清单，确保建模成果的高科学度与严密性。

## 3. 在建模工作流中的位置 (Pipeline Placement)

```text
['Start / User Input']
        │
        ▼
┌──────────────────────────────────────┐
│  [S1] problem-analyzer      │
└──────────────────────────────────────┘
        │
        ▼
[Downstream Stages & Artifact Delivery]
```

- **生命周期阶段**：Stage S1 (赛题理解与任务分解)
- **前置依赖**：无（初始化阶段直接载入）
- **触发时机**：进入阶段 S1 或上游工件就绪时被工作流调度器自动调用。

## 4. 输入契约 (Inputs)

| 必需输入工件 | 说明 |
| :--- | :--- |
| `run_inputs.json` | 阶段执行所依赖的上游工件或输入源 |
| `competition_problem.pdf/txt` | 阶段执行所依赖的上游工件或输入源 |

## 5. 输出契约 (Outputs)

| 生成目标工件 | 说明 |
| :--- | :--- |
| `problem_structure.json` | 本阶段通过严格验证后输出的权威产物 |
| `problem_graph.json` | 本阶段通过严格验证后输出的权威产物 |
| `variables_and_units.json` | 本阶段通过严格验证后输出的权威产物 |
| `hard_assertions.json` | 本阶段通过严格验证后输出的权威产物 |
| `assumption_risk_register.json` | 本阶段通过严格验证后输出的权威产物 |
| `expected_output_ranges.json` | 本阶段通过严格验证后输出的权威产物 |
| `analysis_report.md` | 本阶段通过严格验证后输出的权威产物 |

## 6. 如何调用 (Usage & Invocation)

### Agent 提示词调用模式
在兼容的 Agent 框架或 Claude/Gemini 工作流中：
```markdown
使用技能: $problem-analyzer
任务目标: 执行 赛题形式化分解，抽取数学结构、物理实体、变量单位、目标函数、硬软约束与边界条件，生成可执行的问题依赖图与断言集
输入工件: run_inputs.json, competition_problem.pdf/txt
```

### CLI / 脚本辅助调用（若附带本地脚本）
本技能目录下可能包含辅助验证与执行工具，位于 `scripts/`。可在环境配置完成后直接运行：
```bash
# 查看帮助与参数规范
python skills/01-problem-understanding/problem-analyzer/scripts/<script_name>.py --help
```

## 7. 典型工作流示例 (Workflow Example)

以典型的实际建模任务为例：
1. **加载前置数据与契约**：读取前置工件，解析输入结构；
2. **执行核心算法与决策逻辑**：遵循 `SKILL.md` 中定义的决策树、反套路门禁与核心数学推导；
3. **自我质量闭环检验**：运行内置检验脚本或断言规则，排查异常值与违规指标；
4. **提交权威工件**：生成目标产物并签署 Hash 指纹，移交给下一阶段。

## 8. 实施注意事项 (Caveats & Pitfalls)

- **严禁越界修改**：当前技能只能读写契约内规定的工件，不得擅自修改上游已锁定的物理假设或数据；
- **防范模板化**：坚决杜绝脱离实际赛题背景的“无脑套用”与假大空包装；
- **版本对齐**：当上游工件被回退或修改时，本技能生成的所有下游派生文件必须同步失效并重新生成。
