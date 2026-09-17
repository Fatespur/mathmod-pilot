# 信号、图像、评分与超参优化模板（R1 implementation only）

> **R1 authority override:** 自动推荐、默认赋权或按指标数量套用评价方法的文字不再具有选择权。只在 R1 选择门禁放行某候选后使用相应代码模板。

## 内容索引

  - 阶段0.7：信号/图像数据特征检查（v5 新增）
  - 阶段0.7：信号/图像数据特征检查（v5 新增）
    - 信号质量检查代码模板
    - 预检结果对后续阶段的影响
  - 阶段0.8：评分方法选择预检（v6 新增）
    - 评价方法选择决策流程
    - Optuna 超参优化代码模板（v6 新增）
    - 预检结果对后续阶段的影响

## 阶段0.7：信号/图像数据特征检查（v5 新增）

## 阶段0.7：信号/图像数据特征检查（v5 新增）

**对于信号处理或图像处理类问题，在模型选择之前，必须对数据进行特征检查。**

### 信号质量检查代码模板

```python
# ============================================================
# 信号数据特征检查块（v5 新增）
# 在模型选择和代码生成之前必须运行
# ============================================================

import numpy as np
from scipy import signal
from scipy.fft import fft, fftfreq

def check_signal_quality(data, fs, signal_name="signal"):
    """
    v5 新增：检查信号数据的质量。
    
    参数:
        data: 一维信号数据
        fs: 采样率 (Hz)
        signal_name: 信号名称（用于输出）
    
    返回:
        report: dict, 包含所有检查结果
    """
    report = {
        "snr_db": None,
        "sampling_rate_ok": True,
        "spectral_leakage": False,
        "warnings": [],
    }
    
    # 检查1: SNR估计
    # 使用信号方差与残差方差之比估计
    signal_power = np.var(data)
    # 去趋势后估计噪声
    detrended = signal.detrend(data)
    noise_power = np.var(detrended) * 0.1  # 粗略估计
    if noise_power > 0:
        snr = 10 * np.log10(signal_power / noise_power)
        report["snr_db"] = snr
        if snr < 10:
            report["warnings"].append(
                f"SNR={snr:.1f}dB 较低，建议先进行滤波或小波去噪。"
            )
        print(f"  SNR估计 [{signal_name}]: {snr:.1f} dB")
    
    # 检查2: 采样率是否满足奈奎斯特定理
    N = len(data)
    if N > 0:
        freqs = fftfreq(N, 1/fs)
        spectrum = np.abs(fft(data))
        # 检查频谱能量是否集中在高频端（可能混叠）
        half_N = N // 2
        high_freq_energy = np.sum(spectrum[half_N//2:half_N])
        total_energy = np.sum(spectrum[:half_N])
        if total_energy > 0 and high_freq_energy / total_energy > 0.3:
            report["warnings"].append(
                f"高频能量占比 {high_freq_energy/total_energy*100:.1f}%，"
                f"可能存在混叠。建议提高采样率或使用抗混叠滤波。"
            )
        print(f"  采样率检查 [{signal_name}]: fs={fs}Hz, N={N}, "
              f"Nyquist={fs/2}Hz")
    
    # 检查3: 频谱泄漏检测
    # 使用窗函数平滑后检查频谱展宽
    windowed = data * np.hanning(N)
    spectrum_windowed = np.abs(fft(windowed))
    spectrum_raw = np.abs(fft(data))
    
    # 比较峰值宽度
    if N > 0:
        peak_idx = np.argmax(spectrum_raw[:half_N])
        # 检查峰值周围是否有明显展宽
        if peak_idx > 0 and peak_idx < half_N - 1:
            width_raw = np.sum(spectrum_raw[max(0,peak_idx-5):min(half_N,peak_idx+5)] > 
                              spectrum_raw[peak_idx] * 0.5)
            width_windowed = np.sum(spectrum_windowed[max(0,peak_idx-5):min(half_N,peak_idx+5)] > 
                                   spectrum_windowed[peak_idx] * 0.5)
            if width_raw > width_windowed * 2:
                report["spectral_leakage"] = True
                report["warnings"].append(
                    "检测到频谱泄漏。建议使用窗函数（Hanning/Hamming/Blackman）"
                    "或确保采样长度为信号周期的整数倍。"
                )
                print(f"  频谱泄漏检测 [{signal_name}]: 检测到泄漏 "
                      f"(原始宽度={width_raw}, 加窗宽度={width_windowed})")
    
    if not report["warnings"]:
        print(f"  信号质量检查 [{signal_name}]: 通过")
    
    return report


def check_image_quality(images, labels=None, image_name="image"):
    """
    v5 新增：检查图像数据的质量。
    
    参数:
        images: 图像数据列表或数组 (N, H, W) 或 (N, H, W, C)
        labels: 类别标签（可选，用于类别平衡检查）
        image_name: 图像名称（用于输出）
    
    返回:
        report: dict, 包含所有检查结果
    """
    report = {
        "resolution_ok": True,
        "illumination_consistency": True,
        "class_balance": None,
        "warnings": [],
    }
    
    if len(images) == 0:
        report["warnings"].append("图像数据为空。")
        return report
    
    # 检查1: 分辨率检查
    if isinstance(images, np.ndarray):
        if images.ndim >= 3:
            h, w = images.shape[1], images.shape[2]
            min_resolution = 32
            if h < min_resolution or w < min_resolution:
                report["resolution_ok"] = False
                report["warnings"].append(
                    f"图像分辨率 {h}x{w} 过低（最小要求 {min_resolution}x{min_resolution}）。"
                    f"建议使用超分辨率重建或上采样。"
                )
            print(f"  分辨率检查 [{image_name}]: {h}x{w}, "
                  f"{'通过' if report['resolution_ok'] else '过低'}")
            
            # 检查分辨率一致性
            if images.ndim >= 4:
                shapes = set()
                for i in range(min(len(images), 100)):
                    shapes.add((images[i].shape[0], images[i].shape[1]))
                if len(shapes) > 1:
                    report["warnings"].append(
                        f"图像分辨率不一致: {len(shapes)} 种不同尺寸。"
                        f"建议统一resize到固定尺寸。"
                    )
    
    # 检查2: 光照一致性（基于平均亮度）
    if isinstance(images, np.ndarray) and images.ndim >= 3:
        # 计算每张图像的平均亮度
        if images.ndim == 3:
            # (N, H, W): 灰度图
            brightness = np.mean(images, axis=(1, 2))
        elif images.ndim == 4:
            # (N, H, W, C): 彩色图
            brightness = np.mean(images, axis=(1, 2, 3))
        
        if len(brightness) > 1:
            brightness_cv = np.std(brightness) / (np.mean(brightness) + 1e-10)
            if brightness_cv > 0.3:
                report["illumination_consistency"] = False
                report["warnings"].append(
                    f"光照不一致: 亮度变异系数CV={brightness_cv:.2f} (>0.3)。"
                    f"建议进行直方图均衡化或自适应光照校正。"
                )
            print(f"  光照一致性 [{image_name}]: CV={brightness_cv:.3f}, "
                  f"{'通过' if report['illumination_consistency'] else '不一致'}")
    
    # 检查3: 类别平衡
    if labels is not None:
        unique, counts = np.unique(labels, return_counts=True)
        if len(unique) > 1:
            max_count = np.max(counts)
            min_count = np.min(counts)
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')
            report["class_balance"] = {
                "n_classes": len(unique),
                "imbalance_ratio": imbalance_ratio,
                "counts": dict(zip(unique.tolist(), counts.tolist())),
            }
            if imbalance_ratio > 3:
                report["warnings"].append(
                    f"类别不平衡: 最大/最小样本比={imbalance_ratio:.1f} (>3)。"
                    f"建议使用SMOTE/ADASYN过采样或类别权重调整。"
                )
            print(f"  类别平衡 [{image_name}]: {len(unique)} 类, "
                  f"最大/最小比={imbalance_ratio:.1f}")
    
    if not report["warnings"]:
        print(f"  图像质量检查 [{image_name}]: 通过")
    
    return report


def run_signal_image_precheck(data, config=None):
    """
    v5 新增：信号/图像数据特征预检主函数。
    在模型选择和代码生成之前必须调用。
    
    返回:
        report: dict, 包含所有检查结果
    """
    if config is None:
        config = {}
    
    report = {
        "signal_quality": {},
        "image_quality": {},
        "overall_warnings": [],
    }
    
    print("=" * 60)
    print("信号/图像数据特征预检 (v5)")
    print("=" * 60)
    
    data_type = config.get('data_type', '')
    
    # 信号数据检查
    if data_type == 'signal' or config.get('is_signal', False):
        print("\n[信号质量检查]:")
        fs = config.get('sampling_rate', 1000)
        signal_data = config.get('signal_data', data)
        if isinstance(signal_data, np.ndarray) and signal_data.ndim == 1:
            sig_report = check_signal_quality(signal_data, fs, "输入信号")
            report["signal_quality"] = sig_report
            report["overall_warnings"].extend(sig_report["warnings"])
        elif isinstance(signal_data, np.ndarray) and signal_data.ndim == 2:
            for i in range(signal_data.shape[1]):
                sig_report = check_signal_quality(
                    signal_data[:, i], fs, f"通道{i}"
                )
                report["signal_quality"][f"channel_{i}"] = sig_report
                report["overall_warnings"].extend(sig_report["warnings"])
    
    # 图像数据检查
    if data_type == 'image' or config.get('is_image', False):
        print("\n[图像质量检查]:")
        image_data = config.get('image_data', data)
        img_labels = config.get('image_labels', None)
        if isinstance(image_data, np.ndarray) and image_data.ndim >= 3:
            img_report = check_image_quality(image_data, img_labels, "输入图像")
            report["image_quality"] = img_report
            report["overall_warnings"].extend(img_report["warnings"])
    
    # 汇总
    print("\n" + "=" * 60)
    if report["overall_warnings"]:
        print(f"信号/图像数据预检发现 {len(report['overall_warnings'])} 个警告:")
        for w in report["overall_warnings"]:
            print(f"  - {w}")
    else:
        print("信号/图像数据预检通过，无警告")
    print("=" * 60)
    
    return report
```

### 预检结果对后续阶段的影响

| 预检发现 | 影响的阶段 | 处理方式 |
|---------|----------|---------|
| SNR过低 | 阶段0（模型选择） | 先进行小波去噪或带通滤波，再建模 |
| 频谱泄漏 | 阶段1（数据准备） | 使用窗函数（Hanning/Hamming）预处理 |
| 采样率不足 | 阶段0（模型选择） | 提示混叠风险，建议使用抗混叠滤波 |
| 分辨率过低 | 阶段0（模型选择） | 使用超分辨率重建或上采样 |
| 光照不一致 | 阶段1（数据准备） | 直方图均衡化或CLAHE自适应校正 |
| 类别不平衡 | 阶段0（模型选择） | 使用SMOTE/ADASYN或类别权重 |

---

## 阶段0.8：评分方法选择预检（v6 新增）

**对于评价类问题，在模型选择之前，必须根据数据特征自动选择最优评分方法。**

### 评价候选证据提取（R1：不得自动选择）

```python
# ============================================================
# 评分方法选择预检块（v6 新增）
# 在模型选择和代码生成之前必须运行
# ============================================================

def extract_evaluation_candidate_evidence(data, config=None):
    """
    R1：只提取选择证据和候选提示；不得返回 recommended_method。
    
    决策规则:
    1. 有主观判断矩阵? → AHP
    2. 有客观数据 + 有行业标准权重? → 模糊综合评价
    3. 有客观数据 + 需要排序? → 熵权TOPSIS
    4. 有客观数据 + 需要效率评估? → DEA
    5. 有客观数据 + 需要关联分析? → 灰色关联分析
    6. 主客观结合? → 组合赋权(AHP+熵权)
    
    参数:
        data: DataFrame, 评价数据
        config: dict, 配置信息
    
    返回结果必须交给 model-selection 的 screening matrix 和 anti-template gate。
    """
    if config is None:
        config = {}
    
    result = {
        "structural_evidence": [],
        "candidate_hints": [],
        "warnings": [],
    }
    
    print("=" * 60)
    print("评分方法选择预检 (v6)")
    print("=" * 60)
    
    has_subjective = config.get('has_judgment_matrix', False)
    has_standards = config.get('has_evaluation_standards', False)
    data_type = config.get('data_type', '')
    
    n_indicators = len(data.columns) if hasattr(data, 'columns') else 0
    n_samples = len(data) if hasattr(data, '__len__') else 0
    
    print(f"
数据特征: {n_samples} 个评价对象, {n_indicators} 个指标")
    print(f"主观判断矩阵: {'有' if has_subjective else '无'}")
    print(f"评价标准/等级: {'有' if has_standards else '无'}")
    
    # 候选提示逻辑：提示不等于选择，必须另行比较 baseline 和 serious alternative。
    if has_subjective and has_standards:
        result["structural_evidence"].append("同时存在经验证的偏好判断与等级标准")
        result["candidate_hints"] += ["AHP", "模糊综合评价", "组合赋权"]
    elif has_subjective:
        result["structural_evidence"].append("存在经验证的主观偏好判断矩阵")
        result["candidate_hints"] += ["AHP", "equal-weight baseline", "rank aggregation"]
    elif has_standards:
        result["structural_evidence"].append("存在等级标准，但权重与补偿语义仍需检查")
        result["candidate_hints"] += ["模糊综合评价", "simple normalized score", "rank aggregation"]
    elif data_type == 'efficiency':
        result["structural_evidence"].append("目标语义是投入产出效率")
        result["candidate_hints"] += ["DEA", "simple efficiency ratio baseline"]
    elif data_type == 'correlation':
        result["structural_evidence"].append("目标语义是关联而非排名或效率")
        result["candidate_hints"] += ["statistical association", "灰色关联分析"]
    elif n_indicators > 0:
        result["structural_evidence"].append("存在多指标数据；构念、偏好、效率和补偿语义未知")
        result["candidate_hints"] += ["equal-weight normalized score", "PCA/factor", "entropy weighting", "TOPSIS", "rank aggregation"]
    else:
        result["warnings"].append("数据不足，无法自动选择评价方法")
    
    print(f"
候选提示（非推荐）: {', '.join(result['candidate_hints'])}")
    print("=" * 60)
    
    return result
```

### Optuna 超参优化代码模板（v6 新增）

```python
# ============================================================
# Optuna 超参优化代码模板（v6 新增）
# 用于预测类模型（LightGBM/XGBoost/RandomForest）自动超参调优
# ============================================================

import optuna
from lightgbm import LGBMRegressor
from sklearn.model_selection import cross_val_score

def optimize_lgbm_hyperparams(X, y, n_trials=100, cv=5):
    """
    v6 新增：使用 Optuna 自动优化 LightGBM 超参数。
    
    参数:
        X: 特征矩阵 (n_samples, n_features)
        y: 目标变量 (n_samples,)
        n_trials: Optuna 试验次数
        cv: 交叉验证折数
    
    返回:
        best_params: 最优超参数字典
        best_value: 最优目标函数值（MSE）
    """
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'num_leaves': trial.suggest_int('num_leaves', 20, 300),
            'min_child_samples': trial.suggest_int('min_child_samples', 5, 100),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        }
        model = LGBMRegressor(**params, random_state=42, verbose=-1)
        scores = cross_val_score(model, X, y, cv=cv, scoring='neg_mean_squared_error')
        return -scores.mean()
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value


def optimize_xgboost_hyperparams(X, y, n_trials=100, cv=5):
    """
    v6 新增：使用 Optuna 自动优化 XGBoost 超参数。
    """
    from xgboost import XGBRegressor
    
    def objective(trial):
        params = {
            'n_estimators': trial.suggest_int('n_estimators', 100, 2000),
            'max_depth': trial.suggest_int('max_depth', 3, 15),
            'learning_rate': trial.suggest_float('learning_rate', 0.01, 0.3, log=True),
            'subsample': trial.suggest_float('subsample', 0.5, 1.0),
            'colsample_bytree': trial.suggest_float('colsample_bytree', 0.5, 1.0),
            'gamma': trial.suggest_float('gamma', 0, 5),
            'reg_alpha': trial.suggest_float('reg_alpha', 1e-8, 10.0, log=True),
            'reg_lambda': trial.suggest_float('reg_lambda', 1e-8, 10.0, log=True),
        }
        model = XGBRegressor(**params, random_state=42, verbosity=0)
        scores = cross_val_score(model, X, y, cv=cv, scoring='neg_mean_squared_error')
        return -scores.mean()
    
    study = optuna.create_study(direction='minimize')
    study.optimize(objective, n_trials=n_trials)
    return study.best_params, study.best_value
```

### 预检结果对后续阶段的影响

| 预检发现 | 影响的阶段 | 处理方式 |
|---------|----------|---------|
| 有判断矩阵 | 阶段0（模型选择） | 使用AHP确定权重，CR<0.1通过一致性检验 |
| 有评价标准 | 阶段0（模型选择） | 使用模糊综合评价，定义隶属度函数 |
| 效率评估 | 阶段0（模型选择） | 使用DEA（CCR/BCC模型），区分技术效率与规模效率 |
| 客观数据 | selection 前证据 | 只标记指标方向、尺度、相关性与偏好语义未知；不得自动选择熵权 TOPSIS |
| 主客观结合 | 阶段0（模型选择） | 使用组合赋权（AHP+熵权），乘法合成或加法合成 |
| 关联分析 | 阶段0（模型选择） | 使用灰色关联分析，计算灰色关联度排序 |

---
