"""Mathematical and data-boundary checks, not extra benchmark runs."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from small_reversal import (Learner, STATES, VARIANTS, balanced_cues, evaluate,
                            recovery_trial, teacher_mappings)


class SmallReversalChecks(unittest.TestCase):
    def test_four_states_and_reference_are_normalized_read_only(self):
        model = Learner("fast_slow")
        for cue in STATES:
            self.assertEqual(model.predict(cue), [0.25] * 4)
        before = model.state()
        model.predict("00")
        self.assertEqual(model.state(), before)
        with self.assertRaises(ValueError):
            model.predict(None)

    def test_neither_input_is_observed_and_external_target_controls_update(self):
        first, second = Learner("fast_slow"), Learner("fast_slow")
        self.assertEqual(first.observe("00", "10"), [0.25] * 4)
        second.observe("00", "00")
        self.assertAlmostEqual(first.weights["fast"][0][0], 0.15)
        self.assertAlmostEqual(first.weights["slow"][0][0], 0.015)
        self.assertEqual(first.weights["fast"][1], [0.0] * 3)
        self.assertGreater(first.predict("00")[1], 0.25)
        self.assertGreater(second.predict("00")[0], 0.25)

    def test_gradient_finite_difference_including_reference_target(self):
        for target in STATES:
            model = Learner("fast_slow")
            model.weights["fast"][2] = [0.3, -0.2, 0.1]
            probabilities = model.predict("01")
            for k in range(3):
                initial = model.weights["fast"][2][k]
                step = 1e-6
                model.weights["fast"][2][k] = initial + step
                plus = -math.log(model.predict("01")[STATES.index(target)])
                model.weights["fast"][2][k] = initial - step
                minus = -math.log(model.predict("01")[STATES.index(target)])
                model.weights["fast"][2][k] = initial
                expected = probabilities[k + 1] - float(target == STATES[k + 1])
                self.assertAlmostEqual((plus - minus) / (2 * step), expected, places=8)

    def test_controls_match_initial_effective_step_and_bounds(self):
        for variant in ("fast_slow", "fast_only", "slow_only"):
            model = Learner(variant)
            model.observe("11", "01")
            combined = [sum(matrix[3][k] for matrix in model.weights.values()) for k in range(3)]
            for actual, expected in zip(combined, [-0.055, 0.165, -0.055]):
                self.assertAlmostEqual(actual, expected)
            self.assertEqual(sum(p[2] for p in VARIANTS[variant].values()), 16)

    def test_inactive_decay_and_projection(self):
        model = Learner("fast_slow")
        model.weights["fast"][1] = [1.0] * 3
        model.weights["slow"][1] = [1.0] * 3
        # An out-of-bound fixture tests projection without a long training run.
        model.weights["fast"][2][0] = 20
        model.observe("00", "11")
        self.assertEqual(model.weights["fast"][1], [0.95] * 3)
        self.assertEqual(model.weights["slow"][1], [0.999] * 3)
        self.assertEqual(model.weights["fast"][2][0], 8)
        self.assertEqual(model.clipping_count, 1)
        model.validate()

    def test_balanced_data_derangements_and_frozen_evaluation(self):
        for seed in range(5):
            first, second = teacher_mappings(seed)
            self.assertEqual(set(first.values()), set(STATES))
            self.assertEqual(set(second.values()), set(STATES))
            self.assertTrue(all(first[cue] != second[cue] for cue in STATES))
            cues = balanced_cues(100, 3000 + seed)
            self.assertTrue(all(cues.count(cue) == 25 for cue in STATES))
            model = Learner("frozen")
            model.observe("11", "10")
            result = evaluate(model, cues, first)
            self.assertEqual(result["accuracy"], 0.25)
            self.assertAlmostEqual(result["mean_log_loss"], math.log(4))
        model = Learner("fast_slow")
        model.observe("11", "10")
        before = model.state()
        evaluate(model, cues, second)
        self.assertEqual(model.state(), before)

    def test_recovery_requires_full_post_change_window(self):
        self.assertIsNone(recovery_trial([{"correct": True}] * 39))
        self.assertEqual(recovery_trial([{"correct": False}] * 10 + [{"correct": True}] * 40), 46)
        self.assertIsNone(recovery_trial([{"correct": False}] * 400))


if __name__ == "__main__":
    unittest.main(verbosity=2)
