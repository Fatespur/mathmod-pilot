#!/usr/bin/env python3
"""Audit CUMCM Markdown paper artifacts (paper.md) and emit Chinese validation reports.

Replaces legacy LaTeX/DOCX format validator with native Markdown validator:
- Validates heading hierarchy (# -> ## -> ###) and detects duplicate headings
- Enforces strict CUMCM rule: NO table of contents (# 目录 or [TOC])
- Audits Markdown math integrity (balanced $ and $$, valid math blocks)
- Audits local figure references existence and flags potentially missing interpretations without sentence quotas
- Audits Markdown table syntax (|---|) and interpretation in prose
- Audits bidirectional reference citations ([1], [2]...)
- Scans text for anonymity violations (email, phone, student/school names, local paths)
- Audits content depth and underwriting anomalies
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Any


EMAIL_RE = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I)
PHONE_RE = re.compile(r"(?<!\d)(?:\+?86[- ]?)?1[3-9]\d{9}(?!\d)")
WINDOWS_HOME_RE = re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.I)
UNIX_HOME_RE = re.compile(r"/(?:Users|home)/[^/\s]+", re.I)


@dataclass
class Check:
    id: str
    category: str
    status: str  # PASS, WARNING, FAIL
    message_zh: str
    evidence: list[str]
    rule_class: str
    rule_source: str = "CUMCM 2026 Markdown Standard"
    automatic: bool = True
    manual_action: str | None = None


def count_chinese_characters(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def audit_markdown_paper(
    md_path: Path,
    identity_terms: list[str] | None = None,
    min_body_chars: int = 12000,
) -> tuple[list[Check], dict[str, Any]]:
    checks: list[Check] = []
    identity_terms = identity_terms or []

    if not md_path.is_file():
        checks.append(Check(
            id="FILE-EXISTENCE",
            category="文件",
            status="FAIL",
            message_zh="paper.md 文件不存在",
            evidence=[str(md_path)],
            rule_class="OFFICIAL-MANDATORY"
        ))
        return checks, {}

    md_text = md_path.read_text(encoding="utf-8", errors="replace")
    base_dir = md_path.parent
    lines = md_text.splitlines()

    evidence: dict[str, Any] = {
        "file": str(md_path),
        "total_chars": count_chinese_characters(md_text),
        "headings": [],
        "figures": [],
        "tables": [],
        "citations": {},
        "identity_findings": []
    }

    # 1. STRUCT-NO-TOC: Strictly forbid Table of Contents
    toc_found = re.search(r"(?:^|\n)\s*#*\s*目\s*录\s*(?:$|\n)|\[toc\]", md_text, re.I) is not None
    checks.append(Check(
        id="STRUCT-NO-TOC",
        category="结构",
        status="FAIL" if toc_found else "PASS",
        message_zh="检测到目录标题或 [TOC] 标记，严重违反国赛规则！" if toc_found else "未检测到目录，符合不设目录的国赛硬性规范。",
        evidence=[re.findall(r"(?:^|\n)\s*#*\s*目\s*录.*", md_text, re.I)[0].strip()] if toc_found else [],
        rule_class="OFFICIAL-MANDATORY"
    ))

    # 2. STRUCT-HEADING-HIERARCHY: Heading level jumps & duplicate headings
    heading_re = re.compile(r"^(#{1,4})\s+(.+)$")
    headings: list[tuple[int, str]] = []
    duplicate_headings: list[str] = []
    seen_headings = set()
    irregular_jumps = []
    prev_level = 0

    for lno, line in enumerate(lines, 1):
        m = heading_re.match(line)
        if m:
            level = len(m.group(1))
            title = m.group(2).strip()
            headings.append((level, title))
            if title in seen_headings and level <= 2:
                duplicate_headings.append(f"L{lno}: {title}")
            seen_headings.add(title)

            if prev_level > 0 and level > prev_level + 1:
                irregular_jumps.append(f"跳级标题: 从 H{prev_level} 跳至 H{level} ({title})")
            prev_level = level

    evidence["headings"] = [{"level": lvl, "title": t} for lvl, t in headings]

    has_h1 = any(lvl == 1 for lvl, _ in headings)
    checks.append(Check(
        id="STRUCT-HEADING-HIERARCHY",
        category="结构",
        status="FAIL" if not has_h1 or irregular_jumps or duplicate_headings else "PASS",
        message_zh="标题层级规范，无异常跳级或重复大标题。" if has_h1 and not irregular_jumps and not duplicate_headings else f"标题层级存在异常: 跳级={len(irregular_jumps)}, 重复={len(duplicate_headings)}",
        evidence=irregular_jumps + duplicate_headings,
        rule_class="RECOMMENDED-DEFAULT"
    ))

    # 3. CONTENT-EMPTY-SECTIONS
    empty_sections = []
    curr_h = None
    curr_level = 0
    curr_text: list[str] = []
    for line in lines:
        m = heading_re.match(line)
        if m:
            if curr_h and count_chinese_characters("\n".join(curr_text)) < 15:
                # Level 1 is paper title, or preamble, skip if followed by H2
                if curr_level > 1 and "参考文献" not in curr_h and "附录" not in curr_h:
                    empty_sections.append(curr_h)
            curr_h = m.group(2).strip()
            curr_level = len(m.group(1))
            curr_text = []
        else:
            curr_text.append(line)
    if curr_h and curr_level > 1 and count_chinese_characters("\n".join(curr_text)) < 15 and "参考文献" not in curr_h and "附录" not in curr_h:
        empty_sections.append(curr_h)

    checks.append(Check(
        id="CONTENT-EMPTY-SECTIONS",
        category="内容",
        status="FAIL" if empty_sections else "PASS",
        message_zh="所有章节均有实质内容充实。" if not empty_sections else f"存在实质内容严重空虚的章节: {empty_sections}",
        evidence=empty_sections,
        rule_class="OFFICIAL-MANDATORY"
    ))

    # 4. MATH-INTEGRITY: Unclosed math blocks
    no_code = re.sub(r"```[\s\S]*?```", "", md_text)
    double_dollars = no_code.count("$$")
    unclosed_double = (double_dollars % 2 != 0)
    temp = no_code.replace("$$", "")
    single_dollars = 0
    for i, ch in enumerate(temp):
        if ch == "$" and (i == 0 or temp[i - 1] != "\\"):
            single_dollars += 1
    unclosed_single = (single_dollars % 2 != 0)

    math_ok = not unclosed_double and not unclosed_single
    checks.append(Check(
        id="MATH-INTEGRITY",
        category="公式",
        status="PASS" if math_ok else "FAIL",
        message_zh="所有 Markdown 数学公式块（$ 与 $$）均正确闭合。" if math_ok else f"公式语法损坏: $$未闭合={unclosed_double}, $未闭合={unclosed_single}",
        evidence=[f"double_dollars_count={double_dollars}, single_dollars_count={single_dollars}"],
        rule_class="OFFICIAL-MANDATORY"
    ))

    # 5. FIGURE-INTEGRITY & FIGURE-INTERPRETATION
    fig_re = re.compile(r"!\[(.*?)\]\((.*?)\)")
    found_figures = []
    broken_figures = []
    for m in fig_re.finditer(md_text):
        alt = m.group(1).strip()
        p = m.group(2).strip().split()[0]
        found_figures.append((alt, p))
        if not p.startswith("http://") and not p.startswith("https://"):
            resolved = (base_dir / p).resolve()
            if not resolved.is_file():
                broken_figures.append(p)

    evidence["figures"] = [{"alt": alt, "path": p} for alt, p in found_figures]

    checks.append(Check(
        id="FIGURE-LOCAL-EXISTS",
        category="图表",
        status="FAIL" if broken_figures else "PASS",
        message_zh="所有引用的本地插图文件均真实存在。" if not broken_figures else f"存在引用的图片文件丢失或路径错误: {broken_figures}",
        evidence=broken_figures,
        rule_class="OFFICIAL-MANDATORY"
    ))

    fig_nums_in_caption = re.findall(r"图\s*(\d+)", md_text)
    fig_interpretations_missing = []
    for fn in set(fig_nums_in_caption):
        count = len(re.findall(rf"图\s*{fn}\b", md_text))
        if count < 2:
            fig_interpretations_missing.append(f"图 {fn}")

    checks.append(Check(
        id="FIGURE-INTERPRETATION",
        category="图表",
        status="WARNING" if fig_interpretations_missing else "PASS",
        message_zh="插图均在正文中具备关联分析与解读。" if not fig_interpretations_missing else f"部分插图在正文中缺乏解读分析: {fig_interpretations_missing}",
        evidence=fig_interpretations_missing,
        rule_class="RECOMMENDED-DEFAULT",
        manual_action="补充对该图物理特征、坐标含义与拐点趋势的深度解读文字。" if fig_interpretations_missing else None
    ))

    # 6. TABLE-SYNTAX & TABLE-INTERPRETATION
    table_lines = [l for l in lines if l.strip().startswith("|") and l.strip().endswith("|")]
    malformed_tables = []
    for lno, line in enumerate(lines, 1):
        s = line.strip()
        if s.startswith("|") and s.endswith("|") and "-" in s:
            cols = [c.strip() for c in s[1:-1].split("|")]
            if not all(re.match(r"^:?-+:?$", c) for c in cols):
                malformed_tables.append(f"L{lno}: 表格分隔线语法错误: {s}")

    checks.append(Check(
        id="TABLE-SYNTAX",
        category="图表",
        status="FAIL" if malformed_tables else "PASS",
        message_zh="所有 Markdown 表格语法符合规范。" if not malformed_tables else f"表格存在格式语法错误: {malformed_tables}",
        evidence=malformed_tables,
        rule_class="RECOMMENDED-DEFAULT"
    ))

    # 7. CITATION-BIDIRECTIONAL
    ref_idx = next((i for i, l in enumerate(lines) if re.match(r"^#{1,3}\s*.*参考文献", l.strip())), None)
    body_text = "\n".join(lines[:ref_idx]) if ref_idx is not None else md_text
    ref_text = "\n".join(lines[ref_idx:]) if ref_idx is not None else ""

    body_cites = sorted({int(x) for x in re.findall(r"\[(\d+)\]", body_text)})
    ref_entries = sorted({int(x) for x in re.findall(r"^\s*\[(\d+)\]", ref_text, re.MULTILINE)})

    cite_continuous = (ref_entries == list(range(1, len(ref_entries) + 1))) if ref_entries else True
    cite_match = (set(body_cites) == set(ref_entries)) if (body_cites or ref_entries) else True

    checks.append(Check(
        id="CITATION-BIDIRECTIONAL",
        category="引用",
        status="PASS" if cite_match and cite_continuous else "FAIL",
        message_zh="正文引用与参考文献列表双向完全一致且连续连续标号。" if cite_match and cite_continuous else f"文献引用存在缺陷: 正文引用={body_cites}, 文献列表={ref_entries}",
        evidence=[f"body_cites={body_cites}", f"ref_entries={ref_entries}"],
        rule_class="OFFICIAL-MANDATORY"
    ))

    # 8. ANON-TEXT: Anonymity inspection
    findings: list[dict[str, str]] = []
    patterns = [("email", EMAIL_RE), ("phone", PHONE_RE), ("windows_home", WINDOWS_HOME_RE), ("unix_home", UNIX_HOME_RE)]
    for kind, pat in patterns:
        for m in pat.finditer(md_text):
            findings.append({"kind": kind, "value": m.group(0), "classification": "participant_identity"})
    for term in identity_terms:
        if term and term.casefold() in md_text.casefold():
            findings.append({"kind": "provided_term", "value": term, "classification": "participant_identity"})

    evidence["identity_findings"] = findings
    checks.append(Check(
        id="ANON-TEXT",
        category="匿名",
        status="PASS" if not findings else "FAIL",
        message_zh="未在论文正文中检测到个人姓名、联系方式、高校名称或本地路径。" if not findings else f"检测到敏感身份信息泄露: {findings[:5]}",
        evidence=[json.dumps(f, ensure_ascii=False) for f in findings[:10]],
        rule_class="OFFICIAL-MANDATORY"
    ))

    # 9. CONTENT-DEPTH: Underwriting inspection
    body_chars = count_chinese_characters(body_text)
    underwritten = body_chars < min_body_chars
    hard_min = min(6000, min_body_chars)
    checks.append(Check(
        id="CONTENT-DEPTH",
        category="深度",
        status="WARNING" if underwritten else "PASS",
        message_zh=f"正文汉字篇幅充足（共 {body_chars} 字，满足基线目标 {min_body_chars} 字）。" if not underwritten else f"正文篇幅偏少（共 {body_chars} 字，低于基线目标 {min_body_chars} 字），请检查结果四层结构与核心机理是否充分；不得为篇幅添加重复限定或凑句。",
        evidence=[f"body_chars={body_chars}, min_target={min_body_chars}"],
        rule_class="DIAGNOSTIC-ONLY"
    ))

    from formula_compatibility_validator import audit_formula
    formula = audit_formula(md_text)
    evidence['formula_compatibility'] = formula
    for item in formula['findings']:
        checks.append(Check(id=item['code'], category='公式', status=item['status'],
                            message_zh=item['message'], evidence=[],
                            rule_class='FORMULA-COMPATIBILITY'))
    return checks, evidence


def format_validation_markdown(checks: list[Check], evidence: dict[str, Any]) -> str:
    total = len(checks)
    passed = sum(1 for c in checks if c.status == "PASS")
    warnings = sum(1 for c in checks if c.status == "WARNING")
    failed = sum(1 for c in checks if c.status == "FAIL")

    lines = [
        "# CUMCM Markdown 论文合规与质量验证报告",
        "",
        f"**审查状态**: {'PASS' if failed == 0 and warnings == 0 else ('WARNING' if failed == 0 else 'FAIL')}  ",
        f"**核验概况**: 总检查项 {total} 项，通过 {passed} 项，警告 {warnings} 项，违规失败 {failed} 项。  ",
        f"**正文字数**: {evidence.get('total_chars', 0)} 汉字  ",
        "",
        "---",
        "",
        "## 详细核查清单",
        "",
        "| 检查项ID | 类别 | 级别 | 状态 | 审核结论 |",
        "|---|---|---|---|---|"
    ]

    for c in checks:
        icon = "✅" if c.status == "PASS" else ("⚠️" if c.status == "WARNING" else "❌")
        lines.append(f"| `{c.id}` | {c.category} | {c.rule_class} | {icon} {c.status} | {c.message_zh} |")

    if failed > 0:
        lines.extend([
            "",
            "## 需立即阻断与整改项",
            ""
        ])
        for c in checks:
            if c.status == "FAIL":
                lines.append(f"- **[{c.id}] {c.category}**: {c.message_zh}")
                for ev in c.evidence:
                    lines.append(f"  - 证据: `{ev}`")

    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Markdown paper artifact")
    parser.add_argument("markdown_path", type=Path, help="Path to paper.md")
    parser.add_argument("--identities", nargs="*", default=[], help="Identity terms to audit")
    parser.add_argument("--min-chars", type=int, default=12000, help="Minimum body Chinese characters")
    parser.add_argument("--json-out", type=Path, default=None, help="Output JSON report path")
    parser.add_argument("--md-out", type=Path, default=None, help="Output Markdown report path")
    args = parser.parse_args()

    checks, evidence = audit_markdown_paper(args.markdown_path, identity_terms=args.identities, min_body_chars=args.min_chars)
    report_dict = {
        "overall_status": "FAIL" if any(c.status == "FAIL" for c in checks) else ("WARNING" if any(c.status == "WARNING" for c in checks) else "PASS"),
        "checks": [asdict(c) for c in checks],
        "evidence": evidence
    }

    if args.json_out:
        args.json_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(report_dict, f, ensure_ascii=False, indent=2)

    md_report = format_validation_markdown(checks, evidence)
    if args.md_out:
        args.md_out.parent.mkdir(parents=True, exist_ok=True)
        with open(args.md_out, "w", encoding="utf-8") as f:
            f.write(md_report)

    print(f"MARKDOWN_PAPER_AUDIT: {report_dict['overall_status']}")
    for c in checks:
        if c.status != "PASS":
            print(f"  [{c.status}] {c.id}: {c.message_zh}")

    return 1 if any(c.status == "FAIL" for c in checks) else 0


if __name__ == "__main__":
    sys.exit(main())
