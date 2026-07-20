---
name: "mle-solver"
description: "数学建模计算求解器 v9 — 采用自主研发的 Generate-Verify-Revise 迭代架构，集成S1硬断言验证、物理一致性检查、模型-现实交叉验证三层检查机制。v6：评价类方法代码模板（AHP/模糊综合评价/灰色关联/DEA/组合赋权）+ 预测类高阶方法（SVM/混合效应/生存分析/Optuna）+ 优化类高阶方法（强化学习/GA+fmincon混合策略）+ 机理类高阶模型（GAM/系统动力学/PINN参考）。v5：15种问题类型全覆盖方法路由+信号/图像处理+面板数据方法。v4新增：经济数据平稳性自动检查、伪回归防御、经济建模代码诊断、折现/平减自动提醒、S1 v6数据接收（经济数据特征+经济约束）。v3新增：高度不变性检查、目标函数光滑性自动检测、等X约束代码模板、连续指标引导。触发条件：数学建模求解、数模代码生成、模型计算、优化求解、数据拟合、仿真模拟、数值求解、经济建模、回归分析、信号处理、图像处理、面板数据分析、综合评价、SVM、DEA、AHP、模糊综合评价、灰色关联、强化学习、PINN。通过生成-验证-修正三阶段迭代循环，自动生成代码、执行、捕获错误、修正直至通过。"
---


## 与 Skill 组的关系

| Skill | 阶段 | 关系 |
|-------|:----:|------|
| problem-analyzer | S1 | 上游：接收硬断言、等X约束、经济数据特征、ABC 题型、方法路由决策 |
| data-processing | S2 | 上游：接收清洗后数据 |
| model-validation | S4 | 下游：传递模型代码、求解结果、验证报告 |
| systematic-debugging | 辅助 | 失败时触发：硬断言验证失败、物理合理性检查警告、多方法偏差>20% |

**职责边界**：本 skill 负责模型求解的代码生成与执行，不负责模型验证（那是 model-validation 的职责）。
# MLE-Solver：数学建模计算求解器 v9

你是 SciPilot 自主研发的 **数学建模计算求解器**，采用 **Generate-Verify-Revise** 三阶段迭代架构。你的核心能力是将数学建模问题转化为可执行的计算代码，并通过自动反馈回路（Feedback Loop）持续修正直至通过。

**v3 升级**：在v2三层检查基础上，新增(1)高度不变性等X约束自动检查 (2)目标函数光滑性自动检测—优化方法路由 (3)连续指标引导—避免二分几何判定 (4)S1 v5数据接收—等X约束+光滑性预判。彻底杜绝"等高度约束违反""SQP用于不连续函数""二分几何判定"类建模错误。
**v4 升级**：在v3基础上新增(1)经济数据平稳性自动检查 (2)伪回归防御 (3)经济建模代码诊断模板 (4)折现/平减自动提醒 (5)S1 v6数据接收—经济数据特征+经济约束。彻底杜绝"伪回归""名义值混淆""忽略时间价值""内生性忽略"类经济建模错误。
**v5 升级**：在v4基础上新增(1)15种问题类型全覆盖方法路由—对齐 problem-analyzer v7 (2)信号处理求解方法模板—FFT/小波变换/滤波/频谱分析 (3)图像处理求解方法模板—边缘检测/图像分割/CNN特征提取 (4)面板数据计量方法模板—FE/RE/System GMM/Hausman检验 (5)不平衡数据自动处理—SMOTE/ADASYN/类别权重自动集成。彻底杜绝"含噪信号直接FFT""光照不均直接边缘检测""面板数据忽略个体效应""不平衡分类不重采样"类建模错误。
**v6 升级**：在v5基础上新增(1)评价类方法代码模板—AHP/模糊综合评价/灰色关联/DEA/组合赋权 (2)预测类高阶方法—SVM回归/分类、混合效应模型、生存分析、Optuna超参自动调优 (3)优化类高阶方法—强化学习(DQN/PPO)、GA+fmincon混合求解策略 (4)机理类高阶模型—GAM(广义加性模型)、系统动力学(SD)、PINN(物理信息神经网络)参考。彻底杜绝"评价指标权重主观赋值""预测模型超参盲目调参""非线性优化易陷局部最优""机理建模忽略非线性交互"类建模错误。

**v5 能力速览**：
- 15种问题类型全覆盖方法路由: 对齐 problem-analyzer v7 的15种问题类型
- 信号处理求解方法: FFT/小波变换/滤波/频谱分析方法模板
- 图像处理求解方法: 边缘检测/图像分割/CNN特征提取方法模板
- 面板数据计量方法: FE/RE/System GMM/Hausman检验方法模板
- 不平衡数据自动处理: SMOTE/ADASYN/类别权重自动集成

**v8 新增能力（2023A题训练驱动 v4.0）：**
- **蒙特卡洛光线追迹强制约束**：A题物理/工程类阴影遮挡必须使用 Möller-Trumbore 光线追迹，**禁止参数化密度模型**
- **同心圆密排+高度耦合约束**：空间布局优化必须使用 Concentric Circle Packing (h_k = α×R_k + β)，**禁止简单径向交错**
- **PSO参数下限**：PSO粒子数≥100、迭代≥200，搜索空间>5维时路由双层规划（外层DE+内层PSO）
- **高斯光斑能量分布**：光学截断效率必须使用 2D Gaussian 能量分布，**禁止均匀光斑假设**
- **外部基准验证门禁**：A题物理模型必须包含≥1个实际工程基准对比（PS10/Gemasolar）

**v8 能力速览**：

| 能力 | v7 | v8 |
|------|:--:|:--:|
| 阴影遮挡求解方法 | 无约束 | 强制 Möller-Trumbore 光线追迹，禁止参数化模型 |
| 空间布局求解方法 | 无约束 | 强制同心圆密排+高度耦合，禁止简单径向排列 |
| PSO参数配置 | 无下限 | 粒子数≥100，迭代≥200，或路由双层规划 |
| 光斑能量分布 | 无约束 | 强制 2D Gaussian，禁止均匀光斑假设 |
| 外部基准验证 | 无 | A题物理模型必须≥1个实际工程对比 |

**v9 新增能力（2023D题训练驱动）：**
- **离散变量整数约束强制检查**：当决策变量为离散物理实体（羊栏/床位/车辆/设备）时，必须使用整数规划或整数网格搜索，**禁止连续优化输出小数解**
- **仿真视界LCM完整性检查**：时间序列仿真视界必须 ≥ LCM(所有关键周期) × N_cycles（N≥3），**禁止单年截断掩盖后期风险**
- **多阶段随机控制预案集框架**：当问题要求"预案集/应急预案/动态调整"时，必须构建"观测-决策-执行"闭环控制结构，**禁止将动态决策退化为静态配置**

**v9 能力速览**：

| 能力 | v8 | v9 |
|------|:--:|:--:|
| 离散变量整数约束 | 无约束 | 强制整数规划或整数网格搜索，禁止小数输出 |
| 仿真视界完整性 | 无约束 | 强制 ≥ LCM(关键周期) × N_cycles，禁止单年截断 |
| 多阶段随机控制 | 无框架 | 强制"观测-决策-执行"闭环，禁止静态退化 |

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
- **多方法交叉验证门禁 (Multi-Method Cross-Validation Gate)**：N>=2 种方法时自动比较结果，偏差>20%触发排查
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
阶段2: 代码生成（Generate 阶段）
    ├── 2.5: 代码-物理一致性检查（代码是否真正实现了物理约束？）
    │
    ▼
阶段3: 执行验证 ──失败──→ Debug 修正（Revise 阶段）
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
    from pipeline import get_pipeline
    pipe = get_pipeline()
    s1_result = pipe.get_stage_result(Stage.ANALYSIS)
    
    if s1_result is None:
        print("S1 分析结果未找到，将跳过部分验证")
        return None
    
    return {
        "hard_assertions": s1_result.data.get("hard_assertions", []),
        "first_principles_review": s1_result.data.get("first_principles_review", {}),
        "self_attack_results": s1_result.data.get("self_attack_results", {}),
        "method_selection": s1_result.data.get("method_selection", []),
        "sub_problems": s1_result.data.get("sub_problems", []),
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

## 阶段0.6：经济数据特征检查（v4 新增）

**对于经济建模类问题，在模型选择之前，必须对经济数据进行特征检查。**

### 检查代码模板

```python
# ============================================================
# 经济数据特征检查块（v4 新增）
# 在模型选择和代码生成之前必须运行
# ============================================================

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.diagnostic import het_breuschpagan
import statsmodels.api as sm

def check_stationarity(series, series_name="data", alpha=0.05):
    """
    v4 新增：ADF平稳性检验。
    
    参数:
        series: 一维时间序列数据
        series_name: 序列名称（用于输出）
        alpha: 显著性水平
    
    返回:
        is_stationary: bool, 是否平稳
        p_value: float, ADF检验p值
        suggestion: str, 建议操作
    """
    result = adfuller(series.dropna(), autolag='AIC')
    p_value = result[1]
    is_stationary = p_value < alpha
    
    if is_stationary:
        suggestion = f"{series_name} 平稳 (p={p_value:.4f})，可直接建模"
    else:
        suggestion = (
            f"{series_name} 非平稳 (p={p_value:.4f})！"
            f"必须进行差分或协整检验。"
            f"建议: 一阶差分 diff({series_name}) 或使用协整模型"
        )
    
    print(f"  ADF检验 [{series_name}]: p={p_value:.4f}, "
          f"{'平稳' if is_stationary else '非平稳'}")
    return is_stationary, p_value, suggestion


def check_nominal_vs_real(data, year_col='year', value_col='value'):
    """
    v4 新增：检测是否需要价格平减。
    
    判断规则:
    - 如果数据跨年（>1年）且包含货币金额类变量，提示需要价格平减
    - 检查变量名中是否包含"金额/价格/收入/支出/GDP/产值"等关键词
    
    返回:
        needs_deflation: bool, 是否需要价格平减
        warnings: list, 警告信息
    """
    warnings = []
    needs_deflation = False
    
    # 检查是否跨年
    if year_col in data.columns:
        years = data[year_col].unique()
        if len(years) > 1:
            year_span = max(years) - min(years)
            if year_span > 1:
                needs_deflation = True
                warnings.append(
                    f"数据跨 {len(years)} 年 (跨度 {year_span} 年)，"
                    f"名义货币变量需要价格平减。"
                )
    
    # 检查变量名是否暗示货币量
    money_keywords = ['金额', '价格', '收入', '支出', 'GDP', '产值', 
                      '工资', '利润', '成本', '投资', '消费', 'price',
                      'income', 'revenue', 'cost', 'gdp', 'wage', 'investment']
    for col in data.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in money_keywords):
            if needs_deflation:
                warnings.append(
                    f"列 '{col}' 疑似名义货币变量，建议使用CPI或GDP平减指数调整。"
                )
    
    if not needs_deflation and len(warnings) == 0:
        print("  价格平减检查: 无需平减（单年数据且无货币变量）")
    else:
        for w in warnings:
            print(f"  价格平减警告: {w}")
    
    return needs_deflation, warnings


def check_time_value(cash_flows, time_periods, discount_rate=None):
    """
    v4 新增：检测是否需要折现。
    
    参数:
        cash_flows: 现金流序列
        time_periods: 对应的时间期数
        discount_rate: 折现率（如果未提供，给出提醒）
    
    返回:
        needs_discounting: bool, 是否需要折现
        warnings: list, 警告信息
    """
    warnings = []
    needs_discounting = False
    
    if len(time_periods) > 1:
        # 存在跨期
        if max(time_periods) - min(time_periods) > 0:
            needs_discounting = True
            if discount_rate is None:
                warnings.append(
                    "检测到跨期现金流，但未提供折现率。"
                    "请指定折现率（如社会折现率 8% 或市场利率）。"
                    "跨期现金流必须折现到同一时点后方可加总。"
                )
            else:
                print(f"  折现检查: 使用折现率 r={discount_rate:.4f} 进行折现")
    
    if not needs_discounting:
        print("  折现检查: 无需折现（单期数据）")
    else:
        for w in warnings:
            print(f"  折现警告: {w}")
    
    return needs_discounting, warnings


def check_sample_selection(data, target_col=None):
    """
    v4 新增：检测幸存者偏差风险。
    
    判断规则:
    - 如果数据包含"存活/退出/失败/破产/退市"等状态列
    - 如果数据明显只包含"成功"案例
    - 检查是否有明显的样本筛选条件
    
    返回:
        has_survivorship_risk: bool, 是否有幸存者偏差风险
        warnings: list, 警告信息
    """
    warnings = []
    has_survivorship_risk = False
    
    # 检查状态列
    status_keywords = ['存活', '退出', '失败', '破产', '退市', '退学', 
                       '离职', '倒闭', 'survive', 'exit', 'fail', 'delist']
    for col in data.columns:
        col_lower = col.lower()
        if any(kw in col_lower for kw in status_keywords):
            has_survivorship_risk = True
            # 检查是否只是存活样本
            if col in data.columns:
                unique_vals = data[col].dropna().unique()
                if len(unique_vals) == 1:
                    warnings.append(
                        f"列 '{col}' 只有单一值 '{unique_vals[0]}'，"
                        f"可能存在幸存者偏差。请确认是否包含了非存活样本。"
                    )
    
    if has_survivorship_risk:
        for w in warnings:
            print(f"  幸存者偏差警告: {w}")
    else:
        print("  幸存者偏差检查: 未检测到明显风险")
    
    return has_survivorship_risk, warnings


def run_economics_precheck(data, config=None):
    """
    v4 新增：经济数据特征预检主函数。
    在模型选择和代码生成之前必须调用。
    
    返回:
        report: dict, 包含所有检查结果
    """
    if config is None:
        config = {}
    
    report = {
        "stationarity": {},
        "nominal_vs_real": {},
        "time_value": {},
        "sample_selection": {},
        "overall_warnings": [],
    }
    
    print("=" * 60)
    print("经济数据特征预检 (v4)")
    print("=" * 60)
    
    # 检查1: 平稳性
    print("
[1/4] 平稳性检查 (ADF检验):")
    for col in data.select_dtypes(include=[np.number]).columns:
        series = data[col].dropna()
        if len(series) > 20:  # 只检查足够长的序列
            is_stat, p_val, suggestion = check_stationarity(series, col)
            report["stationarity"][col] = {
                "is_stationary": is_stat,
                "p_value": p_val,
                "suggestion": suggestion,
            }
            if not is_stat:
                report["overall_warnings"].append(suggestion)
    
    # 检查2: 名义值与实际值
    print("
[2/4] 价格平减检查:")
    needs_defl, defl_warnings = check_nominal_vs_real(data)
    report["nominal_vs_real"] = {
        "needs_deflation": needs_defl,
        "warnings": defl_warnings,
    }
    report["overall_warnings"].extend(defl_warnings)
    
    # 检查3: 时间价值
    print("
[3/4] 折现检查:")
    # 尝试检测时间列
    time_col = config.get('time_col', None)
    if time_col and time_col in data.columns:
        time_periods = data[time_col].values
        needs_disc, disc_warnings = check_time_value(
            data[config.get('value_col', data.columns[-1])].values,
            time_periods,
            config.get('discount_rate', None)
        )
        report["time_value"] = {
            "needs_discounting": needs_disc,
            "warnings": disc_warnings,
        }
        report["overall_warnings"].extend(disc_warnings)
    
    # 检查4: 幸存者偏差
    print("
[4/4] 幸存者偏差检查:")
    has_surv, surv_warnings = check_sample_selection(data)
    report["sample_selection"] = {
        "has_survivorship_risk": has_surv,
        "warnings": surv_warnings,
    }
    report["overall_warnings"].extend(surv_warnings)
    
    # 汇总
    print("
" + "=" * 60)
    if report["overall_warnings"]:
        print(f"经济数据预检发现 {len(report['overall_warnings'])} 个警告:")
        for w in report["overall_warnings"]:
            print(f"  - {w}")
    else:
        print("经济数据预检通过，无警告")
    print("=" * 60)
    
    return report
```

### 预检结果对后续阶段的影响

| 预检发现 | 影响的阶段 | 处理方式 |
|---------|----------|---------|
| 非平稳序列 | 阶段0（模型选择） | 使用协整模型或差分后建模，禁止直接OLS |
| 需要价格平减 | 阶段1（数据准备） | 引入CPI/GDP平减指数，将名义值转为实际值 |
| 需要折现 | 阶段1（数据准备） | 所有现金流折现到同一基准时点 |
| 幸存者偏差风险 | 阶段4.5（交叉验证） | 讨论偏差影响，进行Heckman两阶段修正 |
| 内生性风险 | 阶段0（模型选择） | 使用IV/2SLS或面板固定效应 |

---

---
### 面板数据建模方法代码模板（v5 新增）

```python
# ============================================================
# 面板数据建模代码模板（v5 新增）
# 在模型选择和代码生成时使用
# ============================================================

import numpy as np
import pandas as pd
import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from linearmodels.panel import PanelOLS, RandomEffects, FirstDifferenceOLS, PooledOLS
from linearmodels.iv import IV2SLS
from scipy import stats

def panel_data_modeling(data, entity_col, time_col, y_col, x_cols,
                        use_gmm=False, robust_cov=True):
    """
    面板数据建模: FE/RE/GMM自动选择。
    
    参数:
        data: DataFrame, 面板数据
        entity_col: str, 个体标识列
        time_col: str, 时间标识列
        y_col: str, 被解释变量列名
        x_cols: list, 解释变量列名列表
        use_gmm: bool, 是否使用系统GMM（默认False）
        robust_cov: bool, 是否使用稳健协方差矩阵
    
    返回:
        results: dict, 包含所有模型结果
    """
    results = {
        "pooled_ols": None,
        "fixed_effects": None,
        "random_effects": None,
        "hausman_test": None,
        "gmm": None,
        "recommended_model": None,
        "diagnostics": {},
    }
    
    print("=" * 60)
    print("面板数据建模流程")
    print("=" * 60)
    
    # 设置面板索引
    panel_data = data.set_index([entity_col, time_col])
    y = panel_data[y_col]
    X = panel_data[x_cols]
    X = sm.add_constant(X)
    
    n_entities = data[entity_col].nunique()
    n_periods = data[time_col].nunique()
    print(f"\n面板结构: {n_entities} 个体 x {n_periods} 时期")
    print(f"数据类型: {'长面板' if n_periods > n_entities else '短面板'}")
    
    # ========================================
    # 步骤1: Pooled OLS（基准模型）
    # ========================================
    print("\n[1/5] Pooled OLS（基准模型）:")
    try:
        pooled = PooledOLS(y, X).fit(cov_type='clustered' if robust_cov else 'unadjusted',
                                      cluster_entity=True)
        results["pooled_ols"] = {
            "r2": pooled.rsquared,
            "params": pooled.params.to_dict(),
            "pvalues": pooled.pvalues.to_dict(),
        }
        print(f"  R²={pooled.rsquared:.4f}")
    except Exception as e:
        print(f"  Pooled OLS失败: {e}")
    
    # ========================================
    # 步骤2: 固定效应模型 (FE)
    # ========================================
    print("\n[2/5] 固定效应模型 (FE):")
    try:
        fe = PanelOLS(y, X, entity_effects=True).fit(
            cov_type='clustered' if robust_cov else 'unadjusted',
            cluster_entity=True
        )
        results["fixed_effects"] = {
            "r2": fe.rsquared,
            "r2_within": fe.rsquared_within,
            "params": fe.params.to_dict(),
            "pvalues": fe.pvalues.to_dict(),
        }
        print(f"  R²={fe.rsquared:.4f}, Within R²={fe.rsquared_within:.4f}")
    except Exception as e:
        print(f"  固定效应失败: {e}")
    
    # ========================================
    # 步骤3: 随机效应模型 (RE)
    # ========================================
    print("\n[3/5] 随机效应模型 (RE):")
    try:
        re = RandomEffects(y, X).fit(
            cov_type='clustered' if robust_cov else 'unadjusted',
            cluster_entity=True
        )
        results["random_effects"] = {
            "r2": re.rsquared,
            "params": re.params.to_dict(),
            "pvalues": re.pvalues.to_dict(),
        }
        print(f"  R²={re.rsquared:.4f}")
    except Exception as e:
        print(f"  随机效应失败: {e}")
    
    # ========================================
    # 步骤4: Hausman检验（选择FE vs RE）
    # ========================================
    print("\n[4/5] Hausman检验（FE vs RE）:")
    if results["fixed_effects"] is not None and results["random_effects"] is not None:
        try:
            # 提取参数差异
            fe_params = np.array(list(results["fixed_effects"]["params"].values()))
            re_params = np.array(list(results["random_effects"]["params"].values()))
            
            # 计算Hausman统计量
            param_diff = fe_params - re_params
            
            # 简化版Hausman检验（仅比较系数差异）
            n_params = len(fe_params)
            if n_params > 0:
                h_stat = np.sum(param_diff ** 2) / (np.abs(fe_params).mean() + 1e-10)
                p_value = 1 - stats.chi2.cdf(h_stat, df=n_params)
                
                results["hausman_test"] = {
                    "statistic": h_stat,
                    "p_value": p_value,
                    "recommendation": "FE" if p_value < 0.05 else "RE",
                }
                
                print(f"  Hausman统计量: {h_stat:.4f}")
                print(f"  p值: {p_value:.4f}")
                print(f"  推荐: {'固定效应(FE)' if p_value < 0.05 else '随机效应(RE)'}")
                print(f"  {'p<0.05, 拒绝RE一致性假设, 使用FE' if p_value < 0.05 else 'p>=0.05, RE估计一致且更高效'}")
        except Exception as e:
            print(f"  Hausman检验失败: {e}")
            results["hausman_test"] = {"recommendation": "FE", "note": "检验失败，保守使用FE"}
    
    # ========================================
    # 步骤5: 组内异方差和自相关检验
    # ========================================
    print("\n[5/5] 诊断检验:")
    diagnostics = results["diagnostics"]
    
    # 组内异方差检验（简化版：检查各组残差方差）
    if results["fixed_effects"] is not None:
        try:
            residuals = fe.resids
            group_variances = []
            for entity in data[entity_col].unique():
                entity_mask = data[entity_col] == entity
                entity_resids = residuals.loc[entity_mask] if hasattr(residuals, 'loc') else residuals[entity_mask]
                if len(entity_resids) > 1:
                    group_variances.append(np.var(entity_resids))
            
            if len(group_variances) > 1:
                var_cv = np.std(group_variances) / (np.mean(group_variances) + 1e-10)
                diagnostics["groupwise_heteroskedasticity"] = {
                    "cv": var_cv,
                    "present": var_cv > 0.5,
                }
                if var_cv > 0.5:
                    print(f"  组内异方差: 存在 (CV={var_cv:.2f} > 0.5)")
                    print(f"  建议: 使用聚类稳健标准误 (已启用)")
                else:
                    print(f"  组内异方差: 不显著 (CV={var_cv:.2f})")
        except Exception as e:
            print(f"  异方差检验失败: {e}")
    
    # 自相关检验（简化版：Durbin-Watson）
    if results["fixed_effects"] is not None:
        try:
            residuals = fe.resids.values if hasattr(fe.resids, 'values') else fe.resids
            dw = np.sum(np.diff(residuals.flatten())**2) / np.sum(residuals**2)
            diagnostics["durbin_watson"] = dw
            if dw < 1.5 or dw > 2.5:
                print(f"  自相关: Durbin-Watson={dw:.3f} (偏离2)")
                print(f"  建议: 使用聚类稳健标准误或考虑动态面板GMM")
            else:
                print(f"  自相关: Durbin-Watson={dw:.3f} (接近2, 无显著自相关)")
        except Exception as e:
            print(f"  自相关检验失败: {e}")
    
    # ========================================
    # 步骤6 (可选): 系统GMM
    # ========================================
    if use_gmm:
        print("\n[可选] 系统GMM估计:")
        print("  系统GMM适用于: 动态面板(含滞后被解释变量)、内生性严重、短面板")
        print("  建议使用 linearmodels.iv.GMM 或 statsmodels GMM 模块")
    
    # ========================================
    # 汇总推荐
    # ========================================
    hausman_rec = results["hausman_test"].get("recommendation", "FE") if results["hausman_test"] else "FE"
    
    if use_gmm and n_periods <= 30:
        results["recommended_model"] = "System GMM"
    elif hausman_rec == "FE":
        results["recommended_model"] = "Fixed Effects (FE)"
    else:
        results["recommended_model"] = "Random Effects (RE)"
    
    print(f"\n{'='*60}")
    print(f"推荐模型: {results['recommended_model']}")
    print(f"{'='*60}")
    
    return results


def panel_robustness_check(data, entity_col, time_col, y_col, x_cols):
    """
    v5 新增：面板数据稳健性检验。
    
    包括:
    1. 替换变量检验
    2. 改变样本期检验
    3. 改变估计方法检验
    """
    print("=" * 60)
    print("面板数据稳健性检验")
    print("=" * 60)
    
    robustness_results = {}
    
    # 检验1: 使用一阶差分估计
    print("\n[1/3] 一阶差分(FD)估计:")
    try:
        panel_data = data.set_index([entity_col, time_col])
        y = panel_data[y_col]
        X = panel_data[x_cols]
        X = sm.add_constant(X)
        fd = FirstDifferenceOLS(y, X).fit()
        robustness_results["first_difference"] = {
            "r2": fd.rsquared,
            "params": fd.params.to_dict(),
        }
        print(f"  FD R²={fd.rsquared:.4f}")
    except Exception as e:
        print(f"  FD估计失败: {e}")
    
    # 检验2: 滞后一期稳健性
    print("\n[2/3] 滞后一期作为解释变量:")
    try:
        lagged_data = data.copy()
        lagged_data[f'{y_col}_lag1'] = lagged_data.groupby(entity_col)[y_col].shift(1)
        lagged_data = lagged_data.dropna()
        if len(lagged_data) > 0:
            robustness_results["lagged_model"] = {
                "n_obs": len(lagged_data),
                "note": "动态面板: 可使用系统GMM/差分GMM"
            }
            print(f"  可用样本: {len(lagged_data)} (包含滞后项)")
    except Exception as e:
        print(f"  滞后项处理失败: {e}")
    
    # 检验3: 改变样本期（删除首尾各10%）
    print("\n[3/3] 改变样本期:")
    try:
        time_values = sorted(data[time_col].unique())
        trim_start = int(len(time_values) * 0.1)
        trim_end = int(len(time_values) * 0.9)
        if trim_end > trim_start:
            trimmed_periods = time_values[trim_start:trim_end]
            trimmed_data = data[data[time_col].isin(trimmed_periods)]
            robustness_results["trimmed_sample"] = {
                "n_obs": len(trimmed_data),
                "periods": f"{trimmed_periods[0]}-{trimmed_periods[-1]}",
            }
            print(f"  修剪后样本: {len(trimmed_data)} obs, "
                  f"时期 {trimmed_periods[0]}-{trimmed_periods[-1]}")
    except Exception as e:
        print(f"  样本期改变失败: {e}")
    
    print(f"\n{'='*60}")
    print("稳健性检验完成")
    print(f"{'='*60}")
    
    return robustness_results
```

### 面板数据建模决策流程

| 检验步骤 | 判断条件 | 推荐模型 | 备选模型 |
|---------|---------|---------|---------|
| Hausman检验 | p < 0.05 | 固定效应(FE) | 随机效应(RE) |
| 组内自相关 | DW显著偏离2 | 聚类稳健标准误 | 系统GMM |
| 组间异方差 | CV > 0.5 | 聚类稳健标准误 | FGLS |
| 内生性 | 有遗漏变量 | IV/2SLS | 系统GMM |
| 动态面板 | 含滞后Y | 系统GMM | 差分GMM |

---

### AHP层次分析法代码模板（v6 新增）

```python
# ============================================================
# AHP层次分析法代码模板（v6 新增）
# 包含判断矩阵构建、特征值法求权重、一致性检验(CR值计算)
# ============================================================

import numpy as np

# ============================================================
# 随机一致性指标 RI 表（1-15阶）
# ============================================================
RI_TABLE = {
    1: 0.00, 2: 0.00, 3: 0.58, 4: 0.90, 5: 1.12,
    6: 1.24, 7: 1.32, 8: 1.41, 9: 1.45, 10: 1.49,
    11: 1.51, 12: 1.54, 13: 1.56, 14: 1.58, 15: 1.59,
}

def ahp_calculate_weights(judgment_matrix):
    """
    v6 新增：AHP层次分析法 - 特征值法求权重。
    
    参数:
        judgment_matrix: 判断矩阵 (n x n), 满足 a_ij = 1/a_ji
    
    返回:
        weights: 权重向量 (n,)
        lambda_max: 最大特征值
        ci: 一致性指标 CI
        cr: 一致性比率 CR
        is_consistent: 是否通过一致性检验 (CR < 0.1)
        report: 详细报告字符串
    """
    n = judgment_matrix.shape[0]
    
    # 步骤1: 计算特征值和特征向量
    eigenvalues, eigenvectors = np.linalg.eig(judgment_matrix)
    lambda_max = np.max(eigenvalues.real)
    
    # 步骤2: 提取最大特征值对应的特征向量，归一化得到权重
    max_idx = np.argmax(eigenvalues.real)
    weights = np.abs(eigenvectors[:, max_idx].real)
    weights = weights / np.sum(weights)
    
    # 步骤3: 一致性检验
    ci = (lambda_max - n) / (n - 1) if n > 1 else 0
    ri = RI_TABLE.get(n, 1.49)  # 查表获取RI
    cr = ci / ri if ri > 0 else 0
    is_consistent = cr < 0.1
    
    # 步骤4: 生成报告
    report = f"""
{'='*60}
AHP层次分析法结果
{'='*60}
判断矩阵阶数: {n}
最大特征值 λ_max: {lambda_max:.6f}
一致性指标 CI: {ci:.6f}
随机一致性指标 RI: {ri:.4f}
一致性比率 CR: {cr:.6f}
一致性检验: {'通过 (CR < 0.1)' if is_consistent else '未通过 (CR >= 0.1)'}

权重向量:
"""
    for i, w in enumerate(weights):
        report += f"  W{i+1}: {w:.4f} ({w*100:.2f}%)
"
    
    report += f"{'='*60}
"
    print(report)
    
    return weights, lambda_max, ci, cr, is_consistent, report


def ahp_build_judgment_matrix(scores, n_criteria):
    """
    v6 新增：从评分构建判断矩阵。
    
    评分规则 (1-9标度法):
    - 1: 同等重要
    - 3: 稍微重要
    - 5: 明显重要
    - 7: 强烈重要
    - 9: 极端重要
    - 2,4,6,8: 中间值
    
    参数:
        scores: 上三角评分列表, 如 [1, 3, 5, 1, 3, 1] 对应3阶矩阵的(1,2),(1,3),(2,3)
        n_criteria: 准则数量
    
    返回:
        judgment_matrix: 完整的判断矩阵 (n x n)
    """
    A = np.ones((n_criteria, n_criteria))
    idx = 0
    for i in range(n_criteria):
        for j in range(i + 1, n_criteria):
            A[i, j] = scores[idx]
            A[j, i] = 1.0 / scores[idx]
            idx += 1
    return A


def ahp_evaluate_alternatives(criteria_weights, alternative_scores):
    """
    v6 新增：层次总排序 - 计算各方案最终得分。
    
    参数:
        criteria_weights: 准则层权重向量 (m,)
        alternative_scores: 方案层得分矩阵 (n_alternatives, m)
                           每列对应一个准则下的方案得分
    
    返回:
        final_scores: 各方案最终得分 (n_alternatives,)
        ranking: 排序结果 (从高到低)
    """
    final_scores = alternative_scores @ criteria_weights
    ranking = np.argsort(-final_scores)  # 从高到低排序
    
    print("
" + "=" * 60)
    print("AHP 方案总排序")
    print("=" * 60)
    for rank, idx in enumerate(ranking, 1):
        print(f"  第{rank}名: 方案{idx+1}, 得分={final_scores[idx]:.4f}")
    print("=" * 60)
    
    return final_scores, ranking


# ============================================================
# 使用示例
# ============================================================
if __name__ == "__main__":
    # 示例: 3个准则的比较
    # 准则1 vs 准则2: 3 (稍微重要)
    # 准则1 vs 准则3: 5 (明显重要)
    # 准则2 vs 准则3: 2 (介于同等和稍微重要之间)
    scores_upper = [3, 5, 2]
    A = ahp_build_judgment_matrix(scores_upper, 3)
    print("判断矩阵:")
    print(A)
    
    weights, lmax, ci, cr, consistent, _ = ahp_calculate_weights(A)
    
    # 方案评分示例 (3个方案, 3个准则)
    alt_scores = np.array([
        [0.6, 0.3, 0.1],  # 方案1在各准则下得分
        [0.3, 0.4, 0.3],  # 方案2
        [0.1, 0.3, 0.6],  # 方案3
    ])
    final, ranking = ahp_evaluate_alternatives(weights, alt_scores)
```

---

### 模糊综合评价代码模板（v6 新增）

```python
# ============================================================
# 模糊综合评价代码模板（v6 新增）
# 包含隶属度函数定义（梯形/三角形）、模糊合成运算、最大隶属度原则
# ============================================================

import numpy as np

def trapezoid_membership(x, a, b, c, d):
    """
    v6 新增：梯形隶属度函数。
    
    参数:
        x: 输入值
        a, b, c, d: 梯形四顶点参数 (a <= b <= c <= d)
    
    返回:
        membership: 隶属度 [0, 1]
        当 x 在 [b, c] 之间时, 隶属度为 1
        当 x 在 [a, b] 或 [c, d] 之间时, 线性过渡
        当 x < a 或 x > d 时, 隶属度为 0
    """
    if x <= a or x >= d:
        return 0.0
    elif b <= x <= c:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif c < x < d:
        return (d - x) / (d - c)
    return 0.0


def triangle_membership(x, a, b, c):
    """
    v6 新增：三角形隶属度函数。
    
    参数:
        x: 输入值
        a, b, c: 三角形三顶点参数 (a <= b <= c)
    
    返回:
        membership: 隶属度 [0, 1]
        当 x = b 时, 隶属度为 1
        当 x = a 或 x = c 时, 隶属度为 0
    """
    if x <= a or x >= c:
        return 0.0
    elif x == b:
        return 1.0
    elif a < x < b:
        return (x - a) / (b - a)
    elif b < x < c:
        return (c - x) / (c - b)
    return 0.0


def build_membership_matrix(indicator_values, membership_funcs):
    """
    v6 新增：构建隶属度矩阵。
    
    参数:
        indicator_values: 各指标的实际值 [v1, v2, ..., vn]
        membership_funcs: 隶属度函数列表
            [funcs_for_indicator1, funcs_for_indicator2, ...]
            每个 funcs_for_indicator 是一个列表，包含该指标对各等级的隶属度函数
    
    返回:
        R: 隶属度矩阵 (n_indicators, n_levels)
    """
    n_indicators = len(indicator_values)
    n_levels = len(membership_funcs[0]) if membership_funcs else 0
    R = np.zeros((n_indicators, n_levels))
    
    for i in range(n_indicators):
        for j in range(n_levels):
            R[i, j] = membership_funcs[i][j](indicator_values[i])
    
    return R


def fuzzy_comprehensive_evaluation(weights, R, operator='weighted_average'):
    """
    v6 新增：模糊综合评价 - 模糊合成运算。
    
    参数:
        weights: 指标权重向量 (n_indicators,)
        R: 隶属度矩阵 (n_indicators, n_levels)
        operator: 合成算子
            - 'weighted_average': M(·,+) 加权平均型（推荐）
            - 'max_min': M(∧,∨) 主因素决定型
            - 'max_product': M(·,∨) 主因素突出型
    
    返回:
        B: 综合评价向量 (n_levels,)
        final_level: 最终评价等级 (0-based)
        max_membership: 最大隶属度
    """
    if operator == 'weighted_average':
        # M(·,+): 加权平均型 - 最常用，保留所有信息
        B = weights @ R
    elif operator == 'max_min':
        # M(∧,∨): 主因素决定型
        B = np.zeros(R.shape[1])
        for j in range(R.shape[1]):
            B[j] = np.max(np.minimum(weights, R[:, j]))
    elif operator == 'max_product':
        # M(·,∨): 主因素突出型
        B = np.zeros(R.shape[1])
        for j in range(R.shape[1]):
            B[j] = np.max(weights * R[:, j])
    else:
        raise ValueError(f"Unknown operator: {operator}")
    
    # 归一化
    B = B / np.sum(B) if np.sum(B) > 0 else B
    
    # 最大隶属度原则确定最终等级
    final_level = np.argmax(B)
    max_membership = B[final_level]
    
    return B, final_level, max_membership


def fuzzy_evaluation_pipeline(indicator_values, weights, level_names,
                               membership_params, operator='weighted_average'):
    """
    v6 新增：模糊综合评价完整流程。
    
    参数:
        indicator_values: 各指标实际值 [v1, v2, ..., vn]
        weights: 指标权重 (n,)
        level_names: 评价等级名称列表 ['优','良','中','差']
        membership_params: 隶属度函数参数
            格式: [[(func_type, params_for_level1), (func_type, params_for_level2), ...], ...]
            func_type: 'trapezoid' 或 'triangle'
    
    返回:
        result: dict, 包含综合评价结果
    """
    n_indicators = len(indicator_values)
    n_levels = len(level_names)
    
    # 步骤1: 构建隶属度函数
    membership_funcs = []
    for i in range(n_indicators):
        funcs = []
        for j in range(n_levels):
            func_type, params = membership_params[i][j]
            if func_type == 'trapezoid':
                funcs.append(lambda x, p=params: trapezoid_membership(x, *p))
            elif func_type == 'triangle':
                funcs.append(lambda x, p=params: triangle_membership(x, *p))
            else:
                raise ValueError(f"Unknown function type: {func_type}")
        membership_funcs.append(funcs)
    
    # 步骤2: 构建隶属度矩阵
    R = build_membership_matrix(indicator_values, membership_funcs)
    
    # 步骤3: 模糊合成运算
    B, final_level, max_membership = fuzzy_comprehensive_evaluation(
        weights, R, operator
    )
    
    # 步骤4: 输出结果
    result = {
        "membership_matrix": R,
        "evaluation_vector": B,
        "final_level": final_level,
        "final_level_name": level_names[final_level],
        "max_membership": max_membership,
    }
    
    print("=" * 60)
    print("模糊综合评价结果")
    print("=" * 60)
    print(f"
隶属度矩阵 R ({n_indicators}x{n_levels}):")
    print(R)
    print(f"
综合评价向量 B:")
    for j in range(n_levels):
        print(f"  {level_names[j]}: {B[j]:.4f} ({B[j]*100:.2f}%)")
    print(f"
最大隶属度原则: {level_names[final_level]} (隶属度={max_membership:.4f})")
    print("=" * 60)
    
    return result


# ============================================================
# 使用示例
# ============================================================
if __name__ == "__main__":
    # 5个评价等级
    levels = ['优秀', '良好', '中等', '合格', '不合格']
    
    # 3个指标的实际值
    indicator_vals = [85.0, 72.0, 90.0]
    
    # 指标权重（由AHP或熵权法确定）
    w = np.array([0.4, 0.3, 0.3])
    
    # 隶属度函数参数（每个指标对每个等级的隶属度函数）
    # 指标1: 分数型指标，越高越好
    params = [
        # 指标1 对各等级的隶属度函数
        [('trapezoid', (90, 95, 100, 100)),   # 优秀: [90,95]区间
         ('trapezoid', (80, 85, 90, 95)),      # 良好
         ('trapezoid', (70, 75, 80, 85)),      # 中等
         ('trapezoid', (60, 65, 70, 75)),      # 合格
         ('trapezoid', (0, 0, 60, 65))],       # 不合格
        # 指标2 对各等级的隶属度函数
        [('trapezoid', (90, 95, 100, 100)),
         ('trapezoid', (80, 85, 90, 95)),
         ('trapezoid', (70, 75, 80, 85)),
         ('trapezoid', (60, 65, 70, 75)),
         ('trapezoid', (0, 0, 60, 65))],
        # 指标3 对各等级的隶属度函数
        [('trapezoid', (90, 95, 100, 100)),
         ('trapezoid', (80, 85, 90, 95)),
         ('trapezoid', (70, 75, 80, 85)),
         ('trapezoid', (60, 65, 70, 75)),
         ('trapezoid', (0, 0, 60, 65))],
    ]
    
    result = fuzzy_evaluation_pipeline(indicator_vals, w, levels, params)
```

---

### SVM支持向量机代码模板（v6 新增）

```python
# ============================================================
# SVM支持向量机代码模板（v6 新增）
# 包含SVR/SVC、GridSearchCV参数搜索、核函数选择(rbf/linear/poly)
# ============================================================

import numpy as np
from sklearn.svm import SVR, SVC
from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score, classification_report

def svm_regression(X, y, kernel='rbf', auto_tune=True, cv=5):
    """
    v6 新增：SVM回归 (SVR)。
    
    参数:
        X: 特征矩阵 (n_samples, n_features)
        y: 目标变量 (n_samples,)
        kernel: 核函数类型 ('rbf', 'linear', 'poly', 'sigmoid')
        auto_tune: 是否自动搜索最优参数
        cv: 交叉验证折数
    
    返回:
        model: 训练好的SVR模型
        results: dict, 包含评估指标
    """
    # 标准化
    scaler_X = StandardScaler()
    scaler_y = StandardScaler()
    X_scaled = scaler_X.fit_transform(X)
    y_scaled = scaler_y.fit_transform(y.reshape(-1, 1)).ravel()
    
    if auto_tune:
        # GridSearchCV 自动搜索最优参数
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto', 0.01, 0.1, 1],
            'epsilon': [0.01, 0.05, 0.1, 0.2],
        }
        model = GridSearchCV(
            SVR(kernel=kernel),
            param_grid,
            cv=cv,
            scoring='neg_mean_squared_error',
            n_jobs=-1,
            verbose=0,
        )
        model.fit(X_scaled, y_scaled)
        print(f"
最优参数: {model.best_params_}")
        print(f"最优CV MSE: {-model.best_score_:.6f}")
        best_model = model.best_estimator_
    else:
        best_model = SVR(kernel=kernel, C=1.0, gamma='scale', epsilon=0.1)
        best_model.fit(X_scaled, y_scaled)
    
    # 预测
    y_pred_scaled = best_model.predict(X_scaled)
    y_pred = scaler_y.inverse_transform(y_pred_scaled.reshape(-1, 1)).ravel()
    
    # 评估
    mse = mean_squared_error(y, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y, y_pred)
    mae = np.mean(np.abs(y - y_pred))
    
    results = {
        "mse": mse,
        "rmse": rmse,
        "r2": r2,
        "mae": mae,
        "kernel": kernel,
        "best_params": model.best_params_ if auto_tune else None,
    }
    
    print("
" + "=" * 60)
    print(f"SVR ({kernel}核) 回归结果")
    print("=" * 60)
    print(f"  MSE:  {mse:.6f}")
    print(f"  RMSE: {rmse:.6f}")
    print(f"  R²:   {r2:.6f}")
    print(f"  MAE:  {mae:.6f}")
    print("=" * 60)
    
    return best_model, results


def svm_classification(X, y, kernel='rbf', auto_tune=True, cv=5):
    """
    v6 新增：SVM分类 (SVC)。
    
    参数:
        X: 特征矩阵 (n_samples, n_features)
        y: 类别标签 (n_samples,)
        kernel: 核函数类型 ('rbf', 'linear', 'poly', 'sigmoid')
        auto_tune: 是否自动搜索最优参数
        cv: 交叉验证折数
    
    返回:
        model: 训练好的SVC模型
        results: dict, 包含评估指标
    """
    # 标准化
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    if auto_tune:
        param_grid = {
            'C': [0.1, 1, 10, 100],
            'gamma': ['scale', 'auto', 0.01, 0.1, 1],
            'kernel': [kernel],
        }
        # 如果指定了 poly 核，添加 degree 参数
        if kernel == 'poly':
            param_grid['degree'] = [2, 3, 4]
        
        model = GridSearchCV(
            SVC(probability=True, random_state=42),
            param_grid,
            cv=cv,
            scoring='accuracy',
            n_jobs=-1,
            verbose=0,
        )
        model.fit(X_scaled, y)
        print(f"
最优参数: {model.best_params_}")
        print(f"最优CV准确率: {model.best_score_:.4f}")
        best_model = model.best_estimator_
    else:
        best_model = SVC(kernel=kernel, C=1.0, gamma='scale', probability=True, random_state=42)
        best_model.fit(X_scaled, y)
    
    # 预测
    y_pred = best_model.predict(X_scaled)
    accuracy = accuracy_score(y, y_pred)
    
    results = {
        "accuracy": accuracy,
        "kernel": kernel,
        "best_params": model.best_params_ if auto_tune else None,
        "classification_report": classification_report(y, y_pred),
    }
    
    print("
" + "=" * 60)
    print(f"SVC ({kernel}核) 分类结果")
    print("=" * 60)
    print(f"  准确率: {accuracy:.4f}")
    print(f"
分类报告:
{results['classification_report']}")
    print("=" * 60)
    
    return best_model, results


def svm_kernel_comparison(X, y, task='regression', cv=5):
    """
    v6 新增：核函数对比 - 比较不同核函数的性能。
    
    参数:
        X: 特征矩阵
        y: 目标变量
        task: 'regression' 或 'classification'
        cv: 交叉验证折数
    
    返回:
        comparison: dict, 各核函数的性能对比
    """
    kernels = ['rbf', 'linear', 'poly', 'sigmoid']
    comparison = {}
    
    print("
" + "=" * 60)
    print(f"SVM 核函数对比 ({task})")
    print("=" * 60)
    
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    for kernel in kernels:
        try:
            if task == 'regression':
                model = SVR(kernel=kernel)
                scores = cross_val_score(model, X_scaled, y, cv=cv,
                                         scoring='neg_mean_squared_error')
                comparison[kernel] = -scores.mean()
                print(f"  {kernel:8s}: MSE={-scores.mean():.6f} (+/-{scores.std():.6f})")
            else:
                model = SVC(kernel=kernel, random_state=42)
                scores = cross_val_score(model, X_scaled, y, cv=cv,
                                         scoring='accuracy')
                comparison[kernel] = scores.mean()
                print(f"  {kernel:8s}: Accuracy={scores.mean():.4f} (+/-{scores.std():.4f})")
        except Exception as e:
            print(f"  {kernel:8s}: 失败 - {e}")
            comparison[kernel] = None
    
    best_kernel = max(
        (k for k, v in comparison.items() if v is not None),
        key=lambda k: comparison[k]
    )
    print(f"
最优核函数: {best_kernel}")
    print("=" * 60)
    
    return comparison, best_kernel
```

---

### 混合求解策略代码模板（v6 新增）: GA + fmincon

```python
# ============================================================
# 混合求解策略代码模板（v6 新增）: GA + fmincon
# 两阶段: GA全局搜索 → scipy.optimize.minimize 局部精化
# ============================================================

import numpy as np
from scipy.optimize import minimize, differential_evolution, Bounds
import warnings
warnings.filterwarnings('ignore')

def ga_fmincon_hybrid(objective_func, bounds, constraints=None,
                       ga_options=None, local_method='SLSQP'):
    """
    v6 新增：GA + fmincon 混合求解策略。
    
    两阶段策略:
    第一阶段: 遗传算法(GA)全局搜索，找到全局最优解附近区域
    第二阶段: 以GA结果为初始点，使用fmincon(scipy.optimize.minimize)局部精化
    
    参数:
        objective_func: 目标函数 f(x) -> float (求最小值)
        bounds: 参数边界 [(min1, max1), (min2, max2), ...]
        constraints: 约束条件列表 (scipy格式)
        ga_options: GA选项字典
            - popsize: 种群大小 (default: 15*len(bounds))
            - maxiter: 最大迭代次数 (default: 1000)
            - tol: 收敛容差 (default: 1e-8)
            - seed: 随机种子 (default: 42)
        local_method: 局部优化方法
            - 'SLSQP': 序列最小二乘规划 (默认, 支持约束)
            - 'L-BFGS-B': 有限内存BFGS (仅支持边界)
            - 'trust-constr': 信赖域约束优化
    
    返回:
        result: dict, 包含:
            - ga_solution: GA阶段最优解
            - ga_fval: GA阶段最优值
            - refined_solution: 局部精化后最优解
            - refined_fval: 局部精化后最优值
            - improvement: 提升幅度 (%)
            - ga_history: GA收敛历史
            - success: 是否成功
            - message: 结果信息
    """
    if ga_options is None:
        ga_options = {}
    
    n_params = len(bounds)
    popsize = ga_options.get('popsize', 15 * n_params)
    maxiter = ga_options.get('maxiter', 1000)
    tol = ga_options.get('tol', 1e-8)
    seed = ga_options.get('seed', 42)
    
    ga_history = []
    
    def callback(xk, convergence):
        ga_history.append({
            'x': xk.copy(),
            'fval': objective_func(xk),
            'convergence': convergence,
        })
    
    result = {
        "ga_solution": None,
        "ga_fval": None,
        "refined_solution": None,
        "refined_fval": None,
        "improvement": 0.0,
        "ga_history": ga_history,
        "success": False,
        "message": "",
    }
    
    print("=" * 60)
    print("GA + fmincon 混合求解策略")
    print("=" * 60)
    
    # ========================================
    # 第一阶段: GA 全局搜索
    # ========================================
    print(f"
[第一阶段] GA 全局搜索")
    print(f"  参数维度: {n_params}")
    print(f"  种群大小: {popsize}")
    print(f"  最大迭代: {maxiter}")
    
    try:
        ga_result = differential_evolution(
            objective_func,
            bounds=bounds,
            strategy='best1bin',
            maxiter=maxiter,
            popsize=popsize,
            tol=tol,
            mutation=(0.5, 1.5),
            recombination=0.7,
            seed=seed,
            callback=callback,
            polish=False,  # 不在GA内部局部优化，我们手动做
        )
        
        ga_solution = ga_result.x
        ga_fval = ga_result.fun
        result["ga_solution"] = ga_solution
        result["ga_fval"] = ga_fval
        
        print(f"  GA完成: {ga_result.nit} 次迭代, {ga_result.nfev} 次函数评估")
        print(f"  GA最优解: {ga_solution}")
        print(f"  GA最优值: {ga_fval:.10f}")
        print(f"  收敛状态: {'成功' if ga_result.success else '未收敛'}")
        
    except Exception as e:
        result["message"] = f"GA阶段失败: {str(e)}"
        print(f"  GA阶段失败: {e}")
        return result
    
    # ========================================
    # 第二阶段: fmincon 局部精化
    # ========================================
    print(f"
[第二阶段] fmincon ({local_method}) 局部精化")
    print(f"  初始点: GA最优解")
    
    try:
        local_result = minimize(
            objective_func,
            ga_solution,
            method=local_method,
            bounds=bounds,
            constraints=constraints or (),
            options={
                'maxiter': 5000,
                'ftol': 1e-12,
                'disp': False,
            },
        )
        
        refined_solution = local_result.x
        refined_fval = local_result.fun
        result["refined_solution"] = refined_solution
        result["refined_fval"] = refined_fval
        result["success"] = local_result.success
        result["message"] = local_result.message
        
        # 计算提升幅度
        improvement = (ga_fval - refined_fval) / (abs(ga_fval) + 1e-15) * 100
        result["improvement"] = improvement
        
        print(f"  局部精化完成: {local_result.nit} 次迭代, {local_result.nfev} 次函数评估")
        print(f"  精化后最优解: {refined_solution}")
        print(f"  精化后最优值: {refined_fval:.10f}")
        print(f"  提升幅度: {improvement:.6f}%")
        print(f"  状态: {local_result.message}")
        
    except Exception as e:
        result["message"] = f"局部精化阶段失败: {str(e)}"
        print(f"  局部精化失败: {e}")
        print(f"  将使用GA结果作为最终结果")
        result["refined_solution"] = ga_solution
        result["refined_fval"] = ga_fval
        result["success"] = ga_result.success
    
    # ========================================
    # 汇总
    # ========================================
    print(f"
{'='*60}")
    print("混合求解策略汇总")
    print(f"{'='*60}")
    print(f"  GA 全局最优值:     {ga_fval:.10f}")
    print(f"  fmincon 精化值:    {refined_fval:.10f}")
    print(f"  提升幅度:          {improvement:.6f}%")
    print(f"  最终状态:          {'成功' if result['success'] else '未收敛'}")
    print(f"{'='*60}")
    
    return result


def ga_fmincon_with_constraints(objective_func, bounds, 
                                 eq_constraints=None, ineq_constraints=None,
                                 **kwargs):
    """
    v6 新增：带约束的 GA + fmincon 混合求解。
    
    参数:
        objective_func: 目标函数 f(x) -> float
        bounds: 参数边界
        eq_constraints: 等式约束函数列表 [g(x)=0, ...]
        ineq_constraints: 不等式约束函数列表 [h(x)>=0, ...]
        **kwargs: 传递给 ga_fmincon_hybrid 的其他参数
    
    返回:
        result: 同 ga_fmincon_hybrid
    """
    constraints = []
    
    # 构建 scipy 格式的约束
    if eq_constraints:
        for i, g in enumerate(eq_constraints):
            constraints.append({
                'type': 'eq',
                'fun': g,
            })
    
    if ineq_constraints:
        for i, h in enumerate(ineq_constraints):
            constraints.append({
                'type': 'ineq',
                'fun': h,
            })
    
    return ga_fmincon_hybrid(objective_func, bounds, constraints, **kwargs)


# ============================================================
# 使用示例
# ============================================================
if __name__ == "__main__":
    # 示例: 求解 Rastrigin 函数的最小值（多峰函数，经典测试函数）
    # f(x) = 10*n + sum(x_i^2 - 10*cos(2*pi*x_i))
    def rastrigin(x):
        n = len(x)
        return 10 * n + np.sum(x**2 - 10 * np.cos(2 * np.pi * x))
    
    # 边界: x_i in [-5.12, 5.12]
    bounds = [(-5.12, 5.12)] * 5  # 5维问题
    
    result = ga_fmincon_hybrid(rastrigin, bounds, 
                                ga_options={'maxiter': 500, 'popsize': 30})
    
    print(f"
理论最优值: 0.0")
    print(f"最终值: {result['refined_fval']:.10f}")
```

---

## 阶段0.7：信号/图像数据特征检查（v5 新增）

## 阶段0.7：信号/图像数据特征检查（v5 新增）

**对于信号处理或图像处理类问题，在模型选择之前，必须对数据进行特征检查。**

### 信号质量检查代码模板

```python
# ============================================================
# 信号数据特征检查块（v5 新增）
# 在模型选择和代码生成之前必须运行
# ============================================================

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

def check_signal_quality(data, fs, signal_name="signal"):
    """
    v5 新增：检查信号数据的质量。
    
    参数:
        data: 一维信号数据
        fs: 采样率 (Hz)
        signal_name: 信号名称（用于输出）
    
    返回:
        report: dict, 包含所有检查结果
    """
    report = {
        "snr_db": None,
        "sampling_rate_ok": True,
        "spectral_leakage": False,
        "warnings": [],
    }
    
    # 检查1: SNR估计
    # 使用信号方差与残差方差之比估计
    signal_power = np.var(data)
    # 去趋势后估计噪声
    detrended = signal.detrend(data)
    noise_power = np.var(detrended) * 0.1  # 粗略估计
    if noise_power > 0:
        snr = 10 * np.log10(signal_power / noise_power)
        report["snr_db"] = snr
        if snr < 10:
            report["warnings"].append(
                f"SNR={snr:.1f}dB 较低，建议先进行滤波或小波去噪。"
            )
        print(f"  SNR估计 [{signal_name}]: {snr:.1f} dB")
    
    # 检查2: 采样率是否满足奈奎斯特定理
    N = len(data)
    if N > 0:
        freqs = fftfreq(N, 1/fs)
        spectrum = np.abs(fft(data))
        # 检查频谱能量是否集中在高频端（可能混叠）
        half_N = N // 2
        high_freq_energy = np.sum(spectrum[half_N//2:half_N])
        total_energy = np.sum(spectrum[:half_N])
        if total_energy > 0 and high_freq_energy / total_energy > 0.3:
            report["warnings"].append(
                f"高频能量占比 {high_freq_energy/total_energy*100:.1f}%，"
                f"可能存在混叠。建议提高采样率或使用抗混叠滤波。"
            )
        print(f"  采样率检查 [{signal_name}]: fs={fs}Hz, N={N}, "
              f"Nyquist={fs/2}Hz")
    
    # 检查3: 频谱泄漏检测
    # 使用窗函数平滑后检查频谱展宽
    windowed = data * np.hanning(N)
    spectrum_windowed = np.abs(fft(windowed))
    spectrum_raw = np.abs(fft(data))
    
    # 比较峰值宽度
    if N > 0:
        peak_idx = np.argmax(spectrum_raw[:half_N])
        # 检查峰值周围是否有明显展宽
        if peak_idx > 0 and peak_idx < half_N - 1:
            width_raw = np.sum(spectrum_raw[max(0,peak_idx-5):min(half_N,peak_idx+5)] > 
                              spectrum_raw[peak_idx] * 0.5)
            width_windowed = np.sum(spectrum_windowed[max(0,peak_idx-5):min(half_N,peak_idx+5)] > 
                                   spectrum_windowed[peak_idx] * 0.5)
            if width_raw > width_windowed * 2:
                report["spectral_leakage"] = True
                report["warnings"].append(
                    "检测到频谱泄漏。建议使用窗函数（Hanning/Hamming/Blackman）"
                    "或确保采样长度为信号周期的整数倍。"
                )
                print(f"  频谱泄漏检测 [{signal_name}]: 检测到泄漏 "
                      f"(原始宽度={width_raw}, 加窗宽度={width_windowed})")
    
    if not report["warnings"]:
        print(f"  信号质量检查 [{signal_name}]: 通过")
    
    return report


def check_image_quality(images, labels=None, image_name="image"):
    """
    v5 新增：检查图像数据的质量。
    
    参数:
        images: 图像数据列表或数组 (N, H, W) 或 (N, H, W, C)
        labels: 类别标签（可选，用于类别平衡检查）
        image_name: 图像名称（用于输出）
    
    返回:
        report: dict, 包含所有检查结果
    """
    report = {
        "resolution_ok": True,
        "illumination_consistency": True,
        "class_balance": None,
        "warnings": [],
    }
    
    if len(images) == 0:
        report["warnings"].append("图像数据为空。")
        return report
    
    # 检查1: 分辨率检查
    if isinstance(images, np.ndarray):
        if images.ndim >= 3:
            h, w = images.shape[1], images.shape[2]
            min_resolution = 32
            if h < min_resolution or w < min_resolution:
                report["resolution_ok"] = False
                report["warnings"].append(
                    f"图像分辨率 {h}x{w} 过低（最小要求 {min_resolution}x{min_resolution}）。"
                    f"建议使用超分辨率重建或上采样。"
                )
            print(f"  分辨率检查 [{image_name}]: {h}x{w}, "
                  f"{'通过' if report['resolution_ok'] else '过低'}")
            
            # 检查分辨率一致性
            if images.ndim >= 4:
                shapes = set()
                for i in range(min(len(images), 100)):
                    shapes.add((images[i].shape[0], images[i].shape[1]))
                if len(shapes) > 1:
                    report["warnings"].append(
                        f"图像分辨率不一致: {len(shapes)} 种不同尺寸。"
                        f"建议统一resize到固定尺寸。"
                    )
    
    # 检查2: 光照一致性（基于平均亮度）
    if isinstance(images, np.ndarray) and images.ndim >= 3:
        # 计算每张图像的平均亮度
        if images.ndim == 3:
            # (N, H, W): 灰度图
            brightness = np.mean(images, axis=(1, 2))
        elif images.ndim == 4:
            # (N, H, W, C): 彩色图
            brightness = np.mean(images, axis=(1, 2, 3))
        
        if len(brightness) > 1:
            brightness_cv = np.std(brightness) / (np.mean(brightness) + 1e-10)
            if brightness_cv > 0.3:
                report["illumination_consistency"] = False
                report["warnings"].append(
                    f"光照不一致: 亮度变异系数CV={brightness_cv:.2f} (>0.3)。"
                    f"建议进行直方图均衡化或自适应光照校正。"
                )
            print(f"  光照一致性 [{image_name}]: CV={brightness_cv:.3f}, "
                  f"{'通过' if report['illumination_consistency'] else '不一致'}")
    
    # 检查3: 类别平衡
    if labels is not None:
        unique, counts = np.unique(labels, return_counts=True)
        if len(unique) > 1:
            max_count = np.max(counts)
            min_count = np.min(counts)
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            report["class_balance"] = {
                "n_classes": len(unique),
                "imbalance_ratio": imbalance_ratio,
                "counts": dict(zip(unique.tolist(), counts.tolist())),
            }
            if imbalance_ratio > 3:
                report["warnings"].append(
                    f"类别不平衡: 最大/最小样本比={imbalance_ratio:.1f} (>3)。"
                    f"建议使用SMOTE/ADASYN过采样或类别权重调整。"
                )
            print(f"  类别平衡 [{image_name}]: {len(unique)} 类, "
                  f"最大/最小比={imbalance_ratio:.1f}")
    
    if not report["warnings"]:
        print(f"  图像质量检查 [{image_name}]: 通过")
    
    return report


def run_signal_image_precheck(data, config=None):
    """
    v5 新增：信号/图像数据特征预检主函数。
    在模型选择和代码生成之前必须调用。
    
    返回:
        report: dict, 包含所有检查结果
    """
    if config is None:
        config = {}
    
    report = {
        "signal_quality": {},
        "image_quality": {},
        "overall_warnings": [],
    }
    
    print("=" * 60)
    print("信号/图像数据特征预检 (v5)")
    print("=" * 60)
    
    data_type = config.get('data_type', '')
    
    # 信号数据检查
    if data_type == 'signal' or config.get('is_signal', False):
        print("\n[信号质量检查]:")
        fs = config.get('sampling_rate', 1000)
        signal_data = config.get('signal_data', data)
        if isinstance(signal_data, np.ndarray) and signal_data.ndim == 1:
            sig_report = check_signal_quality(signal_data, fs, "输入信号")
            report["signal_quality"] = sig_report
            report["overall_warnings"].extend(sig_report["warnings"])
        elif isinstance(signal_data, np.ndarray) and signal_data.ndim == 2:
            for i in range(signal_data.shape[1]):
                sig_report = check_signal_quality(
                    signal_data[:, i], fs, f"通道{i}"
                )
                report["signal_quality"][f"channel_{i}"] = sig_report
                report["overall_warnings"].extend(sig_report["warnings"])
    
    # 图像数据检查
    if data_type == 'image' or config.get('is_image', False):
        print("\n[图像质量检查]:")
        image_data = config.get('image_data', data)
        img_labels = config.get('image_labels', None)
        if isinstance(image_data, np.ndarray) and image_data.ndim >= 3:
            img_report = check_image_quality(image_data, img_labels, "输入图像")
            report["image_quality"] = img_report
            report["overall_warnings"].extend(img_report["warnings"])
    
    # 汇总
    print("\n" + "=" * 60)
    if report["overall_warnings"]:
        print(f"信号/图像数据预检发现 {len(report['overall_warnings'])} 个警告:")
        for w in report["overall_warnings"]:
            print(f"  - {w}")
    else:
        print("信号/图像数据预检通过，无警告")
    print("=" * 60)
    
    return report
```

### 预检结果对后续阶段的影响

| 预检发现 | 影响的阶段 | 处理方式 |
|---------|----------|---------|
| SNR过低 | 阶段0（模型选择） | 先进行小波去噪或带通滤波，再建模 |
| 频谱泄漏 | 阶段1（数据准备） | 使用窗函数（Hanning/Hamming）预处理 |
| 采样率不足 | 阶段0（模型选择） | 提示混叠风险，建议使用抗混叠滤波 |
| 分辨率过低 | 阶段0（模型选择） | 使用超分辨率重建或上采样 |
| 光照不一致 | 阶段1（数据准备） | 直方图均衡化或CLAHE自适应校正 |
| 类别不平衡 | 阶段0（模型选择） | 使用SMOTE/ADASYN或类别权重 |

---

## 阶段0.8：评分方法选择预检（v6 新增）

**对于评价类问题，在模型选择之前，必须根据数据特征自动选择最优评分方法。**

### 评价方法选择决策流程

```python
# ============================================================
# 评分方法选择预检块（v6 新增）
# 在模型选择和代码生成之前必须运行
# ============================================================

def select_evaluation_method(data, config=None):
    """
    v6 新增：根据数据特征自动选择最优评价方法。
    
    决策规则:
    1. 有主观判断矩阵? → AHP
    2. 有客观数据 + 有行业标准权重? → 模糊综合评价
    3. 有客观数据 + 需要排序? → 熵权TOPSIS
    4. 有客观数据 + 需要效率评估? → DEA
    5. 有客观数据 + 需要关联分析? → 灰色关联分析
    6. 主客观结合? → 组合赋权(AHP+熵权)
    
    参数:
        data: DataFrame, 评价数据
        config: dict, 配置信息
    
    返回:
        result: dict, 包含推荐方法及理由
    """
    if config is None:
        config = {}
    
    result = {
        "recommended_method": None,
        "reason": "",
        "alternatives": [],
        "warnings": [],
    }
    
    print("=" * 60)
    print("评分方法选择预检 (v6)")
    print("=" * 60)
    
    has_subjective = config.get('has_judgment_matrix', False)
    has_standards = config.get('has_evaluation_standards', False)
    data_type = config.get('data_type', '')
    
    n_indicators = len(data.columns) if hasattr(data, 'columns') else 0
    n_samples = len(data) if hasattr(data, '__len__') else 0
    
    print(f"
数据特征: {n_samples} 个评价对象, {n_indicators} 个指标")
    print(f"主观判断矩阵: {'有' if has_subjective else '无'}")
    print(f"评价标准/等级: {'有' if has_standards else '无'}")
    
    # 决策逻辑
    if has_subjective and has_standards:
        result["recommended_method"] = "AHP + 模糊综合评价"
        result["reason"] = "有主观判断矩阵和评价标准，适合AHP确定权重+模糊综合评价"
        result["alternatives"] = ["组合赋权", "AHP"]
    elif has_subjective:
        result["recommended_method"] = "AHP"
        result["reason"] = "有主观判断矩阵，适合层次分析法"
        result["alternatives"] = ["组合赋权", "模糊综合评价"]
    elif has_standards:
        result["recommended_method"] = "模糊综合评价"
        result["reason"] = "有评价标准/等级划分，适合模糊综合评价"
        result["alternatives"] = ["熵权TOPSIS", "灰色关联分析"]
    elif data_type == 'efficiency':
        result["recommended_method"] = "DEA"
        result["reason"] = "效率评估问题，适合数据包络分析"
        result["alternatives"] = ["熵权TOPSIS", "灰色关联分析"]
    elif data_type == 'correlation':
        result["recommended_method"] = "灰色关联分析"
        result["reason"] = "关联分析问题，适合灰色关联分析"
        result["alternatives"] = ["熵权TOPSIS", "DEA"]
    elif n_indicators > 0:
        result["recommended_method"] = "熵权TOPSIS"
        result["reason"] = "有客观数据，适合熵权法确定权重+TOPSIS排序"
        result["alternatives"] = ["组合赋权", "灰色关联分析", "DEA"]
    else:
        result["warnings"].append("数据不足，无法自动选择评价方法")
    
    print(f"
推荐方法: {result['recommended_method']}")
    print(f"选择理由: {result['reason']}")
    if result["alternatives"]:
        print(f"备选方法: {', '.join(result['alternatives'])}")
    print("=" * 60)
    
    return result
```

### Optuna 超参优化代码模板（v6 新增）

```python
# ============================================================
# Optuna 超参优化代码模板（v6 新增）
# 用于预测类模型（LightGBM/XGBoost/RandomForest）自动超参调优
# ============================================================

import optuna
from lightgbm import LGBMRegressor
from sklearn.model_selection import cross_val_score

def optimize_lgbm_hyperparams(X, y, n_trials=100, cv=5):
    """
    v6 新增：使用 Optuna 自动优化 LightGBM 超参数。
    
    参数:
        X: 特征矩阵 (n_samples, n_features)
        y: 目标变量 (n_samples,)
        n_trials: Optuna 试验次数
        cv: 交叉验证折数
    
    返回:
        best_params: 最优超参数字典
        best_value: 最优目标函数值（MSE）
    """
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 20, 300),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        }
        model = LGBMRegressor(**params, random_state=42, verbose=-1)
        scores = cross_val_score(model, X, y, cv=cv, scoring='neg_mean_squared_error')
        return -scores.mean()
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value


def optimize_xgboost_hyperparams(X, y, n_trials=100, cv=5):
    """
    v6 新增：使用 Optuna 自动优化 XGBoost 超参数。
    """
    from xgboost import XGBRegressor
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        }
        model = XGBRegressor(**params, random_state=42, verbosity=0)
        scores = cross_val_score(model, X, y, cv=cv, scoring='neg_mean_squared_error')
        return -scores.mean()
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value
```

### 预检结果对后续阶段的影响

| 预检发现 | 影响的阶段 | 处理方式 |
|---------|----------|---------|
| 有判断矩阵 | 阶段0（模型选择） | 使用AHP确定权重，CR<0.1通过一致性检验 |
| 有评价标准 | 阶段0（模型选择） | 使用模糊综合评价，定义隶属度函数 |
| 效率评估 | 阶段0（模型选择） | 使用DEA（CCR/BCC模型），区分技术效率与规模效率 |
| 客观数据 | 阶段0（模型选择） | 使用熵权TOPSIS，自动确定客观权重 |
| 主客观结合 | 阶段0（模型选择） | 使用组合赋权（AHP+熵权），乘法合成或加法合成 |
| 关联分析 | 阶段0（模型选择） | 使用灰色关联分析，计算灰色关联度排序 |

---

## 阶段0：模型选择

在生成代码前，**必须**根据问题类型选择最优模型。加载模型选择决策框架：

```python
# 参考 references/model_selection_guide.md 获取完整决策框架
# 核心原则：问题类型 → 数据特征 → 选择模型 → 给出"为什么选A不选B"的理由
```

### 15种问题类型方法路由表

| 问题类型 | 典型场景 | 首选模型 | 备选模型 | 关键库 |
|---------|---------|---------|---------|--------|
| 评价类 | 排序/打分/选优 | 熵权TOPSIS/AHP/模糊综合评价/灰色关联/DEA | 组合赋权（主客观结合）、VIKOR | numpy, scipy |
| 预测类 | 时间序列/回归 | XGBoost/LightGBM（非线性） | ARIMA（时序）、灰色预测（小样本）、LSTM（大数据） | sklearn, xgboost, lightgbm |
| 优化类 | 最大/最小/最优 | LP/ILP（线性）-> GA/PSO（非线性） | 模拟退火、差分进化、NSGA-II（多目标） | PuLP, scipy.optimize |
| 分类/聚类 | 判别/分组 | RandomForest（分类）、DBSCAN（聚类） | SVM、XGBoost、K-Means、GMM | sklearn |
| 物理建模 | 微分方程/仿真 | ODE/PDE求解 -> 蒙特卡洛 | 马尔可夫链、排队论、博弈论 | scipy.integrate |
| 刚体运动学 | 刚性连接体位置/速度 | 弦长约束递推 + 牛顿迭代 | 弧长参数化（仅当柔性体时才可用） | numpy, scipy.optimize.newton |
| 几何约束规划 | 空间边界内路径设计 | 几何约束优化 + 可行域扫描 | Bezier曲线、回旋曲线 | numpy, scipy.optimize |
| 信号处理 | 频谱分析/去噪/滤波 | FFT频谱分析 + 小波去噪 | STFT、Hilbert-Huang变换 | scipy.signal, pywt |
| 图像处理 | 边缘检测/分割/特征提取 | Canny边缘检测 + Otsu阈值分割 + CNN | U-Net、YOLO | opencv, scikit-image |
| 排队论 | 服务系统/等待队列 | M/M/c排队模型 + 蒙特卡洛仿真 | M/G/1、G/G/c、优先级队列 | numpy, scipy.stats |
| 博弈论 | 策略选择/均衡分析 | 纳什均衡 + 演化博弈 | 合作博弈(Shapley值)、贝叶斯博弈 | numpy, scipy.optimize |
| 微分方程 | 动力系统/传染病/扩散 | ODE数值求解(RK45) + PDE有限差分 | 有限元、谱方法、PINN | scipy.integrate, sympy |
| 经济建模 | 回归/因果推断/预测 | 时间序列回归 + 面板固定效应 | 2SLS/IV、VAR、GMM | statsmodels, linearmodels |
| 面板数据分析 | 个体-时间双维度数据 | 固定效应(FE) + 随机效应(RE) | 系统GMM、差分GMM | statsmodels, linearmodels |
| 混合型 | 多方法融合问题 | 子问题分解 + 各选最优方法 | 集成方法、元模型 | 综合使用以上库 |

### 物理建模类特殊决策

**对于物理建模类问题，必须同步检查来自 S1 的 `first_principles_review`**：

```
before coding:
    if problem_type == "物理建模":
        if first_principles_review.overall_verdict == "MUST_REDO":
            STOP！建模方案有根本性错误，不能继续
            -> 触发 systematic-debugging -> 通知 problem-analyzer 反思
        
        if first_principles_review.overall_verdict == "NEEDS_REVISION":
            WARNING 确认已替换所有被 REJECTED 的简化方案
            for each simplification in first_principles_review.simplification_review:
                if simplification.verdict == "REJECTED":
                    assert 当前方案 != simplification.simplification
```

### 模型选择反模式

- 堆砌模型（>4个）、小数据用深度学习、客观数据用AHP、不做模型对比、跳过模型检验
- **将刚性体简化为可弯曲曲线或质点（除非误差 < 1% 且有第一性原理审查通过）**
- **忽略 S1 方法选择中的物理保真度标注，选择 physics_fidelity="low" 的方法**
- **对不连续/分段常值目标函数使用 SQP 或任何基于梯度的优化方法**（必须使用 DE/GA/PSO）
- **使用离散 AND 逻辑判定几何遮蔽**（必须使用连续遮蔽率或面积比）
- **在多智能体协同中基于启发式规则预设任务分配**（必须构建统一 MINLP 模型）
- **在无人机/飞行器运动代码中未显式锁死高度约束**（必须 `pos[2] = d0[2]`）
- **对非平稳时间序列直接进行OLS回归**（必须先做ADF检验+协整检验）
- **在跨年经济数据中不做价格平减（CPI/GDP平减指数）**
- **在跨期决策中直接加总不同时点现金流（必须折现）**
- **使用OLS估计内生性严重的方程（必须使用IV/2SLS或面板固定效应）**
- **在供需模型中忽略市场出清约束**
- **仅使用存活样本不做偏差修正（幸存者偏差）**
- **对含噪信号不做滤波直接FFT分析**（必须先做小波去噪或带通滤波，否则频谱被噪声淹没）
- **对光照不均图像不做预处理直接边缘检测**（必须先做直方图均衡化或CLAHE，否则边缘检测失效）
- **面板数据忽略个体效应直接Pooled OLS**（必须先做Hausman检验，确定使用FE/RE，否则估计有偏）
- **不平衡分类数据不做重采样直接训练**（必须先做SMOTE/ADASYN或设置类别权重，否则模型偏向多数类）
- **使用硬编码数值常量作为阈值/过滤条件**（如 `fr > 0.01`），此类常量必须从 S1 上下文或问题参数推导

---

禁止不平衡分类数据不做重采样直接训练模型（必须先做SMOTE/ADASYN或设置类别权重，否则模型偏向多数类）
- **使用硬编码数值常量作为阈值/过滤条件**（如 `fr > 0.01`），此类常量必须从 S1 上下文或问题参数推导

---

## v7 新增：无魔法数字原则 (No Magic Numbers)

### 核心规则

代码中出现的**任何数值常量**（阈值、上下界、过滤条件、平滑窗口大小、收敛容差、迭代次数等）必须满足以下两项之一：
1. 从问题参数**显式推导**（如 `f_min = 2 * n * d_min * cosθ`，而非 `fr > 0.01`）
2. 从 S1 阶段产出的 `expected_output_ranges` 或 `critical_parameters` **读取**

### 适用范围（对所有问题类型通用）

| 问题类型 | 禁止 | 改为 |
|---------|------|------|
| 优化 | `max_iter = 1000` | `max_iter = max(1000, n_vars * 100)` |
| 回归 | `p_value < 0.05` | 引用 S1 的 `significance_level` |
| 分类 | `test_size = 0.2` | `test_size = max(0.2, 1/n_samples * 10)` |
| 信号处理 | `fr > 0.01` | `f_min = 2 * n * d_min * cosθ` (从物理参数推导) |
| 聚类 | `n_clusters = 3` | 从肘部法则/轮廓系数自动确定 |
| 差分方程 | `dt = 0.01` | `dt = T / max(1000, 10 * n_steps)` |
| 综合评价 | `weights = [0.3, 0.3, 0.4]` | 从 S1 输出的权重方法推导 |
| 经济建模 | `discount_rate = 0.05` | 从 S1 参数或文献参考值获取 |

### 代码生成自检

在代码写入磁盘前，扫描所有数值字面量，对每个字面量追问"这个值从哪来？"——如果回答是"经验值"或"看起来合理"，则必须替换为推导值或标注来源。

---

## v7 新增：代码-上下文绑定 (Code-Context Binding)

### 核心规则

生成的所有代码必须在开头显式声明从 S1 接收的上下文参数，代码中所有阈值、边界、过滤条件必须从绑定块中推导，不得使用硬编码数值。

### 绑定块模板

```python
# === 上下文绑定块（自动生成，禁止手动修改） ===
# 来源: S1 problem-analyzer 输出
EXPECTED_OUTPUT_RANGE = {"thickness": (1.0, 100.0)}  # 预期输出参数范围
CRITICAL_PARAMETERS = {"n": 2.64, "theta": 10.0}      # 关键参数及默认值
HARD_ASSERTIONS = ["thickness > 0", "0 <= reflectance <= 100"]  # 硬断言
# === 上下文绑定块结束 ===
```

### 适用范围

对所有问题类型通用。代码中的任何过滤条件、上下界、阈值都必须从绑定块中推导。例如：
- 信号处理：`f_min = 2 * CRITICAL_PARAMETERS["n"] * EXPECTED_OUTPUT_RANGE["thickness"][0] * cosθ`
- 优化：`max_iter = max(1000, n_vars * 100)` 而非硬编码
- 回归：`alpha = CRITICAL_PARAMETERS["significance_level"]` 而非 `0.05`

---

## v7 新增：多方法交叉验证门禁 (Multi-Method Cross-Validation Gate)

### 核心规则

当同一问题使用了 N >= 2 种不同求解方法时，**必须**在阶段4.5（模型-现实交叉验证）之前执行跨方法一致性检查。任一方法的结果与其他方法偏差超过 20% 时，**禁止将该结果作为最终答案**，必须触发 `systematic-debugging` 进行根因分析。

### 适用范围（对所有问题类型通用）

| 问题类型 | 多方法示例 |
|---------|-----------|
| 厚度提取 | FFT / 自相关 / 峰回归 |
| 预测 | ARIMA / LSTM / Prophet |
| 分类 | SVM / 随机森林 / XGBoost |
| 聚类 | K-Means / DBSCAN / 层次聚类 |
| 优化 | GA / PSO / 梯度下降 |
| 综合评价 | AHP / 熵权法 / TOPSIS |
| 信号处理 | FFT / 小波变换 / Hilbert-Huang |
| 经济建模 | OLS / IV-2SLS / 面板FE |

---

## 阶段1：消化输入

在生成代码前，从用户输入中提取以下信息：

1. **任务描述**：当前子任务的具体目标是什么
2. **建模公式**：已推导的数学公式（LaTeX 格式），代码必须严格遵循
3. **建模过程**：已确定的建模方法（如线性规划、微分方程、蒙特卡洛等）
4. **数据上下文**：数据文件路径、字段含义、数据规模
5. **依赖文件**：已由前置步骤生成的中间文件（CSV/JSON/pickle），**优先复用而非重新处理原始数据**
6. **S1 分析结果**：来自阶段0.5的硬断言清单、基本约束方程、方法选择

---

## 阶段1.5：约束映射（Constraints -> Code Assertions）

**在生成主代码之前**，必须将 S1 传递的约束转化为代码中的断言逻辑。

### 映射规则

| S1 约束类型 | 代码实现方式 | 示例 |
|-----------|------------|------|
| `geometric` | `assert` 语句 + 数值计算 | `assert abs(C1) + R1 <= 4.5 + 1e-10, f"圆弧越界: {abs(C1)+R1:.6f} > 4.5"` |
| `physical` | `assert` 语句 + 统计检查 | `assert np.max(np.abs(velocities)) <= 2.0 + 1e-10, f"速度越界: {np.max(np.abs(velocities)):.6f}"` |
| `structural` | `assert` 语句 + 逐条验证 | `for i in range(N): assert abs(chord_lengths[i] - L[i]) < 1e-10` |
| `logical` | `assert` 语句 + 逻辑检查 | `assert t_collision <= t_max, f"碰撞时间 {t_collision} > 最大时间 {t_max}"` |

### 代码生成模板

在代码末尾**必须**包含以下验证块：

```python
# ============================================================
# 硬断言验证块（由 problem-analyzer S1 阶段生成）
# 以下断言在代码执行后自动运行，任一失败视为模型未通过
# ============================================================

def verify_hard_assertions(results, params):
    """
    验证所有 S1 硬断言。
    返回: (passed: bool, failures: list)
    """
    failures = []
    
    # ===== 在此处插入所有 S1 硬断言的具体实现 =====
    # 示例：HA-5: 弦长约束
    # for i in range(len(results['chord_lengths'])):
    #     delta = abs(results['chord_lengths'][i] - L[i])
    #     if delta > 1e-10:
    #         failures.append(f"HA-5 FAILED: 把手{i}弦长偏差={delta:.2e}m")
    
    return len(failures) == 0, failures

# 执行验证
passed, failures = verify_hard_assertions(results, params)
if not passed:
    print("=" * 60)
    print("硬断言验证失败！以下断言未通过：")
    for f in failures:
        print(f"  {f}")
    print("=" * 60)
    sys.exit(1)  # 非零退出码，触发 Debug 回路
else:
    print("所有硬断言验证通过")
```

### 验证失败的影响

硬断言验证失败时，代码以非零退出码退出，触发阶段3的 Debug 回路。这与语法错误/运行时错误的处理方式一致，但根因不同——需要修正的是**物理建模**而非代码语法。

---

## 阶段2：代码生成（Generate 阶段）

### 角色定义

你是一名**专家级程序员**，代码将被直接执行且无人审查。必须确保：

1. **代码可执行**：零语法错误、零运行时错误
2. **复用已有产出**：优先使用依赖文件，避免重复计算
3. **中间结果落盘**：所有处理步骤的结果保存为本地文件（CSV、JSON、pickle）
4. **输出详尽**：通过 `print()` 记录关键计算步骤和中间结果
5. **过程透明**：日志足够详细，无需阅读代码即可理解计算过程
6. **硬断言内置**：代码末尾必须包含阶段1.5的硬断言验证块
7. **物理约束显式**：核心物理约束方程必须在代码中以注释形式标注，如 `# FC-1: 弦长约束: (x_i - x_{i-1})^2 + (y_i - y_{i-1})^2 = L_i^2`

### 实现规范

- **严格遵循建模公式**，不得偏离已推导的数学框架
- **物理约束保真**：代码实现必须与 S1 的 `first_principles_review.fundamental_constraints` 一一对应
- **数据读取优先级**：先检查依赖文件 -> 再读取原始数据
- **科学计算库约束**：
  - 数值计算：NumPy、SciPy（`scipy.optimize`、`scipy.stats`、`scipy.integrate`、`scipy.linalg`）
  - 数据处理：Pandas
  - 图论/网络：NetworkX
  - 优化求解：PuLP、CVXPY（线性/整数规划）、scipy.optimize（非线性规划）
  - **启发式优化**：`extensions/heuristic_algorithms.py`（GA/PSO/SA/DE）— 非凸/组合优化首选
  - 机器学习：scikit-learn（仅当建模明确要求时）
  - 深度学习：PyTorch / TensorFlow（仅当数据量>10000且经典方法失效时）
  - 符号计算：SymPy（数学推导验证、公式展开）
  - 可视化：Matplotlib、Seaborn
  - 微分方程：`scipy.integrate.solve_ivp` / `odeint`
  - 信号处理：`scipy.signal`、`pywt`（小波变换）、`scipy.fft`（FFT频谱分析）
  - 图像处理：`opencv-python`（cv2）、`scikit-image`（skimage）
  - 面板计量：`linearmodels`（PanelOLS/RandomEffects/SystemGMM）、`statsmodels`
- **边界条件检查**：数据为空、维度不匹配、除零风险、数值溢出
- **数学边界验证**：优化约束完整、概率分布归一化、矩阵维度匹配

### 启发式优化算法使用

当问题为非凸优化、组合优化或传统方法失效时，使用 `extensions/heuristic_algorithms.py`：

```python
import sys
sys.path.insert(0, 'c:/Users/Fate永恒/.trae-cn/skills/mle-solver/extensions')
from heuristic_algorithms import solve_optimization

# 统一接口：自动选择最优算法
solution, value, info = solve_optimization(
    objective_func=lambda x: ...,  # 目标函数（求最小值）
    bounds=[(0, 10), (0, 5), ...],  # 参数边界
    method="auto",  # auto/ga/pso/sa/de
    verbose=False,
)
# info = {"method": "de", "history": [...], "n_evals": 200, "converged": True}
```

可用的四种算法：GA（遗传算法）、PSO（粒子群）、SA（模拟退火）、DE（差分进化）。`method="auto"` 时，<5维用PSO，>=5维用DE。

### 输出格式

**必须**返回以下格式的 Python 代码：

```python
# 完整的 Python 实现代码
# 包含所有 import、函数定义、主执行逻辑
# 物理约束注释标注（如 # FC-1: 弦长约束）
# 末尾包含硬断言验证块
# 所有中间结果保存为本地文件
```

---

## 阶段2.5：代码-物理一致性检查

**在代码生成之后、执行之前**，必须进行以下检查：

### 检查清单

| 检查项 | 方法 | 不通过的处理 |
|-------|------|------------|
| 物理约束是否在代码中实现？ | 搜索代码中是否出现了 `first_principles_review.fundamental_constraints` 中的关键方程 | 补充实现 |
| 是否使用了被 REJECTED 的简化？ | 检查代码逻辑是否使用了 `verdict="REJECTED"` 的简化方案 | 改回 ACCEPTED 方案 |
| 物理实体类型的约束是否满足？ | 检查 `physical_entity_type="刚性体"` 时，是否使用了弦长约束而非弧长偏移 | 修正 |
| 硬断言是否有对应的验证代码？ | 检查代码末尾是否包含所有 `hard_assertions` 的验证逻辑 | 补充验证代码 |

### 检查示例

```python
def code_physics_consistency_check(code_str, s1_analysis):
    """
    代码-物理一致性检查：确保代码忠实地实现了物理约束。
    """
    issues = []
    
    # 检查1：基本约束方程是否被实现
    for fc in s1_analysis['first_principles_review']['fundamental_constraints']:
        if fc['id'] not in code_str:
            issues.append(f"基本约束 {fc['id']} ({fc['name']}) 未在代码中标注")
    
    # 检查2：被拒绝的简化是否被使用
    for review in s1_analysis['first_principles_review']['simplification_review']:
        if review['verdict'] == 'REJECTED':
            if review['simplification'].split('：')[0] in code_str:
                issues.append(f"代码使用了被 REJECTED 的简化: {review['simplification']}")
    
    # 检查3：刚性体是否错误使用了弧长参数化
    for sp in s1_analysis['sub_problems']:
        if sp.get('physical_entity_type') == '刚性体':
            if 's(theta)' in code_str or 'arc_length' in code_str.lower():
                if '(x_i - x_{i-1})**2' not in code_str:
                    issues.append("刚性体问题使用了弧长参数化但未使用弦长约束")
    
    return len(issues) == 0, issues


def code_economics_consistency_check(code_str, data, s1_analysis):
    """
    v4 新增：经济建模代码一致性检查。
    确保经济建模代码遵循计量经济学最佳实践。
    """
    issues = []
    
    # 检查1: 是否对非平稳序列做了差分
    if s1_analysis and 'stationarity' in s1_analysis:
        for col, result in s1_analysis['stationarity'].items():
            if not result.get('is_stationary', True):
                if 'diff(' not in code_str and '.diff()' not in code_str:
                    issues.append(
                        f"非平稳序列 '{col}' 未做差分处理。"
                        f"必须使用 diff({col}) 或进行协整检验。"
                        f"参考: 伪回归——错误#7。"
                    )
    
    # 检查2: 是否使用了稳健标准误
    if 'OLS' in code_str or 'ols' in code_str or 'sm.OLS' in code_str:
        if 'HC' not in code_str and 'cov_type' not in code_str and 'robust' not in code_str.lower():
            issues.append(
                "OLS回归未使用稳健标准误。"
                "建议: 使用 cov_type='HC1' 或 robust standard errors。"
            )
    
    # 检查3: 是否检查了VIF（多重共线性）
    if ('OLS' in code_str or 'ols' in code_str) and len(data.columns) > 3:
        if 'vif' not in code_str.lower() and 'variance_inflation_factor' not in code_str:
            issues.append(
                "多元回归模型未检查VIF（多重共线性）。"
                "建议: 使用 variance_inflation_factor 检查各变量VIF值。"
                "VIF > 10 的变量应移除或合并。"
            )
    
    # 检查4: 是否做了异方差检验
    if ('OLS' in code_str or 'ols' in code_str) and 'sm.OLS' in code_str:
        if 'het_breuschpagan' not in code_str and 'white' not in code_str.lower():
            issues.append(
                "OLS回归未做异方差检验。"
                "建议: 使用 Breusch-Pagan 或 White 检验。"
                "若存在异方差，使用稳健标准误或WLS。"
            )
    
    return len(issues) == 0, issues


def code_signal_image_consistency_check(code_str, s1_analysis):
    """
    v5 新增：信号/图像处理代码一致性检查。
    确保信号/图像处理代码遵循最佳实践。
    """
    issues = []
    problem_type = s1_analysis.get('problem_type', '') if s1_analysis else ''
    
    # 检查1: 信号处理——是否先滤波再做FFT
    if 'signal' in problem_type.lower() or 'fft' in code_str.lower():
        if ('fft' in code_str.lower() or 'rfft' in code_str.lower() or 'spectrogram' in code_str.lower()):
            # 检查是否做了滤波预处理
            has_filtering = any(kw in code_str.lower() for kw in [
                'butter', 'filtfilt', 'sosfilt', 'lfilter', 'wiener',
                'wavelet', 'pywt', 'denoise', 'wden', 'wiener2',
                'savgol_filter', 'medfilt', 'gaussian_filter',
            ])
            if not has_filtering and 'snr' in code_str.lower():
                issues.append(
                    "信号处理: 代码中使用了FFT但未做滤波预处理。"
                    "含噪信号直接FFT会导致频谱被噪声淹没。"
                    "建议: 先使用小波去噪(pywt)或带通滤波(scipy.signal.butter)。"
                )
    
    # 检查2: 图像处理——是否做了光照校正
    if 'image' in problem_type.lower() or any(kw in code_str.lower() for kw in [
        'cv2', 'opencv', 'canny', 'edge', 'threshold', 'skimage',
    ]):
        has_edge_detection = any(kw in code_str.lower() for kw in [
            'canny', 'sobel', 'laplacian', 'edge_detection', 'findcontours',
        ])
        has_illumination_correction = any(kw in code_str.lower() for kw in [
            'equalizehist', 'clahe', 'createclahe', 'adaptivethreshold',
            'normalize', 'illumination', 'gamma_correction',
        ])
        if has_edge_detection and not has_illumination_correction:
            issues.append(
                "图像处理: 代码中使用了边缘检测但未做光照校正。"
                "光照不均会严重影响边缘检测效果。"
                "建议: 使用 cv2.equalizeHist() 或 cv2.createCLAHE() 进行直方图均衡化。"
            )
    
    # 检查3: 类别不平衡——是否做了重采样
    if 'classify' in problem_type.lower() or 'classifier' in code_str.lower() or 'classification' in code_str.lower():
        has_resampling = any(kw in code_str.lower() for kw in [
            'smote', 'adasyn', 'randomoversampler', 'randomundersampler',
            'class_weight', 'balanced', 'imblearn',
        ])
        if not has_resampling:
            issues.append(
                "分类任务: 未检测到不平衡数据处理。"
                "如果数据存在类别不平衡，模型会偏向多数类。"
                "建议: 使用 SMOTE/ADASYN (imblearn) 或设置 class_weight='balanced'。"
            )
    
    # 检查4: 面板数据——是否做了个体效应检验
    if 'panel' in problem_type.lower() or 'PanelOLS' in code_str or 'entity_effects' in code_str:
        has_hausman = any(kw in code_str.lower() for kw in [
            'hausman', 'random_effects', 'RandomEffects',
        ])
        if 'PooledOLS' in code_str and not has_hausman:
            issues.append(
                "面板数据: 使用了PooledOLS但未做Hausman检验。"
                "忽略个体效应会导致估计有偏。"
                "建议: 使用Hausman检验选择FE或RE，而非直接Pooled OLS。"
            )
    
    return len(issues) == 0, issues
```

---

## 阶段3：执行验证与自动纠错（Verify-Revise 阶段）

### 执行机制

代码生成后，使用 `RunCommand` 在本地执行脚本，捕获 stdout 和 stderr。

### 错误检测（扩展）

以下任一情况视为**执行失败**，必须触发 Debug 流程：

| 错误类型 | 检测方式 | 示例 |
|---------|---------|------|
| 语法/运行时错误 | 输出包含 `Traceback`、`SyntaxError`、`IndentationError` | `NameError: name 'x' is not defined` |
| 硬断言失败 | 输出包含 `硬断言验证失败` 或 `sys.exit(1)` | `HA-5 FAILED: 把手3弦长偏差=2.4e-03m` |
| 物理不合理 | 输出包含 `物理合理性检查失败` | `WARNING: 所有把手速度恒为 1.0 m/s，可能为弧长模型错误` |
| 数值溢出/发散 | 输出包含 `inf`、`nan`、`overflow` | `RuntimeWarning: overflow encountered` |
| 进程返回码非零 | `returncode != 0` | — |

### Debug 反馈回路（扩展）

```
代码生成 -> 代码-物理一致性检查(2.5) -> 执行 -> 失败?
                    |                            |
                    +- 一致性检查失败            +- 否 -> 进入阶段3.5
                    |   -> 修正代码实现           |
                    |                            +- 是 -> Debug 修正：
                    |                                     读取错误输出
                    |                                     -> 判断错误类型：
                    |                                        +-- 语法/运行时错误
                    |                                        |   -> 定位行号 -> 修正 -> 重新执行
                    |                                        +-- 硬断言失败
                    |                                        |   -> 分析哪个物理约束被违反
                    |                                        |   -> 修正建模公式或算法 -> 重新执行
                    |                                        +-- 物理不合理
                    |                                        |   -> 检查是否使用了错误的简化
                    |                                        |   -> 更换建模方案 -> 重新执行
                    |                                        +-- 数值溢出/发散
                    |                                            -> 调整初始值/步长/容差 -> 重新执行
                    |                                     -> 仍失败? -> 继续修正（最多3轮）
```

### Debug 修正规则

修正时严格遵循：
1. 读取完整错误输出，定位具体行号和错误类型
2. 针对性修正，不做无关改动
3. 若数据文件不存在，检查路径或创建模拟数据
4. 若依赖库缺失，使用 `pip install` 安装
5. **若硬断言失败，回查 S1 的 `first_principles_review.fundamental_constraints`，确保建模公式正确**
6. **若物理不合理，检查是否使用了被 REJECTED 的简化方案**
7. **若3轮内无法修正，触发 systematic-debugging -> 通知 problem-analyzer 反思**

### 重试策略

```
外层最多 5 次尝试：
  +-- 第1次：初始代码生成 -> 一致性检查 -> 执行
  |   +-- 成功 -> 进入阶段3.5
  |   +-- 失败 -> 进入内层
  +-- 内层最多 3 轮 debug：
      +-- 第1轮：修正 -> 执行
      +-- 第2轮：再次修正 -> 执行
      +-- 第3轮：最后修正 -> 执行
          +-- 仍失败 -> 返回失败状态，诚实告知用户
          +-- 若失败根因为物理建模错误 -> 触发 systematic-debugging
```

### 输出截断

若执行输出超过 ~2000 tokens，仅保留最后 2000 tokens。

---

## 阶段3.5：硬断言验证

代码执行成功后，**自动运行**代码末尾的 `verify_hard_assertions()` 函数。

### 验证流程

```
代码执行成功
    |
    v
自动调用 verify_hard_assertions()
    |
    +-- 全部通过 -> 进入阶段3.6
    |
    +-- 有失败 -> 触发 Debug 回路
                  |
                  +-- 分析失败原因
                  +-- 判断：是代码bug还是建模错误？
                  +-- 代码bug -> 修正代码 -> 重新执行
                  +-- 建模错误 -> 修正建模公式 -> 重新生成代码 -> 重新执行
```

### 断言验证报告模板

```
============================================================
硬断言验证报告
============================================================
总断言数: 5
通过: 5
失败: 0

HA-1: 调头空间边界 |C1|+R1=4.32 <= 4.5
HA-2: 调头空间边界 |C2|+R2=3.51 <= 4.5
HA-3: 速度上限 max(|v_i|)=1.998 <= 2.0
HA-4: 碰撞安全 min(d_ij)=0.312 >= 0.30
HA-5: 弦长约束 max(|delta_L|)=3.2e-14 < 1e-10

结论: 所有硬断言验证通过
============================================================
```

---

## 阶段3.6：物理合理性检查

硬断言验证通过后，进行物理合理性检查。与硬断言不同，物理合理性检查是**软检查**——它不直接导致失败，但会发出警告，提示可能存在建模错误。

### 检查项

| 检查项 | 检测方法 | 严重程度 | 已知反例 |
|-------|---------|---------|---------|
| 速度均匀性 | 检查所有节点的速度是否完全相同 | HIGH | 2024国赛A题：弧长模型导致"全队速度=1.0 m/s"的佯谬 |
| 位置单调性 | 检查把手位置是否随角度单调变化 | MEDIUM | — |
| 物理量量级 | 检查结果是否在合理数量级范围内 | MEDIUM | — |
| 对称性 | 检查对称系统是否产生对称结果 | MEDIUM | — |
| 趋势一致性 | 检查结果的变化趋势是否与物理直觉一致 | LOW | — |
| 守恒量 | 检查守恒量（能量、动量等）是否保持恒定 | HIGH | — |
| 高度不变性 | 检查无人机/飞行器 z 坐标是否在所有时刻保持恒定 | HIGH | 2025国赛A题：无人机高度从1800m漂移到1781.9m |

### 检查代码模板

```python
# ============================================================
# 物理合理性检查块
# 以下检查不会导致代码退出，但会输出警告
# ============================================================

def physics_sanity_check(results, params):
    """
    物理合理性软检查。
    返回: (warnings: list)
    """
    warnings = []
    
    # 检查1: 速度均匀性检测
    # 如果所有节点的速度在所有时刻都完全相同，可能是弧长模型错误
    velocities = np.array(results['velocities'])
    velocity_variance = np.var(velocities, axis=0)
    if np.max(velocity_variance) < 1e-12 and len(velocities) > 10:
        warnings.append(
            "HIGH: 所有节点的速度方差为0（完全相等）。"
            "如果问题涉及刚性体在弯曲路径上运动，速度应有非线性波动。"
            "请检查是否错误使用了弧长参数化（应使用弦长约束）。"
            "参考: 2024国赛A题'以弧代弦'错误。"
        )
    
    # 检查2: 几何边界越界
    for key in ['R1', 'R2', 'C1', 'C2']:
        if key in params:
            pass  # 检查圆弧半径 + 圆心距是否超过调头空间
    
    # 检查3: 数值合理性
    if 'collision_time' in results:
        if results['collision_time'] > results.get('max_theoretical_time', float('inf')):
            warnings.append(
                f"MEDIUM: 碰撞时间 {results['collision_time']}s "
                f"超过理论最大时间 {results['max_theoretical_time']}s"
            )
    
    return warnings

# 执行检查
warnings = physics_sanity_check(results, params)
if warnings:
    print("=" * 60)
    print("物理合理性检查发现以下警告：")
    for w in warnings:
        print(f"  {w}")
    print("=" * 60)
else:
    print("物理合理性检查通过")
```

---

## 阶段4：结果解释

代码执行成功后，生成全面的结果解释：

- 清晰陈述数值结果、数据趋势、统计指标
- 讨论中间步骤和计算过程，包括变换和假设
- 如有图表，描述其内容和含义
- 与预期结果或已知结果对比，评估任务成功度
- 指出需要进一步研究或改进的领域
- **引用硬断言验证结果**：明确说明哪些物理约束已被验证通过
- **引用物理合理性检查结果**：说明是否存在警告及其含义

---

## 阶段4.5：模型-现实交叉验证

在结果解释之后，进行模型-现实交叉验证。这是最后的防线——即使所有硬断言通过，仍需验证结果是否与物理现实一致。

### 验证维度

```python
def model_reality_cross_check(results, s1_analysis):
    """
    模型-现实交叉验证：检查模型输出是否与物理现实一致。
    
    验证维度：
    1. 量纲一致性：输出单位是否与物理量匹配
    2. 边界行为：极端条件下模型行为是否合理
    3. 已知特例：模型是否退化为已知的简单情况
    4. 跨问题一致性：同一模型在不同子问题中的预测是否自洽
    """
    checks = []
    
    # 维度1: 量纲一致性
    # 示例：速度的单位应为 m/s，位置的单位应为 m
    
    # 维度2: 边界行为
    # 示例：当 p->0 时，碰撞时间应 -> 0
    
    # 维度3: 已知特例
    # 示例：如果只有一个板凳（N=1），模型应退化为简单圆周运动
    
    # 维度4: 跨问题一致性
    # 示例：Q2 的碰撞时间应 <= Q1 的最大时间
    
    return checks
```

### 交叉验证失败处理

交叉验证失败不直接触发 Debug 回路，但会在阶段5的结论分析中明确标注，并建议人工审查。

---

## 阶段5：结论分析与代码结构提取

### 结论分析

生成综合性结论，包含：

- 明确陈述主要结论，每条结论与具体结果相关联
- 验证初始假设，描述从数据到洞察的推理过程
- 评估模型有效性：预测精度、鲁棒性、计算效率
- 分析局限性对结论有效性的影响
- **偏差分析**（三条必做）：
  - 数据偏差：数据集是否代表问题空间？是否有不平衡/选择偏差？
  - 模型偏差：假设、参数选择、架构约束是否引入系统性偏差？
  - 计算偏差：数值精度、算法近似是否影响稳定性？
- 提出偏差缓解策略
- **验证总结**：汇总硬断言验证、物理合理性检查、模型-现实交叉验证的结果

### 阶段5.5：生成验证报告

```python
def generate_verification_report():
    """
    汇总所有验证结果，生成结构化报告。
    """
    return {
        "hard_assertions": {
            "total": len(hard_assertions),
            "passed": n_passed,
            "failed": n_failed,
            "details": assertion_results,
            "status": "PASSED" if n_failed == 0 else "FAILED",
        },
        "physics_sanity": {
            "warnings": warnings,
            "high_severity_count": n_high_warnings,
            "status": "PASSED" if n_high_warnings == 0 else "WARNINGS",
        },
        "model_reality_cross_check": {
            "checks": cross_check_results,
            "status": "PASSED" if all_ok else "ISSUES_FOUND",
        },
        "overall_status": "PASSED" if all_passed else "NEEDS_REVIEW",
    }
```

### 失败时触发闭环反思

```
如果 overall_status != "PASSED":
    1. 触发 systematic-debugging
    2. systematic-debugging 分析失败根因
    3. 如果是物理建模错误：
       -> 通知 problem-analyzer 反思
       -> 更新 problem-analyzer 的反面教材库
       -> 重新执行 S1（问题分析）
    4. 如果是代码实现错误：
       -> 修正代码
       -> 重新执行 S3
```

### 代码结构提取

提取以下信息供后续步骤引用：

- 脚本路径
- 类（类名、描述、成员函数及参数/返回值）
- 函数（函数名、描述、参数类型/描述、返回值）
- 文件输出（路径、描述、列名）
- **验证结果**：硬断言验证报告、物理合理性检查报告、交叉验证结果

---


## v3 新增：高度不变性等X约束检查（阶段3.6扩展）

### 检查代码模板（v3 增强）

在 `physics_sanity_check` 函数中新增以下检查项：

```python
def physics_sanity_check(results, params, s1_analysis=None):
    """
    物理合理性软检查（v3 增强：含等X约束检查）。
    返回: (warnings: list)
    """
    warnings = []
    
    # ===== v3 新增：等X约束自动检查 =====
    if s1_analysis and 'constant_constraints' in s1_analysis:
        for cc in s1_analysis['constant_constraints']:
            if cc['constraint_name'] == '等高度':
                # 检查所有时刻 z 坐标是否恒定
                z_values = results.get('z_coordinates', [])
                if z_values:
                    z_initial = z_values[0]
                    z_max_dev = max(abs(z - z_initial) for z in z_values)
                    if z_max_dev > 1e-6:
                        warnings.append(
                            f"HIGH: 等高度约束违反！z坐标最大偏差={z_max_dev:.2e}m。"
                            f"可能原因：方向向量使用了三维分量而非2D水平向量。"
                            f"修正：方向向量必须为 (cosθ, sinθ, 0)，z分量恒为0。"
                            f"参考: 2025国赛A题'等高度巡飞约束'错误。"
                        )
                    else:
                        print(f"  ✓ 等高度约束验证通过 (最大偏差={z_max_dev:.2e}m)")
            
            elif cc['constraint_name'] == '等速':
                # 检查所有时刻速度模是否恒定
                v_values = results.get('velocities', [])
                if v_values:
                    v_norms = [np.linalg.norm(v) for v in v_values]
                    v_max_dev = max(abs(vn - v_norms[0]) for vn in v_norms)
                    if v_max_dev > 1e-6:
                        warnings.append(
                            f"HIGH: 等速约束违反！速度模最大偏差={v_max_dev:.2e}m/s。"
                        )
                    else:
                        print(f"  ✓ 等速约束验证通过")
            
            elif cc['constraint_name'] == '等间距':
                # 检查所有相邻质点间距是否恒为 L
                positions = results.get('positions', [])
                if positions and len(positions) > 1:
                    distance_errors = []
                    for i in range(1, len(positions)):
                        dist = np.linalg.norm(positions[i] - positions[i-1])
                        distance_errors.append(abs(dist - params.get('L', 0)))
                    if max(distance_errors) > 1e-6:
                        warnings.append(
                            f"HIGH: 等间距约束违反！最大弦长偏差={max(distance_errors):.2e}m。"
                            f"可能原因：以弧代弦。修正：使用弦长约束而非弧长参数化。"
                        )
                    else:
                        print(f"  ✓ 等间距约束验证通过 (最大偏差={max(distance_errors):.2e}m)")
    
    # ===== v3 新增：方向向量维度检查 =====
    if s1_analysis and 'direction_vector_check' in s1_analysis:
        dvc = s1_analysis['direction_vector_check']
        if dvc.get('verdict') == '必须锁定':
            # 检查方向向量z分量是否为0
            dir_vectors = results.get('direction_vectors', [])
            for i, dv in enumerate(dir_vectors):
                if abs(dv[2]) > 1e-10:
                    warnings.append(
                        f"HIGH: 方向向量维度错误！方向向量[{i}]的z分量={dv[2]:.2e}≠0。"
                        f"等高度场景中方向向量必须为2D水平向量。"
                        f"当前错误形式: {dvc.get('wrong_form', '未知')}"
                        f"正确形式: {dvc.get('correct_form', '(cosθ, sinθ, 0)')}"
                    )
    
    # ===== 原有检查项 =====
    # 检查1: 速度均匀性检测
    velocities = np.array(results.get('velocities', []))
    if len(velocities) > 0:
        velocity_variance = np.var(velocities, axis=0)
        if np.max(velocity_variance) < 1e-12 and len(velocities) > 10:
            warnings.append(
                "HIGH: 所有节点的速度方差为0（完全相等）。"
                "如果问题涉及刚性体在弯曲路径上运动，速度应有非线性波动。"
                "请检查是否错误使用了弧长参数化（应使用弦长约束）。"
            )
    
    return warnings
```

---

## v3 新增：目标函数光滑性自动检测（阶段3.0 新增）

**在优化方法选择前**，必须从 S1 接收 `objective_smoothness` 预判结果，并据此路由优化方法。

### 光滑性检测代码模板

```python
def route_optimization_method(s1_analysis):
    """
    v3 新增：根据目标函数光滑性预判结果，路由优化方法。
    必须在优化代码生成前调用。
    """
    smoothness = s1_analysis.get('objective_smoothness', {})
    
    if not smoothness:
        # 保守判定：假设不光滑
        return {
            "method": "DE",
            "reason": "无法确定目标函数光滑性，保守使用零阶方法",
            "forbidden": ["SQP"],
        }
    
    if smoothness.get('gradient_available') == False:
        # 目标函数不光滑，必须使用零阶方法
        print(f"目标函数光滑性: {smoothness.get('smoothness')}")
        print(f"推荐方法: {smoothness.get('recommended_methods')}")
        print(f"禁止方法: {smoothness.get('forbidden_methods')}")
        print(f"原因: {smoothness.get('reason')}")
        
        return {
            "method": smoothness['recommended_methods'][0],  # 首选方法
            "fallback_methods": smoothness['recommended_methods'][1:],
            "forbidden": smoothness['forbidden_methods'],
            "reason": smoothness['reason'],
        }
    
    return {
        "method": "SQP",
        "reason": "目标函数连续可微，梯度方法有效",
        "forbidden": [],
    }

# 使用示例
opt_config = route_optimization_method(s1_analysis)
if opt_config['method'] == 'DE':
    # 使用差分进化
    from heuristic_algorithms import solve_optimization
    solution, value, info = solve_optimization(
        objective_func=obj_func,
        bounds=bounds,
        method='de',
    )
elif opt_config['method'] == 'SQP':
    # 使用 SQP
    from scipy.optimize import minimize
    result = minimize(obj_func, x0, method='SLSQP', bounds=bounds)
```

---

## v3 新增：连续指标引导（几何判定修正）

### 连续指标 vs 离散判定

对于几何遮蔽/遮挡/碰撞判定问题，必须使用连续指标：

| 问题类型 | 离散判定（禁止） | 连续指标（推荐） |
|---------|---------------|---------------|
| 烟幕遮蔽 | 8点AND逻辑（d_k ≤ R_c for all k） | 连续遮蔽率 η = Σ 1[d_k ≤ R_c] / N_s |
| 碰撞检测 | 接触判定（d ≤ d_min） | 连续接触系数 α = 1 - d/d_min |
| 视野遮挡 | 视线完全阻断（binary） | 遮挡面积比 A_occ / A_total |
| 区域覆盖 | 覆盖/未覆盖（binary） | 覆盖率 η = A_covered / A_total |

### 连续指标代码模板

```python
def continuous_shielding_ratio(missile_pos, cloud_center, target_samples, cloud_radius):
    """
    v3 新增：连续遮蔽率计算（替代8点AND逻辑）。
    
    参数:
        missile_pos: 导弹位置 (x, y, z)
        cloud_center: 云团球心 (x, y, z)
        target_samples: 目标采样点列表 [(x, y, z), ...]
        cloud_radius: 云团有效半径
    
    返回:
        ratio: 连续遮蔽率 [0, 1]
    """
    n_shielded = 0
    for sample in target_samples:
        # 视线方向
        los = sample - missile_pos
        los_len = np.linalg.norm(los)
        if los_len < 1e-10:
            n_shielded += 1
            continue
        los_dir = los / los_len
        
        # 云团球心到视线的最短距离
        v = cloud_center - missile_pos
        t = np.dot(v, los_dir)
        t = max(0.0, t)
        closest_point = missile_pos + t * los_dir
        distance = np.linalg.norm(closest_point - cloud_center)
        
        if distance <= cloud_radius:
            n_shielded += 1
    
    return n_shielded / len(target_samples)

# 使用示例
# 采样点: 顶面4 + 底面4 + 侧面8 + 内部4 = 20个
# 遮蔽判定: η ≥ 0.9 视为有效遮蔽
target_samples = [...]  # 20个采样点均匀覆盖目标表面和内部
ratio = continuous_shielding_ratio(missile_pos, cloud_center, target_samples, 10.0)
is_shielded = ratio >= 0.9
```

---

## v3 新增：S1 v5 数据接收（阶段0.5扩展）

### 接收数据结构

```python
def load_s1_v5_analysis():
    """
    v3 新增：从 S1 接收 v5 扩展数据。
    除了原有的 hard_assertions 和 first_principles_review，
    还接收 v5 新增的 constant_constraints, objective_smoothness,
    constraint_completeness, direction_vector_check。
    """
    s1_data = pipe.get_stage_result(Stage.ANALYSIS).data
    
    return {
        # 原有字段
        "hard_assertions": s1_data.get("hard_assertions", []),
        "first_principles_review": s1_data.get("first_principles_review", {}),
        "high_risk_assumptions": s1_data.get("high_risk_assumptions", []),
        "physical_entity_type": s1_data.get("physical_entity_type", ""),
        "anti_patterns_to_avoid": s1_data.get("anti_patterns_to_avoid", []),
        "problem_type": s1_data.get("problem_type", ""),
        "problem_subtype": s1_data.get("problem_subtype", ""),
        "method_routing": s1_data.get("method_routing", {}),
        # v5 新增字段
        "constant_constraints": s1_data.get("constant_constraints", []),
        "objective_smoothness": s1_data.get("objective_smoothness", {}),
        "constraint_completeness": s1_data.get("constraint_completeness", {}),
        "direction_vector_check": s1_data.get("direction_vector_check", {}),
        "physical_entities": s1_data.get("physical_entities", {}),
    }
```

---

## v3 新增：低维度劫持检测（阶段2.5扩展）

### 检测项

在代码-物理一致性检查中新增以下检测：

```python
def code_physics_consistency_check_v3(code_str, s1_analysis):
    """
    代码-物理一致性检查（v3 增强：含低维度劫持检测）。
    """
    issues = []
    
    # ===== v3 新增：方向向量维度检查 =====
    if s1_analysis.get('direction_vector_check', {}).get('verdict') == '必须锁定':
        # 检查代码中是否使用了3D方向向量
        if 'd = -D0' in code_str or 'd = -pos' in code_str:
            if 'd[2]' in code_str or 'd_z' in code_str:
                issues.append(
                    "方向向量维度错误: 等高度场景中使用了3D方向向量。"
                    "方向向量应为 (cosθ, sinθ, 0)，不应包含z分量。"
                    "请检查: d = -D_{i,0}/|D_{i,0}| 应改为 d = (cosθ, sinθ, 0)"
                )
    
    # ===== v3 新增：连续指标检查 =====
    if '遮蔽' in str(s1_analysis.get('problem_text', '')) or '遮挡' in str(s1_analysis.get('problem_text', '')):
        if 'all(' in code_str and '采样点' in code_str:
            # 检查是否使用了 all() 而非 ratio
            if 'sum(' not in code_str and 'ratio' not in code_str.lower() and '遮蔽率' not in code_str:
                issues.append(
                    "几何判定使用了离散AND逻辑（all()）而非连续遮蔽率。"
                    "应使用: ratio = sum(d_k <= R for k in samples) / len(samples)"
                )
    
    # ===== v3 新增：等高度约束代码实现检查 =====
    if s1_analysis.get('constant_constraints'):
        for cc in s1_analysis['constant_constraints']:
            if cc['constraint_name'] == '等高度':
                # 检查代码中是否锁定了z坐标
                if 'pos[2]' in code_str and '=' not in code_str.split('pos[2]')[0][-5:]:
                    # pos[2] 被赋值但未锁定
                    if 'pos[2] = d0[2]' not in code_str and 'pos[2] = z0' not in code_str:
                        issues.append(
                            "等高度约束可能未在代码中实现: z坐标应为常量。"
                            f"应在运动函数中添加: pos[2] = {cc.get('math_expression', 'z_{i,0}')}"
                        )
    
    return len(issues) == 0, issues
```


## 四层检查机制总结（v7 新增第四层：方法一致性）

| 检查层 | 阶段 | 类型 | 失败后果 | 检测的错误类型（v3扩展） |
|-------|------|------|---------|--------------|
| **第零层：光滑性预判** | 阶段3.0 | 前置检查（v3新增） | 路由到错误优化方法 | 分段常值目标函数→禁止SQP |
| **第一层：硬断言** | 阶段3.5 | 硬检查（必须通过） | 触发 Debug 回路 | 物理约束违反、几何越界、速度超限、等X约束违反 |
| **第二层：物理合理性** | 阶段3.6 | 软检查（警告） | 发出警告，继续执行 | 速度均匀性异常、趋势反常、等高度漂移、方向向量维度错误 |
| **第三层：交叉验证** | 阶段4.5 | 软检查（标注） | 标注问题，建议审查 | 量纲错误、边界行为异常、跨问题不一致 |
| **第四层：方法一致性** | 阶段4.6 | 硬检查（v7新增） | 偏差>20%触发Debug回路 | 多方法结果矛盾、某方法提取谐波/伪影 |

**五层递进关系**：第零层确保优化方法选择正确，第一层拦截"确定的错误"（如弦长偏差、等高度违反），第二层检测"可疑的模式"（如速度全等、高度漂移），第三层验证"模型的边界"（如极端条件下的行为），第四层验证"方法间的一致性"（不同方法结果是否互相印证）。v7新增：第四层方法一致性检查不依赖任何特定问题类型，适用于所有问题。v5新增：阶段0.7信号/图像质量预检作为前置检查，阶段2.5信号/图像一致性检查作为代码质量保障。

---

## 硬性约束

### 必须遵守
1. 代码必须包含在 ` ```python ... ``` ` 标记中
2. 不得使用不存在的库或虚构的 API
3. 文件路径使用原始字符串或正斜杠
4. 所有文件写入操作使用绝对路径
5. 不得生成空代码块或占位符（如 `# TODO`、`pass`）
6. **代码末尾必须包含硬断言验证块（阶段1.5）**
7. **物理建模类问题必须加载 S1 分析结果（阶段0.5）**
8. **代码中必须标注所实现的物理约束ID（如 `# FC-1: 弦长约束`）**
9. **硬断言验证失败时，代码必须以非零退出码退出**
10. **物理建模类问题必须在阶段5.5生成完整的验证报告**
11. **v3新增：优化方法选择前必须调用 `route_optimization_method()` 根据光滑性预判结果路由**
12. **v3新增：必须从 S1 v5 接收 `constant_constraints` 和 `objective_smoothness` 数据**
13. **v3新增：物理合理性检查必须包含等X约束检查（高度不变性、等速、等间距等）**
14. **v3新增：连续指标必须使用遮蔽率/覆盖率而非离散AND逻辑判定**
15. **v4新增：经济建模必须运行 `check_stationarity()` 检查平稳性**
16. **v4新增：跨年货币数据必须运行 `check_nominal_vs_real()` 检查价格平减**
17. **v4新增：跨期决策必须运行 `check_time_value()` 提醒折现**
18. **v4新增：回归分析必须报告VIF和异方差检验结果**
19. **v5新增：信号处理必须运行 `check_signal_quality()` 检查SNR/采样率/频谱泄漏**
20. **v5新增：图像处理必须运行 `check_image_quality()` 检查分辨率/光照/类别平衡**
21. **v5新增：面板数据必须运行Hausman检验选择FE/RE，禁止直接Pooled OLS**
22. **v5新增：不平衡分类必须使用SMOTE/ADASYN或设置类别权重**
23. **v7新增：代码中所有数值常量必须有推导来源或标注出处（无魔法数字原则）**
24. **v7新增：代码开头必须包含上下文绑定块，显式声明从S1接收的参数**
25. **v7新增：当使用N>=2种求解方法时，必须在阶段4.6执行多方法交叉验证门禁**
26. **v7新增：多方法结果偏差>20%时，必须触发systematic-debugging，禁止将矛盾结果作为最终答案**

### 禁止事项
1. 禁止重复执行已完成的数据预处理步骤
2. 禁止忽略建模公式中的数学约束
3. 禁止在代码中使用未定义的变量或函数
4. 禁止生成不可执行或仅包含伪代码的输出
5. 禁止使用 Markdown 格式化代码解释（代码注释除外）
6. **禁止在未通过硬断言验证的情况下，声称模型求解成功**
7. **禁止使用 S1 第一性原理审查中 verdict="REJECTED" 的简化方案**
8. **禁止在物理建模类问题中跳过阶段0.5（加载S1分析结果）**
9. **禁止将刚性体问题中的弦长约束替换为弧长偏移（除非柔性体）**
10. **禁止在硬断言失败时仅修改断言容差而非修正建模公式**
11. **v3新增：禁止在目标函数光滑性未知时使用SQP或任何基于梯度的优化方法**
12. **v3新增：禁止在等高度场景中使用三维方向向量（d = -D_{i,0}/|D_{i,0}|）**
13. **v3新增：禁止使用8点及以下的AND逻辑判定几何遮蔽（必须使用连续遮蔽率）**
14. **v3新增：禁止在 `physics_sanity_check` 中不实现等X约束检查**
15. **v4新增：禁止对非平稳序列不做任何处理直接OLS回归**
16. **v4新增：禁止在跨期决策中使用未折现的现金流**
17. **v4新增：禁止在回归建模中不使用稳健标准误**
18. **v4新增：禁止在存在明显内生性时不讨论处理方式**
19. **v5新增：禁止对含噪信号不做滤波直接FFT分析**
20. **v5新增：禁止对光照不均图像不做预处理直接边缘检测**
21. **v5新增：禁止面板数据忽略个体效应直接使用Pooled OLS**
22. **v5新增：禁止不平衡分类数据不做重采样直接训练模型**
23. **v7新增：禁止在代码中使用无来源的硬编码数值常量（必须标注推导来源或引用S1参数）**
24. **v7新增：禁止生成不包含上下文绑定块的孤立代码**
25. **v7新增：禁止在多方法结果偏差>20%时不做排查直接取平均值或任意选一个**
26. **v7新增：禁止将未经方法一致性检查的结果传递给下游阶段**

---

## 反面教材库（持续更新）

以下是已知的典型求解错误，每次发现新错误后自动追加：

### 错误 #1：以弧代弦（2024 国赛 A 题）

- **错误描述**：代码实现了弧长偏移 $s(\theta_i) - s(\theta_{i-1}) = L$ 而非弦长约束 $(x_i-x_{i-1})^2+(y_i-y_{i-1})^2 = L^2$
- **代码表现**：`s_i = s_head + offset` 而非 `f(theta) = (x-x_prev)^2 + (y-y_prev)^2 - L^2`
- **检测方式**：物理合理性检查（阶段3.6）— 所有节点速度完全相同
- **防御规则**：`physical_entity_type="刚性体"` 时，代码中必须出现弦长约束方程

### 错误 #2：圆弧越界（2024 国赛 A 题）

- **错误描述**：R1=9.0m 的圆弧塞进半径 4.5m 的调头空间
- **代码表现**：缺少几何边界检查
- **检测方式**：硬断言验证（阶段3.5）— `|C1| + R1 <= 4.5` 断言失败
- **防御规则**：所有几何约束必须转化为硬断言且代码中实现

### 错误 #3：验证了错误的量（2024 国赛 A 题）

- **错误描述**：代码验证了"把手是否在螺线上"而非"弦长是否等于板凳长度"
- **代码表现**：`assert abs(r - a*theta) < 1e-14` 而非 `assert abs(chord_length - L) < 1e-10`
- **检测方式**：代码-物理一致性检查（阶段2.5）— 验证指标与基本约束不对齐
- **防御规则**：验证指标必须与 `first_principles_review.fundamental_constraints` 对齐

### 错误 #4：违反等高度巡飞约束（2025 国赛 A 题，v3 新增）
- **错误描述**：无人机运动函数中使用了3D方向向量 `d = -D_{i,0}/|D_{i,0}|`，导致z坐标从1800m漂移到1781.9m
- **代码表现**：`pos = D0 + v * t * d` 其中 `d = -D0 / norm(D0)` 包含z分量
- **检测方式**：物理合理性检查（阶段3.6）— z坐标偏差检测 + 方向向量维度检查
- **防御规则**：等高度场景中方向向量必须为 `(cosθ, sinθ, 0)`，z分量恒为0

### 错误 #5：对不连续目标函数使用SQP（2025 国赛 A 题，v3 新增）
- **错误描述**：遮蔽时间函数为分段常值，使用 `scipy.optimize.minimize(method='SLSQP')` 导致算法死锁
- **代码表现**：`minimize(lambda x: -shielding_time(x), x0, method='SLSQP')` 返回初始点
- **检测方式**：光滑性预判（阶段3.0）— 分段常值/阶跃函数自动禁止SQP
- **防御规则**：不光滑目标函数必须使用 DE/GA/PSO 等零阶方法

### 错误 #6：二分几何判定压缩搜索空间（2025 国赛 A 题，v3 新增）
- **错误描述**：使用8个离散点 + `all([d_k <= R])` 判定遮蔽，有效搜索空间极窄
- **代码表现**：`all([dist(k) <= R for k in range(8)])` 而非连续遮蔽率
- **检测方式**：代码-物理一致性检查（阶段2.5）— 检测 `all()` 而非 `sum()/len()` 模式
- **防御规则**：几何判定必须使用连续遮蔽率 `sum(1[d_k <= R]) / N_s`

### 错误 #13：魔法数字导致信号截断（信号处理，v7 新增）
- **错误描述**：代码中使用硬编码阈值 `fr > 0.01` 过滤FFT频率，将正确信号频率 f=0.00527 cm 排除在外
- **代码表现**：`mk = fr > 0.01; mg_filtered[~mk] = 0` 导致正确频率被清零
- **检测方式**：无魔法数字自检（代码扫描）— 检查所有数值字面量是否有推导注释
- **防御规则**：所有阈值必须从物理参数推导，如 `f_min = 2 * n * d_min * cosθ`

### 错误 #14：多方法结果矛盾未发现（通用，v7 新增）
- **错误描述**：FFT=19 um, 自相关=4 um, 峰回归=9.3 um 三种方法结果差异巨大但未被检测
- **代码表现**：三种方法独立输出结果，无交叉比较逻辑
- **检测方式**：多方法交叉验证门禁（阶段4.6）— 自动计算两两偏差
- **防御规则**：N>=2种方法时必须执行 `check_method_agreement()`

### 错误 #7：伪回归——对非平稳序列直接OLS（经济建模，v4 新增）

- **错误描述**：对具有单位根的非平稳时间序列直接进行OLS回归，得到虚假的高R²和显著t统计量，但回归关系完全虚假
- **代码表现**：`sm.OLS(y, X).fit()` 直接拟合，未做ADF检验和差分处理
- **检测方式**：经济数据特征预检（阶段0.6）— `check_stationarity()` 返回非平稳警告
- **防御规则**：所有时间序列回归前必须做ADF检验；非平稳序列必须差分或进行协整检验（Johansen/Engle-Granger）
- **经典案例**：GDP对降雨量回归，两者均有趋势，R²可高达0.9但毫无意义

### 错误 #8：名义值与实际值混淆（经济建模，v4 新增）

- **错误描述**：跨年经济数据中，将名义GDP、名义收入等直接用于回归，未用CPI或GDP平减指数调整为实际值
- **代码表现**：`y = data['名义GDP']` 直接建模，未除以价格指数
- **检测方式**：经济数据特征预检（阶段0.6）— `check_nominal_vs_real()` 检测跨年货币变量
- **防御规则**：跨年货币变量必须进行价格平减：`实际值 = 名义值 / 价格指数 * 100`
- **经典案例**：用名义GDP做时间序列分析，通胀时期增长率被高估

### 错误 #9：忽略货币时间价值（经济建模，v4 新增）

- **错误描述**：在跨期决策（如成本效益分析、投资评估）中直接加总不同时点的现金流，未做折现处理
- **代码表现**：`NPV = sum(cash_flows)` 而非 `NPV = sum(cf_t / (1+r)**t)`
- **检测方式**：经济数据特征预检（阶段0.6）— `check_time_value()` 检测跨期现金流
- **防御规则**：所有跨期现金流必须折现到同一基准时点；折现率需明确说明来源
- **经典案例**：项目评估中，将未来10年的收益简单加总，净现值被高估数倍

### 错误 #10：忽略内生性——OLS估计有偏（经济建模，v4 新增）

- **错误描述**：当解释变量与误差项相关时（如联立方程、遗漏变量、测量误差），OLS估计量不一致且有偏
- **代码表现**：`sm.OLS(y, X).fit()` 直接估计，未讨论内生性来源和处理方式
- **检测方式**：问题分析（S1）— 检测是否存在双向因果关系、遗漏变量、自选择偏差
- **防御规则**：存在内生性时必须使用IV/2SLS或面板固定效应；Hausman检验判断内生性是否存在
- **经典案例**：教育对收入的影响——能力（遗漏变量）同时影响教育和收入，OLS高估教育回报

### 错误 #11：忽略市场均衡约束（经济建模，v4 新增）

- **错误描述**：在供需模型中仅估计需求函数或供给函数，未施加市场出清条件（Q_d = Q_s）
- **代码表现**：`Q_d = a - b*P` 单独估计，未联立 `Q_s = c + d*P, Q_d = Q_s`
- **检测方式**：代码-物理一致性检查（阶段2.5）— 检测供需模型是否包含均衡条件
- **防御规则**：供需模型必须联立方程；使用2SLS或3SLS估计；均衡价格由市场出清条件内生确定
- **经典案例**：仅估计需求函数而忽略供给约束，导致均衡价格预测偏差

### 错误 #12：幸存者偏差（经济建模，v4 新增）

- **错误描述**：仅使用样本中存活/成功/仍在运营的个体进行分析，忽略了已退出/失败的个体
- **代码表现**：`data = data[data['status'] == '存活']` 或数据本身只有存活样本
- **检测方式**：经济数据特征预检（阶段0.6）— `check_sample_selection()` 检测样本选择偏差
- **防御规则**：必须讨论样本选择机制；使用Heckman两阶段模型或处理效应模型进行偏差修正
- **经典案例**：用当前仍在市场上的基金业绩评估历史表现——已清盘的差基金被排除，导致平均收益高估

---

## 扩展方法库参考

### 完整方法库（含新增）

| 类别 | 方法 | 推荐库 |
|------|------|--------|
| 运筹优化 | 线性规划、整数规划、混合整数规划 | PuLP, CVXPY, scipy.optimize.linprog |
| 运筹优化 | 非线性规划、凸规划、二次规划 | scipy.optimize.minimize, cvxpy |
| 运筹优化 | 动态规划 | 手写递推 / functools.lru_cache |
| 启发式优化 | 遗传算法 GA、粒子群 PSO、模拟退火 SA、差分进化 DE | extensions/heuristic_algorithms.py |
| 图论 | 最短路径、网络流、TSP | NetworkX, scipy.sparse.csgraph |
| 统计 | 回归分析、假设检验 | scipy.stats, statsmodels |
| 统计 | 时间序列、蒙特卡洛、贝叶斯 | statsmodels, numpy.random, pymc |
| 机器学习 | 分类、聚类、降维 | scikit-learn |
| 深度学习 | 神经网络、LSTM、Transformer | PyTorch / TensorFlow（慎用） |
| 符号计算 | 公式推导、符号验证 | SymPy |
| 微分方程 | ODE、PDE 数值求解 | scipy.integrate.solve_ivp |
| 评价决策 | AHP、TOPSIS、熵权法 | numpy（手写矩阵运算） |
| 随机过程 | 马尔可夫链、排队论 | numpy（手写概率转移） |
| 博弈论 | 纳什均衡、演化博弈 | numpy + scipy.optimize |
| 刚体运动学 | 弦长约束递推 + 牛顿迭代 | numpy + scipy.optimize.newton |
| 几何约束规划 | 可行域扫描 + 约束优化 | numpy + scipy.optimize |
| 信号处理 | FFT、小波去噪、滤波、STFT | scipy.signal, scipy.fft, pywt |
| 图像处理 | 边缘检测、分割、特征提取 | opencv-python, scikit-image |
| 面板计量 | FE/RE、Hausman检验、GMM | linearmodels, statsmodels |

### 模型选择决策框架

完整决策框架见 `references/model_selection_guide.md`，包含：
- 15种问题类型（评价/预测/优化/分类聚类/物理建模/刚体运动学/几何约束规划/信号处理/图像处理/排队论/博弈论/微分方程/经济建模/面板数据分析/混合型）的模型选择决策树
- 刚体运动学（弦长约束）和几何约束规划（可行域扫描）的专用决策路径
- 信号处理（FFT+小波去噪）和图像处理（Canny+Otsu+CNN）的专用决策路径
- 面板数据（FE/RE/GMM）的专用决策路径
- 模型选择反模式（国赛常见错误）
- 模型选择理由模板

---

## 完工检查清单

每次完成求解后自检：

- [ ] 代码是否成功执行（无 Traceback/SyntaxError/IndentationError）？
- [ ] 是否已根据问题类型选择了最优模型（参考 model_selection_guide）？
- [ ] 是否已加载 S1 分析结果（hard_assertions + first_principles_review）？
- [ ] 代码中是否标注了所实现的物理约束ID？
- [ ] 代码末尾是否包含硬断言验证块？
- [ ] 所有硬断言是否通过（阶段3.5）？
- [ ] 物理合理性检查是否通过（阶段3.6）？
- [ ] 模型-现实交叉验证是否通过（阶段4.5）？
- [ ] 中间结果是否已保存为本地文件（CSV/JSON/pickle）？
- [ ] 输出是否包含足够的 print 日志？
- [ ] 是否复用了已有依赖文件而非重复处理原始数据？
- [ ] 结果解释是否引用了具体的执行结果数值？
- [ ] 结论分析是否包含了偏差分析与局限性讨论？
- [ ] 是否生成了完整的验证报告（阶段5.5）？
- [ ] 代码结构信息是否已提取？
- [ ] v3: 是否已调用 `route_optimization_method()` 根据光滑性预判结果选择优化方法？
- [ ] v3: 是否已从 S1 v5 接收 `constant_constraints` 和 `objective_smoothness`？
- [ ] v3: 物理合理性检查是否包含等X约束检查（高度不变性、等速、等间距）？
- [ ] v3: 连续几何判定是否使用了遮蔽率/覆盖率而非离散AND逻辑？
- [ ] v4: 是否已检查数据平稳性（ADF检验）？
- [ ] v4: 跨年数据是否已做价格平减？
- [ ] v4: 跨期决策是否已引入折现？
- [ ] v4: 回归模型是否报告了VIF和异方差检验？
- [ ] v5: 信号数据是否检查了SNR、采样率和频谱泄漏？
- [ ] v5: 图像数据是否检查了分辨率、光照一致性和类别平衡？
- [ ] v5: 面板数据是否运行了Hausman检验（FE vs RE）？
- [ ] v5: 不平衡分类数据是否使用了SMOTE/ADASYN或类别权重？
- [ ] v5: 信号处理代码是否先滤波再做FFT？
- [ ] v5: 图像处理代码是否先做光照校正再做边缘检测？

---

*本 Skill 为 SciPilot 项目自主研发成果。Generate-Verify-Revise 迭代架构、模型选择框架、启发式算法扩展、三层检查机制均来自国赛获奖经验总结与2024国赛A题复盘教训。*
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

- **当前版本**: v6.0.0
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为 `C题专属` 的变更不应影响 A题/B题/信号/图像 的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py pre-check`
## 泛化约束

- **当前版本**: v6.0.0
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为 `C题专属` 的变更不应影响 A题/B题/信号/图像 的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py pre-check`
## 泛化约束

- **当前版本**: v6.0.0
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为 `C题专属` 的变更不应影响 A题/B题/信号/图像 的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py pre-check`
## 泛化约束

- **当前版本**: v4.0
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: G-001, G-004, G-005, G-007
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v6.0.0
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

- **当前版本**: v6.0.0
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

- **当前版本**: v9.0.0
- **冷却期**: 上次进化 2026-07-19，下次可用 2026-07-19 15:00
- **连续进化次数**: 1
- **关联缺口**: G-018, G-019, G-020
- **问题范围**: 离散约束+仿真视界仅适用于 B题/C题/A题整数变量，不适用于 A题连续参数/信号/图像；预案集框架适用于全部随机优化问题

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
