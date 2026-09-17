# 灵敏度、模型检验与高级诊断（R2 diagnostic library only）

> **R2 authority override:** 本文的固定阈值、经验评级和示例扰动范围不能产生 release verdict。正式阈值必须预注册并有问题证据；最终结论只由 R2 绑定证据与确定性 gate 聚合。

## 内容索引

  - 七大分析模块（v6 新增模块 8）
  - 模块1：灵敏度分析 (sensitivity) — v2 保留 + 增强
    - 方法选择指南
    - 输出示例（v2 保留）
  - 模块2：模型检验 (validation) — v3 新增更多高级检验方法
    - 基础检验（原有保留）
    - v3 新增：高级检验方法
    - 6.5.1 面板数据诊断代码模板
    - 问题类型→检验策略自动路由（v3 新增）

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
