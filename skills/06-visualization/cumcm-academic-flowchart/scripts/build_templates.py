from __future__ import annotations

import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from drawio_generator import generate_drawio
from layout_candidates import build_layout
from method_framework import build_method_framework
from style_engine import apply_theme
from utils import stable_id


TEMPLATES = {
    "method-framework.drawio": "method_framework",
    "hierarchical-tree.drawio": "hierarchical_tree",
    "dual-stream.drawio": "dual_stream",
    "swimlane.drawio": "question_swimlane",
    "hub-spoke.drawio": "hub_spoke",
    "concentric.drawio": "concentric",
    "rectangular-loop.drawio": "rectangular_loop",
    "u-shaped.drawio": "u_shaped",
    "matrix.drawio": "matrix",
    "layered-architecture.drawio": "layered_architecture",
    "split-merge.drawio": "split_merge",
    "circular-cycle.drawio": "circular_cycle",
}


def template_ir() -> dict:
    question = {
        "question_id": "Q1",
        "primary_type": "优化类",
        "confidence": 0.95,
    }
    nodes, edges, _ = build_method_framework(
        question,
        "定义决策变量、目标函数和约束，建立混合整数规划模型，结合遗传算法求解并开展可行性与敏感性检验。",
        "template",
    )
    module_labels = {
        "formulation": "模型定义",
        "modeling": "核心方法",
        "solution": "求解策略",
        "validation": "模型检验",
        "result": "结果输出",
    }
    groups = []
    for module, label in module_labels.items():
        node_ids = [node["id"] for node in nodes if node.get("module") == module]
        if len(node_ids) >= 2:
            groups.append(
                {
                    "id": stable_id("template-group", module),
                    "label": label,
                    "group_type": "module",
                    "node_ids": node_ids,
                }
            )
    return {
        "nodes": nodes,
        "edges": edges,
        "groups": groups,
    }


def main() -> int:
    output_dir = SCRIPT_DIR.parent / "assets" / "templates"
    output_dir.mkdir(parents=True, exist_ok=True)
    ir = template_ir()
    for filename, layout_name in TEMPLATES.items():
        layout = build_layout(ir, layout_name, seed=42)
        scene, _ = apply_theme(layout, "journal-rich")
        generate_drawio(scene, output_dir / filename, f"{layout_name} editable template")
    print(f"Generated {len(TEMPLATES)} editable draw.io templates in {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
