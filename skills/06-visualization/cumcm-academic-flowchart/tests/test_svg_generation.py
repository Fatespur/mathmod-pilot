import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from _support import make_ir
from layout_candidates import build_layout
from style_engine import apply_theme
from svg_generator import generate_svg
from validate_svg import validate_svg


class SVGGenerationTests(unittest.TestCase):
    def make_svg(self, temp: str, transparent: bool = True) -> tuple[Path, dict]:
        scene, _ = apply_theme(build_layout(make_ir(), "serpentine"), "journal-rich")
        path = Path(temp) / "diagram.svg"
        generate_svg(scene, path, "数学符号 α ≤ β & γ", transparent=transparent)
        return path, scene

    def test_native_svg_valid(self):
        with tempfile.TemporaryDirectory() as temp:
            path, scene = self.make_svg(temp)
            self.assertTrue(validate_svg(path, len(scene["nodes"]))["passed"])

    def test_svg_has_viewbox(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.make_svg(temp)
            root = ET.parse(path).getroot()
            self.assertIn("viewBox", root.attrib)

    def test_svg_transparent_has_no_background_rect(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.make_svg(temp, True)
            content = path.read_text(encoding="utf-8")
            self.assertNotIn('<rect width="', content)

    def test_svg_embeds_no_remote_assets(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _ = self.make_svg(temp)
            content = path.read_text(encoding="utf-8")
            self.assertNotIn("<image", content)
            self.assertNotIn("@import", content)

    def test_arrow_tip_is_aligned_and_gapped_from_target(self):
        with tempfile.TemporaryDirectory() as temp:
            path, scene = self.make_svg(temp)
            content = path.read_text(encoding="utf-8")
            self.assertIn('refX="10"', content)
            first_edge = scene["edges"][0]
            root = ET.parse(path).getroot()
            polyline = next(
                element
                for element in root
                if element.tag.endswith("polyline") and element.attrib["id"] == first_edge["id"]
            )
            rendered_tip = tuple(float(value) for value in polyline.attrib["points"].split()[-1].split(","))
            self.assertNotEqual(rendered_tip, tuple(first_edge["points"][-1]))

    def test_svg_path_text_mode(self):
        with tempfile.TemporaryDirectory() as temp:
            scene, _ = apply_theme(build_layout(make_ir(), "u_shaped"), "journal-rich")
            path = Path(temp) / "outlined.svg"
            generate_svg(scene, path, "轮廓文字", transparent=True, text_mode="path")
            content = path.read_text(encoding="utf-8")
            self.assertIn('data-text="步骤', content)
            self.assertNotIn("<text", content)


if __name__ == "__main__":
    unittest.main()
