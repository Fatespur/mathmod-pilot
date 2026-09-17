from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

from png_renderer import render_png
from svg_generator import generate_svg


def _prefix_scene(scene: dict[str, Any], prefix: str, shift_x: float, shift_y: float = 0.0) -> dict[str, Any]:
    result = deepcopy(scene)
    mapping = {}
    for node in result["nodes"]:
        mapping[node["id"]] = f"{prefix}_{node['id']}"
        node["id"] = mapping[node["id"]]
        node["x"] += shift_x
        node["y"] += shift_y
    for group in result.get("groups", []):
        group["id"] = f"{prefix}_{group['id']}"
        group["node_ids"] = [mapping.get(node_id, node_id) for node_id in group.get("node_ids", [])]
        group["x"] += shift_x
        group["y"] += shift_y
    for edge in result["edges"]:
        edge["id"] = f"{prefix}_{edge['id']}"
        edge["source"] = mapping[edge["source"]]
        edge["target"] = mapping[edge["target"]]
        edge["points"] = [[x + shift_x, y + shift_y] for x, y in edge["points"]]
    return result


def comparison_scene(primary: dict[str, Any], alternative: dict[str, Any], gap: float = 160.0) -> dict[str, Any]:
    header_height = 76.0
    left = _prefix_scene(primary, "primary", 0, header_height)
    right = _prefix_scene(alternative, "alternative", primary["width"] + gap, header_height)
    right_start = primary["width"] + gap
    return {
        "layout_name": "comparison",
        "layout_family": "comparison",
        "width": primary["width"] + gap + alternative["width"],
        "height": max(primary["height"], alternative["height"]) + header_height,
        "nodes": left["nodes"] + right["nodes"],
        "groups": left.get("groups", []) + right.get("groups", []),
        "edges": left["edges"] + right["edges"],
        "background": primary.get("background", "#FFFFFF"),
        "theme": primary.get("theme", "journal-rich"),
        "headers": [
            {"label": f"主方案 · {primary['layout_name']}", "x": primary["width"] / 2, "y": 48},
            {"label": f"备选方案 · {alternative['layout_name']}", "x": right_start + alternative["width"] / 2, "y": 48},
        ],
    }


def generate_comparison(
    primary: dict[str, Any],
    alternative: dict[str, Any],
    svg_path: Path,
    png_path: Path,
    *,
    title: str,
    transparent: bool,
    long_edge: int,
    dpi: int,
    target_width_mm: float,
) -> dict[str, Any]:
    scene = comparison_scene(primary, alternative)
    generate_svg(scene, svg_path, f"{title} · 主备布局比较", transparent=transparent, target_width_mm=target_width_mm * 2)
    png_info = render_png(scene, png_path, long_edge=long_edge, dpi=dpi, transparent=transparent, target_width_mm=target_width_mm * 2)
    return {"scene": scene, "png": png_info}
