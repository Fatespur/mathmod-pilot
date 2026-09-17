from __future__ import annotations

from typing import Any

from layout_scoring import edge_crossing_count, node_overlap_pairs
from utils import segment_intersects_box


def _point_on_box_boundary(
    point: tuple[float, float],
    node: dict[str, Any],
    tolerance: float = 1e-3,
) -> bool:
    x, y = point
    left, right = node["x"], node["x"] + node["width"]
    top, bottom = node["y"], node["y"] + node["height"]
    on_horizontal = left - tolerance <= x <= right + tolerance and (
        abs(y - top) <= tolerance or abs(y - bottom) <= tolerance
    )
    on_vertical = top - tolerance <= y <= bottom + tolerance and (
        abs(x - left) <= tolerance or abs(x - right) <= tolerance
    )
    return on_horizontal or on_vertical


def _strictly_inside(point: tuple[float, float], node: dict[str, Any], tolerance: float = 1e-6) -> bool:
    x, y = point
    return (
        node["x"] + tolerance < x < node["x"] + node["width"] - tolerance
        and node["y"] + tolerance < y < node["y"] + node["height"] - tolerance
    )


def _near_endpoint_inside(
    boundary: tuple[float, float],
    adjacent: tuple[float, float],
    node: dict[str, Any],
) -> bool:
    probe = (
        boundary[0] + (adjacent[0] - boundary[0]) * 0.01,
        boundary[1] + (adjacent[1] - boundary[1]) * 0.01,
    )
    return _strictly_inside(probe, node)


def validate_layout(layout: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    overlaps = node_overlap_pairs(layout)
    if overlaps:
        errors.append(f"Node overlaps: {overlaps[:8]}")
    node_map = {node["id"]: node for node in layout["nodes"]}
    crossings_nodes = []
    degenerate_edge_segments: list[tuple[str, int]] = []
    endpoint_violations: list[tuple[str, str]] = []
    for edge in layout["edges"]:
        points = [tuple(point) for point in edge["points"]]
        if len(points) < 2:
            endpoint_violations.append((edge["id"], "fewer_than_two_points"))
            continue
        source, target = node_map[edge["source"]], node_map[edge["target"]]
        if not _point_on_box_boundary(points[0], source):
            endpoint_violations.append((edge["id"], "source_anchor_not_on_boundary"))
        if not _point_on_box_boundary(points[-1], target):
            endpoint_violations.append((edge["id"], "target_anchor_not_on_boundary"))
        if _near_endpoint_inside(points[0], points[1], source):
            endpoint_violations.append((edge["id"], "route_enters_source_interior"))
        if _near_endpoint_inside(points[-1], points[-2], target):
            endpoint_violations.append((edge["id"], "route_enters_target_interior"))
        for segment_index, (start, end) in enumerate(zip(points, points[1:])):
            if start == end:
                degenerate_edge_segments.append((edge["id"], segment_index))
            for node_id, node in node_map.items():
                if node_id in {edge["source"], edge["target"]}:
                    continue
                if segment_intersects_box(start, end, (node["x"], node["y"], node["width"], node["height"]), pad=4):
                    crossings_nodes.append((edge["id"], node_id))
    if degenerate_edge_segments:
        errors.append(f"Zero-length edge segments: {degenerate_edge_segments[:8]}")
    if endpoint_violations:
        errors.append(f"Invalid edge endpoints: {endpoint_violations[:8]}")
    if crossings_nodes:
        errors.append(f"Edges cross nodes: {crossings_nodes[:8]}")
    edge_crossings = edge_crossing_count(layout)
    if edge_crossings:
        warnings.append(f"{edge_crossings} edge segment crossings detected")
    for node in layout["nodes"]:
        if node["x"] < 0 or node["y"] < 0 or node["x"] + node["width"] > layout["width"] or node["y"] + node["height"] > layout["height"]:
            errors.append(f"Node outside canvas: {node['id']}")
    aspect = layout["width"] / max(layout["height"], 1)
    if aspect > 3.5 or aspect < 0.32:
        warnings.append(f"Extreme page aspect ratio: {aspect:.2f}")
    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "overlaps": overlaps,
        "edge_node_crossings": crossings_nodes,
        "degenerate_edge_segments": degenerate_edge_segments,
        "endpoint_violations": endpoint_violations,
        "edge_crossings": edge_crossings,
        "aspect_ratio": round(aspect, 4),
    }
