import json
import tempfile
import unittest
from pathlib import Path

from _support import SKILL_ROOT
from cumcm_flowchart import EXIT_OK, main
from extract_modeling_ir import extract_modeling_ir


class EndToEndTests(unittest.TestCase):
    def test_chinese_path_contest_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "中文路径"
            root.mkdir()
            source = root / "方案.md"
            source.write_text("以成本最小为目标建立整数规划，输出最优方案并验证。", encoding="utf-8")
            output = root / "输出"
            code = main([
                "--input", str(source), "--output", str(output),
                "--primary-layout", "rectangular_loop",
                "--alternative-layout", "u_shaped",
                "--png-long-edge", "3200", "--contest-mode", "--strict",
            ])
            self.assertEqual(code, EXIT_OK)
            quality = json.loads((output / "quality_report.json").read_text(encoding="utf-8"))
            self.assertTrue(quality["passed"])
            self.assertNotIn(str(root), json.dumps(quality, ensure_ascii=False))

    def test_example_outputs_are_complete(self):
        required = {
            "diagram_primary.drawio", "diagram_primary.svg", "diagram_primary.png",
            "diagram_alternative.drawio", "diagram_alternative.svg", "diagram_alternative.png",
            "diagram_primary.layout.json", "diagram_alternative.layout.json",
            "diagram_comparison.svg", "diagram_comparison.png", "modeling_ir.json",
            "diagram_plan.json", "diagram_manifest.json", "generation_report.md",
            "quality_report.json",
        }
        for folder in (SKILL_ROOT / "assets" / "examples").iterdir():
            if folder.is_dir():
                with self.subTest(example=folder.name):
                    self.assertTrue(required.issubset({path.name for path in (folder / "output").iterdir()}))
                    quality = json.loads((folder / "output" / "quality_report.json").read_text(encoding="utf-8"))
                    self.assertTrue(quality["passed"])

    def test_code_paper_conflict_warning(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            paper = root / "solution.md"
            code = root / "solver.py"
            paper.write_text("建立预测模型并输出未来趋势", encoding="utf-8")
            code.write_text("print('only output')", encoding="utf-8")
            _, warnings = extract_modeling_ir([paper, code], contest_mode=True)
            self.assertTrue(any("源代码" in warning or "模型" in warning for warning in warnings))


if __name__ == "__main__":
    unittest.main()
