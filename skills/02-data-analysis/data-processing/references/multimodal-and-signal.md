# 图像、高维特征与信号预处理

## 内容索引

  - v4 新增：图像数据预处理
    - 8.1 概念
    - 8.2 Resize 统一尺寸
    - 8.3 像素归一化与标准化
    - 8.4 数据增强
    - 8.5 通道处理
    - 8.6 图像预处理流程
  - v4 新增：高维特征选择
    - 9.1 概念
    - 9.2 LASSO (L1 正则化) 特征选择
    - 9.3 递归特征消除 (RFE)
    - 9.4 互信息 (Mutual Information)
    - 9.5 Boruta 算法
    - 9.6 特征选择报告模板
  - v4 新增：信号数据预处理
    - 10.1 概念
    - 10.2 去噪方法
    - 10.3 重采样与插值
    - 10.4 窗函数应用
    - 10.5 基于频谱的异常值检测
    - 10.6 信号预处理完整流程

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
