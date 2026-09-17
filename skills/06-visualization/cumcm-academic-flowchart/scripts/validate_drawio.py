from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def validate_drawio(path: Path, expected_nodes: set[str] | None = None) -> dict[str, Any]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except Exception as exc:
        return {"passed": False, "errors": [f"XML parse failed: {exc}"], "node_ids": [], "edge_ids": []}
    cells = root.findall(".//mxCell")
    node_ids = {cell.get("id") for cell in cells if cell.get("vertex") == "1" and cell.get("id")}
    edge_cells = [cell for cell in cells if cell.get("edge") == "1"]
    edge_ids = {cell.get("id") for cell in edge_cells if cell.get("id")}
    for cell in edge_cells:
        if cell.get("source") not in node_ids or cell.get("target") not in node_ids:
            errors.append(f"Edge {cell.get('id')} references missing node")
    if len(node_ids) != len([cell for cell in cells if cell.get("vertex") == "1" and cell.get("id")]):
        errors.append("Duplicate vertex IDs")
    if expected_nodes and not expected_nodes.issubset(node_ids):
        errors.append(f"Missing expected nodes: {sorted(expected_nodes - node_ids)}")
    return {
        "passed": not errors,
        "errors": errors,
        "node_ids": sorted(node_ids),
        "edge_ids": sorted(edge_ids),
        "size": path.stat().st_size,
    }
