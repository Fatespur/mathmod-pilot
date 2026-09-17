from __future__ import annotations

from typing import Any

from layout_candidates import candidate_layout_names


def create_diagram_plan(
    ir: dict[str, Any],
    primary_layout: str | None = None,
    alternative_layout: str | None = None,
) -> dict[str, Any]:
    candidates = candidate_layout_names(ir)
    for name in [alternative_layout, primary_layout]:
        if name and name not in candidates:
            candidates.insert(0, name)
    node_count = len(ir["nodes"])
    return {
        "schema_version": "1.0",
        "diagrams": [
            {
                "id": "overall",
                "purpose": "整篇论文总体技术路线图" if len(ir.get("questions", [])) > 1 else "单问建模方法框架图",
                "diagram_type": ir["diagram"]["diagram_type"],
                "node_count": node_count,
                "candidate_layouts": candidates[:10],
                "primary_layout": primary_layout,
                "alternative_layout": alternative_layout,
                "target_width_mm": ir["diagram"]["target_width_mm"],
                "transparent_background": ir["diagram"]["transparent_background"],
                "theme": ir["diagram"]["theme"],
                "suggested_paper_position": "问题分析之后",
                "split_recommendation": ["overall_route", "question_flow", "validation_flow"] if node_count > 24 else [],
            }
        ],
    }
