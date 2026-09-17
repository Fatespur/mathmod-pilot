# S0–S7 Pipeline Manifest 契约

## 目的

让 15 个 skill 通过可验证文件协作，而不是依赖同一段对话中的隐式记忆。

## 状态流

`not_started → in_progress → completed`

出现不可恢复输入缺失时使用 `blocked`；执行或校验失败使用 `failed`。只有必需产物存在且质量门禁通过后才能写入 `completed`。

## 读写规则

1. 开始阶段时读取 `pipeline_manifest.json` 并核对 `schema_version=1.0`。
2. 验证所有 `inputs[].path` 存在；有哈希时复算 SHA-256。
3. 只消费状态为 `completed` 的必需上游阶段。
4. 写入产物时记录路径、角色、来源阶段、可选 schema 和 SHA-256。
5. 阻断性 warning 必须返回 `owner_stage` 修复；不得在下游静默忽略。
6. 任何更新保留旧产物，不覆盖无法复算的用户原始数据。

## 阶段所有权

| 阶段 | Owner | 主要产物 |
|---|---|---|
| S0 | `brainstorming` | 目标、范围、成功标准 |
| S1 | `problem-analyzer` | 问题图、变量、约束、方法路由 |
| S2 | `data-processing` | 处理后数据、字段字典、质量报告 |
| S3 | `mle-solver` | 模型、代码、求解结果、日志 |
| S4 | `model-validation` | 验证计划、指标、稳健性和不确定性 |
| S5 | 绘图 skill 组 | 图表计划、源码、数据快照、成图 |
| S6 | `mcm-paper-writing` | 论文、数字报告、引用报告 |
| S7 | `paper-review` | 审阅报告、修订稿、最终门禁 |

## 冲突处理

- 数字冲突：回到数字首次生成的阶段，不在 S6 手工改值。
- 假设冲突：回到 S1 更新风险登记，并重跑受影响阶段。
- 图文冲突：先核对 S3/S4 数据，再重绘 S5，最后更新 S6。
- 引用冲突：交给 `reference-manager`，不以补写虚假 DOI 通过检查。

