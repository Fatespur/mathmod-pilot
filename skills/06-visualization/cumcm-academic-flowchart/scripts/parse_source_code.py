from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from utils import read_text


KEYWORDS = {
    "data_entry": ["read_csv", "read_excel", "load", "readtable", "csvread", "dataset"],
    "preprocessing": ["dropna", "fillna", "standard", "normalize", "clean", "outlier", "impute"],
    "model_definition": ["model", "network", "regression", "svm", "lstm", "ode", "equation"],
    "training": ["fit", "train", "backward", "epoch"],
    "objective": ["objective", "loss", "cost", "fitness", "minimize", "maximize"],
    "constraint": ["constraint", "bounds", "subject to", "constr"],
    "solver": ["solve", "optimizer", "linprog", "milp", "fmin", "pso", "ga"],
    "metric": ["accuracy", "rmse", "mae", "r2", "mape", "score"],
    "output": ["save", "export", "write", "print", "plot"],
}


def parse_python(path: Path) -> dict[str, Any]:
    text = read_text(path)
    try:
        tree = ast.parse(text)
        functions = [node.name for node in ast.walk(tree) if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))]
        classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    except SyntaxError:
        functions, classes = [], []
    return {
        "path": path.name,
        "functions": functions,
        "classes": classes,
        "signals": {
            category: [keyword for keyword in keywords if keyword.lower() in text.lower()]
            for category, keywords in KEYWORDS.items()
        },
    }


def parse_source_code(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".py":
        return parse_python(path)
    text = read_text(path)
    return {
        "path": path.name,
        "functions": re.findall(r"(?im)^\s*(?:function|def)\s+([A-Za-z_]\w*)", text),
        "classes": [],
        "signals": {
            category: [keyword for keyword in keywords if keyword.lower() in text.lower()]
            for category, keywords in KEYWORDS.items()
        },
    }
