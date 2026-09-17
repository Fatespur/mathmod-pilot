from __future__ import annotations

import math
import random
from collections import defaultdict
from typing import Any, Callable

from layout_geometry import group_bounds, layout_family, normalize_canvas, scene_node
from route_edges import route_all_edges


def _linear_centers(count: int, direction: str) -> list[tuple[float, float]]:
    gap_x, gap_y = 390.0, 215.0
    if direction in {"left_to_right", "right_to_left"}:
        centers = [(index * gap_x, 0.0) for index in range(count)]
        return list(reversed(centers)) if direction == "right_to_left" else centers
    centers = [(0.0, index * gap_y) for index in range(count)]
    return list(reversed(centers)) if direction == "bottom_to_top" else centers


def _serpentine_centers(count: int) -> list[tuple[float, float]]:
    columns = max(3, min(5, math.ceil(math.sqrt(count * 1.5))))
    centers = []
    for index in range(count):
        row, col = divmod(index, columns)
        if row % 2:
            col = columns - 1 - col
        centers.append((col * 320.0, row * 215.0))
    return centers


def _matrix_centers(count: int) -> list[tuple[float, float]]:
    columns = max(2, math.ceil(math.sqrt(count)))
    return [(index % columns * 390.0, index // columns * 215.0) for index in range(count)]


def _radial_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    count = len(nodes)
    if count == 1:
        return [(0.0, 0.0)]
    radius = max(430.0, count * 62.0)
    core_index = next(
        (index for index, node in enumerate(nodes) if node.get("framework_role") == "main_method"),
        0,
    )
    centers: list[tuple[float, float] | None] = [None] * count
    centers[core_index] = (0.0, 0.0)
    ring_indices = [index for index in range(count) if index != core_index]
    for ring_position, node_index in enumerate(ring_indices):
        angle = 2 * math.pi * ring_position / max(1, len(ring_indices)) - math.pi / 2
        centers[node_index] = (radius * math.cos(angle), radius * math.sin(angle))
    return [center or (0.0, 0.0) for center in centers]


def _stage_groups(nodes: list[dict[str, Any]]) -> dict[int, list[int]]:
    stages: dict[int, list[int]] = defaultdict(list)
    for index, node in enumerate(nodes):
        stages[int(node.get("stage", node.get("level", 0)))].append(index)
    return stages


def _framework_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    stages = _stage_groups(nodes)
    centers: list[tuple[float, float] | None] = [None] * len(nodes)
    for column, (_, indices) in enumerate(sorted(stages.items())):
        count = len(indices)
        vertical_gap = 190.0
        for row, index in enumerate(indices):
            centers[index] = (column * 405.0, (row - (count - 1) / 2) * vertical_gap)
    return [center or (0.0, 0.0) for center in centers]


def _hierarchical_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    stages = _stage_groups(nodes)
    centers: list[tuple[float, float] | None] = [None] * len(nodes)
    for row, (_, indices) in enumerate(sorted(stages.items())):
        count = len(indices)
        horizontal_gap = 340.0
        for column, index in enumerate(indices):
            centers[index] = ((column - (count - 1) / 2) * horizontal_gap, row * 225.0)
    return [center or (0.0, 0.0) for center in centers]


def _cycle_centers(count: int) -> list[tuple[float, float]]:
    radius = max(400.0, count * 58.0)
    return [
        (radius * math.cos(2 * math.pi * index / count - math.pi / 2), radius * math.sin(2 * math.pi * index / count - math.pi / 2))
        for index in range(count)
    ]


def _u_centers(count: int) -> list[tuple[float, float]]:
    if count <= 3:
        return _linear_centers(count, "left_to_right")
    left_count = math.ceil(count / 3)
    bottom_count = max(1, count - 2 * left_count)
    right_count = count - left_count - bottom_count
    centers = [(0.0, index * 215.0) for index in range(left_count)]
    y_bottom = (left_count - 1) * 215.0
    centers.extend(((index + 1) * 390.0, y_bottom) for index in range(bottom_count))
    x_right = (bottom_count + 1) * 390.0
    centers.extend((x_right, y_bottom - index * 215.0) for index in range(right_count))
    return centers[:count]


def _perimeter_centers(count: int) -> list[tuple[float, float]]:
    width = max(900.0, math.ceil(count / 4) * 290.0)
    height = max(560.0, math.ceil(count / 4) * 165.0)
    per_side = [math.ceil(count / 4)] * 4
    centers = []
    for index in range(per_side[0]):
        centers.append((index * width / max(1, per_side[0] - 1), 0.0))
    for index in range(1, per_side[1] + 1):
        centers.append((width, index * height / per_side[1]))
    for index in range(1, per_side[2] + 1):
        centers.append((width - index * width / per_side[2], height))
    for index in range(1, per_side[3]):
        centers.append((0.0, height - index * height / per_side[3]))
    return centers[:count]


def _concentric_centers(count: int) -> list[tuple[float, float]]:
    if count <= 1:
        return [(0.0, 0.0)]
    inner = min(6, max(3, math.ceil((count - 1) / 2)))
    centers = [(0.0, 0.0)]
    remaining = count - 1
    for index in range(min(inner, remaining)):
        angle = 2 * math.pi * index / min(inner, remaining)
        centers.append((310 * math.cos(angle), 310 * math.sin(angle)))
    outer_remaining = count - len(centers)
    for index in range(outer_remaining):
        angle = 2 * math.pi * index / outer_remaining + math.pi / max(1, outer_remaining)
        centers.append((590 * math.cos(angle), 590 * math.sin(angle)))
    return centers


def _dual_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    midpoint = math.ceil(len(nodes) / 2)
    centers = []
    for index in range(midpoint):
        centers.append((index * 300.0, 0.0))
    for index in range(len(nodes) - midpoint):
        centers.append((index * 300.0, 270.0))
    return centers


def _swimlane_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    groups: dict[str, list[int]] = defaultdict(list)
    for index, node in enumerate(nodes):
        groups[node.get("question_id", "Q")].append(index)
    centers: list[tuple[float, float] | None] = [None] * len(nodes)
    lane_y = 0.0
    for indices in groups.values():
        by_stage: dict[int, list[int]] = defaultdict(list)
        for index in indices:
            by_stage[int(nodes[index].get("stage", nodes[index].get("level", 0)))].append(index)
        max_stack = max((len(stack) for stack in by_stage.values()), default=1)
        lane_height = max(300.0, max_stack * 155.0 + 90.0)
        for column, (_, stage_indices) in enumerate(sorted(by_stage.items())):
            for branch_row, index in enumerate(stage_indices):
                offset = (branch_row - (len(stage_indices) - 1) / 2) * 145.0
                centers[index] = (column * 365.0, lane_y + offset)
        lane_y += lane_height
    return [center or (0.0, 0.0) for center in centers]


def _question_architecture_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    """Lay out every question as six balanced method modules, not a process row."""
    groups: dict[str, list[int]] = defaultdict(list)
    for index, node in enumerate(nodes):
        groups[node.get("question_id", "Q")].append(index)
    centers: list[tuple[float, float] | None] = [None] * len(nodes)
    lane_top = 0.0
    stage_to_zone = {0: 0, 1: 1, 2: 2, 3: 3, 4: 4, 5: 4, 6: 5, 7: 5, 8: 5}
    for question_index, indices in enumerate(groups.values()):
        by_zone: dict[int, list[int]] = defaultdict(list)
        for index in indices:
            stage = int(nodes[index].get("stage", nodes[index].get("level", 0)))
            by_zone[stage_to_zone.get(stage, min(stage, 5))].append(index)
        max_stack = max((len(stack) for stack in by_zone.values()), default=1)
        lane_height = max(620.0, 175.0 * max_stack + 170.0)
        lane_center = lane_top + lane_height / 2
        for zone, zone_indices in sorted(by_zone.items()):
            ordered = sorted(
                zone_indices,
                key=lambda index: (
                    nodes[index].get("framework_role") != "main_method",
                    nodes[index].get("framework_role") != "output",
                    -int(nodes[index].get("stage", 0)),
                    nodes[index].get("branch", ""),
                    nodes[index]["id"],
                ),
            )
            count = len(ordered)
            for row, index in enumerate(ordered):
                offset = (row - (count - 1) / 2) * 175.0
                visual_zone = zone if question_index % 2 == 0 else 5 - zone
                centers[index] = (visual_zone * 405.0, lane_center + offset)
        lane_top += lane_height + 130.0
    return [center or (0.0, 0.0) for center in centers]


def _architecture_centers(nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    return _framework_centers(nodes)


def _convergence_centers(nodes: list[dict[str, Any]], fan_out: bool = False) -> list[tuple[float, float]]:
    count = len(nodes)
    split = max(2, count // 2)
    sources = split if not fan_out else 1
    centers = []
    for index in range(sources):
        centers.append((0.0, (index - (sources - 1) / 2) * 170.0))
    remaining = count - sources
    for index in range(remaining):
        x = 340.0 + index * 290.0 if not fan_out else 340.0
        y = 0.0 if not fan_out else (index - (remaining - 1) / 2) * 170.0
        centers.append((x, y))
    return centers


def _centers_for(layout_name: str, nodes: list[dict[str, Any]]) -> list[tuple[float, float]]:
    family = layout_family(layout_name)
    if family == "linear":
        return _linear_centers(len(nodes), layout_name)
    if family == "serpentine":
        return _serpentine_centers(len(nodes))
    if family == "matrix":
        return _matrix_centers(len(nodes))
    if family == "radial":
        return _radial_centers(nodes)
    if family == "cycle":
        return _cycle_centers(len(nodes))
    if family == "u_shape":
        return _u_centers(len(nodes))
    if family == "perimeter":
        return _perimeter_centers(len(nodes))
    if family == "concentric":
        return _concentric_centers(len(nodes))
    if family == "parallel":
        return _dual_centers(nodes)
    if family == "swimlane":
        return _swimlane_centers(nodes)
    if family == "question_architecture":
        return _question_architecture_centers(nodes)
    if family == "architecture":
        return _architecture_centers(nodes)
    if family == "framework":
        return _framework_centers(nodes)
    if family == "hierarchy":
        return _hierarchical_centers(nodes)
    if family == "convergence":
        return _convergence_centers(nodes, layout_name == "fan_out")
    return _linear_centers(len(nodes), "left_to_right")


def build_layout(ir: dict[str, Any], layout_name: str, *, seed: int = 42, spacing_scale: float = 1.0) -> dict[str, Any]:
    random.seed(seed)
    base_nodes = ir["nodes"]
    centers = _centers_for(layout_name, base_nodes)
    if spacing_scale != 1.0:
        centers = [(x * spacing_scale, y * spacing_scale) for x, y in centers]
    scene_nodes = [scene_node(node, center) for node, center in zip(base_nodes, centers)]
    width, height = normalize_canvas(scene_nodes)
    nodes_by_id = {node["id"]: node for node in scene_nodes}
    groups = [
        bounds
        for group in ir.get("groups", [])
        if (bounds := group_bounds(group, nodes_by_id)) is not None
    ]
    routed_edges = route_all_edges(ir["edges"], nodes_by_id, layout_name)
    return {
        "schema_version": "1.0",
        "layout_name": layout_name,
        "layout_family": layout_family(layout_name),
        "seed": seed,
        "width": width,
        "height": height,
        "nodes": scene_nodes,
        "groups": groups,
        "edges": routed_edges,
    }


def candidate_layout_names(ir: dict[str, Any]) -> list[str]:
    question_types = {question["primary_type"] for question in ir.get("questions", [])}
    has_feedback = any(edge.get("feedback") for edge in ir.get("edges", []))
    if len(ir.get("questions", [])) > 1:
        return ["question_architecture", "hierarchical_tree", "question_swimlane", "method_framework", "layered_architecture", "hub_spoke", "matrix"]
    if has_feedback:
        return ["rectangular_loop", "method_framework", "circular_cycle", "u_shaped", "hierarchical_tree", "layered_architecture"]
    if "优化类" in question_types:
        return ["method_framework", "hierarchical_tree", "rectangular_loop", "layered_architecture", "hub_spoke", "matrix"]
    if "预测类" in question_types:
        return ["method_framework", "layered_architecture", "hierarchical_tree", "dual_stream", "split_merge", "hub_spoke"]
    if "评价类" in question_types:
        return ["method_framework", "hub_spoke", "hierarchical_tree", "split_merge", "layered_architecture", "matrix"]
    if "数理统计类" in question_types:
        return ["method_framework", "hierarchical_tree", "layered_architecture", "split_merge", "matrix", "hub_spoke"]
    return ["method_framework", "concentric", "hierarchical_tree", "layered_architecture", "hub_spoke", "u_shaped"]


def generate_layout_candidates(
    ir: dict[str, Any],
    *,
    seed: int = 42,
    forced: list[str] | None = None,
    spacing_scale: float = 1.0,
) -> list[dict[str, Any]]:
    names = []
    for name in (forced or []) + candidate_layout_names(ir):
        if name and name not in names:
            names.append(name)
    if len(names) < 4:
        names.extend(name for name in ["left_to_right", "serpentine", "hub_spoke", "matrix"] if name not in names)
    return [build_layout(ir, name, seed=seed, spacing_scale=spacing_scale) for name in names[:10]]
