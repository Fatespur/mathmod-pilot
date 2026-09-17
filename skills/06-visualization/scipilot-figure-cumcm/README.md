# Competition Scientific Data Visualization Planner (`scipilot-figure-cumcm`)

> 所属分类：`06-visualization` | 竞赛流水线阶段：`S5A`

## 1. 技能概述 (Overview)

`scipilot-figure-cumcm` 是 CUMCM 数学建模全生命周期中的核心技能模块。
**核心定位**：数模竞赛论证图表规划器：将核心结论与证据映射为高质量图型，严禁无效凑数图，控制篇幅信息增益与审阅抓手。

## 2. 为什么需要它 (Why It Matters)

专门负责从“结论-证据-图型”映射竞赛图表，杜绝双轴误导、彩虹色谱等低级错误，规范竞赛图表产出。

在传统的数学建模中，建模人员或智能体容易陷入凭主观直觉盲目套用模型、缺少前后数据与断言契约、忽视物理与机理一致性等常见缺陷。本技能通过明确的输入输出契约、严格的反套路规则与自检清单，确保建模成果的高科学度与严密性。

## 3. 在建模工作流中的位置 (Pipeline Placement)

```text
['model-validation']
        │
        ▼
┌──────────────────────────────────────┐
│  [S5A] scipilot-figure-cumcm      │
└──────────────────────────────────────┘
        │
        ▼
[Downstream Stages & Artifact Delivery]
```

- **生命周期阶段**：Stage S5A (竞赛结论数据图表规划)
- **前置依赖**：model-validation
- **触发时机**：进入阶段 S5A 或上游工件就绪时被工作流调度器自动调用。

## 4. 输入契约 (Inputs)

| 必需输入工件 | 说明 |
| :--- | :--- |
| `validation_evidence.json` | 阶段执行所依赖的上游工件或输入源 |
| `results/` | 阶段执行所依赖的上游工件或输入源 |
| `paper_claim_register.json` | 阶段执行所依赖的上游工件或输入源 |

## 5. 输出契约 (Outputs)

| 生成目标工件 | 说明 |
| :--- | :--- |
| `figure_plan.json` | 本阶段通过严格验证后输出的权威产物 |
| `figure_manifest.json` | 本阶段通过严格验证后输出的权威产物 |
| `figures/final/*.png` | 本阶段通过严格验证后输出的权威产物 |
| `figures/final/*.svg` | 本阶段通过严格验证后输出的权威产物 |

## 6. 如何调用 (Usage & Invocation)

### Agent 提示词调用模式
在兼容的 Agent 框架或 Claude/Gemini 工作流中：
```markdown
使用技能: $scipilot-figure-cumcm
任务目标: 执行 数模竞赛论证图表规划器：将核心结论与证据映射为高质量图型，严禁无效凑数图，控制篇幅信息增益与审阅抓手
输入工件: validation_evidence.json, results/, paper_claim_register.json
```

### CLI / 脚本辅助调用（若附带本地脚本）
本技能目录下可能包含辅助验证与执行工具，位于 `scripts/`。可在环境配置完成后直接运行：
```bash
# 查看帮助与参数规范
python skills/06-visualization/scipilot-figure-cumcm/scripts/<script_name>.py --help
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
