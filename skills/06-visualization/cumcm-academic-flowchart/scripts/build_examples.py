from __future__ import annotations

import subprocess
import sys
import json
import argparse
from pathlib import Path


EXAMPLES = {
    "optimization": ("method_framework", "rectangular_loop", 300),
    "prediction": ("method_framework", "dual_stream", 300),
    "evaluation": ("method_framework", "hub_spoke", 300),
    "statistical": ("hierarchical_tree", "method_framework", 600),
    "mechanism": ("method_framework", "concentric", 300),
    "rectangular-loop": ("rectangular_loop", "method_framework", 300),
    "dual-stream": ("dual_stream", "method_framework", 300),
    "question-swimlane": ("question_swimlane", "hierarchical_tree", 300),
    "hub-spoke": ("hub_spoke", "method_framework", 300),
    "neural-architecture": ("layered_architecture", "hierarchical_tree", 300),
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--force", action="store_true", help="Rebuild even when a passing output exists")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    cli = root / "scripts" / "cumcm_flowchart.py"
    for name, (primary, alternative, dpi) in EXAMPLES.items():
        folder = root / "assets" / "examples" / name
        quality_path = folder / "output" / "quality_report.json"
        if quality_path.exists() and not args.force:
            try:
                if json.loads(quality_path.read_text(encoding="utf-8")).get("passed") is True:
                    print(f"Skipped {name}: existing output already passed")
                    continue
            except (OSError, json.JSONDecodeError):
                pass
        command = [
            sys.executable,
            str(cli),
            "--input",
            str(folder / "input.md"),
            "--output",
            str(folder / "output"),
            "--primary-layout",
            primary,
            "--alternative-layout",
            alternative,
            "--theme",
            "journal-rich",
            "--transparent",
            "--png-dpi",
            str(dpi),
            "--png-long-edge",
            "3200",
            "--seed",
            "42",
            "--contest-mode",
            "--strict",
            "--overwrite",
        ]
        completed = subprocess.run(command, check=False)
        if completed.returncode:
            raise SystemExit(f"Example {name} failed with exit code {completed.returncode}")
        print(f"Built {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
