from __future__ import annotations

import math
from typing import Any

from layout_geometry import layout_family
from layout_scoring import score_layout


def _normalized_positions(layout: dict[str, Any]) -> dict[str, tuple[float, float]]:
    return {
        node["id"]: (
            (node["x"] + node["width"] / 2) / max(layout["width"], 1),
            (node["y"] + node["height"] / 2) / max(layout["height"], 1),
        )
        for node in layout["nodes"]
    }


def layout_diversity_score(primary: dict[str, Any], alternative: dict[str, Any]) -> float:
    left, right = _normalized_positions(primary), _normalized_positions(alternative)
    common = sorted(set(left) & set(right))
    displacement = sum(math.dist(left[node_id], right[node_id]) for node_id in common) / max(1, len(common))
    family_difference = 0.62 if layout_family(primary["layout_name"]) != layout_family(alternative["layout_name"]) else 0.12
    aspect_difference = min(
        0.15,
        abs(primary["width"] / max(primary["height"], 1) - alternative["width"] / max(alternative["height"], 1)) * 0.06,
    )
    return round(min(1.0, family_difference + min(0.28, displacement * 0.45) + aspect_difference), 4)


def select_layouts(
    candidates: list[dict[str, Any]],
    *,
    primary_name: str | None = None,
    alternative_name: str | None = None,
    minimum_diversity: float = 0.55,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    for candidate in candidates:
        score_layout(candidate)
    ranked = sorted(candidates, key=lambda candidate: candidate["metrics"]["layout_score"], reverse=True)
    primary = next((candidate for candidate in ranked if candidate["layout_name"] == primary_name), ranked[0])
    alternative = None
    if alternative_name:
        alternative = next((candidate for candidate in ranked if candidate["layout_name"] == alternative_name), None)
    if alternative is None:
        for candidate in ranked:
            if candidate is primary:
                continue
            if layout_diversity_score(primary, candidate) >= minimum_diversity:
                alternative = candidate
                break
    if alternative is None:
        alternative = next(candidate for candidate in ranked if candidate is not primary)
    diversity = layout_diversity_score(primary, alternative)
    primary["role"] = "primary"
    alternative["role"] = "alternative"
    primary["layout_diversity_score"] = diversity
    alternative["layout_diversity_score"] = diversity
    return primary, alternative, ranked
