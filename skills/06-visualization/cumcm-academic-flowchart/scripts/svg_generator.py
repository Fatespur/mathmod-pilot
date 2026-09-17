from __future__ import annotations

import html
import math
import os
import re
from pathlib import Path
from typing import Any

from utils import shorten_polyline_end, write_text


FONT_STACK = "'Microsoft YaHei','Noto Sans CJK SC','Source Han Sans SC','SimHei',Arial,sans-serif"
FONT_PATHS = [
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "msyh.ttc",
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "simhei.ttf",
    Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf",
]


def _esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def _wrap(label: str, max_chars: int = 8) -> list[str]:
    value = label.strip()
    if len(re.findall(r"[A-Za-z0-9²()/-]", value)) >= 3:
        max_chars = max(max_chars, 12)
    if len(value) <= max_chars:
        return [value]
    lines = [value[index : index + max_chars] for index in range(0, len(value), max_chars)]
    return lines[:3]


def _shape(node: dict[str, Any]) -> str:
    x, y, width, height = node["x"], node["y"], node["width"], node["height"]
    style = node["style"]
    common = (
        f'fill="{style["fill"]}" fill-opacity="{style["fill_opacity"]}" '
        f'stroke="{style["stroke"]}" stroke-opacity="{style["stroke_opacity"]}" '
        f'stroke-width="{style["stroke_width"]}" vector-effect="non-scaling-stroke"'
    )
    shape = node.get("shape", "roundrect")
    if shape == "diamond":
        points = f"{x + width / 2},{y} {x + width},{y + height / 2} {x + width / 2},{y + height} {x},{y + height / 2}"
        return f'<polygon points="{points}" {common}/>'
    if shape == "hexagon":
        inset = width * 0.16
        points = f"{x + inset},{y} {x + width - inset},{y} {x + width},{y + height/2} {x + width-inset},{y+height} {x+inset},{y+height} {x},{y+height/2}"
        return f'<polygon points="{points}" {common}/>'
    if shape == "data":
        inset = width * 0.12
        points = f"{x + inset},{y} {x + width},{y} {x + width-inset},{y+height} {x},{y+height}"
        return f'<polygon points="{points}" {common}/>'
    if shape == "ellipse":
        return f'<ellipse cx="{x + width/2}" cy="{y + height/2}" rx="{width/2}" ry="{height/2}" {common}/>'
    if shape == "document":
        fold = min(24, height * 0.25)
        path = f"M{x},{y} H{x+width-fold} L{x+width},{y+fold} V{y+height-fold/2} Q{x+width*0.75},{y+height+fold/2} {x+width*0.5},{y+height} Q{x+width*0.25},{y+height-fold/2} {x},{y+height} Z"
        return f'<path d="{path}" {common}/>'
    if shape == "cylinder":
        ry = min(18, height * 0.22)
        return (
            f'<path d="M{x},{y+ry} Q{x},{y} {x+width/2},{y} Q{x+width},{y} {x+width},{y+ry} '
            f'V{y+height-ry} Q{x+width},{y+height} {x+width/2},{y+height} Q{x},{y+height} {x},{y+height-ry} Z" {common}/>'
            f'<ellipse cx="{x+width/2}" cy="{y+ry}" rx="{width/2}" ry="{ry}" fill="none" stroke="{style["stroke"]}" stroke-opacity="{style["stroke_opacity"]}" stroke-width="{style["stroke_width"]}"/>'
        )
    extra = ' stroke-dasharray="5 3"' if shape == "core" else ""
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="16" ry="16" {common}{extra}/>'


def _path_text(
    value: str,
    x: float,
    y: float,
    font_size: float,
    fill: str,
    *,
    anchor: str = "middle",
    weight: int = 500,
) -> str:
    try:
        from matplotlib.font_manager import FontProperties
        from matplotlib.path import Path as MplPath
        from matplotlib.textpath import TextPath
    except ImportError as exc:
        raise RuntimeError("SVG path text mode requires matplotlib") from exc
    font_path = next((path for path in FONT_PATHS if path.exists()), None)
    prop = FontProperties(fname=str(font_path), weight=weight) if font_path else FontProperties(family="sans-serif", weight=weight)
    glyphs = TextPath((0, 0), value, size=font_size, prop=prop)
    bounds = glyphs.get_extents()
    if anchor == "middle":
        shift_x = x - (bounds.xmin + bounds.xmax) / 2
    elif anchor == "end":
        shift_x = x - bounds.xmax
    else:
        shift_x = x - bounds.xmin
    glyph_center_y = (bounds.ymin + bounds.ymax) / 2
    vertices = glyphs.vertices
    codes = glyphs.codes
    commands: list[str] = []
    index = 0
    while index < len(codes):
        code = codes[index]
        vx, vy = vertices[index]
        px, py = vx + shift_x, y - (vy - glyph_center_y)
        if code == MplPath.MOVETO:
            commands.append(f"M{px:.3f},{py:.3f}")
        elif code == MplPath.LINETO:
            commands.append(f"L{px:.3f},{py:.3f}")
        elif code == MplPath.CURVE3 and index + 1 < len(codes):
            ex, ey = vertices[index + 1]
            commands.append(
                f"Q{px:.3f},{py:.3f} {ex + shift_x:.3f},{y - (ey - glyph_center_y):.3f}"
            )
            index += 1
        elif code == MplPath.CURVE4 and index + 2 < len(codes):
            c2x, c2y = vertices[index + 1]
            ex, ey = vertices[index + 2]
            commands.append(
                f"C{px:.3f},{py:.3f} {c2x + shift_x:.3f},{y - (c2y - glyph_center_y):.3f} "
                f"{ex + shift_x:.3f},{y - (ey - glyph_center_y):.3f}"
            )
            index += 2
        elif code == MplPath.CLOSEPOLY:
            commands.append("Z")
        index += 1
    return (
        f'<path data-text="{_esc(value)}" d="{" ".join(commands)}" '
        f'fill="{fill}" fill-rule="nonzero"/>'
    )


def _single_text(
    value: str,
    x: float,
    y: float,
    font_size: float,
    fill: str,
    *,
    text_mode: str,
    anchor: str = "middle",
    weight: int = 500,
) -> str:
    if text_mode == "path":
        return _path_text(value, x, y, font_size, fill, anchor=anchor, weight=weight)
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" dominant-baseline="middle" '
        f'font-family="{FONT_STACK}" font-size="{font_size:.2f}" font-weight="{weight}" '
        f'fill="{fill}">{_esc(value)}</text>'
    )


def _text(node: dict[str, Any], font_size: float, text_mode: str) -> str:
    shape = node.get("shape", "roundrect")
    lines = _wrap(
        node.get("short_label") or node["label"],
        4 if shape == "diamond" else 6 if shape in {"hexagon", "data"} else 8,
    )
    line_height = font_size * 1.22
    center_x = node["x"] + node["width"] / 2
    start_y = node["y"] + node["height"] / 2 - (len(lines) - 1) * line_height / 2
    style = node["style"]
    if text_mode == "path":
        return "".join(
            _path_text(
                line,
                center_x,
                start_y + index * line_height,
                font_size,
                style["text"],
                weight=style["font_weight"],
            )
            for index, line in enumerate(lines)
        )
    tspans = "".join(
        f'<tspan x="{center_x}" y="{start_y + index * line_height}">{_esc(line)}</tspan>'
        for index, line in enumerate(lines)
    )
    return (
        f'<text text-anchor="middle" dominant-baseline="middle" font-family="{FONT_STACK}" '
        f'font-size="{font_size:.2f}" font-weight="{style["font_weight"]}" fill="{style["text"]}">{tspans}</text>'
    )


def generate_svg(
    scene: dict[str, Any],
    output: Path,
    title: str,
    *,
    transparent: bool = True,
    target_width_mm: float = 160,
    text_mode: str = "text",
) -> Path:
    width, height = scene["width"], scene["height"]
    font_size = min(30.0, max(15.0, width / max(target_width_mm, 1) * 3.45))
    edge_font_size = min(24.0, max(13.0, width / max(target_width_mm, 1) * 2.75))
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" version="1.1" width="{target_width_mm}mm" '
        f'height="{target_width_mm * height / width:.3f}mm" viewBox="0 0 {width} {height}" '
        f'data-node-count="{len(scene["nodes"])}" data-edge-count="{len(scene["edges"])}">',
        f"<title>{_esc(title)}</title>",
        f'<metadata>{{"generator":"cumcm-academic-flowchart","layout":"{_esc(scene["layout_name"])}","text_mode":"{_esc(text_mode)}"}}</metadata>',
        "<defs>",
        '<marker id="arrow" markerWidth="10" markerHeight="8" refX="10" refY="4" orient="auto" markerUnits="strokeWidth"><path d="M0,0 L10,4 L0,8 Z" fill="context-stroke"/></marker>',
        '<linearGradient id="coreGradient" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.18"/><stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/></linearGradient>',
        "</defs>",
    ]
    if not transparent:
        parts.append(f'<rect width="{width}" height="{height}" fill="{scene.get("background", "#FFFFFF")}"/>')
    for group in scene.get("groups", []):
        style = group["style"]
        group_label = _single_text(
            group.get("label", ""),
            group["x"] + 18,
            group["y"] + 28,
            font_size * 0.9,
            style["text"],
            text_mode=text_mode,
            anchor="start",
            weight=700,
        )
        parts.append(
            f'<g id="{_esc(group["id"])}"><rect x="{group["x"]}" y="{group["y"]}" width="{group["width"]}" height="{group["height"]}" rx="22" '
            f'fill="{style["fill"]}" fill-opacity="{style["fill_opacity"]}" stroke="{style["stroke"]}" '
            f'stroke-opacity="{style["stroke_opacity"]}" stroke-dasharray="8 6"/>{group_label}</g>'
        )
    for header in scene.get("headers", []):
        parts.append(_single_text(
            header["label"], header["x"], header["y"], font_size * 1.08,
            header.get("color", "#1F2937"), text_mode=text_mode, weight=700,
        ))
    for edge in scene["edges"]:
        style = edge["style"]
        visual_points = shorten_polyline_end(
            [(float(x), float(y)) for x, y in edge["points"]],
            gap=max(5.0, style["stroke_width"] * 2.5),
        )
        points = " ".join(f"{x:.3f},{y:.3f}" for x, y in visual_points)
        dash = ' stroke-dasharray="10 7"' if style["dash"] else ""
        parts.append(
            f'<polyline id="{_esc(edge["id"])}" points="{points}" fill="none" stroke="{style["stroke"]}" '
            f'stroke-opacity="{style["stroke_opacity"]}" stroke-width="{style["stroke_width"]}" '
            f'stroke-linejoin="round" stroke-linecap="round" marker-end="url(#arrow)" vector-effect="non-scaling-stroke"{dash}/>'
        )
        if edge.get("label"):
            mid = edge["points"][len(edge["points"]) // 2]
            parts.append(_single_text(
                edge["label"], mid[0] + 6, mid[1] - 7, edge_font_size,
                style["stroke"], text_mode=text_mode, anchor="start",
            ))
    for node in scene["nodes"]:
        parts.append(f'<g id="{_esc(node["id"])}" data-semantic-type="{_esc(node.get("semantic_type",""))}">')
        parts.append(_shape(node))
        if node.get("importance") == "primary":
            parts.append(
                f'<rect x="{node["x"]+4}" y="{node["y"]+4}" width="{node["width"]-8}" height="{node["height"]-8}" rx="13" fill="url(#coreGradient)" pointer-events="none"/>'
            )
        parts.append(_text(node, font_size, text_mode))
        parts.append("</g>")
    parts.append("</svg>")
    write_text(output, "\n".join(parts) + "\n")
    return output
