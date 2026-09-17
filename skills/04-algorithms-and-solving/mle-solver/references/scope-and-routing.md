# 规则作用域、优先级与上游接收

> **R1/R2 authority override:** 阶段 0 模型选择已移交 `model-selection`。S3 入口必须加载 `problem_structure.json`、`candidate_portfolio.json`、`selection_verdict.json`，且门禁为 `ALLOW_FORMULATION`；旧 `method_routing.json` 与本文历史默认表无选择权。S3 只产出待验证模型，不能发布或自证；S4 的独立、哈希绑定四态门禁拥有下游放行权。

## 内容索引

  - 泛化约束与反过拟合（v9 随附，2023D题训练教训）
    - v9 规则不适用清单
    - v9 规则（L2 条件硬约束）
  - 泛化约束与反过拟合（v8 随附，2023A题教训）
    - v8 规则不适用清单
    - v8 规则（引用 problem-analyzer v13 L2 条件硬约束）
  - 规则优先级体系
  - 源码出处
  - 工作流
  - 阶段0.5：加载 S1 分析结果
    - 加载内容
    - 对后续阶段的影响

## 泛化约束与反过拟合（v9 随附，2023D题训练教训）

**核心原则**：v9 新增的"强制约束"来源于 2023D题（圈养湖羊空间利用率）训练数据。v9 规则分为两类：
- **离散约束+仿真视界**：适用于 B题/C题中涉及离散资源分配和时间序列仿真的场景。A题连续参数、信号处理、图像处理**不适用**。
- **预案集框架**：适用于所有随机优化问题（含 A题随机场景），不限于 B题/C题。

**题型互斥检查（代码生成前强制执行）**：
```
# v9 规则作用域 Gate 0（题型互斥）
if problem_type in ("信号处理", "图像处理"):
    SKIP v9_discrete_constraint  # 信号/图像不使用离散资源约束
    SKIP v9_horizon_check_for_LCM  # 信号采样周期 ≠ 羊栏生命周期

# v9 离散约束 Gate 1（子类型互斥）
if problem_type == "A题物理/工程" and not has_discrete_resources:
    SKIP v9_discrete_constraint  # A题连续参数（厚度/速度/温度）使用连续优化
# else: ENABLE v9_discrete_constraint for B题/C题/A题整数变量

# v9 视界检查 Gate 2（场景特征匹配）
if has_time_series_simulation:
    ENABLE v9_horizon_check  # 全部题型的时间序列仿真均需检查
```

### v9 规则不适用清单

| v9 规则 | 不适用的问题类型 | 应使用的替代方法 |
|---------|----------------|----------------|
| 离散变量整数约束 | A题连续参数/信号/图像/纯统计 | 连续优化方法（梯度/SQP/L-BFGS-B） |
| 仿真视界LCM检查 | 静态优化/稳态分析/确定性规划 | 标准静态求解方法 |
| 多阶段随机控制预案集 | 确定性优化/无随机因素 | 确定性优化方法 |

### v9 规则（L2 条件硬约束）

> 以下规则仅在 Gate 检查通过后生效。

| 规则 | 层级 | 核心要求 | 禁止 | 适用题型 |
|------|:----:|---------|------|---------|
| 整数约束 | L2 [COND] | 离散变量使用整数规划/整数网格搜索 | 连续优化输出小数给离散变量 | B题/C题/A题整数变量 |
| 仿真视界 | L2 [COND] | 仿真视界 ≥ LCM(关键周期) × N_cycles | 单年截断(365天) | 全部时间序列仿真 |
| 预案集框架 | L2 [COND] | "观测-决策-执行"闭环，≥3场景预案 | 静态配置替代动态预案 | 全部随机优化问题 |

**不适用场景**：A题连续参数 → 连续优化；信号/图像 → 标准方法；静态优化 → 确定性方法。

## 泛化约束与反过拟合（v8 随附，2023A题教训）


**核心原则**：v8 新增的"强制约束"来源于 2023A题（定日镜场优化），**仅适用于 A题-几何光学子类型**。B题、C题、信号处理、图像处理、以及 A题的非光学子类型（流体力学、热传导、结构力学等）**完全不适用** v8 规则。

**题型互斥检查（代码生成前强制执行）**：
```
if problem_type != "A题物理/工程" or physics_subtype != "geometric_optics":
    SKIP_ALL_V8_RULES  # 不生成任何 v8 相关代码
    return  # 使用 v7 及之前的方法模板
```

### v8 规则不适用清单

| v8 规则 | 不适用的问题类型 | 应使用的替代方法 |
|---------|----------------|----------------|
| 蒙特卡洛光线追迹 | B题/C题/信号/图像/流体/结构/热学 | 对应问题的标准求解方法 |
| 同心圆密排+高度耦合 | 非圆形区域布局、B题/C题 | 网格搜索/线性规划/整数规划 |
| PSO粒子数≥100 | 低维优化(<5维)、B题/C题 | 梯度方法(SQP/L-BFGS-B)/小规模PSO |
| 高斯光斑能量分布 | 非光学截断问题、B题/C题 | 均匀分布/经验分布 |
| 外部基准验证 | B题/C题/信号/图像/纯理论A题 | 交叉验证/统计检验/标准测试集 |


### v8 规则（引用 problem-analyzer v13 L2 条件硬约束）

> **详细定义见 `problem-analyzer` SKILL.md 的"规则优先级体系"章节。**
> 以下规则仅在 `problem_type=A题物理/工程 AND physics_subtype=geometric_optics` 时通过 Gate 检查后生效。

| 规则 | 层级 | 核心要求 | 禁止 |
|------|:----:|---------|------|
| 光线追迹 | L2 | Möller-Trumbore 蒙特卡洛光线追迹 | 参数化密度模型 |
| 同心圆密排 | L2 | Concentric Circle Packing (h_k=αR_k+β) | 简单径向交错 |
| PSO参数 | L2 | 粒子≥100, 迭代≥200, 或双层规划 | 小规模PSO直接搜索>5维空间 |
| 高斯光斑 | L2 | 2D Gaussian 能量分布 | 均匀光斑假设 |
| 外部基准 | L2 | ≥1个实际工程基准对比 | 仅内部蒙特卡洛验证 |

**不适用场景**：B题/C题/信号/图像/流体/结构/热学/声学/电磁波 — 使用对应领域的标准方法。
**代码模板**：AHP/模糊综合评价/SVM/GA/Optuna 等模板已移至 `references/code_templates/`（使用时按需加载）。

## 规则优先级体系

本 Skill 遵循全局三层分级体系（详见 `problem-analyzer` SKILL.md）：

- **L1 全局硬约束** `[HARD]`：始终生效 — 如 S1→S7 顺序、paper_macros 绑定
- **L2 条件硬约束** `[COND]`：Gate 检查通过后生效 — 如 v8 A题规则
- **L3 软建议** `[SOFT]`：推荐但允许偏离 — 如代码风格建议

所有硬约束在代码生成前统一检查，L2 规则在非匹配题型中自动跳过。



**v7 新增能力：**
- **无魔法数字原则 (No Magic Numbers)**：所有数值常量必须从问题参数或 S1 上下文推导，禁止硬编码
- **多方法一致性诊断（非门禁）**：若已运行 N>=2 种独立方法，可记录差异并调查其原因；任何固定差异百分比仅是题目特定诊断参数，不能单独生成 PASS/FAIL，也不能替代共同偏差、错误 estimand、基线和外样本检查。
- **代码-上下文绑定 (Code-Context Binding)**：生成代码必须显式引用 S1 参数，禁止孤立代码块

**v6 新增能力：**
- 评价类方法代码模板: AHP/模糊综合评价/灰色关联/DEA/组合赋权
- 预测类高阶方法: SVM回归/分类、混合效应模型、生存分析、Optuna超参自动调优
- 优化类高阶方法: 强化学习(DQN/PPO)、GA+fmincon混合求解策略
- 机理类高阶模型: GAM(广义加性模型)、系统动力学(SD)、PINN(物理信息神经网络)参考

<HARD-GATE>
代码生成后，**必须**在本地执行并验证通过：
1. 无 Traceback、无 SyntaxError、无 IndentationError
2. 所有 S1 硬断言（hard_assertions）必须通过
3. 物理合理性检查必须通过（v3: 含高度不变性等X约束检查）
4. 模型-现实交叉验证必须通过
5. v3新增: 目标函数光滑性验证（优化方法选择前）

任一未通过，必须进入 Debug 回路修正。不得输出未经验证的代码。
</HARD-GATE>

## 源码出处

`usail-hkust/LLM-MM-Agent`，核心 Prompt 蒸馏自 `MMAgent/prompt/template.py` 中的 `TASK_CODING_PROMPT`、`TASK_CODING_DEBUG_PROMPT`、`TASK_RESULT_PROMPT`、`TASK_RESULT_WITH_CODE_PROMPT`、`TASK_ANSWER_PROMPT`。

---

## 工作流

```
用户输入（数模问题 + 数据 + S1分析结果）
    │
    ▼
阶段0: 模型选择（导入 model_selection_guide 决策框架）
    ├── 0.5: 加载 S1 分析结果（v7: 硬断言清单 + 第一性原理审查 + 等X约束 + 目标函数光滑性预判 + 15种问题类型路由）
    │
    ▼
阶段1: 消化输入（理解任务描述、建模公式、数据上下文）
    ├── 1.5: 约束映射——将基本约束方程转化为代码中的断言语句
    │
    ▼
阶段2: 代码生成（MLE-Solver / Programmer 角色）
    ├── 2.5: 代码-物理一致性检查（代码是否真正实现了物理约束？）
    │
    ▼
阶段3: 执行验证 ──失败──→ Debug 修正（Evaluator / Critic 角色）
    │                        │
    │ 成功                    │ 失败类型扩展：
    ▼                        │   - 语法/运行时错误
    ├── 3.5: 硬断言验证      │   - 硬断言失败
    │                        │   - 物理不合理
    ├── 3.6: 物理合理性检查  │ ← 任一失败均触发修正
    │                        │
    ▼                        │
阶段4: 结果解释 ──────────────┘
    ├── 4.5: 模型-现实交叉验证
    │
    ▼
阶段5: 结论分析（含偏差分析）+ 代码结构提取
    ├── 5.5: 生成验证报告（断言结果 + 合理性检查 + 交叉验证）
    └── 失败时：触发 systematic-debugging → 通知 problem-analyzer 反思
```

---

## 阶段0.5：加载 S1 分析结果

在模型选择之后、消化输入之前，**必须**从 problem-analyzer（S1）的输出中加载以下信息：

### 加载内容

```python
import json
from pathlib import Path

def load_s1_analysis():
    """
    从 pipeline 中加载 S1（problem-analyzer）的分析结果。
    
    必须加载的字段：
    - hard_assertions: 硬断言清单（必须逐条验证）
    - first_principles_review: 第一性原理审查结果（基本约束方程 + 简化审查）
    - self_attack_results: 假设自攻击测试结果（哪些是高风险假设）
    - method_selection: 方法选择结果（推荐方法 + 物理保真度标注）
    - sub_problems: 子问题分解（含 physical_entity_type）
    """
    required = {
        "hard_assertions": "hard_assertions.json",
        "method_selection": "method_routing.json",
        "sub_problems": "problem_graph.json",
        "first_principles_review": "analysis_report.json",
        "self_attack_results": "assumption_risk_register.json",
    }
    missing = [path for path in required.values() if not Path(path).exists()]
    if missing:
        raise FileNotFoundError(f"S1 必需产物缺失: {missing}")
    return {
        key: json.loads(Path(path).read_text(encoding="utf-8"))
        for key, path in required.items()
    }
```

### 对后续阶段的影响

| S1 字段 | 影响的阶段 | 用途 |
|--------|----------|------|
| `hard_assertions` | 阶段1.5、3.5 | 转化为代码断言，求解后逐条验证 |
| `first_principles_review.fundamental_constraints` | 阶段1.5、2.5 | 确保代码实现了基本约束方程 |
| `first_principles_review.simplification_review` | 阶段0、2.5 | 确认采用的方法已通过审查（非 REJECTED） |
| `self_attack_results` | 阶段4.5、5 | 高风险假设必须在灵敏度分析中覆盖 |
| `method_selection` | 阶段0 | 确认推荐方法及其物理保真度 |
| `sub_problems[].physical_entity_type` | 阶段2.5 | 触发针对性的物理约束检查 |

---
