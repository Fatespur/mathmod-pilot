from __future__ import annotations

from pathlib import Path
from typing import Any

from utils import write_text


def generate_mermaid(ir: dict[str, Any], output: Path, direction: str = "LR") -> Path:
    lines = [f"flowchart {direction}"]
    for node in ir["nodes"]:
        label = (node.get("short_label") or node["label"]).replace('"', "'")
        shape = node.get("semantic_type")
        if shape in {"convergence", "assumption_test", "significance"}:
            lines.append(f'  {node["id"]}{{"{label}"}}')
        else:
            lines.append(f'  {node["id"]}["{label}"]')
    for edge in ir["edges"]:
        arrow = "-.->" if edge.get("feedback") else "-->"
        label = f'|"{edge["label"]}"|' if edge.get("label") else ""
        lines.append(f'  {edge["source"]} {arrow}{label} {edge["target"]}')
    lines.extend(
        [
            "  classDef data fill:#D9EAF6,stroke:#2F6FB0,color:#253247",
            "  classDef model fill:#E7E2F6,stroke:#5146A5,color:#253247",
            "  linkStyle default stroke:#44546A,stroke-width:1.5px",
        ]
    )
    write_text(output, "\n".join(lines) + "\n")
    return output
