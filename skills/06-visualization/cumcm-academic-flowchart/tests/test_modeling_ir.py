import copy
import json
import unittest
from pathlib import Path

from _support import SKILL_ROOT, make_ir
from validate_ir import validate_ir


class ModelingIRTests(unittest.TestCase):
    def test_all_five_types_validate(self):
        for question_type in ("优化类", "预测类", "评价类", "数理统计类", "机理分析类"):
            with self.subTest(question_type=question_type):
                self.assertTrue(validate_ir(make_ir(question_type), use_jsonschema=False)["passed"])

    def test_duplicate_node_id_rejected(self):
        ir = make_ir()
        ir["nodes"][1]["id"] = ir["nodes"][0]["id"]
        self.assertFalse(validate_ir(ir, use_jsonschema=False)["passed"])

    def test_broken_edge_reference_rejected(self):
        ir = make_ir()
        ir["edges"][0]["target"] = "missing"
        self.assertFalse(validate_ir(ir, use_jsonschema=False)["passed"])

    def test_schema_is_valid_json(self):
        schema = json.loads((SKILL_ROOT / "schemas" / "modeling_ir.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(schema["type"], "object")
        self.assertIn("nodes", schema["required"])

    def test_deterministic_ids(self):
        self.assertEqual(
            [node["id"] for node in make_ir()["nodes"]],
            [node["id"] for node in make_ir()["nodes"]],
        )


if __name__ == "__main__":
    unittest.main()
