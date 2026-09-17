# Mathematical Modeling Paper Writing (Markdown-Only) (`mcm-paper-writing`)

> 所属分类：`07-writing` | 竞赛流水线阶段：`S6`

## 1. 技能概述 (Overview)

`mcm-paper-writing` 是 CUMCM 数学建模全生命周期中的核心技能模块。
**核心定位**：纯 Markdown 论文写作流水线：页码预算分配、Word 原生 OMML 数学公式规范、三线表排版、匿名合规审计与 Word 原生生成器。

## 2. 为什么需要它 (Why It Matters)

彻底弃用脆弱的 LaTeX 编译依赖，采用标准 Markdown + Word 原生 OMML 架构，内置完善的校验脚本与排版工具。

在传统的数学建模中，建模人员或智能体容易陷入凭主观直觉盲目套用模型、缺少前后数据与断言契约、忽视物理与机理一致性等常见缺陷。本技能通过明确的输入输出契约、严格的反套路规则与自检清单，确保建模成果的高科学度与严密性。

## 3. 在建模工作流中的位置 (Pipeline Placement)

```text
['scipilot-figure-cumcm', 'cumcm-academic-flowchart', 'model-validation']
        │
        ▼
┌──────────────────────────────────────┐
│  [S6] mcm-paper-writing      │
└──────────────────────────────────────┘
        │
        ▼
[Downstream Stages & Artifact Delivery]
```

- **生命周期阶段**：Stage S6 (规范化竞赛论文写作与排版)
- **前置依赖**：scipilot-figure-cumcm, cumcm-academic-flowchart, model-validation
- **触发时机**：进入阶段 S6 或上游工件就绪时被工作流调度器自动调用。

## 4. 输入契约 (Inputs)

| 必需输入工件 | 说明 |
| :--- | :--- |
| `figure_manifest.json` | 阶段执行所依赖的上游工件或输入源 |
| `framework_assessment.json` | 阶段执行所依赖的上游工件或输入源 |
| `model_spec.json` | 阶段执行所依赖的上游工件或输入源 |
| `validation_report.md` | 阶段执行所依赖的上游工件或输入源 |
| `paper_macros.json` | 阶段执行所依赖的上游工件或输入源 |

## 5. 输出契约 (Outputs)

| 生成目标工件 | 说明 |
| :--- | :--- |
| `paper_page_plan.json` | 本阶段通过严格验证后输出的权威产物 |
| `paper_macros.json` | 本阶段通过严格验证后输出的权威产物 |
| `pre_draft_numeric_evidence.json` | 本阶段通过严格验证后输出的权威产物 |
| `PAPER_FINAL.md` | 本阶段通过严格验证后输出的权威产物 |
| `paper.docx` | 本阶段通过严格验证后输出的权威产物 |
| `writing_metrics.json` | 本阶段通过严格验证后输出的权威产物 |

## 6. 如何调用 (Usage & Invocation)

### Agent 提示词调用模式
在兼容的 Agent 框架或 Claude/Gemini 工作流中：
```markdown
使用技能: $mcm-paper-writing
任务目标: 执行 纯 Markdown 论文写作流水线：页码预算分配、Word 原生 OMML 数学公式规范、三线表排版、匿名合规审计与 Word 原生生成器
输入工件: figure_manifest.json, framework_assessment.json, model_spec.json, validation_report.md, paper_macros.json
```

### CLI / 脚本辅助调用（若附带本地脚本）
本技能目录下可能包含辅助验证与执行工具，位于 `scripts/`。可在环境配置完成后直接运行：
```bash
# 查看帮助与参数规范
python skills/07-writing/mcm-paper-writing/scripts/<script_name>.py --help
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
