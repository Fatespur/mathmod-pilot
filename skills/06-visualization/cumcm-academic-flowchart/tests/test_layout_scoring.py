import copy
import unittest

from _support import make_ir
from layout_candidates import build_layout
from layout_scoring import node_overlap_pairs, score_layout
from validate_layout import validate_layout


class LayoutScoringTests(unittest.TestCase):
    def test_clean_layout_scores(self):
        layout = build_layout(make_ir(), "serpentine")
        metrics = score_layout(layout)
        self.assertGreater(metrics["layout_score"], 80)

    def test_overlap_detected(self):
        layout = build_layout(make_ir(), "serpentine")
        layout["nodes"][1]["x"] = layout["nodes"][0]["x"]
        layout["nodes"][1]["y"] = layout["nodes"][0]["y"]
        self.assertTrue(node_overlap_pairs(layout))

    def test_canvas_cropping_detected(self):
        layout = build_layout(make_ir(), "left_to_right")
        layout["nodes"][0]["x"] = -1
        self.assertFalse(validate_layout(layout)["passed"])


if __name__ == "__main__":
    unittest.main()
