from __future__ import annotations

from pathlib import Path
from typing import Any

from color_engine import validate_color
from validate_drawio import validate_drawio
from validate_layout import validate_layout
from validate_png import validate_png
from validate_svg import validate_svg
from validate_typography import validate_typography


def _semantic_review(ir: dict[str, Any]) -> dict[str, Any]:
    errors = []
    warnings = []
    framework_metrics: dict[str, Any] = {}
    semantic_types = {node.get("semantic_type") for node in ir["nodes"]}
    question_types = {question.get("primary_type", "") for question in ir.get("questions", [])}
    required_core_sets = []
    for question_type in question_types:
        if "优化" in question_type:
            required_core_sets.append({"objective", "constraint", "model"})
        elif "预测" in question_type:
            required_core_sets.append({"model", "prediction"})
        elif "评价" in question_type:
            required_core_sets.append({"indicator", "weight", "model"})
        elif "统计" in question_type:
            required_core_sets.append({"descriptive", "hypothesis", "statistic", "significance"})
        elif "机理" in question_type:
            required_core_sets.append({"mechanism", "equation"})
    if required_core_sets:
        if any(not semantic_types & required for required in required_core_sets):
            errors.append("Question-type-specific core modeling step is missing")
    elif not semantic_types & {"model", "equation", "mechanism", "objective", "statistic"}:
        errors.append("Core modeling step is missing")
    if not semantic_types & {"output", "prediction", "result", "significance"}:
        errors.append("Final output is missing")
    if not semantic_types & {"validation", "diagnosis", "sensitivity", "metric"}:
        errors.append("Model validation is missing")
    if any(node.get("inferred") for node in ir["nodes"]):
        warnings.append("IR contains inferred nodes that require human review")
    if any(question.get("primary_type") is None for question in ir.get("questions", [])):
        errors.append("Question type is missing")
    if ir.get("meta", {}).get("framework_mode") == "method_hierarchy":
        for question in ir.get("questions", []):
            question_id = question["question_id"]
            question_nodes = [node for node in ir["nodes"] if node.get("question_id") == question_id]
            node_ids = {node["id"] for node in question_nodes}
            question_edges = [
                edge for edge in ir["edges"]
                if edge["source"] in node_ids and edge["target"] in node_ids and not edge.get("feedback")
            ]
            roles = [node.get("framework_role") for node in question_nodes]
            out_degree = {
                node_id: sum(edge["source"] == node_id for edge in question_edges)
                for node_id in node_ids
            }
            in_degree = {
                node_id: sum(edge["target"] == node_id for edge in question_edges)
                for node_id in node_ids
            }
            branching_nodes = sum(value >= 2 for value in out_degree.values())
            merging_nodes = sum(value >= 2 for value in in_degree.values())
            supporting_nodes = sum(role in {"submethod", "component", "validation"} for role in roles)
            framework_metrics[question_id] = {
                "main_methods": roles.count("main_method"),
                "supporting_nodes": supporting_nodes,
                "branching_nodes": branching_nodes,
                "merging_nodes": merging_nodes,
            }
            if roles.count("main_method") < 1:
                errors.append(f"{question_id}: main modeling method is missing")
            if supporting_nodes < 3:
                errors.append(f"{question_id}: insufficient submethods/components for a method framework")
            stage_count = len({node.get("stage", node.get("level")) for node in question_nodes})
            linearity_ratio = round(
                sum(
                    out_degree[node_id] <= 1 and in_degree[node_id] <= 1
                    for node_id in node_ids
                ) / max(1, len(node_ids)),
                3,
            )
            framework_metrics[question_id].update(
                {
                    "stage_count": stage_count,
                    "linearity_ratio": linearity_ratio,
                }
            )
            if not (branching_nodes and merging_nodes):
                errors.append(f"{question_id}: diagram degenerates into a linear step chain")
            if stage_count < 4:
                errors.append(f"{question_id}: method architecture has insufficient semantic depth")
    return {
        "passed": not errors,
        "errors": errors,
        "warnings": warnings,
        "framework_metrics": framework_metrics,
    }


def review_variant(
    ir: dict[str, Any],
    scene: dict[str, Any],
    theme: dict[str, Any],
    paths: dict[str, Path],
    png_long_edge: int,
    transparent: bool,
    target_width_mm: float,
) -> dict[str, Any]:
    expected_nodes = {node["id"] for node in scene["nodes"]}
    semantic = _semantic_review(ir)
    layout = validate_layout(scene)
    color = validate_color(scene, theme, transparent)
    typography = validate_typography(scene, target_width_mm)
    drawio = validate_drawio(paths["drawio"], expected_nodes)
    svg = validate_svg(paths["svg"], len(expected_nodes))
    png = validate_png(
        paths["png"],
        minimum_long_edge=png_long_edge,
        require_alpha=transparent,
        expected_node_count=len(expected_nodes),
    )
    format_consistency = {
        "node_sets_consistent": expected_nodes.issubset(set(drawio.get("node_ids", []))) and svg.get("node_count") == len(expected_nodes) and png.get("node_count") in {None, len(expected_nodes)},
        "shared_scene_graph": True,
    }
    blockers = []
    if not semantic["passed"]:
        blockers.extend(semantic["errors"])
    if not layout["passed"]:
        blockers.extend(layout["errors"])
    if not drawio["passed"]:
        blockers.extend(drawio["errors"])
    if not svg["passed"]:
        blockers.extend(svg["errors"])
    if not png["passed"]:
        blockers.extend(png["errors"])
    if not transparent and ir["diagram"].get("transparent_background"):
        blockers.append("Transparent background configuration not applied")
    if not format_consistency["node_sets_consistent"]:
        blockers.append("Node sets are inconsistent across formats")
    semantic_score = 25.0 if semantic["passed"] else max(0.0, 25.0 - 6 * len(semantic["errors"]))
    flow_score = 15.0 if layout["passed"] else max(0.0, 15.0 - 4 * len(layout["errors"]))
    layout_score = 15.0 * min(1.0, scene.get("metrics", {}).get("layout_score", 0) / 92.0)
    visual_score = 12.0 if typography["passed"] and all(len(node.get("short_label", "")) <= 14 for node in scene["nodes"]) else 9.0
    color_score = 10.0 if color["passed"] else max(6.0, 10.0 - len(color["issues"]))
    paper_score = 8.0 if typography["passed"] and 0.32 <= layout["aspect_ratio"] <= 3.5 else 6.0
    category_scores = {
        "mathematical_semantics": round(semantic_score, 2),
        "flow_logic": round(flow_score, 2),
        "layout_routing": round(layout_score, 2),
        "visual_hierarchy_compression": round(visual_score, 2),
        "color_transparency": round(color_score, 2),
        "paper_fit": round(paper_score, 2),
        "svg_quality": 5.0 if svg["passed"] else 0.0,
        "png_quality": 5.0 if png["passed"] else 0.0,
        "drawio_editability": 5.0 if drawio["passed"] else 0.0,
    }
    total = round(sum(category_scores.values()), 2)
    return {
        "passed": not blockers,
        "total_score": total,
        "category_scores": category_scores,
        "blocking_errors": blockers,
        "semantic": semantic,
        "layout": layout,
        "color_quality_report": color,
        "typography": typography,
        "drawio": drawio,
        "svg": svg,
        "png": png,
        "format_consistency": format_consistency,
    }


def dual_layout_review(
    primary: dict[str, Any],
    alternative: dict[str, Any],
    *,
    minimum_diversity: float = 0.55,
) -> dict[str, Any]:
    primary_nodes = {node["id"] for node in primary["nodes"]}
    alternative_nodes = {node["id"] for node in alternative["nodes"]}
    primary_edges = {(edge["source"], edge["target"]) for edge in primary["edges"] if edge.get("key")}
    alternative_edges = {(edge["source"], edge["target"]) for edge in alternative["edges"] if edge.get("key")}
    diversity = float(primary.get("layout_diversity_score", 0))
    errors = []
    if primary_nodes != alternative_nodes:
        errors.append("Primary and alternative node sets differ")
    if primary_edges != alternative_edges:
        errors.append("Primary and alternative key-edge sets differ")
    if primary["layout_family"] == alternative["layout_family"]:
        errors.append("Primary and alternative use the same layout family")
    if diversity < minimum_diversity:
        errors.append(f"Layout diversity {diversity:.3f} < {minimum_diversity}")
    return {
        "passed": not errors,
        "errors": errors,
        "node_sets_equal": primary_nodes == alternative_nodes,
        "key_edges_equal": primary_edges == alternative_edges,
        "families": [primary["layout_family"], alternative["layout_family"]],
        "layout_diversity_score": diversity,
    }
