import tempfile
import unittest
from pathlib import Path

from _support import SCRIPTS
from cumcm_flowchart import EXIT_INPUT, build_parser, main


class CLITests(unittest.TestCase):
    def test_all_required_arguments_exposed(self):
        options = {option for action in build_parser()._actions for option in action.option_strings}
        required = {
            "--input", "--output", "--diagram", "--question", "--layouts",
            "--primary-layout", "--alternative-layout", "--engine", "--theme",
            "--transparent", "--background", "--png-dpi", "--png-long-edge",
            "--svg-text-mode", "--target-width-mm", "--language", "--contest-mode",
            "--strict", "--overwrite", "--config", "--seed", "--debug",
        }
        self.assertTrue(required.issubset(options))

    def test_rejects_too_small_png(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.md"
            source.write_text("预测未来趋势", encoding="utf-8")
            code = main(["--input", str(source), "--output", str(Path(temp) / "out"), "--png-long-edge", "1000"])
            self.assertEqual(code, EXIT_INPUT)

    def test_rejects_nonempty_output_without_overwrite(self):
        with tempfile.TemporaryDirectory() as temp:
            source = Path(temp) / "input.md"
            source.write_text("预测未来趋势", encoding="utf-8")
            output = Path(temp) / "out"
            output.mkdir()
            (output / "keep.txt").write_text("keep", encoding="utf-8")
            code = main(["--input", str(source), "--output", str(output)])
            self.assertEqual(code, EXIT_INPUT)

    def test_missing_input_returns_input_error(self):
        with tempfile.TemporaryDirectory() as temp:
            code = main(["--input", str(Path(temp) / "missing.md"), "--output", str(Path(temp) / "out")])
            self.assertEqual(code, EXIT_INPUT)


if __name__ == "__main__":
    unittest.main()
