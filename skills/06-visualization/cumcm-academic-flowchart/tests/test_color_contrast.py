import unittest

from _support import make_ir
from color_engine import contrast_ratio, validate_color
from layout_candidates import build_layout
from style_engine import apply_theme


class ColorContrastTests(unittest.TestCase):
    def test_journal_theme_passes(self):
        scene, theme = apply_theme(build_layout(make_ir(), "left_to_right"), "journal-rich")
        self.assertTrue(validate_color(scene, theme, True)["passed"])

    def test_black_white_contrast(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#FFFFFF"), 21.0, places=1)

    def test_semantics_not_color_only(self):
        scene, theme = apply_theme(build_layout(make_ir(), "left_to_right"), "journal-rich")
        report = validate_color(scene, theme, True)
        self.assertIn("shape", report["colorblind_strategy"])
        self.assertGreaterEqual(report["semantic_color_count"], 3)


if __name__ == "__main__":
    unittest.main()
