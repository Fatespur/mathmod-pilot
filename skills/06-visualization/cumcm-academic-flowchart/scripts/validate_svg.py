from __future__ import annotations

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


def validate_svg(path: Path, expected_node_count: int | None = None) -> dict[str, Any]:
    errors: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except Exception as exc:
        return {"passed": False, "errors": [f"SVG parse failed: {exc}"]}
    view_box = root.get("viewBox")
    if not view_box or len(view_box.split()) != 4:
        errors.append("SVG viewBox is missing or invalid")
    if root.find(".//{http://www.w3.org/2000/svg}image") is not None:
        errors.append("SVG contains a raster image")
    if "http://" in path.read_text(encoding="utf-8") or "https://" in path.read_text(encoding="utf-8"):
        text = path.read_text(encoding="utf-8")
        if "www.w3.org/2000/svg" not in text or text.count("http") > 1:
            errors.append("SVG references a remote resource")
    node_count = int(root.get("data-node-count", "0"))
    edge_count = int(root.get("data-edge-count", "0"))
    if expected_node_count is not None and node_count != expected_node_count:
        errors.append(f"SVG node count {node_count} != {expected_node_count}")
    return {
        "passed": not errors,
        "errors": errors,
        "viewBox": view_box,
        "node_count": node_count,
        "edge_count": edge_count,
        "size": path.stat().st_size,
    }
