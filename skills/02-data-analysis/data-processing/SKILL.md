---
name: data-processing
title: Competition Data Processing & Feature Engineering
category: data-analysis
stage: S2A
description: "赛题多源数据解析、缺失值与异常值检测、时序与空间特征工程、PCA降维、平滑滤波与无数据穿越（leakage-safe）预处理"
inputs: ["problem_structure.json", "raw_data_files (.csv/.xlsx/.txt/.mat)"]
outputs: ["preprocessing_manifest.json", "data_dictionary.json", "preprocessing_report.md", "clean_data/"]
dependencies: ["problem-analyzer"]
---

## Codex execution contract

- **Language:** Match the requested deliverable language. Default CUMCM narrative to `zh-CN` and MCM/ICM narrative to `en-US`. Preserve official terms, source text, symbols, units, column names, schema keys, paths, and code identifiers.
- **Inspect first:** Validate local inputs, upstream manifests, field meanings, units, hashes, and existing artifacts before selecting operations.
- **Progressive disclosure:** Keep detailed Chinese domain rules in `references/`; load only the files required for the active data domain.
- **Run, do not simulate:** Execute preprocessing and checks. Never report sample output or unexecuted code as a real result.
- **Evidence and privacy:** Keep every transformation traceable; do not send competition data or credentials to third-party APIs without explicit authorization.
- **Handoff:** Use `pipeline_manifest.json` as the S0–S7 interface; on first use read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json). Record inputs, outputs, parameters, seeds, warnings, provenance, and validation status.
- **Failure routing:** Stop propagation on missing or contradictory upstream evidence and return the defect to the responsible skill.
- **Completion:** Mark S2 complete only when outputs exist, checks ran, and downstream values can be recomputed.

# Data Processing — 数学建模数据预处理

负责 S2：读取、剖析、清洗、转换和验证多源数据，输出可供建模、验证、绘图和论文引用的可追溯数据集与报告。

## 核心流程

1. 读取 S1 的问题类型、变量语义、单位、硬断言和预期范围。
2. 识别文件格式、编码、字段类型、主键、时间索引、单位和缺失机制。
3. 先划分训练/验证/测试集，再拟合插补、缩放、特征选择或重采样器，防止数据泄漏。
4. 执行通用清洗，并按数据域加载对应 reference。
5. 用硬断言、范围、量纲和业务约束复查处理结果。
6. 保存原始数据指纹、处理代码、参数、处理后数据、字段字典和 Markdown 报告。

## 按需读取

- 物理约束、经济时序和不平衡分类：读 [references/quality-and-tabular.md](references/quality-and-tabular.md)。
- 图像、高维特征和信号：读 [references/multimodal-and-signal.md](references/multimodal-and-signal.md)。
- API 用法、格式、缺失值、异常值、归一化与硬规则：读 [references/operations-and-rules.md](references/operations-and-rules.md)。
- 更深入的数据处理方法：按任务需要读 [references/advanced_data_processing.md](references/advanced_data_processing.md)。

## 必需产物

- `processed_data.*`：处理后数据。
- `data_dictionary.json`：字段、类型、单位与含义。
- `preprocessing_report.md`：质量问题、操作、参数、样本变化和约束验证。
- `preprocessing_manifest.json`：输入哈希、随机种子、拟合范围和产物路径。

## 完成门禁

- 训练外数据未参与拟合预处理器；处理前后样本数和字段变化可解释。
- 不静默删除异常；区分测量错误、真实极值和结构突变。
- 时间序列保持时间顺序，经济数据完成平稳性/季节性检查。
- 所有下游数字可从处理后文件或报告复算。
