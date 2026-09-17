# 开源许可证与知识产权审查报告 (License & IP Review)

> 审查对象: `./`
> 审查结论: **ALL CLEAN — 合格允许采用 MIT License 发布**

---

## 1. 资产来源审查 (Origin of Assets)

1. **原创提示词与方法论规范** (`SKILL.md`, `references/`)：
   - 包含的建模阶段状态机规范、反套路门禁、宏变量校验契约、评审标准与篇幅分配模型，全部属于项目作者原创或竞赛公共学术规范的系统化总结。
2. **原创执行脚本** (`scripts/`)：
   - `cumcm-academic-flowchart`: 独立的流程图生成引擎（draw.io XML 组装、SVG 生成、颜色引擎），内部无第三方专有代码复制。
   - `mle-solver/extensions/heuristic_algorithms.py`: 基于 NumPy 的纯自主实现（遗传算法 GA、粒子群 PSO、模拟退火 SA）。
   - `mcm-paper-writing/scripts`: 原创的 CUMCM 格式校验器、OMML 公式兼容性检测器、数值宏一致性校验器。
   - `scipilot-figure-skill/scripts`: 基于标准 Matplotlib / Seaborn 的学术样式库与校验脚本。
3. **第三方依赖库审查**：
   - 依赖项全部为标准开源科学计算栈（NumPy, SciPy, Pandas, Matplotlib, Seaborn, NetworkX, python-docx, jsonschema 等），均为宽松开源许可证（BSD / MIT / Apache 2.0）。
   - 无任何 GPL / AGPL 强传染性开源软件代码。
   - 未引入任何未经授权的专有大模型 SDK 或私有闭源二进制文件。

---

## 2. 敏感信息与隐私清理审查 (Privacy & Secrets)

- [x] **API Key / Token / Secret**: 已执行全仓自动化正则表达式扫描，未发现任何暴露的硬编码 API Key（如 `sk-...`）。
- [x] **个人隐私路径**: 消除所有如 `[HOST_WORKSPACE_PATH]` 与 `[HOST_USER_PATH]` 等私有宿主机硬编码绝对路径，全部改造成统一的相对路径与 CLI 参数支持。
- [x] **竞赛题目私有数据**: 杜绝将真实队伍的赛题敏感原始实验数据与竞赛过程文件打包入库，样例全部基于泛化数据或微型标准问题构建。

---

## 3. 开源授权建议

鉴于仓库中全部代码、文档、规范与配置均属于原创或遵循宽松开源协议，推荐以 **MIT License** 形式在 GitHub 独立公开发布。
