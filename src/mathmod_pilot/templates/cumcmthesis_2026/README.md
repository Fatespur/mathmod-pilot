# 2026 年全国大学生数学建模竞赛（CUMCM）标准 LaTeX 论文模板 (cumcmthesis 2026)

本模板专为 **2026 年全国大学生数学建模竞赛（高教社杯）** 制作，基于经典的 `cumcmthesis` 文档类与现代 `ctex` 宏包升级优化。

---

## 1. 核心特性
- **支持 2026 最新年份与竞赛标准**：完整包含 2026 年官方承诺书页、编号专用页、中文摘要与规范三线表；
- **支持双模切换**：
  - `\documentclass{cumcmthesis}`：包含承诺书与编号页（供打印签名或日常排版）；
  - `\documentclass[withoutpreface]{cumcmthesis}`：一键去除承诺书与编号页，直接以论文题目和摘要为第 1 页（**符合电子版提交匿名要求**）；
- **完善宏包预载**：集成 AMS 数学公式、三线表、多子图排版、BibTeX 引用、超链接、代码高亮等。

---

## 2. 推荐编译方式 (XeLaTeX)
推荐使用 **TeX Live** 或 **MiKTeX**，配合 **TeXstudio / VS Code / Cursor** 进行编译：

```bash
xelatex template_2026.tex
bibtex template_2026
xelatex template_2026.tex
xelatex template_2026.tex
```

---

## 3. 文件清单
- `cumcmthesis.cls`：2026 年版文档类核心控制文件；
- `template_2026.tex`：2026 年版论文示范源码；
- `references.bib`：标准 BibTeX 参考文献库；
- `compile_2026.bat`：Windows 一键编译批处理脚本。
