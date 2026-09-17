from __future__ import annotations

from pathlib import Path
from typing import Any


def validate_png(
    path: Path,
    *,
    minimum_long_edge: int = 3200,
    require_alpha: bool = True,
    expected_node_count: int | None = None,
) -> dict[str, Any]:
    try:
        from PIL import Image
    except ImportError as exc:
        return {"passed": False, "errors": [f"Pillow unavailable: {exc}"]}
    errors: list[str] = []
    try:
        image = Image.open(path)
        image.verify()
        image = Image.open(path)
        image.load()
    except Exception as exc:
        return {"passed": False, "errors": [f"PNG verification failed: {exc}"]}
    if max(image.size) < minimum_long_edge:
        errors.append(f"PNG long edge {max(image.size)} < {minimum_long_edge}")
    if require_alpha and "A" not in image.getbands():
        errors.append("PNG does not contain an alpha channel")
    if require_alpha and "A" in image.getbands() and image.getchannel("A").getextrema()[0] == 255:
        errors.append("PNG alpha channel is fully opaque")
    metadata_count = image.info.get("node_count")
    if expected_node_count is not None and metadata_count is not None and int(metadata_count) != expected_node_count:
        errors.append(f"PNG node metadata {metadata_count} != {expected_node_count}")
    return {
        "passed": not errors,
        "errors": errors,
        "width": image.width,
        "height": image.height,
        "mode": image.mode,
        "long_edge": max(image.size),
        "alpha_extrema": image.getchannel("A").getextrema() if "A" in image.getbands() else None,
        "dpi": image.info.get("dpi"),
        "node_count": int(metadata_count) if metadata_count else None,
        "size": path.stat().st_size,
    }
