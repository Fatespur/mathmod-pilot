from __future__ import annotations

import math
import os
import re
from pathlib import Path
from typing import Any

from utils import hex_rgb, shorten_polyline_end


FONT_CANDIDATES = [
    ("Microsoft YaHei", Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "msyh.ttc"),
    ("Noto Sans CJK SC", Path("C:/Windows/Fonts/NotoSansCJK-Regular.ttc")),
    ("Source Han Sans SC", Path("C:/Windows/Fonts/SourceHanSansSC-Regular.otf")),
    ("SimHei", Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "simhei.ttf"),
    ("Arial", Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / "arial.ttf"),
]


def detect_font(size: int) -> tuple[Any, str, list[str]]:
    try:
        from PIL import ImageFont
    except ImportError as exc:
        raise RuntimeError("PNG rendering requires Pillow") from exc
    warnings = []
    for name, path in FONT_CANDIDATES:
        if path.exists():
            try:
                return ImageFont.truetype(str(path), size=size), name, warnings
            except OSError:
                warnings.append(f"Font exists but could not be loaded: {path.name}")
    warnings.append("No preferred CJK font found; Pillow default font may not render Chinese")
    return ImageFont.load_default(size=max(10, size)), "Pillow default", warnings


def _rgba(color: str, opacity: float = 1.0) -> tuple[int, int, int, int]:
    return (*hex_rgb(color), max(0, min(255, round(opacity * 255))))


def _polygon_for(node: dict[str, Any], scale: float) -> list[tuple[int, int]]:
    x, y, width, height = (node[key] * scale for key in ("x", "y", "width", "height"))
    shape = node.get("shape")
    if shape == "diamond":
        return [(round(x + width / 2), round(y)), (round(x + width), round(y + height / 2)), (round(x + width / 2), round(y + height)), (round(x), round(y + height / 2))]
    if shape == "hexagon":
        inset = width * 0.16
        return [(round(x + inset), round(y)), (round(x + width - inset), round(y)), (round(x + width), round(y + height / 2)), (round(x + width - inset), round(y + height)), (round(x + inset), round(y + height)), (round(x), round(y + height / 2))]
    inset = width * 0.12
    return [(round(x + inset), round(y)), (round(x + width), round(y)), (round(x + width - inset), round(y + height)), (round(x), round(y + height))]


def _draw_arrow(draw: Any, points: list[tuple[int, int]], fill: tuple[int, int, int, int], width: int) -> None:
    draw.line(points, fill=fill, width=width, joint="curve")
    if len(points) < 2:
        return
    start, end = points[-2], points[-1]
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    length = max(10, width * 4)
    left = (round(end[0] - length * math.cos(angle - math.pi / 6)), round(end[1] - length * math.sin(angle - math.pi / 6)))
    right = (round(end[0] - length * math.cos(angle + math.pi / 6)), round(end[1] - length * math.sin(angle + math.pi / 6)))
    draw.polygon([end, left, right], fill=fill)


def _wrap(label: str, max_chars: int = 8) -> list[str]:
    value = label.strip()
    if len(re.findall(r"[A-Za-z0-9²()/-]", value)) >= 3:
        max_chars = max(max_chars, 12)
    return [value[index : index + max_chars] for index in range(0, len(value), max_chars)][:3] or [""]


def render_png(
    scene: dict[str, Any],
    output: Path,
    *,
    long_edge: int = 4800,
    dpi: int = 300,
    transparent: bool = True,
    target_width_mm: float = 160,
) -> dict[str, Any]:
    try:
        from PIL import Image, ImageDraw, PngImagePlugin
    except ImportError as exc:
        raise RuntimeError("PNG rendering requires Pillow; install Pillow>=10") from exc
    if long_edge < 3200:
        raise ValueError("PNG long edge must be at least 3200 px")
    scale = long_edge / max(scene["width"], scene["height"])
    image_size = (max(1, round(scene["width"] * scale)), max(1, round(scene["height"] * scale)))
    background = (0, 0, 0, 0) if transparent else _rgba(scene.get("background", "#FFFFFF"), 1)
    image = Image.new("RGBA", image_size, background)
    draw = ImageDraw.Draw(image, "RGBA")
    font_user_units = min(30.0, max(15.0, scene["width"] / max(target_width_mm, 1) * 3.45))
    font_size = max(12, round(font_user_units * scale))
    edge_font_size = max(10, round(font_size * 0.82))
    font, font_name, font_warnings = detect_font(font_size)
    edge_font, _, _ = detect_font(edge_font_size)
    for group in scene.get("groups", []):
        style = group["style"]
        box = tuple(round(group[key] * scale) for key in ("x", "y", "width", "height"))
        xy = (box[0], box[1], box[0] + box[2], box[1] + box[3])
        draw.rounded_rectangle(
            xy,
            radius=max(8, round(22 * scale)),
            fill=_rgba(style["fill"], style["fill_opacity"]),
            outline=_rgba(style["stroke"], style["stroke_opacity"]),
            width=max(1, round(scale)),
        )
        if group.get("label"):
            group_font, _, _ = detect_font(max(10, round(font_size * 0.88)))
            draw.text(
                (box[0] + round(18 * scale), box[1] + round(12 * scale)),
                group["label"],
                font=group_font,
                fill=_rgba(style["text"], 1),
            )
    for header in scene.get("headers", []):
        header_font, _, _ = detect_font(max(12, round(font_size * 1.08)))
        bbox = draw.textbbox((0, 0), header["label"], font=header_font)
        text_width = bbox[2] - bbox[0]
        draw.text(
            (round(header["x"] * scale - text_width / 2), round(header["y"] * scale)),
            header["label"],
            font=header_font,
            fill=_rgba(header.get("color", "#1F2937"), 1),
        )
    for edge in scene["edges"]:
        style = edge["style"]
        visual_points = shorten_polyline_end(
            [(float(x), float(y)) for x, y in edge["points"]],
            gap=max(5.0, style["stroke_width"] * 2.5),
        )
        points = [(round(x * scale), round(y * scale)) for x, y in visual_points]
        _draw_arrow(
            draw,
            points,
            _rgba(style["stroke"], style["stroke_opacity"]),
            max(2, round(style["stroke_width"] * scale)),
        )
        if edge.get("label"):
            mid = points[len(points) // 2]
            draw.text((mid[0] + 5, mid[1] - edge_font_size), edge["label"], font=edge_font, fill=_rgba(style["stroke"], 1))
    for node in scene["nodes"]:
        style = node["style"]
        x, y, width, height = (round(node[key] * scale) for key in ("x", "y", "width", "height"))
        xy = (x, y, x + width, y + height)
        fill = _rgba(style["fill"], style["fill_opacity"])
        outline = _rgba(style["stroke"], style["stroke_opacity"])
        stroke_width = max(2, round(style["stroke_width"] * scale))
        shape = node.get("shape", "roundrect")
        if shape in {"diamond", "hexagon", "data"}:
            draw.polygon(_polygon_for(node, scale), fill=fill, outline=outline, width=stroke_width)
        elif shape == "ellipse":
            draw.ellipse(xy, fill=fill, outline=outline, width=stroke_width)
        elif shape == "document":
            points = [(x, y), (x + width - 24, y), (x + width, y + 24), (x + width, y + height), (x, y + height)]
            draw.polygon(points, fill=fill, outline=outline)
        elif shape == "cylinder":
            draw.rounded_rectangle(xy, radius=max(8, round(height * 0.18)), fill=fill, outline=outline, width=stroke_width)
            draw.ellipse((x, y, x + width, y + round(height * 0.34)), outline=outline, width=stroke_width)
        else:
            draw.rounded_rectangle(
                xy,
                radius=max(8, round(16 * scale)),
                fill=fill,
                outline=outline,
                width=stroke_width,
            )
            if shape == "core":
                inset = max(3, round(4 * scale))
                draw.rounded_rectangle(
                    (x + inset, y + inset, x + width - inset, y + height - inset),
                    radius=max(6, round(13 * scale)),
                    outline=outline,
                    width=max(1, stroke_width // 2),
                )
        label = node.get("short_label") or node["label"]
        lines = _wrap(label, 4 if shape == "diamond" else 6 if shape in {"hexagon", "data"} else 8)
        line_height = font_size * 1.18
        start_y = y + height / 2 - len(lines) * line_height / 2
        for index, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(
                (x + width / 2 - text_width / 2, start_y + index * line_height),
                line,
                font=font,
                fill=_rgba(style["text"], 1),
            )
    if not transparent:
        opaque_background = Image.new("RGBA", image_size, _rgba(scene.get("background", "#FFFFFF"), 1))
        image = Image.alpha_composite(opaque_background, image)
    output.parent.mkdir(parents=True, exist_ok=True)
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("generator", "cumcm-academic-flowchart")
    metadata.add_text("layout", scene["layout_name"])
    metadata.add_text("node_count", str(len(scene["nodes"])))
    metadata.add_text("edge_count", str(len(scene["edges"])))
    image.save(output, format="PNG", dpi=(dpi, dpi), pnginfo=metadata, optimize=True)
    return {
        "path": str(output),
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "dpi": dpi,
        "long_edge": max(image.size),
        "transparent": transparent,
        "alpha_extrema": image.getchannel("A").getextrema(),
        "font": font_name,
        "warnings": font_warnings,
        "renderer": "Pillow direct Scene Graph rasterizer",
    }
