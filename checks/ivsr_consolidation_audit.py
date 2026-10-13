"""Audit fast/slow response differences and paired consolidation.

Standard library only. No training experiment or external interaction.
"""

import math
import random
import unittest


def tv(first, second):
    return 0.5 * sum(abs(a - b) for a, b in zip(first, second))


def sigmoid(value):
    return 1 / (1 + math.exp(-value))


def softmax(scores):
    values = [math.exp(v - max(scores)) for v in scores]
    return [v / sum(values) for v in values]


def trigger(current, smoothed, threshold):
    return current > threshold and smoothed > threshold


def transfer(fast, slow, fraction, bound_fast=8, bound_slow=8, mask=1):
    lo = max(-bound_slow - slow, fast - bound_fast)
    hi = min(bound_slow - slow, fast + bound_fast)
    return max(lo, min(hi, fraction * mask * fast))


class ConsolidationAudit(unittest.TestCase):
    def test_distance_and_signed_gap(self):
        self.assertEqual(tv([1, 0], [0, 1]), 1)
        rng = random.Random(0)
        for _ in range(200):
            slow = softmax([rng.uniform(-4, 4) for _ in range(4)])
            fast = softmax([rng.uniform(-4, 4) for _ in range(4)])
            distance = tv(fast, slow)
            self.assertGreaterEqual(distance, 0)
            self.assertLessEqual(distance, 1)
            self.assertEqual(tv(slow, slow), 0)
            self.assertEqual(distance, tv(slow, fast))
            self.assertAlmostEqual(sum(a - n for a, n in zip(fast, slow)), 0)

    def test_binary_distance(self):
        for a, n in ((0.8, 0.5), (0.2, 0.5), (0, 1), (0.3, 0.3)):
            self.assertAlmostEqual(tv([a, 1 - a], [n, 1 - n]), abs(a - n))

    def test_context_average_keeps_local_information(self):
        gaps = [0.6, -0.6]
        self.assertEqual(sum(gaps) / len(gaps), 0)
        self.assertAlmostEqual(sum(abs(g) for g in gaps) / len(gaps), 0.6)
        # Signed changes in different contexts must not cancel before distance.

    def test_smoothed_trigger_and_current_gate(self):
        smoothed, decisions = 0, []
        for current in (0.4, 0.4, 0.4):
            smoothed = 0.75 * smoothed + 0.25 * current
            decisions.append(trigger(current, smoothed, 0.2))
        self.assertEqual(decisions, [False, False, True])
        self.assertFalse(trigger(0, smoothed, 0.2))
        # Smoothing is heuristic: a sufficiently large single spike can pass.
        self.assertTrue(trigger(1, 0.25 * 1, 0.2))
        self.assertFalse(trigger(0.2, 0.4, 0.2))

    def test_same_distance_opposite_external_selection(self):
        slow = 0.5
        distances, gains = [], []
        for fast in (0.8, 0.2):
            residual = math.log(fast / (1 - fast))
            candidate_slow = sigmoid(0.5 * residual)
            distances.append(tv([fast, 1 - fast], [slow, 1 - slow]))
            # External target is success; gain is old minus new log loss.
            gains.append(math.log(candidate_slow / slow))
        self.assertAlmostEqual(distances[0], distances[1])
        self.assertAlmostEqual(gains[0], math.log(4 / 3))
        self.assertAlmostEqual(gains[1], math.log(2 / 3))
        decisions = [trigger(d, d, 0.1) and g > 0 for d, g in zip(distances, gains)]
        self.assertEqual(decisions, [True, False])

    def test_agreement_can_be_wrong(self):
        slow = fast = 0.01
        self.assertEqual(tv([fast, 1 - fast], [slow, 1 - slow]), 0)
        self.assertGreater(-math.log(fast), 4)  # External target: success.

    def test_invisible_fast_weight(self):
        context = [0, 1]
        slow, residual = [0, 0], [4, 0]
        n = sigmoid(sum(x * w for x, w in zip(context, slow)))
        a = sigmoid(sum(x * (s + f) for x, s, f in zip(context, slow, residual)))
        self.assertEqual(tv([a, 1 - a], [n, 1 - n]), 0)
        self.assertNotEqual(residual, [0, 0])

    def test_bounded_transfer_conserves_predictions_and_retention(self):
        rng = random.Random(1)
        for _ in range(1000):
            fast = [rng.uniform(-8, 8) for _ in range(4)]
            slow = [rng.uniform(-8, 8) for _ in range(4)]
            fractions = [rng.random() for _ in range(4)]
            changes = [transfer(f, s, k) for f, s, k in zip(fast, slow, fractions)]
            next_fast = [f - c for f, c in zip(fast, changes)]
            next_slow = [s + c for s, c in zip(slow, changes)]
            old_prediction = softmax([f + s for f, s in zip(fast, slow)])
            new_prediction = softmax([f + s for f, s in zip(next_fast, next_slow)])
            for old, new in zip(old_prediction, new_prediction):
                self.assertAlmostEqual(old, new, places=12)
            for f, s, fn, sn, c in zip(fast, slow, next_fast, next_slow, changes):
                self.assertLessEqual(abs(fn), 8 + 1e-12)
                self.assertLessEqual(abs(sn), 8 + 1e-12)
                self.assertAlmostEqual(f + s, fn + sn, places=12)
                for d in (0, 1, 5, 20):
                    actual = .95**d * (fn - f) + .999**d * (sn - s)
                    self.assertAlmostEqual(actual, (.999**d - .95**d) * c, places=12)

    def test_locked_and_saturated_components(self):
        self.assertEqual(transfer(4, 2, 0.5, mask=0), 0)
        self.assertEqual(transfer(4, 8, 0.5), 0)
        self.assertEqual(transfer(-4, -8, 0.5), 0)
        self.assertEqual(transfer(4, 7.5, 0.5), 0.5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
