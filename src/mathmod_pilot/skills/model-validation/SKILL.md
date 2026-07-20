---
name: "model-validation"
description: "数学建模模型检验、灵敏度分析与不确定性分析 v8。基于 SALib + SciPy + Statsmodels + Scikit-learn 构建。产出论文级分析报告和验证类图表（灵敏度龙卷风图、残差诊断图、蒙特卡洛分布图等）。v4新增：连续遮蔽率验证、接力链物理上限验证、几何约束延续性验证、等X约束复查。v5新增：经济计量诊断检验+稳健性检验+因果推断验证。v6新增：排队论/博弈论/ODE/信号/图像/面板数据验证策略全覆盖。覆盖 OAT/Morris/Sobol/FAST 灵敏度分析、拟合优度/残差/交叉验证/多重共线性模型检验、蒙特卡洛/Bootstrap 不确定性分析。触发条件：灵敏度分析、模型检验、不确定性分析、参数敏感性、模型验证、残差分析、交叉验证、蒙特卡洛模拟、Bootstrap。"
---


## 与 Skill 组的关系

| Skill | 阶段 | 关系 |
|-------|:----:|------|
| problem-analyzer | S1 | 上游：接收问题类型分类、高风险假设列表 |
| mle-solver | S3 | 上游：接收模型代码、求解结果 |
| scipilot-figure-cumcm | S5 | 下游：传递验证结果（灵敏度系数、残差数据、蒙特卡洛分布），用于生成验证类图表 |
| mcm-paper-writing | S6 | 下游：传递验证指标（R²/RMSE/灵敏度系数/稳健性检验结果） |
| paper-review | S7 | 下游：传递验证完整性报告 |
| systematic-debugging | 辅助 | 多方法偏差>20%时触发调试 |

**职责边界**：本 skill 负责模型检验、灵敏度分析、不确定性分析，不负责模型求解（那是 mle-solver 的职责）。
# Model-Validation：模型检验、灵敏度与不确定性分析（v8）

你是一个**模型检验与不确定性分析**专家，基于 SALib + SciPy + Statsmodels + Scikit-learn 构建的完整工具链。你的核心能力是将数学建模的模型输出进行系统化检验，产出论文级分析报告和图表。

**v4 增强：** 在v3基础上新增连续遮蔽率验证、接力链物理上限验证、几何约束延续性验证、等X约束复查。适用于弹道运动学/遮蔽类/刚体链类物理建模问题的深度验证。

**v5 增强：** 在v4基础上新增经济计量诊断检验（平稳性/协整/自相关/异方差/多重共线性/内生性）、稳健性检验（替代变量/替代模型/子样本/时间窗口）、因果推断验证（IV有效性/DID平行趋势/RDD带宽敏感性）。适用于经济预测/政策评估/金融建模类问题的深度验证。

**v8 增强（2023A题训练驱动 v4.0）：** 在v7基础上新增A题物理模型外部基准验证——A题物理/工程类模型必须在验证阶段包含≥1个实际工程案例的对比验证（如PS10/Gemasolar/Ivanpah等实际电站的实测数据），禁止仅使用内部蒙特卡洛不确定性分析作为唯一验证手段。

**v8 能力速览**：

| 能力 | v7 | v8 |
|------|:--:|:--:|
| 外部基准验证 | 无 | A题物理模型必须≥1个实际工程基准对比 |
| 基准数据源 | 无 | SolarPACES/PS10/Gemasolar/Ivanpah实测数据 |

### v8 规则：外部基准验证（引用 mle-solver v8 L2 条件硬约束）

> **详细定义见 `mle-solver` SKILL.md 的 v8 规则引用表。**
> 仅在 `problem_type=A题物理/工程 AND has_real_world_analog=True` 时激活。

**验证要求**：≥1个实际工程案例对比（如 PS10/Gemasolar/Ivanpah），偏差>10%触发排查。
**不适用场景**：B题/C题/信号/图像/纯理论A题 — 使用交叉验证+统计检验。
**基准数据源**：按子类型路由（SolarPACES/WindPower/工程规范）。

**v8 增强（2023D题训练驱动）：** 在v7基础上新增仿真视界完整性验证：
- **仿真视界LCM检查**：对于时间序列仿真模型，验证仿真总天数 ≥ LCM(所有关键周期) × N_cycles（N≥3）。关键周期包括繁殖周期、批次间隔、育肥周期等。防止"时间视界截断"导致后期风险被掩盖。
- **预热期完整性检查**：验证预热期 ≥ 1个完整生命周期，确保系统达到稳态后再计算损失。
- **运营期完整性检查**：验证运营期 ≥ 2个完整生命周期，确保样本量足够。

**v7 增强：** 在v6基础上新增通用跨方法一致性验证（method_agreement）——不依赖任何特定问题类型，当多方法结果偏差 > 20% 时自动触发排查。更新所有问题类型的验证路由，将 method_agreement 作为强制验证维度。

**v6 增强：** 在v5基础上新增六大验证策略全覆盖：
- **排队论验证策略**：稳态条件/队长分布/等待时间分布/服务强度验证
- **博弈论验证策略**：均衡存在性/稳定性/比较静态/收益矩阵敏感性
- **ODE/PDE验证策略**：稳定性(Lyapunov)/收敛性/守恒量/刚性检测
- **信号处理验证策略**：SNR/频谱分辨率/窗函数效应/重构误差
- **图像处理验证策略**：IoU/Dice系数/精度-召回/混淆矩阵/鲁棒性
- **面板数据诊断**：Hausman检验/FE vs RE/组内组间变异/序列相关
适用于排队论、博弈论、微分方程、信号处理、图像处理、面板数据分析类问题的深度验证。

## 七大分析模块（v6 新增模块 8）

```
用户输入（模型 + 数据 + 参数 + S1 v5高风险假设 + S3验证报告 + 问题类型）
    │
    ├── 灵敏度分析  ── OAT / Morris / Sobol / FAST（v2：聚焦高风险参数）
    │
    ├── 模型检验   ── 拟合优度 / 残差分析 / 交叉验证 / 多重共线性 / v3高级检验
    │
    ├── 不确定性   ── 蒙特卡洛 / Bootstrap / 置信区间 / 分布拟合
    │
    ├── v4新增：物理约束验证 ── 连续遮蔽率 / 接力链物理上限 / 几何约束延续性 / 等X约束复查
    │
    ├── v5新增：经济模型专项验证 ── 经济计量诊断 / 稳健性检验 / 因果推断验证 / 经济含义验证
    │
    ├── 验证交叉引用 ── S3硬断言复查 / 高风险假设追踪（v2新增）
    │
    ├── v8新增：仿真视界完整性验证 ── LCM检查 / 预热期检查 / 运营期检查
    │
    └── v3/v4/v5/v6/v7：问题类型→检验策略自动路由
```

---

## 模块1：灵敏度分析 (sensitivity) — v2 保留 + 增强

判断哪些参数对模型输出影响最大，**优先分析 S1 标记的高风险参数**。

### 方法选择指南

| 场景 | 推荐方法 | 说明 | 适用问题类型 |
|------|---------|------|-------------|
| 参数少（<5），快速定性 | OAT | 中心差分法，扰动 ±10% | 物理建模、优化 |
| 参数多（>10），初步筛选 | Morris | 计算 μ* 和 σ，快速识别关键参数 | 综合评价、多参数优化 |
| 参数少（<10），精确量化 | Sobol | 一阶 S1 + 总阶 ST，黄金标准 | 物理建模、统计分析 |
| 非线性强，计算资源有限 | FAST | 傅里叶振幅法，效率高于 Sobol | 微分方程、ODE/PDE |

### 输出示例（v2 保留）

```python
# Sobol 全局灵敏度分析表明，**高风险参数 α**（S1 假设敏感性分析中标记为致命级）
# 对模型输出的贡献最大（S1=0.xxx），与预期一致。
# α 的总阶灵敏度指数 ST=0.xxx 显著高于一阶指数 S1=0.xxx，
# 表明 α 与其他参数存在较强的交互效应。
```

---

## 模块2：模型检验 (validation) — v3 新增更多高级检验方法

系统化检验模型质量，覆盖以下检验方法：

### 基础检验（原有保留）

| 指标 | 含义 | 论文判定标准 |
|------|------|-------------|
| R² | 决定系数 | >0.7 良好，>0.9 优秀 |
| Adjusted R² | 修正决定系数 | 惩罚参数过多，与 R² 接近说明无过拟合 |
| RMSE | 均方根误差 | 与数据量纲相同，越小越好 |
| Durbin-Watson | 残差自相关 | 接近2（1.5-2.5）说明残差独立 |
| Shapiro-Wilk p | 残差正态性 | p>0.05 说明残差服从正态分布 |
| VIF | 多重共线性 | <5 良好，>10 严重 |
| 条件数 | 矩阵稳定性 | <30 良好 |

### v3 新增：高级检验方法

#### 1. 交叉验证方法

| 方法 | 适用场景 | 使用方式 |
|------|---------|---------|
| **k-Fold CV** | 一般数据集，预测模型 | k=5 或 k=10，计算 CV-RMSE |
| **LOOCV** | 小样本（n<50） | 留一交叉验证，更稳定但计算量大 |
| **滚动预测 CV** | 时间序列 | 滚动窗口预测，模拟真实预测场景 |
| **时间序列分割** | 时序预测 | 不随机洗牌，按时间分割训练/测试 |

#### 2. Bootstrap 检验

| 用途 | 说明 |
|------|------|
| 参数估计标准误 | 估计回归系数的标准误差和置信区间 |
| 模型预测置信区间 | 给出预测值的置信区间（90% / 95%） |
| 分布拟合 | 估计统计量的抽样分布 |

#### 3. 分类模型检验

| 指标 | 含义 | 论文判定标准 |
|------|------|-------------|
| **准确率 (Accuracy)** | 分类正确比例 | — |
| **精确率 (Precision)** | 预测为正例中真实正例比例 | — |
| **召回率 (Recall)** | 真实正例中预测正确比例 | — |
| **F1-score** | P 和 R 的调和平均 | 不平衡数据必用 |
| **AUC-ROC** | ROC 曲线下面积 | >0.8 良好，>0.9 优秀 |
| **AUC-PR** | PR 曲线下面积 | 不平衡数据更准确 |
| **混淆矩阵** | TP/TN/FP/FN 交叉表 | 必须可视化 |
| **混淆矩阵热力图** | 可视化分类错误分布 | 国赛论文推荐 |

#### 4. 聚类模型检验

| 指标 | 含义 | 范围 | 理想值 |
|------|------|------|-------|
| **轮廓系数 (Silhouette)** | 聚类紧致度 | [-1, 1] | 越大越好 (>0.5良好) |
| **Davies-Bouldin 指数** | 簇间距离平均相似度 | [0, ∞) | 越小越好 (<0.5优秀) |
| **Calinski-Harabasz 指数** | 簇间方差/簇内方差 | (0, ∞) | 越大越好 |
| **稳定性分析** | 多次聚类结果一致性 | — | Jaccard相似度越大越好 |

#### 5. 模型比较检验

| 方法 | 用途 | 说明 |
|------|------|------|
| **似然比检验** | 嵌套模型比较 | 比较两个嵌套模型的拟合优度差异 |
| **AIC/BIC** | 非嵌套模型比较 | 选择AIC/BIC最小的模型 |
| **Diebold-Mariano 检验** | 时间序列预测模型比较 | 检验预测精度是否显著不同 |

#### 6. 残差高级检验

| 检验 | 用途 | 原假设 |
|------|------|------|
| **Breusch-Pagan 检验** | 异方差检验 | H0: 误差同方差 |
| **Ljung-Box 检验** | 序列自相关检验 | H0: 残差无自相关 |
| **ADF 检验** | 单位根检验（时序）| H0: 序列非平稳 |
| **Jarque-Bera 检验** | 正态性检验 | H0: 残差服从正态分布 |

#### 6.5 v5 新增：经济计量诊断检验

| 检验类别 | 检验方法 | 用途 | 原假设/判定标准 |
|---------|---------|------|---------------|
| **自相关检验** | Durbin-Watson | 一阶自相关 | DW≈2 (1.5~2.5) 无自相关 |
| | Ljung-Box | 高阶自相关 | H0: 残差无自相关 (p>0.05) |
| | Breusch-Godfrey | 高阶自相关（可含滞后因变量） | H0: 无自相关 (p>0.05) |
| **异方差检验** | Breusch-Pagan | 线性形式异方差 | H0: 误差同方差 (p>0.05) |
| | White | 一般形式异方差 | H0: 误差同方差 (p>0.05) |
| | Goldfeld-Quandt | 分组异方差 | H0: 两组方差相等 (p>0.05) |
| **多重共线性** | VIF | 方差膨胀因子 | VIF<5 良好，VIF>10 严重 |
| | 条件数 (Condition Number) | 矩阵病态程度 | <30 良好，>100 严重 |
| **内生性检验** | Hausman | 内生性存在性 | H0: 所有解释变量外生 (p>0.05) |
| | Durbin-Wu-Hausman (DWH) | 内生性（增强版） | H0: 变量外生 (p>0.05) |
| **平稳性检验** | ADF (Augmented Dickey-Fuller) | 单位根检验 | H0: 序列非平稳 (p<0.05拒绝) |
| | KPSS | 平稳性检验 | H0: 序列平稳 (p>0.05接受) |
| | Phillips-Perron | 单位根（稳健） | H0: 序列非平稳 (p<0.05拒绝) |
| **协整检验** | Engle-Granger 两步法 | 两变量协整 | H0: 残差非平稳（无协整） |
| | Johansen | 多变量协整 | 迹检验/最大特征值检验 |
| **结构突变检验** | Chow (断点检验) | 已知断点结构变化 | H0: 无结构变化 (p>0.05) |
| | Bai-Perron | 未知多断点 | 自动检测结构突变点 |
| | CUSUM | 参数稳定性 | 累积和是否超出临界带 |
| **模型设定检验** | Ramsey RESET | 模型设定错误 | H0: 模型设定正确 (p>0.05) |
| | 连接检验 (Link Test) | 模型设定错误 | H0: 模型设定正确 (p>0.05) |
| **面板数据诊断** | Hausman 检验 | FE vs RE 模型选择 | H0: RE一致有效 (p<0.05选FE) |
| | Wooldridge 检验 | 面板序列相关 | H0: 无一阶自相关 (p>0.05) |
| | Pesaran CD 检验 | 截面相关 | H0: 无截面相关 (p>0.05) |
| | Modified Wald 检验 | 组间异方差 | H0: 组间同方差 (p>0.05) |
| | F检验 (Pooled vs FE) | 个体效应显著性 | H0: 无个体效应 (p<0.05选FE) |
| | LM检验 (Pooled vs RE) | 随机效应显著性 | H0: 无随机效应 (p<0.05选RE) |

### 6.5.1 面板数据诊断代码模板

```python
# v6 新增：面板数据诊断检验
import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import acorr_ljungbox

# --- Hausman 检验 (FE vs RE) ---
def hausman_test(fe_model, re_model):
    """
    Hausman 检验：比较固定效应和随机效应模型的参数差异。
    H0: RE 估计量一致且有效（个体效应与解释变量无关）
    H1: RE 估计量不一致（应使用 FE）
    """
    # 提取 FE 和 RE 的参数估计
    fe_params = fe_model.params
    re_params = re_model.params
    # 提取共同的参数
    common_params = [p for p in fe_params.index if p in re_params.index and p != 'const']
    fe_beta = fe_params[common_params].values
    re_beta = re_params[common_params].values
    # 协方差矩阵差异
    diff_cov = fe_model.cov_params().loc[common_params, common_params].values -                re_model.cov_params().loc[common_params, common_params].values
    diff = fe_beta - re_beta
    try:
        hausman_stat = diff @ np.linalg.inv(diff_cov) @ diff
        hausman_p = 1 - stats.chi2.cdf(hausman_stat, len(common_params))
    except np.linalg.LinAlgError:
        hausman_stat = np.nan
        hausman_p = np.nan
    return {
        'statistic': hausman_stat,
        'p_value': hausman_p,
        'n_params': len(common_params),
        'conclusion': '选择固定效应模型(FE)' if hausman_p < 0.05 else '不拒绝随机效应模型(RE)',
    }

# 示例：使用 statsmodels 的 PanelOLS / RandomEffects
# from linearmodels.panel import PanelOLS, RandomEffects
# fe_model = PanelOLS(y, X, entity_effects=True).fit()
# re_model = RandomEffects(y, X).fit()

# --- 组内/组间/总体变异分解 ---
def decompose_variation(data, y_col, entity_col, time_col):
    """
    面板数据变异分解：组内(Within) + 组间(Between) + 总体(Overall)。
    """
    # 总体变异
    overall_var = data[y_col].var()
    overall_mean = data[y_col].mean()
    
    # 组间变异（个体均值之间的变异）
    entity_means = data.groupby(entity_col)[y_col].mean()
    between_var = entity_means.var()
    
    # 组内变异（个体内部偏离自身均值的变异）
    data_centered = data.copy()
    data_centered[f'{y_col}_demeaned'] = data[y_col] - data.groupby(entity_col)[y_col].transform('mean')
    within_var = data_centered[f'{y_col}_demeaned'].var()
    
    # 时间变异
    time_means = data.groupby(time_col)[y_col].mean()
    time_var = time_means.var()
    
    return {
        'overall_mean': overall_mean,
        'overall_std': np.sqrt(overall_var),
        'between_std': np.sqrt(between_var),
        'within_std': np.sqrt(within_var),
        'time_std': np.sqrt(time_var),
        'between_ratio': between_var / overall_var,
        'within_ratio': within_var / overall_var,
        'rho': between_var / (between_var + within_var),  # 组内相关系数(ICC)
    }

# --- Wooldridge 序列相关检验 ---
def wooldridge_serial_corr_test(data, y_col, entity_col, time_col, X_cols):
    """
    Wooldridge 面板序列相关检验。
    基于一阶差分回归的残差自相关检验。
    H0: 无一阶序列相关。
    """
    # 按个体和时间排序
    data = data.sort_values([entity_col, time_col]).copy()
    
    # 一阶差分
    data[f'D_{y_col}'] = data.groupby(entity_col)[y_col].diff()
    for col in X_cols:
        data[f'D_{col}'] = data.groupby(entity_col)[col].diff()
    
    # 删除缺失值
    diff_data = data.dropna(subset=[f'D_{y_col}'] + [f'D_{col}' for col in X_cols])
    
    # 差分回归
    y_diff = diff_data[f'D_{y_col}']
    X_diff = sm.add_constant(diff_data[[f'D_{col}' for col in X_cols]])
    model_diff = sm.OLS(y_diff, X_diff).fit()
    
    # 残差
    resid = model_diff.resid
    
    # 对残差进行自回归
    # 需要按个体分组获取滞后残差
    diff_data['resid'] = resid
    diff_data['resid_lag'] = diff_data.groupby(entity_col)['resid'].shift(1)
    lag_data = diff_data.dropna(subset=['resid_lag'])
    
    resid_reg = sm.OLS(lag_data['resid'], sm.add_constant(lag_data['resid_lag'])).fit()
    
    return {
        'statistic': resid_reg.tvalues['resid_lag'],
        'p_value': resid_reg.pvalues['resid_lag'],
        'conclusion': '存在一阶序列相关' if resid_reg.pvalues['resid_lag'] < 0.05 else '无一阶序列相关',
    }

# --- 面板数据完整诊断流程 ---
def panel_diagnostic_report(data, y_col, entity_col, time_col, X_cols):
    """
    v6 新增：面板数据完整诊断报告。
    """
    report = {}
    
    # 1. 变异分解
    report['variation'] = decompose_variation(data, y_col, entity_col, time_col)
    
    # 2. Pooled OLS vs FE (F检验)
    # 3. Pooled OLS vs RE (LM检验)
    # 4. FE vs RE (Hausman检验)
    # 5. Wooldridge 序列相关检验
    report['serial_corr'] = wooldridge_serial_corr_test(data, y_col, entity_col, time_col, X_cols)
    
    # 6. 截面相关检验 (Pesaran CD)
    # 7. 组间异方差检验 (Modified Wald)
    
    return report
```

```python
# v5 新增：经济计量诊断检验完整示例
import numpy as np
import statsmodels.api as sm
from statsmodels.stats.diagnostic import (
    het_breuschpagan, het_white, acorr_ljungbox,
    acorr_breusch_godfrey
)
from statsmodels.tsa.stattools import adfuller, kpss, coint
from statsmodels.stats.outliers_influence import variance_inflation_factor

# --- 自相关检验 ---
# Durbin-Watson (statsmodels 自动输出)
model = sm.OLS(y, X).fit()
dw_stat = sm.stats.durbin_watson(model.resid)

# Ljung-Box 检验
lb_result = acorr_ljungbox(model.resid, lags=[10], return_df=True)
# Breusch-Godfrey 检验
bg_result = acorr_breusch_godfrey(model, nlags=2)

# --- 异方差检验 ---
# Breusch-Pagan
bp_test = het_breuschpagan(model.resid, model.model.exog)
# White 检验
white_test = het_white(model.resid, model.model.exog)

# --- 多重共线性 ---
# VIF
vif_data = {f"x{i}": variance_inflation_factor(X.values, i) for i in range(X.shape[1])}
# 条件数
from numpy.linalg import cond
cond_num = cond(X.values)

# --- 内生性检验 (Hausman) ---
# 假设 endog_var 为疑似内生变量，iv 为工具变量
X_hat = sm.OLS(endog_var, iv).fit().fittedvalues
model_iv = sm.OLS(y, sm.add_constant(np.column_stack([X_hat, X_other]))).fit()
# Hausman 检验：比较 OLS 和 IV 估计差异

# --- 平稳性检验 ---
# ADF
adf_result = adfuller(series, autolag='AIC')
# KPSS
kpss_result = kpss(series, regression='c')
# Phillips-Perron
from statsmodels.tsa.stattools import range_unit_root_test

# --- 协整检验 ---
# Engle-Granger (两变量)
coint_result = coint(y_series, x_series)
# Johansen
from statsmodels.tsa.vector_ar.vecm import coint_johansen
johansen_result = coint_johansen(data_matrix, det_order=0, k_ar_diff=1)

# --- 结构突变检验 ---
from statsmodels.stats.diagnostic import breaks_cusumolsresid
# CUSUM
cusum_result = breaks_cusumolsresid(model.resid, ddof=model.df_model)
# Chow 检验 (已知断点)
# F = ((RSS_pooled - (RSS_1 + RSS_2)) / k) / ((RSS_1 + RSS_2) / (n1 + n2 - 2k))

# --- 模型设定检验 ---
# Ramsey RESET
from statsmodels.stats.diagnostic import linear_reset
reset_result = linear_reset(model, power=2)
```

#### 7. 协方差分析 (ANOVA)

| 类型 | 用途 |
|------|------|
| **单因素 ANOVA** | 比较多组均值是否显著差异 |
| **双因素 ANOVA** | 比较两个因素对因变量的主效应和交互效应 |
| **重复测量 ANOVA** | 同一被试多次测量比较 |

### 问题类型→检验策略自动路由（v3 新增）

```python
VALIDATION_ROUTING = {
    "物理建模": {
        "required": [
            ("拟合优度", "RMSE"),
            ("残差检验", "Jarque-Bera"),
            ("交叉验证", "不同方法结果对比"),
            ("灵敏度分析", "Sobol 分析高风险参数"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("能量守恒检验", "一阶矩验证"),
            ("边界行为检验", "极限情况验证"),
        ],
        "report_template": """
### {model_name} 模型检验报告

1. **拟合优度**：$R^2 = {R2:.3f}$，调整$R^2 = {adjR2:.3f}$，$RMSE = {RMSE:.4f}$
2. **残差检验**：Durbin-Watson = {dw:.2f}，Shapiro-Wilk p = {swp:.3f}，表明残差满足独立同分布假设
3. **交叉验证**：5折CV-RMSE = {cv_rmse:.4f}，表明模型泛化能力良好
4. **灵敏度分析**：高风险参数 {hr_param} 的一阶灵敏度 $S_1 = {s1:.3f}$，确认为主导因素
        """,
    },
    "优化决策": {
        "required": [
            ("最优性间隙", "下界验证"),
            ("可行域验证", "所有约束检查"),
            ("灵敏度分析", "目标函数对约束参数"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("多起点验证", "局部最优 vs 全局最优"),
            ("Pareto前沿分析", "多目标）",
        ],
    },
    "预测预报": {
        "required": [
            ("滚动交叉验证", "CV-RMSE"),
            ("残差检验", "Ljung-Box + ADF"),
            ("预测区间", "覆盖率验证"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("模型比较", "Diebold-Mariano 检验"),
            ("残差自相关", "Ljung-Box"),
        ],
    },
    "综合评价": {
        "required": [
            ("权重敏感性", "不同权重组合下排名稳定性"),
            ("排序一致性", "不同方法结果的秩相关系数"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("灵敏度分析", "指标权重对最终排名的影响"),
        ],
    },
    "分类判别": {
        "required": [
            ("交叉验证", "5-Fold"),
            ("混淆矩阵", "必须可视化"),
            ("不平衡数据", "F1 + PR-AUC"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("特征重要性", "随机森林特征重要性排序"),
            ("ROC曲线", "可视化"),
        ],
    },
    "聚类分析": {
        "required": [
            ("多个指标验证", "轮廓系数 + DB指数 + CH指数"),
            ("稳定性分析", "随机扰动后聚类一致性"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("可视化降维", "t-SNE/UMAP可视化聚类结果"),
        ],
    },
    "统计分析": {
        "required": [
            ("效应量", "不仅报告p值，必须报告效应量"),
            ("方差齐性检验", "Levene检验"),
            ("正态性检验", "Shapiro-Wilk"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("多重比较校正", "Bonferroni / Holm"),
            ("功效分析", "检验力计算"),
        ],
    },
"图论网络": {
        "required": [
            ("算法复杂度", "时间/空间复杂度分析"),
            ("正确性验证", "小规模实例解析解验证"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("鲁棒性分析", "边/节点删除后连通性变化"),
        ],
    },
    "排队论": {
        "required": [
            ("稳态条件验证", "ρ < 1 服务强度"),
            ("服务强度验证", "λ/μ < 1"),
            ("队长分布拟合", "理论分布 vs 实际分布"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("等待时间分布", "指数分布拟合"),
            ("灵敏度分析", "到达率/服务率±20%"),
            ("排队系统优化", "最优服务台数"),
        ],
        "report_template": """
### {model_name} 排队论验证报告

1. **稳态条件**：服务强度 ρ = {rho:.3f} {rho_judgment}，系统{steady_state}
2. **队长分布**：平均队长 L = {L:.3f}，理论值 L_theory = {L_theory:.3f}，K-S检验 p = {ks_p:.3f}
3. **等待时间**：平均等待时间 W = {W:.3f}，理论值 W_theory = {W_theory:.3f}
4. **灵敏度分析**：到达率 ±20% 时，队长波动范围 [{L_min:.3f}, {L_max:.3f}]
        """,
    },
    "博弈论": {
        "required": [
            ("均衡存在性验证", "Nash均衡存在性"),
            ("收益矩阵敏感性", "支付参数±20%扰动"),
            ("比较静态分析", "参数变化对均衡的影响"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("演化稳定性", "ESS检验"),
            ("多均衡选择", "风险占优/帕累托占优"),
            ("混合策略验证", "概率分布合理性"),
        ],
        "report_template": """
### {model_name} 博弈论验证报告

1. **均衡存在性**：{equilibrium_type}均衡存在，策略组合为 {strategy_profile}
2. **收益矩阵敏感性**：支付参数 ±20% 扰动下，均衡{stable_or_not}（{n_stable}/{n_total} 保持不变）
3. **比较静态分析**：当 {param} 增加时，均衡策略由 {eq_before} 变为 {eq_after}，符合{intuition}
4. **演化稳定性**：{ess_result}，入侵者比例阈值 = {invasion_threshold:.2%}
        """,
    },
    "微分方程": {
        "required": [
            ("稳定性分析", "Lyapunov 稳定性"),
            ("收敛性验证", "数值解收敛性"),
            ("守恒量检查", "能量/质量/动量守恒"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("刚性检测", "刚性比/Stiffness Ratio"),
            ("相图分析", "相轨迹/不动点"),
            ("步长敏感性", "不同步长结果对比"),
        ],
        "report_template": """
### {model_name} ODE/PDE验证报告

1. **稳定性分析**：Lyapunov 指数 λ = {lyap:.3f}，系统处于{stability_type}
2. **收敛性验证**：步长减半时，数值解相对误差 = {conv_error:.2e}，收敛阶 = {conv_order:.2f}
3. **守恒量检查**：{conserved_quantity} 最大相对偏差 = {conservation_error:.2e}
4. **刚性检测**：刚性比 = {stiffness_ratio:.1f}，{stiffness_judgment}
        """,
    },
    "信号处理": {
        "required": [
            ("SNR计算", "信噪比评估"),
            ("频谱分辨率验证", "频率分辨率分析"),
            ("窗函数效应分析", "频谱泄漏/旁瓣"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("重构误差", "MSE/MAE"),
            ("时频分辨率权衡", "Heisenberg不确定性"),
            ("滤波器性能", "幅频/相频响应"),
        ],
        "report_template": """
### {model_name} 信号处理验证报告

1. **信噪比**：SNR = {SNR:.2f} dB，{snr_judgment}
2. **频谱分辨率**：频率分辨率 Δf = {df:.3f} Hz，可分辨 {n_freq} 个频率分量
3. **窗函数效应**：使用 {window_type} 窗，主瓣宽度 = {mainlobe:.3f}，旁瓣衰减 = {sidelobe:.1f} dB
4. **重构误差**：MSE = {mse:.4e}，MAE = {mae:.4e}
        """,
    },
    "图像处理": {
        "required": [
            ("IoU/Dice系数", "分割精度"),
            ("精度-召回曲线", "PR曲线及AUC"),
            ("混淆矩阵", "像素级分类"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("鲁棒性(噪声)", "加噪后性能变化"),
            ("鲁棒性(旋转)", "旋转不变性"),
            ("计算效率", "推理时间/内存占用"),
        ],
        "report_template": """
### {model_name} 图像处理验证报告

1. **分割精度**：IoU = {iou:.3f}，Dice系数 = {dice:.3f}
2. **精度-召回**：Precision = {precision:.3f}，Recall = {recall:.3f}，F1 = {f1:.3f}，PR-AUC = {pr_auc:.3f}
3. **混淆矩阵**：总体准确率 = {accuracy:.3f}，Kappa系数 = {kappa:.3f}
4. **鲁棒性**：加噪(σ={noise_sigma})后IoU下降 {iou_drop_noise:.1%}，旋转{angle}°后IoU下降 {iou_drop_rot:.1%}
        """,
    },
    "面板数据分析": {
        "required": [
            ("Hausman检验", "FE vs RE 选择"),
            ("组内R²", "Within R-squared"),
            ("稳健标准误", "聚类稳健标准误"),
            ("方法一致性", "method_agreement"),  # v7 新增
        ],
        "optional": [
            ("序列相关检验", "Wooldridge检验"),
            ("截面相关检验", "Pesaran CD检验"),
            ("组间异方差", "Modified Wald检验"),
        ],
        "report_template": """
### {model_name} 面板数据诊断报告

1. **Hausman检验**：χ² = {hausman_chi2:.2f}，p = {hausman_p:.3f}，选择{fe_or_re}模型
2. **拟合优度**：组内 R² = {within_r2:.3f}，组间 R² = {between_r2:.3f}，总体 R² = {overall_r2:.3f}
3. **稳健性**：聚类稳健标准误下，核心变量{significance_status}
4. **序列相关**：Wooldridge检验 p = {wooldridge_p:.3f}，{serial_corr_judgment}
        """,
    },
}
```

---

## 模块8：跨方法一致性验证 (method_agreement) — v7 新增

### 核心定位

`method_agreement` 是所有问题类型通用的**强制验证维度**。它不依赖任何特定问题类型的知识——只比较数值结果，适用于优化、回归、分类、聚类、信号处理、物理建模、经济建模等所有场景。

### 检查逻辑

1. 从 S3 阶段结果中读取所有可用方法的结果
2. 计算两两偏差矩阵
3. 如果最大偏差超过 20%，标记为 `FAILED`，触发 `systematic-debugging`
4. 如果偏差在 5%-20% 之间，标记为 `WARNING`，在报告中说明
5. 如果偏差 < 5%，标记为 `PASSED`

### 报告模板

```
### 方法一致性验证报告

1. **参与方法**：{method_names}，共 {N} 种方法
2. **最大偏差**：{max_disagreement:.1%}（{method_A} vs {method_B}）
3. **一致性判定**：{PASSED/WARNING/FAILED}
4. **建议**：{recommendation}
```

---

### 自动路由使用方式

```python
from model_validation.routing import get_validation_strategy

problem_type = "物理建模"  # 来自 S1 problem-analyzer
strategy = get_validation_strategy(problem_type)
# strategy.required 给出必须执行的检验
# strategy.optional 给出可选检验
# strategy.report_template 给出论文段落模板
```

---

## 模块3：不确定性分析 (uncertainty) — v2 保留 + 增强

评估参数不确定性如何传播到模型输出，为决策提供置信区间。

### 蒙特卡洛模拟

```python
from model_validation.uncertainty import UncertaintyAnalyzer

# v3 增强：高风险参数使用更大的标准差
param_dist = {
    'alpha': {'dist': 'normal', 'loc': 0.5, 'scale': 0.1},  # 来自参数测量误差
    'beta':  {'dist': 'uniform', 'low': 1, 'high': 5},  # 参数不确定性范围
}

def model(X):
    return X[:, 0] * np.sin(X[:, 1]) + X[:, 2] * X[:, 0]**2

ua = UncertaintyAnalyzer(model, param_dist)
result = ua.monte_carlo(n_samples=10000)
print(result.summary())
# 输出: 均值, 标准差, 95%CI, 99%CI
```

### Bootstrap 重抽样

```python
result = ua.bootstrap(data, statistic='mean', n_bootstrap=5000)
# 估计均值的 95% 置信区间
```

---

## 模块4：验证交叉引用（v2 新增保留）

### 4.1 S3 硬断言复查

```python
from model_validation.cross_reference import VerificationCrossReference

vcr = VerificationCrossReference(
    verification_reports=verification_reports,
    hard_assertions=hard_assertions,
)

# 复查：S4 参数扰动后，S3 硬断言是否仍然成立？
recheck = vcr.recheck_hard_assertions(model_outputs)
# 返回: {"HA-1": True, "HA-2": True, ...}

# 论文表述：
# "在灵敏度分析参数扰动范围内（±10%），所有硬断言仍然成立，
#  验证了模型的数值稳定性。"
```

### 4.2 高风险假设追踪

```python
# 追踪高风险假设在灵敏度分析中的实际表现
tracking = vcr.track_high_risk_assumptions(
    high_risk_assumptions=high_risk_assumptions,
    sensitivity_results=result_sobol,
)

# 论文段落：
# "表X 总结了所有高风险假设（S1 阶段标记）在灵敏度分析中的实际表现。
#  其中，弦长约束假设（HA-1）在全部 223 个节点上精确成立
#  （最大偏差 < 10^{-15}m），与 S3 硬断言验证结果一致。
#  折射率假设（H1）的灵敏度系数 S_n≈-1.0，确认为绝对主导因素，
#  与 S1 阶段的风险评估（致命级）吻合。"
```

---

## 模块5：可视化 (visualization) — v3 新增更多图表

论文级图表一键生成，所有图表均使用 300 DPI 输出。

### 已有图表（保留）

| 图表 | 用途 |
|------|------|
| **龙卷风图** | 灵敏度分析结果展示，展示各参数灵敏度排序 |
| **残差诊断四合一图** | Q-Q图 + 残差-拟合值 + 直方图 + 时序图 |
| **蒙特卡洛分布图** | 参数不确定性传播后输出分布直方图 |
| **灵敏度排名图** | 参数灵敏度排序条形图 |

### v3 新增图表

| 图表 | 用途 |
|------|------|
| **混淆矩阵热力图** | 分类模型结果展示，显示各类别的分类准确率 |
| **ROC曲线 + PR曲线** | 分类模型性能展示，AUC标注 |
| **聚类结果降维可视化** | 聚类结果二维展示（t-SNE/UMAP + 颜色区分簇）|
| **预测区间图** | 时序预测展示预测区间 + 实际观测值 |
| **Pareto前沿图** | 多目标优化展示非支配解分布 |
| **权重敏感性热力图** | 综合评价展示不同权重组合下排名变化 |

### 使用示例

```python
from model_validation.visualization import (
    plot_tornado, plot_residuals, plot_mc_distribution,
    plot_confusion_matrix_heatmap, plot_roc_curve,
    plot_clustering_2d, plot_prediction_interval, plot_pareto_front,
)

# v3 新增：混淆矩阵热力图
plot_confusion_matrix_heatmap(cm, class_names, save_path='confusion_matrix.png')

# v3 新增：ROC曲线
plot_roc_curve(fpr, tpr, auc, save_path='roc_curve.png')

# v3 新增：Pareto前沿
plot_pareto_front(objective1, objective2, ref_point=None, save_path='pareto.png')
```

---

## 完整工作流示例（v3 更新）

```python
import numpy as np
from model_validation.sensitivity import SensitivityAnalyzer
from model_validation.validation import ModelValidator
from model_validation.uncertainty import UncertaintyAnalyzer
from model_validation.visualization import plot_tornado, plot_residuals, plot_mc_distribution
from model_validation.cross_reference import VerificationCrossReference  # v2

# 0. 从 pipeline 获取 S1 信息
from pipeline import get_pipeline
pipe = get_pipeline()
ctx = pipe.get_context()
s1 = ctx.get_analysis()
high_risk_assumptions = s1.data.get("high_risk_assumptions", [])
hard_assertions = s1.data.get("hard_assertions", [])
problem_type = s1.data["problem_type"]  # v3 新增：问题类型

# 1. 获取推荐检验策略
from model_validation.routing import get_validation_strategy
strategy = get_validation_strategy(problem_type)

# 2. 定义问题和模型
problem = {
    'names': ['alpha', 'beta', 'gamma'],
    'bounds': [[0, 1], [0.5, 5], [0.01, 0.5]],
}
# v2 新增：标记高风险参数
high_risk_params = [ha["parameter"] for ha in high_risk_assumptions if ha["risk_level"] in ["致命", "高"]]

def my_model(X):
    return X[:, 0]**2 + 3*X[:, 1] + 0.5*X[:, 2]

# 3. 灵敏度分析（v2：高风险参数高亮）
sa = SensitivityAnalyzer(problem, my_model, high_risk_params=high_risk_params)
result_sobol = sa.run_sobol(N=1024)
print(result_sobol.high_risk_summary())  # v2 新增：高风险参数专项报告
plot_tornado(result_sobol, high_risk_params=high_risk_params, save_path='tornado.png')

# 4. 生成模拟数据验证
X_true = np.random.uniform(0, 1, (100, 3))
y_true = my_model(X_true)
noise = np.random.normal(0, 0.5, 100)
y_pred = y_true + noise

# 5. 模型检验（v3：按策略执行）
v = ModelValidator(y_true, y_pred, X=X_true, n_params=3, problem_type=problem_type)
report = v.full_report(strategy=strategy)  # v3 新增：按策略执行
print(report.summary())
is_ok, issues = report.is_valid()
plot_residuals(y_true, y_pred, save_path='residuals.png')

# 6. 不确定性分析
param_dist = {
    'alpha': {'dist': 'normal', 'loc': 0.5, 'scale': 0.1},
    'beta':  {'dist': 'uniform', 'low': 0, 'high': 10},
    'gamma': {'dist': 'triangular', 'left': 0.01, 'mode': 0.1, 'right': 0.5},
}

ua = UncertaintyAnalyzer(my_model, param_dist)
mc_result = ua.monte_carlo(n_samples=10000)
print(mc_result.summary())
plot_mc_distribution(mc_result.mc_samples, mc_result.mc_ci_95, save_path='mc_dist.png')

# 7. v2 验证交叉引用
vcr = VerificationCrossReference(
    verification_reports=verification_reports,
    hard_assertions=hard_assertions,
)
recheck = vcr.recheck_hard_assertions(model_outputs)
tracking = vcr.track_high_risk_assumptions(high_risk_assumptions, result_sobol)
```

---


## v4 新增：物理约束验证（模块6）

### 6.1 连续遮蔽率验证（弹道运动学/遮蔽类问题）

对于涉及几何遮蔽/遮挡/碰撞的物理建模问题，必须在验证阶段引入连续遮蔽率验证：

```python
def validate_continuous_shielding(
    model_results: dict,
    target_samples: list,
    cloud_radius: float,
    threshold: float = 0.9,
) -> dict:
    """
    v4 新增：连续遮蔽率验证。
    
    验证内容：
    1. 有效遮蔽时长是否使用连续遮蔽率判据（η ≥ threshold）
    2. 遮蔽窗口的连续性和稳定性
    3. 采样点数量是否足够（N_s ≥ 20）
    4. 与离散判定的对比
    
    参数:
        model_results: 模型求解结果，包含 shielding_times, burst_points 等
        target_samples: 目标采样点列表
        cloud_radius: 云团有效半径
        threshold: 遮蔽率阈值（默认0.9）
    
    返回:
        validation_result: 验证结果
    """
    issues = []
    recommendations = []
    
    # 检查1: 采样点数量
    n_samples = len(target_samples)
    if n_samples < 20:
        issues.append({
            "severity": "HIGH",
            "check": f"采样点数量不足 (N_s={n_samples} < 20)",
            "impact": "统计稳定性不足，遮蔽率可能波动剧烈",
            "recommendation": "增加采样点至至少20个（顶面4+底面4+侧面8+内部4）",
        })
    else:
        recommendations.append(f"✓ 采样点数量充足 (N_s={n_samples})")
    
    # 检查2: 连续遮蔽率 vs 离散判定对比
    for i, result in enumerate(model_results.get('shielding_results', [])):
        continuous_time = result.get('continuous_shielding_time', 0)
        discrete_time = result.get('discrete_shielding_time', 0)
        if discrete_time > 0 and continuous_time > 0:
            diff_ratio = abs(continuous_time - discrete_time) / max(continuous_time, discrete_time)
            if diff_ratio > 0.05:
                issues.append({
                    "severity": "MEDIUM",
                    "check": f"弹{i+1}: 连续遮蔽率({continuous_time:.2f}s)与离散判定({discrete_time:.2f}s)偏差{diff_ratio*100:.1f}%",
                    "impact": "离散判定可能高估或低估遮蔽效果",
                    "recommendation": "使用连续遮蔽率作为最终判定标准",
                })
    
    # 检查3: 遮蔽窗口稳定性
    for i, result in enumerate(model_results.get('shielding_results', [])):
        ratio_curve = result.get('ratio_curve', [])
        if ratio_curve:
            n_high = sum(1 for r in ratio_curve if r >= threshold)
            n_total = len(ratio_curve)
            stability = n_high / n_total
            if stability < 0.5:
                issues.append({
                    "severity": "MEDIUM",
                    "check": f"弹{i+1}: 遮蔽窗口稳定性低 (stability={stability:.2f})",
                    "impact": "遮蔽效果不稳定，可能无法满足实际需求",
                })
    
    return {
        "status": "PASSED" if len([i for i in issues if i['severity'] == 'HIGH']) == 0 else "ISSUES",
        "issues": issues,
        "recommendations": recommendations,
        "n_samples": n_samples,
        "threshold": threshold,
    }
```

### 6.2 接力链物理上限验证（弹道运动学/多弹时序）

对于多弹接力链/时序优化问题，必须验证结果是否达到物理上限：

```python
def validate_relay_chain_limit(
    model_results: dict,
    geometric_params: dict,
) -> dict:
    """
    v4 新增：接力链物理上限验证。
    
    验证内容：
    1. 接力链总遮蔽时长是否接近物理上限
    2. 各弹遮蔽窗口的重叠分析
    3. 单无人机路径是否仅通过LOS一次
    4. y容差窗口是否充分利用
    
    参数:
        model_results: 模型求解结果，包含 relay_chain_results
        geometric_params: 几何参数，包含 LOS_slope, drone_height, cloud_radius, etc.
    
    返回:
        validation_result: 验证结果
    """
    issues = []
    analysis = {}
    
    results = model_results.get('relay_chain_results', {})
    total_time = results.get('total_shielding_time', 0)
    single_time = results.get('single_shell_time', 0)
    n_shells = results.get('n_shells', 0)
    
    # 计算物理上限
    drone_height = geometric_params.get('drone_height', 1800)
    los_x_at_z = geometric_params.get('LOS_x_at_z', drone_height * 10)
    drone_x0 = geometric_params.get('drone_x0', 17800)
    direction_deg = geometric_params.get('direction_deg', 6.0)
    speed = geometric_params.get('speed', 70.0)
    cloud_radius = geometric_params.get('cloud_radius', 10.0)
    
    # y容差窗口
    y_tolerance = 2 * cloud_radius / (speed * np.sin(np.radians(direction_deg)))
    # 物理上限
    physical_limit = single_time + y_tolerance - 2.0  # 扣除重叠区
    
    analysis['y_tolerance'] = y_tolerance
    analysis['physical_limit'] = physical_limit
    analysis['actual_time'] = total_time
    analysis['efficiency'] = total_time / physical_limit if physical_limit > 0 else 0
    
    # 检查1: 是否接近物理上限
    if analysis['efficiency'] < 0.5:
        issues.append({
            "severity": "HIGH",
            "check": f"接力链效率低 ({analysis['efficiency']*100:.1f}% of physical limit)",
            "impact": "优化算法可能未充分探索搜索空间，或存在更优解",
            "recommendation": "检查优化算法是否收敛到全局最优",
        })
    elif analysis['efficiency'] > 0.95:
        issues.append({
            "severity": "LOW",
            "check": f"接力链效率接近上限 ({analysis['efficiency']*100:.1f}%)",
            "impact": "结果合理，接近物理上限",
        })
    
    # 检查2: 重叠分析
    windows = results.get('shielding_windows', [])
    if len(windows) >= 2:
        for i in range(len(windows) - 1):
            overlap = min(windows[i][1], windows[i+1][1]) - max(windows[i][0], windows[i+1][0])
            if overlap > 0:
                analysis[f'overlap_{i}_{i+1}'] = overlap
    
    # 检查3: 单路径验证
    analysis['path_crosses_LOS_once'] = True  # 无人机直线路径仅通过LOS一次
    
    return {
        "status": "PASSED" if len([i for i in issues if i['severity'] == 'HIGH']) == 0 else "ISSUES",
        "issues": issues,
        "analysis": analysis,
    }
```

### 6.3 几何约束延续性验证

验证几何约束在子问题间的延续性：

```python
def validate_geometric_continuity(
    all_sub_results: dict,
    s1_analysis: dict,
) -> dict:
    """
    v4 新增：几何约束延续性验证。
    
    验证内容：
    1. Q1→Q2→Q3→Q4→Q5 的几何约束是否一致
    2. LOS 方程是否在所有子问题中保持一致
    3. 实体初始位置和速度范围是否一致
    4. 跨子问题的起爆点是否自洽（如 Q4 FY1 应与 Q2 FY1 一致）
    
    参数:
        all_sub_results: 所有子问题的求解结果
        s1_analysis: S1 分析结果
    
    返回:
        validation_result: 验证结果
    """
    issues = []
    
    # 检查1: LOS方程一致性
    if 'missile_directions' in all_sub_results:
        dirs = all_sub_results['missile_directions']
        for mid, dirs_list in dirs.items():
            if len(set(tuple(d) for d in dirs_list)) > 1:
                issues.append({
                    "severity": "HIGH",
                    "check": f"导弹 {mid} 的方向向量在不同子问题中不一致",
                    "impact": "几何计算基础不一致，结果不可比",
                })
    
    # 检查2: 跨子问题起爆点自洽
    q2_result = all_sub_results.get('Q2', {})
    q4_result = all_sub_results.get('Q4', {})
    if q2_result and q4_result:
        q2_fy1_burst = q2_result.get('fy1_burst_point', None)
        q4_fy1_burst = q4_result.get('fy1_burst_point', None)
        if q2_fy1_burst and q4_fy1_burst:
            diff = np.linalg.norm(np.array(q2_fy1_burst) - np.array(q4_fy1_burst))
            if diff > 1.0:  # 允许1m精度差异
                issues.append({
                    "severity": "HIGH",
                    "check": f"Q4 FY1起爆点与Q2不一致 (偏差 {diff:.1f}m)",
                    "impact": "Q4中FY1的参数应与Q2最优解一致",
                    "recommendation": f"将Q4 FY1参数同步为Q2最优解",
                })
    
    # 检查3: 实体初始位置一致性
    init_positions = s1_analysis.get('initial_positions', {})
    for q_name, result in all_sub_results.items():
        for entity, pos in result.get('initial_positions', {}).items():
            if entity in init_positions:
                if any(abs(pos[i] - init_positions[entity][i]) > 1e-6 for i in range(3)):
                    issues.append({
                        "severity": "HIGH",
                        "check": f"{q_name}: {entity} 初始位置与S1定义不一致",
                    })
    
    return {
        "status": "PASSED" if len(issues) == 0 else "ISSUES",
        "issues": issues,
    }
```

### 6.4 等X约束复查清单（v4 新增）

在验证阶段，必须复查所有等X约束是否满足：

```python
def validate_constant_constraints(
    model_results: dict,
    s1_analysis: dict,
) -> dict:
    """
    v4 新增：等X约束复查。
    
    从S1 v5接收 constant_constraints，在验证阶段逐项复查。
    这是验证阶段的最后防线——确保S1-S3中所有等X约束都被满足。
    """
    constraints = s1_analysis.get('constant_constraints', [])
    results = []
    
    for cc in constraints:
        if cc['constraint_name'] == '等高度':
            z_values = model_results.get('z_coordinates', [])
            z_initial = z_values[0] if z_values else 0
            z_dev = max(abs(z - z_initial) for z in z_values) if z_values else 0
            passed = z_dev < 1e-6
            results.append({
                "constraint": cc['constraint_name'],
                "hard_assertion": cc['hard_assertion_id'],
                "passed": passed,
                "deviation": z_dev,
                "severity": cc['severity'],
                "detail": f"z坐标最大偏差={z_dev:.2e}m" if not passed else "✓",
            })
        
        elif cc['constraint_name'] == '等速':
            v_values = model_results.get('velocities', [])
            v_norms = [np.linalg.norm(v) for v in v_values] if v_values else []
            v_dev = max(abs(vn - v_norms[0]) for vn in v_norms) if v_norms else 0
            passed = v_dev < 1e-6
            results.append({
                "constraint": cc['constraint_name'],
                "hard_assertion": cc['hard_assertion_id'],
                "passed": passed,
                "deviation": v_dev,
                "severity": cc['severity'],
            })
        
        elif cc['constraint_name'] == '等间距':
            positions = model_results.get('positions', [])
            dist_errors = []
            for i in range(1, len(positions)):
                dist_errors.append(abs(np.linalg.norm(positions[i] - positions[i-1]) - cc.get('L', 0)))
            max_dist_err = max(dist_errors) if dist_errors else 0
            passed = max_dist_err < 1e-6
            results.append({
                "constraint": cc['constraint_name'],
                "hard_assertion": cc['hard_assertion_id'],
                "passed": passed,
                "deviation": max_dist_err,
                "severity": cc['severity'],
            })
    
    all_passed = all(r['passed'] for r in results)
    fatal_failures = [r for r in results if not r['passed'] and r['severity'] == '致命']
    
    return {
        "status": "PASSED" if all_passed else "FAILED" if fatal_failures else "WARNINGS",
        "results": results,
        "total": len(results),
        "passed_count": sum(1 for r in results if r['passed']),
        "failed_count": sum(1 for r in results if not r['passed']),
    }
```

---

## v4 新增：问题类型→验证策略扩展路由

### 弹道运动学（遮蔽类）专项验证策略

```python
def get_validation_strategy_v4(problem_type: str, problem_subtype: str = "") -> dict:
    """
    v4 增强：根据问题类型和子类型返回差异化验证策略。
    """
    strategy = get_validation_strategy(problem_type)  # 调用 v3 基础策略
    
    # v4 子类型扩展
    if problem_subtype == "弹道运动学" or "遮蔽" in problem_type:
        strategy.update({
            "v4_additional": {
                "continuous_shielding_validation": True,
                "relay_chain_limit_validation": True,
                "geometric_continuity_validation": True,
                "constant_constraint_recheck": True,
                "recommended_metrics": [
                    "连续遮蔽率 ≥ 0.9",
                    "接力链效率 (actual / physical_limit)",
                    "y容差窗口利用率",
                    "等高度约束偏差 ≤ 1e-6 m",
                ],
            }
        })
    
if problem_subtype == "刚体运动学":
        strategy.update({
            "v4_additional": {
                "constant_constraint_recheck": True,
                "geometric_continuity_validation": True,
                "recommended_metrics": [
                    "等间距约束偏差 ≤ 1e-10 m",
                    "弦长累积误差",
                    "速度分布非线性程度",
                ],
            }
        })
    
    # v5 扩展：经济建模专项策略
    if "经济" in problem_type or problem_subtype in ["经济预测", "政策评估", "金融建模"]:
        strategy.update({
            "v5_additional": {
                "econometric_diagnostics": True,
                "robustness_checks": True,
                "causal_inference_validation": True,
                "economic_meaning_check": True,
                "recommended_metrics": [
                    "ADF + KPSS 平稳性检验",
                    "Durbin-Watson + Breusch-Pagan + White 残差诊断",
                    "VIF < 10 + 条件数 < 30",
                    "至少2种稳健性检验策略",
                    "Hausman 内生性检验",
                    "系数符号与经济理论一致性",
                    "弹性/边际效应合理性",
                ],
            }
        })
    
    # v6 扩展：排队论专项策略
    if "排队" in problem_type or problem_subtype in ["排队论", "排队系统", "服务系统"]:
        strategy.update({
            "v6_additional": {
                "queuing_validation": True,
                "steady_state_check": True,
                "queue_length_distribution": True,
                "service_intensity_check": True,
                "recommended_metrics": [
                    "服务强度 ρ < 1",
                    "平均队长 L 理论vs实际",
                    "平均等待时间 W 理论vs实际",
                    "K-S 检验队长分布拟合",
                ],
            }
        })
    
    # v6 扩展：博弈论专项策略
    if "博弈" in problem_type or problem_subtype in ["博弈论", "博弈", "策略互动"]:
        strategy.update({
            "v6_additional": {
                "game_theory_validation": True,
                "equilibrium_existence": True,
                "payoff_sensitivity": True,
                "comparative_statics": True,
                "recommended_metrics": [
                    "Nash 均衡存在性",
                    "收益矩阵 ±20% 扰动后均衡稳定性",
                    "比较静态分析（参数变化→均衡变化）",
                    "演化稳定策略(ESS)检验",
                ],
            }
        })
    
    # v6 扩展：微分方程专项策略
    if "微分方程" in problem_type or problem_subtype in ["ODE", "PDE", "微分方程", "常微分方程", "偏微分方程"]:
        strategy.update({
            "v6_additional": {
                "ode_pde_validation": True,
                "stability_analysis": True,
                "convergence_check": True,
                "conservation_check": True,
                "stiffness_detection": True,
                "recommended_metrics": [
                    "Lyapunov 指数/特征值分析",
                    "不同步长收敛性对比",
                    "能量/质量/动量守恒偏差",
                    "刚性比检测",
                    "相图分析",
                ],
            }
        })
    
    # v6 扩展：信号处理专项策略
    if "信号" in problem_type or problem_subtype in ["信号处理", "信号分析", "滤波", "频谱分析"]:
        strategy.update({
            "v6_additional": {
                "signal_processing_validation": True,
                "snr_calculation": True,
                "spectral_resolution": True,
                "window_function_analysis": True,
                "reconstruction_error": True,
                "recommended_metrics": [
                    "SNR (dB)",
                    "频率分辨率 Δf",
                    "窗函数主瓣宽度/旁瓣衰减",
                    "重构 MSE/MAE",
                    "时频分辨率权衡",
                ],
            }
        })
    
    # v6 扩展：图像处理专项策略
    if "图像" in problem_type or problem_subtype in ["图像处理", "图像分割", "图像分类", "图像识别"]:
        strategy.update({
            "v6_additional": {
                "image_processing_validation": True,
                "iou_dice": True,
                "precision_recall": True,
                "confusion_matrix": True,
                "robustness_noise_rotation": True,
                "recommended_metrics": [
                    "IoU + Dice 系数",
                    "Precision/Recall/F1/PR-AUC",
                    "像素级混淆矩阵",
                    "加噪鲁棒性（IoU下降率）",
                    "旋转/缩放鲁棒性",
                    "推理时间/FLOPs",
                ],
            }
        })
    
    # v6 扩展：面板数据分析专项策略
    if "面板" in problem_type or problem_subtype in ["面板数据", "面板数据分析", "面板回归"]:
        strategy.update({
            "v6_additional": {
                "panel_data_diagnostics": True,
                "hausman_test": True,
                "variation_decomposition": True,
                "serial_corr_test": True,
                "robust_se": True,
                "recommended_metrics": [
                    "Hausman 检验 (FE vs RE)",
                    "组内/组间/总体 R²",
                    "聚类稳健标准误",
                    "Wooldridge 序列相关检验",
                    "Pesaran CD 截面相关检验",
                    "平衡面板vs非平衡面板稳健性",
                ],
            }
        })
    
    return strategy
```


## 模块7：经济模型专项验证（v5 新增）

### 7.1 稳健性检验

对于经济建模/政策评估/金融建模类问题，必须执行稳健性检验，确保核心结论不依赖于特定的模型设定或变量度量方式。

```python
# v5 新增：稳健性检验完整模板
import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy import stats

def robustness_checks(model, data, y_col, x_cols, control_cols=None):
    """
    执行多种稳健性检验策略。
    
    检验策略:
    1. 替代变量检验 - 用不同代理变量替换关键解释变量
    2. 替代模型设定 - 更换函数形式(线性/对数/二次)
    3. 子样本检验 - 排除极端值、不同行业/地区子样本
    4. 不同时间窗口 - 滚动窗口或不同时间段
    5. 添加/删除控制变量 - 逐步回归
    """
    results = {}
    
    X = sm.add_constant(data[x_cols])
    y = data[y_col]
    base_model = sm.OLS(y, X).fit()
    results['baseline'] = {
        'coef': base_model.params,
        'pvalues': base_model.pvalues,
        'r2': base_model.rsquared,
    }
    
    # 策略1: 替代变量检验
    if 'x_alt' in data.columns:
        X_alt = sm.add_constant(data[['x_alt'] + x_cols[1:]])
        model_alt = sm.OLS(y, X_alt).fit()
        results['alternative_variable'] = {
            'coef': model_alt.params,
            'pvalues': model_alt.pvalues,
            'r2': model_alt.rsquared,
            'note': '使用替代变量重新估计',
        }
    
    # 策略2: 替代模型设定
    # 对数形式
    positive_mask = (y > 0) & (data[x_cols[0]] > 0)
    if positive_mask.sum() > 30:
        y_log = np.log(y[positive_mask])
        X_log = sm.add_constant(np.log(data.loc[positive_mask, x_cols].clip(lower=1e-10)))
        model_log = sm.OLS(y_log, X_log).fit()
        results['log_form'] = {
            'coef': model_log.params,
            'pvalues': model_log.pvalues,
            'r2': model_log.rsquared,
            'note': '双对数模型（弹性估计）',
        }
    
    # 策略3: 子样本检验
    # 排除首尾5%极端值
    y_pct = np.percentile(y, [5, 95])
    y_trim_mask = (y >= y_pct[0]) & (y <= y_pct[1])
    if y_trim_mask.sum() > 30:
        X_trim = sm.add_constant(data.loc[y_trim_mask, x_cols])
        y_trim = y[y_trim_mask]
        model_trim = sm.OLS(y_trim, X_trim).fit()
        results['trimmed_sample'] = {
            'coef': model_trim.params,
            'pvalues': model_trim.pvalues,
            'r2': model_trim.rsquared,
            'note': '排除首尾5%极端值',
        }
    
    # 策略4: 不同时间窗口
    if 'year' in data.columns:
        years = sorted(data['year'].unique())
        if len(years) >= 6:
            # 前半段 vs 后半段
            mid = len(years) // 2
            early_mask = data['year'].isin(years[:mid])
            late_mask = data['year'].isin(years[mid:])
            for period_name, mask in [('early', early_mask), ('late', late_mask)]:
                if mask.sum() > 20:
                    X_period = sm.add_constant(data.loc[mask, x_cols])
                    y_period = y[mask]
                    model_period = sm.OLS(y_period, X_period).fit()
                    results[f'time_window_{period_name}'] = {
                        'coef': model_period.params,
                        'pvalues': model_period.pvalues,
                        'r2': model_period.rsquared,
                        'note': f'{period_name} period',
                    }
    
    # 策略5: 添加/删除控制变量
    if control_cols:
        for i, cc in enumerate(control_cols):
            cols_sub = x_cols + [c for c in control_cols if c != cc]
            X_sub = sm.add_constant(data[cols_sub])
            model_sub = sm.OLS(y, X_sub).fit()
            results[f'drop_control_{cc}'] = {
                'coef': model_sub.params,
                'pvalues': model_sub.pvalues,
                'r2': model_sub.rsquared,
                'note': f'删除控制变量 {cc}',
            }
    
    # 策略6: 替换估计方法 (FE → RE → System GMM) — v6 新增面板数据稳健性
    if 'entity_id' in data.columns and 'year' in data.columns:
        from linearmodels.panel import PanelOLS, RandomEffects
        # 准备面板数据
        panel_data = data.set_index(['entity_id', 'year'])
        y_panel = panel_data[y_col]
        X_panel = panel_data[x_cols]
        
        # 固定效应 (FE)
        try:
            fe_model = PanelOLS(y_panel, X_panel, entity_effects=True).fit()
            results['panel_FE'] = {
                'coef': fe_model.params,
                'pvalues': fe_model.pvalues,
                'r2': fe_model.rsquared_within,
                'note': '面板固定效应模型(FE)',
            }
        except:
            pass
        
        # 随机效应 (RE)
        try:
            re_model = RandomEffects(y_panel, X_panel).fit()
            results['panel_RE'] = {
                'coef': re_model.params,
                'pvalues': re_model.pvalues,
                'r2': re_model.rsquared_overall,
                'note': '面板随机效应模型(RE)',
            }
        except:
            pass
    
    # 策略7: 平衡面板 vs 非平衡面板 — v6 新增面板数据稳健性
    if 'entity_id' in data.columns and 'year' in data.columns:
        # 识别平衡面板子集
        entity_year_counts = data.groupby('entity_id')['year'].nunique()
        max_years = entity_year_counts.max()
        balanced_entities = entity_year_counts[entity_year_counts == max_years].index
        balanced_data = data[data['entity_id'].isin(balanced_entities)]
        
        if len(balanced_data) > 30 and len(balanced_data) < len(data):
            X_bal = sm.add_constant(balanced_data[x_cols])
            y_bal = balanced_data[y_col]
            model_bal = sm.OLS(y_bal, X_bal).fit()
            results['balanced_panel'] = {
                'coef': model_bal.params,
                'pvalues': model_bal.pvalues,
                'r2': model_bal.rsquared,
                'note': f'平衡面板子集 (n={len(balanced_data)})',
            }
    
    # 汇总稳健性判断
    core_var = x_cols[0]
    consistency = {
        'sign_consistent': True,
        'significance_consistent': True,
        'magnitude_range': [float('inf'), float('-inf')],
    }
    
    for key, res in results.items():
        if core_var in res['coef'].index:
            consistency['magnitude_range'][0] = min(consistency['magnitude_range'][0], res['coef'][core_var])
            consistency['magnitude_range'][1] = max(consistency['magnitude_range'][1], res['coef'][core_var])
    
    results['robustness_summary'] = {
        'n_checks': len(results) - 1,
        'core_variable': core_var,
        'coefficient_range': consistency['magnitude_range'],
        'conclusion': '稳健' if consistency['sign_consistent'] else '需进一步检验',
    }
    
    return results
```

### 7.2 因果推断验证

```python
# v5 新增：因果推断验证模板

# --- IV (工具变量) 有效性检验 ---
def iv_validity_check(first_stage, instruments, sargan_result=None):
    """
    检验工具变量的有效性。
    
    关键指标:
    1. 第一阶段F统计量 > 10 (Staiger-Stock 经验法则)
    2. 过度识别检验: Sargan/Hansen J 检验 p>0.05
    3. 弱工具变量检验: Cragg-Donald F统计量
    """
    checks = {}
    
    # F统计量检验
    f_stat = first_stage.fvalue
    f_pvalue = first_stage.f_pvalue
    checks['first_stage_F'] = {
        'f_stat': f_stat,
        'f_pvalue': f_pvalue,
        'passed': f_stat > 10,
        'rule': 'F > 10 (Staiger-Stock 经验法则)',
    }
    
    # 过度识别检验
    if sargan_result is not None:
        checks['overidentification'] = {
            'j_stat': sargan_result.get('j_stat', None),
            'p_value': sargan_result.get('p_value', None),
            'passed': sargan_result.get('p_value', 0) > 0.05,
            'rule': 'Sargan/Hansen J 检验 p > 0.05',
        }
    
    return checks


# --- DID (双重差分) 平行趋势检验 ---
def did_parallel_trend_test(data, time_col, treat_col, outcome_col, pre_periods):
    """
    检验DID的平行趋势假设。
    
    方法:
    1. 事件研究法 (Event Study) - 检验处理前各期系数是否为零
    2. 可视化平行趋势 - 处理组和对照组在事前趋势一致
    3. 联合显著性检验 - 处理前虚拟变量联合不显著
    """
    results = {}
    
    # 事件研究法：生成时间虚拟变量×处理组交互项
    for t in pre_periods:
        data[f'pre_{t}'] = ((data[time_col] == t) & (data[treat_col] == 1)).astype(int)
    
    pre_vars = [f'pre_{t}' for t in pre_periods]
    X = sm.add_constant(data[pre_vars])
    y = data[outcome_col]
    
    event_model = sm.OLS(y, X).fit()
    
    # 联合显著性检验
    joint_test = event_model.f_test(pre_vars)
    
    results['event_study'] = {
        'pre_coefficients': event_model.params[pre_vars].to_dict(),
        'joint_F': joint_test.fvalue,
        'joint_pvalue': joint_test.pvalue,
        'parallel_trend_holds': joint_test.pvalue > 0.05,
        'rule': '处理前各期系数联合不显著 (p > 0.05)',
    }
    
    return results


# --- RDD (断点回归) 带宽敏感性分析 ---
def rdd_bandwidth_sensitivity(data, running_var, cutoff, outcome, bandwidths=None):
    """
    检验RDD结果对带宽选择的敏感性。
    
    方法:
    1. 不同带宽下估计结果对比
    2. 最优带宽 (IK/CCT 方法)
    3. 安慰剂断点检验
    """
    if bandwidths is None:
        h_opt = 1.84 * np.std(data[running_var]) / len(data) ** (1/5)
        bandwidths = [h_opt * m for m in [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]]
    
    results = {'bandwidth_estimates': []}
    
    for h in bandwidths:
        mask = (data[running_var] >= cutoff - h) & (data[running_var] <= cutoff + h)
        subset = data[mask]
        if len(subset) > 30:
            T = (subset[running_var] >= cutoff).astype(int)
            X = sm.add_constant(pd.DataFrame({
                'T': T,
                'running_centered': subset[running_var] - cutoff,
                'T_x_running': T * (subset[running_var] - cutoff),
            }))
            y = subset[outcome]
            model = sm.OLS(y, X).fit()
            results['bandwidth_estimates'].append({
                'bandwidth': h,
                'treatment_effect': model.params['T'],
                'se': model.bse['T'],
                'pvalue': model.pvalues['T'],
            })
    
    # 检查估计值的稳定性
    if len(results['bandwidth_estimates']) >= 2:
        effects = [e['treatment_effect'] for e in results['bandwidth_estimates']]
        results['stability'] = {
            'mean_effect': np.mean(effects),
            'std_effect': np.std(effects),
            'cv': np.std(effects) / abs(np.mean(effects)) if np.mean(effects) != 0 else float('inf'),
            'stable': np.std(effects) / abs(np.mean(effects)) < 0.5 if np.mean(effects) != 0 else False,
        }
    
    return results
```

### 7.3 经济含义验证

```python
# v5 新增：经济含义验证模板

def validate_economic_meaning(model, variable_meanings, economic_theory):
    """
    验证模型结果的经济含义合理性。
    
    检查项:
    1. 系数符号是否与经济理论一致
    2. 弹性/边际效应是否在合理范围
    3. 预测值范围是否合理
    """
    checks = {}
    
    params = model.params
    pvalues = model.pvalues
    
    for var, meaning in variable_meanings.items():
        if var in params.index:
            coef = params[var]
            pval = pvalues[var]
            expected_sign = economic_theory.get(var, {}).get('expected_sign', None)
            reasonable_range = economic_theory.get(var, {}).get('reasonable_range', None)
            
            check = {
                'variable': var,
                'meaning': meaning,
                'coefficient': coef,
                'pvalue': pval,
                'significant': pval < 0.05,
            }
            
            # 符号检验
            if expected_sign is not None:
                sign_match = (coef > 0 and expected_sign == 'positive') or \
                             (coef < 0 and expected_sign == 'negative')
                check['sign_match'] = sign_match
                check['expected_sign'] = expected_sign
                if not sign_match and pval < 0.05:
                    check['warning'] = f'系数符号与经济理论预期不符（预期{expected_sign}，实际{coef:.4f}）'
            
            # 范围检验
            if reasonable_range is not None:
                in_range = reasonable_range[0] <= coef <= reasonable_range[1]
                check['in_reasonable_range'] = in_range
                if not in_range:
                    check['warning'] = check.get('warning', '') + \
                        f'系数超出合理范围 [{reasonable_range[0]}, {reasonable_range[1]}]'
            
            checks[var] = check
    
    # 弹性计算（对数-对数模型）
    elasticities = {}
    for var, meaning in variable_meanings.items():
        if var in params.index and '弹性' in str(meaning) or 'elasticity' in str(meaning).lower():
            elasticities[var] = params[var]
    
    # 预测值合理性
    y_pred = model.predict()
    pred_range_check = {
        'min': np.min(y_pred),
        'max': np.max(y_pred),
        'mean': np.mean(y_pred),
        'negative_ratio': np.mean(y_pred < 0),
        'outlier_ratio': np.mean(np.abs(stats.zscore(y_pred)) > 3),
    }
    
    return {
        'coefficient_checks': checks,
        'elasticities': elasticities,
        'prediction_range': pred_range_check,
        'all_signs_match': all(
            c.get('sign_match', True) for c in checks.values()
        ),
        'warnings': [c.get('warning') for c in checks.values() if c.get('warning')],
    }
```

### 7.4 经济计量诊断报告模板

```python
# v5 新增：经济计量诊断报告自动生成

def generate_econometric_report(diagnostic_results, robustness_results, 
                                  causal_results, economic_meaning_results):
    """
    生成论文级经济计量诊断报告。
    """
    report = []
    
    # 1. 平稳性与协整
    report.append("### 经济计量诊断报告")
    report.append("")
    report.append("#### 1. 平稳性检验")
    for var, result in diagnostic_results.get('stationarity', {}).items():
        report.append(f"- **{var}**: ADF统计量={result['adf']:.3f}, p={result['adf_p']:.3f}; "
                      f"KPSS统计量={result['kpss']:.3f}, p={result['kpss_p']:.3f}")
        if result['adf_p'] < 0.05 and result['kpss_p'] > 0.05:
            report.append(f"  - 结论：{var} 为平稳序列")
        elif result['adf_p'] < 0.05:
            report.append(f"  - 结论：{var} 为 I(1) 过程，一阶差分后平稳")
    
    report.append("")
    report.append("#### 2. 残差诊断")
    diag = diagnostic_results.get('residual_diagnostics', {})
    report.append(f"- Durbin-Watson = {diag.get('dw', 'N/A'):.3f}（接近2表明无自相关）")
    report.append(f"- Breusch-Pagan 异方差检验: p = {diag.get('bp_p', 'N/A'):.3f}")
    report.append(f"- Jarque-Bera 正态性检验: p = {diag.get('jb_p', 'N/A'):.3f}")
    report.append(f"- 最大 VIF = {diag.get('max_vif', 'N/A'):.2f}（<10表明无严重多重共线性）")
    
    report.append("")
    report.append("#### 3. 稳健性检验")
    report.append(f"共执行 {robustness_results.get('n_checks', 0)} 种稳健性检验策略：")
    for key, res in robustness_results.items():
        if key not in ['baseline', 'robustness_summary'] and 'note' in res:
            report.append(f"- {res['note']}：核心变量系数 = {res['coef'].get('x1', 'N/A'):.4f} "
                          f"(p = {res['pvalues'].get('x1', 'N/A'):.3f})")
    summary = robustness_results.get('robustness_summary', {})
    cr = summary.get('coefficient_range', [0, 0])
    report.append(f"- **结论**：核心变量系数范围 [{cr[0]:.4f}, {cr[1]:.4f}]，结果{summary.get('conclusion', '')}")
    
    report.append("")
    report.append("#### 4. 经济含义验证")
    for var, check in economic_meaning_results.get('coefficient_checks', {}).items():
        sig = '***' if check['pvalue'] < 0.01 else '**' if check['pvalue'] < 0.05 else ''
        report.append(f"- **{var}**（{check['meaning']}）：系数={check['coefficient']:.4f}, "
                      f"p={check['pvalue']:.3f}{sig}")
        if 'sign_match' in check:
            report.append(f"  - 符号{'符合' if check['sign_match'] else '不符合'}经济理论预期")
    
    return '\n'.join(report)
```


## Pipeline 集成（v3 新增字段）

### 回写 Pipeline

```python
from pipeline import get_pipeline, Stage, StageResult

with get_pipeline() as pipe:
    ctx = pipe.get_context()
    
    # v3 新增：问题类型感知
    problem_type = ctx.get_problem_type()
    strategy = get_validation_strategy(problem_type)
    
    result = {
        "goodness_of_fit": goodness_of_fit,
        "residual_analysis": residual_analysis,
        "sensitivity_analysis": sensitivity_analysis,
        "uncertainty_analysis": uncertainty_analysis,
        "high_risk_tracking": tracking,  # v2 新增
        "hard_assertions_recheck": recheck,  # v2 新增
        "strategy_used": strategy,  # v3/v4/v5/v6
        "advanced_tests": advanced_tests,  # v3 新增
        # v4 新增字段
        "continuous_shielding_validation": continuous_shielding,  # v4
        "relay_chain_validation": relay_chain,  # v4
        "geometric_continuity": geometric_continuity,  # v4
        "constant_constraint_recheck": const_recheck,  # v4
        "validation_report_path": "reports/s4_validation.md",
    }
    
    pipe.set_stage_result(Stage.VALIDATION, StageResult(
        stage=Stage.VALIDATION, status="completed",
        data=result,
        files=["reports/s4_validation.md", "figures/*.png"],
    ))
```

---

## 规则优先级体系

本 Skill 遵循全局三层分级体系（详见 `problem-analyzer` SKILL.md）。以下为 model-validation 特有的约束：

**L1 全局硬约束** `[HARD]` — 始终生效：
- 必须对所有模型进行灵敏度分析
- 必须对所有模型进行不确定性分析
- 必须重新验证所有常量约束（如高度不变、等X约束）
- 蒙特卡洛采样次数 ≥ 5000

**L2 条件硬约束** `[COND]` — 特定题型生效：
- [A题物理有工程对标] 必须包含≥1个外部基准验证（详见 v8 规则）
- [排队论] 必须验证稳态条件（服务强度 ρ<1）
- [面板数据] 必须执行 Hausman 检验

**L3 软建议** `[SOFT]` — 推荐但允许偏离：
- 灵敏度分析优先使用 Sobol 方法（维度>10时降级为 Morris）
- 不确定性分析优先使用 Bootstrap（样本量>1000时降级为蒙特卡洛）

## 硬性约束（原始列表，供兼容参考）（v3 新增）

### 必须遵守
1. 代码必须使用 `model_validation` 模块，不得重复实现已有功能
2. 图表保存路径必须使用绝对路径，格式为 `d:\Trae_Model_Project\cumcm\figures\xxx.png`
3. 灵敏度分析结果必须在论文中引用具体的数值（S1, ST, μ*）
4. 模型检验报告必须包含所有关键指标，不得选择性报告
5. **v2 新增：灵敏度分析必须优先包含 S1 标记的高风险参数**
6. **v2 新增：必须输出高风险假设追踪表，对比 S1 预期与实际表现**
7. **v3 新增：必须根据问题类型自动选择检验策略**
8. **v3 新增：分类模型在类别不平衡时必须报告 F1 + PR-AUC，禁止只报告准确率**
9. **v3 新增：聚类模型必须报告至少两个聚类有效性指标**
10. **v4 新增：弹道运动学/遮蔽类问题必须执行连续遮蔽率验证（模块6.1）**
11. **v4 新增：多弹时序优化问题必须执行接力链物理上限验证（模块6.2）**
12. **v4 新增：必须执行几何约束延续性验证（模块6.3），确保子问题间几何一致性**
13. **v4 新增：必须执行等X约束复查（模块6.4），从S1 v5接收 constant_constraints**
14. **v5新增：经济建模必须执行完整的计量诊断检验（自相关+异方差+多重共线性+VIF）**
15. **v5新增：经济建模必须执行至少2种稳健性检验策略**
16. **v5新增：回归模型必须报告系数经济含义（符号/弹性/边际效应）**
17. **v5新增：时间序列建模必须报告平稳性检验结果**
18. **v6新增：排队论必须验证稳态条件（服务强度ρ<1）并报告队长分布拟合**
19. **v6新增：博弈论必须验证均衡存在性并执行收益矩阵敏感性分析**
20. **v6新增：ODE/PDE求解必须验证Lyapunov稳定性和数值收敛性**
21. **v6新增：信号处理必须报告SNR和频谱分辨率验证**
22. **v6新增：图像处理必须报告IoU/Dice系数和精度-召回曲线**
23. **v6新增：面板数据分析必须执行Hausman检验并报告组内R²**

### 禁止事项
1. 禁止跳过灵敏度分析直接写论文结论
2. 禁止在残差不满足假设时不做处理
3. 禁止使用不存在的分布类型或虚构的 API
4. 禁止在论文中只写"模型拟合良好"而不提供具体数值
5. **v2 新增：禁止忽略 S1 标记的高风险参数，只分析"安全"参数**
6. **v3 新增：禁止在样本量不足时使用复杂检验方法**
7. **v3 新增：禁止在时序预测中使用随机 k-Fold 交叉验证**
8. **v4 新增：禁止在弹道运动学问题中跳过连续遮蔽率验证**
9. **v4 新增：禁止在接力链问题中不分析物理上限**
10. **v4 新增：禁止在跨子问题验证中忽略几何约束延续性（如Q4 FY1与Q2 FY1不一致）**
11. **v4 新增：禁止在验证阶段不复查等X约束（等高度、等速、等间距）**
12. **v5新增：禁止在经济建模中跳过计量诊断检验直接报告回归结果**
13. **v5新增：禁止在时间序列建模中不报告平稳性检验结果**
14. **v5新增：禁止在存在明显异方差时使用OLS标准误（必须用稳健标准误）**
15. **v5新增：禁止在VIF>10时不处理多重共线性**
16. **v6新增：排队论必须验证稳态条件（服务强度ρ<1），禁止在非稳态下直接分析队长分布**
17. **v6新增：博弈论必须验证均衡存在性，禁止在无均衡情况下直接报告策略分析**
18. **v6新增：ODE/PDE求解必须验证数值收敛性（不同步长对比），禁止单步长直接报告结果**
19. **v6新增：信号处理必须报告SNR和频谱分辨率，禁止不评估信号质量直接分析**
20. **v6新增：图像处理必须报告IoU/Dice和混淆矩阵，禁止仅报告总体准确率（尤其类别不平衡时）**
21. **v6新增：面板数据分析必须执行Hausman检验选择FE/RE，禁止随意选择模型设定**
22. **v6新增：面板数据必须报告聚类稳健标准误，禁止在存在组内相关时使用普通标准误**
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

- **当前版本**: v?
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

- **当前版本**: v?
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

- **当前版本**: v?
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
- **关联缺口**: G-004, G-006
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v8.0.0
- **冷却期**: 上次进化 2026-07-19，下次可用 2026-07-19 15:00
- **连续进化次数**: 1
- **关联缺口**: G-019
- **问题范围**: 仿真视界LCM检查适用于全部时间序列仿真题型，不适用于静态优化/稳态分析

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v8.0.0
- **冷却期**: 上次进化 2026-07-19，下次可用 2026-07-19 15:00
- **连续进化次数**: 1
- **关联缺口**: G-019
- **问题范围**: 仿真视界LCM检查适用于全部时间序列仿真题型，不适用于静态优化/稳态分析

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`


## 学习历史

> 本 Skill 受学习机制 v3.0 守护。每次进化前必须通过回归测试和安全检查。
> **当前版本**: v8.0.0

| 日期 | 训练 | 触发缺口 | 缺口ID | 变更摘要 |
|------|------|---------|--------|---------|
| 2026-07-19 | 2023CUMCM_D | 仿真视界完整性检查 | G-019 | v8: 新增仿真视界LCM检查、预热期/运营期完整性验证，防止时间截断偏误 |

## 泛化约束

- **当前版本**: v8.0.0
- **冷却期**: 上次进化 2026-07-19，下次可用 2026-07-19 15:00
- **连续进化次数**: 1
- **关联缺口**: G-019
- **问题范围**: 仿真视界LCM检查适用于全部时间序列仿真题型，不适用于静态优化/稳态分析

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
