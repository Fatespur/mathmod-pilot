---
name: "data-processing"
description: "Math modeling data preprocessing: multi-format data loading (Excel/CSV/TXT/JSON/MAT), cleaning (missing values, outliers, duplicates), transformation (normalization, smoothing, PCA, feature engineering), and report generation for thesis use. v2 增强：物理约束感知数据验证。v3 增强：经济数据质量检查（平稳性/季节性/通胀调整/协整/时间序列特征工程）。v4：不平衡数据处理(SMOTE/ADASYN)+图像预处理+高维特征选择+信号预处理。Invoke when user needs to load, clean, preprocess, or explore data for math modeling, especially when the raw data requires cleaning before modeling."
---

# Data Processing — 数学建模数据预处理（v4）

You are a **data preprocessing specialist for mathematical modeling competitions**. Your core capability is to load, clean, transform, and profile data, producing structured outputs that feed directly into the modeling pipeline.

**v2 增强：** 物理约束感知数据验证 — 从 S1 获取硬断言，检查数据是否违反已知物理约束。

**v3 增强：** 经济数据质量检查 — 从 S1 v6 获取经济数据特征，自动执行平稳性检验、季节性检测、通胀调整提醒、协整检验、时间序列特征工程。杜绝"伪回归""名义值混淆""忽略季节性"等经济数据预处理错误。

**v4 增强：** 异构数据全覆盖 — 新增不平衡数据处理（SMOTE/ADASYN/类别权重）、图像数据预处理（resize/归一化/数据增强）、高维特征选择（LASSO/RFE/互信息/Boruta）、信号数据预处理（去噪/滤波/重采样/窗函数）、文本数据预处理（分词/TF-IDF/词向量）。

## When to Trigger

Invoke this skill when:
- User uploads a data file (Excel, CSV, TXT, etc.) and needs to understand its structure
- User asks to "clean data", "preprocess data", "handle missing values", "detect outliers"
- User needs to normalize/standardize data before modeling
- User needs a data preprocessing report for the thesis
- Pipeline stage S2 (DATA_PROCESSING) is activated


## 与 Skill 组的关系

本 skill 在数学建模 Pipeline 中担任 S2 阶段（数据处理），与其他 Skill 协同：

| Skill | 角色 | 与本 skill 的关系 |
|-------|------|------------------|
| **problem-analyzer** | S1 问题分析 | 上游：接收 S1 的硬断言（用于物理约束感知数据验证）和经济数据特征 |
| **mle-solver** | S3 建模求解 | 下游：向 S3 输出清洗后的数据集和预处理报告 |
| **model-validation** | S4 模型验证 | 下游：预处理后的数据用于模型验证的输入 |
| **scipilot-figure-cumcm** | S5 数据可视化 | 下游：预处理数据供可视化使用 |
| **mcm-paper-writing** | S6 论文写作 | 下游：论文中引用数据预处理方法 |

## Core Capabilities

| Module | Class | Purpose |
|--------|-------|---------|
| `reader.py` | `DataReader` | Multi-format data loading with auto-detection |
| `cleaner.py` | `DataCleaner` | Missing values, outliers, duplicates |
| `transformer.py` | `DataTransformer` | Normalization, smoothing, PCA, feature engineering |
| `reporter.py` | `DataReporter` | Preprocessing report generation (Markdown) |
| `constraint_validator.py` | `ConstraintValidator` | **v2 新增**：物理约束感知数据验证 |
| `imbalance_handler.py` | `ImbalanceHandler` | **v4 新增**：不平衡数据处理 |
| `image_processor.py` | `ImageProcessor` | **v4 新增**：图像数据预处理 |
| `feature_selector.py` | `FeatureSelector` | **v4 新增**：高维特征选择 |

## v2 新增：物理约束感知数据验证

### 概念

在数据清洗后、建模前，利用 S1 阶段产出的硬断言（hard_assertions）对数据进行物理约束验证。这可以防止以下情况：

- 厚度数据出现负值
- 速度数据超过物理极限
- 角度数据超出 [0, 2π] 范围
- 距离数据不满足三角不等式

### 使用方式

```python
from data_processing import DataProcessor
from pipeline import get_pipeline

with get_pipeline() as pipe:
    ctx = pipe.get_context()
    s1 = ctx.get_analysis()
    hard_assertions = s1.data.get("hard_assertions", [])
    
    dp = DataProcessor(language="zh")
    dp.load("data.xlsx")
    dp.clean(missing_strategy="median", outlier_method="iqr")
    
    # v2 新增：物理约束验证
    dp.validate_physical_constraints(hard_assertions)
    # 自动检查数据是否违反：
    #   - HA-1: 厚度 > 0
    #   - HA-2: 入射角 ∈ [0, π/2]
    #   - HA-3: 反射率 ∈ [0, 1]
    #   - ...
    
    # 获取验证结果
    violations = dp.get_constraint_violations()
    if violations:
        print(f"WARNING: {len(violations)} 个数据点违反物理约束")
        for v in violations:
            print(f"  {v['constraint_id']}: 行 {v['row']}, 值={v['value']}, 预期={v['expected']}")
    
    # 继续后续处理
    dp.normalize(method="minmax")
    data = dp.get_processed_data()
```

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

## v4 新增：图像数据预处理

### 8.1 概念

图像数据在进入模型前必须进行统一的预处理，包括尺寸标准化、像素值归一化、数据增强和通道处理。这些操作确保模型训练的一致性和泛化能力。

### 8.2 Resize 统一尺寸

```python
import cv2
import numpy as np

def preprocess_images(image_paths: list, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    将图像统一resize到目标尺寸。
    """
    processed = []
    for path in image_paths:
        img = cv2.imread(path)
        img = cv2.resize(img, target_size, interpolation=cv2.INTER_AREA)
        processed.append(img)
    return np.array(processed)
```

### 8.3 像素归一化与标准化

```python
# 归一化到 [0, 1]（适用于深度学习模型）
def normalize_01(images: np.ndarray) -> np.ndarray:
    return images.astype(np.float32) / 255.0

# 标准化（适用于传统机器学习）
def standardize(images: np.ndarray) -> np.ndarray:
    mean = np.mean(images, axis=(0, 1, 2), keepdims=True)
    std = np.std(images, axis=(0, 1, 2), keepdims=True)
    return (images - mean) / (std + 1e-8)
```

### 8.4 数据增强

```python
from tensorflow.keras.preprocessing.image import ImageDataGenerator

# 实时数据增强（训练时）
datagen = ImageDataGenerator(
    rotation_range=20,          # 随机旋转 ±20°
    width_shift_range=0.1,      # 水平平移 ±10%
    height_shift_range=0.1,     # 垂直平移 ±10%
    horizontal_flip=True,       # 水平翻转
    vertical_flip=False,        # 垂直翻转（根据场景决定）
    brightness_range=[0.8, 1.2],# 亮度调整 [80%, 120%]
    zoom_range=0.1,             # 缩放范围
    shear_range=0.1,            # 剪切变换
    fill_mode='nearest'         # 填充模式
)

datagen.fit(X_train)
```

### 8.5 通道处理

```python
# 灰度化
def to_grayscale(images: np.ndarray) -> np.ndarray:
    """将RGB图像转为灰度图（H x W x 3 -> H x W x 1）"""
    gray = np.dot(images[..., :3], [0.2989, 0.5870, 0.1140])
    return gray[..., np.newaxis]

# BGR → RGB（OpenCV默认读取为BGR）
def bgr_to_rgb(images: np.ndarray) -> np.ndarray:
    return images[..., ::-1]  # 反转通道顺序
```

### 8.6 图像预处理流程

```python
def full_image_pipeline(image_paths: list, target_size=(224, 224)):
    """
    图像预处理完整流程。
    """
    images = preprocess_images(image_paths, target_size)
    images = bgr_to_rgb(images)         # 通道转换
    images = normalize_01(images)       # 归一化
    return images
```

---

## v4 新增：高维特征选择

### 9.1 概念

当特征数量 p 远大于样本数量 n（p > n）时，模型容易过拟合且计算效率低下。必须通过特征选择降维，保留最具信息量的特征。以下是四种核心方法。

### 9.2 LASSO (L1 正则化) 特征选择

```python
from sklearn.linear_model import LassoCV
from sklearn.preprocessing import StandardScaler

# 标准化后使用LASSO，L1正则化自动将不重要的特征系数压缩为0
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

lasso = LassoCV(cv=5, random_state=42, max_iter=10000)
lasso.fit(X_scaled, y)

# 提取非零系数特征
selected_features = np.where(lasso.coef_ != 0)[0]
print(f"LASSO 选择了 {len(selected_features)}/{X.shape[1]} 个特征")
print(f"最优 alpha: {lasso.alpha_:.4f}")
```

### 9.3 递归特征消除 (RFE)

```python
from sklearn.feature_selection import RFE
from sklearn.ensemble import RandomForestRegressor

estimator = RandomForestRegressor(random_state=42)
rfe = RFE(estimator, n_features_to_select=10)  # 保留最重要的10个特征
rfe.fit(X, y)

# 查看特征排名（1=保留，数字越大越不重要）
feature_ranking = rfe.ranking_
selected_features = np.where(rfe.support_)[0]
```

### 9.4 互信息 (Mutual Information)

```python
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif

# 回归问题
mi_scores = mutual_info_regression(X, y, random_state=42)

# 分类问题
# mi_scores = mutual_info_classif(X, y, random_state=42)

# 按互信息得分排序
feature_mi = sorted(zip(range(X.shape[1]), mi_scores), key=lambda x: x[1], reverse=True)
for idx, score in feature_mi[:10]:
    print(f"特征 {idx}: MI = {score:.4f}")
```

### 9.5 Boruta 算法

```python
from boruta import BorutaPy
from sklearn.ensemble import RandomForestClassifier

rf = RandomForestClassifier(n_jobs=-1, class_weight='balanced', max_depth=5, random_state=42)

# Boruta通过影子特征对比，判断特征是否显著
boruta = BorutaPy(rf, n_estimators='auto', verbose=2, random_state=42)
boruta.fit(X.values, y.values)

# 结果解读
selected = boruta.support_           # True=确认重要
tentative = boruta.support_weak_     # True=暂定（不确定）
rejected = ~(selected | tentative)   # True=确认不重要

print(f"确认重要: {selected.sum()} 个")
print(f"暂定: {tentative.sum()} 个")
print(f"确认不重要: {rejected.sum()} 个")
```

### 9.6 特征选择报告模板

```python
def generate_feature_selection_report(X, y, methods=['lasso', 'rfe', 'mi', 'boruta']):
    """
    综合多种特征选择方法，生成选择报告。
    返回: 每种方法选出的特征集合和交集。
    """
    results = {}
    # ... 各方法执行 ...
    
    # 计算交集（被多种方法同时选中的特征最可靠）
    all_selected = [set(r) for r in results.values()]
    intersection = set.intersection(*all_selected)
    
    report = {
        'per_method': results,
        'intersection': intersection,
        'consensus_score': {feat: sum(1 for s in all_selected if feat in s) 
                            for feat in set.union(*all_selected)}
    }
    return report
```

---

## v4 新增：信号数据预处理

### 10.1 概念

传感器信号、振动数据、声学信号等时序信号在建模前必须进行去噪、滤波、重采样等预处理，以消除噪声干扰并提取有效特征。

### 10.2 去噪方法

#### 移动平均去噪

```python
def moving_average_denoise(signal: np.ndarray, window_size: int = 5) -> np.ndarray:
    """
    简单移动平均去噪，适用于快速平滑。
    """
    return np.convolve(signal, np.ones(window_size)/window_size, mode='same')
```

#### Savitzky-Golay (SG) 滤波

```python
from scipy.signal import savgol_filter

# SG滤波在平滑的同时保留信号的高阶特征（峰/谷形状）
denoised = savgol_filter(signal, window_length=11, polyorder=3)
```

#### 小波去噪

```python
import pywt

def wavelet_denoise(signal: np.ndarray, wavelet: str = 'db4', level: int = 4) -> np.ndarray:
    """
    小波阈值去噪：分解→阈值处理→重构。
    适用于非平稳信号，效果好于频域滤波。
    """
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745  # 噪声方差估计
    threshold = sigma * np.sqrt(2 * np.log(len(signal)))
    
    # 软阈值处理
    coeffs_thresholded = [coeffs[0]]  # 保留近似系数
    for c in coeffs[1:]:
        coeffs_thresholded.append(pywt.threshold(c, threshold, mode='soft'))
    
    return pywt.waverec(coeffs_thresholded, wavelet)
```

### 10.3 重采样与插值

```python
from scipy.signal import resample
from scipy.interpolate import interp1d

# 均匀重采样（改变采样率）
def resample_signal(signal: np.ndarray, original_fs: float, target_fs: float) -> np.ndarray:
    """从 original_fs 重采样到 target_fs"""
    num_samples = int(len(signal) * target_fs / original_fs)
    return resample(signal, num_samples)

# 非均匀采样插值到均匀网格
def interpolate_to_uniform(time: np.ndarray, signal: np.ndarray, target_fs: float):
    """将非均匀采样信号插值到均匀采样率"""
    t_uniform = np.arange(time[0], time[-1], 1.0 / target_fs)
    interpolator = interp1d(time, signal, kind='cubic', fill_value='extrapolate')
    signal_uniform = interpolator(t_uniform)
    return t_uniform, signal_uniform
```

### 10.4 窗函数应用

```python
from scipy.signal import get_window

def apply_window(signal: np.ndarray, window_type: str = 'hann') -> np.ndarray:
    """
    对信号施加窗函数，减少频谱泄漏。
    窗类型: hann, hamming, blackman, blackmanharris
    """
    window = get_window(window_type, len(signal))
    return signal * window

# 窗函数对比
# Hann:    旁瓣下降快，频率分辨率中等 → 通用首选
# Hamming: 旁瓣最低，主瓣稍宽 → 对旁瓣抑制要求高时
# Blackman:旁瓣极低，主瓣最宽 → 需要极高动态范围时
```

### 10.5 基于频谱的异常值检测

```python
from scipy.fft import fft, fftfreq

def spectral_outlier_detection(signal: np.ndarray, fs: float, threshold_factor: float = 3.0) -> np.ndarray:
    """
    基于频谱的异常检测：检测频域中能量异常高的频率成分。
    返回异常频率数组。
    """
    N = len(signal)
    fft_vals = np.abs(fft(signal))
    freqs = fftfreq(N, 1/fs)
    
    # 只考虑正频率
    pos_mask = freqs > 0
    freqs_pos = freqs[pos_mask]
    fft_pos = fft_vals[pos_mask]
    
    # 计算频谱能量的中位数和MAD
    median_energy = np.median(fft_pos)
    mad_energy = np.median(np.abs(fft_pos - median_energy))
    threshold = median_energy + threshold_factor * mad_energy / 0.6745
    
    anomaly_freqs = freqs_pos[fft_pos > threshold]
    return anomaly_freqs
```

### 10.6 信号预处理完整流程

```python
def signal_preprocessing_pipeline(signal: np.ndarray, fs: float, 
                                   target_fs: float = None) -> np.ndarray:
    """
    信号预处理完整流程。
    """
    # 1. 去噪
    signal = wavelet_denoise(signal)
    
    # 2. 重采样（如需要）
    if target_fs is not None and target_fs != fs:
        signal = resample_signal(signal, fs, target_fs)
    
    # 3. 标准化（零均值单位方差）
    signal = (signal - np.mean(signal)) / np.std(signal)
    
    return signal
```

---

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

```python
from pipeline import get_pipeline, Stage, StageResult, StageStatus
from data_processing import DataProcessor

with get_pipeline() as pipe:
    ctx = pipe.get_context()
    
    if not ctx.can_run_stage(Stage.DATA_PROCESSING):
        raise RuntimeError("S1 analysis must complete before S2 data processing")
    
    # v2: 获取 S1 物理约束
    s1 = ctx.get_analysis()
    hard_assertions = s1.data.get("hard_assertions", [])
    
    dp = DataProcessor(language=ctx.get_language())
    dp.load("data.xlsx").clean().validate_physical_constraints(hard_assertions).normalize().smooth(...)

    result = dp.to_pipeline_result()
    pipe.set_stage_result(Stage.DATA_PROCESSING, StageResult(
        stage=Stage.DATA_PROCESSING,
        status="completed",
        data=result,
        files=[],
    ))
```

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

- **当前版本**: v3.1
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: G-002, G-010
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v?
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
## 泛化约束

- **当前版本**: v?
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`


## 学习历史

> 本 Skill 受学习机制 v3.0 守护。每次进化前必须通过回归测试和安全检查。
> **当前版本**: v?

| 日期 | 训练 | 触发缺口 | 缺口ID | 变更摘要 |
|------|------|---------|--------|---------|
| 暂无 | - | - | - | - |

## 泛化约束

- **当前版本**: v?
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: 无
- **问题范围**: 本 Skill 被标记为特定题型的变更不应影响其他题型的分类

## 学习机制引用

- 训练索引: `training/training_index.json`
- 缺口登记册: `training/evolution/gap_registry.json`
- 回归测试: `python training/scripts/regression_test.py --skill all`
- 安全进化: `python training/scripts/evolution_safeguard.py safe-evolve`
- 学习优化: `python training/scripts/learning_optimizer.py check-rotation`
