# CUMCM 数学建模技能工具箱 (CUMCM Modeling Skills Toolkit)

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue)](pyproject.toml)
[![收录技能](https://img.shields.io/badge/打包技能-15%20个-emerald)](registry/skills.json)
[![建模阶段](https://img.shields.io/badge/覆盖阶段-9%20大阶段-purple)](registry/workflow.json)
[![状态](https://img.shields.io/badge/状态-生产就绪%20%7C%20开箱即用-success)](#)

> **专为全国大学生数学建模竞赛 (CUMCM) 与美赛 (MCM/ICM) 打造的 Agent 原生技能工具箱**  
> *覆盖：赛题机理拆解 → 数据探索预处理 → 反套路模型遴选 → 优化算法求解 → 独立模型验证 → 出版级科研图表 → 规范纯 Markdown 写作 → 终审对账门禁。*

[English README](README.md) | [系统架构设计](docs/architecture.md) | [工作流与门禁机制](docs/workflow.md) | [技能依赖图谱](docs/skill-map.md) | [使用指南](docs/usage.md) | [审计报告](docs/audit/SKILL_INVENTORY.md)

---

## 项目概述

**CUMCM Modeling Skills Toolkit** 是从高水平实战竞赛工程中萃取、去耦、标准化的数学建模全流程工具箱。

它旨在解决传统数学建模中“智能体无脑盲目套模型”、“各阶段缺乏严格契约与断言”、“求解崩溃缺乏科学自愈”、“论文排版繁琐且公式兼容性差”等痛点。工具箱建立在**确定性状态机与强类型工件契约**之上：
- **15 个精选核心技能**：严格对标竞赛真实流程，剔除一切无关的通用软件运维与不稳定网络依赖；
- **反套路门禁**：拒绝形式主义与关键词盲目匹配，强制构建基线模型与主备选投资组合；
- **独立验证放行门禁**：预注册验证计划，严密执行基线超越检验、参数灵敏度分析与误差包络测试；
- **顶级学术流程图引擎**：内置生成国奖水准的双流、泳道方法架构图，一键导出 draw.io、原生 SVG 与透明高清 PNG；
- **纯 Markdown 写作流水线**：Word 原生 OMML 公式适配、三线表规范、严格无目录限制、绝对匿名检测。

---

## 建模工作流全生命周期

```mermaid
flowchart LR
    S0[S0 状态机初始化] --> S1[S1 赛题机理分解]
    S1 --> S2A[S2A 数据预处理]
    S2A --> S2B[S2B 反套路模型遴选]
    S2B --> S3[S3 算法求解执行]
    S3 --> S4[S4 独立模型验证]
    S4 --> S5A[S5A 结论数据图表]
    S4 --> S5B[S5B 学术方法架构图]
    S5A --> S6[S6 规范 Markdown 写作]
    S5B --> S6
    S6 --> S7[S7 终审与对账门禁]
    
    S3 -. 求解发散/崩溃 .-> S3D[S3-dbg 数模自愈排查]
    S3D -. 修复约束 .-> S3
    S4 -. 验证未达标 .-> S2B
    S7 -. 数值错漏 .-> S4
```

---

## 核心技能矩阵 (Skill Catalog)

| 阶段 | 归属分类 | 技能名称 | 核心职责 |
| :---: | :--- | :--- | :--- |
| **S0** | `09-orchestration` | [`modeling-workflow-orchestrator`](skills/09-orchestration/modeling-workflow-orchestrator/) | 全流程状态机控制中枢，负责工件哈希验真、依赖失效级联与回退路由。 |
| **S1** | `01-problem-understanding` | [`problem-analyzer`](skills/01-problem-understanding/problem-analyzer/) | 赛题机理分解，抽取物理实体、变量量纲、目标函数与物理硬断言。 |
| **S2A** | `02-data-analysis` | [`data-processing`](skills/02-data-analysis/data-processing/) | 赛题多源数据解析、缺失值插补、时序/空间特征工程与防穿越预处理。 |
| **S2B** | `03-model-formulation` | [`model-selection`](skills/03-model-formulation/model-selection/) | 执行反套路门禁，构建基线/主选/备选多层次模型投资组合，评估参数可识别性。 |
| **S3** | `04-algorithms-and-solving` | [`mle-solver`](skills/04-algorithms-and-solving/mle-solver/) | 将数学抽象转化为数值优化与启发式算法实现（内置 GA/PSO/SA/MILP），执行断言验证。 |
| **S3-dbg** | `04-algorithms-and-solving` | [`systematic-debugging`](skills/04-algorithms-and-solving/systematic-debugging/) | 数模专属故障自愈：排查物理失真、量纲违规、经济计量反模式与求解发散。 |
| **S4** | `05-validation` | [`model-validation`](skills/05-validation/model-validation/) | 独立模型放行门禁：预注册验证计划，执行基线超越检验、灵敏度与鲁棒性分析。 |
| **S5A** | `06-visualization` | [`scipilot-figure-cumcm`](skills/06-visualization/scipilot-figure-cumcm/) | 论文结论-证据图表规划器，杜绝无效凑数图，控制篇幅信息增益。 |
| **S5A** | `06-visualization` | [`scipilot-figure-skill`](skills/06-visualization/scipilot-figure-skill/) | 出版级科研绘图引擎：专业 Matplotlib/Seaborn 样式、色盲安全调色板与视觉质检。 |
| **S5A** | `06-visualization` | [`matlab-figure`](skills/06-visualization/matlab-figure/) | MATLAB 原生三维曲面 (surf/mesh)、矢量流场 (quiver) 与 Parula 科学色标图。 |
| **S5B** | `06-visualization` | [`cumcm-academic-flowchart`](skills/06-visualization/cumcm-academic-flowchart/) | 学术方法架构与技术路线图生成引擎（支持 draw.io, 原生 SVG, 高清 PNG）。 |
| **S6** | `07-writing` | [`mcm-paper-writing`](skills/07-writing/mcm-paper-writing/) | 纯 Markdown 写作流水线：动态篇幅预算、Word 原生 OMML 公式与无目录匿名排版。 |
| **PH2** | `07-writing` | [`reference-manager`](skills/07-writing/reference-manager/) | GB/T 7714 参考文献标准化与双向引用核验，杜绝虚构文献。 |
| **S7** | `08-quality-assurance` | [`paper-review`](skills/08-quality-assurance/paper-review/) | 终稿全方位审查：数值宏全链溯源对账、符号未定义扫描与匿名合规确认。 |
| **对标** | `08-quality-assurance` | [`winning-paper-analysis`](skills/08-quality-assurance/winning-paper-analysis/) | 历年国奖优秀论文结构库对标：摘要黄金比例、各节篇幅密度与论述范式。 |

---

## 快速上手

### 1. 环境克隆与安装
```bash
git clone https://github.com/Fatespur/mathmod-pilot
cd cumcm-modeling-skills
pip install -r requirements.txt
```

### 2. 结合 AI Agent 使用
工具箱中所有 Skill 均附带完备的 `SKILL.md`。只需在兼容的 Agent 框架中挂载本仓库目录，即可按名唤起：
```markdown
使用技能: $problem-analyzer
任务目标: 对给定赛题进行形式化数学拆解，输出 variables_and_units.json 与 hard_assertions.json
```

### 3. 运行交互式可视化官网
```bash
cd site
npm install
npm run dev
```
在浏览器中打开 `http://localhost:5173` 即可查看兼具美感与功能性的现代学术官网。

---

## 仓库规范与开源许可

- **开源协议**: 本仓库依据 [MIT License](LICENSE) 授权开源，允许自由学术使用与二次开发。
- **知识产权审查**: 详见 [docs/audit/LICENSE_REVIEW.md](docs/audit/LICENSE_REVIEW.md)。
- **贡献指引**: 欢迎提交 Issue 与 Pull Request，详见 [CONTRIBUTING.md](CONTRIBUTING.md)。
