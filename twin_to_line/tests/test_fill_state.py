import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fill_state import resolve_state, infer_fill_count, resolve_fixture

S = lambda i, K, v: resolve_state(i, K, v)[0]


class ResolveState(unittest.TestCase):
    def test_k0_everything_waits(self):
        self.assertEqual({S(i, 0, "no_vial") for i in range(1, 31)}, {"WAITING"})

    def test_partially_filled(self):
        K = 12
        self.assertEqual(S(1, K, "pass"), "PASS")
        self.assertEqual(S(7, K, "missing_cap"), "DEFECT")
        self.assertEqual(S(8, K, "crooked_cap"), "DEFECT")
        self.assertEqual(S(9, K, "damaged_vial"), "DEFECT")
        self.assertEqual(S(13, K, "no_vial"), "WAITING")
        self.assertEqual(S(30, K, "no_vial"), "WAITING")

    def test_skipped_position_inside_prefix_is_missed(self):
        self.assertEqual(S(5, 12, "no_vial"), "MISSED")
        self.assertEqual(S(1, 1, "no_vial"), "MISSED")

    def test_final_filled_position(self):
        self.assertEqual(S(12, 12, "pass"), "PASS")
        self.assertEqual(S(12, 12, "no_vial"), "MISSED")
        self.assertEqual(S(12, 12, "missing_cap"), "DEFECT")

    def test_positions_after_k(self):
        self.assertEqual(S(13, 12, "no_vial"), "WAITING")
        self.assertEqual(S(13, 12, "pass"), "UNSURE")           # a vial where none should be yet
        self.assertEqual(S(20, 12, "missing_cap"), "UNSURE")

    def test_full_fixture(self):
        self.assertEqual(S(30, 30, "pass"), "PASS")
        self.assertEqual(S(30, 30, "no_vial"), "MISSED")
        self.assertEqual(S(1, 30, "no_vial"), "MISSED")

    def test_unknown_fill_count(self):
        self.assertEqual(S(4, None, "pass"), "PASS")
        self.assertEqual(S(4, None, "missing_cap"), "DEFECT")
        self.assertEqual(S(4, None, "no_vial"), "UNSURE")

    def test_unknown_visual_is_unsure(self):
        for K in (None, 0, 12, 30):
            self.assertEqual(S(5, K, "unknown"), "UNSURE")

    def test_reason_text(self):
        self.assertEqual(resolve_state(7, 12, "missing_cap"), ("DEFECT", "missing_cap"))
        self.assertIn("K=12", resolve_state(5, 12, "no_vial")[1])

    def test_bad_inputs(self):
        for K in (-1, 31, 2.0, "3", True):
            with self.assertRaises(ValueError):
                resolve_state(1, K, "pass")
        for i in (0, 31):
            with self.assertRaises(ValueError):
                resolve_state(i, 5, "pass")
        with self.assertRaises(ValueError):
            resolve_state(1, 5, "GOOD")


class InferFillCount(unittest.TestCase):
    def fx(self, occupied, other="no_vial"):
        return ["pass" if i in occupied else other for i in range(1, 31)]

    def test_empty_fixture(self):
        self.assertEqual(infer_fill_count(self.fx(set())), 0)

    def test_prefix_with_gap(self):
        v = self.fx({1, 2, 3, 5, 6})
        self.assertEqual(infer_fill_count(v), 6)
        K, src, states = resolve_fixture(v, infer=True)
        self.assertEqual((K, src), (6, "inferred"))
        self.assertEqual(states[3][0], "MISSED")              # G04 skipped
        self.assertEqual(states[6][0], "WAITING")

    def test_defect_counts_as_occupied(self):
        v = self.fx({1, 2}); v[2] = "missing_cap"
        self.assertEqual(infer_fill_count(v), 3)

    def test_unknown_does_not_extend_k(self):
        v = self.fx({1, 2}); v[9] = "unknown"
        self.assertEqual(infer_fill_count(v), 2)

    def test_last_placement_miss_is_invisible(self):
        # robot placed G01-G05 but skipped G06: occupancy alone cannot tell G06 from waiting
        self.assertEqual(infer_fill_count(self.fx({1, 2, 3, 4, 5})), 5)

    def test_given_beats_inferred(self):
        K, src, states = resolve_fixture(self.fx({1, 2}), fill_count=3, infer=True)
        self.assertEqual((K, src, states[2][0]), (3, "given", "MISSED"))

    def test_unknown_k(self):
        K, src, states = resolve_fixture(self.fx({1}))
        self.assertEqual((K, src, states[0][0], states[1][0]), (None, "unknown", "PASS", "UNSURE"))

    def test_wrong_length(self):
        with self.assertRaises(ValueError):
            infer_fill_count(["pass"] * 29)


if __name__ == "__main__":
    unittest.main()
