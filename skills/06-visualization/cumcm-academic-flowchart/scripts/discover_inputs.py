from __future__ import annotations

from pathlib import Path
from typing import Iterable


SUPPORTED_NAMES = {
    "problem.pdf",
    "problem.docx",
    "problem.md",
    "problem.txt",
    "solution.md",
    "analysis.md",
    "paper.docx",
    "paper.tex",
    "paper.md",
    "readme.md",
}
SUPPORTED_SUFFIXES = {
    ".pdf",
    ".docx",
    ".md",
    ".txt",
    ".tex",
    ".py",
    ".m",
    ".r",
    ".jl",
    ".csv",
    ".xlsx",
    ".json",
    ".yaml",
    ".yml",
    ".drawio",
}
PRIORITY = {
    "solution.md": 0,
    "analysis.md": 1,
    "paper.md": 2,
    "paper.docx": 3,
    "problem.md": 4,
    "problem.pdf": 5,
    "problem.docx": 6,
}


def discover_inputs(inputs: Iterable[str | Path], max_files: int = 80) -> list[Path]:
    discovered: list[Path] = []
    for raw in inputs:
        path = Path(raw).expanduser()
        if path.is_file():
            discovered.append(path.resolve())
            continue
        if path.is_dir():
            for child in path.iterdir():
                if child.is_file() and (
                    child.name.lower() in SUPPORTED_NAMES or child.suffix.lower() in SUPPORTED_SUFFIXES
                ):
                    discovered.append(child.resolve())
                elif child.is_dir() and child.name.lower() in {"src", "code", "scripts"}:
                    discovered.extend(
                        candidate.resolve()
                        for candidate in child.rglob("*")
                        if candidate.is_file() and candidate.suffix.lower() in SUPPORTED_SUFFIXES
                    )
    unique = {str(path).casefold(): path for path in discovered}
    ordered = sorted(
        unique.values(),
        key=lambda path: (PRIORITY.get(path.name.lower(), 20), path.name.lower()),
    )
    return ordered[:max_files]
