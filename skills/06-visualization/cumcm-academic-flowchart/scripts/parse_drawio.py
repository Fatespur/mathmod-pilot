from __future__ import annotations

import html
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from utils import stable_id


def _plain_label(value: str) -> str:
    value = html.unescape(value or "")
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.IGNORECASE)
    value = re.sub(r"<[^>]+>", "", value)
    return re.sub(r"\s+", " ", value).strip()


def _semantic_type(label: str, style: str) -> str:
    lowered = label.lower()
    rules = [
        ("output", ("输出", "结果", "方案", "prediction", "output")),
        ("validation", ("验证", "检验", "诊断", "validation", "check")),
        ("objective", ("目标", "objective")),
        ("constraint", ("约束", "constraint")),
        ("solver", ("求解", "算法", "solver", "algorithm")),
        ("data", ("数据", "输入", "data", "input")),
    ]
    for semantic_type, keywords in rules:
        if any(keyword in lowered for keyword in keywords):
            return semantic_type
    if "rhombus" in style:
        return "convergence"
    if "document" in style:
        return "output"
    return "model"


def parse_drawio(path: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Read an uncompressed diagrams.net graph into semantic nodes and edges."""
    warnings: list[str] = []
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        raise ValueError(f"Invalid draw.io XML: {path.name}: {exc}") from exc
    model = root.find(".//mxGraphModel")
    if model is None:
        raise ValueError(
            f"{path.name} does not contain an uncompressed mxGraphModel; "
            "open it in diagrams.net and save with compressed=false"
        )
    cells = model.findall(".//mxCell")
    raw_nodes = [
        cell
        for cell in cells
        if cell.get("vertex") == "1"
        and cell.get("id") not in {"0", "1"}
        and not (cell.get("id") or "").startswith("group_")
        and "container=1" not in (cell.get("style") or "")
        and "verticalAlign=top;spacingTop=" not in (cell.get("style") or "")
    ]
    mapping = {
        cell.get("id", f"cell-{index}"): stable_id("node", path.name, cell.get("id", index))
        for index, cell in enumerate(raw_nodes)
    }
    nodes: list[dict[str, Any]] = []
    for index, cell in enumerate(raw_nodes):
        old_id = cell.get("id", f"cell-{index}")
        label = _plain_label(cell.get("value", "")) or f"节点 {index + 1}"
        semantic_type = _semantic_type(label, cell.get("style", ""))
        nodes.append(
            {
                "id": mapping[old_id],
                "label": label,
                "short_label": label[:14],
                "description": "Imported from editable draw.io source",
                "semantic_type": semantic_type,
                "question_id": "Q1",
                "importance": "primary" if semantic_type in {"model", "objective", "output"} else "secondary",
                "level": index,
                "source_reference": path.name,
                "inferred": False,
            }
        )
    edges: list[dict[str, Any]] = []
    for index, cell in enumerate(cell for cell in cells if cell.get("edge") == "1"):
        source = cell.get("source")
        target = cell.get("target")
        if source not in mapping or target not in mapping:
            warnings.append(f"Skipped edge {cell.get('id', index)} with missing endpoint")
            continue
        label = _plain_label(cell.get("value", ""))
        style = cell.get("style", "")
        edges.append(
            {
                "id": stable_id("edge", path.name, cell.get("id", index)),
                "source": mapping[source],
                "target": mapping[target],
                "edge_type": "feedback" if "dashed=1" in style else "process_flow",
                "label": label,
                "feedback": "dashed=1" in style or any(token in label for token in ("返回", "迭代", "否")),
                "key": "dashed=1" not in style,
            }
        )
    if not nodes:
        raise ValueError(f"No editable vertex nodes found in {path.name}")
    if not edges:
        warnings.append("No valid edges found; the imported graph will be relaid as isolated semantic nodes")
    return nodes, edges, warnings
