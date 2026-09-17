# 模型选择、代码生成、执行与交叉验证（R1 formulation boundary）

> **R1 authority override:** 本文中的模型选择、优选表和默认方法仅属历史材料。S3 必须先验证 `candidate_portfolio.json` 与 `selection_verdict.json=ALLOW_FORMULATION`，只能实现已接受候选；发现前提或可解性缺陷时返回 `model-selection`。元启发式只能在更早层级已有不可行或难解证据后使用。

## 内容索引

  - 阶段0：模型选择
    - 15种问题类型方法路由表
    - 物理建模类特殊决策
    - 模型选择反模式
  - v7 新增：无魔法数字原则 (No Magic Numbers)
    - 核心规则
    - 适用范围（对所有问题类型通用）
    - 代码生成自检
  - v7 新增：代码-上下文绑定 (Code-Context Binding)
    - 核心规则
    - 绑定块模板
    - 适用范围
  - v7 新增：多方法交叉验证门禁 (Multi-Method Cross-Validation Gate)
    - 核心规则
    - 适用范围（对所有问题类型通用）
  - 阶段1：消化输入
  - 阶段1.5：约束映射（Constraints -> Code Assertions）
    - 映射规则
    - 代码生成模板
    - 验证失败的影响
  - 阶段2：代码生成（Programmer 角色）
    - 角色定义
    - 实现规范
    - 启发式优化算法使用
    - 输出格式
  - 阶段2.5：代码-物理一致性检查
    - 检查清单
    - 检查示例
  - 阶段3：执行验证与自动纠错（Critic 角色）
    - 执行机制
    - 错误检测（扩展）
    - Debug 反馈回路（扩展）
    - Debug 修正规则
    - 重试策略
    - 输出截断
  - 阶段3.5：硬断言验证
    - 验证流程
    - 断言验证报告模板
  - 阶段3.6：物理合理性检查
    - 检查项
    - 检查代码模板
  - 阶段4：结果解释
  - 阶段4.5：模型-现实交叉验证
    - 验证维度
    - 交叉验证失败处理
  - 阶段5：结论分析与代码结构提取
    - 结论分析
    - 阶段5.5：生成验证报告
    - 失败时触发闭环反思
    - 代码结构提取

## 阶段0：模型选择

在生成代码前，**必须**根据问题类型选择最优模型。加载模型选择决策框架：

```python
# 参考 references/model_selection_guide.md 获取完整决策框架
# 核心原则：问题类型 → 数据特征 → 选择模型 → 给出"为什么选A不选B"的理由
```

### 15种问题类型方法路由表

| 已放行候选族 | 典型场景 | 历史实现例（非选择器） | 其他实现例 | 关键库 |
|---------|---------|---------|---------|--------|
| 评价类（须已放行） | 排序/打分/选优 | 熵权TOPSIS/AHP/模糊综合评价/灰色关联/DEA | 组合赋权、VIKOR；只实现 verdict 指定候选 | numpy, scipy |
| 预测类（须已放行） | 时间序列/回归 | ARIMA、灰色、树模型、LSTM 等实现例 | 复杂度由 selection 证据约束，不按样本区间自动选择 | sklearn, xgboost, lightgbm |
| 优化类（须已放行） | 最大/最小/最优 | LP/ILP/凸或确定性数值路线优先 | GA/PSO/NSGA-II 仅在前级难解证据成立后实现 | PuLP, scipy.optimize |
| 分类/聚类 | 判别/分组 | RandomForest（分类）、DBSCAN（聚类） | SVM、XGBoost、K-Means、GMM | sklearn |
| 物理建模 | 微分方程/仿真 | ODE/PDE求解 -> 蒙特卡洛 | 马尔可夫链、排队论、博弈论 | scipy.integrate |
| 刚体运动学 | 刚性连接体位置/速度 | 弦长约束递推 + 牛顿迭代 | 弧长参数化（仅当柔性体时才可用） | numpy, scipy.optimize.newton |
| 几何约束规划 | 空间边界内路径设计 | 几何约束优化 + 可行域扫描 | Bezier曲线、回旋曲线 | numpy, scipy.optimize |
| 信号处理 | 频谱分析/去噪/滤波 | FFT频谱分析 + 小波去噪 | STFT、Hilbert-Huang变换 | scipy.signal, pywt |
| 图像处理 | 边缘检测/分割/特征提取 | Canny边缘检测 + Otsu阈值分割 + CNN | U-Net、YOLO | opencv, scikit-image |
| 排队论（须已放行） | 服务系统/等待队列 | M/M/c 仅在泊松到达、指数服务、独立平稳等前提成立时 | M/G/c、G/G/c 近似或离散事件仿真候选由 selection 决定 | numpy, scipy.stats |
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

## 阶段2：代码生成（Programmer 角色）

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
# 先把本 skill 自带的 extensions/heuristic_algorithms.py
# 复制到当前任务的 src/ 目录，避免用户路径和安装路径硬编码。
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

## 阶段3：执行验证与自动纠错（Critic 角色）

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
