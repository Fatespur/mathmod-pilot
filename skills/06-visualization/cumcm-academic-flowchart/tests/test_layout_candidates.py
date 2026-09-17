import unittest

from _support import make_ir
from layout_candidates import build_layout, generate_layout_candidates
from validate_layout import validate_layout


class LayoutCandidateTests(unittest.TestCase):
    def test_at_least_four_candidates(self):
        self.assertGreaterEqual(len(generate_layout_candidates(make_ir(), seed=42)), 4)

    def test_required_layout_families_build(self):
        names = [
            "left_to_right", "dual_stream", "question_swimlane", "hub_spoke",
            "circular_cycle", "rectangular_loop", "u_shaped", "serpentine",
            "concentric", "matrix", "layered_architecture", "fan_in",
        ]
        for name in names:
            with self.subTest(name=name):
                layout = build_layout(make_ir(), name)
                self.assertEqual(len(layout["nodes"]), len(make_ir()["nodes"]))

    def test_feedback_routes_generate(self):
        layout = build_layout(make_ir(feedback=True), "rectangular_loop")
        self.assertTrue(any(edge["feedback"] for edge in layout["edges"]))

    def test_multi_question_swimlane(self):
        layout = build_layout(make_ir(multi=True), "question_swimlane")
        self.assertEqual(layout["layout_family"], "swimlane")

    def test_seed_reproducibility(self):
        left = build_layout(make_ir(), "serpentine", seed=9)
        right = build_layout(make_ir(), "serpentine", seed=9)
        self.assertEqual(left["nodes"], right["nodes"])

    def test_routes_have_no_zero_length_segments(self):
        names = [
            "left_to_right", "dual_stream", "question_swimlane", "hub_spoke",
            "circular_cycle", "rectangular_loop", "u_shaped", "serpentine",
            "concentric", "matrix", "layered_architecture", "fan_in",
        ]
        for name in names:
            with self.subTest(name=name):
                layout = build_layout(make_ir(feedback=True), name)
                for edge in layout["edges"]:
                    self.assertTrue(
                        all(start != end for start, end in zip(edge["points"], edge["points"][1:])),
                        f"{name}/{edge['id']} contains a zero-length segment: {edge['points']}",
                    )
                self.assertEqual(validate_layout(layout)["degenerate_edge_segments"], [])


if __name__ == "__main__":
    unittest.main()
