# CUMCM Agent Skill 完整审计与准入清单 (Skill Inventory & Audit)

> 审计基准目录: `[CUMCM_PROD_ROOT]/.agents/skills/`
> 审计时间: 2026-09-17
> 准入统计: 原始 19 个 | 保留 14 个 (KEEP) | 部分裁剪 1 个 (PARTIAL) | 排除 4 个 (EXCLUDE)

---

## 1. 总体审计结论 (Executive Summary)

本工程针对原 CUMCM 生产 Agent 体系中的 19 个 Skill 进行了逐行代码与 Prompt 审查。根据数学建模竞赛（CUMCM/MCM/ICM）的真实全生命周期工作流，去粗取精，将真正具备数学抽象、机理建模、数值优化、统计检验、专业图表与规范写作能力的核心组件提炼重构，剥离通用软件工程与不可控的外部依赖。

| 裁决状态 | 数量 | 技能清单 |
| :--- | :---: | :--- |
| **KEEP (完全保留)** | 14 | `problem-analyzer`, `data-processing`, `model-selection`, `mle-solver`, `model-validation`, `scipilot-figure-cumcm`, `scipilot-figure-skill`, `matlab-figure`, `cumcm-academic-flowchart`, `mcm-paper-writing`, `reference-manager`, `paper-review`, `winning-paper-analysis`, `modeling-workflow-orchestrator` |
| **PARTIAL (部分裁剪保留)** | 1 | `systematic-debugging` (深度保留物理/计量反模式与求解发散自愈，剔除通用软件 Git/Docker 运维) |
| **EXCLUDE (剔除排除)** | 4 | `documents`, `pdf`, `spreadsheets`, `paper-search` |

---

## 2. 全量审计明细表 (Full Audit Table)

| Skill | Category | Verdict | Core Function | Modeling Stage | Dependencies | Reason |
| :--- | :--- | :---: | :--- | :--- | :--- | :--- |
| `problem-analyzer` | `01-problem-understanding` | **KEEP** | 赛题形式化分解，抽取数学结构、物理实体、变量单位、目标函数、硬软约束与边界条件，生成可执行的问题依赖图与断言集 | Stage S1 (赛题理解与任务分解) | None | 数学建模竞赛的起点门禁，决定后续所有数学抽象与数据准备的方向，纯粹服务于数模工作流。 |
| `data-processing` | `02-data-analysis` | **KEEP** | 赛题多源数据解析、缺失值与异常值检测、时序与空间特征工程、PCA降维、平滑滤波与无数据穿越（leakage-safe）预处理 | Stage S2A (数据预处理与特征工程) | problem-analyzer | 直接对接 S1 问题结构，提供符合数模规范的数据画像与清洗流程，属于核心数模能力。 |
| `model-selection` | `03-model-formulation` | **KEEP** | 基于数学结构构建基线/主选/备选模型组合，执行反套路门禁（Anti-template gate），评估参数可识别性与求解器可行性 | Stage S2B (模型方案遴选与架构设计) | problem-analyzer, data-processing | 严格杜绝关键词机械套用模型，基于赛题机理构建多层次模型组合，是高水平获奖论文的核心方法论。 |
| `mle-solver` | `04-algorithms-and-solving` | **KEEP** | 数学模型方程映射、变量与约束组装、求解器配置（LP/MILP/ODE/PDE/图论）与启发式优化算法（GA/PSO/SA）执行 | Stage S3 (模型建立与数值求解) | model-selection | 负责将数学抽象转化为可执行代码与计算结果，内置完整的启发式优化算法实现，是模型求解的中枢。 |
| `systematic-debugging` | `04-algorithms-and-solving` | **PARTIAL** | 数模专属故障自愈：物理合理性失真检测、量纲不一致排查、数值不收敛诊断、经济计量反模式拦截与硬断言失败自愈 | Stage S3-dbg (求解异常与数值自愈) | mle-solver, model-validation | 裁剪剥离通用软件 Git/Docker/Web 报错，深度保留针对数学建模的物理与计量反模式库、数值发散根因诊断流程。 |
| `model-validation` | `05-validation` | **KEEP** | 独立模型放行门禁：预注册验证计划、基线超越性检验、参数灵敏度分析、鲁棒性压力测试、扰动分析与误差包络评估 | Stage S4 (独立模型检验与灵敏度分析) | mle-solver | 数模论文拿高奖的关键关卡，确保结论不仅有解，而且解具备稳定性、误差界与优于朴素基准的科学证据。 |
| `cumcm-academic-flowchart` | `06-visualization` | **KEEP** | 竞赛级技术路线图与方法架构图引擎：支持双流布局、泳道分解、循环机理与 draw.io / 原生 SVG / 高清 PNG 矢量生成 | Stage S5B (学术技术路线与架构图生成) | model-validation, problem-analyzer | 国内顶尖数模论文标志性的方法架构图生成引擎，含 60+ 专用渲染脚本与精美模版，极大提升论文专业度。 |
| `scipilot-figure-cumcm` | `06-visualization` | **KEEP** | 数模竞赛论证图表规划器：将核心结论与证据映射为高质量图型，严禁无效凑数图，控制篇幅信息增益与审阅抓手 | Stage S5A (竞赛结论数据图表规划) | model-validation | 专门负责从“结论-证据-图型”映射竞赛图表，杜绝双轴误导、彩虹色谱等低级错误，规范竞赛图表产出。 |
| `scipilot-figure-skill` | `06-visualization` | **KEEP** | 出版级科研绘图引擎：Matplotlib/Seaborn 专业样式库、色盲安全调色板、中文字体排版、多子图编排与矢量导出质量校验 | Stage S5A (科研图表渲染与视觉自检) | scipilot-figure-cumcm | 提供真正可运行的 Python 绘图辅助脚本（check_figure, export_figure, layout_tools 等），支撑 S5A 渲染。 |
| `matlab-figure` | `06-visualization` | **KEEP** | MATLAB 原生图表生成：3D 三维曲面 (surf/mesh)、矢量场流向 (quiver)、Parula 科学色标与系统动力学仿真可视化 | Stage S5A (MATLAB 原生高阶图表) | mle-solver | 数模竞赛中不可或缺的 MATLAB 原生图表规范，用于处理特定空间几何、偏微分方程解曲面及矢量场。 |
| `mcm-paper-writing` | `07-writing` | **KEEP** | 纯 Markdown 论文写作流水线：页码预算分配、Word 原生 OMML 数学公式规范、三线表排版、匿名合规审计与 Word 原生生成器 | Stage S6 (规范化竞赛论文写作与排版) | scipilot-figure-cumcm, cumcm-academic-flowchart, model-validation | 彻底弃用脆弱的 LaTeX 编译依赖，采用标准 Markdown + Word 原生 OMML 架构，内置完善的校验脚本与排版工具。 |
| `reference-manager` | `07-writing` | **KEEP** | 参考文献标准化与双向引用核验：GB/T 7714 / APA 格式规范化、DOI 与学术元数据在线校验、文中 [n] 引用一致性审查 | Stage PH2 (参考文献治理与学术规范) | mcm-paper-writing | 严禁捏造伪造文献，保证文中引用标号与文末清单 100% 双向闭环，保障数模竞赛学术严谨性。 |
| `paper-review` | `08-quality-assurance` | **KEEP** | 论文终稿全方位审查：数值宏前后溯源一致性、公式符号未定义扫描、假设与结论契合度审计、匿名合规检查与提交就绪裁决 | Stage S7 (终审评阅与质量门禁) | mcm-paper-writing, reference-manager | 竞赛提交前最后的安全门禁，确保数据指标与正文计算毫厘不差，彻底规避形式违规与低级笔误。 |
| `winning-paper-analysis` | `08-quality-assurance` | **KEEP** | 国奖优秀论文特征库对标：摘要黄金结构、正文篇幅密度分布、图表出现频次与放置策略、高分论述表达范式对比 | Stage Benchmark (优秀论文对标与基准比对) | problem-analyzer | 提供历年国奖特等奖论文的量化指标与结构对标，为写作规划与最终审阅提供经验基准。 |
| `modeling-workflow-orchestrator` | `09-orchestration` | **KEEP** | 全流程状态机编排引擎：工件有向无环图（Artifact DAG）、状态跃迁控制、上游修改级联失效机制与审阅回退路由 | Stage S0 (全流程生命周期状态机协调) | None | 整套 Toolkit 的调度中枢，将 15 个独立 Skill 通过严格的工件输入输出契约串联为工业级数模流水线。 |
| `documents` | `external-or-generic` | **EXCLUDE** | Document Editing Tool (Generic) | Excluded | N/A | 通用 Anthropic 容器 docx 工具，依赖 @oai/artifact-tool 与 Google Docs MCP，非数学建模专有，已被 mcm-paper-writing 内置的 cumcm_word_generator.py 替代。 |
| `pdf` | `external-or-generic` | **EXCLUDE** | PDF / AcroForms Utility (Generic) | Excluded | N/A | 通用容器 PDF 渲染与交互表单工具，不包含数学建模方法论与算法，属于通用系统外设插件。 |
| `spreadsheets` | `external-or-generic` | **EXCLUDE** | Spreadsheets / Google Sheets Utility (Generic) | Excluded | N/A | 通用财务与商业表格编辑工具，数学建模竞赛中的数据清洗与探索已由 data-processing (pandas/scipy/numpy) 完整覆盖。 |
| `paper-search` | `external-or-generic` | **EXCLUDE** | Academic Literature Search Scraper (Generic) | Excluded | N/A | 通用计算机学术会议 (NeurIPS/ICLR/ICML) 爬虫，对外部 API 存在强依赖且易受反爬影响，非数模本地封闭式解题的核心能力。 |

---

## 3. 剔除项深度剖析 (Exclusion Justifications)

### 3.1 `documents`
- **属性**：通用 Anthropic 容器文档编辑组件。
- **原因**：依赖 `@oai/artifact-tool` Node.js 运行时与 Google Docs MCP 插件，并非针对数学建模竞赛。数学建模论文的排版与格式要求极其严格，Toolkit 已在 `mcm-paper-writing` 中原生集成了轻量级、无外部依赖的 `cumcm_word_generator.py`（基于 python-docx + OMML 原生公式支持），完全覆盖论文排版需求。

### 3.2 `pdf`
- **属性**：通用 PDF 交互与 AcroForms 表单填充插件。
- **原因**：用于容器内可视化渲染与 PDF 表单修改，不包含任何数学建模方法论与算法。论文的 PDF 生成由标准的 Word 导出或 headless 渲染工具承载，无需携带臃肿的通用 PDF 运维工具。

### 3.3 `spreadsheets`
- **属性**：通用财务/医疗/商业表格处理组件。
- **原因**：依赖 `@oai/artifact-tool` 与复杂商业模型模板，非数模科研数据分析规范。数模中的结构化数据探索、缺失值插补、特征衍生均由 `data-processing` 基于 Python 科学计算生态（NumPy/SciPy/Pandas）高精度执行。

### 3.4 `paper-search`
- **属性**：通用学术论文爬虫（NeurIPS/ICLR/arXiv/OpenAlex）。
- **原因**：依赖大量外部在线 API 与网络环境，易受反爬与网络隔离影响；数模竞赛通常要求在封闭或指定网络环境下进行独立推导与求解，不应将外部爬虫作为核心建模依赖。

---

## 4. 裁剪项说明 (PARTIAL Modifications)

### `systematic-debugging`
- **保留核心**：
  - 数学建模专属根因分析流程（四阶段排查法则）；
  - 物理合理性检查告警与量纲一致性断言排查；
  - 经济计量反模式库（虚假回归、共线性遮蔽、内生性疏忽）；
  - 数值求解不收敛与遗传/退火算法早停自愈；
  - mle-solver 硬断言失败自愈回路。
- **裁剪剥离**：
  - Git diff / commit 历史追溯、通用软件构建失败、Web 容器服务异常等通用软件工程运维指令。
