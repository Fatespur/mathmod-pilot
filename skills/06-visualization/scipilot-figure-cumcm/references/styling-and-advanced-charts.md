# 竞赛配置、配色与高级图表

## 内容索引

  - CUMCM 国赛配置
  - MCM 美赛配置
  - CUMCM 专属配色方案
  - 高级图表类型
    - 1. 三维可视化
    - 2. 高级统计图
    - 3. 预测区间图
    - 4. 雷达图（多模型对比）
    - 5. 论文级多面板组合图
    - 6. Pareto 前沿图
  - 图表数量分配建议（v5.2 更新：强制生成+用户选择）
  - 图表快速参考

## CUMCM 国赛配置

```python
def setup_cumcm_style():
    """国赛专属 matplotlib 配置"""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'Noto Sans CJK SC',
        'font.size': 8,
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'legend.fontsize': 8,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',
        'axes.unicode_minus': False,
        'axes.grid': True,
        'grid.alpha': 0.3,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })
```

国赛规范：
- 图题格式：`图X 图表标题`（中文，加粗）
- 图注格式：在图下方，中文，宋体
- 分辨率：300 DPI（PNG）+ SVG 矢量
- 配色：蓝色系 + 橙色系对比
- 表格：三线表，无竖线
- 禁止：多面板合并为一张大图（每张图独立）

---

## MCM 美赛配置

```python
def setup_mcm_style():
    """美赛专属 matplotlib 配置"""
    import matplotlib.pyplot as plt
    plt.rcParams.update({
        'font.family': 'DejaVu Sans',
        'font.size': 8,
        'axes.labelsize': 9,
        'axes.titlesize': 10,
        'xtick.labelsize': 7,
        'ytick.labelsize': 7,
        'legend.fontsize': 8,
        'figure.dpi': 300,
        'savefig.dpi': 300,
        'savefig.bbox': 'tight',
        'savefig.facecolor': 'white',
        'axes.grid': True,
        'grid.alpha': 0.2,
        'axes.spines.top': False,
        'axes.spines.right': False,
    })
```

美赛规范：
- 图题格式：`Figure X: Chart Title`（英文）
- 图注格式：在图下方，英文
- 配色：Cool-toned（蓝/绿/紫），色盲安全

---

## CUMCM 专属配色方案

```python
CUMCM_COLORS = {
    "primary": "#2563EB",          # 主色（蓝）
    "primary_light": "#60A5FA",    # 浅蓝
    "primary_lighter": "#93C5FD",  # 更浅蓝
    "secondary": "#EA580C",        # 橙色（对比色）
    "secondary_light": "#FDBA74",  # 浅橙
    "tertiary": "#059669",         # 绿色
    "tertiary_light": "#6EE7B7",   # 浅绿
    "gray": "#6B7280",             # 灰色
    "light_gray": "#D1D5DB",       # 浅灰
    "bg": "#FFFFFF",               # 白色背景
    "ink": "#1A1A2E",              # 文字色
}

# 多系列配色（5色）
CUMCM_PALETTE_5 = ["#2563EB", "#EA580C", "#059669", "#7C3AED", "#DC2626"]

# 多系列配色（8色）
CUMCM_PALETTE_8 = [
    "#2563EB", "#EA580C", "#059669", "#7C3AED",
    "#DC2626", "#0891B2", "#CA8A04", "#BE185D",
]

# Okabe-Ito 色盲安全配色（8色）
OKABE_ITO = [
    "#0072B2", "#E69F00", "#009E73", "#F0E442",
    "#56B4E9", "#D55E00", "#CC79A7", "#000000",
]
```

---

## 高级图表类型

### 1. 三维可视化

#### 3D 曲面图

```python
import matplotlib.pyplot as plt
import numpy as np

def plot_3d_surface(x, y, z, title="3D曲面图", xlabel="X", ylabel="Y", zlabel="Z",
                    save_path=None, cmap='viridis'):
    """3D曲面图 — 展示二维参数空间中的函数值"""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    X, Y = np.meshgrid(x, y)
    surf = ax.plot_surface(X, Y, z, cmap=cmap, edgecolor='none',
                          alpha=0.9, antialiased=True)
    
    ax.set_xlabel(xlabel, fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_ylabel(ylabel, fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_zlabel(zlabel, fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold')
    
    fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
    ax.view_init(elev=30, azim=45)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

#### 3D 轨迹图

```python
def plot_3d_trajectory(x, y, z, title="3D轨迹图", save_path=None):
    """3D轨迹图 — 展示空间运动轨迹（如板凳龙运动）"""
    fig = plt.figure(figsize=(8, 6))
    ax = fig.add_subplot(111, projection='3d')
    
    ax.plot(x, y, z, 'b-', linewidth=1.0, alpha=0.8)
    ax.scatter(x[0], y[0], z[0], c='#059669', s=50, marker='o', label='起点')
    ax.scatter(x[-1], y[-1], z[-1], c='#DC2626', s=50, marker='s', label='终点')
    
    ax.set_xlabel('X (m)', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_ylabel('Y (m)', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_zlabel('Z (m)', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold')
    ax.legend(fontsize=8, prop={'family': 'Noto Sans CJK SC'})
    ax.view_init(elev=20, azim=60)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

### 2. 高级统计图

#### 小提琴图 + 箱线图 + 散点 (三合一)

```python
def plot_violin_box_scatter(data_dict, title="分布对比图", save_path=None):
    """小提琴图 + 箱线图 + stripplot 三合一 — 论文级分布对比"""
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    groups = list(data_dict.keys())
    positions = list(range(1, len(groups) + 1))
    
    for i, (name, values) in enumerate(data_dict.items()):
        ax.violinplot(values, positions=[i+1], showmeans=False,
                     showmedians=True, widths=0.6)
        ax.boxplot(values, positions=[i+1], widths=0.25,
                  patch_artist=True,
                  boxprops=dict(facecolor='#93C5FD', alpha=0.5),
                  medianprops=dict(color='#DC2626', linewidth=1.5))
    
    ax.set_xticks(positions)
    ax.set_xticklabels(groups, fontsize=8, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='y')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

#### 相关性热力图

```python
def plot_correlation_heatmap(df, method='pearson', title="相关性热力图", save_path=None):
    """论文级相关性矩阵热力图 — 含数值标注"""
    corr = df.corr(method=method)
    
    fig, ax = plt.subplots(figsize=(8, 6.5))
    im = ax.imshow(corr, cmap='RdBu_r', vmin=-1, vmax=1, aspect='equal')
    
    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, fontsize=7, rotation=45, ha='right',
                       fontfamily='Noto Sans CJK SC')
    ax.set_yticklabels(corr.columns, fontsize=7, fontfamily='Noto Sans CJK SC')
    
    for i in range(len(corr.columns)):
        for j in range(len(corr.columns)):
            if i > j:
                val = corr.iloc[i, j]
                color = 'white' if abs(val) > 0.5 else 'black'
                ax.text(j, i, f'{val:.2f}', ha='center', va='center',
                       fontsize=6, color=color, fontweight='bold')
    
    cbar = fig.colorbar(im, ax=ax, shrink=0.8, aspect=30)
    cbar.set_label('相关系数', fontsize=8, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

### 3. 预测区间图

```python
def plot_prediction_interval(time, y_true, y_pred, ci_lower, ci_upper,
                             title="预测区间图", save_path=None):
    """预测区间图 — 展示预测值 + 95%置信区间阴影带"""
    fig, ax = plt.subplots(figsize=(8, 4))
    
    ax.plot(time, y_true, 'k-', linewidth=1.2, label='实际值', zorder=3)
    ax.plot(time, y_pred, '#2563EB', linestyle='--', linewidth=1.2,
           label='预测值', zorder=3)
    ax.fill_between(time, ci_lower, ci_upper, alpha=0.15, color='#2563EB',
                    label='95%预测区间')
    
    ax.set_xlabel('时间', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_ylabel('值', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold')
    ax.legend(fontsize=8, prop={'family': 'Noto Sans CJK SC'})
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

### 4. 雷达图（多模型对比）

```python
def plot_radar_chart(categories, values_dict, title="多模型对比雷达图", save_path=None):
    """雷达图 — 多模型多指标对比，展示各模型在不同维度上的表现"""
    N = len(categories)
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    
    colors = CUMCM_PALETTE_5
    for i, (label, values) in enumerate(values_dict.items()):
        values = list(values) + [values[0]]
        ax.plot(angles, values, 'o-', linewidth=1.5, label=label,
               color=colors[i % len(colors)], markersize=4)
        ax.fill(angles, values, alpha=0.08, color=colors[i % len(colors)])
    
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories, fontsize=8, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0), fontsize=8,
             prop={'family': 'Noto Sans CJK SC'})
    ax.set_ylim(0, 1)
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

### 5. 论文级多面板组合图

```python
def plot_figure_panels(panels, layout="2x2", title="多面板组合图", save_path=None):
    """
    论文级多面板组合图（国赛每张图独立，美赛可组合）
    
    panels: [{"func": plot_func, "kwargs": {...}, "label": "a"}, ...]
    layout: "2x2" | "1x3" | "2x3" | "3x2" | "1x2" | "2x1"
    """
    layout_map = {
        "2x2": (2, 2), "1x3": (1, 3), "2x3": (2, 3),
        "3x2": (3, 2), "1x2": (1, 2), "2x1": (2, 1),
    }
    nrows, ncols = layout_map.get(layout, (2, 2))
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(7.2*ncols/2, 5*nrows/2))
    axes = axes.flatten() if nrows*ncols > 1 else [axes]
    
    for i, panel in enumerate(panels):
        if i >= len(axes):
            break
        ax = axes[i]
        if 'func' in panel:
            panel['func'](ax=ax, **panel.get('kwargs', {}))
        if 'label' in panel:
            ax.text(-0.1, 1.05, f'({panel["label"]})', transform=ax.transAxes,
                   fontsize=10, fontweight='bold', fontfamily='Noto Sans CJK SC')
    
    for i in range(len(panels), len(axes)):
        axes[i].set_visible(False)
    
    fig.suptitle(title, fontsize=12, fontfamily='Noto Sans CJK SC', fontweight='bold')
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

### 6. Pareto 前沿图

```python
def plot_pareto_front(obj1, obj2, nondominated_mask=None,
                      title="Pareto前沿图", save_path=None):
    """Pareto前沿图 — 多目标优化结果展示"""
    fig, ax = plt.subplots(figsize=(6, 5))
    
    if nondominated_mask is not None:
        # 支配解
        ax.scatter(obj1[~nondominated_mask], obj2[~nondominated_mask],
                  c='#D1D5DB', s=20, alpha=0.5, label='支配解', zorder=1)
        # 非支配解
        ax.scatter(obj1[nondominated_mask], obj2[nondominated_mask],
                  c='#2563EB', s=40, edgecolors='#1E40AF', linewidth=0.5,
                  label='Pareto最优解', zorder=2)
        # 连接Pareto前沿
        idx = np.argsort(obj1[nondominated_mask])
        ax.plot(obj1[nondominated_mask][idx], obj2[nondominated_mask][idx],
               '--', color='#EA580C', linewidth=1.5, alpha=0.7, zorder=3)
    else:
        ax.scatter(obj1, obj2, c='#2563EB', s=30, alpha=0.7)
    
    ax.set_xlabel('目标1', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_ylabel('目标2', fontsize=9, fontfamily='Noto Sans CJK SC')
    ax.set_title(title, fontsize=10, fontfamily='Noto Sans CJK SC', fontweight='bold')
    ax.legend(fontsize=8, prop={'family': 'Noto Sans CJK SC'})
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    return fig
```

---

## 图表数量分配建议（v5.2 更新：强制生成+用户选择）

**原则：S5 阶段尽可能多地生成图表，S6 阶段由用户筛选。下表为最低要求，实际生成应超过此数。**

| 问题类型 | 最低图表数 | 推荐生成数 | 数据图 | 流程/架构图 | 检验图 |
|---------|-----------|-----------|--------|-----------|--------|
| 物理建模 | 18 | 22-28 | 8-12 | 4-5 | 6-8 |
| 优化决策 | 20 | 25-30 | 10-14 | 4-5 | 6-8 |
| 预测预报 | 18 | 22-28 | 10-14 | 3-4 | 5-7 |
| 综合评价 | 18 | 22-28 | 10-13 | 3-4 | 5-7 |
| 分类判别 | 18 | 22-28 | 10-13 | 3-4 | 5-7 |
| 聚类分析 | 16 | 20-25 | 10-12 | 3-4 | 4-6 |
| 统计分析 | 16 | 20-25 | 10-12 | 2-3 | 5-7 |
| 图论网络 | 15 | 18-23 | 8-10 | 4-5 | 4-5 |
| 经济建模 | 18 | 22-28 | 8-12 | 3-4 | 7-9 |
| 排队论 | 15 | 18-23 | 9-11 | 3-4 | 4-6 |
| 博弈论 | 16 | 20-25 | 9-11 | 3-4 | 5-7 |
| 微分方程 | 17 | 20-25 | 10-12 | 3-4 | 5-7 |
| 信号处理 | 16 | 20-25 | 11-13 | 2-3 | 4-6 |
| 图像处理 | 16 | 20-25 | 11-13 | 2-3 | 4-6 |

---

## 图表快速参考

```python
def get_chart_templates(problem_type: str) -> list:
    """根据问题类型获取推荐的图表模板列表（覆盖14种问题类型：物理建模、优化决策、预测预报、综合评价、分类判别、聚类分析、统计分析、图论网络、经济建模、排队论、博弈论、微分方程、信号处理、图像处理）"""
    return CHART_ROUTING.get(problem_type, [
        ("数据分布图", "scipilot", "箱线/直方图/散点图"),
        ("模型结果图", "scipilot", "折线图/柱状图"),
        ("检验图", "model-validation", "残差图/灵敏度图"),
        ("流程图", "cumcm-academic-flowchart", "算法流程"),
        ("结构图", "cumcm-academic-flowchart", "框架/架构/Pipeline"),
    ])
```

---
