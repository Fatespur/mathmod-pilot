# 数据预处理高级方法扩展

本文档为 data-processing skill 的高级扩展，新增缺失值高级插补、异常检测、降维和特征工程方法。

## 快速使用

```python
from data_processing_advanced import AdvancedDataProcessor

adp = AdvancedDataProcessor()

# 高级缺失值插补
adp.impute_missing(data, method="mice", n_iterations=10)

# 高级异常值检测
adp.detect_outliers_advanced(data, method="isolation_forest")

# 高级降维
adp.reduce_dimensions(data, method="umap", n_components=2)

# 平滑去噪
adp.smooth_advanced(data, method="loess")

# 特征选择
adp.select_features(data, target, method="mutual_info", k=10)
```

---

## 1. 高级缺失值插补

### MICE（多重插补）

```python
import numpy as np
import pandas as pd
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import BayesianRidge

def impute_mice(
    data: pd.DataFrame,
    n_iterations: int = 10,
    estimator: str = "bayesian_ridge",
    random_state: int = 42,
) -> pd.DataFrame:
    """
    MICE 多重插补（链式方程）
    
    Parameters
    ----------
    data : 含缺失值的 DataFrame
    n_iterations : 迭代次数
    estimator : 回归器 ("bayesian_ridge", "random_forest")
    random_state : 随机种子
    
    Returns
    -------
    插补后的 DataFrame
    """
    if estimator == "random_forest":
        est = RandomForestRegressor(n_estimators=100, random_state=random_state)
    else:
        est = BayesianRidge()
    
    imputer = IterativeImputer(
        estimator=est,
        max_iter=n_iterations,
        random_state=random_state,
        verbose=0,
    )
    
    imputed_array = imputer.fit_transform(data.select_dtypes(include=[np.number]))
    result = data.copy()
    result[data.select_dtypes(include=[np.number]).columns] = imputed_array
    
    return result
```

### KNN 插补

```python
from sklearn.impute import KNNImputer

def impute_knn(
    data: pd.DataFrame,
    n_neighbors: int = 5,
    weights: str = "uniform",
) -> pd.DataFrame:
    """
    KNN 插补：用最近邻样本的值填充缺失值
    
    Parameters
    ----------
    n_neighbors : 近邻数
    weights : "uniform" 或 "distance"
    """
    imputer = KNNImputer(n_neighbors=n_neighbors, weights=weights)
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    imputed_array = imputer.fit_transform(data[numeric_cols])
    result = data.copy()
    result[numeric_cols] = imputed_array
    return result
```

---

## 2. 高级异常值检测

### Isolation Forest（孤立森林）

```python
from sklearn.ensemble import IsolationForest

def detect_outliers_isolation_forest(
    data: pd.DataFrame,
    contamination: float = 0.05,
    random_state: int = 42,
) -> pd.Series:
    """
    孤立森林异常值检测
    
    Parameters
    ----------
    data : 数值型 DataFrame
    contamination : 预期异常比例 (0.01-0.1)
    
    Returns
    -------
    outlier_mask : True=异常值
    """
    iso_forest = IsolationForest(
        contamination=contamination,
        random_state=random_state,
        n_estimators=100,
    )
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    preds = iso_forest.fit_predict(numeric_data)
    # preds: 1=正常, -1=异常
    outlier_mask = pd.Series(preds == -1, index=numeric_data.index)
    return outlier_mask
```

### LOF（局部异常因子）

```python
from sklearn.neighbors import LocalOutlierFactor

def detect_outliers_lof(
    data: pd.DataFrame,
    n_neighbors: int = 20,
    contamination: float = 0.05,
) -> pd.Series:
    """
    LOF 局部异常因子检测
    
    适合检测局部密度异常（如簇间离群点）
    """
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    lof = LocalOutlierFactor(
        n_neighbors=n_neighbors,
        contamination=contamination,
    )
    preds = lof.fit_predict(numeric_data)
    outlier_mask = pd.Series(preds == -1, index=numeric_data.index)
    return outlier_mask
```

---

## 3. 高级降维方法

### t-SNE

```python
from sklearn.manifold import TSNE

def reduce_tsne(
    data: pd.DataFrame,
    n_components: int = 2,
    perplexity: float = 30.0,
    random_state: int = 42,
) -> np.ndarray:
    """
    t-SNE 降维（适合可视化，不适合作为特征输入）
    
    Parameters
    ----------
    n_components : 降维后的维度（通常 2 或 3）
    perplexity : 困惑度（5-50），数据集越大越大
    """
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    tsne = TSNE(
        n_components=n_components,
        perplexity=min(perplexity, len(numeric_data) / 3),
        random_state=random_state,
        n_iter=1000,
    )
    return tsne.fit_transform(numeric_data)
```

### UMAP

```python
try:
    import umap
    HAS_UMAP = True
except ImportError:
    HAS_UMAP = False

def reduce_umap(
    data: pd.DataFrame,
    n_components: int = 2,
    n_neighbors: int = 15,
    min_dist: float = 0.1,
    random_state: int = 42,
) -> np.ndarray:
    """
    UMAP 降维（比 t-SNE 更快，保留全局结构更好）
    
    Parameters
    ----------
    n_neighbors : 局部邻域大小（5-50）
    min_dist : 最小嵌入距离（0-1），越小越聚集
    """
    if not HAS_UMAP:
        raise ImportError("请安装 umap-learn: pip install umap-learn")
    
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    reducer = umap.UMAP(
        n_components=n_components,
        n_neighbors=n_neighbors,
        min_dist=min_dist,
        random_state=random_state,
    )
    return reducer.fit_transform(numeric_data)
```

### LDA（线性判别分析）

```python
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

def reduce_lda(
    data: pd.DataFrame,
    target: pd.Series,
    n_components: int = None,
) -> np.ndarray:
    """
    LDA 有监督降维（最大化类间距离）
    
    Parameters
    ----------
    target : 类别标签
    n_components : 降维后的维度（≤ n_classes-1）
    """
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    lda = LinearDiscriminantAnalysis(n_components=n_components)
    return lda.fit_transform(numeric_data, target)
```

---

## 4. 高级平滑与去噪

### LOESS / LOWESS

```python
from statsmodels.nonparametric.smoothers_lowess import lowess

def smooth_loess(
    x: np.ndarray,
    y: np.ndarray,
    frac: float = 0.1,
    return_sorted: bool = True,
) -> np.ndarray:
    """
    LOESS 局部加权回归平滑
    
    Parameters
    ----------
    x, y : 输入数据（一维）
    frac : 用于平滑的数据比例（0.01-0.5），越大越平滑
    
    Returns
    -------
    smoothed_y : 平滑后的 y 值
    """
    result = lowess(y, x, frac=frac, return_sorted=return_sorted)
    if return_sorted:
        return result[:, 1]
    return result
```

### 小波去噪

```python
import pywt
import numpy as np

def smooth_wavelet(
    signal: np.ndarray,
    wavelet: str = "db4",
    level: int = None,
    threshold_mode: str = "soft",
) -> np.ndarray:
    """
    小波阈值去噪
    
    Parameters
    ----------
    signal : 一维信号
    wavelet : 小波基 ("db4", "sym5", "coif3" 等)
    level : 分解层数
    threshold_mode : "soft" 或 "hard"
    
    Returns
    -------
    denoised : 去噪后的信号
    """
    if level is None:
        level = int(np.log2(len(signal))) - 2
    
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    
    # 使用全局阈值
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    threshold = sigma * np.sqrt(2 * np.log(len(signal)))
    
    # 阈值处理（仅细节系数）
    denoised_coeffs = [coeffs[0]]  # 近似系数保留
    for detail in coeffs[1:]:
        if threshold_mode == "soft":
            denoised = pywt.threshold(detail, threshold, mode="soft")
        else:
            denoised = pywt.threshold(detail, threshold, mode="hard")
        denoised_coeffs.append(denoised)
    
    return pywt.waverec(denoised_coeffs, wavelet)
```

---

## 5. 特征选择

### 互信息特征选择

```python
from sklearn.feature_selection import mutual_info_regression, mutual_info_classif
from sklearn.feature_selection import SelectKBest, f_regression, f_classif

def select_features_mutual_info(
    data: pd.DataFrame,
    target: pd.Series,
    k: int = 10,
    task: str = "regression",
    random_state: int = 42,
) -> pd.DataFrame:
    """
    使用互信息进行特征选择
    
    Parameters
    ----------
    data : 特征 DataFrame
    target : 目标变量
    k : 保留的特征数
    task : "regression" 或 "classification"
    
    Returns
    -------
    (selected_features, scores)
    """
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    
    if task == "classification":
        mi = mutual_info_classif(numeric_data, target, random_state=random_state)
    else:
        mi = mutual_info_regression(numeric_data, target, random_state=random_state)
    
    mi_scores = pd.Series(mi, index=numeric_data.columns).sort_values(ascending=False)
    selected = mi_scores.head(k).index.tolist()
    
    return data[selected], mi_scores.head(k)
```

### 方差阈值 + 相关性去冗余

```python
def select_features_variance_corr(
    data: pd.DataFrame,
    variance_threshold: float = 0.01,
    corr_threshold: float = 0.95,
) -> pd.DataFrame:
    """
    方差阈值 + 高相关性去冗余
    
    Parameters
    ----------
    variance_threshold : 方差阈值，低于此值的特征被删除
    corr_threshold : 相关性阈值，高于此值的特征对中删除一个
    
    Returns
    -------
    筛选后的 DataFrame
    """
    from sklearn.feature_selection import VarianceThreshold
    
    numeric_data = data.select_dtypes(include=[np.number]).dropna()
    
    # 1. 方差阈值
    selector = VarianceThreshold(threshold=variance_threshold)
    selector.fit(numeric_data)
    selected = numeric_data.columns[selector.get_support()]
    data_filtered = numeric_data[selected]
    
    # 2. 相关性去冗余
    corr_matrix = data_filtered.corr().abs()
    upper_tri = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
    
    to_drop = set()
    for col in upper_tri.columns:
        high_corr = upper_tri[col][upper_tri[col] > corr_threshold].index.tolist()
        to_drop.update(high_corr)
    
    return data_filtered.drop(columns=list(to_drop))
```

---

## 6. 类别不平衡处理

### SMOTE 过采样

```python
from imblearn.over_sampling import SMOTE

def balance_smote(
    X: pd.DataFrame,
    y: pd.Series,
    random_state: int = 42,
) -> tuple:
    """
    SMOTE 过采样处理类别不平衡
    
    Parameters
    ----------
    X, y : 特征和目标（分类任务）
    
    Returns
    -------
    (X_resampled, y_resampled)
    """
    smote = SMOTE(random_state=random_state)
    X_res, y_res = smote.fit_resample(X, y)
    return X_res, y_res
```

---

## 7. 归一化扩展

### QuantileTransformer + PowerTransformer

```python
from sklearn.preprocessing import QuantileTransformer, PowerTransformer

def normalize_advanced(
    data: pd.DataFrame,
    method: str = "quantile",
    **kwargs,
) -> pd.DataFrame:
    """
    高级归一化方法
    
    Parameters
    ----------
    method : "quantile" (均匀分布), "box-cox" (正态化), "yeo-johnson" (含负数)
    """
    numeric_data = data.select_dtypes(include=[np.number])
    
    if method == "quantile":
        transformer = QuantileTransformer(
            output_distribution="uniform",
            random_state=kwargs.get("random_state", 42),
        )
    elif method == "box-cox":
        transformer = PowerTransformer(method="box-cox")
    elif method == "yeo-johnson":
        transformer = PowerTransformer(method="yeo-johnson")
    else:
        raise ValueError(f"未知方法: {method}")
    
    transformed = transformer.fit_transform(numeric_data)
    result = data.copy()
    result[numeric_data.columns] = transformed
    return result
```