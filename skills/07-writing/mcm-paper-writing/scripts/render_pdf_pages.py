#!/usr/bin/env python3
"""Render every PDF page to PNG and write a review manifest."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from pypdf import PdfReader


def resolve_pdftoppm() -> str:
    """Resolve the real Poppler binary when a runtime CMD shim is broken."""
    executable = shutil.which("pdftoppm")
    if executable:
        candidate = Path(executable)
        if candidate.suffix.lower() == ".exe":
            return str(candidate)
        try:
            dependency_root = candidate.parents[2]
            real_binary = dependency_root / "native" / "poppler" / "Library" / "bin" / "pdftoppm.exe"
            if real_binary.exists():
                return str(real_binary)
        except IndexError:
            pass
        return executable
    raise RuntimeError("pdftoppm is unavailable")


def render(pdf: Path, output_dir: Path, dpi: int = 150) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    executable = resolve_pdftoppm()
    prefix = output_dir / "page"
    result = subprocess.run([executable, "-png", "-r", str(dpi), str(pdf), str(prefix)], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip())
    pages = sorted(output_dir.glob("page-*.png"))
    expected = len(PdfReader(pdf).pages)
    if len(pages) != expected:
        raise RuntimeError(f"rendered {len(pages)} pages but PDF contains {expected}")
    return pages


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dpi", type=int, default=150)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        pages = render(args.pdf, args.output_dir, args.dpi)
        manifest = {"schema_version": "1.0", "pdf": str(args.pdf), "dpi": args.dpi, "page_count": len(pages), "pages": [str(path) for path in pages], "all_pages_reviewed": False}
        (args.output_dir / "render_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"PDF已渲染为{len(pages)}页PNG；必须逐页检查后再更新复核记录。")
        return 0
    except (OSError, RuntimeError) as exc:
        print(f"PDF渲染失败：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
