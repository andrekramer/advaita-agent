"""Boundary and update checks for the first learning experiment."""

import math
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from tiny_mapping import FastSlowLearner, balanced_cues, evaluate, log_loss


class TinyMappingChecks(unittest.TestCase):
    def test_predictions_are_target_free_and_read_only(self):
        model = FastSlowLearner()
        before = model.state()
        self.assertEqual(model.predict("A"), 0.5)
        self.assertEqual(model.predict("B"), 0.5)
        self.assertEqual(model.state(), before)

    def test_external_target_controls_the_direction(self):
        positive, negative = FastSlowLearner(), FastSlowLearner()
        self.assertEqual(positive.observe("A", 1), 0.5)
        self.assertEqual(negative.observe("A", 0), 0.5)
        self.assertAlmostEqual(positive.fast[0], 0.10)
        self.assertAlmostEqual(positive.slow[0], 0.01)
        self.assertAlmostEqual(positive.predict("A"), 0.5274723043445937)
        self.assertAlmostEqual(negative.predict("A"), 1 - positive.predict("A"))
        self.assertEqual(positive.predict("B"), 0.5)

    def test_inactive_relations_decay_and_bounds_hold(self):
        model = FastSlowLearner(fast=[0, -1], slow=[0, -0.2])
        model.observe("A", 1)
        self.assertAlmostEqual(model.fast[1], -0.95)
        self.assertAlmostEqual(model.slow[1], -0.1998)
        saturated = FastSlowLearner(fast=[-8, 8], slow=[-8, 8])
        saturated.observe("A", 0)
        self.assertTrue(all(abs(w) <= 8 for w in saturated.fast + saturated.slow))

    def test_gradient_matches_external_log_loss(self):
        model = FastSlowLearner(fast=[0.3, 0], slow=[-0.1, 0])
        p = model.predict("A")
        step = 1e-6
        model.fast[0] += step
        plus = log_loss(model.predict("A"), 1)
        model.fast[0] -= 2 * step
        minus = log_loss(model.predict("A"), 1)
        self.assertAlmostEqual((plus - minus) / (2 * step), -(1 - p), places=8)

    def test_evaluation_preserves_state_and_frozen_baseline(self):
        cues = balanced_cues(40, 10000)
        self.assertEqual(cues.count("A"), 20)
        self.assertEqual(cues.count("B"), 20)
        model = FastSlowLearner(fast=[-0.3, 0.2], slow=[-0.1, 0.3])
        before = model.state()
        evaluate(model, cues)
        self.assertEqual(model.state(), before)
        baseline = evaluate(FastSlowLearner(), cues)
        self.assertEqual(baseline["accuracy"], 0.5)
        self.assertAlmostEqual(baseline["mean_log_loss"], math.log(2))


if __name__ == "__main__":
    unittest.main(verbosity=2)
