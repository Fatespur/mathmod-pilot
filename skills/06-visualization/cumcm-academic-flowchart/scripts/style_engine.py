from __future__ import annotations

from copy import deepcopy
from typing import Any

from utils import load_theme


SEMANTIC_ROLE = {
    "data": "data",
    "input": "data",
    "sample": "data",
    "preprocessing": "processing",
    "data_quality": "processing",
    "normalization": "processing",
    "direction": "processing",
    "feature": "feature",
    "screening": "feature",
    "indicator": "feature",
    "model": "model",
    "equation": "model",
    "mechanism": "model",
    "objective": "decision",
    "constraint": "decision",
    "decision_variable": "decision",
    "solver": "decision",
    "convergence": "validation",
    "validation": "validation",
    "diagnosis": "validation",
    "sensitivity": "validation",
    "metric": "validation",
    "output": "result",
    "prediction": "result",
    "significance": "result",
    "interval": "result",
    "weight": "feature",
    "statistic": "model",
    "identification": "decision",
    "initial_condition": "auxiliary",
    "boundary_condition": "auxiliary",
    "state_variable": "feature",
    "control_variable": "decision",
    "exogenous_variable": "data",
    "parameter": "feature",
}


def apply_theme(layout: dict[str, Any], theme_name: str) -> tuple[dict[str, Any], dict[str, Any]]:
    theme = load_theme(theme_name)
    scene = deepcopy(layout)
    for node in scene["nodes"]:
        role = "model" if node.get("framework_role") == "main_method" else SEMANTIC_ROLE.get(node.get("semantic_type", ""), "auxiliary")
        palette = theme["roles"][role]
        node["style"] = {
            "role": role,
            "fill": palette["fill"],
            "stroke": palette["stroke"],
            "text": palette.get("text", theme["text"]),
            "fill_opacity": theme["opacity"]["core" if node.get("importance") == "primary" else "node"],
            "stroke_opacity": theme["opacity"]["stroke"],
            "stroke_width": 1.5 if node.get("importance") == "primary" else 1.15,
            "font_weight": 700 if node.get("importance") == "primary" else 500,
        }
    for group in scene.get("groups", []):
        opacity_scale = 0.72 if group.get("group_type") == "module" else 1.0
        group["style"] = {
            "fill": theme["group"]["fill"],
            "stroke": theme["group"]["stroke"],
            "text": theme["text"],
            "fill_opacity": theme["opacity"]["group"] * opacity_scale,
            "stroke_opacity": 0.75,
        }
    for edge in scene["edges"]:
        edge["style"] = {
            "stroke": theme["edge"]["feedback" if edge.get("feedback") else "primary" if edge.get("key") else "auxiliary"],
            "stroke_opacity": theme["opacity"]["edge_primary" if edge.get("key") else "edge_auxiliary"],
            "stroke_width": 1.6 if edge.get("key") else 1.1,
            "dash": bool(edge.get("feedback") or not edge.get("key")),
        }
    scene["theme"] = theme["name"]
    scene["background"] = theme.get("background", "#FFFFFF")
    return scene, theme
