# Mathematical Model Solver & Heuristics (`mle-solver`)

> 所属分类：`04-algorithms-and-solving` | 竞赛流水线阶段：`S3`

## 1. 技能概述 (Overview)

`mle-solver` 是 CUMCM 数学建模全生命周期中的核心技能模块。
**核心定位**：数学模型方程映射、变量与约束组装、求解器配置（LP/MILP/ODE/PDE/图论）与启发式优化算法（GA/PSO/SA）执行。

## 2. 为什么需要它 (Why It Matters)

负责将数学抽象转化为可执行代码与计算结果，内置完整的启发式优化算法实现，是模型求解的中枢。

在传统的数学建模中，建模人员或智能体容易陷入凭主观直觉盲目套用模型、缺少前后数据与断言契约、忽视物理与机理一致性等常见缺陷。本技能通过明确的输入输出契约、严格的反套路规则与自检清单，确保建模成果的高科学度与严密性。

## 3. 在建模工作流中的位置 (Pipeline Placement)

```text
['model-selection']
        │
        ▼
┌──────────────────────────────────────┐
│  [S3] mle-solver      │
└──────────────────────────────────────┘
        │
        ▼
[Downstream Stages & Artifact Delivery]
```

- **生命周期阶段**：Stage S3 (模型建立与数值求解)
- **前置依赖**：model-selection
- **触发时机**：进入阶段 S3 或上游工件就绪时被工作流调度器自动调用。

## 4. 输入契约 (Inputs)

| 必需输入工件 | 说明 |
| :--- | :--- |
| `candidate_portfolio.json` | 阶段执行所依赖的上游工件或输入源 |
| `selection_verdict.json` | 阶段执行所依赖的上游工件或输入源 |
| `problem_structure.json` | 阶段执行所依赖的上游工件或输入源 |

## 5. 输出契约 (Outputs)

| 生成目标工件 | 说明 |
| :--- | :--- |
| `model_spec.json` | 本阶段通过严格验证后输出的权威产物 |
| `solver_manifest.json` | 本阶段通过严格验证后输出的权威产物 |
| `paper_macro_candidates.json` | 本阶段通过严格验证后输出的权威产物 |
| `validation_handoff.json` | 本阶段通过严格验证后输出的权威产物 |
| `results/` | 本阶段通过严格验证后输出的权威产物 |

## 6. 如何调用 (Usage & Invocation)

### Agent 提示词调用模式
在兼容的 Agent 框架或 Claude/Gemini 工作流中：
```markdown
使用技能: $mle-solver
任务目标: 执行 数学模型方程映射、变量与约束组装、求解器配置（LP/MILP/ODE/PDE/图论）与启发式优化算法（GA/PSO/SA）执行
输入工件: candidate_portfolio.json, selection_verdict.json, problem_structure.json
```

### CLI / 脚本辅助调用（若附带本地脚本）
本技能目录下可能包含辅助验证与执行工具，位于 `scripts/`。可在环境配置完成后直接运行：
```bash
# 查看帮助与参数规范
python skills/04-algorithms-and-solving/mle-solver/scripts/<script_name>.py --help
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
