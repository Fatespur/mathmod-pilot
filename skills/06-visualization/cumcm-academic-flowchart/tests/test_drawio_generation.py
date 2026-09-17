import tempfile
import unittest
from pathlib import Path

from _support import make_ir
from drawio_generator import generate_drawio
from layout_candidates import build_layout
from parse_drawio import parse_drawio
from style_engine import apply_theme
from validate_drawio import validate_drawio


class DrawioGenerationTests(unittest.TestCase):
    def test_generate_and_validate(self):
        with tempfile.TemporaryDirectory() as temp:
            scene, _ = apply_theme(build_layout(make_ir(), "left_to_right"), "journal-rich")
            path = Path(temp) / "图.drawio"
            generate_drawio(scene, path, "含 & < > 符号")
            result = validate_drawio(path, {node["id"] for node in scene["nodes"]})
            self.assertTrue(result["passed"])

    def test_import_generated_drawio(self):
        with tempfile.TemporaryDirectory() as temp:
            scene, _ = apply_theme(build_layout(make_ir(), "u_shaped"), "journal-rich")
            path = Path(temp) / "source.drawio"
            generate_drawio(scene, path, "source")
            nodes, edges, warnings = parse_drawio(path)
            self.assertEqual(len(nodes), len(scene["nodes"]))
            self.assertEqual(len(edges), len(scene["edges"]))

    def test_edges_have_target_perimeter_spacing(self):
        with tempfile.TemporaryDirectory() as temp:
            scene, _ = apply_theme(build_layout(make_ir(), "left_to_right"), "journal-rich")
            path = Path(temp) / "spacing.drawio"
            generate_drawio(scene, path, "spacing")
            content = path.read_text(encoding="utf-8")
            self.assertIn("targetPerimeterSpacing=6", content)

    def test_broken_drawio_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "broken.drawio"
            path.write_text("<mxfile><broken>", encoding="utf-8")
            with self.assertRaises(ValueError):
                parse_drawio(path)


if __name__ == "__main__":
    unittest.main()
