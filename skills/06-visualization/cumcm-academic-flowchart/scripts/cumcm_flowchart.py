from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from comparison_board import generate_comparison
from diagram_planner import create_diagram_plan
from discover_inputs import discover_inputs
from drawio_generator import generate_drawio
from elk_adapter import elk_layout_request
from extract_modeling_ir import extract_modeling_ir
from graphviz_adapter import generate_dot, graphviz_available
from layout_candidates import generate_layout_candidates
from layout_selector import select_layouts
from mermaid_generator import generate_mermaid
from normalize_ir import normalize_ir
from parse_documents import dependency_report
from png_renderer import render_png
from quality_review import dual_layout_review, review_variant
from style_engine import apply_theme
from svg_generator import generate_svg
from utils import log, read_json, safe_output_dir, write_json, write_text
from validate_ir import validate_ir
from validate_layout import validate_layout


EXIT_OK = 0
EXIT_QUALITY = 1
EXIT_INPUT = 2
EXIT_DEPENDENCY = 3


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate validated academic mathematical-modeling diagrams")
    parser.add_argument("--input", nargs="+", required=True, help="Input file(s) or directory")
    parser.add_argument("--output", required=True, help="Output directory")
    parser.add_argument("--diagram", default="auto")
    parser.add_argument("--question")
    parser.add_argument("--layouts", type=int, default=2)
    parser.add_argument("--primary-layout")
    parser.add_argument("--alternative-layout")
    parser.add_argument("--engine", choices=["auto", "direct", "graphviz", "elk", "mermaid"], default="auto")
    parser.add_argument("--theme", default="journal-rich")
    parser.add_argument("--transparent", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--background", default="#FFFFFF")
    parser.add_argument("--png-dpi", type=int, choices=[300, 600], default=300)
    parser.add_argument("--png-long-edge", type=int, default=4800)
    parser.add_argument("--svg-text-mode", choices=["text", "path"], default="text")
    parser.add_argument("--target-width-mm", type=float, default=160)
    parser.add_argument("--language", default="zh-CN")
    parser.add_argument("--contest-mode", action="store_true")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--config")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--debug", action="store_true")
    return parser


def _load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    config_path = Path(path)
    if config_path.suffix.lower() == ".json":
        return read_json(config_path)
    try:
        import yaml
    except ImportError as exc:
        raise RuntimeError("YAML config requires PyYAML; JSON config remains available") from exc
    return yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}


def _apply_config(args: argparse.Namespace, config: dict[str, Any]) -> argparse.Namespace:
    for key, value in config.items():
        attribute = key.replace("-", "_")
        if hasattr(args, attribute):
            setattr(args, attribute, value)
    return args


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _copy_aliases(output: Path) -> None:
    aliases = {
        "diagram_primary.drawio": "primary.drawio",
        "diagram_primary.svg": "primary.svg",
        "diagram_primary.png": "primary.png",
        "diagram_primary.layout.json": "primary.layout.json",
        "diagram_alternative.drawio": "alternative.drawio",
        "diagram_alternative.svg": "alternative.svg",
        "diagram_alternative.png": "alternative.png",
        "diagram_alternative.layout.json": "alternative.layout.json",
        "diagram_comparison.svg": "comparison.svg",
        "diagram_comparison.png": "comparison.png",
    }
    for source_name, alias_name in aliases.items():
        source = output / source_name
        if source.exists():
            shutil.copyfile(source, output / alias_name)


def _write_variant(
    ir: dict[str, Any],
    scene: dict[str, Any],
    theme: dict[str, Any],
    output: Path,
    role: str,
    args: argparse.Namespace,
) -> tuple[dict[str, Path], dict[str, Any]]:
    paths = {
        "drawio": output / f"diagram_{role}.drawio",
        "svg": output / f"diagram_{role}.svg",
        "png": output / f"diagram_{role}.png",
        "layout": output / f"diagram_{role}.layout.json",
    }
    title = ir["meta"]["title"]
    generate_drawio(scene, paths["drawio"], title)
    generate_svg(
        scene,
        paths["svg"],
        title,
        transparent=args.transparent,
        target_width_mm=args.target_width_mm,
        text_mode=args.svg_text_mode,
    )
    png_info = render_png(
        scene,
        paths["png"],
        long_edge=args.png_long_edge,
        dpi=args.png_dpi,
        transparent=args.transparent,
        target_width_mm=args.target_width_mm,
    )
    layout_payload = {key: value for key, value in scene.items() if key not in {"theme_definition"}}
    write_json(paths["layout"], layout_payload)
    quality = review_variant(
        ir,
        scene,
        theme,
        paths,
        args.png_long_edge,
        args.transparent,
        args.target_width_mm,
    )
    quality["png_renderer"] = png_info
    return paths, quality


def _generation_report(
    args: argparse.Namespace,
    ir: dict[str, Any],
    primary: dict[str, Any],
    alternative: dict[str, Any],
    quality: dict[str, Any],
    files: list[Path],
    optional_dependencies: dict[str, bool],
    corrections: list[dict[str, Any]],
) -> str:
    unavailable = [name for name, available in optional_dependencies.items() if not available]
    return f"""# 学术框架图生成报告

## 输入与语义

- 输入：{", ".join(ir["meta"]["source_files"])}
- 图种：{ir["diagram"]["diagram_type"]}
- 小问分类：{", ".join(f'{q["question_id"]}={q["primary_type"]}({q["confidence"]:.2f})' for q in ir["questions"])}
- 竞赛离线模式：{"开启" if args.contest_mode else "关闭"}

## 核心架构

`Input → ModelingIR → Diagram Plan → Candidate Layouts → Scoring → Primary/Alternative → Shared Scene Graph → draw.io/SVG/PNG → Five-part Quality Review`

## 布局

- 主方案：{primary["layout_name"]} / {primary["layout_family"]} / 布局分 {primary["metrics"]["layout_score"]}
- 备用方案：{alternative["layout_name"]} / {alternative["layout_family"]} / 布局分 {alternative["metrics"]["layout_score"]}
- 布局差异度：{quality["dual_layout"]["layout_diversity_score"]}
- 自动修正轮次：{len(corrections)}

## 输出实现

- draw.io：未压缩 `mxGraphModel`，稳定节点 ID，可在 diagrams.net 编辑。
- SVG：由 Scene Graph 直接生成标准形状、`text/tspan`、透明度、正交折线和正确 viewBox。
- PNG：Pillow 直接按 Scene Graph 以目标像素栅格化；不是截图，也不是低清放大。
- 主题：{args.theme}；语义配色、真实 alpha、文字保持不透明。

## 质量结果

- 主方案：{quality["primary"]["total_score"]}/100，门槛 92，{"通过" if quality["primary"]["total_score"] >= 92 and quality["primary"]["passed"] else "未通过"}
- 备用方案：{quality["alternative"]["total_score"]}/100，门槛 88，{"通过" if quality["alternative"]["total_score"] >= 88 and quality["alternative"]["passed"] else "未通过"}
- 双布局：{"通过" if quality["dual_layout"]["passed"] else "未通过"}

## 可选依赖

- 状态：{optional_dependencies}
- 不可用：{", ".join(unavailable) if unavailable else "无"}
- Graphviz：{"可用" if graphviz_available() else "不可用；已使用内置离线布局"}
- ELK/Mermaid/draw.io Desktop：非核心依赖。

## 合规与人工复核

- 未使用在线渲染服务，未伪造结果，未记录身份信息。
- AI 推断节点已在 ModelingIR 中以 `inferred` 标记。
- 请作者核对题型、数学逻辑、变量含义、小问依赖和图题。
- “国奖级”是质量目标，不是获奖承诺。
"""


def run(args: argparse.Namespace) -> int:
    if args.layouts < 2:
        raise ValueError("--layouts must be at least 2")
    if args.png_long_edge < 3200:
        raise ValueError("--png-long-edge must be at least 3200")
    output = safe_output_dir(Path(args.output), args.overwrite)
    inputs = discover_inputs(args.input)
    if not inputs:
        raise FileNotFoundError("No supported input files found")
    log(f"Discovered {len(inputs)} input files", args.debug)
    ir, extraction_warnings = extract_modeling_ir(
        inputs,
        diagram_type=args.diagram,
        language=args.language,
        contest_mode=args.contest_mode,
        target_width_mm=args.target_width_mm,
        theme=args.theme,
        variants=args.layouts,
        question_filter=args.question,
    )
    ir = normalize_ir(ir)
    ir_validation = validate_ir(ir)
    if not ir_validation["passed"]:
        raise ValueError(f"ModelingIR validation failed: {ir_validation['errors']}")
    plan = create_diagram_plan(ir, args.primary_layout, args.alternative_layout)
    write_json(output / "modeling_ir.json", ir)
    write_json(output / "diagram_plan.json", plan)
    if args.engine == "graphviz":
        generate_dot(ir, output / "diagram_intermediate.dot")
    elif args.engine == "elk":
        write_json(output / "diagram_elk_request.json", elk_layout_request(ir))
    elif args.engine == "mermaid":
        generate_mermaid(ir, output / "diagram_intermediate.mmd")
    corrections: list[dict[str, Any]] = []
    primary = alternative = None
    ranked: list[dict[str, Any]] = []
    for attempt, spacing_scale in enumerate((1.0, 1.14, 1.30), start=1):
        candidates = generate_layout_candidates(
            ir,
            seed=args.seed,
            forced=[args.primary_layout, args.alternative_layout],
            spacing_scale=spacing_scale,
        )
        selected_primary, selected_alternative, ranked = select_layouts(
            candidates,
            primary_name=args.primary_layout,
            alternative_name=args.alternative_layout,
        )
        primary_issues = validate_layout(selected_primary)
        alternative_issues = validate_layout(selected_alternative)
        if primary_issues["passed"] and alternative_issues["passed"]:
            primary, alternative = selected_primary, selected_alternative
            break
        corrections.append(
            {
                "round": attempt,
                "issues": primary_issues["errors"] + alternative_issues["errors"],
                "severity": "blocking",
                "strategy": f"Increase spacing to {spacing_scale + 0.14:.2f} and reroute edges",
                "before_scores": [selected_primary["metrics"]["layout_score"], selected_alternative["metrics"]["layout_score"]],
                "after_scores": None,
                "remaining": [],
            }
        )
        primary, alternative = selected_primary, selected_alternative
    if corrections and primary and alternative:
        corrections[-1]["after_scores"] = [primary["metrics"]["layout_score"], alternative["metrics"]["layout_score"]]
        corrections[-1]["remaining"] = validate_layout(primary)["errors"] + validate_layout(alternative)["errors"]
    primary_scene, theme_definition = apply_theme(primary, args.theme)
    alternative_scene, _ = apply_theme(alternative, args.theme)
    primary_scene["layout_diversity_score"] = primary["layout_diversity_score"]
    alternative_scene["layout_diversity_score"] = alternative["layout_diversity_score"]
    primary_paths, primary_quality = _write_variant(ir, primary_scene, theme_definition, output, "primary", args)
    alternative_paths, alternative_quality = _write_variant(ir, alternative_scene, theme_definition, output, "alternative", args)
    comparison_info = generate_comparison(
        primary_scene,
        alternative_scene,
        output / "diagram_comparison.svg",
        output / "diagram_comparison.png",
        title=ir["meta"]["title"],
        transparent=args.transparent,
        long_edge=args.png_long_edge,
        dpi=args.png_dpi,
        target_width_mm=args.target_width_mm,
    )
    dual_quality = dual_layout_review(primary_scene, alternative_scene)
    quality = {
        "schema_version": "1.0",
        "thresholds": {"primary": 92, "alternative": 88, "layout_diversity": 0.55},
        "ir": ir_validation,
        "primary": primary_quality,
        "alternative": alternative_quality,
        "dual_layout": dual_quality,
        "auto_corrections": corrections,
        "extraction_warnings": extraction_warnings,
    }
    quality["passed"] = (
        primary_quality["passed"]
        and alternative_quality["passed"]
        and primary_quality["total_score"] >= 92
        and alternative_quality["total_score"] >= 88
        and dual_quality["passed"]
    )
    write_json(output / "quality_report.json", quality)
    _copy_aliases(output)
    optional_dependencies = dependency_report()
    report = _generation_report(
        args,
        ir,
        primary_scene,
        alternative_scene,
        quality,
        inputs,
        optional_dependencies,
        corrections,
    )
    write_text(output / "generation_report.md", report)
    generated_files = sorted(path for path in output.iterdir() if path.is_file())
    manifest = {
        "schema_version": "1.0",
        "generator": "cumcm-academic-flowchart",
        "created_at": datetime.now(timezone.utc).isoformat(),
        "contest_mode": args.contest_mode,
        "source_files": ir["meta"]["source_files"],
        "theme": args.theme,
        "seed": args.seed,
        "engine": "direct-scene-graph" if args.engine == "auto" else args.engine,
        "outputs": [
            {"name": path.name, "bytes": path.stat().st_size, "sha256": _sha256(path)}
            for path in generated_files
        ],
        "quality_passed": quality["passed"],
        "ai_operations": [
            "input discovery",
            "question classification",
            "ModelingIR extraction",
            "candidate layout generation and scoring",
            "draw.io/SVG/PNG generation",
            "five-part quality review",
        ],
        "human_review_required": True,
    }
    write_json(output / "diagram_manifest.json", manifest)
    if args.debug:
        print(json.dumps({"output": str(output), "quality": quality["passed"]}, ensure_ascii=False, indent=2))
    return EXIT_OK if quality["passed"] or not args.strict else EXIT_QUALITY


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        args = _apply_config(args, _load_config(args.config))
        return run(args)
    except (ValueError, FileNotFoundError, FileExistsError) as exc:
        print(f"Input/configuration error: {exc}", file=sys.stderr)
        return EXIT_INPUT
    except RuntimeError as exc:
        print(f"Dependency/runtime error: {exc}", file=sys.stderr)
        return EXIT_DEPENDENCY
    except Exception as exc:
        print(f"Unexpected error: {exc}", file=sys.stderr)
        if getattr(args, "debug", False):
            traceback.print_exc()
        return EXIT_QUALITY


if __name__ == "__main__":
    raise SystemExit(main())
