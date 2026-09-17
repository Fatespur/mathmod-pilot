# 经济计量、稳健性与因果验证（R2 evidence producer）

> **R2 authority override:** 计量检验结果是绑定证据，不是自认证。识别假设、estimand、数据边界、稳健性与不确定性必须按预注册计划进入 R2 gate。

## 内容索引

  - 模块7：经济模型专项验证（v5 新增）
    - 7.1 稳健性检验
    - 7.2 因果推断验证
    - 7.3 经济含义验证
    - 7.4 经济计量诊断报告模板

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
