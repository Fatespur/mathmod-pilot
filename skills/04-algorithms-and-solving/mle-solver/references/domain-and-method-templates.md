# 经济、面板、评价、预测与混合求解模板

## 内容索引

  - 阶段0.6：经济数据特征检查（v4 新增）
    - 检查代码模板
    - 预检结果对后续阶段的影响
    - 面板数据建模方法代码模板（v5 新增）
    - 面板数据建模决策流程
    - AHP层次分析法代码模板（v6 新增）
    - 模糊综合评价代码模板（v6 新增）
    - SVM支持向量机代码模板（v6 新增）
    - 混合求解策略代码模板（v6 新增）: GA + fmincon

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
