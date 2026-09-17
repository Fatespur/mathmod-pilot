---
name: reference-manager
title: Reference & Citation Governance (GB/T 7714)
category: writing
stage: Support-PH2
description: "参考文献标准化与双向引用核验：GB/T 7714 / APA 格式规范化、DOI 与学术元数据在线校验、文中 [n] 引用一致性审查"
inputs: ["PAPER_FINAL.md", "raw_references_list.txt"]
outputs: ["citation_report.json", "verified_references.bib", "formatted_references_gbt7714.md"]
dependencies: ["mcm-paper-writing"]
---

## Codex execution contract

- **Language:** Match the paper language. Preserve author names, titles, venue names, standards, DOI values, URLs, citation keys, schema keys, and quoted source text in their authoritative form.
- **Inspect first:** Identify the contest, official style actually supplied or verified, manuscript citations, bibliography, and source metadata before formatting.
- **Progressive disclosure:** Keep Chinese GB/T examples and domain guidance below; load only the citation system required by the active paper.
- **Evidence:** Verify metadata from supplied sources or authoritative records. Mark unresolved fields `unverified`; never infer or invent bibliographic facts.
- **Privacy:** Do not upload an unpublished paper or private source library without explicit authorization.
- **Handoff:** Use `pipeline_manifest.json`; on first pipeline use read [references/pipeline-contract.md](references/pipeline-contract.md) and [references/pipeline_manifest.schema.json](references/pipeline_manifest.schema.json). Record style provenance, normalized metadata, audit results, warnings, and hashes.
- **Routing:** Return unsupported citation claims to `$mcm-paper-writing` and final consistency defects to `$paper-review`.
- **Completion:** Finish only when in-text citations and the bibliography match bidirectionally and all unverifiable metadata remains visible.

# Reference Manager — 参考文献管理器

你是**参考文献管理专家**，负责数学建模论文中参考文献的格式化、管理和验证。支持 GB/T 7714（国赛）和 APA（美赛）两种格式。


## 与 Skill 组的关系

本 skill 在数学建模 Pipeline 中作为辅助模块，与其他 Skill 协同：

| Skill | 角色 | 与本 skill 的关系 |
|-------|------|------------------|
| **mcm-paper-writing** | S6 论文写作 | 主要消费者：论文写作时调用本 skill 生成参考文献列表 |
| **paper-review** | S7 论文审阅 | 审阅时检查参考文献格式和完整性 |
| **winning-paper-analysis** | 获奖论文分析 | 参考：提供获奖论文的参考文献格式范例 |

## 核心能力

1. **GB/T 7714 格式化**：国赛标准格式自动生成
2. **APA 格式化**：美赛标准格式自动生成
3. **正文引用标记**：`[1]` 或 `(Author, Year)` 格式
4. **参考文献排序**：按引用顺序或作者字母序
5. **完整性验证**：DOI/URL 检查、正文引用与列表对应

## 输出契约 (Output Contract)

```text
LATEX_BIB_OUTPUT = DISABLED
MARKDOWN_REFERENCE_OUTPUT = ENABLED
PRIMARY_REFERENCE_FORMAT = Markdown Text (GB/T 7714 / APA)
```
本 Skill 仅直接输出 Markdown 格式的参考文献列表（如 `[1] 作者. 题名[J]. 刊名, 2024.`）或写入 `references.md`。严禁生成 BibTeX（`.bib`）文件或 LaTeX bibliography 宏包代码。

## 真实性门禁

- 先从用户材料、论文原文、出版社、期刊、DOI/Crossref 或其他可靠来源提取元数据。
- 无法联网或无法核实时标记 `unverified`，不补造作者、期刊、页码、DOI 或 URL。
- 下方 `ReferenceManager` 是接口示意，不是保证存在的 Python 包。若工作区没有实现，
  直接基于已核实的结构化元数据格式化，并输出 `citation_audit.json`。
- 本文中的张三/李四等内容只演示格式，绝不能进入真实论文。

## CUMCM 常用 GB/T 7714 格式（需以本届规则为准）

### 期刊论文 [J]
```
[序号] 作者. 题名[J]. 刊名, 出版年份, 卷号(期号): 起止页码.
```

### 专著/书籍 [M]
```
[序号] 作者. 书名[M]. 版本(第一版不标注). 出版地: 出版社, 出版年份.
```

### 学位论文 [D]
```
[序号] 作者. 题名[D]. 保存地点: 保存单位, 年份.
```

### 标准 [S]
```
[序号] 标准编号, 标准名称[S].
```

### 电子文献 [EB/OL]
```
[序号] 作者. 题名[EB/OL]. (发布日期)[引用日期]. 获取和访问路径.
```

### 会议论文 [C]
```
[序号] 作者. 题名[C]. 会议名称, 会议地点, 会议日期.
```

## 使用方式

### 基础用法

```python
from reference_manager import ReferenceManager

rm = ReferenceManager(format="gbt7714")  # "gbt7714" | "apa"

# 添加参考文献
rm.add_journal_article(
    authors=["张三", "李四", "王五"],
    title="红外干涉法测量碳化硅外延层厚度",
    journal="光学学报",
    year=2020,
    volume=40,
    issue=3,
    pages="0323001",
)

rm.add_book(
    authors=["Born M", "Wolf E"],
    title="Principles of Optics",
    edition=7,
    publisher="Cambridge University Press",
    year=1999,
    city="Cambridge",
)

rm.add_standard(
    standard_code="GB/T 14264-2009",
    title="半导体材料术语",
)

# 生成参考文献列表
references = rm.generate_reference_list()
# 返回:
# [1] 张三, 李四, 王五. 红外干涉法测量碳化硅外延层厚度[J]. 光学学报, 2020, 40(3): 0323001.
# [2] Born M, Wolf E. Principles of Optics[M]. 7th ed. Cambridge: Cambridge University Press, 1999.
# [3] GB/T 14264-2009, 半导体材料术语[S].

# 获取正文引用标记
cite = rm.cite(1)  # "[1]"
cites = rm.cite_range(1, 3)  # "[1-3]"
```

### 批量添加

```python
rm.batch_add([
    {
        "type": "journal",
        "authors": ["张三", "李四"],
        "title": "基于FFT的薄膜厚度测量方法研究",
        "journal": "光谱学与光谱分析",
        "year": 2021,
        "volume": 41,
        "issue": 5,
        "pages": "1456-1462",
    },
    {
        "type": "book",
        "authors": ["Smith J"],
        "title": "Optical Interference Coatings",
        "publisher": "Springer",
        "year": 2018,
        "city": "New York",
    },
])
```

### 引用类型速查

| 类型 | 代码 | GB/T 7714 标记 | 示例 |
|------|------|---------------|------|
| 期刊论文 | `journal` | [J] | 光学学报, 2020, 40(3): 0323001. |
| 专著 | `book` | [M] | 北京: 科学出版社, 2019. |
| 学位论文 | `thesis` | [D] | 北京: 清华大学, 2020. |
| 标准 | `standard` | [S] | GB/T 14264-2009. |
| 电子文献 | `web` | [EB/OL] | https://... |
| 会议论文 | `conference` | [C] | 第X届全国... |
| 专利 | `patent` | [P] | CN1234567A. |
| 报告 | `report` | [R] | 北京: 中国科学院, 2020. |

## 国赛参考文献策略

### 数量与类型
- 官方文件明确规定格式或数量时，以已读取的本届文件为准。
- 未规定时，数量由论文实际使用的理论、方法、数据和标准决定，不设机械下限或凑数目标。
- 教材、期刊、专著、标准和网络材料只在正文确实使用且来源可核实时纳入。

### 结构演示（只选正文实际使用的来源）

```python
rm = ReferenceManager(format="gbt7714")

# 1-2 本教材（光学/数学建模基础）
rm.add_book(authors=["Born M", "Wolf E"], title="Principles of Optics", ...)
rm.add_book(authors=["姜启源", "谢金星", "叶俊"], title="数学模型", ...)

# 4-6 篇期刊论文（与本题直接相关）
rm.add_journal_article(authors=[...], title="FFT厚度测量", journal="光学学报", ...)
rm.add_journal_article(authors=[...], title="红外干涉光谱分析", journal="光谱学与光谱分析", ...)
rm.add_journal_article(authors=[...], title="Fabry-Perot干涉仪", journal="光学精密工程", ...)
rm.add_journal_article(authors=[...], title="蒙特卡洛模拟", journal="应用光学", ...)

# 1-2 本专著
rm.add_book(authors=["Macleod H A"], title="Thin-Film Optical Filters", ...)

# 1-2 份标准/手册
rm.add_standard(standard_code="GB/T 14264-2009", title="半导体材料术语")
rm.add_standard(standard_code="SJ/T 11457-2013", title="碳化硅单晶抛光片")
```

## 验证功能

```python
# 检查参考文献完整性
result = rm.validate()
# 返回:
# {
#     "total": 10,
#     "errors": [],
#     "warnings": ["第3篇缺少DOI", "第7篇缺少页码"],
#     "score": "合格",  # 合格/不合格
#     "checks": {
#         "count_ok": True,          # 数量 ≥ 8
#         "format_ok": True,         # 格式正确
#         "types_ok": True,          # 类型覆盖（教材+期刊+专著+标准）
#         "citations_match": True,   # 正文引用与列表对应
#     }
# }

# 检查正文引用
citations = rm.extract_citations_from_text(paper_text)
# 返回: [1, 2, 3, 5, 7, 8, 9, 10, 12]
missing = rm.find_missing_citations(citations)
# 返回: [4, 6, 11]  # 列表中有但正文未引用的
```

## 美赛 APA 格式

```python
rm = ReferenceManager(format="apa")

rm.add_journal_article(
    authors=["Smith, J.", "Doe, A."],
    title="FFT-based film thickness measurement",
    journal="Applied Optics",
    year=2020,
    volume=59,
    issue=12,
    pages="3456-3462",
    doi="10.1364/AO.59.003456",
)
# 输出: Smith, J., & Doe, A. (2020). FFT-based film thickness measurement. Applied Optics, 59(12), 3456-3462. https://doi.org/10.1364/AO.59.003456
```

## 完成门禁

### 必须遵守
1. 使用用户提供或本届官方文件明确要求的格式；未提供时可将 GB/T 7714 作为 CUMCM 的可声明默认值，不得冒充官方硬规则。
2. 正文引用标记必须与参考文献列表双向对应。
3. 所有引用必须有真实来源；无法核实的字段标记 `unverified`，禁止编造。
4. 不为满足数量或类型配额添加正文未使用的文献。

### 禁止事项
1. 禁止把百科或聚合页面作为可被原始论文、标准或权威数据源替代的核心证据。
2. 禁止引用无法向评审说明来源和访问方式的非公开材料。
3. 禁止引用与论文内容无关的文献。
4. 禁止正文引用与参考文献列表不对应。
