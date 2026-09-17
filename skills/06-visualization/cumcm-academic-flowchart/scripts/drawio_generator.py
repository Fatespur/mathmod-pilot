from __future__ import annotations

import datetime as dt
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

from utils import write_text


SHAPE_STYLE = {
    "roundrect": "rounded=1;whiteSpace=wrap;html=0;",
    "data": "shape=parallelogram;perimeter=parallelogramPerimeter;whiteSpace=wrap;html=0;",
    "diamond": "rhombus;whiteSpace=wrap;html=0;",
    "hexagon": "shape=hexagon;perimeter=hexagonPerimeter2;whiteSpace=wrap;html=0;",
    "core": "rounded=1;double=1;whiteSpace=wrap;html=0;",
    "document": "shape=document;whiteSpace=wrap;html=0;",
    "ellipse": "ellipse;whiteSpace=wrap;html=0;",
    "cylinder": "shape=cylinder3;whiteSpace=wrap;html=0;",
}


def _style(node: dict[str, Any]) -> str:
    style = node["style"]
    base = SHAPE_STYLE.get(node.get("shape", "roundrect"), SHAPE_STYLE["roundrect"])
    return (
        base
        + f"fillColor={style['fill']};strokeColor={style['stroke']};fontColor={style['text']};"
        + f"fillOpacity={round(style['fill_opacity'] * 100)};strokeOpacity={round(style['stroke_opacity'] * 100)};"
        + f"strokeWidth={style['stroke_width']};fontSize=14;fontStyle={1 if style['font_weight'] >= 700 else 0};"
        + "fontFamily=Microsoft YaHei;align=center;verticalAlign=middle;spacing=8;"
    )


def generate_drawio(scene: dict[str, Any], output: Path, title: str) -> Path:
    mxfile = ET.Element(
        "mxfile",
        {
            "host": "app.diagrams.net",
            "modified": dt.datetime.now(dt.timezone.utc).isoformat(),
            "agent": "cumcm-academic-flowchart",
            "version": "24.7.17",
            "type": "device",
            "compressed": "false",
        },
    )
    diagram = ET.SubElement(mxfile, "diagram", {"id": scene["layout_name"], "name": title})
    model = ET.SubElement(
        diagram,
        "mxGraphModel",
        {
            "dx": "0",
            "dy": "0",
            "grid": "1",
            "gridSize": "10",
            "guides": "1",
            "tooltips": "1",
            "connect": "1",
            "arrows": "1",
            "fold": "1",
            "page": "1",
            "pageScale": "1",
            "pageWidth": str(round(scene["width"])),
            "pageHeight": str(round(scene["height"])),
            "math": "0",
            "shadow": "0",
        },
    )
    root = ET.SubElement(model, "root")
    ET.SubElement(root, "mxCell", {"id": "0"})
    ET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
    for group in scene.get("groups", []):
        style = group["style"]
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": group["id"],
                "value": group.get("label", ""),
                "style": (
                    "rounded=1;whiteSpace=wrap;html=0;dashed=1;verticalAlign=top;spacingTop=8;"
                    f"fillColor={style['fill']};strokeColor={style['stroke']};fontColor={style['text']};"
                    f"fillOpacity={round(style['fill_opacity'] * 100)};strokeOpacity={round(style['stroke_opacity'] * 100)};"
                    "fontSize=14;fontStyle=1;"
                ),
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": str(group["x"]),
                "y": str(group["y"]),
                "width": str(group["width"]),
                "height": str(group["height"]),
                "as": "geometry",
            },
        )
    for node in scene["nodes"]:
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": node["id"],
                "value": node.get("short_label") or node["label"],
                "style": _style(node),
                "vertex": "1",
                "parent": "1",
            },
        )
        ET.SubElement(
            cell,
            "mxGeometry",
            {
                "x": str(node["x"]),
                "y": str(node["y"]),
                "width": str(node["width"]),
                "height": str(node["height"]),
                "as": "geometry",
            },
        )
    for edge in scene["edges"]:
        style = edge["style"]
        edge_style = (
            "edgeStyle=orthogonalEdgeStyle;rounded=1;orthogonalLoop=1;jettySize=auto;html=0;"
            "sourcePerimeterSpacing=2;targetPerimeterSpacing=6;"
            f"strokeColor={style['stroke']};strokeOpacity={round(style['stroke_opacity'] * 100)};"
            f"strokeWidth={style['stroke_width']};endArrow=block;endFill=1;"
            + ("dashed=1;" if style["dash"] else "")
        )
        cell = ET.SubElement(
            root,
            "mxCell",
            {
                "id": edge["id"],
                "value": edge.get("label", ""),
                "style": edge_style,
                "edge": "1",
                "parent": "1",
                "source": edge["source"],
                "target": edge["target"],
            },
        )
        geometry = ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
        points = edge.get("points", [])[1:-1]
        if points:
            array = ET.SubElement(geometry, "Array", {"as": "points"})
            for x, y in points:
                ET.SubElement(array, "mxPoint", {"x": str(x), "y": str(y)})
    ET.indent(mxfile, space="  ")
    xml = '<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(mxfile, encoding="unicode")
    write_text(output, xml)
    return output
