import tempfile
import unittest
from pathlib import Path

from PIL import Image

from _support import make_ir
from layout_candidates import build_layout
from png_renderer import render_png
from style_engine import apply_theme


class TransparencyTests(unittest.TestCase):
    def test_transparent_png_has_alpha_range(self):
        with tempfile.TemporaryDirectory() as temp:
            scene, _ = apply_theme(build_layout(make_ir(), "matrix"), "journal-rich")
            path = Path(temp) / "transparent.png"
            render_png(scene, path, long_edge=3200, transparent=True)
            with Image.open(path) as image:
                self.assertEqual(image.mode, "RGBA")
                self.assertEqual(image.getchannel("A").getextrema()[0], 0)

    def test_opaque_png_alpha_is_solid(self):
        with tempfile.TemporaryDirectory() as temp:
            scene, _ = apply_theme(build_layout(make_ir(), "matrix"), "journal-rich")
            path = Path(temp) / "opaque.png"
            render_png(scene, path, long_edge=3200, transparent=False)
            with Image.open(path) as image:
                self.assertEqual(image.getchannel("A").getextrema(), (255, 255))

    def test_node_text_remains_opaque(self):
        scene, _ = apply_theme(build_layout(make_ir(), "matrix"), "journal-rich")
        self.assertTrue(all(node["style"]["text"].startswith("#") for node in scene["nodes"]))


if __name__ == "__main__":
    unittest.main()
