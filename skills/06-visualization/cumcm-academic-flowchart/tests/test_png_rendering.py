import tempfile
import unittest
from pathlib import Path

from PIL import Image

from _support import make_ir
from layout_candidates import build_layout
from png_renderer import render_png
from style_engine import apply_theme
from validate_png import validate_png


class PNGRenderingTests(unittest.TestCase):
    def render(self, temp: str, dpi: int = 300, transparent: bool = True):
        scene, _ = apply_theme(build_layout(make_ir(), "u_shaped"), "journal-rich")
        path = Path(temp) / "diagram.png"
        info = render_png(scene, path, long_edge=3200, dpi=dpi, transparent=transparent)
        return path, scene, info

    def test_300_dpi(self):
        with tempfile.TemporaryDirectory() as temp:
            path, scene, _ = self.render(temp, 300)
            result = validate_png(
                path,
                minimum_long_edge=3200,
                require_alpha=True,
                expected_node_count=len(scene["nodes"]),
            )
            self.assertTrue(result["passed"])
            self.assertAlmostEqual(result["dpi"][0], 300, delta=1)

    def test_600_dpi(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _, _ = self.render(temp, 600)
            with Image.open(path) as image:
                self.assertAlmostEqual(image.info["dpi"][0], 600, delta=1)

    def test_long_edge_exact(self):
        with tempfile.TemporaryDirectory() as temp:
            path, _, info = self.render(temp)
            with Image.open(path) as image:
                self.assertEqual(max(image.size), 3200)
            self.assertEqual(info["long_edge"], 3200)

    def test_direct_scene_renderer_metadata(self):
        with tempfile.TemporaryDirectory() as temp:
            _, _, info = self.render(temp)
            self.assertIn("direct Scene Graph", info["renderer"])


if __name__ == "__main__":
    unittest.main()
