from __future__ import annotations

from typing import Any


def elk_layout_request(ir: dict[str, Any], algorithm: str = "org.eclipse.elk.layered") -> dict[str, Any]:
    return {
        "id": "root",
        "layoutOptions": {
            "elk.algorithm": algorithm,
            "elk.direction": "RIGHT",
            "elk.edgeRouting": "ORTHOGONAL",
            "elk.spacing.nodeNode": "60",
        },
        "children": [
            {"id": node["id"], "width": 200, "height": 76}
            for node in ir["nodes"]
        ],
        "edges": [
            {"id": edge["id"], "sources": [edge["source"]], "targets": [edge["target"]]}
            for edge in ir["edges"]
        ],
    }


def elk_available() -> bool:
    return False
