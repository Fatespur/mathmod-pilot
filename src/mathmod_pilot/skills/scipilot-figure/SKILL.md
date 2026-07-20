---
name: "scipilot-figure-cumcm"
description: "数学建模竞赛（CUMCM/MCM）专属数据可视化增强模块。v5.3：S5多样化可视化原则——强制生成所有适用图表类型（雷达图/气泡图/热力图/3D曲面/堆叠面积/小提琴图/哑铃图/瀑布图/平行坐标/流向图/环形图/联合分布等），图表选择权完全交给用户。基于 scipilot-figure-skill 核心能力扩展：问题类型→图表自动路由、3D可视化、高级统计图、预测区间图、雷达图、交互式图表、论文级多面板组合。v3：3D+高级统计+预测区间+雷达图+Pareto+多面板。v4：补齐经济建模/排队论/博弈论/微分方程/信号处理/图像处理图表路由。v5：新增Pyecharts地理可视化、Plotly交互式3D、networkx动态网络图、matlab-figure路由、系统动力学可视化。与 diagram-generator、matlab-figure、nature-figure 互补，构成完整竞赛绘图工具链。v5.3：新增 figures/candidates/ 超额供图机制——除论文所需图表外，额外生成候选图表供用户选择，附带 README.md 清单和 selection_guide.md 选择指南。"
---

# SciPilot Figure — 数学建模竞赛专属增强（v5.3）

> 基于 scipilot-figure-skill 核心能力，专为数学建模竞赛（CUMCM/MCM）扩展的高级可视化模块。v5.3 新增：figures/candidates/ 超额供图机制——除论文所需图表外，额外生成候选图表供用户选择，附带 README.md 清单和 selection_guide.md 选择指南。与 diagram-generator、matlab-figure、nature-figure 共同构成完整竞赛绘图工具链。

## 与 Skill 组的关系

本 Skill 定位为 Pipeline S5 阶段（可视化）的**主调度器**，与以下 Skill 协同工作：

| Skill | 角色 | 调用时机 |
|-------|------|---------|
| **scipilot-figure-skill** | 数据可视化顾问（选图+画图） | 本模块的数据剖析和选图阶段，提供8步工作流 |
| **diagram-generator** | 算法流程图/框架图/架构图/Pipeline图（matplotlib.patches） | CHART_ROUTING 中标注 `diagram-generator` 的图表 |

| **matlab-figure** | MATLAB 专属绘图（surf/mesh/pcolor/quiver/Simulink） | 需要 MATLAB 工具链时，由 MATLAB路由表分发 |
| **nature-figure** | Nature/高影响力期刊级图表（Python/R双后端） | 美赛 MCM 论文投稿级图表需求 |
| **model-validation** | 模型验证图表（灵敏度/残差诊断/蒙特卡洛） | CHART_ROUTING 中标注 `model-validation` 的图表 |

**核心原则：** 本模块作为 S5 入口，接收 S1（problem-analyzer v8）的问题类型分类结果，根据 CHART_ROUTING 将图表任务分发到各专项 Skill，确保每个图表使用最合适的工具。

**Python/MATLAB 双轨选择：** 同一类图表（如三维曲面）可同时路由到 Python 轨道（scipilot-figure-skill 的 plot_surface）或 MATLAB 轨道（matlab-figure 的 surf/mesh），由用户根据团队工具链选择。数据通过 CSV/MAT 中间文件实现互通。

---

## S5 多样化可视化原则（v5.2 新增，v5.3 增强）

### 核心原则：生成所有，用户选择

**S5 阶段必须尽可能多地生成所有适用图表类型，而不是只生成少量基础图表。最终的图表选择权完全交给用户（在 S6 论文写作阶段自行决定使用哪些图表）。**

理由：
- 美赛（MCM）对图表美观度和多样性要求极高，评审会根据图表质量判断论文水平
- 用户最了解论文的论证逻辑和叙事结构，应由用户决定哪些图表最能支撑论文论点
- 提前生成所有图表可以避免后续反复补充，节省总时间
- 不同图表类型揭示数据的不同侧面，提供更多分析视角

### 通用图表类型清单（UNIVERSAL_CHART_PALETTE）

以下图表类型应在 S5 阶段逐项检查，凡数据支持的就生成：

| # | 图表类型 | 英文名 | 适用条件 | 优先级 |
|---|---------|--------|---------|--------|
| 1 | 柱状图（分组/堆叠） | Bar Chart | 任何分类对比 | 必须 |
| 2 | 折线图 | Line Chart | 任何时序/趋势数据 | 必须 |
| 3 | 散点图 | Scatter Plot | 任何二维数值关系 | 必须 |
| 4 | Pareto 前沿图 | Pareto Front | 多目标优化（≥2目标） | 必须 |
| 5 | 热力图 | Heatmap | 矩阵数据/参数灵敏度 | 必须 |
| 6 | 雷达图 | Radar Chart | 多维度对比（≥3维度） | 强烈推荐 |
| 7 | 小提琴图/箱线图 | Violin/Box Plot | 分布对比/蒙特卡洛结果 | 强烈推荐 |
| 8 | 堆叠面积图 | Stacked Area | 累积量随时间变化 | 强烈推荐 |
| 9 | 气泡图 | Bubble Chart | 三维数据（x,y,size） | 强烈推荐 |
| 10 | 3D 曲面图 | 3D Surface | 二维参数空间+函数值 | 推荐 |
| 11 | 哑铃图 | Dumbbell Chart | 前后对比（理想vs非理想） | 推荐 |
| 12 | 瀑布图 | Waterfall Chart | 成本/收益构成分解 | 推荐 |
| 13 | 桑基/流向图 | Sankey/Flow | 资源/物资流动路径 | 推荐 |
| 14 | 环形图/旭日图 | Donut/Sunburst | 构成比例（多层级） | 推荐 |
| 15 | 平行坐标图 | Parallel Coordinates | 高维数据可视化（≥4维） | 推荐 |
| 16 | 联合分布图 | Joint Distribution | 双变量分布+边际分布 | 推荐 |
| 17 | 龙卷风图 | Tornado Chart | 灵敏度分析结果 | 推荐 |
| 18 | 蒙特卡洛分布图 | Monte Carlo Dist. | 不确定性量化 | 推荐 |
| 19 | 模型架构图 | Architecture Diagram | 多模型/多子问题关系 | 必须 |
| 20 | 算法流程图 | Algorithm Flowchart | 任何模型求解算法 | 必须 |
| 21 | Pipeline 流程图 | Pipeline Diagram | 整体建模流程 | 必须 |
| 22 | 问题分析框架图 | Framework Diagram | 问题分解+方法选择 | 推荐 |

### 图表生成策略

```
S5 执行流程：
1. 从 S1 analysis 获取 problem_type 和 sub_problems 数据
2. 从 S3 results 获取所有数值结果
3. 遍历 UNIVERSAL_CHART_PALETTE，逐项检查数据是否支持
4. 对每个适用图表类型，生成对应的数据可视化
5. 同时调用 diagram-generator 生成流程/架构图
6. 最终输出：所有图表集中存放在 figures/ 目录
7. S6 论文写作时，用户从 figures/ 中自行选择需要的图表

反模式（禁止）：
- ❌ 只生成柱状图（"感觉只有条状图"）
- ❌ 认为"图表够多了"就停止生成
- ❌ 在 S5 阶段替用户决定"哪些图表不需要"
- ❌ 把图表选择逻辑放在 S6 论文写作里
```

### 问题类型→图表数量强制要求

| 问题类型 | 最少图表数 | 必须包含的图表类型 |
|---------|-----------|-------------------|
| 优化决策 | ≥20 | 柱状图、折线图、Pareto前沿、气泡图、雷达图、热力图、龙卷风图、瀑布图、3D曲面、小提琴图、哑铃图、平行坐标、堆叠面积、环形图、联合分布、架构图、流程图、Pipeline图 |
| 物理建模 | ≥18 | 柱状图、3D轨迹、3D曲面、相图、龙卷风图、残差诊断、蒙特卡洛分布、架构图、流程图 |
| 预测预报 | ≥18 | 折线图、预测区间、ACF/PACF、精度对比、特征重要性、雷达图、残差诊断、架构图 |
| 综合评价 | ≥18 | 柱状图、热力图、雷达图、平行坐标、权重分布、排名变化、灵敏度热力图、架构图 |
| 经济建模 | ≥18 | 折线图、残差诊断、脉冲响应、方差分解、稳健性森林图、热力图、架构图 |
| 其他类型 | ≥15 | 根据 CHART_ROUTING + UNIVERSAL_CHART_PALETTE 交叉检查 |


### figures/candidates/ 超额供图机制（v5.3 新增）

**核心原则：除论文必需图表外，必须额外生成候选图表，供用户在 S6 写作时自由选择。**

理由：
- 论文写作阶段（S6）用户可能发现需要额外的图表来支撑论证
- 不同图表类型揭示数据的不同侧面，提供更多分析视角
- 提前生成候选图表可以避免 S6→S5 的回溯，节省总时间
- 用户最了解论文的论证逻辑，应由用户决定哪些图表最能支撑论文论点

#### 目录结构

```
figures/
├── fig1_correlation_heatmap.png/svg     # 论文必需图表（S6 默认使用）
├── fig2_category_trend.png/svg
├── ...
├── candidates/                          # 候选图表（v5.3 新增）
│   ├── README.md                        # 候选图表清单（含缩略图描述）
│   ├── selection_guide.md               # 按论文章节的选择指南
│   ├── cand_radar_category.png/svg      # 品类雷达图
│   ├── cand_bubble_elasticity.png/svg   # 价格弹性气泡图
│   ├── cand_heatmap_seasonal.png/svg    # 季节性热力图
│   ├── cand_violin_distribution.png/svg # 销量分布小提琴图
│   ├── cand_sankey_flow.png/svg         # 供应链流向图（如适用）
│   ├── cand_parallel_coords.png/svg     # 多维度平行坐标图
│   └── ...                              # 更多候选图表
```

#### 候选图表生成规则

| 条件 | 候选图表类型 | 数量 |
|------|-------------|------|
| 任何问题 | 雷达图、气泡图、小提琴图、堆叠面积图 | ≥4 |
| 时序数据 | 季节性热力图、ACF/PACF 图、预测区间图 | ≥3 |
| 优化问题 | 3D 曲面图、哑铃图、平行坐标图 | ≥3 |
| 统计/关联分析 | 联合分布图、相关性网络图 | ≥2 |
| 经济/商业 | 瀑布图、环形图、桑基图 | ≥3 |
| **总计** | **论文必需图 + 候选图** | **≥15 张（必需）+ ≥8 张（候选）** |

#### README.md 模板

```markdown
# 候选图表清单 (Candidate Figures)

> 以下图表为 S5 阶段额外生成的候选图表，供 S6 论文写作时选择使用。
> 每张图表已生成 PNG（300dpi）和 SVG 两种格式。

## 候选图表列表

| 文件名 | 图表类型 | 描述 | 推荐使用场景 |
|--------|---------|------|-------------|
| cand_radar_category.png | 雷达图 | 6品类多维度对比 | 4.1.1 品类关联分析 |
| cand_bubble_elasticity.png | 气泡图 | 价格弹性×销量×损耗率 | 4.2.2 需求函数分析 |
| ... | ... | ... | ... |

## 使用建议

1. 打开每张候选图表的 PNG 预览，评估是否适合论文
2. 如果适合，将对应文件复制到 figures/ 目录并重命名为论文图号
3. 在论文中引用时使用标准图题格式：`图X 图表标题`
4. 不需要的候选图表可以保留在 candidates/ 目录，不影响论文
```

#### selection_guide.md 模板

```markdown
# 候选图表选择指南

## 按论文章节推荐

### 4.1 问题一（关联分析）
- 推荐：cand_radar_category.png（品类雷达图）
- 推荐：cand_heatmap_seasonal.png（季节性热力图）
- 备选：cand_violin_distribution.png（销量分布）

### 4.2 问题二（品类优化）
- 推荐：cand_bubble_elasticity.png（弹性气泡图）
- 推荐：cand_3d_surface.png（3D 利润曲面）
- 备选：cand_parallel_coords.png（多维平行坐标）

### 4.3 问题三（单品优化）
- 推荐：cand_dumbbell_compare.png（单品哑铃对比图）
- 备选：cand_waterfall_profit.png（利润瀑布图）

### 6. 模型检验
- 备选：cand_sankey_flow.png（供应链流向图）
```

#### 生成检查清单

S5 完成后必须确认：
- [ ] figures/ 目录下论文必需图表 ≥ 12 张（PNG+SVG）
- [ ] figures/candidates/ 目录下候选图表 ≥ 8 张（PNG+SVG）
- [ ] figures/candidates/README.md 已生成
- [ ] figures/candidates/selection_guide.md 已生成
- [ ] 所有图表中文标注、300dpi


---

## 问题类型→图表自动路由

```python
CHART_ROUTING = {
    "物理建模": [
        ("频谱/波形图", "scipilot", "折线图 + annotations 标注峰值"),
        ("3D轨迹图", "scipilot", "3D散点/线图 展示空间运动；备选 matlab-figure: surf 曲面"),
        ("参数灵敏度龙卷风图", "model-validation", "横向柱状 + 高亮高风险参数"),
        ("残差诊断图", "model-validation", "四合一图：Q-Q + 残差-拟合 + 直方图 + 时序"),
        ("蒙特卡洛分布图", "model-validation", "直方图 + KDE + 95%CI竖线"),
        ("模型架构图", "diagram-generator", "模型关系 + 三层验证层级"),
        ("算法流程图", "diagram-generator", "步骤1-5 + 本题变量标注"),
    ],
    "优化决策": [
        # 基础对比图（必须）
        ("方案对比柱状图", "scipilot", "分组柱状图：成本/时间/CO2 等指标多方案对比"),
        ("方案对比折线图", "scipilot", "折线图：Pareto比例扫描下的指标变化趋势"),
        # 多目标分析（必须）
        ("Pareto前沿图", "scipilot", "散点图 + 非支配解高亮 + 最优方案标注"),
        ("Pareto气泡图", "scipilot", "气泡图：x=成本, y=时间, 气泡大小=CO2 — 三维权衡"),
        ("3D权衡曲面", "scipilot", "3D曲面图：成本×时间×CO2 三维空间可视化"),
        # 多维度对比（强烈推荐）
        ("雷达图", "scipilot", "多方案多指标雷达图（≥4维度）"),
        ("平行坐标图", "scipilot", "高维Pareto前沿平行坐标可视化"),
        ("哑铃图", "scipilot", "理想vs非理想条件前后对比"),
        # 成本/构成分析（推荐）
        ("瀑布图", "scipilot", "成本构成分解瀑布图"),
        ("环形图", "scipilot", "排放/资源构成比例环形图"),
        ("堆叠面积图", "scipilot", "累积运输量随时间变化"),
        # 灵敏度与不确定性（必须）
        ("灵敏度热力图", "model-validation", "参数×指标 灵敏度矩阵热力图"),
        ("灵敏度龙卷风图", "model-validation", "横向柱状 + 高亮高风险参数"),
        ("蒙特卡洛分布图", "model-validation", "直方图 + KDE + 95%CI竖线"),
        ("小提琴分布图", "model-validation", "蒙特卡洛结果的小提琴分布对比"),
        # 变量关系（推荐）
        ("联合分布图", "scipilot", "成本vs时间 散点图 + 边际KDE分布"),
        ("约束满足可视化", "scipilot", "热力图/散点图 展示可行域"),
        # 物流/流向（推荐）
        ("运输流向图", "scipilot", "桑基图/流向图 展示物资流动路径"),
        # 流程/架构图（必须）
        ("模型架构图", "diagram-generator", "子问题关系 + 数据流 + 三层验证"),
        ("算法流程图", "diagram-generator", "Branch & Bound / MILP求解流程"),
        ("问题分析框架图", "diagram-generator", "问题→方法→求解→验证 纵向框架"),
        ("Pipeline流程图", "diagram-generator", "S0-S7 建模流程总览"),
    ],
    "预测预报": [
        ("时序预测图", "scipilot", "折线图 + 预测区间阴影带"),
        ("残差自相关图", "scipilot", "ACF/PACF 图"),
        ("预测精度对比图", "scipilot", "多模型折线图 + RMSE标注"),
        ("特征重要性图", "scipilot", "横向柱状，按重要性排序"),
        ("模型对比雷达图", "scipilot", "多模型多指标雷达图"),
    ],
    "综合评价": [
        ("权重分布图", "scipilot", "横向柱状 + 权重值标注"),
        ("排名变化图", "scipilot", "平行坐标/折线图 展示不同方法排名"),
        ("评价结果热力图", "scipilot", "评价对象×指标 热力图"),
        ("权重敏感性热力图", "model-validation", "热力图 展示权重扰动下排名变化"),
        ("因子载荷图", "scipilot", "散点图 展示主成分/因子贡献"),
    ],
    "分类判别": [
        ("混淆矩阵热力图", "scipilot", "分类结果可视化"),
        ("ROC曲线", "scipilot", "多模型ROC曲线 + AUC标注"),
        ("PR曲线", "scipilot", "不平衡数据必备"),
        ("特征重要性排序", "scipilot", "横向柱状"),
        ("决策边界可视化", "scipilot", "2D散点 + 决策边界等高线"),
    ],
    "聚类分析": [
        ("聚类结果降维图", "scipilot", "t-SNE/UMAP 2D散点 + 颜色区分簇"),
        ("轮廓系数图", "scipilot", "各簇轮廓系数分布"),
        ("聚类热力图", "scipilot", "聚类中心/样本特征矩阵"),
        ("树状图", "scipilot", "层次聚类结果"),
        ("肘部法则图", "scipilot", "k vs 聚类质量指标"),
    ],
    "统计分析": [
        ("箱线/小提琴图", "scipilot", "分组比较 + stripplot叠加"),
        ("相关性热力图", "scipilot", "Pearson/Spearman相关矩阵"),
        ("Q-Q图", "scipilot", "正态性检验"),
        ("效应量森林图", "scipilot", "多组比较 + 置信区间"),
        ("交互效应图", "scipilot", "双因素交互作用"),
    ],
    "图论网络": [
        ("网络拓扑图", "diagram-generator", "节点-边可视化；备选 networkx 动态网络图"),
        ("最短路径图", "scipilot", "路径高亮"),
        ("流量分布图", "scipilot", "热力图/面积图"),
        ("算法复杂度图", "scipilot", "n vs 运行时间"),
    ],
    "经济建模": [
        ("时序趋势图", "scipilot", "折线图 + 趋势线 + 标注断点"),
        ("残差诊断四合一图", "model-validation", "Q-Q + 残差-拟合 + 直方图 + 时序"),
        ("脉冲响应图", "scipilot", "多变量脉冲响应函数"),
        ("方差分解图", "scipilot", "预测误差方差分解堆积图"),
        ("稳健性检验对比图", "model-validation", "多策略系数森林图"),
        ("模型架构图", "diagram-generator", "经济理论→计量模型→检验流程"),
    ],
    "排队论": [
        ("队长分布图", "scipilot", "柱状图 + 理论分布曲线叠加"),
        ("等待时间分布图", "scipilot", "直方图 + KDE + 理论分布"),
        ("服务强度敏感图", "scipilot", "折线图: ρ vs 平均队长/等待时间"),
        ("系统状态转移图", "diagram-generator", "Markov链状态转移"),
        ("多服务台对比图", "scipilot", "分组柱状图: c=1,2,3..."),
    ],
    "博弈论": [
        ("收益矩阵热力图", "scipilot", "热力图 + 数值标注"),
        ("策略演化轨迹图", "scipilot", "相图: 策略比例随时间变化"),
        ("均衡敏感度图", "scipilot", "参数变化对均衡的影响"),
        ("博弈树/博弈流图", "diagram-generator", "决策节点+收益叶子"),
        ("Pareto边界图", "scipilot", "多目标收益空间"),
    ],
    "微分方程": [
        ("相图/向量场图", "scipilot", "2D相平面 + 向量场 + 轨线；备选 matlab-figure: quiver 向量场"),
        ("时间演化图", "scipilot", "多变量时间历程曲线"),
        ("参数分岔图", "scipilot", "参数 vs 稳态解"),
        ("稳定性分析图", "scipilot", "特征值分布 + 稳定区域"),
        ("数值方法对比图", "scipilot", "不同方法精度/效率对比"),
    ],
    "信号处理": [
        ("时域波形图", "scipilot", "折线图 + 标注峰值/谷值"),
        ("频谱图", "scipilot", "FFT幅度谱 + 相位谱"),
        ("时频图/谱图", "scipilot", "短时傅里叶变换 spectrogram"),
        ("小波变换图", "scipilot", "小波尺度图 scalogram"),
        ("滤波效果对比图", "scipilot", "原始vs滤波后信号叠加"),
    ],
    "图像处理": [
        ("原始与处理后对比图", "scipilot", "并排显示 原始/处理后"),
        ("边缘检测结果图", "scipilot", "多方法边缘检测对比"),
        ("分割结果图", "scipilot", "原始图像 + 分割掩码叠加"),
        ("混淆矩阵热力图", "scipilot", "分类结果可视化"),
        ("特征可视化图", "scipilot", "CNN特征图/t-SNE降维"),
    ],
}
```

---

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
        ("流程图", "diagram-generator", "算法流程"),
        ("结构图", "diagram-generator", "框架/架构/Pipeline"),
    ])
```

---

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
| 因果回路图 | diagram-generator | 展示反馈关系 |
| 存量流量图（SFD） | diagram-generator 或 matlab-figure（Simulink） | 展示SD模型结构 |
| 动态行为图 | scipilot (matplotlib折线) | 展示变量时间演化 |
| 箭头/向量场图 | scipilot-figure-skill（matplotlib quiver）或 matlab-figure（quiver） | 展示系统动态方向 |
| Simulink仿真模型 | matlab-figure（Simulink） | 系统动力学完整仿真 |
| Vensim模型可视化 | matlab-figure（Vensim集成） | Vensim模型导入与展示 |

---

## 版本历史

- **v1**：初始版本，基于 scipilot-figure-skill 核心能力扩展数学建模竞赛图表
- **v2**：新增 3D可视化、高级统计图、预测区间图、雷达图、Pareto前沿图、多面板组合
- **v3**：完善问题类型路由（8种）、图表分配建议、get_chart_templates 函数
- **v4**：补齐经济建模/排队论/博弈论/微分方程/信号处理/图像处理图表路由，CHART_ROUTING 覆盖 14 种问题类型
- **v5**：新增 Pyecharts 地理可视化（地图/时间线/金字塔图）、Plotly 交互式3D散点与分子结构图、networkx 动态网络图、matlab-figure绘图方法路由、系统动力学可视化（箭头图/存量流量图）
- **v5.1**：完善 MATLAB 路由表，统一标注为 `matlab-figure`（替代泛化的"MATLAB"）；更新"与 Skill 组的关系"章节，对齐当前14个Skill的完整生态；系统动力学路由表补充 matlab-figure（Simulink/Vensim）；CHART_ROUTING 中关键图表增加 matlab-figure 备选标注
- **v5.2**：新增"S5 多样化可视化原则"——强制生成所有适用图表类型，引入 UNIVERSAL_CHART_PALETTE（22种图表类型逐项检查），图表选择权完全交给用户（S6 阶段自行筛选）；"优化决策" CHART_ROUTING 从5项扩展到22项（含雷达图、气泡图、3D曲面、热力图、瀑布图、哑铃图、平行坐标、堆叠面积、环形图、联合分布、小提琴图、流向图、框架图）；图表数量分配建议从"推荐"改为"最低要求+推荐生成数"，优化决策最低20张、推荐25-30张
- **v5.3**：新增 figures/candidates/ 超额供图机制——除论文所需图表外，额外生成候选图表（≥8张）供用户选择，附带 README.md 清单和 selection_guide.md 选择指南；S5 多样化可视化原则标题增强为"v5.2 新增，v5.3 增强"；新增候选图表生成规则表、目录结构模板、README.md 模板、selection_guide.md 模板、生成检查清单
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

- **当前版本**: v5.3
- **冷却期**: 上次进化 N/A，下次可用 N/A
- **连续进化次数**: 0
- **关联缺口**: G-003, G-008
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
