# 数据质量、物理/经济约束与表格数据

> `DataProcessor` examples are interface blueprints rather than a guaranteed installed
> package. Verify availability before import; otherwise implement and execute equivalent
> local checks.

## 内容索引

  - v2 新增：物理约束感知数据验证
    - 概念
    - 使用方式
    - 约束定义格式
    - 验证结果报告
    - 论文表述
  - v3 新增：经济数据质量检查
    - 6.1 平稳性检验
    - 6.2 季节性检测与处理
    - 6.3 通胀调整提醒
    - 6.4 差分处理
    - 6.5 时间序列特征工程
    - 6.6 协整检验
    - 6.7 时间序列异常值检测
  - v4 新增：不平衡数据处理
    - 7.1 概念
    - 7.2 SMOTE 过采样
    - 7.3 ADASYN 自适应过采样
    - 7.4 RandomUnderSampler 欠采样
    - 7.5 类别权重自动计算
    - 7.6 使用 Pipeline 确保无数据泄漏
    - 7.7 不平衡处理策略选择

## v2 新增：物理约束感知数据验证

### 概念

在数据清洗后、建模前，利用 S1 阶段产出的硬断言（hard_assertions）对数据进行物理约束验证。这可以防止以下情况：

- 厚度数据出现负值
- 速度数据超过物理极限
- 角度数据超出 [0, 2π] 范围
- 距离数据不满足三角不等式

### 使用方式

```python
import json
from pathlib import Path
from data_processing import DataProcessor

hard_assertions = json.loads(
    Path("hard_assertions.json").read_text(encoding="utf-8")
)

dp = DataProcessor(language="zh")
dp.load("data.xlsx")
dp.clean(missing_strategy="median", outlier_method="iqr")
    
# v2 新增：物理约束验证
dp.validate_physical_constraints(hard_assertions)
    
violations = dp.get_constraint_violations()
if violations:
    print(f"WARNING: {len(violations)} 个数据点违反物理约束")
    
dp.normalize(method="minmax")
data = dp.get_processed_data()
```

`DataProcessor` 是接口示意。如果工作区没有该实现，Codex 必须生成并执行任务本地实现，不得声称已调用不存在的包。

### 约束定义格式

```python
hard_assertions = [
    {
        "id": "HA-1",
        "expression": "thickness > 0",
        "meaning": "厚度必须为正",
        "violation_consequence": "物理意义无效",
        "column": "thickness",  # v2 新增：关联的列名
        "check_type": "gt",     # v2 新增：检查类型（gt/lt/between/eq）
        "check_value": 0,       # v2 新增：检查阈值
    },
    {
        "id": "HA-2",
        "expression": "0 <= angle <= pi/2",
        "meaning": "入射角在有效范围内",
        "column": "angle",
        "check_type": "between",
        "check_value": [0, 3.14159/2],
    },
    {
        "id": "HA-3",
        "expression": "0 <= reflectance <= 1",
        "meaning": "反射率在 [0,1] 内",
        "column": "reflectance",
        "check_type": "between",
        "check_value": [0, 1],
    },
]
```

### 验证结果报告

物理约束验证结果会自动整合到预处理报告中：

```markdown
## 物理约束验证

| 约束ID | 约束内容 | 违反数 | 通过率 | 处理方式 |
|--------|---------|--------|--------|---------|
| HA-1 | 厚度 > 0 | 0 | 100% | 通过 |
| HA-2 | 0 ≤ 角度 ≤ π/2 | 0 | 100% | 通过 |
| HA-3 | 0 ≤ 反射率 ≤ 1 | 3 | 99.96% | 标记为异常值，已剔除 |
```

### 论文表述

```markdown
在数据预处理阶段，对 7469 个测量点进行了物理约束验证。
经验证，所有数据点满足厚度为正、入射角在有效范围 [0, π/2] 内的基本物理约束。
反射率数据中有 3 个点（0.04%）略超出 [0, 1] 范围（最大偏差 0.002），
判定为测量噪声，已标记为异常值并剔除。
```

## v3 新增：经济数据质量检查

### 6.1 平稳性检验

对于时间序列数据，必须在建模前进行平稳性检验：

```python
def check_stationarity(data: pd.Series, significance: float = 0.05) -> dict:
    """
    执行ADF单位根检验和KPSS平稳性检验。
    返回: {is_stationary, adf_stat, adf_pvalue, kpss_stat, kpss_pvalue, recommendation}
    """
```

### 6.2 季节性检测与处理

```python
def detect_seasonality(data: pd.Series, freq: str = None) -> dict:
    """
    检测时间序列的季节性模式。
    返回: {has_seasonality, seasonal_period, acf_peaks, recommendation}
    """
```

### 6.3 通胀调整提醒

```python
def check_inflation_adjustment(data: pd.DataFrame, columns: list, year_span: int) -> dict:
    """
    检查跨年货币数据是否需要价格平减。
    返回: {needs_adjustment, suggested_deflator, warning_message}
    """
```

### 6.4 差分处理

| 差分类型 | 公式 | 适用场景 |
|---------|------|---------|
| 一阶差分 | Δy_t = y_t - y_{t-1} | I(1)序列去趋势 |
| 季节差分 | Δ_s y_t = y_t - y_{t-s} | 季节非平稳 |
| 对数差分 | Δln(y_t) ≈ 增长率 | 经济变量增长率 |
| 二阶差分 | Δ²y_t = Δy_t - Δy_{t-1} | I(2)序列 |

### 6.5 时间序列特征工程

```python
def time_series_feature_engineering(data: pd.DataFrame, date_col: str) -> dict:
    """
    自动构造时间序列特征。
    包括：滞后项、滚动统计量、时间虚拟变量、趋势项。
    """
```

### 6.6 协整检验

```python
def check_cointegration(y: pd.Series, X: pd.DataFrame) -> dict:
    """
    对多元非平稳序列进行协整检验。
    返回: {is_cointegrated, method, test_stat, pvalue, recommendation}
    """
```

### 6.7 时间序列异常值检测

| 方法 | 检测类型 | 适用场景 |
|------|---------|---------|
| AO (Additive Outlier) | 单点异常 | 数据录入错误 |
| LS (Level Shift) | 水平永久偏移 | 政策变化/制度变更 |
| TC (Temporary Change) | 暂时性变化 | 突发事件影响 |
| IQR (Interquartile) | 统计异常 | 通用（已有） |

## v4 新增：不平衡数据处理

### 7.1 概念

在分类问题中，当各类别样本数量严重不均衡时，模型会偏向多数类，导致少数类几乎无法被正确识别。必须在预处理阶段对不平衡数据进行重采样或权重调整。

### 7.2 SMOTE 过采样

```python
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import train_test_split

# 必须先分割，再对训练集做SMOTE（防止数据泄漏）
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, stratify=y, random_state=42)

smote = SMOTE(random_state=42, k_neighbors=5)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

print(f"原始分布: {dict(zip(*np.unique(y_train, return_counts=True)))}")
print(f"SMOTE后分布: {dict(zip(*np.unique(y_train_resampled, return_counts=True)))}")
```

### 7.3 ADASYN 自适应过采样

```python
from imblearn.over_sampling import ADASYN

# ADASYN在少数类密度低的区域生成更多样本
adasyn = ADASYN(random_state=42, n_neighbors=5)
X_train_resampled, y_train_resampled = adasyn.fit_resample(X_train, y_train)
```

### 7.4 RandomUnderSampler 欠采样

```python
from imblearn.under_sampling import RandomUnderSampler

# 随机欠采样多数类，使其与少数类数量一致
rus = RandomUnderSampler(random_state=42)
X_train_resampled, y_train_resampled = rus.fit_resample(X_train, y_train)
```

### 7.5 类别权重自动计算

```python
from sklearn.utils.class_weight import compute_class_weight

# 自动计算类别权重（多数类权重低，少数类权重高）
class_weights = compute_class_weight(
    class_weight='balanced',
    classes=np.unique(y_train),
    y=y_train
)
class_weight_dict = dict(zip(np.unique(y_train), class_weights))

# 直接传入分类器
from sklearn.ensemble import RandomForestClassifier
clf = RandomForestClassifier(class_weight=class_weight_dict, random_state=42)
```

### 7.6 使用 Pipeline 确保无数据泄漏

```python
from imblearn.pipeline import Pipeline as ImbPipeline
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

# 使用 imblearn.Pipeline 确保SMOTE仅在训练时应用
pipeline = ImbPipeline([
    ('scaler', StandardScaler()),
    ('smote', SMOTE(random_state=42)),
    ('classifier', RandomForestClassifier(random_state=42))
])

pipeline.fit(X_train, y_train)  # SMOTE只在fit时生效
y_pred = pipeline.predict(X_test)  # predict时不会做SMOTE
```

### 7.7 不平衡处理策略选择

| 策略 | 适用场景 | 注意事项 |
|------|---------|---------|
| SMOTE | 少数类样本极少的特征空间连续数据 | 可能生成噪声样本 |
| ADASYN | 少数类密度不均匀时 | 对噪声敏感 |
| RandomUnderSampler | 多数类样本量极大（>10万） | 可能丢失重要信息 |
| 类别权重 | 样本量中等，不想改变数据分布 | 需分类器支持 `class_weight` |
| SMOTE+ENN | 需要同时清理噪声 | 计算量较大 |

---
