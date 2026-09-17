from __future__ import annotations

import math
from typing import Any


LAYOUT_FAMILIES = {
    "left_to_right": "linear",
    "right_to_left": "linear",
    "top_to_bottom": "linear",
    "bottom_to_top": "linear",
    "dual_stream": "parallel",
    "parallel_lanes": "parallel",
    "split_merge": "parallel",
    "horizontal_swimlane": "swimlane",
    "vertical_swimlane": "swimlane",
    "question_swimlane": "swimlane",
    "question_architecture": "question_architecture",
    "fan_in": "convergence",
    "fan_out": "convergence",
    "y_shape": "convergence",
    "hourglass": "convergence",
    "hub_spoke": "radial",
    "radial": "radial",
    "central_model": "radial",
    "circular_cycle": "cycle",
    "feedback_ring": "cycle",
    "iterative_loop": "cycle",
    "rectangular_loop": "perimeter",
    "hui_shape": "perimeter",
    "perimeter_flow": "perimeter",
    "u_shaped": "u_shape",
    "horseshoe": "u_shape",
    "serpentine": "serpentine",
    "s_curve": "serpentine",
    "zigzag": "serpentine",
    "concentric": "concentric",
    "nested_layers": "concentric",
    "core_shell": "concentric",
    "matrix": "matrix",
    "quadrant": "matrix",
    "grid_dependency": "matrix",
    "layered_architecture": "architecture",
    "modular_architecture": "architecture",
    "encoder_fusion_decoder": "architecture",
    "method_framework": "framework",
    "modular_method_map": "framework",
    "hierarchical_tree": "hierarchy",
    "method_tree": "hierarchy",
}


SEMANTIC_SHAPES = {
    "data": "data",
    "input": "data",
    "sample": "data",
    "decision_variable": "hexagon",
    "objective": "hexagon",
    "solver": "hexagon",
    "convergence": "diamond",
    "assumption_test": "diamond",
    "significance": "diamond",
    "model": "core",
    "equation": "core",
    "mechanism": "core",
    "output": "document",
    "prediction": "document",
    "validation": "roundrect",
    "diagnosis": "roundrect",
    "sensitivity": "roundrect",
}


def layout_family(layout_name: str) -> str:
    return LAYOUT_FAMILIES.get(layout_name, layout_name)


def node_dimensions(node: dict[str, Any]) -> tuple[float, float]:
    label = node.get("short_label") or node.get("label", "")
    # Chinese glyphs are close to square at paper sizes.  Reserve real
    # horizontal padding instead of using a Latin-character heuristic.
    lines = max(1, min(3, math.ceil(len(label) / 8)))
    longest_line = min(8, max(1, len(label)))
    width = max(230.0, min(340.0, 92.0 + longest_line * 22.0))
    height = 78.0 + (lines - 1) * 26.0
    if node.get("importance") == "primary":
        width += 20
        height += 8
    if node.get("framework_role") == "main_method":
        width += 42
        height += 18
    elif node.get("framework_role") in {"context", "evidence"}:
        width = max(210.0, width - 14)
    return width, height


def scene_node(node: dict[str, Any], center: tuple[float, float]) -> dict[str, Any]:
    width, height = node_dimensions(node)
    x = center[0] - width / 2
    y = center[1] - height / 2
    result = dict(node)
    shape = "core" if node.get("framework_role") == "main_method" else SEMANTIC_SHAPES.get(node.get("semantic_type", ""), "roundrect")
    result.update(
        {
            "x": round(x, 3),
            "y": round(y, 3),
            "width": round(width, 3),
            "height": round(height, 3),
            "shape": shape,
        }
    )
    return result


def normalize_canvas(nodes: list[dict[str, Any]], margin: float = 100.0) -> tuple[float, float]:
    min_x = min(node["x"] for node in nodes)
    min_y = min(node["y"] for node in nodes)
    max_x = max(node["x"] + node["width"] for node in nodes)
    max_y = max(node["y"] + node["height"] for node in nodes)
    shift_x, shift_y = margin - min_x, margin - min_y
    for node in nodes:
        node["x"] = round(node["x"] + shift_x, 3)
        node["y"] = round(node["y"] + shift_y, 3)
    return round(max_x - min_x + 2 * margin, 3), round(max_y - min_y + 2 * margin, 3)


def group_bounds(
    group: dict[str, Any],
    nodes_by_id: dict[str, dict[str, Any]],
    padding: float = 42.0,
) -> dict[str, Any] | None:
    members = [nodes_by_id[node_id] for node_id in group.get("node_ids", []) if node_id in nodes_by_id]
    if not members:
        return None
    min_x = min(node["x"] for node in members) - padding
    min_y = min(node["y"] for node in members) - padding - 18
    max_x = max(node["x"] + node["width"] for node in members) + padding
    max_y = max(node["y"] + node["height"] for node in members) + padding
    return {
        **group,
        "x": round(min_x, 3),
        "y": round(min_y, 3),
        "width": round(max_x - min_x, 3),
        "height": round(max_y - min_y, 3),
    }
