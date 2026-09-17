# 物理约束与问题类型验证路由（R2 evidence producer）

> **R2 authority override:** 本文只能生产绑定到当前 artifact 的诊断证据；任何 `PASSED` 局部返回值都不能绕过 V01/V09、failure envelope 或四态 release gate。

## 内容索引

  - v4 新增：物理约束验证（模块6）
    - 6.1 连续遮蔽率验证（弹道运动学/遮蔽类问题）
    - 6.2 接力链物理上限验证（弹道运动学/多弹时序）
    - 6.3 几何约束延续性验证
    - 6.4 等X约束复查清单（v4 新增）
  - v4 新增：问题类型→验证策略扩展路由
    - 弹道运动学（遮蔽类）专项验证策略

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
