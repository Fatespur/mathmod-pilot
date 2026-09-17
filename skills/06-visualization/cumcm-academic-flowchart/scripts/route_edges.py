from __future__ import annotations

from typing import Any

from utils import polyline_length, segment_intersects_box, simplify_polyline


Point = tuple[float, float]
Port = tuple[Point, Point]


def _center(node: dict[str, Any]) -> Point:
    return node["x"] + node["width"] / 2, node["y"] + node["height"] / 2


def _ports(node: dict[str, Any], clearance: float = 24.0) -> list[Port]:
    cx, cy = _center(node)
    left, right = node["x"], node["x"] + node["width"]
    top, bottom = node["y"], node["y"] + node["height"]
    return [
        ((left, cy), (left - clearance, cy)),
        ((right, cy), (right + clearance, cy)),
        ((cx, top), (cx, top - clearance)),
        ((cx, bottom), (cx, bottom + clearance)),
    ]


def _segment_hits_node(
    start: Point,
    end: Point,
    node: dict[str, Any],
    *,
    pad: float = 10.0,
) -> bool:
    return segment_intersects_box(
        start,
        end,
        (node["x"], node["y"], node["width"], node["height"]),
        pad=pad,
    )


def _collisions(
    points: list[Point],
    nodes: dict[str, dict[str, Any]],
    source_id: str,
    target_id: str,
) -> int:
    count = 0
    last_segment = len(points) - 2
    for segment_index, (start, end) in enumerate(zip(points, points[1:])):
        for node_id, node in nodes.items():
            if segment_index == 0 and node_id == source_id:
                continue
            if segment_index == last_segment and node_id == target_id:
                continue
            if _segment_hits_node(start, end, node):
                count += 1
    return count


def _bend_count(points: list[Point]) -> int:
    bends = 0
    for first, middle, last in zip(points, points[1:], points[2:]):
        incoming = (middle[0] - first[0], middle[1] - first[1])
        outgoing = (last[0] - middle[0], last[1] - middle[1])
        if abs(incoming[0] * outgoing[1] - incoming[1] * outgoing[0]) > 1e-9:
            bends += 1
    return bends


def _corridors(nodes: dict[str, dict[str, Any]], clearance: float = 34.0) -> tuple[list[float], list[float]]:
    left = min(node["x"] for node in nodes.values()) - clearance
    right = max(node["x"] + node["width"] for node in nodes.values()) + clearance
    top = min(node["y"] for node in nodes.values()) - clearance
    bottom = max(node["y"] + node["height"] for node in nodes.values()) + clearance
    x_values = [left, right]
    y_values = [top, bottom]
    for node in nodes.values():
        x_values.extend([node["x"] - clearance, node["x"] + node["width"] + clearance])
        y_values.extend([node["y"] - clearance, node["y"] + node["height"] + clearance])
    return sorted(set(x_values)), sorted(set(y_values))


def _between_port_candidates(
    source_escape: Point,
    target_escape: Point,
    x_corridors: list[float],
    y_corridors: list[float],
) -> list[list[Point]]:
    sx, sy = source_escape
    tx, ty = target_escape
    candidates: list[list[Point]] = [
        [source_escape, (tx, sy), target_escape],
        [source_escape, (sx, ty), target_escape],
        [source_escape, ((sx + tx) / 2, sy), ((sx + tx) / 2, ty), target_escape],
        [source_escape, (sx, (sy + ty) / 2), (tx, (sy + ty) / 2), target_escape],
    ]
    for corridor_x in x_corridors:
        candidates.append(
            [source_escape, (corridor_x, sy), (corridor_x, ty), target_escape]
        )
    for corridor_y in y_corridors:
        candidates.append(
            [source_escape, (sx, corridor_y), (tx, corridor_y), target_escape]
        )
    return candidates


def _relevant_corridors(
    values: list[float],
    source_value: float,
    target_value: float,
    *,
    limit: int = 10,
) -> list[float]:
    """Keep useful obstacle corridors without evaluating every node boundary."""
    if len(values) <= limit:
        return values
    low, high = sorted((source_value, target_value))
    midpoint = (source_value + target_value) / 2
    between = [value for value in values if low <= value <= high]
    ranked = sorted(
        values,
        key=lambda value: (
            0 if value in between else 1,
            min(abs(value - source_value), abs(value - target_value), abs(value - midpoint)),
            value,
        ),
    )
    selected = {values[0], values[-1], *ranked[: max(0, limit - 2)]}
    return sorted(selected)


def route_edge(
    edge: dict[str, Any],
    nodes: dict[str, dict[str, Any]],
    layout_name: str,
    corridors: tuple[list[float], list[float]] | None = None,
) -> dict[str, Any]:
    source = nodes[edge["source"]]
    target = nodes[edge["target"]]
    source_center, target_center = _center(source), _center(target)
    x_corridors, y_corridors = corridors or _corridors(nodes)
    candidates: list[list[Point]] = []
    for source_port, source_escape in _ports(source):
        for target_port, target_escape in _ports(target):
            for middle in _between_port_candidates(
                source_escape,
                target_escape,
                _relevant_corridors(x_corridors, source_escape[0], target_escape[0]),
                _relevant_corridors(y_corridors, source_escape[1], target_escape[1]),
            ):
                candidates.append(
                    simplify_polyline(
                        [source_port, source_escape, *middle[1:-1], target_escape, target_port]
                    )
                )
    if edge.get("feedback"):
        feedback_y = min(source["y"], target["y"]) - 64.0
        for source_port, source_escape in _ports(source):
            for target_port, target_escape in _ports(target):
                candidates.append(
                    simplify_polyline(
                        [
                            source_port,
                            source_escape,
                            (source_escape[0], feedback_y),
                            (target_escape[0], feedback_y),
                            target_escape,
                            target_port,
                        ]
                    )
                )
    candidates = [points for points in candidates if len(points) >= 2]
    best = min(
        candidates,
        key=lambda points: (
            _collisions(points, nodes, edge["source"], edge["target"]),
            0 if edge.get("feedback") and min(point[1] for point in points) < min(source["y"], target["y"]) else 1,
            _bend_count(points),
            polyline_length(points),
            abs(points[0][0] - target_center[0]) + abs(points[0][1] - target_center[1]),
            abs(points[-1][0] - source_center[0]) + abs(points[-1][1] - source_center[1]),
        ),
    )
    result = dict(edge)
    result["points"] = [[round(x, 3), round(y, 3)] for x, y in best]
    result["route_type"] = "orthogonal_obstacle_aware"
    result["route_collisions"] = _collisions(best, nodes, edge["source"], edge["target"])
    return result


def route_all_edges(
    edges: list[dict[str, Any]],
    nodes: dict[str, dict[str, Any]],
    layout_name: str,
) -> list[dict[str, Any]]:
    corridors = _corridors(nodes)
    return [route_edge(edge, nodes, layout_name, corridors) for edge in edges]
