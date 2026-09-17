#!/usr/bin/env python3
"""Validate numerical claims in a modeling paper against paper_macros.json."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable


NUMBER_RE = re.compile(
    r"(?<![\w.])"
    r"(?P<token>[+-]?(?:(?:\d{1,3}(?:,\d{3})+)|(?:\d+))(?:\.\d+)?"
    r"(?:[eE][+-]?\d+)?%?)"
    r"(?![\w.])"
)

STRUCTURAL_PATTERNS = (
    re.compile(r"^\s{0,3}#{1,6}\s+(?:第?[一二三四五六七八九十百]+[、.]|\d+(?:\.\d+)*[、.]?)"),
    re.compile(r"(?:图|表|式|公式|Figure|Fig\.?|Table|Equation|Eq\.?)\s*\(?\s*$", re.I),
    re.compile(r"\\(?:tag|qquad)\s*\{?\(?\s*$"),
)


@dataclass(frozen=True)
class MacroValue:
    key: str
    value: float
    tolerance: float
    formats: tuple[str, ...]


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise ValueError(f"文件不存在: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"JSON 无效: {path}:{exc.lineno}:{exc.colno}: {exc.msg}") from exc


def validate_macro_document(document: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["宏文件根节点必须是对象"]

    if "macros" in document:
        if document.get("schema_version") != "1.0":
            errors.append("schema_version 必须为 1.0")
        macros = document.get("macros")
        if not isinstance(macros, dict) or not macros:
            errors.append("macros 必须是非空对象")
        else:
            _validate_macro_nodes(macros, "macros", errors)
        allowlist = document.get("allowlist", {})
        if allowlist is not None and not isinstance(allowlist, dict):
            errors.append("allowlist 必须是对象")
    else:
        numeric_count = sum(1 for _ in _legacy_numeric_leaves(document))
        if numeric_count == 0:
            errors.append("旧版宏文件至少需要一个数值叶节点")
    return errors


def _validate_macro_nodes(node: Any, path: str, errors: list[str]) -> None:
    if not isinstance(node, dict):
        errors.append(f"{path} 必须是对象")
        return
    if "value" in node and not isinstance(node["value"], dict):
        if not node.get("source"):
            errors.append(f"{path}.source 不能为空")
        if not _contains_numeric(node["value"]):
            errors.append(f"{path}.value 必须包含数值")
        if "precision" in node and (
            not isinstance(node["precision"], int) or not 0 <= node["precision"] <= 15
        ):
            errors.append(f"{path}.precision 必须是 0-15 的整数")
        if "formats" in node and not (
            isinstance(node["formats"], list)
            and all(isinstance(item, str) for item in node["formats"])
        ):
            errors.append(f"{path}.formats 必须是字符串数组")
        return
    for key, value in node.items():
        _validate_macro_nodes(value, f"{path}.{key}", errors)


def _contains_numeric(value: Any) -> bool:
    if isinstance(value, bool):
        return False
    if isinstance(value, (int, float)):
        return math.isfinite(float(value))
    if isinstance(value, str):
        try:
            return math.isfinite(float(value.replace(",", "").rstrip("%")))
        except ValueError:
            return False
    if isinstance(value, list):
        return bool(value) and all(_contains_numeric(item) for item in value)
    return False


def _legacy_numeric_leaves(node: Any, prefix: str = "") -> Iterable[tuple[str, float]]:
    if isinstance(node, bool):
        return
    if isinstance(node, (int, float)) and math.isfinite(float(node)):
        yield prefix or "value", float(node)
    elif isinstance(node, dict):
        for key, value in node.items():
            child = f"{prefix}.{key}" if prefix else str(key)
            yield from _legacy_numeric_leaves(value, child)
    elif isinstance(node, list):
        for index, value in enumerate(node):
            child = f"{prefix}[{index}]"
            yield from _legacy_numeric_leaves(value, child)


def flatten_macros(document: dict[str, Any]) -> tuple[list[MacroValue], dict[str, set[Any]]]:
    values: list[MacroValue] = []
    allowlist = {"values": set(), "years": set(), "tokens": set()}

    if "macros" not in document:
        for key, value in _legacy_numeric_leaves(document):
            values.append(MacroValue(key, value, _default_tolerance(value), ()))
        return values, allowlist

    def visit(node: Any, path: str) -> None:
        if isinstance(node, dict) and "value" in node and not isinstance(node["value"], dict):
            precision = node.get("precision")
            tolerance = float(node.get("tolerance", 0.0))
            formats = tuple(str(item) for item in node.get("formats", []))
            for index, numeric in enumerate(_numeric_values(node["value"])):
                key = path if index == 0 else f"{path}[{index}]"
                tol = tolerance or _precision_tolerance(numeric, precision)
                values.append(MacroValue(key, numeric, tol, formats))
            return
        if isinstance(node, dict):
            for key, value in node.items():
                visit(value, f"{path}.{key}" if path else key)

    visit(document["macros"], "")
    raw_allowlist = document.get("allowlist", {}) or {}
    allowlist["values"].update(raw_allowlist.get("values", []))
    allowlist["years"].update(raw_allowlist.get("years", []))
    allowlist["tokens"].update(raw_allowlist.get("tokens", []))
    return values, allowlist


def _numeric_values(value: Any) -> list[float]:
    if isinstance(value, bool):
        return []
    if isinstance(value, (int, float)):
        return [float(value)]
    if isinstance(value, str):
        return [parse_number(value)]
    if isinstance(value, list):
        result: list[float] = []
        for item in value:
            result.extend(_numeric_values(item))
        return result
    return []


def _default_tolerance(value: float) -> float:
    return max(1e-12, abs(value) * 1e-9)


def _precision_tolerance(value: float, precision: Any) -> float:
    if isinstance(precision, int):
        return max(_default_tolerance(value), 0.5 * 10 ** (-precision))
    return _default_tolerance(value)


def parse_number(token: str) -> float:
    clean = token.strip().replace(",", "")
    percent = clean.endswith("%")
    if percent:
        clean = clean[:-1]
    value = float(clean)
    return value / 100.0 if percent else value


def is_structural(line: str, start: int, end: int, token: str) -> bool:
    prefix = line[:start]
    suffix = line[end:]
    if STRUCTURAL_PATTERNS[0].search(line):
        heading_prefix = re.match(r"^\s{0,3}#{1,6}\s+(\d+(?:\.\d+)*)", line)
        if heading_prefix and start < heading_prefix.end():
            return True
    if any(pattern.search(prefix[-24:]) for pattern in STRUCTURAL_PATTERNS[1:]):
        return True
    if re.match(r"^\s*\)?", suffix) and re.search(r"(?:式|公式|Eq\.?)\s*\($", prefix[-16:], re.I):
        return True
    if prefix.endswith("[") and re.match(r"(?:[-–,]\s*\d+)*\]", suffix):
        return True
    if re.search(r"\]\s*$", suffix) and re.search(r"\[[\d,\-–\s]*$", prefix):
        return True
    return False


def token_matches_macro(token: str, numeric: float, macro: MacroValue) -> bool:
    if token in macro.formats:
        return True
    if math.isclose(numeric, macro.value, rel_tol=0.0, abs_tol=macro.tolerance):
        return True
    if token.endswith("%") and math.isclose(
        numeric, macro.value, rel_tol=0.0, abs_tol=max(macro.tolerance, 5e-12)
    ):
        return True
    return False


def validate_paper(text: str, macros: list[MacroValue], allowlist: dict[str, set[Any]]) -> dict[str, Any]:
    matched: list[dict[str, Any]] = []
    unknown: list[dict[str, Any]] = []
    structural: list[dict[str, Any]] = []
    in_fence = False

    for line_number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        for match in NUMBER_RE.finditer(line):
            token = match.group("token")
            item = {
                "line": line_number,
                "column": match.start() + 1,
                "token": token,
                "context": line.strip()[:240],
            }
            if is_structural(line, match.start(), match.end(), token):
                item["reason"] = "structural"
                structural.append(item)
                continue
            if token in allowlist["tokens"]:
                item["reason"] = "allowlist-token"
                structural.append(item)
                continue
            numeric = parse_number(token)
            if token.isdigit() and int(token) in allowlist["years"]:
                item["reason"] = "allowlist-year"
                structural.append(item)
                continue
            allow_values = []
            for raw in allowlist["values"]:
                try:
                    allow_values.append(parse_number(str(raw)))
                except ValueError:
                    if token == str(raw):
                        item["reason"] = "allowlist-value"
                        structural.append(item)
                        break
            else:
                if any(math.isclose(numeric, value, abs_tol=_default_tolerance(value)) for value in allow_values):
                    item["reason"] = "allowlist-value"
                    structural.append(item)
                    continue
                keys = [macro.key for macro in macros if token_matches_macro(token, numeric, macro)]
                if keys:
                    item["macros"] = keys
                    matched.append(item)
                else:
                    unknown.append(item)

    return {
        "status": "passed" if not unknown else "failed",
        "summary": {
            "matched": len(matched),
            "unknown": len(unknown),
            "structural_or_allowed": len(structural),
        },
        "matched": matched,
        "unknown": unknown,
        "structural_or_allowed": structural,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--paper", type=Path, help="Markdown paper to validate")
    parser.add_argument("--macros", type=Path, required=True, help="paper_macros.json")
    parser.add_argument("--report", type=Path, help="JSON report path")
    parser.add_argument(
        "--validate-macros-only",
        action="store_true",
        help="Validate the macro document without scanning a paper",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        document = load_json(args.macros)
        errors = validate_macro_document(document)
        if errors:
            raise ValueError("; ".join(errors))
        macros, allowlist = flatten_macros(document)
        if args.validate_macros_only:
            print(f"宏文件有效，共加载 {len(macros)} 个数值。")
            return 0
        if args.paper is None:
            raise ValueError("未使用 --validate-macros-only 时必须提供 --paper")
        paper_text = args.paper.read_text(encoding="utf-8-sig")
        result = validate_paper(paper_text, macros, allowlist)
        result.update(
            {
                "schema_version": "paper_number_report.schema.v2_1",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "paper": str(args.paper),
                "macros": str(args.macros),
                "paper_sha256": hashlib.sha256(args.paper.read_bytes()).hexdigest(),
                "macros_sha256": hashlib.sha256(args.macros.read_bytes()).hexdigest(),
                "macro_values_loaded": len(macros),
            }
        )
        report_path = args.report or args.paper.with_name("paper_number_report.json")
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        summary = result["summary"]
        print(
            f"数字校验 {result['status']}: matched={summary['matched']}, "
            f"unknown={summary['unknown']}, structural_or_allowed="
            f"{summary['structural_or_allowed']}"
        )
        if result["unknown"]:
            for item in result["unknown"][:20]:
                print(f"  {item['line']}:{item['column']} 未知数字 {item['token']}: {item['context']}")
        print(f"报告: {report_path}")
        return 0 if result["status"] == "passed" else 1
    except (OSError, ValueError) as exc:
        print(f"输入或配置错误: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
