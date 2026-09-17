# 专项约束、反模式与完工清单

> **R2 authority override:** 本文历史性的 20% 多方法差异规则只可触发诊断，不能产生验证 PASS/FAIL。S3 无发布权；S4 必须检查 estimand、共享假设、共同偏差、泄漏与独立证据，并由哈希绑定四态门禁裁决。

## 内容索引

  - v3 新增：高度不变性等X约束检查（阶段3.6扩展）
    - 检查代码模板（v3 增强）
  - v3 新增：目标函数光滑性自动检测（阶段3.0 新增）
    - 光滑性检测代码模板
  - v3 新增：连续指标引导（几何判定修正）
    - 连续指标 vs 离散判定
    - 连续指标代码模板
  - v3 新增：S1 v5 数据接收（阶段0.5扩展）
    - 接收数据结构
  - v3 新增：低维度劫持检测（阶段2.5扩展）
    - 检测项
  - 四层检查机制总结（v7 新增第四层：方法一致性）
  - 硬性约束
    - 必须遵守
    - 禁止事项
  - 反面教材库（持续更新）
    - 错误 #1：以弧代弦（2024 国赛 A 题）
    - 错误 #2：圆弧越界（2024 国赛 A 题）
    - 错误 #3：验证了错误的量（2024 国赛 A 题）
    - 错误 #4：违反等高度巡飞约束（2025 国赛 A 题，v3 新增）
    - 错误 #5：对不连续目标函数使用SQP（2025 国赛 A 题，v3 新增）
    - 错误 #6：二分几何判定压缩搜索空间（2025 国赛 A 题，v3 新增）
    - 错误 #13：魔法数字导致信号截断（信号处理，v7 新增）
    - 错误 #14：多方法结果矛盾未发现（通用，v7 新增）
    - 错误 #7：伪回归——对非平稳序列直接OLS（经济建模，v4 新增）
    - 错误 #8：名义值与实际值混淆（经济建模，v4 新增）
    - 错误 #9：忽略货币时间价值（经济建模，v4 新增）
    - 错误 #10：忽略内生性——OLS估计有偏（经济建模，v4 新增）
    - 错误 #11：忽略市场均衡约束（经济建模，v4 新增）
    - 错误 #12：幸存者偏差（经济建模，v4 新增）
  - 扩展方法库参考
    - 完整方法库（含新增）
    - 模型选择决策框架
  - 完工检查清单

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
| **第四层：方法一致性** | 阶段4.6 | 诊断（非发布门禁） | 题目特定差异触发 Debug | 多方法结果矛盾、某方法提取谐波/伪影；最终由 S4 裁决 |

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
26. **多方法差异超过题目预注册容差时，触发 systematic-debugging；固定 20% 无权证明或否定 correctness，矛盾结果必须交 S4 独立裁决。**

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
25. **禁止在多方法结果超过题目预注册容差时不做排查直接取平均值或任意选一个；不得把固定 20% 当通用门禁。**
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

*本 Skill 基于港科大 MM-Agent (NeurIPS 2025, arXiv:2505.14148) 源码蒸馏。核心 Prompt 逻辑源自 `MMAgent/prompt/template.py`。扩展部分（模型选择框架、启发式算法、三层检查机制）来自国赛获奖经验总结与2024国赛A题复盘教训。*
