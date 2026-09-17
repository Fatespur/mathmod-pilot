---
name: systematic-debugging
title: Model Diagnostic & Anomaly Recovery
category: algorithms-and-solving
stage: S3-dbg
description: "数模专属故障自愈：物理合理性失真检测、量纲不一致排查、数值不收敛诊断、经济计量反模式拦截与硬断言失败自愈"
inputs: ["solver_crash_log", "failed_assertions.json", "unreasonable_physics_metrics"]
outputs: ["debug_report.json", "repaired_model_spec.json", "regression_test_evidence.json"]
dependencies: ["mle-solver", "model-validation"]
---

## Codex execution contract

- **Language:** Explain diagnostics in the user’s language while preserving error text, stack traces, symbols, variable names, schema keys, paths, commands, and code identifiers verbatim.
- **Inspect first:** Read complete errors, recent changes, relevant source, inputs, logs, manifests, and a comparable working pattern before proposing a fix.
- **Progressive disclosure:** Use the domain anti-pattern sections only when evidence points to that model class.
- **Evidence:** Reproduce the failure, trace the bad value, state one falsifiable root-cause hypothesis, and add the smallest failing regression test before editing.
- **Run, do not simulate:** Apply one justified fix and rerun the focused test, hard assertions, and relevant regression suite.
- **Handoff:** When used in the modeling pipeline, read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json); record reproduction, evidence, fix, tests, unresolved warnings, and provenance.
- **Failure routing:** After three failed hypotheses, reassess the architecture instead of stacking patches.
- **Completion:** Finish only when the root cause—not merely the symptom—is removed and no relevant regression remains.


## 与 Skill 组的关系

| Skill | 阶段 | 关系 |
|-------|:----:|------|
| mle-solver | S3 | 触发者：硬断言验证失败、物理合理性检查警告、多方法偏差>20% 时被调用 |
| model-validation | S4 | 触发者：method_agreement 检查失败时被调用 |
| problem-analyzer | S1 | 参考者：对比 S1 的 model_assumptions 与代码实现 |

**职责边界**：本 skill 是故障恢复模块，不参与正常的 Pipeline 流程。仅在 mle-solver 或 model-validation 遇到错误时被触发。
# Systematic Debugging（v4 — 数学建模+经济计量+通用反模式增强版）

## Overview

Random fixes waste time and create new bugs. Quick patches mask underlying issues.

**Core principle:** ALWAYS find root cause before attempting fixes. Symptom fixes are failure.

**Violating the letter of this process is violating the spirit of debugging.**
**v4 增强：** 在v3物理+经济双领域反模式基础上，新增通用反模式库——覆盖所有问题类型都可能犯的6类错误：魔法数字、方法分歧、盲传结果、阈值遮蔽、过度平滑、假设漂移。这些反模式不依赖任何特定领域知识，适用于所有场景。

**v3 增强：** 在v2物理建模反模式基础上，新增经济计量建模反模式库。


## The Iron Law

```
NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST
```

If you haven't completed Phase 1, you cannot propose fixes.

## When to Use

Use for ANY technical issue:
- Test failures
- Bugs in production
- Unexpected behavior
- Performance problems
- Build failures
- Integration issues

**v2 新增：数学建模专属触发条件：**
- 硬断言验证失败（mle-solver 阶段 3.5）
- 物理合理性检查报出警告（mle-solver 阶段 3.6）
- 模型输出违反物理直觉
- 灵敏度分析结果与预期严重不符
- 数值求解不收敛
- 量纲不一致

**Use this ESPECIALLY when:**
- Under time pressure (emergencies make guessing tempting)
- "Just one quick fix" seems obvious
- You've already tried multiple fixes
- Previous fix didn't work
- You don't fully understand the issue

---

## The Four Phases

You MUST complete each phase before proceeding to the next.

### Phase 1: Root Cause Investigation

**BEFORE attempting ANY fix:**

1. **Read Error Messages Carefully**
   - Don't skip past errors or warnings
   - They often contain the exact solution
   - Read stack traces completely
   - Note line numbers, file paths, error codes

2. **Reproduce Consistently**
   - Can you trigger it reliably?
   - What are the exact steps?
   - Does it happen every time?

3. **Check Recent Changes**
   - What changed that could cause this?
   - Git diff, recent commits
   - New dependencies, config changes

4. **v2 新增：数学建模专属根因分析**

   **4a. 物理约束违规分析**
   当硬断言失败时：
   ```
   1. 确认断言表达式是否正确编码了物理约束
   2. 检查数值计算中是否有精度损失（如 1e-15 级别的舍入误差）
   3. 检查是否有数学简化忽略了关键约束（如"以弧代弦"）
   4. 使用 analytical 方法验证数值结果
   ```

   **4b. 量纲一致性检查**
   ```
   1. 逐项检查方程中每个项的量纲
   2. 确认所有物理量使用了正确的单位系统
   3. 检查是否有无量纲化步骤引入了错误
   ```

   **4c. 反模式库匹配（v2 新增）**
   将当前问题与已知反模式库匹配：
   | 反模式 | 症状 | 根因 |
   |--------|------|------|
   | 弧长代替弦长 | 所有速度恒定、碰撞时间偏晚 | 刚体约束被简化为柔性约束 |
   | 连续近似离散 | 边界条件不满足 | 微分方程代替差分方程 |
   | 线性化失效 | 大扰动下结果偏离 | 非线性项被截断 |
   | 单精度溢出 | 迭代不收敛 | float32 精度不足 |
   | 伪回归 | 高R²但DW极低、系数显著但不合理 | 未做ADF检验直接OLS回归 |
   | 内生性忽略 | 系数符号与经济学理论相反 | 遗漏变量/测量误差/联立性 |
   | 名义值混淆 | 增长率异常偏高 | 未使用CPI/GDP平减指数 |
   | 忽略时间价值 | NPV异常大 | 跨期现金流直接加总 |
   | 幸存者偏差 | 成功率/收益率系统性偏高 | 仅保留存活样本 |
   | 异方差忽略 | t值膨胀、显著性虚假 | 残差方差随拟合值变化 |
   | 自相关忽略 | DW≠2、残差ACF显著 | 时间序列残差存在记忆 |
   | 多重共线性 | 系数符号反转、标准误极大 | VIF>10 |
   | 结构突变忽略 | 模型预测在特定时点后失效 | 政策/制度变化 |
   | Granger因果误用 | 声称"X导致Y"但仅做Granger检验 | 混淆预测性与因果性 |

   **4d. 经济计量诊断分析**
   当经济模型结果异常时：
   ```
   1. 检查数据平稳性：ADF检验 → 非平稳则差分或协整
   2. 检查残差诊断：自相关(DW/Ljung-Box) + 异方差(Breusch-Pagan/White) + 正态性(Jarque-Bera)
   3. 检查多重共线性：VIF > 10 → 变量筛选或正则化
   4. 检查内生性：Hausman检验 → 使用IV/2SLS
   5. 检查结构稳定性：Chow检验 → 分段建模或引入虚拟变量
   6. 检查模型设定：Ramsey RESET → 添加非线性项
   ```

5. **Trace Data Flow**
   - Where does bad value originate?
   - What called this with bad value?
   - Keep tracing up until you find the source

### Phase 2: Pattern Analysis

**Find the pattern before fixing:**

1. **Find Working Examples**
   - Locate similar working code in same codebase
   - What works that's similar to what's broken?

2. **Compare Against References**
   - If implementing pattern, read reference implementation COMPLETELY
   - Don't skim - read every line

3. **Identify Differences**
   - What's different between working and broken?
   - List every difference, however small

4. **v2 新增：数学建模专属模式分析**
   - 检查数学简化是否保留了物理约束
   - 对比解析解与数值解的差异
   - 检查是否有已知的数值方法陷阱（如刚性问题用显式方法）

### Phase 3: Hypothesis and Testing

**Scientific method:**

1. **Form Single Hypothesis**
   - State clearly: "I think X is the root cause because Y"
   - Be specific, not vague

2. **Test Minimally**
   - Make the SMALLEST possible change to test hypothesis
   - One variable at a time

3. **Verify Before Continuing**
   - Did it work? Yes → Phase 4
   - Didn't work? Form NEW hypothesis

4. **v2 新增：数学建模假说模板**
   - "我认为根因是 [数学简化/数值方法/物理约束编码] 错误，因为 [具体证据]"
   - 构造最小反例验证假说
   - 用解析解或已知特例交叉验证

### Phase 4: Implementation

**Fix the root cause, not the symptom:**

1. **Create Failing Test Case**
   - Simplest possible reproduction
   - MUST have before fixing

2. **Implement Single Fix**
   - Address the root cause identified
   - ONE change at a time

3. **Verify Fix**
   - Test passes now?
   - No other tests broken?

4. **v2 新增：修复后必须重新运行硬断言验证**
   - 所有硬断言必须通过
   - 物理合理性检查不应产生新的警告

5. **If 3+ Fixes Failed: Question Architecture**
   - Is this pattern fundamentally sound?
   - Should we refactor architecture vs. continue fixing symptoms?

## v2 新增：数学建模反模式库

| 反模式 | 典型症状 | 检测方法 | 修复方向 |
|--------|---------|---------|---------|
| 弧长代替弦长 | 刚体链中所有点速度恒定 | 检查速度方差是否为零 | 使用弦长约束 `|P_i - P_{i-1}| = L` |
| 连续近似离散 | 边界附近误差大 | 检查边界条件残差 | 使用差分方程代替微分方程 |
| 线性化截断 | 大参数时偏离 | 对比完整模型和简化模型 | 保留高阶项或用数值方法 |
| 隐式约束遗漏 | 数值解违反物理直觉 | 逐项审查约束编码 | 补充缺失的约束条件 |
| 单步迭代发散 | 迭代不收敛 | 检查雅可比矩阵条件数 | 使用阻尼牛顿法或信赖域方法 |
| 量纲不一致 | 方程两端单位不同 | 逐项量纲分析 | 检查无量纲化步骤 |
| 对称性破坏 | 对称问题得到非对称解 | 交换输入验证对称性 | 检查初始条件/边界条件对称性 |

## v3 新增：经济建模反模式库

| 反模式 | 典型症状 | 检测方法 | 修复方向 |
|--------|---------|---------|---------|
| 伪回归 | R²>0.9但DW<0.5，系数显著但不合理 | 检查ADF检验是否执行 | 差分后回归或使用ECM |
| 内生性忽略 | 系数符号与理论相反，Hausman显著 | Durbin-Wu-Hausman检验 | 使用IV/2SLS或面板固定效应 |
| 名义值混淆 | 跨年增长率异常偏高 | 检查是否做价格平减 | 使用CPI/GDP平减指数 |
| 忽略时间价值 | NPV/收益评估过于乐观 | 检查是否引入折现率 | 引入折现率参数 |
| 幸存者偏差 | 平均收益率系统性偏高 | 检查样本是否包含失败案例 | 使用Heckman两阶段修正 |
| 异方差忽略 | t值膨胀、F检验不可靠 | Breusch-Pagan/White检验 | 使用HC3稳健标准误或WLS |
| 自相关忽略 | DW≠2、残差ACF显著 | Durbin-Watson/Ljung-Box | Newey-West标准误或Cochrane-Orcutt |
| 多重共线性 | 系数符号反转、标准误极大 | VIF>10 | 变量筛选/Ridge/Lasso/PCA |
| 结构突变 | 预测在特定时点后失效 | Chow检验/Bai-Perron | 分段建模或引入虚拟变量 |
| 过度差分 | 差分后MA项显著，方差增大 | 检查差分前后AIC/BIC | 减少差分阶数或使用分数阶差分 |
| Granger因果误用 | 论文声称因果关系 | 检查措辞是否"导致""决定" | 改为"预测""关联"，明确Granger≠因果 |
| 模型设定错误 | Ramsey RESET显著 | 检查散点图是否非线性 | 添加平方项/交互项或使用非线性模型 |

## v4 新增：通用反模式库（跨领域适用）

以下反模式不依赖任何特定问题类型，在任何代码/建模场景中都可能出现：

| 反模式 | 典型症状 | 检测方法 | 修复方向 |
|--------|---------|---------|----------|
| **魔法数字** | 代码中出现无来源的数值常量 | 扫描所有数值字面量，检查是否有推导注释或S1参数引用 | 替换为从S1上下文推导的表达式 |
| **方法分歧** | 多种方法给出互相矛盾的结果 | 多方法结果偏差 > 20% | 触发根因分析，检查各方法的假设条件和预处理步骤 |
| **盲传结果** | 结果未经验证直接传递给下游 | 检查 Pipeline 阶段间是否有质量标记 | 在阶段间添加 quality_flag 门禁 |
| **阈值遮蔽** | 过滤/截断条件排除真实信号 | 检查过滤后数据量是否 < 过滤前的50% | 使用从物理参数推导的合理范围，而非硬编码阈值 |
| **过度平滑** | 预处理改变了信号/数据的核心特征 | 检查平滑前后关键统计量变化 > 10% | 减小平滑窗口或使用保留特征的预处理方法 |
| **假设漂移** | 代码实现与 S1 的模型假设不一致 | 对比 S1 的 model_assumptions 与代码实际实现 | 修正代码使其与 S1 假设一致，或更新 S1 假设 |

### 反模式检测触发时机

- 在 mle-solver 阶段3执行失败时自动触发
- 在 model-validation 的 method_agreement 检查失败时自动触发
- 在 Pipeline 阶段间数据传递时，检查上一阶段结果是否有验证标记
- 在任何代码生成后，扫描所有数值字面量是否有推导注释

## Quick Reference

| Phase | Key Activities | Success Criteria |
|-------|---------------|------------------|
| **1. Root Cause** | Read errors, reproduce, check changes, **v2: 检查物理约束** | Understand WHAT and WHY |
| **2. Pattern** | Find working examples, compare, **v2: 匹配反模式库** | Identify differences |
| **3. Hypothesis** | Form theory, test minimally | Confirmed or new hypothesis |
| **4. Implementation** | Create test, fix, verify, **v2: 重跑硬断言** | Bug resolved, tests pass |

## Red Flags - STOP and Follow Process

If you catch yourself thinking:
- "Quick fix for now, investigate later"
- "Just try changing X and see if it works"
- "It's probably X, let me fix that"
- "I don't fully understand but this might work"
- **v2 新增："只是数值误差，忽略它"** — 数值误差可能是物理建模错误的信号
- **v2 新增："反正结果看起来合理"** — 看起来合理 ≠ 物理上正确
- **v3 新增："R²这么高，模型肯定没问题"** — 可能是伪回归，检查DW统计量和ADF检验
- **v3 新增："系数都显著，直接用就行"** — 可能有多重共线性或异方差，检查VIF和残差图
- **v3 新增："数据是统计局发布的，直接可以用"** — 名义值vs实际值，跨年数据需要价格平减
- **v4 新增："这个阈值设0.01就行，经验值"** — 魔法数字反模式，必须从问题参数推导
- **v4 新增："三种方法结果不一样，取个平均值吧"** — 方法分歧反模式，必须排查根因
- **v4 新增："结果看起来没问题，传给下一阶段吧"** — 盲传结果反模式，必须经过质量门禁
- **v4 新增："过滤一下噪声，阈值设高点"** — 阈值遮蔽反模式，可能排除真实信号

**ALL of these mean: STOP. Return to Phase 1.**
