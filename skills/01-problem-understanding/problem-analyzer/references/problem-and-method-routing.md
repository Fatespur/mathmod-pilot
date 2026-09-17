# 目标性质、问题类型与方法路由（R1 legacy knowledge only）

> **R1 authority override:** 命名模型、样本量阈值、题型到方法表和默认路线仅保留为历史知识，不得用于 S1 选择、推荐或排序模型。S1 只抽取 `problem_structure.json`；所有模型族与候选比较交给 `model-selection`。

## 内容索引

  - v10 FIX（v11 保留）：目标函数光滑性自动预判（修复缺失整数/离散变量检测）
  - v3 保留核心功能：15种问题类型自动识别（v7 新增信号处理+图像处理）
    - 15种问题类型分类器
    - 建模方法路由表（一站式）
  - v7 新增：ABC题型智能路由模块
  - v2 保留核心功能：第一性原理审查
    - 第一性原理审查流程
    - 假设自攻击测试
    - 硬断言生成

## v10 FIX（v11 保留）：目标函数光滑性自动预判（修复缺失整数/离散变量检测）

**v10 修复说明：** v5-v9版本的 `classify_objective_smoothness()` 存在致命缺陷——它只检测"阶跃关键词"和"连续关键词"两层，完全缺失"整数/离散变量"检测层。当赛题中出现"最大化"、"最小化"等词时（如B题运输优化），函数直接在第二层命中"连续可微"，返回 `gradient_available: True`，推荐SQP/梯度下降。但MILP的决策变量包含整数（火箭发射次数、调度班次），决策空间是离散断裂的，根本不存在导数概念。**修复方法：在函数最前面增加第0层——整数/离散变量优先检测，优先级高于所有其他检测。**

在推荐优化方法前，必须自动判定目标函数的光滑性：

```python
def classify_objective_smoothness(problem_text: str, sub_problem: dict, problem_type: str = None) -> str:
    """自动判定目标函数的光滑性，路由到合适的优化方法
    
    v10 FIX: 增加整数/离散变量检测层（第0层，最高优先级）。
    即使目标函数数学形式是线性的，如果决策变量包含整数（如发射次数、调度班次），
    决策空间是离散断裂的，不存在导数概念，必须使用Branch and Bound/Cutting Plane。
    """
    
    # ═══════════════════════════════════════════════════════════
    # 第0层（最高优先级）：整数/离散变量检测
    # 核心原则：可微性取决于决策空间，而非目标函数的数学形式
    # 即使目标函数是线性的，只要决策变量含整数，空间就是离散的
    # ═══════════════════════════════════════════════════════════
    integer_indicators = [
        # 中文关键词
        "整数", "整数规划", "混合整数", "离散", "整数变量",
        "发射次数", "发射数量", "班次", "次数", "个数", "数量(整数)",
        "调度", "批次", "整数约束",
        # 英文关键词
        "integer", "MILP", "ILP", "integer programming", "discrete",
        "number of launches", "number of", "count", "batch",
        "integer constraint", "mixed-integer",
    ]
    if any(kw in problem_text for kw in integer_indicators):
        return {
            "smoothness": "不可微（离散整数空间）",
            "gradient_available": False,
            "recommended_methods": ["Branch and Bound", "Cutting Plane", "Gurobi/CPLEX/intlinprog"],
            "forbidden_methods": ["SQP", "梯度下降", "牛顿法", "内点法", "任何基于梯度的连续优化方法"],
            "reason": "决策变量包含整数（如发射次数、调度班次），决策空间是离散断裂的，不存在连续可微的概念。即使目标函数数学形式是线性的，整数空间中也无法求导。必须使用分支定界法(Branch and Bound)或割平面法(Cutting Plane)等组合优化方法，借助Gurobi、CPLEX、MATLAB intlinprog等专业MILP求解器进行精确求解。",
            "anti_pattern_id": "错误#28",
        }
    
    # 如果问题类型是"优化决策"且子类型包含"整数规划"/"MILP"
    if problem_type and any(kw in str(problem_type).lower() for kw in ["milp", "ilp", "整数规划", "混合整数"]):
        return {
            "smoothness": "不可微（离散整数空间）",
            "gradient_available": False,
            "recommended_methods": ["Branch and Bound", "Cutting Plane", "Gurobi/CPLEX/intlinprog"],
            "forbidden_methods": ["SQP", "梯度下降", "牛顿法", "内点法", "任何基于梯度的连续优化方法"],
            "reason": "问题类型为MILP/ILP，决策变量包含整数，决策空间为离散空间，不存在导数。必须使用分支定界法或割平面法。",
            "anti_pattern_id": "错误#28",
        }
    
    # 检测阶跃/分段常值特征
    step_indicators = [
        "遮蔽", "遮挡", "碰撞", "接触", "是否", "有无",
        "二值", "bool", "threshold", "判定",
    ]
    if any(kw in problem_text for kw in step_indicators):
        return {
            "smoothness": "分段常值/阶跃",
            "gradient_available": False,
            "recommended_methods": ["网格搜索", "随机搜索", "DE", "GA", "PSO"],
            "forbidden_methods": ["SQP", "梯度下降", "牛顿法", "任何基于梯度的优化"],
            "reason": "目标函数在大部分区域梯度为零，基于梯度的优化会死锁",
            "anti_pattern_id": "错误#9",
        }
    
    # 检测连续特征（仅当目标函数数学形式连续且决策变量为连续变量时）
    continuous_indicators = [
        "最小化", "最大化", "拟合", "误差", "偏差", "距离",
        "连续", "可微", "光滑",
    ]
    if any(kw in problem_text for kw in continuous_indicators):
        return {
            "smoothness": "连续可微",
            "gradient_available": True,
            "recommended_methods": ["SQP", "内点法", "梯度下降"],
            "forbidden_methods": [],
            "reason": "目标函数连续可微，且决策变量为连续变量，梯度方法有效",
            "warning": "注意：此判定仅适用于决策变量全为连续变量的情况。如果存在整数变量，请查看第0层检测结果。"
        }
    
    # 默认：保守判定为不光滑
    return {
        "smoothness": "未知（保守判定为不光滑）",
        "gradient_available": False,
        "recommended_methods": ["网格搜索", "随机搜索", "DE"],
        "forbidden_methods": ["SQP"],
        "reason": "无法确定目标函数光滑性，保守使用零阶方法",
    }
```

---

## v3 保留核心功能：15种问题类型自动识别（v7 新增信号处理+图像处理）

### 15种问题类型分类器

| # | 问题类型 | 关键词 | 数据特征 | 首选方法 | 检验重点 |
|---|---------|--------|---------|---------|---------|
| 1 | 物理建模 | 厚度、速度、力、温度、光、波、干涉 | 光谱/时域信号 | 微分方程+数值求解 | 第一性原理、硬断言 |
| 2 | 优化决策 | 最大化、最小化、最优、调度 | 约束条件列表 | LP→GA/PSO | 可行域验证、灵敏度 |
| 3 | 预测预报 | 预测、趋势、未来、时序 | 时间序列数据 | XGBoost/LightGBM | 预测区间、残差分析 |
| 4 | 综合评价 | 评价、排名、打分、选优 | 多指标矩阵 | 先区分构念、偏好、效率、理想点与排序语义；命名方法仅作候选例 | 权重/归一化敏感性、排序稳定性 |
| 5 | 分类判别 | 分类、识别、判别、诊断 | 带标签数据集 | RandomForest | 混淆矩阵、ROC、F1 |
| 6 | 聚类分析 | 聚类、分组、划分、分层 | 无标签数据集 | DBSCAN | 轮廓系数、DB指数 |
| 7 | 统计分析 | 显著性、检验、相关性 | 实验/调查数据 | 假设检验+效应量 | p值、效应量、检验力 |
| 8 | 图论网络 | 路径、最短、连通、网络 | 邻接/距离矩阵 | 先抽取容量、需求、车辆、仓库、时间窗、流守恒与子环结构 | 可行性、界、复杂度 |
| 9 | 微分方程 | 变化率、扩散、传播、动力学 | 微分方程描述 | Runge-Kutta | 稳定性、收敛性 |
| 10 | 排队论 | 排队、等待、服务 | 到达/服务时间 | 先检验到达/服务分布、独立性、平稳性、优先级、放弃与容量 | 假设检验、稳态/仿真证据 |
| 11 | 博弈论 | 博弈、策略、均衡、收益 | 收益矩阵 | Nash均衡 | 均衡存在性、稳定性 |
| 12 | 混合型 | 多步骤、包含多种特征 | 多类型数据 | 分阶段组合 | 子问题间一致性 |
| 13 | 经济建模 | 经济、金融、市场、供需、价格、投资、GDP | 时间序列/面板数据 | 计量经济学方法 | 平稳性、协整、诊断检验 |
| 14 | 信号处理 | 频谱、滤波、FFT、小波、去噪 | 时域/频域信号 | FFT+小波变换 | SNR、频谱分辨率 |
| 15 | 图像处理 | 图像、像素、边缘、分割、识别 | 图像数据 | CNN/边缘检测 | IoU、Dice系数 |

### 建模方法路由表（一站式）

#### 物理建模子类型路由

| 子类型 | 核心方法 | 备选方法 | 验证策略 | 反模式 |
|--------|---------|---------|---------|--------|
| 刚体运动学 | 弦长约束递推 + 牛顿迭代 | 拉格朗日力学 | 硬断言 + 物理合理性 + 量纲检查 | 弧长代替弦长、质点近似 |
| 波动光学 | FFT频谱分析 + 干涉模型 | 小波变换 | 交叉验证 + 残差分析 | 忽略多光束干涉、单峰近似 |
| 热传导 | 有限差分/有限元 + Crank-Nicolson | 解析解 | 能量守恒 + 稳态极限 | 显式格式不稳定性 |
| 流体力学 | Navier-Stokes简化 + 数值求解 | 伯努利方程 | 质量守恒 + 雷诺数合理性 | 忽略粘性、忽略湍流 |
| 电磁场 | Maxwell方程 + FDTD/FEM | 解析解 | 边界条件 + 能量守恒 | 准静态近似越界 |
| 弹道运动学 | 等高度运动方程（v5自动检测）+ 自由落体 + 连续遮蔽率 | 拉格朗日力学 | 硬断言（等高度+速度范围+起爆高度）+ 连续遮蔽率 + 方向向量维度验证 | 违反等高度约束（v5自动检测）、3D方向向量直接应用、二分几何判定 |
| 信号处理 | FFT频谱分析 + 小波变换 + 滤波去噪 | STFT、Hilbert-Huang | SNR验证 + 频谱分辨率 + 窗函数效应 | 忽略频谱泄漏、窗函数选择不当 |
| 图像处理 | 边缘检测(Canny/Sobel) + 阈值分割(Otsu) + CNN | 形态学处理、Hough变换 | IoU/Dice系数 + 精度-召回 + 混淆矩阵 | 忽略光照变化、过拟合 |
| 系统动力学 | 系统动力学模型(SD) | 微分方程 | 反馈回路验证+存量流量 | 忽略延迟效应 |
| PINN | 物理信息神经网络 | 有限元 | 物理残差+数据残差 | 忽略边界条件权重 |

#### 优化决策子类型路由

| 子类型 | 核心方法 | 备选方法 | 验证策略 | 反模式 |
|--------|---------|---------|---------|--------|
| 线性规划 | 单纯形法/内点法 | 对偶单纯形 | 对偶间隙 + 灵敏度 | 忽略整数约束 |
| 整数规划 | 分支定界 + 割平面 | GA/PSO（大规模） | 最优性间隙 + 下界 | 松弛解不可行；**禁用梯度方法** |
| 非线性规划 | 目标函数光滑→SQP/内点法；不光滑→DE/GA/PSO | 多起点 | KKT条件 + 多起点 | 局部最优、未验证全局性、对不光滑函数使用SQP |
| 多目标优化 | 先检查精确锚点、epsilon-constraint、Pareto 枚举与凸标量化 | 仅在前述路线不可接受且有证据时考虑进化方法（例：NSGA-II / MOEA/D） | 可行性、支配关系、界/间隙、尺度敏感性 | 因“多目标”直接套进化算法 |
| 动态规划 | Bellman递推 | 近似DP | 最优子结构 + 无后效性 | 维度爆炸 |
| 强化学习 | DQN/PPO/A3C | 动态规划 | 奖励函数设计+收敛曲线 | 忽略状态空间维度 |
| 混合求解策略 | GA+fmincon 两阶段 | 单方法 | 全局最优性+局部精化 | 两阶段目标不一致 |

#### 预测预报子类型路由（按样本量）

| 样本信息 | R1 作用 | 禁止推论 | 验证策略 |
|--------|---------|---------|---------|
| 有效样本很少 | 收紧参数/复杂度预算，扩大不确定性披露 | 不得直接选 GM(1,1) 或任何命名模型 | 时间顺序保持的基线、滚动评估、区间覆盖 |
| 有效样本中等 | 比较简约候选并检查正则化与断点 | 不得因跨越固定阈值切换模型族 | 滚动评估、残差依赖、稳定性 |
| 有效样本较多 | 允许筛查更宽复杂度，但仍需 baseline | 不得自动升级为 ML/DL | 滚动评估、校准/区间、漂移审计 |
| n ≥ 1000（超大数据） | LightGBM+Optuna 超参自动调优 | 深度学习 | 早停+学习率调度 | 忽略超参搜索 |
| 多变量 | VAR/VECM（线性）→ XGBoost（非线性） | 随机森林 | Granger因果 + 脉冲响应 |

#### 评价类方法子类型路由（v8 新增）

| 子类型 | 核心方法 | 适用场景 | 验证策略 | 反模式 |
|--------|---------|---------|---------|--------|
| 层次分析法(AHP) | 判断矩阵+特征值法 | 指标少、专家打分 | 一致性比率 CR<0.1 | 指标过多(>9个)导致一致性差 |
| 模糊综合评价 | 隶属度函数+模糊合成 | 定性指标多、边界模糊 | 隶属度合理性+敏感性 | 隶属度函数选择随意 |
| 灰色关联分析 | 邓氏关联度+关联序 | 小样本(n<30)、信息不完全 | 分辨系数ρ敏感性 | 忽略数据预处理 |
| 熵权-TOPSIS | 熵权法+TOPSIS排序 | 多指标客观评价 | 权重敏感性+排序稳定性 | 忽略指标方向性 |
| 组合赋权 | 主客观组合(AHP+熵权) | 需兼顾主观经验与客观数据 | 权重变化对排名影响 | 组合方式机械 |
| DEA(数据包络分析) | CCR/BCC模型 | 多投入多产出效率评价 | 效率值分布+超效率 | 忽略规模报酬假设 |

#### 经济建模子类型路由（v6 新增）

| 子类型 | 核心方法 | 备选方法 | 验证策略 | 反模式 |
|--------|---------|---------|---------|--------|
| 经济预测（低有效样本） | 收紧复杂度预算；naive/drift 等基线 | 多个低参数候选按结构筛查 | 滚动验证 + 区间覆盖 | 按 n 阈值硬选 GM/ARIMA |
| 经济预测（中等有效样本） | 检查趋势、季节、断点、协变量与协整 | 简约时序/统计候选按前提筛查 | 残差依赖 + 预测区间 | 跨固定 n 阈值换族 |
| 经济预测（较高有效样本） | 可扩大复杂度筛查但必须胜过基线 | 树/深度候选仅在结构与泛化证据支持时进入 | 滚动验证 + 漂移审计 | 因样本“多”自动升级复杂模型 |
| 政策评估 | 双重差分法(DID) + 平行趋势检验 | 断点回归(RDD)/合成控制法(SCM) | 安慰剂检验 + 稳健性检验 | 将相关性解释为因果性 |
| 金融建模 | GARCH/EGARCH（波动率） | ARIMA-GARCH / Copula | VaR回测 + Kupiec检验 | 忽略波动率聚集效应 |
| 市场均衡 | 供需联立方程 + 2SLS/3SLS | 一般均衡模型(CGE) | 市场出清条件验证 + 内生性检验 | 忽略市场出清约束 |
| 面板数据分析 | 固定效应(FE) + 随机效应(RE) + Hausman检验 | 系统GMM、差分GMM | Hausman检验 + 组内R² + 稳健标准误 | 忽略个体异质性、混用FE/RE |

#### 机理分析高阶方法路由（v8 新增）

| 子类型 | 核心方法 | 适用场景 | 验证策略 | 反模式 |
|--------|---------|---------|---------|--------|
| GAM(广义加性模型) | 光滑样条+局部回归 | 非线性关系、可加性假设 | 偏残差图+有效自由度+GCV | 忽略交互项、过度光滑 |
| 系统动力学(SD) | 存量流量图+反馈回路 | 复杂系统长期行为仿真 | 极限测试+敏感性分析+历史拟合 | 忽略延迟效应、过度简化反馈 |
| PINN(物理信息神经网络) | 物理约束嵌入神经网络损失 | 有物理定律但数据稀缺 | 物理残差+数据残差+边界条件 | 忽略边界条件权重、损失项不平衡 |

```python
def classify_economic_data_features(data: dict) -> dict:
    """自动检测经济数据特征"""
    features = {
        "stationarity": None,       # ADF检验结果
        "seasonality": False,       # 是否存在季节性
        "trend": None,              # 趋势类型（线性/指数/无）
        "structural_break": False,  # 是否存在结构性断点
        "cointegration": None,      # 协整关系（多变量）
        "frequency": None,          # 数据频率（年/季/月/日）
    }
    return features

def detect_economic_constraints(problem_text: str) -> list:
    """自动检测经济约束"""
    constraints = []
    # 市场均衡约束
    if any(kw in problem_text for kw in ["供需", "市场", "均衡", "出清"]):
        constraints.append({"id": "EC-MKT", "expr": "Q_s = Q_d", "desc": "市场出清条件"})
    # 预算约束
    if any(kw in problem_text for kw in ["预算", "收入", "支出", "成本"]):
        constraints.append({"id": "EC-BUDGET", "expr": "ΣC_i ≤ B", "desc": "预算约束"})
    # 非负约束
    if any(kw in problem_text for kw in ["价格", "数量", "产量", "GDP"]):
        constraints.append({"id": "EC-NONNEG", "expr": "x_i ≥ 0", "desc": "经济变量非负约束"})
    return constraints

def check_common_modeling_traps(model: dict) -> list:
    """通用建模陷阱检查"""
    traps = []
    # 量纲检查
    traps.append({"id": "CMT-DIM", "check": "量纲一致性", "status": "待检查"})
    # 边界检查
    traps.append({"id": "CMT-BOUND", "check": "边界条件合理性", "status": "待检查"})
    # 简化假设审查
    traps.append({"id": "CMT-SIMP", "check": "简化假设误差评估", "status": "待检查"})
    # 线性假设审查
    traps.append({"id": "CMT-LINEAR", "check": "线性假设合理性", "status": "待检查"})
    return traps
```

---

## v7 新增：ABC题型智能路由模块

在问题分析的第一步，必须运行以下分类器自动识别国赛ABC题型：

```python
def classify_abc_problem_type(problem_text: str, data: dict) -> dict:
    """自动识别国赛ABC题型
    
    A题特征: 物理/工程/微分方程/几何/力学
    B题特征: 社会/经济/管理/评价/博弈/排队
    C题特征: 数据驱动/分类/聚类/预测/大量数据
    """
    
    # A题特征检测
    a_keywords = [
        "物理", "工程", "微分方程", "几何", "力学", "运动",
        "热传导", "流体", "电磁", "波动", "光学", "结构",
        "无人机", "飞行器", "导弹", "弹道", "刚体", "链",
        "绳索", "信号", "频谱", "滤波", "图像", "像素",
        "边缘检测", "分割", "识别", "傅里叶", "小波",
    ]
    
    # B题特征检测
    b_keywords = [
        "社会", "经济", "管理", "评价", "博弈", "排队",
        "策略", "均衡", "市场", "供需", "价格", "投资",
        "金融", "GDP", "政策", "规划", "调度", "分配",
        "面板数据", "面板", "个体", "截面", "固定效应",
        "随机效应", "Hausman", "GMM", "双重差分", "DID",
    ]
    
    # C题特征检测
    c_keywords = [
        "数据驱动", "分类", "聚类", "预测", "识别", "机器学习",
        "深度学习", "大数据", "样本", "特征工程", "特征提取",
        "训练集", "测试集", "标签", "标注", "回归", "神经网络",
        "CNN", "RNN", "LSTM", "Transformer", "XGBoost",
    ]
    
    a_score = sum(1 for kw in a_keywords if kw in problem_text)
    b_score = sum(1 for kw in b_keywords if kw in problem_text)
    c_score = sum(1 for kw in c_keywords if kw in problem_text)
    
    # 如果有大量数据，倾向于C题
    if data.get("has_large_dataset", False):
        c_score += 3
    
    scores = {"A": a_score, "B": b_score, "C": c_score}
    
    # 附加上下文信息
    result = {
        "abc_type": max(scores, key=scores.get),
        "scores": scores,
        "confidence": max(scores.values()) / (sum(scores.values()) + 1),
        "type_characteristics": {
            "A": "物理/工程主导——需要建立机理模型，注意物理约束，使用微分方程/数值求解",
            "B": "社会/经济/管理主导——需要建立决策/评价模型，注意经济约束，使用计量/博弈方法",
            "C": "数据驱动主导——需要数据预处理，注意过拟合，使用机器学习/统计学习方法",
        },
    }
    
    # 如果特征不明显，给出混合型建议
    if max(scores.values()) <= 1:
        result["abc_type"] = "混合型"
        result["note"] = "特征不够明显，建议结合赛题上下文人工判断"
    
    return result
```

---

## v2 保留核心功能：第一性原理审查

### 第一性原理审查流程

```python
def first_principles_review(physical_entity_type: str, sub_problems: list) -> dict:
    """
    第一性原理审查：
    1. 提取基本物理/数学约束
    2. 审计每个建模简化对约束的保留程度
    3. 量化简化误差并给出裁决
    """
    return {
        "physical_entity_type": physical_entity_type,
        "fundamental_constraints": [
            {"constraint": "相邻质点距离恒为L", "type": "硬约束", "math": "|P_i - P_{i-1}| = L"},
        ],
        "simplification_audit": [
            {"simplification": "用弧长代替弦长", "error_percent": 2.3, "verdict": "致命"},
        ],
    }
```

### 假设自攻击测试

```python
def assumption_self_attack(assumptions: list) -> list:
    """
    假设自攻击测试：
    对每个假设：构造反例→估计违反影响程度→风险分级
    """
    return [
        {
            "assumption_id": 1,
            "content": "[假设内容]",
            "risk_level": "致命/高/中/低",
            "counter_example": "...",
            "impact_estimate": "如果违反，xxx结果将偏离yy%",
        }
    ]
```

### 硬断言生成

```python
def generate_hard_assertions(constraints: list) -> list:
    """生成硬断言列表"""
    return [
        {
            "id": "HA-1",
            "expression": "||P_i - P_{i-1}| - L| < 1e-10",
            "meaning": "任意相邻板凳间距必须精确等于L",
            "violation_consequence": "板凳龙断开，所有运动学结论无效",
        }
    ]
```

---
