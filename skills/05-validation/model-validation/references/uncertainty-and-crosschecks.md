# 一致性、不确定性、交叉引用与可视化（R2 diagnostic library only）

> **R2 authority override:** 方法接近仅表示 agreement，不证明 correctness。下文 5%/20% 等通用差异阈值已退役为历史示例，不得据此 PASS/FAIL；必须检查 estimand、共享假设、共享偏差、泄漏与独立证据。

> The `model_validation.*` imports below are API blueprints, not guaranteed bundled
> modules. Use them only when present; otherwise generate task-local implementations
> with SALib, SciPy, statsmodels and scikit-learn and execute the same checks.

## 内容索引

  - 模块8：跨方法一致性验证 (method_agreement) — v7 新增
    - 核心定位
    - 检查逻辑
    - 报告模板
    - 自动路由使用方式
  - 模块3：不确定性分析 (uncertainty) — v2 保留 + 增强
    - 蒙特卡洛模拟
    - Bootstrap 重抽样
  - 模块4：验证交叉引用（v2 新增保留）
    - 4.1 S3 硬断言复查
    - 4.2 高风险假设追踪
  - 模块5：可视化 (visualization) — v3 新增更多图表
    - 已有图表（保留）
    - v3 新增图表
    - 使用示例
  - 完整工作流示例（v3 更新）

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

# 0. 从 S1 文件产物获取信息；不要假定存在 pipeline Python 包
import json
from pathlib import Path
high_risk_assumptions = json.loads(
    Path("assumption_risk_register.json").read_text(encoding="utf-8")
)
hard_assertions = json.loads(
    Path("hard_assertions.json").read_text(encoding="utf-8")
)
routing = json.loads(Path("method_routing.json").read_text(encoding="utf-8"))
problem_type = routing["problem_type"]

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
