# 绘图硬规则与后端路由

## 内容索引

  - 硬性约束
    - 必须遵守
    - 禁止事项
  - Pyecharts 地理可视化（v5 新增）
  - Plotly 交互式3D可视化（v5 新增）
  - networkx 动态网络图（v5 新增）
  - matlab-figure绘图方法路由（v5 新增）
  - 系统动力学可视化路由（v5 新增）
  - 版本历史

## 硬性约束

### 必须遵守
1. 所有图表中文标注（国赛）或英文标注（美赛）
2. 300 DPI PNG + SVG 矢量双格式
3. 图题格式：`图X 图表标题`（国赛）/ `Figure X: Title`（美赛）
4. 色盲安全配色（Okabe-Ito）+ 灰度预览
5. 字号：标签 8pt、刻度 7pt、图注 9pt
6. 每张图一个核心结论，不过度拥挤
7. 误差必有交代（SD/SEM/CI + n）

### 禁止事项
1. 禁止饼图（用横向柱状替代）
2. 禁止 3D 柱状图/3D 饼图（视角扭曲数据）
3. 禁止 rainbow/jet 色图
4. 禁止多面板合并为一张图（国赛）
5. 禁止图像后留白超过页面 15%
6. 禁止图中文字 < 6pt

---

## Pyecharts 地理可视化（v5 新增）

包含地图绘制代码模板:

```python
from pyecharts import options as opts
from pyecharts.charts import Map, Timeline, Funnel

def plot_choropleth_map(data_dict, title="地理分布图", save_path=None):
    """Pyecharts 中国地图 - 热力值填充"""
    map_chart = (
        Map(init_opts=opts.InitOpts(width="800px", height="600px"))
        .add("数值", [list(z) for z in data_dict.items()], "china")
        .set_global_opts(
            title_opts=opts.TitleOpts(title=title),
            visualmap_opts=opts.VisualMapOpts(max_=max(data_dict.values())),
        )
    )
    if save_path:
        map_chart.render(save_path)
    return map_chart
```

---

## Plotly 交互式3D可视化（v5 新增）

```python
import plotly.graph_objects as go
import plotly.express as px

def plot_3d_scatter_interactive(x, y, z, color=None, title="3D散点图", save_path=None):
    """Plotly 3D交互式散点图"""
    fig = go.Figure(data=[go.Scatter3d(
        x=x, y=y, z=z, mode='markers',
        marker=dict(size=3, color=color, colorscale='Viridis', opacity=0.8)
    )])
    fig.update_layout(title=title, scene=dict(xaxis_title='X', yaxis_title='Y', zaxis_title='Z'))
    if save_path:
        fig.write_html(save_path)
    return fig
```

---

## networkx 动态网络图（v5 新增）

```python
import networkx as nx
import matplotlib.pyplot as plt

def plot_network_graph(edges, node_labels=None, title="网络拓扑图", save_path=None):
    """networkx 网络关系图"""
    G = nx.Graph()
    G.add_edges_from(edges)
    pos = nx.spring_layout(G, seed=42)
    fig, ax = plt.subplots(figsize=(10, 8))
    nx.draw(G, pos, ax=ax, with_labels=True, node_color='#2563EB', 
            node_size=500, font_size=8, edge_color='#93C5FD')
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
    return fig
```

---

## matlab-figure绘图方法路由（v5 新增）

添加MATLAB绘图方法对照表:

| Python（scipilot-figure-skill） | matlab-figure | 图型 | 适用场景 |
|-------------------------------|---------------|------|---------|
| plot_surface / plot_3d_surface | surf / mesh | 三维曲面 | 物理建模、温度场、应力场 |
| plot_heatmap / seaborn heatmap | pcolor / imagesc | 热力图 | 相关性矩阵、空间分布 |
| plot_quiver / ax.quiver | quiver / quiver3 | 向量场 | 流体力学、电磁场、相图 |
| plot_errorbar / ax.errorbar | errorbar | 误差棒 | 实验数据、模型对比 |
| plot_fill / ax.fill_between | patch / fill | 填充区域 | 置信区间、可行域 |
| annotate / ax.text | text / annotation | 文本标注 | 图中标注、公式说明 |

| — | Simulink | 系统动力学建模 | 存量流量模型、反馈系统 |
| — | Vensim 集成 | 系统动力学可视化 | 因果回路图、SD模型仿真 |
| — | parula 色标 | 专业配色 | Nature 推荐色标 |

**使用决策：**
- 默认使用 Python 轨道（scipilot-figure-skill + scipilot-figure-cumcm）
- 当题目要求 MATLAB、需要 Simulink/Vensim 系统动力学、或需要 parula 色标时，切换到 matlab-figure
- 数据通过 CSV/MAT 中间文件互通，`scipilot-figure-cumcm` 负责 Python 轨道，`matlab-figure` 负责 MATLAB 轨道

---

## 系统动力学可视化路由（v5 新增）

| 图型 | 推荐工具 | 用途 |
|------|---------|------|
| 因果回路图 | cumcm-academic-flowchart | 展示反馈关系 |
| 存量流量图（SFD） | cumcm-academic-flowchart 或 matlab-figure（Simulink） | 展示SD模型结构 |
| 动态行为图 | scipilot (matplotlib折线) | 展示变量时间演化 |
| 箭头/向量场图 | scipilot-figure-skill（matplotlib quiver）或 matlab-figure（quiver） | 展示系统动态方向 |
| Simulink仿真模型 | matlab-figure（Simulink） | 系统动力学完整仿真 |
| Vensim模型可视化 | matlab-figure（Vensim集成） | Vensim模型导入与展示 |

---
