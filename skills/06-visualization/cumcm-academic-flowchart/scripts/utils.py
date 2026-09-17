from __future__ import annotations

import hashlib
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterable


SKILL_ROOT = Path(__file__).resolve().parents[1]
THEME_ROOT = SKILL_ROOT / "assets" / "themes"
SCHEMA_ROOT = SKILL_ROOT / "schemas"


def stable_id(prefix: str, *parts: object) -> str:
    raw = "|".join(str(part).strip() for part in parts)
    digest = hashlib.sha1(raw.encode("utf-8")).hexdigest()[:10]
    safe_prefix = re.sub(r"[^a-zA-Z0-9_-]+", "_", prefix).strip("_") or "item"
    return f"{safe_prefix}_{digest}"


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "gb18030"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(encoding="utf-8", errors="replace")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )


def sanitize_source_path(path: Path, contest_mode: bool) -> str:
    return path.name if contest_mode else str(path.resolve())


def normalize_hex(color: str) -> str:
    value = color.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    if len(value) != 6 or not re.fullmatch(r"[0-9a-fA-F]{6}", value):
        raise ValueError(f"Invalid color: {color}")
    return f"#{value.upper()}"


def hex_rgb(color: str) -> tuple[int, int, int]:
    value = normalize_hex(color)[1:]
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb: Iterable[int]) -> str:
    r, g, b = (max(0, min(255, int(v))) for v in rgb)
    return f"#{r:02X}{g:02X}{b:02X}"


def blend(foreground: str, background: str, alpha: float) -> str:
    fg = hex_rgb(foreground)
    bg = hex_rgb(background)
    return rgb_hex(round(alpha * f + (1 - alpha) * b) for f, b in zip(fg, bg))


def relative_luminance(color: str) -> float:
    channels = []
    for channel in hex_rgb(color):
        value = channel / 255
        channels.append(value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4)
    return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]


def contrast_ratio(color_a: str, color_b: str) -> float:
    a, b = relative_luminance(color_a), relative_luminance(color_b)
    lighter, darker = max(a, b), min(a, b)
    return (lighter + 0.05) / (darker + 0.05)


def grayscale_value(color: str) -> float:
    r, g, b = hex_rgb(color)
    return 0.299 * r + 0.587 * g + 0.114 * b


def box_intersection(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> tuple[float, float]:
    ax, ay, aw, ah = a
    bx, by, bw, bh = b
    return (
        max(0.0, min(ax + aw, bx + bw) - max(ax, bx)),
        max(0.0, min(ay + ah, by + bh) - max(ay, by)),
    )


def point_in_box(point: tuple[float, float], box: tuple[float, float, float, float], pad: float = 0) -> bool:
    x, y = point
    bx, by, bw, bh = box
    return bx - pad <= x <= bx + bw + pad and by - pad <= y <= by + bh + pad


def segment_intersects_box(
    start: tuple[float, float],
    end: tuple[float, float],
    box: tuple[float, float, float, float],
    pad: float = 0,
) -> bool:
    x1, y1 = start
    x2, y2 = end
    bx, by, bw, bh = box
    bx -= pad
    by -= pad
    bw += 2 * pad
    bh += 2 * pad
    if point_in_box(start, (bx, by, bw, bh)) or point_in_box(end, (bx, by, bw, bh)):
        return True
    dx, dy = x2 - x1, y2 - y1
    p = (-dx, dx, -dy, dy)
    q = (x1 - bx, bx + bw - x1, y1 - by, by + bh - y1)
    low, high = 0.0, 1.0
    for pi, qi in zip(p, q):
        if abs(pi) < 1e-12:
            if qi < 0:
                return False
            continue
        t = qi / pi
        if pi < 0:
            low = max(low, t)
        else:
            high = min(high, t)
        if low > high:
            return False
    return True


def segment_intersection(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> bool:
    def orientation(p: tuple[float, float], q: tuple[float, float], r: tuple[float, float]) -> float:
        return (q[1] - p[1]) * (r[0] - q[0]) - (q[0] - p[0]) * (r[1] - q[1])

    return orientation(a1, a2, b1) * orientation(a1, a2, b2) < 0 and orientation(b1, b2, a1) * orientation(b1, b2, a2) < 0


def polyline_length(points: list[tuple[float, float]]) -> float:
    return sum(math.dist(a, b) for a, b in zip(points, points[1:]))


def simplify_polyline(
    points: list[tuple[float, float]],
    *,
    tolerance: float = 1e-9,
) -> list[tuple[float, float]]:
    """Remove duplicate and redundant collinear points without changing the route."""
    deduplicated: list[tuple[float, float]] = []
    for point in points:
        normalized = (float(point[0]), float(point[1]))
        if not deduplicated or math.dist(deduplicated[-1], normalized) > tolerance:
            deduplicated.append(normalized)
    if len(deduplicated) < 3:
        return deduplicated
    simplified = [deduplicated[0]]
    for index, point in enumerate(deduplicated[1:-1], start=1):
        previous = simplified[-1]
        following = deduplicated[index + 1]
        same_x = abs(previous[0] - point[0]) <= tolerance and abs(point[0] - following[0]) <= tolerance
        same_y = abs(previous[1] - point[1]) <= tolerance and abs(point[1] - following[1]) <= tolerance
        between_y = min(previous[1], following[1]) - tolerance <= point[1] <= max(previous[1], following[1]) + tolerance
        between_x = min(previous[0], following[0]) - tolerance <= point[0] <= max(previous[0], following[0]) + tolerance
        if not ((same_x and between_y) or (same_y and between_x)):
            simplified.append(point)
    simplified.append(deduplicated[-1])
    return simplified


def shorten_polyline_end(
    points: list[tuple[float, float]],
    gap: float,
) -> list[tuple[float, float]]:
    """Move a polyline tip backwards so its arrowhead stays clear of a node border."""
    shortened = simplify_polyline(points)
    if len(shortened) < 2 or gap <= 0:
        return shortened
    start, end = shortened[-2], shortened[-1]
    length = math.dist(start, end)
    if length <= 1e-9:
        return shortened
    effective_gap = min(float(gap), length * 0.45)
    ratio = effective_gap / length
    shortened[-1] = (
        end[0] + (start[0] - end[0]) * ratio,
        end[1] + (start[1] - end[1]) * ratio,
    )
    return shortened


def unique_preserving(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def load_theme(name_or_path: str) -> dict[str, Any]:
    candidate = Path(name_or_path)
    if not candidate.exists():
        candidate = THEME_ROOT / f"{name_or_path}.json"
    if not candidate.exists():
        available = ", ".join(sorted(path.stem for path in THEME_ROOT.glob("*.json")))
        raise FileNotFoundError(f"Theme {name_or_path!r} not found. Available: {available}")
    theme = read_json(candidate)
    theme["name"] = theme.get("name", candidate.stem)
    return theme


def optional_dependency_status() -> dict[str, bool]:
    import importlib.util

    return {
        "Pillow": importlib.util.find_spec("PIL") is not None,
        "pypdf": importlib.util.find_spec("pypdf") is not None,
        "python-docx": importlib.util.find_spec("docx") is not None,
        "openpyxl": importlib.util.find_spec("openpyxl") is not None,
        "PyYAML": importlib.util.find_spec("yaml") is not None,
        "jsonschema": importlib.util.find_spec("jsonschema") is not None,
    }


def safe_output_dir(path: Path, overwrite: bool) -> Path:
    path = path.resolve()
    if path.exists() and any(path.iterdir()) and not overwrite:
        raise FileExistsError(f"Output directory is not empty: {path}. Use --overwrite.")
    path.mkdir(parents=True, exist_ok=True)
    return path


def log(message: str, debug: bool = False) -> None:
    if debug:
        print(message, file=sys.stderr)
