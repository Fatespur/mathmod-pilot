---
name: "diagram-generator"
description: "生成精确的算法流程图、框架图、模型架构图、Pipeline流程图。matplotlib.patches精确控制间距/字体/模块尺寸/箭头，支持阴影、渐变、彩色accent bar、自定义曲线箭头。当用户需要论文中的算法流程图、框架图、架构图、Pipeline图、问题分析框架图、技术路线图时调用。"
---


## 与 Skill 组的关系

| Skill | 阶段 | 关系 |
|-------|:----:|------|
| scipilot-figure-cumcm | S5 | 调度者：将结构图/框架图/流程图路由到本 skill |
| scipilot-figure-skill | S5 | 互补：本 skill 负责结构图/框架图，scipilot-figure-skill 负责数据图 |
| nature-figure | S5 | 互补：本 skill 负责结构图，nature-figure 负责期刊排版和 AI 示意图 |
| mcm-paper-writing | S6 | 下游：论文写作阶段消费本 skill 产出的流程图/框架图/架构图/Pipeline 图 |

**职责边界**：本 skill 只负责算法流程图、框架图、模型架构图、Pipeline 流程图的生成。不负责数据可视化（那是 scipilot-figure-skill 和 scipilot-figure-cumcm 的职责）。
# Diagram Generator

# Diagram Generator — 论文图表生成器（v3）

你是**论文图表生成专家**，专门生成数学建模论文中需要的**精确算法流程图、框架图、模型架构图和Pipeline图**。基于 matplotlib.patches 实现像素级精确控制。

**v3 变更：框架图、模型架构图、Pipeline 流程图统一使用 matplotlib.patches 方案（像素级精确控制，阴影/渐变/自定义箭头）。**

## 核心能力

1. **算法流程图**：每个模型至少 1 张，结合本题变量标注，步骤清晰 1-5 步
2. **决策分支图**：含判断节点的条件分支流程
3. **迭代循环图**：展示迭代/循环逻辑的算法结构

## 两种后端

| 后端 | 适用场景 | 优点 | 缺点 |
|------|---------|------|------|
| **mermaid** | 文本描述流程图，快速生成 | 纯文本，易修改，可直接嵌入 Markdown | 布局不可控，中文支持需配置 |
| **matplotlib.patches** | 精确控制每个节点位置、颜色、字体 | 完全可控，中文完美支持，输出矢量图 | 代码量较大 |

**默认使用 mermaid（快）+ matplotlib.patches（精确），互为补充。注意：graphviz 不再推荐用于流程图（受限于 HTML label 解析不一致）。**

---

## 一、算法流程图

### 数据格式

```python
steps = [
    {"id": "step1", "text": "输入参数: M_total, C_elev, m_rocket", "vars": "M_total, C_elev, m_rocket"},
    {"id": "step2", "text": "构建 MILP 模型: min Cost = f(x_elev, N_rocket)", "vars": "x_elev, N_rocket"},
    {"id": "dec1", "text": "N_rocket 是否为整数?", "type": "decision"},
    {"id": "step3", "text": "Branch and Bound 分支定界", "vars": ""},
    {"id": "step4", "text": "LP 松弛求解", "vars": ""},
    {"id": "step5", "text": "输出最优解: x_elev*, N_rocket*, T*", "vars": "x_elev*, N_rocket*, T*"},
]
relationships = [
    ("step1", "step2"),
    ("step2", "dec1"),
    ("dec1", "step3", "是"),
    ("dec1", "step4", "否"),
    ("step3", "step5"),
    ("step4", "step5"),
]
```

### 生成函数

```python
def generate_algorithm_flowchart(
    steps: list,          # [{"id": "step1", "text": "...", "vars": "n, d", "type": "process|decision"}, ...]
    relationships: list,  # [("step1", "step2", "label"), ...]
    title: str = "算法流程图",
    output_path: str = "figures/algorithm_flowchart.png",
    use_mermaid: bool = True,
):
    """生成算法流程图"""
```

### Mermaid 方式（推荐）

```python
def to_mermaid(steps, relationships):
    """将步骤和关系转换为 Mermaid flowchart 语法"""
    lines = ["flowchart TD"]
    for s in steps:
        shape = "{{" if s.get("type") == "decision" else "["
        shape_end = "}}" if s.get("type") == "decision" else "]"
        label = f"{s['text']}<br/>变量: {s['vars']}" if s.get('vars') else s['text']
        lines.append(f"    {s['id']}{shape}{label}{shape_end}")
    for r in relationships:
        label = f"|{r[2]}|" if len(r) > 2 else ""
        lines.append(f"    {r[0]} -->{label} {r[1]}")
    return "\n".join(lines)
```

### Matplotlib.patches 方式

```python
def generate_algorithm_flowchart_matplotlib(
    steps: list,
    relationships: list,
    title: str = "算法流程图",
    output_path: str = "figures/algorithm_flowchart.png",
    figsize: tuple = (10, 8),
    dpi: int = 300,
):
    """使用 matplotlib.patches 生成精确算法流程图"""
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
    import numpy as np

    fig, ax = plt.subplots(figsize=figsize)
    font_family = 'Noto Sans CJK SC'

    # 计算节点位置（网格布局）
    n_steps = len(steps)
    cols = 2
    rows = (n_steps + cols - 1) // cols

    node_w, node_h = 3.5, 1.2
    gap_x, gap_y = 1.5, 1.5

    positions = {}
    for i, step in enumerate(steps):
        col = i % cols
        row = i // cols
        x = col * (node_w + gap_x) + gap_x
        y = (rows - 1 - row) * (node_h + gap_y) + gap_y
        positions[step['id']] = (x + node_w/2, y + node_h/2)

        # 绘制节点
        is_decision = step.get('type') == 'decision'
        boxstyle = 'round,pad=0.1'
        color = '#FFF3E0' if is_decision else '#E3F2FD'
        edge = '#D35400' if is_decision else '#1565C0'

        rect = FancyBboxPatch(
            (x, y), node_w, node_h, boxstyle=boxstyle,
            facecolor=color, edgecolor=edge, linewidth=2
        )
        ax.add_patch(rect)

        label = f"{step['text']}\n{step.get('vars', '')}"
        ax.text(x + node_w/2, y + node_h/2, label, ha='center', va='center',
                fontsize=8, fontfamily=font_family, color='#212121')

    # 绘制箭头
    for r in relationships:
        x1, y1 = positions[r[0]]
        x2, y2 = positions[r[1]]
        label = r[2] if len(r) > 2 else ''
        ax.annotate(label, xy=(x2, y2 + node_h/2), xytext=(x1, y1 - node_h/2),
                   arrowprops=dict(arrowstyle='->', color='#37474F', lw=1.5,
                                  connectionstyle='arc3,rad=0.1'),
                   fontsize=7, fontfamily=font_family, color='#1565C0', ha='center')

    ax.set_xlim(0, cols * (node_w + gap_x) + gap_x)
    ax.set_ylim(0, rows * (node_h + gap_y) + gap_y)
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, fontsize=14, fontfamily=font_family, fontweight='bold', pad=15)

    plt.tight_layout()
    fig.savefig(output_path, dpi=dpi, bbox_inches='tight', facecolor='white')
    plt.close()
    return output_path
```

---

## 统一接口

```python
def generate_diagram(
    diagram_type: str,
    **kwargs,
) -> str:
    """
    统一图表生成接口

    Parameters
    ----------
    diagram_type : "algorithm"
    **kwargs : 传递给具体生成函数的参数
    """
    generators = {
        "algorithm": generate_algorithm_flowchart,
    }

    if diagram_type not in generators:
        raise ValueError(f"未知图表类型: {diagram_type}，可选: {list(generators.keys())}")
    return generators[diagram_type](**kwargs)
```


---

## 硬性约束

1. 所有图表必须使用**中文标签和图例**（国赛要求）或英文标签（美赛要求）
2. 算法流程图必须**结合本题变量**，不能放通用流程图
3. 输出格式：PNG（300dpi）
4. 图题格式：`图X 图表标题`（X 为自动编号或手动指定）
5. 配色：蓝色系为主，橙色系为判断节点，灰色系为背景
6. 字体：Noto Sans CJK SC（中文）+ DejaVu Sans（英文/数字混排）
7. **框架图、架构图、Pipeline 图统一使用 matplotlib.patches 方案**（像素级精确控制，参考项目中的 s5_diagrams_pro.py（matplotlib.patches 像素级精确控制方案））
## 回归测试覆盖

本 Skill 的回归测试用例位于 `training/evolution/regression_cases.json`:

| 用例ID | 问题类型 | 验证内容 |
|--------|---------|---------|
| RT-001 | A题 |  |
| RT-002 | B题 |  |
| RT-003 | C题 |  |
| RT-004 | 通用 |  |
| RT-005 | 通用 |  |

## 泛化约束

- **当前版本**: v1.0
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v?
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v?
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`


## 学习历史

> 本 Skill 受学习机制 v3.0 守护。每次进化前必须通过回归测试和安全检查。
> **当前版本**: v?

| 日期 | 训练 | 触发缺口 | 缺口ID | 变更摘要 |
|------|------|---------|--------|---------|
| 暂无 | - | - | - | - |

## 泛化约束

- **当前版本**: v?
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
