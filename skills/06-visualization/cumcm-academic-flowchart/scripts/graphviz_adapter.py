from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any

from utils import write_text


def graphviz_available() -> bool:
    return shutil.which("dot") is not None


def generate_dot(ir: dict[str, Any], output: Path, rankdir: str = "LR") -> Path:
    lines = [
        "digraph ModelingFramework {",
        f'  graph [rankdir={rankdir}, splines=ortho, bgcolor="transparent", pad=0.2];',
        '  node [shape=box, style="rounded,filled", fontname="Arial", color="#53657A", fillcolor="#EAF1F7"];',
        '  edge [color="#44546A", arrowsize=0.8];',
    ]
    for node in ir["nodes"]:
        label = (node.get("short_label") or node["label"]).replace('"', '\\"')
        lines.append(f'  "{node["id"]}" [label="{label}"];')
    for edge in ir["edges"]:
        lines.append(f'  "{edge["source"]}" -> "{edge["target"]}";')
    lines.append("}")
    write_text(output, "\n".join(lines) + "\n")
    return output
