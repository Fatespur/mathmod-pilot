import unittest

from _support import make_ir
from layout_candidates import generate_layout_candidates
from layout_selector import select_layouts
from quality_review import dual_layout_review


class DualLayoutTests(unittest.TestCase):
    def test_different_families_and_diversity(self):
        primary, alternative, _ = select_layouts(generate_layout_candidates(make_ir(feedback=True), seed=42))
        result = dual_layout_review(primary, alternative)
        self.assertTrue(result["passed"])
        self.assertGreaterEqual(result["layout_diversity_score"], 0.55)

    def test_node_and_key_edge_sets_equal(self):
        primary, alternative, _ = select_layouts(generate_layout_candidates(make_ir(), seed=42))
        result = dual_layout_review(primary, alternative)
        self.assertTrue(result["node_sets_equal"])
        self.assertTrue(result["key_edges_equal"])

    def test_same_family_rejected(self):
        candidates = generate_layout_candidates(make_ir(), seed=42, forced=["left_to_right", "top_to_bottom"])
        left, right = candidates[0], candidates[1]
        left["layout_diversity_score"] = right["layout_diversity_score"] = 0.9
        self.assertFalse(dual_layout_review(left, right)["passed"])


if __name__ == "__main__":
    unittest.main()
