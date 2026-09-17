# 使用方式、格式、策略与硬规则

> `DataProcessor` examples describe a preferred interface. Verify that implementation
> exists before importing it; otherwise generate equivalent task-local code and preserve
> the same input/output contract.

## 内容索引

  - Usage
    - Quick Start (via DataProcessor)
    - Detailed Usage
  - Pipeline Integration
  - Supported Data Formats
  - Missing Value Strategies
  - Outlier Detection Methods
  - Normalization Methods
  - Hard Rules
    - MUST DO
    - MUST NOT DO

## Usage

### Quick Start (via DataProcessor)

```python
from data_processing import DataProcessor

dp = DataProcessor(language="zh")  # "zh" for CUMCM, "en" for MCM

# Full pipeline
dp.load("data.xlsx") \
  .clean(missing_strategy="median", outlier_method="iqr") \
  .validate_physical_constraints(hard_assertions) \  # v2新增
  .normalize(method="minmax") \
  .smooth(columns=["signal"], method="sg", window=5)

# Get processed data for modeling
data = dp.get_processed_data()

# Generate preprocessing report for thesis
report = dp.report()
print(report)
```

### Detailed Usage

```python
from data_processing import DataProcessor

dp = DataProcessor(language="zh")

# 1. Load data
dp.load("2025_CUMCM_B_data.xlsx", sheet_name="Sheet1")

# 2. Profile data (understand structure)
profile = dp.profile()
print(profile)

# 3. Detect outliers without modifying
outliers = dp.detect_outliers(method="iqr")
print(f"Outliers found: {sum(m.sum() for m in outliers.values())}")

# 4. Clean data
dp.clean(
    missing_strategy="median",      # Handle missing values
    outlier_method="iqr",           # Detect outliers
    drop_duplicates=True,           # Remove duplicates
)

# 5. v2 新增：物理约束验证
dp.validate_physical_constraints(hard_assertions)
violations = dp.get_constraint_violations()

# 6. Transform data
dp.normalize(method="minmax")       # Normalize to [0,1]
dp.smooth(columns=["reflectance"],  # Smooth noisy data
          method="sg", window=7)

# 7. Generate report
report = dp.report()

# 8. Get processed data for downstream
data = dp.get_processed_data()

# 9. Save processed data
dp.save("cleaned_data.csv")
```

## Pipeline Integration

不要假定存在名为 `pipeline` 或 `data_processing` 的 Python 包。Codex 应在任务目录中：

1. 读取并校验 `pipeline_manifest.json`。
2. 从 S1 产物路径加载 `hard_assertions.json` 和 `variables_and_units.json`。
3. 根据实际数据生成任务本地的处理代码。
4. 保存处理后数据、字段字典、报告和 `preprocessing_manifest.json`。
5. 将这些真实路径、哈希和状态写回 `pipeline_manifest.json`。

本文其他 `DataProcessor` 代码块是接口示意；只有工作区确实提供该实现时才能直接导入，否则应生成等价的 pandas/scikit-learn 代码并运行验证。

## Supported Data Formats

| Format | Extension | Method |
|--------|-----------|--------|
| Excel | .xlsx, .xls | `pd.read_excel` |
| CSV | .csv | `pd.read_csv` (auto-detect encoding) |
| TSV | .tsv | `pd.read_csv(sep='\t')` |
| Text | .txt | Auto-detect delimiter + encoding |
| JSON | .json | `pd.read_json` |
| MATLAB | .mat | `scipy.io.loadmat` |

## Missing Value Strategies

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| `drop` | Remove rows with missing values | Missing data is < 5% |
| `mean` | Fill with column mean | Symmetric distribution |
| `median` | Fill with column median | Skewed distribution (recommended) |
| `mode` | Fill with most frequent value | Categorical data |
| `ffill` / `bfill` | Forward/backward fill | Time series data |
| `interpolate` | Linear interpolation | Continuous data |
| `seasonal_interpolate` | 季节性插值 | 含季节模式的时间序列 |
| `time_interpolate` | 时间索引插值 | 不规则时间间隔 |
| `knn` | KNN imputation | When correlations matter |
| `mice` | **v4 新增**：多重插补 (Multiple Imputation) | 缺失率较高且特征间存在关联 |
| `constant` | Fill with fixed value | Known default value |

## Outlier Detection Methods

| Method | Description | When to Use |
|--------|-------------|-------------|
| `iqr` | Q1-1.5×IQR, Q3+1.5×IQR | Robust, non-parametric (recommended) |
| `zscore` | \|z\| > 3 | Normal distribution |
| `percentile` | Below/above percentile | Known outlier proportion |
| `physical_constraint` | **v2 新增**：违反物理约束 | 已知物理上下界时 |
| `time_series_iqr` | 滚动窗口IQR | 时间序列（考虑局部趋势） |
| `level_shift` | 水平偏移检测 | 经济政策变化 |
| `isolation_forest` | **v4 新增**：隔离森林 | 高维数据，异常点比例未知 |
| `local_outlier_factor` | **v4 新增**：局部异常因子 | 局部密度异常（簇状数据） |

## Normalization Methods

| Method | Formula | When to Use |
|--------|---------|-------------|
| `minmax` | (x-min)/(max-min) | Bounded output needed |
| `zscore` | (x-μ)/σ | Gaussian assumption |
| `robust` | (x-median)/IQR | Outliers present |
| `l2` | x/||x|| | Direction matters |

## Hard Rules

### MUST DO
1. Always profile data before cleaning — understand the data first
2. Always generate a preprocessing report — include it in the thesis
3. Always save the cleaned data — downstream skills need it
4. Use median for missing values by default (robust to outliers)
5. Use IQR for outlier detection by default (non-parametric)
6. Document every transformation step in the report
7. **v2 新增：如果 S1 提供了硬断言，必须在预处理中执行物理约束验证**
8. **v2 新增：物理约束验证结果必须写入预处理报告**
9. **v3 新增：时间序列数据必须在预处理中进行平稳性检验（ADF+KPSS）**
10. **v3 新增：跨年货币数据必须检查是否需要价格平减（CPI/GDP平减指数）**
11. **v3 新增：含季节模式的时间序列必须进行季节性检测和调整**
12. **v3 新增：多元非平稳序列必须进行协整检验**
13. **v4 新增：不平衡分类数据必须进行重采样或使用类别权重**
14. **v4 新增：图像数据必须在预处理中统一尺寸和归一化**
15. **v4 新增：高维数据（p > n）必须进行特征选择**


### MUST NOT DO
1. Do NOT skip data profiling — you must understand the data before cleaning
2. Do NOT delete outliers without documenting — explain why and how
3. Do NOT normalize without understanding the data distribution
4. Do NOT apply smoothing to all columns — only to noisy signals
5. Do NOT forget to set `language="zh"` for CUMCM papers
6. **v2 新增：不要忽略物理约束违规 — 每个违规都必须标记并报告**
7. **v3 新增：禁止对时间序列数据跳过平稳性检验直接进入建模**
8. **v3 新增：禁止对跨年货币数据忽略通胀调整**
9. **v3 新增：禁止对有季节效应的时间序列不做季节调整**
10. **v4 新增：禁止在不平衡数据上不做处理直接训练分类器**
11. **v4 新增：禁止对训练集和测试集分别做SMOTE（必须先分割再SMOTE，用Pipeline防泄漏）**
