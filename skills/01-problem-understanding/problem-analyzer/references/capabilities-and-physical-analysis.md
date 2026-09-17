# 能力、物理实体、范围与约束分析（R1 structural extraction only）

> **R1 authority override:** 历史命名方法和竞赛题型经验不是选择规则。只可提取实体、单位、边界、约束、守恒、风险与预期范围；不得由 `problem-analyzer` 输出推荐模型。

## 内容索引

  - v5 新增能力速览
  - v6 新增能力速览
  - v7 新增能力速览
  - v8 新增能力速览
  - v9 新增能力速览
  - v9 新增：输出参数预期范围估计 (Expected Output Ranges)
    - 核心原则
    - 各问题类型的预期范围估计指南
    - 与下游的对接
  - v5 新增：物理实体类型自动识别与约束提取
    - 物理实体类型分类器（v5 增强）
    - 等X约束自动检测（v5 新增）
    - 方向向量维度验证（v5 新增）
  - v5 新增：约束完整性检查清单
    - 第一层：物理约束（Physical Constraints）
    - 第二层：逻辑约束（Logical Constraints）
    - 第三层：优化约束（Optimization Constraints）
  - v11 新增能力速览
  - v12 新增能力速览（2023A题训练驱动）
  - v13 新增能力速览（2023A题训练驱动 v4.0）
  - v14 新增能力速览（2023D题训练驱动）
    - v14 核心：预案集关键词路由
    - v14 核心：离散变量自动检测
    - v14 规则作用域
    - 典型误判案例（禁止复现）
  - 泛化约束与反过拟合（v13 随附，2023A题教训）
    - 规则作用域白名单/黑名单
    - 题型互斥检查（强制门禁）
    - 典型误判案例（禁止复现）
    - 规则优先级体系（三层分级）
    - v12 核心：A题几何光学+蒙特卡洛光线追迹路由
    - v12 核心：同心圆密排+高度-半径耦合布局路由
    - v12 核心：双层规划优化架构路由
    - v11 核心：C题"时序预测+优化"两阶段路由
    - v11 核心：FP-Growth 关联规则挖掘方法路由
    - v11 核心：Double-log 双对数需求模型方法路由
    - v11 核心：全局启发式优化方法路由
    - v11 核心：VIKOP 多准则评价方法路由
    - v11 核心：蔬菜季节性分类数据预处理路由

## v5 新增能力速览

| 能力 | v4 | v5 |
|------|:--:|:--:|
| 物理实体类型识别 | 手动标注 | 自动识别 + 约束方程自动提取 |
| 等X约束检测 | 无 | 自动检测等高度/等速/等温/等压/等间距 |
| 约束完整性检查 | 无 | 3层清单：物理约束→逻辑约束→优化约束 |
| 方向向量维度验证 | 无 | 等高度场景自动验证z分量为0 |
| 目标函数光滑性预判 | 无 | 自动判定连续/分段常值/阶跃，路由优化方法 |

## v6 新增能力速览

| 能力 | v5 | v6 |
|------|:--:|:--:|
| 经济建模类型识别 | 无 | 自动识别经济预测/政策评估/金融建模 |
| 经济约束自动检测 | 无 | 自动检测市场均衡/预算约束/非负约束 |
| 经济数据特征检测 | 无 | 自动检测平稳性/季节性/趋势/结构性断点 |
| 经济建模方法路由 | 无 | 根据数据特征自动路由计量方法 |
| 通用建模陷阱检测 | 无 | 量纲/边界/简化/线性假设四维检查 |

## v7 新增能力速览

| 能力 | v6 | v7 |
|------|:--:|:--:|
| 信号处理子类型路由 | 无 | FFT/小波/滤波/频谱分析子类型路由 |
| 图像处理子类型路由 | 无 | 边缘检测/分割/特征提取子类型路由 |
| ABC题型智能路由 | 无 | 自动识别A题(物理/工程)/B题(社会/经济/管理)/C题(数据驱动) |
| 面板数据方法路由 | 无 | FE/RE/System GMM 面板数据方法路由 |
| 问题类型扩充 | 13种 | 15种（新增信号处理+图像处理） |

## v8 新增能力速览

| 能力 | v7 | v8 |
|------|:--:|:--:|
| 评价类方法全覆盖 | 仅熵权TOPSIS | AHP/模糊综合评价/灰色关联/组合赋权/DEA |
| 预测类高阶方法 | 基础方法 | SVM/混合效应/生存分析/Optuna超参调优 |
| 机理类高阶模型 | 无 | GAM/系统动力学/PINN |
| 优化类高阶方法 | 无 | 强化学习/混合求解策略(GA+fmincon) |
| 绘图方法路由 | 14种问题类型 | 补充Pyecharts/Plotly/networkx/MATLAB路由 |

## v9 新增能力速览

| 能力 | v8 | v9 |
|------|:--:|:--:|
| 输出参数范围估计 | 无 | 自动估计关键输出参数的预期范围（数量级正确即可） |
| 魔法数字防御 | 无 | 在S1输出中提供 expected_output_ranges 和 critical_parameters 供下游推导阈值 |
| 方法一致性预检 | 无 | 为多方法场景预生成 method_agreement 检查参数 |


---

## v9 新增：输出参数预期范围估计 (Expected Output Ranges)

### 核心原则

在 S1 阶段必须估计关键输出参数的**预期范围**。这个估计不需要精确，只需要一个**数量级正确**的宽松范围，足以在后续阶段识别明显错误的结果。

### 各问题类型的预期范围估计指南

| 问题类型 | 典型输出 | 估计方法 | 示例范围 |
|---------|---------|---------|---------|
| 物理建模 | 厚度/速度/温度 | 基于物理常识（半导体工艺、材料科学） | 外延层厚度: 0.1-500 um |
| 优化决策 | 目标函数值 | 基于物理上下界（最大/最小可能值） | 遮蔽时间: 0-总仿真时间 |
| 预测预报 | 预测值 | 基于历史数据的 min/max 扩展 50% | 如果历史范围 [10, 100] -> [5, 150] |
| 综合评价 | 综合得分 | 基于归一化后的理论范围 | [0, 1] 或 [0, 100] |
| 分类判别 | 准确率 | 基于类别数和随机基线 | 二分类: 0.5-1.0；多分类: 1/K-1.0 |
| 聚类分析 | 簇数 | 基于数据规模和领域知识 | 2 到 sqrt(n) |
| 信号处理 | 主频/周期 | 基于采样率和信号长度 | 主频: 0 到 Nyquist频率 |
| 经济建模 | 增长率/弹性 | 基于经济常识 | GDP增长率: -15% 到 +25% |

### 与下游的对接

`expected_output_ranges` 通过 Pipeline 传递给 mle-solver 的上下文绑定块，用于：
1. 替代硬编码阈值（如 `f_min = 2 * n * d_min * cos_theta` 中的 `d_min` 来自 `expected_output_ranges`）
2. 在阶段4.6方法一致性检查中，辅助判断哪个方法的结果更合理
3. 在 model-validation 中作为合理性检查的参考范围

---

## v5 新增：物理实体类型自动识别与约束提取

### 物理实体类型分类器（v5 增强）

在问题分析的第一步，必须运行以下分类器自动识别问题中的物理实体类型：

```python
def classify_physical_entities(problem_text: str, data: dict) -> dict:
    """自动识别问题中的物理实体类型，并提取对应的约束方程"""
    
    entity_detectors = {
        # 无人机/飞行器（必须检测等X约束）
        "飞行器/无人机": {
            "keywords": ["无人机", "飞行器", "巡飞", "巡航", "飞行"],
            "constraints": ["等高度", "匀速", "直线飞行", "最大速度", "最小速度"],
            "hard_constraints": [
                {"id": "HA-Z", "expr": "z_i(t) = z_{i,0}", "desc": "等高度巡飞"},
                {"id": "HA-V", "expr": "70 ≤ v_i ≤ 140", "desc": "速度范围"},
                {"id": "HA-DIR", "expr": "v_z = 0", "desc": "方向向量z分量为0"},
            ],
            "anti_patterns": [
                "将三维方向向量直接应用于速度（导致z轴漂移）",
                "忽略等高度约束（z坐标变化）",
            ],
        },
        "导弹/弹丸": {
            "keywords": ["导弹", "弹丸", "炮弹", "来袭", "制导"],
            "constraints": ["匀速", "直线飞行", "方向直指目标"],
            "hard_constraints": [
                {"id": "HA-MDIR", "expr": "d_j = -M_{j,0}/|M_{j,0}|", "desc": "导弹方向向量"},
            ],
        },
        "烟幕弹/干扰弹": {
            "keywords": ["烟幕", "干扰弹", "投放", "起爆"],
            "constraints": ["自由落体", "起爆延迟", "有效半径", "下沉速度"],
            "hard_constraints": [
                {"id": "HA-BURST", "expr": "z_b ≥ 0", "desc": "起爆高度非负"},
            ],
        },
        "烟幕云团": {
            "keywords": ["云团", "烟幕", "遮蔽", "球体"],
            "constraints": ["球体", "匀速下沉", "有效时间", "有效半径"],
        },
        "被保护目标": {
            "keywords": ["目标", "圆柱体", "保护", "假目标", "诱饵"],
            "constraints": ["静止", "圆柱体形状"],
        },
        "刚体链/绳索": {
            "keywords": ["板凳", "龙身", "链条", "绳索", "连接"],
            "constraints": ["弦长约束", "刚性连接"],
            "hard_constraints": [
                {"id": "HA-CHORD", "expr": "|P_i - P_{i-1}| = L", "desc": "弦长约束"},
            ],
            "anti_patterns": [
                "以弧代弦（弧长偏移代替弦长约束）",
                "质点近似（忽略刚性体尺寸）",
            ],
        },
    }
    
    detected = []
    for entity_type, detector in entity_detectors.items():
        if any(kw in problem_text for kw in detector["keywords"]):
            detected.append({
                "entity_type": entity_type,
                "constraints": detector["constraints"],
                "hard_constraints": detector.get("hard_constraints", []),
                "anti_patterns": detector.get("anti_patterns", []),
            })
    
    return {"entities": detected, "total_constraints": sum(len(e["constraints"]) for e in detected)}
```

### 等X约束自动检测（v5 新增）

对于任何物理建模问题，必须自动检测所有"等X"约束（等高度、等速、等温、等压、等间距...）：

```python
def detect_constant_constraints(problem_text: str) -> list:
    """自动检测问题中的'等X'约束"""
    
    constant_patterns = {
        "等高度": {
            "keywords": ["等高度", "定高", "同一高度", "高度不变", "z坐标不变", "巡飞"],
            "math": "z_i(t) = z_{i,0}",
            "hard_assertion": "HA-ALT",
            "violation_check": "检测所有时刻z坐标是否恒定",
            "severity": "致命",
        },
        "等速": {
            "keywords": ["匀速", "等速", "速度恒定", "恒定速度", "速度不变"],
            "math": "v_i(t) = v_{i,0}",
            "hard_assertion": "HA-SPD",
            "violation_check": "检测所有时刻速度模是否恒定",
            "severity": "致命",
        },
        "等温": {
            "keywords": ["等温", "恒温", "温度不变", "温度恒定"],
            "math": "T(t) = T_0",
            "hard_assertion": "HA-TMP",
            "severity": "高",
        },
        "等压": {
            "keywords": ["等压", "恒压", "压力不变"],
            "math": "P(t) = P_0",
            "hard_assertion": "HA-PRS",
            "severity": "高",
        },
        "等间距": {
            "keywords": ["等间距", "等距", "间距不变", "固定距离", "弦长"],
            "math": "|P_i - P_{i-1}| = L",
            "hard_assertion": "HA-DIST",
            "violation_check": "检测所有相邻质点间距是否恒为L",
            "severity": "致命",
        },
    }
    
    detected = []
    for const_name, pattern in constant_patterns.items():
        if any(kw in problem_text for kw in pattern["keywords"]):
            detected.append({
                "constraint_name": const_name,
                "math_expression": pattern["math"],
                "hard_assertion_id": pattern["hard_assertion"],
                "severity": pattern["severity"],
            })
    
    return detected
```

### 方向向量维度验证（v5 新增）

对于等高度飞行场景，必须验证方向向量只有水平分量：

```python
def verify_direction_vector_dimensionality(entity_type: str, constraints: list) -> dict:
    """验证方向向量的维度与物理约束一致"""
    
    if "等高度" in [c["constraint_name"] for c in constraints]:
        return {
            "check": "方向向量维度验证",
            "rule": "方向向量 = (cosθ, sinθ, 0)，z分量必须为0",
            "correct_form": "d_i = (cosθ_i, sinθ_i, 0)",
            "wrong_form": "d_i = (cosα, cosβ, cosγ) 或 d_i = -D_{i,0}/|D_{i,0}|",
            "hard_assertion": "HA-DIR: v_z = 0",
            "verdict": "必须锁定",
        }
    return {"check": "方向向量维度验证", "verdict": "无需锁定（无等高度约束）"}
```

---

## v5 新增：约束完整性检查清单

在完成问题分析后，必须逐项检查以下三层约束是否完整：

### 第一层：物理约束（Physical Constraints）

```python
PHYSICAL_CONSTRAINT_CHECKLIST = [
    {"id": "PC-1", "check": "所有运动实体的速度范围是否明确？", "example": "70 ≤ v ≤ 140 m/s"},
    {"id": "PC-2", "check": "所有运动实体的运动方式是否明确？", "example": "匀速直线/自由落体/匀速下沉"},
    {"id": "PC-3", "check": "所有'等X'约束是否已识别并生成硬断言？", "example": "等高度→HA-ALT"},
    {"id": "PC-4", "check": "方向向量的维度是否与物理约束一致？", "example": "等高度→z分量=0"},
    {"id": "PC-5", "check": "重力/空气阻力/摩擦力是否已考虑？", "example": "g=9.8, 空气阻力见假设1"},
    {"id": "PC-6", "check": "所有实体的尺寸/形状是否已建模？", "example": "球体半径10m, 圆柱体r=7m h=10m"},
    {"id": "PC-7", "check": "所有空间边界是否已转化为不等式？", "example": "z_b ≥ 0, R_c ≤ 10"},
    {"id": "PC-8", "check": "几何判定方法是否使用连续指标？", "example": "连续遮蔽率≥0.9, 非8点AND"},
]
```

### 第二层：逻辑约束（Logical Constraints）

```python
LOGICAL_CONSTRAINT_CHECKLIST = [
    {"id": "LC-1", "check": "投放间隔是否已约束？", "example": "t_{r,i+1} - t_{r,i} ≥ 1"},
    {"id": "LC-2", "check": "起爆延迟是否非负？", "example": "t_d ≥ 0"},
    {"id": "LC-3", "check": "实体数量上限是否已约束？", "example": "每架无人机最多3枚弹"},
    {"id": "LC-4", "check": "是否有互斥约束？", "example": "同一无人机不能同时服务两个导弹"},
]
```

### 第三层：优化约束（Optimization Constraints）

```python
OPTIMIZATION_CONSTRAINT_CHECKLIST = [
    {"id": "OC-1", "check": "目标函数是否已明确定义？", "example": "max T_shield"},
    {"id": "OC-2", "check": "目标函数的光滑性是否已判定？", "example": "分段常值→禁止SQP；整数变量→禁止梯度方法"},
    {"id": "OC-3", "check": "决策变量是否已全部列出？", "example": "θ, v, t_r, t_d"},
    {"id": "OC-4", "check": "是否是多智能体协同？如何建模？", "example": "统一MINLP vs 独立优化+合并"},
]
```

---


## v11 新增能力速览

| 能力 | v10 | v11 |
|------|:--:|:--:|
| C题"时序预测+优化"两阶段路由 | 无 | 自动识别C题中需要"先预测后优化"的子问题，路由 ARIMA/Prophet/Holt-Winters → 优化方法 |
| FP-Growth 关联规则挖掘 | 无 | 自动检测"购物篮分析"场景，路由 FP-Growth 频繁模式挖掘 |
| Double-log 双对数需求模型 | 无 | 自动检测"需求价格弹性"场景，路由 Double-log 恒弹性模型 |
| 全局启发式优化方法 | 无 | 自动检测非凸/不连续目标函数，路由 PSO/GA/DE 全局优化 |
| VIKOP 多准则评价 | 无 | 自动检测"多单品选择"场景，路由 VIKOP 多准则评级 |
| 蔬菜季节性分类 | 无 | 自动检测"生鲜/蔬菜"场景，路由 常年性/季节性/时令性 三分法 |
## v12 新增能力速览（2023A题训练驱动）

| 能力 | v11 | v12 |
|------|:--:|:--:|
| A题几何光学路由 | 无 | 自动检测A题"阴影/遮挡/反射"场景，路由 几何光学+蒙特卡洛光线追迹(Möller-Trumbore) |
| 空间布局策略路由 | 无 | 自动检测"定日镜场/天线阵列/传感器部署"场景，路由 同心圆密排+高度-半径耦合 |
| 双层规划架构路由 | 无 | 搜索空间>5维时自动路由 双层规划（外层DE布局结构+内层PSO姿态优化） |
| 截断效率模型路由 | 无 | 自动检测"光斑/能量分布"场景，路由 2D高斯能量分布(非均匀光斑) |
| 外部基准验证要求 | 无 | A题物理建模自动标记"需外部基准验证"（PS10/Gemasolar等实际电站对比） |

## v13 新增能力速览（2023A题训练驱动 v4.0）

| 能力 | v12 | v13 |
|------|:--:|:--:|
| A题阴影遮挡反模式强化 | 路由建议 | **强制规则**：A题物理/工程类阴影遮挡必须使用蒙特卡洛光线追迹，**禁止参数化密度模型** |
| 布局策略反模式强化 | 路由建议 | **强制规则**：定日镜场/天线阵列空间布局必须使用同心圆密排+高度耦合，**禁止简单径向排列** |
| PSO参数下限 | 无 | PSO粒子数≥100、迭代≥200，或路由双层规划 |
| 光斑能量分布反模式 | 路由建议 | **强制规则**：光学截断效率必须使用高斯能量分布，**禁止均匀光斑假设** |

## v14 新增能力速览（2023D题训练驱动）

| 能力 | v13 | v14 |
|------|:--:|:--:|
| 预案集关键词路由 | 无 | 自动检测"预案集/应急预案/动态调整/自适应"关键词，路由多阶段随机控制框架 |
| 离散变量自动检测 | 基础 | 自动检测"羊栏/床位/车辆/设备/人员/台数"等离散资源，标记整数约束 |
| 仿真视界完整性路由 | 无 | 时间序列仿真自动标记 LCM 视界需求，传递至 mle-solver |

### v14 核心：预案集关键词路由

**触发条件**：检测到以下关键词组合时自动激活：
- "预案集" / "应急预案" / "多场景预案" / "动态调整" / "自适应控制"
- 问题同时包含随机因素（随机分布/概率/不确定性）
- 决策变量需要根据观测结果动态调整

**路由逻辑**：
```
if has_contingency_keywords AND has_stochastic_elements:
    route = "multi-stage-stochastic-control"
    framework = "观测-决策-执行闭环"
    min_plans = 3  # 至少3个场景预案
    evaluation_interval = "建议为批次间隔的1-2倍"
    anti_pattern = "静态配置（将动态预案集退化为单一分配方案）"
    
    # 硬断言
    assert has_contingency_plans >= 3, "预案集必须包含≥3个场景预案"
    assert has_decision_trigger, "预案集必须包含决策触发器"
    assert has_evaluation_interval, "预案集必须定义评估周期"
```

### v14 核心：离散变量自动检测

**触发条件**：检测到以下离散资源关键词：
- 空间类：羊栏/栏位/床位/仓位/停车位/机位/展位
- 设备类：车辆/机器/设备/仪器/服务器/终端
- 人员类：人员/护士/医生/教师/工人/操作员
- 计数类：台数/个数/头数/只数/数量

**路由逻辑**：
```
if has_discrete_resource_keywords:
    discrete_vars = extract_discrete_variables()
    constraint_type = "INTEGER"  # 标记为整数约束
    recommended_method = "整数规划(MILP) 或 整数网格搜索"
    anti_pattern = "连续优化（线性规划/梯度下降）输出小数解"
    
    # 传递给 mle-solver
    s1_output["discrete_constraints"] = {
        "variables": discrete_vars,
        "type": "INTEGER",
        "method": "integer_programming_or_grid_search",
        "forbidden": "continuous_optimization_for_discrete_vars"
    }
```

### v14 规则作用域

| 规则 | 白名单（全部匹配才激活） | 黑名单（任一匹配即禁用） |
|------|------------------------|------------------------|
| 预案集路由 | `has_contingency_keywords=True` AND `has_stochastic_elements=True` | 纯确定性优化、无随机因素 |
| 离散变量检测 | `has_discrete_resource_keywords=True` | 纯连续变量（温度/速度/厚度/浓度） |
| 仿真视界路由 | `has_time_series_simulation=True` AND `has_multiple_cycles=True` | 静态优化/稳态分析 |

### 典型误判案例（禁止复现）

| 误判场景 | 错误做法 | 正确做法 |
|---------|---------|---------|
| A题连续厚度优化 | 套用整数网格搜索 | 使用连续优化（SQP/L-BFGS-B） |
| 信号处理频谱分析 | 套用LCM视界检查 | 使用 Nyquist 采样定理 |
| 确定性线性规划 | 套用多阶段随机控制 | 使用标准 LP 求解 |
| C题纯统计预测 | 套用预案集框架 | 使用 ARIMA/Prophet 时间序列预测 |

## 泛化约束与反过拟合（v13 随附，2023A题教训）


**核心原则**：v13 新增的"强制规则"来源于 2023A题（定日镜场优化）训练数据，**仅适用于特定子类型的 A题**。以下规则必须通过白名单匹配后才能激活，通过黑名单过滤防止误触发。**严禁**将 v13 规则套用到 B题、C题、信号处理、图像处理或非光学类 A题。

### 规则作用域白名单/黑名单

| 规则 | 白名单（全部匹配才激活） | 黑名单（任一匹配即禁用） |
|------|------------------------|------------------------|
| 蒙特卡洛光线追迹 | `problem_type=A` AND `physics_subtype=geometric_optics` AND `has_shadow_blocking=True` | 流体力学、热传导、结构力学、电路分析、声学、电磁波 |
| 同心圆密排+高度耦合 | `problem_type=A` AND `has_circular_field=True` AND `has_spatial_layout=True` AND `layout_type=radial` | 线性排列、矩形网格、随机散布、非圆形区域 |
| 双层规划 | `search_space_dim>=5` AND `has_hierarchical_structure=True` AND `problem_type=A` | 维度<5、无分层结构、B题/C题社会/经济问题 |
| 高斯光斑能量分布 | `has_optical_truncation=True` AND `has_energy_spot=True` AND `problem_type=A` | 非光学问题、非截断问题、点源假设 |
| PSO参数下限 | `optimization_method=PSO` AND `search_space_dim>=5` AND `problem_type=A` | 小规模优化(<5维)、B题/C题、梯度方法 |

### 题型互斥检查（强制门禁）

**在激活任何 v13 规则之前，必须先通过以下互斥检查**：

```
# 题型互斥检查（Gate 0）
if problem_type in ("B题社会/经济", "C题数据驱动"):
    DISABLE_ALL_V13_RULES  # 全部 v13 规则不适用
    route_to = "v11 路由体系 (FP-Growth / Double-log / VIKOP / predict-then-optimize)"

if problem_type in ("信号处理", "图像处理"):
    DISABLE_ALL_V13_RULES  # 全部 v13 规则不适用
    route_to = "v7 信号/图像子类型路由"

# 子类型互斥检查（Gate 1）
if problem_type == "A题物理/工程" and physics_subtype not in ("geometric_optics", "solar_thermal"):
    DISABLE_ALL_V13_RULES  # 非光学/光热类 A题，使用 v10 基础物理路由
    route_to = "v10 基础物理路由 (力学/热学/电磁学/流体)"

# 场景特征检查（Gate 2）
if physics_subtype == "geometric_optics":
    if has_shadow_blocking:
        ENABLE ray_tracing_rule
    if has_circular_field:
        ENABLE concentric_packing_rule
    if has_optical_truncation:
        ENABLE gaussian_spot_rule
```

### 典型误判案例（禁止复现）

| 误判场景 | 错误做法 | 正确做法 |
|---------|---------|---------|
| B题经济预测+优化 | 套用双层规划（DE+PSO） | 使用 Double-log + 线性规划/L-BFGS-B |
| C题销量预测+补货 | 套用同心圆密排 | 使用 predict-then-optimize (ARIMA→LP) |
| A题流体力学管道设计 | 套用蒙特卡洛光线追迹 | 使用 CFD/Navier-Stokes 数值求解 |
| A题结构力学桥梁优化 | 套用高斯光斑能量分布 | 使用有限元分析 + 应力约束优化 |
| 图像处理目标检测 | 套用外部基准验证(PS10) | 使用 mAP/IoU 标准验证集 |

### 规则优先级体系（三层分级）

**所有规则按以下三层分级，优先遵循高层级规则：**

| 层级 | 标识 | 含义 | 违反后果 |
|:----:|------|------|---------|
| **L1 全局硬约束** | `[HARD]` | 跨题型始终生效，不可违反 | 模型无效/论文不合格 |
| **L2 条件硬约束** | `[COND]` | 通过 Gate 0/1/2 后强制生效 | 特定题型下模型错误 |
| **L3 软建议** | `[SOFT]` | 最优实践推荐，允许偏离（需说明理由） | 效率/精度可能下降 |

**v13 A题规则属于 L2 条件硬约束**：当 Gate 0+1+2 全部通过时，与 L1 同等强制力；当任一 Gate 不通过时，完全不参与路由决策。与 L1 全局硬约束（如"必须遵循 S1→S7 顺序"）**不冲突**——作用域不同。

**L1 全局硬约束示例**（始终生效）：
- 必须遵循 S1→S2→S3→...→S7 执行顺序
- 所有数值必须来自 paper_macros.json
- CUMCM 论文必须使用三线表

**L2 条件硬约束示例**（作用域内强制）：
- [A题几何光学] 阴影遮挡必须用蒙特卡洛光线追迹
- [A题几何光学] 空间布局必须用同心圆密排+高度耦合
- [>5维优化] PSO粒子数≥100，迭代≥200

**L3 软建议示例**（推荐但允许偏离）：
- 可视化优先使用矢量图格式
- 优化算法优先选择全局启发式方法


### v12 核心：A题几何光学+蒙特卡洛光线追迹路由

**适用场景**：A题（物理/工程类）中涉及阴影、遮挡、反射效率计算的问题。

**触发条件**：检测到以下关键词组合时自动激活：
- "阴影" + "遮挡" / "反射" / "定日镜" / "太阳能" / "光热"
- 问题涉及多个物体间的几何遮挡关系
- 效率计算中阴影遮挡是关键分量

**路由逻辑**：
```
if problem_type == "物理/工程" and has_shadow_blocking:
    route = "monte-carlo-ray-tracing"
    method = "Möller-Trumbore 射线-三角形相交判定 + KD-Tree加速"
    anti_pattern = "参数化密度模型（径向分档/density_factor）"
    
    # 关键约束
    assert shadow_method != "参数化", "A题阴影遮挡禁止使用参数化密度模型"
    assert ray_tracing_method == "Monte Carlo", "必须使用物理光线追迹"
```

### v12 核心：同心圆密排+高度-半径耦合布局路由

**适用场景**：空间布局优化问题（定日镜场、天线阵列、传感器部署）。

**触发条件**：检测到"布局"+"优化"+"圆形区域"+"间距约束"。

**路由逻辑**：
```
if has_spatial_layout and has_circular_field:
    route = "concentric-circle-packing"
    model = "h_k = α×R_k + β（高度-半径耦合）"
    heuristic = "Campo启发式布局规则"
    anti_pattern = "简单径向交错排列（固定步长）"
```

### v12 核心：双层规划优化架构路由

**适用场景**：搜索空间维度>5的优化问题。

**触发条件**：决策变量维度≥5，且存在分层结构（布局结构 vs 姿态参数）。

**路由逻辑**：
```
if search_space_dim >= 5:
    route = "bi-level-planning"
    outer_layer = "DE（差分进化）— 确定布局结构(R_k, N_k)"
    inner_layer = "PSO（粒子群）— 优化单圈姿态(θ_i, φ_i)"
    anti_pattern = "单层PSO/DE直接搜索高维空间"
```



### v11 核心：C题"时序预测+优化"两阶段路由

**适用场景**：C题（数据驱动类）中需要先预测未来需求再优化决策的问题。

**触发条件**：检测到以下关键词组合时自动激活：
- "预测" + "优化" / "定价" / "补货" / "调度"
- 问题包含未来时间点的决策需求
- 数据包含时间序列（日期列）

**路由逻辑**：
```
if problem_type == "数据驱动" and has_time_series and has_optimization:
    route = "predict-then-optimize"
    
    # 第一阶段：预测方法路由
    prediction_methods = {
        "强季节性": ["Holt-Winters", "Prophet", "SARIMA"],
        "弱季节性": ["ARIMA", "LSTM", "XGBoost"],
        "多变量": ["VAR", "LSTM-Multivariate"],
        "稀疏数据": ["Croston", "Moving Average"],
    }
    
    # 第二阶段：优化方法路由
    optimization_methods = {
        "连续决策变量": ["L-BFGS-B", "SLSQP", "IPOPT"],
        "离散决策变量": ["Branch and Bound", "GA", "PSO"],
        "混合整数": ["MINLP → MILP线性化", "NSGA-II", "DE"],
        "组合优化": ["贪心+局部搜索", "模拟退火", "禁忌搜索"],
    }
```

### v11 核心：FP-Growth 关联规则挖掘方法路由

**适用场景**：商超/零售/电商数据的"购物篮分析"——识别单品间的共现购买模式。

**触发条件**：检测到以下关键词时自动激活：
- "关联" + "单品" / "商品" / "产品"
- "共现" / "搭配" / "购物篮"
- 数据包含"交易ID"或"订单ID"列

**路由方法**：
```python
FP_GROWTH_ROUTING = {
    "method": "FP-Growth",
    "reason": "频繁模式挖掘，识别单品间共现购买规则（如{A}→{B}），适合购物篮分析场景",
    "min_support": 0.02,  # 最小支持度（至少2%交易包含）
    "min_confidence": 0.3,  # 最小置信度
    "output": "关联规则列表 + 提升度(lift)排序",
    "alternatives": ["Apriori", "Eclat"],
    "anti_patterns": [
        "仅用Pearson相关代替关联规则（相关系数不反映共现模式）",
        "设置过高的支持度导致无规则输出",
    ],
}
```

### v11 核心：Double-log 双对数需求模型方法路由

**适用场景**：经济学需求函数建模，估计价格弹性。

**触发条件**：检测到以下关键词时自动激活：
- "需求" + "弹性" / "价格"
- "定价" + "销量"
- "成本加成" + "需求函数"

**路由方法**：
```python
DOUBLE_LOG_ROUTING = {
    "method": "Double-log Regression",
    "model": "ln Q = β₀ + β₁·ln P + β₂·ln X + ε",
    "reason": "双对数模型直接估计恒弹性需求函数，β₁即为价格弹性，比线性近似更符合经济学理论",
    "requirements": ["OLS回归", "报告R²和显著性", "异方差检验"],
    "alternatives": ["线性弹性模型（仅当加成率变化<20%时）"],
    "anti_patterns": [
        "线性弹性模型在加成率变化大时精度下降",
        "忽略控制变量导致遗漏变量偏差",
    ],
}
```

### v11 核心：全局启发式优化方法路由

**适用场景**：目标函数非凸/不连续/多峰时的全局优化。

**触发条件**：classify_objective_smoothness() 判定目标函数为不连续或分段常值时自动激活。

**路由方法**：
```python
GLOBAL_OPTIMIZATION_ROUTING = {
    "PSO": {
        "use": "中等规模连续优化（≤100变量）",
        "variant": "GBest-PSO（全局最优粒子群）",
        "reason": "全局搜索能力强，不易陷入局部最优，适合非线性非凸问题",
    },
    "GA": {
        "use": "混合整数/组合优化",
        "variant": "NSGA-II（多目标）",
        "reason": "自然处理离散变量，支持多目标Pareto前沿",
    },
    "DE": {
        "use": "高维连续优化",
        "reason": "差分进化收敛快，适合>50变量场景",
    },
    "SA": {
        "use": "大规模组合优化",
        "reason": "模拟退火适合TSP/调度类问题",
    },
    "anti_patterns": [
        "SQP用于不连续目标函数（导致局部最优）",
        "L-BFGS-B用于混合整数问题（要求梯度）",
        "单一初始点求解（无法验证全局最优性）",
    ],
}
```

### v11 核心：VIKOP 多准则评价方法路由

**适用场景**：需要从多个候选单品中综合选择最优子集。

**触发条件**：检测到以下关键词时自动激活：
- "选择" + "单品" / "商品" / "方案"
- "多维度" + "评价" / "排序"
- 问题包含"≤N个"类型的约束

**路由方法**：
```python
VIKOP_ROUTING = {
    "method": "VIKOP (VIseKriterijumska Optimizacija I Kompromisno Resenje)",
    "reason": "多准则妥协解排序法，从多个维度综合评价单品，比单一利润排序更全面",
    "criteria": [
        "利润贡献度（权重0.35）",
        "需求稳定性（权重0.25）",
        "季节性覆盖（权重0.20）",
        "损耗率（权重0.10）",
        "品类多样性贡献（权重0.10）",
    ],
    "alternatives": ["TOPSIS", "熵权法", "灰色关联"],
    "anti_patterns": [
        "仅按利润排序（忽略需求稳定性和季节性）",
        "权重主观赋值不说明理由",
    ],
}
```

### v11 核心：蔬菜季节性分类数据预处理路由

**适用场景**：生鲜/蔬菜/农产品数据的季节性单品分类。

**触发条件**：检测到以下关键词时自动激活：
- "蔬菜" / "生鲜" / "农产品"
- 数据包含"单品编码"和"销售日期"列

**路由方法**：
```python
VEGETABLE_SEASON_CLASSIFICATION = {
    "method": "销售月份数/总月份数 比率分类",
    "categories": {
        "常年性": {"ratio": "≥0.8", "desc": "几乎全年有销售，应优先选入补货计划"},
        "季节性": {"ratio": "0.3~0.8", "desc": "特定季节销售，需根据当前季节决定"},
        "时令性": {"ratio": "<0.3", "desc": "仅在短时令内销售，需谨慎选择"},
    },
    "usage": "在Q3单品选择中，常年性单品权重+30%，季节性±0%，时令性-30%",
    "anti_patterns": [
        "忽略单品季节性差异，对所有单品同等对待",
        "在非时令季节选择时令性单品",
    ],
}
```

---
