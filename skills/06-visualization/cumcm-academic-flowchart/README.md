# 数学建模竞赛高级学术框架图生成 Skill

`cumcm-academic-flowchart` 面向 CUMCM/MCM/ICM 论文，将题面、方案、论文、源码和数据字段转换为主备双布局的论文级框架图。它先构建 ModelingIR，再由同一 Scene Graph 生成可编辑 draw.io、原生 SVG 和透明高分辨率 PNG，并输出质量报告。

## 适用与不适用

适用于总体技术路线、单问流程、多问依赖、数据处理、优化、预测、评价、数理统计、机理模型、算法闭环、训练推理、模型验证、灵敏度分析、多模型融合、已有 draw.io 优化及 Mermaid/Graphviz 转换。不用于折线图、柱状图、散点图、热力图、地图、普通数学题、无关 UML、海报或文生图插画。

## 安装与 Codex 加载

将本目录复制到 `$CODEX_HOME/skills/cumcm-academic-flowchart`。Python 3.10+ 必需，核心 draw.io/SVG 使用标准库；PNG 使用 Pillow。文档解析和测试依赖见 `requirements.txt`。

## CLI

```powershell
python scripts/cumcm_flowchart.py --input solution.md --output figures/modeling_diagrams `
  --diagram auto --layouts 2 --theme journal-rich --transparent `
  --png-dpi 300 --png-long-edge 4800 --seed 42 --contest-mode
```

支持：`--input --output --diagram --question --layouts --primary-layout --alternative-layout --engine --theme --transparent --background --png-dpi --png-long-edge --svg-text-mode --target-width-mm --language --contest-mode --strict --overwrite --config --seed --debug`。

## 三种输出

- **SVG 是论文优先格式**：真正矢量、文字可选择、透明背景、正确 viewBox。
- **PNG 是兼容格式**：从同一矢量场景直接高分辨率栅格化，默认 300 DPI/4800 px 长边，支持 600 DPI。
- **draw.io 是可编辑源格式**：未压缩合法 XML，可在 diagrams.net 中直接打开并继续编辑。

所有格式使用同一 ModelingIR、布局坐标、节点 ID、颜色和连线，不依赖远程字体或图片。

## 布局与主备机制

布局库覆盖线性、双流、泳道、汇聚/发散、中心辐射、环形、回字形、U 形、蛇形、同心、矩阵、分层架构。每图至少生成 4 个候选，主方案取综合评分最高者；备用方案必须来自不同布局家族、保持相同节点和关键边且差异度不低于 0.55。

## 主题、颜色与透明度

内置 `journal-rich`、`ocean-gradient`、`violet-cyan`、`teal-orange`、`forest-science`、`warm-earth`、`editorial-pastel`、`dark-academic`、`monochrome-print`。使用语义配色而非随机着色。可复制 `assets/themes/*.json` 修改颜色、填充 alpha、边框与箭头透明度，并通过 `--theme` 选择。

## PNG DPI、像素和透明背景

DPI 是打印元数据，实际清晰度同时取决于像素尺寸。默认长边 4800 px，至少不得低于 3200 px。`--transparent` 生成 RGBA PNG；不使用截图、不先低清渲染再放大。

## diagrams.net、SVG 与 PNG

在 [diagrams.net](https://app.diagrams.net/) 选择“文件 → 打开”即可编辑 `.drawio`。SVG 可直接插入 Word/LaTeX 或矢量编辑器。PNG 由 CLI 自动生成；无需 draw.io Desktop。

## 竞赛模式

`--contest-mode` 禁止联网并仅使用本地文件；输出不记录个人绝对路径或身份信息，标记推断步骤，记录 AI 操作并要求用户复核数学逻辑。系统不承诺获奖，也不伪造数据或实验结果。

## 测试

```powershell
python -m compileall .
python -m unittest discover -s tests -v
```

如果安装 pytest，也可执行 `pytest tests -v`。

## 常见问题与限制

- 字体缺失：按 Microsoft YaHei → Noto Sans CJK SC → Source Han Sans SC → SimHei → Arial → sans-serif 降级并写入警告。
- 可选文档依赖缺失：纯文本、源码、JSON 和 YAML 仍可用；报告会列出降级。
- Graphviz、ELK、Mermaid 和 draw.io Desktop 均非核心依赖；核心三格式离线生成。
- 自动评分不能代替作者核对数学逻辑，复杂图可能需要拆成总体图、单问图与验证图。

## 合规声明

实现借鉴公开规范的架构思想，没有复制第三方项目代码。研究来源与许可证说明见 `references/research_sources.md`。竞赛期间必须遵守赛事规则和所在学校要求。

## 四个完整调用示例

总体技术路线：

```powershell
python scripts/cumcm_flowchart.py --input solution.md paper.docx --output figures/overall `
  --diagram overall_route --primary-layout question_swimlane --alternative-layout hub_spoke `
  --layouts 2 --theme journal-rich --transparent --png-dpi 300 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```

回字形算法闭环：

```powershell
python scripts/cumcm_flowchart.py --input optimization.md --output figures/loop `
  --diagram algorithm_loop --primary-layout rectangular_loop --alternative-layout u_shaped `
  --theme teal-orange --transparent --png-dpi 300 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```

双数据流预测架构：

```powershell
python scripts/cumcm_flowchart.py --input multimodal.md model.py --output figures/dual `
  --diagram data_pipeline --primary-layout dual_stream --alternative-layout layered_architecture `
  --theme ocean-gradient --transparent --png-dpi 600 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```

优化已有 draw.io：

```powershell
python scripts/cumcm_flowchart.py --input existing.drawio --output figures/revised `
  --diagram auto --primary-layout layered_architecture --alternative-layout serpentine `
  --theme journal-rich --transparent --png-dpi 300 --png-long-edge 4800 `
  --seed 42 --contest-mode --strict
```
