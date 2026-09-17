# CUMCM Modeling Skills Toolkit 架构设计

## 1. 核心设计哲学 (Core Philosophy)

**CUMCM Modeling Skills Toolkit** 是面向全国大学生数学建模竞赛（CUMCM）与美国大学生数学建模竞赛（MCM/ICM）的 Agent 原生技能工具箱。

与传统的“零散提示词收集”或“单一黑盒自动化脚本”不同，本工具箱采用**状态机驱动与工件契约隔离（State Machine & Artifact Contracts）**架构：

```text
┌─────────────────────────────────────────────────────────────┐
│             Stage S0: State Machine Orchestrator            │
│  (State Authority, Artifact Hash Verification, Routing DAG) │
└──────────────────────────────┬──────────────────────────────┘
                               │ Dispatches & Monitors
    ┌──────────────────────────┴──────────────────────────┐
    ▼                                                     ▼
┌─────────────────────────┐               ┌─────────────────────────┐
│     Scientific Layer    │               │    Presentation Layer   │
│  S1 Problem Analyzer    │               │  S5A Scientific Figures │
│  S2A Data Processing    │───────┬──────▶│  S5B Academic Flowchart │
│  S2B Model Selection    │       │       │  S6  Markdown Writing   │
│  S3  MLE / Solver       │       │       │  PH2 Reference Manager  │
│  S3-dbg Debugging       │       │       │  S7  Paper Review       │
│  S4  Model Validation   │       │       └─────────────────────────┘
└─────────────────────────┘       │                    ▲
                                  └────────────────────┘
                                   Strict Artifact Flow
```

## 2. 三大核心支柱 (Three Pillars)

### 2.1 强类型工件契约 (Deterministic Artifact Contracts)
每个 Skill 之间的协作不依赖上下文漫谈，而是通过严格的 JSON Schema 与规范化 Markdown 工件进行交接：
- 上游输出作为下游严格输入；
- 每次工件生成计算 SHA-256 哈希值并签署指纹；
- 上游事实（如机理参数、数据字典）一旦冻结，下游 Skill 无权暗中篡改。

### 2.2 反套路门禁与模型组合 (Anti-Template & Portfolio)
在模型遴选阶段（Stage S2B），强制实行**反套路门禁（Anti-template Gate）**：
- 严禁看到“预测”就直接套用 LSTM/BP 神经网络，严禁看到“评价”就无脑套用层次分析法（AHP）；
- 强制要求建立 **基线模型 (Baseline) + 主选机理模型 (Primary) + 备选对冲模型 (Alternative)** 的投资组合架构；
- 主选模型必须在阶段 S4 中通过统计检验与基线超越性证明，方可放行进入写作阶段。

### 2.3 异常自愈与修订回退 DAG (Revision Feedback DAG)
任何真实比赛中都会遇到求解不收敛、数据缺失或指标反常。Toolkit 内置了闭环反馈有向图：
- `solver_crash` / `implementation_anomaly` -> 自动路由至 `systematic-debugging` 启动根因排查；
- `scientific_validation_revise` -> 验证门禁拦截，回退至 `model-selection` 激活备选方案；
- `numeric_mismatch` -> 终审阶段检测到正文数值与求解结果不符，强制回退校准数值宏。

---

## 3. 分层目录拓扑 (Repository Layout)

工具箱根据数模全生命周期的逻辑，划分为 9 大标准分类：
1. `01-problem-understanding`: 赛题形式化拆解与物理实体抽象
2. `02-data-analysis`: 赛题特征工程与防数据泄露预处理
3. `03-model-formulation`: 机理与数学规划方案遴选
4. `04-algorithms-and-solving`: 启发式与数值求解算法库及故障恢复
5. `05-validation`: 独立模型放行门禁与灵敏度检验
6. `06-visualization`: 出版级数据图表与学术方法架构流程图
7. `07-writing`: 纯 Markdown 结构化论文撰写与参考文献治理
8. `08-quality-assurance`: 终稿一致性审查与国奖基准库对标
9. `09-orchestration`: 全流程状态机调度引擎
