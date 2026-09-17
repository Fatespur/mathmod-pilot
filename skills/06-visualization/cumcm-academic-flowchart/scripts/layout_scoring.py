from __future__ import annotations

import math
from itertools import combinations
from statistics import mean
from typing import Any

from utils import box_intersection, polyline_length, segment_intersection


def node_overlap_pairs(layout: dict[str, Any]) -> list[tuple[str, str]]:
    overlaps = []
    for left, right in combinations(layout["nodes"], 2):
        width, height = box_intersection(
            (left["x"], left["y"], left["width"], left["height"]),
            (right["x"], right["y"], right["width"], right["height"]),
        )
        if width > 1 and height > 1:
            overlaps.append((left["id"], right["id"]))
    return overlaps


def edge_crossing_count(layout: dict[str, Any]) -> int:
    segments = []
    for edge in layout["edges"]:
        points = [tuple(point) for point in edge["points"]]
        segments.extend((edge["id"], start, end) for start, end in zip(points, points[1:]))
    crossings = 0
    for (edge_a, a1, a2), (edge_b, b1, b2) in combinations(segments, 2):
        if edge_a != edge_b and segment_intersection(a1, a2, b1, b2):
            crossings += 1
    return crossings


def _visual_balance(layout: dict[str, Any]) -> float:
    centers = [
        (node["x"] + node["width"] / 2, node["y"] + node["height"] / 2)
        for node in layout["nodes"]
    ]
    centroid = (mean(point[0] for point in centers), mean(point[1] for point in centers))
    canvas_center = (layout["width"] / 2, layout["height"] / 2)
    normalized = math.dist(centroid, canvas_center) / max(layout["width"], layout["height"], 1)
    return max(0.0, 1.0 - normalized * 2)


def _group_cohesion(layout: dict[str, Any]) -> float:
    if len(layout.get("groups", [])) <= 1:
        return 1.0
    nodes = {node["id"]: node for node in layout["nodes"]}
    scores = []
    for group in layout["groups"]:
        members = [nodes[node_id] for node_id in group.get("node_ids", []) if node_id in nodes]
        if len(members) < 2:
            continue
        centers = [(node["x"] + node["width"] / 2, node["y"] + node["height"] / 2) for node in members]
        average = mean(math.dist(a, b) for a, b in combinations(centers, 2))
        scores.append(max(0.0, 1.0 - average / max(layout["width"], layout["height"], 1)))
    return mean(scores) if scores else 1.0


def _semantic_order(layout: dict[str, Any]) -> float:
    family = layout["layout_family"]
    if family not in {"linear", "serpentine", "swimlane", "question_architecture", "parallel", "architecture", "framework", "hierarchy"}:
        return 1.0
    nodes = {node["id"]: node for node in layout["nodes"]}
    correct = 0
    considered = 0
    for edge in layout["edges"]:
        if edge.get("feedback"):
            continue
        source, target = nodes[edge["source"]], nodes[edge["target"]]
        sx, sy = source["x"] + source["width"] / 2, source["y"] + source["height"] / 2
        tx, ty = target["x"] + target["width"] / 2, target["y"] + target["height"] / 2
        considered += 1
        if family == "question_architecture":
            if source.get("question_id") != target.get("question_id"):
                ordered = ty >= sy - 20
            else:
                digits = "".join(character for character in str(source.get("question_id", "1")) if character.isdigit())
                question_number = int(digits or "1")
                ordered = tx >= sx - 20 if question_number % 2 else tx <= sx + 20
        elif family == "hierarchy":
            ordered = ty >= sy - 20
        elif family in {"framework", "architecture", "parallel", "swimlane", "linear"}:
            ordered = tx >= sx - 20
        else:
            ordered = tx >= sx - 20 or ty >= sy - 20
        if ordered:
            correct += 1
    return correct / considered if considered else 1.0


def score_layout(layout: dict[str, Any]) -> dict[str, Any]:
    node_count = max(1, len(layout["nodes"]))
    possible_pairs = max(1, node_count * (node_count - 1) / 2)
    overlaps = node_overlap_pairs(layout)
    overlap_score = max(0.0, 1.0 - len(overlaps) / possible_pairs * 8)
    crossings = edge_crossing_count(layout)
    crossing_score = max(0.0, 1.0 - crossings / max(1, len(layout["edges"])) * 0.35)
    lengths = [polyline_length([tuple(point) for point in edge["points"]]) for edge in layout["edges"]]
    edge_length_score = max(0.65, 1.0 - (mean(lengths) if lengths else 0) / max(layout["width"], layout["height"], 1) * 0.25)
    label_clipping_score = 1.0
    node_area = sum(node["width"] * node["height"] for node in layout["nodes"])
    density = node_area / max(1, layout["width"] * layout["height"])
    density_score = max(0.7, 1.0 - abs(density - 0.16) * 1.2)
    whitespace_balance_score = max(0.75, 1.0 - abs(density - 0.16))
    visual_balance_score = _visual_balance(layout)
    semantic_order_score = _semantic_order(layout)
    group_cohesion_score = _group_cohesion(layout)
    flow_clarity_score = 0.5 * overlap_score + 0.3 * crossing_score + 0.2 * semantic_order_score
    aspect = layout["width"] / max(layout["height"], 1)
    paper_fit_score = max(0.75, 1.0 - min(abs(aspect - 1.45), 2.0) * 0.08)
    symmetry_score = max(0.75, visual_balance_score)
    weighted = (
        0.25 * flow_clarity_score
        + 0.15 * overlap_score
        + 0.12 * crossing_score
        + 0.10 * semantic_order_score
        + 0.10 * group_cohesion_score
        + 0.08 * label_clipping_score
        + 0.08 * paper_fit_score
        + 0.06 * visual_balance_score
        + 0.06 * whitespace_balance_score
    )
    architecture_bonus = {
        "question_architecture": 4.0,
        "framework": 2.0,
        "hierarchy": 2.0,
        "architecture": 1.5,
    }.get(layout["layout_family"], 0.0)
    metrics = {
        "node_overlap_score": round(overlap_score, 4),
        "edge_crossing_score": round(crossing_score, 4),
        "edge_length_score": round(edge_length_score, 4),
        "label_clipping_score": round(label_clipping_score, 4),
        "whitespace_balance_score": round(whitespace_balance_score, 4),
        "visual_balance_score": round(visual_balance_score, 4),
        "semantic_order_score": round(semantic_order_score, 4),
        "group_cohesion_score": round(group_cohesion_score, 4),
        "flow_clarity_score": round(flow_clarity_score, 4),
        "paper_fit_score": round(paper_fit_score, 4),
        "symmetry_score": round(symmetry_score, 4),
        "density_score": round(density_score, 4),
        "overlap_pairs": overlaps,
        "edge_crossings": crossings,
        "architecture_bonus": architecture_bonus,
        "layout_score": round(min(100.0, weighted * 100 + architecture_bonus), 2),
    }
    layout["metrics"] = metrics
    return metrics
