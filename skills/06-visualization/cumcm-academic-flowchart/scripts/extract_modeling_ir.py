from __future__ import annotations

from pathlib import Path
from typing import Any

from classify_question import classify_document, split_questions
from method_framework import build_method_framework
from parse_documents import parse_document
from parse_drawio import parse_drawio
from parse_source_code import parse_source_code
from utils import sanitize_source_path, stable_id, unique_preserving


def extract_modeling_ir(
    files: list[Path],
    *,
    diagram_type: str = "auto",
    language: str = "zh-CN",
    contest_mode: bool = False,
    target_width_mm: float = 160,
    theme: str = "journal-rich",
    variants: int = 2,
    question_filter: str | None = None,
) -> tuple[dict[str, Any], list[str]]:
    warnings: list[str] = []
    texts: list[str] = []
    source_records = []
    code_records = []
    drawio_records: list[tuple[Path, list[dict[str, Any]], list[dict[str, Any]]]] = []
    for path in files:
        if path.suffix.lower() in {".py", ".m", ".r", ".jl"}:
            code_records.append(parse_source_code(path))
            continue
        if path.suffix.lower() == ".drawio":
            drawio_nodes, drawio_edges, drawio_warnings = parse_drawio(path)
            warnings.extend(drawio_warnings)
            drawio_records.append((path, drawio_nodes, drawio_edges))
            texts.append("\n".join(node["label"] for node in drawio_nodes))
            source_records.append(sanitize_source_path(path, contest_mode))
            continue
        text, parse_warnings = parse_document(path)
        warnings.extend(parse_warnings)
        if text.strip():
            texts.append(text)
            source_records.append(sanitize_source_path(path, contest_mode))
    combined = "\n\n".join(texts)
    questions = classify_document(combined)
    question_texts = dict(split_questions(combined))
    if question_filter:
        target = question_filter.upper().replace("问题", "Q")
        questions = [question for question in questions if question["question_id"].upper() == target]
        if not questions:
            raise ValueError(f"Question filter did not match: {question_filter}")
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []
    groups: list[dict[str, Any]] = []
    imported_drawio = bool(drawio_records)
    if imported_drawio:
        if len(drawio_records) > 1:
            warnings.append("Multiple draw.io inputs were merged; verify cross-diagram semantics manually")
        for _, imported_nodes, imported_edges in drawio_records:
            nodes.extend(imported_nodes)
            edges.extend(imported_edges)
        questions = questions[:1]
        questions[0]["question_id"] = "Q1"
        groups.append(
            {
                "id": stable_id("group", "Q1"),
                "label": f"Q1 · {questions[0]['primary_type']}",
                "question_id": "Q1",
                "node_ids": [node["id"] for node in nodes],
            }
        )
    else:
        for question in questions:
            question_nodes, question_edges, detected_methods = build_method_framework(
                question,
                question_texts.get(question["question_id"], combined),
                source_records[0] if source_records else "user_input",
                compact=len(questions) > 1,
            )
            question["detected_methods"] = detected_methods
            nodes.extend(question_nodes)
            edges.extend(question_edges)
            if len(questions) > 1:
                groups.append(
                    {
                        "id": stable_id("group", question["question_id"]),
                        "label": f"{question['question_id']} · {question.get('goal', question['primary_type']).splitlines()[0][:24]}",
                        "question_id": question["question_id"],
                        "group_type": "question",
                        "node_ids": [node["id"] for node in question_nodes],
                    }
                )
            else:
                module_labels = {
                    "data": "数据基础",
                    "feature": "特征构建",
                    "indicator": "指标体系",
                    "preprocessing": "数据处理",
                    "formulation": "模型定义",
                    "variables": "变量体系",
                    "modeling": "核心方法",
                    "weighting": "权重方法",
                    "inference": "统计推断",
                    "equation": "方程体系",
                    "solution": "求解策略",
                    "validation": "模型检验",
                    "result": "结果输出",
                }
                for module in unique_preserving(node.get("module", "") for node in question_nodes):
                    members = [node["id"] for node in question_nodes if node.get("module") == module]
                    if module in module_labels and len(members) >= 2:
                        groups.append(
                            {
                                "id": stable_id("module", question["question_id"], module),
                                "label": module_labels[module],
                                "question_id": question["question_id"],
                                "group_type": "module",
                                "module": module,
                                "node_ids": members,
                            }
                        )
    for index in range(len(questions) - 1):
        source_question_id = questions[index]["question_id"]
        target_question_id = questions[index + 1]["question_id"]
        source_nodes = [node for node in nodes if node["question_id"] == source_question_id]
        target_nodes = [node for node in nodes if node["question_id"] == target_question_id]
        source = next((node for node in reversed(source_nodes) if node["semantic_type"] == "output"), source_nodes[-1])
        target = target_nodes[0]
        edges.append(
            {
                "id": stable_id("dependency", source["id"], target["id"]),
                "source": source["id"],
                "target": target["id"],
                "edge_type": "question_dependency",
                "label": "结果/参数传递",
                "feedback": False,
                "key": True,
            }
        )
    inferred_nodes = [node["id"] for node in nodes if node["inferred"]]
    if inferred_nodes:
        warnings.append(f"{len(inferred_nodes)} 个节点基于低置信度题型模板推断，需人工复核")
    code_signals = {
        category: unique_preserving(
            keyword
            for record in code_records
            for keyword in record["signals"].get(category, [])
        )
        for category in {
            "data_entry",
            "preprocessing",
            "model_definition",
            "training",
            "objective",
            "constraint",
            "solver",
            "metric",
            "output",
        }
    }
    if code_records and not code_signals["model_definition"]:
        warnings.append("源码中未识别到模型定义；方案与代码可能不一致")
    if diagram_type == "auto":
        diagram_type = "overall_route" if len(questions) > 1 else {
            "优化类": "optimization_flow",
            "预测类": "prediction_flow",
            "评价类": "evaluation_flow",
            "数理统计类": "statistical_analysis_flow",
            "机理分析类": "mechanism_model",
        }[questions[0]["primary_type"]]
    title = "数学建模总体技术路线" if len(questions) > 1 else f"{questions[0]['question_id']} 建模框架"
    ir = {
        "schema_version": "1.0",
        "meta": {
            "title": title,
            "language": language,
            "competition": "CUMCM",
            "source_files": source_records + [sanitize_source_path(path, contest_mode) for path in files if path.suffix.lower() in {".py", ".m", ".r", ".jl"}],
            "contest_mode": contest_mode,
            "ai_generated": True,
            "identity_redacted": contest_mode,
            "framework_mode": "imported_diagram" if imported_drawio else "method_hierarchy",
        },
        "questions": questions,
        "diagram": {
            "diagram_type": diagram_type,
            "purpose": "paper_method_overview",
            "target_width_mm": target_width_mm,
            "target_height_mm": None,
            "transparent_background": True,
            "theme": theme,
            "variants": variants,
        },
        "groups": groups,
        "nodes": nodes,
        "edges": edges,
        "code_signals": code_signals,
        "warnings": warnings,
    }
    return ir, warnings
