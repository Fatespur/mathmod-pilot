from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = SKILL_ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from utils import stable_id


TYPE_CORES = {
    "优化类": ["data", "objective", "constraint", "model", "solver", "validation", "output"],
    "预测类": ["data", "preprocessing", "feature", "model", "prediction", "metric", "validation"],
    "评价类": ["data", "indicator", "weight", "model", "output", "validation"],
    "数理统计类": ["sample", "descriptive", "hypothesis", "statistic", "significance", "diagnosis", "output"],
    "机理分析类": ["boundary", "state_variable", "mechanism", "equation", "solver", "validation", "output"],
}


def make_ir(question_type: str = "优化类", *, feedback: bool = False, multi: bool = False) -> dict:
    semantic_types = TYPE_CORES[question_type]
    nodes = []
    for index, semantic_type in enumerate(semantic_types):
        question_id = "Q1" if not multi or index < len(semantic_types) // 2 else "Q2"
        nodes.append(
            {
                "id": stable_id("test-node", question_type, index),
                "label": f"步骤{index + 1}：{semantic_type}",
                "short_label": f"步骤{index + 1}",
                "description": "",
                "semantic_type": semantic_type,
                "question_id": question_id,
                "importance": "primary" if semantic_type in {"model", "objective", "equation", "statistic"} else "secondary",
                "level": index,
                "source_reference": "test.md",
                "inferred": False,
            }
        )
    edges = []
    for index in range(len(nodes) - 1):
        edges.append(
            {
                "id": stable_id("test-edge", question_type, index),
                "source": nodes[index]["id"],
                "target": nodes[index + 1]["id"],
                "edge_type": "process_flow",
                "label": "",
                "feedback": False,
                "key": True,
            }
        )
    if feedback:
        edges.append(
            {
                "id": stable_id("test-feedback", question_type),
                "source": nodes[-2]["id"],
                "target": nodes[1]["id"],
                "edge_type": "feedback",
                "label": "未通过",
                "feedback": True,
                "key": False,
            }
        )
    question_ids = ["Q1", "Q2"] if multi else ["Q1"]
    groups = [
        {
            "id": stable_id("test-group", question_id),
            "label": question_id,
            "question_id": question_id,
            "node_ids": [node["id"] for node in nodes if node["question_id"] == question_id],
        }
        for question_id in question_ids
    ]
    questions = [
        {
            "question_id": question_id,
            "primary_type": question_type,
            "confidence": 0.95,
            "goal": "测试",
            "inputs": [],
            "outputs": [],
            "auxiliary_methods": [],
            "reason": "测试",
            "uncertainties": [],
        }
        for question_id in question_ids
    ]
    return {
        "schema_version": "1.0",
        "meta": {
            "title": "测试建模框架",
            "language": "zh-CN",
            "competition": "CUMCM",
            "source_files": ["test.md"],
            "contest_mode": True,
            "ai_generated": True,
            "identity_redacted": True,
        },
        "questions": questions,
        "diagram": {
            "diagram_type": "auto",
            "purpose": "paper_method_overview",
            "target_width_mm": 160,
            "target_height_mm": None,
            "transparent_background": True,
            "theme": "journal-rich",
            "variants": 2,
        },
        "groups": groups,
        "nodes": nodes,
        "edges": edges,
        "code_signals": {},
        "warnings": [],
    }
