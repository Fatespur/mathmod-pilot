from __future__ import annotations

from copy import deepcopy
from typing import Any

from utils import stable_id


def normalize_ir(ir: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(ir)
    seen_nodes: set[str] = set()
    for index, node in enumerate(result.get("nodes", [])):
        if not node.get("id") or node["id"] in seen_nodes:
            node["id"] = stable_id("node", node.get("question_id", "Q"), node.get("label", ""), index)
        seen_nodes.add(node["id"])
        node.setdefault("short_label", node.get("label", "")[:14])
        node.setdefault("semantic_type", "process")
        node.setdefault("importance", "secondary")
        node.setdefault("stage", node.get("level", index))
        node.setdefault(
            "framework_role",
            "main_method" if node.get("importance") == "primary" and node.get("semantic_type") in {"model", "equation", "mechanism"} else "component",
        )
        node.setdefault("module", "modeling" if node.get("framework_role") == "main_method" else "process")
        node.setdefault("branch", "main")
        node.setdefault("parent_id", None)
        node.setdefault("inferred", False)
        node.setdefault("source_reference", "")
    seen_edges: set[str] = set()
    for index, edge in enumerate(result.get("edges", [])):
        if not edge.get("id") or edge["id"] in seen_edges:
            edge["id"] = stable_id("edge", edge.get("source", ""), edge.get("target", ""), index)
        seen_edges.add(edge["id"])
        edge.setdefault("edge_type", "process_flow")
        edge.setdefault("label", "")
        edge.setdefault("feedback", False)
        edge.setdefault("key", True)
    return result
