from __future__ import annotations

from typing import Any


def validate_typography(scene: dict[str, Any], target_width_mm: float = 160) -> dict[str, Any]:
    width = max(float(scene.get("width", 1)), 1)
    node_user_units = min(30.0, max(15.0, width / max(target_width_mm, 1) * 3.45))
    edge_user_units = min(24.0, max(13.0, width / max(target_width_mm, 1) * 2.75))
    node_font_pt = node_user_units * target_width_mm / width * 72 / 25.4
    edge_font_pt = edge_user_units * target_width_mm / width * 72 / 25.4
    errors = []
    warnings = []
    if node_font_pt < 7.5:
        errors.append(f"Node font {node_font_pt:.2f} pt < 7.5 pt")
    elif node_font_pt < 8.5:
        warnings.append(f"Node font {node_font_pt:.2f} pt is below the preferred 8.5 pt")
    if edge_font_pt < 6.5:
        errors.append(f"Edge font {edge_font_pt:.2f} pt < 6.5 pt")
    elif edge_font_pt < 7.5:
        warnings.append(f"Edge font {edge_font_pt:.2f} pt is below the preferred 7.5 pt")
    for node in scene["nodes"]:
        label = node.get("short_label") or node.get("label", "")
        if len(label) > 36:
            errors.append(f"Node {node['id']} label exceeds 3 lines")
        elif len(label) > 14:
            warnings.append(f"Node {node['id']} label exceeds recommended 14 Chinese characters")
    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "font_fallback": [
            "Microsoft YaHei",
            "Noto Sans CJK SC",
            "Source Han Sans SC",
            "SimHei",
            "Arial",
            "sans-serif",
        ],
        "target_width_mm": target_width_mm,
        "node_font_pt": round(node_font_pt, 3),
        "core_font_pt": round(max(9.5, node_font_pt), 3),
        "group_title_pt": 10.0,
        "edge_label_pt": round(edge_font_pt, 3),
    }
