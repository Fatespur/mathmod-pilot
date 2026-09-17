from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils import SCHEMA_ROOT


ALLOWED_TYPES = {"优化类", "预测类", "评价类", "数理统计类", "机理分析类"}


def validate_ir(ir: dict[str, Any], use_jsonschema: bool = True) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required = {"meta", "questions", "diagram", "groups", "nodes", "edges"}
    missing = required - set(ir)
    if missing:
        errors.append(f"Missing top-level keys: {sorted(missing)}")
    node_ids = [node.get("id") for node in ir.get("nodes", [])]
    if len(node_ids) != len(set(node_ids)):
        errors.append("Node IDs are not unique")
    edge_ids = [edge.get("id") for edge in ir.get("edges", [])]
    if len(edge_ids) != len(set(edge_ids)):
        errors.append("Edge IDs are not unique")
    node_set = set(node_ids)
    for edge in ir.get("edges", []):
        if edge.get("source") not in node_set or edge.get("target") not in node_set:
            errors.append(f"Edge {edge.get('id')} has invalid endpoint")
    for question in ir.get("questions", []):
        if question.get("primary_type") not in ALLOWED_TYPES:
            errors.append(f"Invalid primary type for {question.get('question_id')}")
        if not 0 <= float(question.get("confidence", -1)) <= 1:
            errors.append(f"Invalid confidence for {question.get('question_id')}")
    if not ir.get("nodes"):
        errors.append("IR contains no nodes")
    if use_jsonschema:
        try:
            import jsonschema

            schema = json.loads((SCHEMA_ROOT / "modeling_ir.schema.json").read_text(encoding="utf-8"))
            jsonschema.validate(ir, schema)
        except ImportError:
            warnings.append("jsonschema is unavailable; built-in validation used")
        except Exception as exc:
            errors.append(f"JSON Schema validation failed: {exc}")
    return {"passed": not errors, "errors": errors, "warnings": warnings}
