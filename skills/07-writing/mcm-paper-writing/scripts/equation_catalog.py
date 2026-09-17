#!/usr/bin/env python3
"""Extract Pandoc-compatible LaTeX and build equation/source mappings."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable


HEADING_RE = re.compile(r"^#{1,6}\s+(?P<title>.+?)\s*$")
LABEL_RE = re.compile(r"\\label\{(?P<label>[^{}]+)\}")
REF_RE = re.compile(r"\\(?:eqref|ref)\{(?P<label>[^{}]+)\}")
INLINE_RE = re.compile(r"(?<!\\)\\\((?P<body>.+?)(?<!\\)\\\)")
BEGIN_RE = re.compile(r"\\begin\{(?P<env>equation\*?)\}")
END_RE = re.compile(r"\\end\{(?P<env>equation\*?)\}")
DISPLAY_OPEN_RE = re.compile(r"(?<!\\)\\\[")
DISPLAY_CLOSE_RE = re.compile(r"(?<!\\)\\\]")

ALLOWED_ENVIRONMENTS = {
    "equation",
    "equation*",
    "aligned",
    "cases",
    "matrix",
    "pmatrix",
    "bmatrix",
    "vmatrix",
}

DISCOURAGED_PATTERNS = {
    r"\\begin\{tikzpicture\}": "TikZ is not a Word-native input environment",
    r"\\includegraphics": "image inclusion is not allowed inside equations",
    r"[＋－＝，。；：]": "full-width punctuation appears in LaTeX",
}


@dataclass
class EquationRecord:
    equation_number: int | None
    label: str | None
    latex: str
    section: str
    paragraph_id: str
    word_location: str
    inline: bool
    display: bool
    referenced_at: list[str]
    conversion_status: str
    source_line_start: int
    source_line_end: int


def _balanced_braces(text: str) -> bool:
    depth = 0
    escaped = False
    for char in text:
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def _environment_issues(latex: str) -> list[str]:
    issues: list[str] = []
    stack: list[str] = []
    for match in re.finditer(r"\\(?P<kind>begin|end)\{(?P<env>[^{}]+)\}", latex):
        kind, env = match.group("kind"), match.group("env")
        if env not in ALLOWED_ENVIRONMENTS:
            issues.append(f"unsupported or unverified environment: {env}")
        if kind == "begin":
            stack.append(env)
        elif not stack or stack.pop() != env:
            issues.append(f"unmatched environment ending: {env}")
    if stack:
        issues.append("unclosed environments: " + ", ".join(stack))
    return issues


def _compatibility_issues(latex: str) -> list[str]:
    issues = _environment_issues(latex)
    if not _balanced_braces(latex):
        issues.append("unbalanced braces")
    for pattern, message in DISCOURAGED_PATTERNS.items():
        if re.search(pattern, latex):
            issues.append(message)
    declared = set(re.findall(r"\\newcommand\s*\{?\\([A-Za-z]+)", latex))
    private = {
        name
        for name in re.findall(r"\\([A-Za-z]+)", latex)
        if name.startswith("my") and name not in declared
    }
    if private:
        issues.append("undeclared private macros: " + ", ".join(sorted(private)))
    return issues


def _collect_reference_locations(lines: list[str]) -> dict[str, list[str]]:
    locations: dict[str, list[str]] = {}
    for number, line in enumerate(lines, 1):
        for match in REF_RE.finditer(line):
            locations.setdefault(match.group("label"), []).append(f"line:{number}")
    return locations


def extract_equations(text: str) -> tuple[list[EquationRecord], list[dict[str, str]]]:
    lines = text.splitlines()
    references = _collect_reference_locations(lines)
    records: list[EquationRecord] = []
    issues: list[dict[str, str]] = []
    section = "未分节"
    number = 0
    index = 0
    i = 0

    while i < len(lines):
        line = lines[i]
        heading = HEADING_RE.match(line)
        if heading:
            section = heading.group("title")

        begin = BEGIN_RE.search(line)
        display_open = DISPLAY_OPEN_RE.search(line)
        if begin:
            env = begin.group("env")
            start = i
            buffer = [line[begin.start() :]]
            while not END_RE.search(buffer[-1]) and i + 1 < len(lines):
                i += 1
                buffer.append(lines[i])
            latex = "\n".join(buffer).strip()
            if not END_RE.search(buffer[-1]):
                issues.append({"severity": "FAIL", "message": "unclosed equation environment", "line": str(start + 1)})
            label_match = LABEL_RE.search(latex)
            label = label_match.group("label") if label_match else None
            numbered = env == "equation"
            if numbered:
                number += 1
            if numbered and not label:
                label = f"eq:auto_{number:03d}"
                issues.append({"severity": "WARNING", "message": f"numbered equation uses generated label {label}", "line": str(start + 1)})
            index += 1
            records.append(
                EquationRecord(
                    equation_number=number if numbered else None,
                    label=label,
                    latex=latex,
                    section=section,
                    paragraph_id=f"eq-{index:04d}",
                    word_location=f"after-source-line-{start + 1}",
                    inline=False,
                    display=True,
                    referenced_at=references.get(label or "", []),
                    conversion_status="native-omml-not-verified",
                    source_line_start=start + 1,
                    source_line_end=i + 1,
                )
            )
        elif display_open:
            start = i
            body = line[display_open.start() :]
            buffer = [body]
            while not DISPLAY_CLOSE_RE.search(buffer[-1]) and i + 1 < len(lines):
                i += 1
                buffer.append(lines[i])
            latex = "\n".join(buffer).strip()
            if not DISPLAY_CLOSE_RE.search(buffer[-1]):
                issues.append({"severity": "FAIL", "message": "unclosed display equation", "line": str(start + 1)})
            index += 1
            records.append(
                EquationRecord(
                    equation_number=None,
                    label=None,
                    latex=latex,
                    section=section,
                    paragraph_id=f"eq-{index:04d}",
                    word_location=f"after-source-line-{start + 1}",
                    inline=False,
                    display=True,
                    referenced_at=[],
                    conversion_status="native-omml-not-verified",
                    source_line_start=start + 1,
                    source_line_end=i + 1,
                )
            )
        else:
            for match in INLINE_RE.finditer(line):
                index += 1
                records.append(
                    EquationRecord(
                        equation_number=None,
                        label=None,
                        latex=f"\\({match.group('body').strip()}\\)",
                        section=section,
                        paragraph_id=f"eq-{index:04d}",
                        word_location=f"source-line-{i + 1}",
                        inline=True,
                        display=False,
                        referenced_at=[],
                        conversion_status="native-omml-not-verified",
                        source_line_start=i + 1,
                        source_line_end=i + 1,
                    )
                )
        i += 1

    labels: dict[str, EquationRecord] = {}
    for record in records:
        if record.label:
            if record.label in labels:
                issues.append({"severity": "FAIL", "message": f"duplicate label: {record.label}", "line": str(record.source_line_start)})
            labels[record.label] = record
        for message in _compatibility_issues(record.latex):
            issues.append({"severity": "WARNING", "message": message, "line": str(record.source_line_start)})

    for label, locations in references.items():
        if label not in labels:
            issues.append({"severity": "FAIL", "message": f"unresolved equation reference: {label}", "line": ",".join(locations)})

    return records, issues


def write_tex(records: Iterable[EquationRecord], path: Path) -> None:
    chunks = [
        "% Pandoc-compatible equation source generated by mcm-paper-writing",
        "% Preserve this file as the editable source of truth.",
        "",
    ]
    for record in records:
        marker = record.equation_number if record.equation_number is not None else "unnumbered"
        chunks.extend(
            [
                f"% paragraph_id={record.paragraph_id}; number={marker}; section={record.section}",
                record.latex,
                "",
            ]
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(chunks).rstrip() + "\n", encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", type=Path, required=True, help="Markdown paper containing LaTeX")
    parser.add_argument("--tex", type=Path, required=True, help="Output equations.tex")
    parser.add_argument("--mapping", type=Path, required=True, help="Output equation_mapping.json")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        text = args.paper.read_text(encoding="utf-8-sig")
        records, issues = extract_equations(text)
        write_tex(records, args.tex)
        payload = {
            "schema_version": "1.0",
            "source": str(args.paper),
            "equation_count": len(records),
            "numbered_count": sum(item.equation_number is not None for item in records),
            "conversion_mode": "source-catalog-only-native-omml-not-verified",
            "equations": [asdict(item) for item in records],
            "issues": issues,
            "status": "FAIL" if any(item["severity"] == "FAIL" for item in issues) else ("WARNING" if issues else "PASS"),
        }
        args.mapping.parent.mkdir(parents=True, exist_ok=True)
        args.mapping.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"公式目录已生成：{len(records)} 个公式，状态 {payload['status']}。")
        return 1 if payload["status"] == "FAIL" else 0
    except OSError as exc:
        print(f"公式目录生成失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
