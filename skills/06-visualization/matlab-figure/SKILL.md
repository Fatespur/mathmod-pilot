---
name: matlab-figure
title: MATLAB Native 3D & Dynamic Visualization
category: visualization
stage: S5A
description: "MATLAB 原生图表生成：3D 三维曲面 (surf/mesh)、矢量场流向 (quiver)、Parula 科学色标与系统动力学仿真可视化"
inputs: ["matlab_surface_data.mat", "trajectory_matrix.csv"]
outputs: ["matlab_figure_3d.png", "matlab_figure_3d.svg", "matlab_figure_code.m"]
dependencies: ["mle-solver"]
---

## Codex execution contract

- **Language:** Match the requested deliverable language. Default CUMCM labels to `zh-CN` and MCM/ICM labels to `en-US`; preserve MATLAB syntax, symbols, units, schema keys, paths, and identifiers.
- **Inspect first:** Validate source data, target dimensions, required MATLAB/Simulink runtime, upstream metrics, and the intended paper claim.
- **Progressive disclosure:** Keep detailed Chinese MATLAB recipes below or in `references/`; load only the active chart family.
- **Run, render, inspect:** Execute MATLAB code when the runtime exists, export the figure, and inspect the rendered output. If MATLAB is unavailable, provide code and report that rendering remains unverified.
- **Evidence and privacy:** Trace plotted values to local artifacts; do not send data to external services without explicit authorization.
- **Handoff:** Use `pipeline_manifest.json`; on first pipeline use read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json). Record code, data, exports, runtime, QA, warnings, and provenance.
- **Routing:** Send chart selection to `$scipilot-figure-skill` and method framework diagrams to `$cumcm-academic-flowchart`.
- **Completion:** Mark final only after dimensions, fonts, units, crop, color, and export integrity are checked.

# MATLAB Figure — 数学建模竞赛绘图（v1）

你是**MATLAB 数学建模竞赛绘图专家**。本 skill 补充 Python 绘图生态，提供 MATLAB 独有的绘图能力和系统动力学可视化支持。

## 与 Skill 组的关系

- **scipilot-figure-skill**：Python 数据可视化顾问（matplotlib/seaborn/plotly）
- **scipilot-figure-cumcm**：Python 数学建模竞赛增强（问题类型→图表路由）
- **cumcm-academic-flowchart**：算法流程图/框架图/架构图/Pipeline图（draw.io/SVG/透明高分辨率 PNG）
- **本 skill**：MATLAB 专属互补，覆盖 Python 生态中不擅长的 MATLAB 特定功能

## 核心能力

| 能力 | 说明 |
|------|------|
| 三维曲面可视化 | surf/mesh/meshc/meshz 函数 |
| 热力图 | pcolor/imagesc/heatmap |
| 向量场可视化 | quiver/quiver3/streamline |
| 误差棒标注 | errorbar 函数 |
| 填充区域 | patch/fill/fill3 |
| 文本与标注 | text/gtext/annotation |
| 专业色标 | parula/jet/hsv/hot/cool |
| 系统动力学 | Simulink建模 / Vensim集成 / system dynamics Toolbox |

## 使用决策

**何时使用 MATLAB 而非 Python：**
- 题目要求使用 MATLAB
- 需要 Simulink 系统动力学建模
- 需要 MATLAB 原生 parula 色标或既有 MATLAB 工作流
- 需要 quiver 向量场 overlay 在 surf 曲面上
- 团队只有 MATLAB 可用

## 一、三维曲面可视化

### surf 函数

```matlab
% 三维曲面图
[X, Y] = meshgrid(linspace(-5, 5, 100), linspace(-5, 5, 100));
Z = X .* exp(-X.^2 - Y.^2);

figure('Position', [100, 100, 800, 600]);
surf(X, Y, Z, 'EdgeColor', 'none', 'FaceAlpha', 0.9);
colormap('parula');
colorbar;
xlabel('X', 'FontSize', 12);
ylabel('Y', 'FontSize', 12);
zlabel('Z', 'FontSize', 12);
title('三维曲面图', 'FontSize', 14, 'FontWeight', 'bold');
view(45, 30);
grid on;
```

### mesh 函数

```matlab
% 网格曲面图（带网格线）
mesh(X, Y, Z);
colormap('parula');
xlabel('X'); ylabel('Y'); zlabel('Z');
```

## 二、热力图 (pcolor)

```matlab
% 热力图
data = rand(20, 30);
figure;
pcolor(data);
colormap('parula');
colorbar;
shading interp;  % 平滑着色
xlabel('列'); ylabel('行');
title('热力图');
```

## 三、向量场可视化 (quiver)

```matlab
% 向量场图
[X, Y] = meshgrid(-2:0.2:2, -2:0.2:2);
U = -Y;
V = X;

figure;
quiver(X, Y, U, V, 2, 'LineWidth', 1.5, 'Color', [0.1, 0.4, 0.8]);
xlabel('X'); ylabel('Y');
title('向量场图');
axis equal;
grid on;
```

## 四、误差棒标注 (errorbar)

```matlab
% 误差棒图
x = 1:10;
y = sin(x);
err = 0.1 * rand(1, 10);

figure;
errorbar(x, y, err, 'o-', 'LineWidth', 1.5, 'MarkerSize', 8, ...
         'MarkerFaceColor', [0.1, 0.4, 0.8], 'Color', [0.1, 0.4, 0.8]);
xlabel('X'); ylabel('Y');
title('误差棒图');
grid on;
```

## 五、填充区域 (patch/fill)

```matlab
% 填充区域（置信区间）
x = 0:0.1:10;
y = sin(x);
ci_upper = y + 0.2;
ci_lower = y - 0.2;

figure;
hold on;
% 填充置信区间
fill([x, fliplr(x)], [ci_upper, fliplr(ci_lower)], ...
     [0.1, 0.4, 0.8], 'FaceAlpha', 0.2, 'EdgeColor', 'none');
% 主曲线
plot(x, y, 'LineWidth', 2, 'Color', [0.1, 0.4, 0.8]);
xlabel('X'); ylabel('Y');
title('置信区间图');
grid on;
```

## 六、文本与标注 (text/annotation)

```matlab
% 文本标注
figure;
plot(1:10, sin(1:10), 'o-', 'LineWidth', 2);
text(5, 0.5, '峰值', 'FontSize', 12, 'Color', 'red', ...
     'HorizontalAlignment', 'center');
annotation('textarrow', [0.3, 0.5], [0.7, 0.5], ...
           'String', '关键点', 'FontSize', 10);
```

## 七、专业色标

### parula 色标

```matlab
% parula 是 MATLAB 默认色标，比 jet 更科学
colormap('parula');

% 色标选择指南
% parula: 默认选择，感知均匀，色盲友好
% jet:   不推荐（存在感知不均匀问题）
% hot:   热力数据
% cool:  冷色调数据
% gray:  灰度打印
% hsv:   周期数据
```

## 八、系统动力学可视化

### Simulink 建模

```matlab
% 系统动力学模型在 Simulink 中建模
% 1. 打开 Simulink: simulink
% 2. 新建模型: new_system('sd_model')
% 3. 添加组件: 积分器(Integrator)、增益(Gain)、求和(Sum)、
%              函数(Function)、示波器(Scope)
% 4. 连接组件表示因果关系
% 5. 运行仿真: sim('sd_model')
```

### Vensim 集成

MATLAB 可以通过数据导入/导出与 Vensim 集成：
- 从 Vensim 导出仿真数据到 .mat 文件
- 在 MATLAB 中加载并可视化
- 将 MATLAB 优化结果反馈到 Vensim

```matlab
% 加载 Vensim 导出的数据
load('vensim_output.mat');
% 可视化
plot(time, population, 'LineWidth', 2);
hold on;
plot(time, resources, 'LineWidth', 2);
legend('人口', '资源');
```

## 九、图表导出

```matlab
% 导出为高分辨率 PNG
print('-dpng', '-r300', 'figure.png');

% 导出为矢量 EPS
print('-depsc', '-r300', 'figure.eps');

% 导出为 PDF
print('-dpdf', '-r300', 'figure.pdf');

% 导出为 SVG
print('-dsvg', 'figure.svg');
```

## 十、论文级设计原则

1. **专业色标**：优先使用 parula（感知均匀、色盲友好），避免 jet
2. **误差标注**：存在重复测量或估计不确定性时，使用适当的误差棒或置信区间并在图注说明
3. **图例美观**：位置不遮挡数据，字体大小 ≥ 8pt
4. **坐标轴标签**：包含量纲单位
5. **分辨率**：导出 ≥ 300 DPI
6. **中文支持**：设置 'FontName', 'SimHei' 或 'Microsoft YaHei'
- **本 skill**：MATLAB 专属互补
