from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from paper_number_validator import (
    flatten_macros,
    validate_macro_document,
    validate_paper,
)


VALID_MACROS = {
    "schema_version": "1.0",
    "metadata": {"contest": "CUMCM"},
    "macros": {
        "data": {
            "count": {
                "value": 878042,
                "source": "results/data.json#/count",
                "precision": 0,
                "formats": ["878,042"],
            }
        },
        "metrics": {
            "r2": {
                "value": 0.9431,
                "source": "results/metrics.json#/r2",
                "precision": 3,
                "formats": ["0.943"],
            },
            "error": {
                "value": 0.067,
                "source": "results/metrics.json#/error",
                "formats": ["6.7%"],
            },
            "ci": {
                "value": [4.1, 7.9],
                "source": "results/metrics.json#/ci",
                "precision": 1,
            },
        },
    },
    "allowlist": {"years": [2026], "values": [2], "tokens": ["1e-8"]},
}


class MacroValidationTests(unittest.TestCase):
    def test_valid_document(self) -> None:
        self.assertEqual(validate_macro_document(VALID_MACROS), [])

    def test_missing_source_is_invalid(self) -> None:
        invalid = json.loads(json.dumps(VALID_MACROS))
        del invalid["macros"]["data"]["count"]["source"]
        self.assertTrue(any("source" in error for error in validate_macro_document(invalid)))

    def test_legacy_numeric_mapping(self) -> None:
        values, _ = flatten_macros({"count": 12, "nested": {"score": 0.5}})
        self.assertEqual({item.key for item in values}, {"count", "nested.score"})


class PaperValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.macros, self.allowlist = flatten_macros(VALID_MACROS)

    def test_matching_formats_and_structural_numbers(self) -> None:
        paper = """# 5 模型结果

共有 878,042 条记录，模型的 $R^2$ 为 0.943，相对误差为 6.7%。
置信区间为 [4.1, 7.9]。见图2和式(3)，研究年份为 2026。
计算采用 2 个阶段，容差为 1e-8。
"""
        result = validate_paper(paper, self.macros, self.allowlist)
        self.assertEqual(result["status"], "passed", result["unknown"])

    def test_unknown_number_fails(self) -> None:
        result = validate_paper("最终成本为 123.45 元。", self.macros, self.allowlist)
        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["unknown"][0]["token"], "123.45")

    def test_numbers_in_code_fence_are_ignored(self) -> None:
        paper = "```python\nthreshold = 999\n```\n模型的 $R^2$ 为 0.943。"
        result = validate_paper(paper, self.macros, self.allowlist)
        self.assertEqual(result["status"], "passed", result["unknown"])

    def test_json_report_inputs_can_be_serialized(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "paper_macros.json"
            path.write_text(json.dumps(VALID_MACROS), encoding="utf-8")
            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(validate_macro_document(loaded), [])


if __name__ == "__main__":
    unittest.main()
