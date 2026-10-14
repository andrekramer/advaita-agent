"""Small synthetic correctness fixtures; no additional benchmark conditions."""

from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from round2 import Model, STATES, blocks_for, evaluate


def strong_fast(variant="hybrid"):
    model = Model(variant)
    model.weights["fast"] = [[4.0, 0, 0] for _ in STATES]
    return model


class RoundTwoChecks(unittest.TestCase):
    def test_external_selection_accepts_correct_rejects_wrong_same_gap(self):
        good, bad = strong_fast(), strong_fast()
        first, second = good.prepare(), bad.prepare()
        self.assertEqual(first["D"], second["D"])
        self.assertTrue(first["gate"])
        accepted = good.consolidate(first, [(c, "10") for c in STATES] * 2)
        rejected = bad.consolidate(second, [(c, "00") for c in STATES] * 2)
        self.assertTrue(accepted["accepted"])
        self.assertFalse(rejected["accepted"])
        self.assertGreater(accepted["gain"], 0)
        self.assertLess(rejected["gain"], 0)
        self.assertEqual(bad.weights["slow"], [[0.0] * 3 for _ in STATES])

    def test_gate_does_not_accept_hidden_selection_labels(self):
        model = Model("hybrid")
        prepared = model.prepare()
        self.assertFalse(prepared["gate"])
        record = model.consolidate(prepared, None)
        self.assertEqual(record["labels_accessed"], 0)
        self.assertIsNone(record["gain"])
        with self.assertRaises(AssertionError):
            model.consolidate(prepared, [(c, "10") for c in STATES] * 2)

    def test_ablation_removes_only_its_named_gate(self):
        unconditional = strong_fast("no_selection")
        record = unconditional.consolidate(unconditional.prepare(), None)
        self.assertTrue(record["accepted"])
        self.assertEqual(record["labels_accessed"], 0)
        no_trigger = Model("no_trigger")
        prepared = no_trigger.prepare()
        self.assertTrue(prepared["gate"])
        self.assertEqual(prepared["D"], 0)
        record = no_trigger.consolidate(prepared, [(c, "10") for c in STATES] * 2)
        self.assertFalse(record["accepted"])  # no improvement despite open trigger

    def test_bounded_transfer_and_delayed_retention_identity(self):
        model = strong_fast("no_selection")
        model.weights["slow"][0][0] = 7.8
        # Saturation limits the transfer, without separately clipping F/S.
        self.assertAlmostEqual(model.proposal()[0][0], 0.2)
        before = model.state()
        prepared = model.prepare()
        model.smoothed = prepared["Dbar"] = 1.0
        prepared["gate"] = True
        record = model.consolidate(prepared, None)
        after = model.state()
        self.assertLess(record["conservation_error"], 1e-12)
        for _ in range(10):
            model.decay()
        for i in range(4):
            for k in range(3):
                c = after["slow"][i][k] - before["slow"][i][k]
                actual = model.weights["fast"][i][k] + model.weights["slow"][i][k]
                control = .95**10 * before["fast"][i][k] + .999**10 * before["slow"][i][k]
                self.assertAlmostEqual(actual - control, (.999**10 - .95**10) * c, places=12)

    def test_transfer_only_has_no_direct_slow_learning(self):
        model = Model("transfer_only")
        for cue in STATES:
            model.observe(cue, "10")
        self.assertEqual(model.weights["slow"], [[0.0] * 3 for _ in STATES])
        model.weights["slow"][0][0] = 1.0
        model.observe("00", "00")
        self.assertEqual(model.weights["slow"][0][0], 0.999)

    def test_evaluation_and_gap_do_not_update_diagnostic(self):
        model = strong_fast()
        model.prepare()
        before = (model.state(), model.smoothed, model.clipping_count)
        mapping = dict(zip(STATES, STATES))
        evaluate(model, mapping)
        evaluate(model, mapping, "slow")
        self.assertEqual(before, (model.state(), model.smoothed, model.clipping_count))
        model.decay()
        self.assertEqual(model.smoothed, before[1])
        self.assertEqual(model.weights["fast"][0][0], 3.8)

    def test_registered_block_budgets_and_paired_stream(self):
        transient, persistent = [blocks_for("noise", s) for s in ("transient", "persistent")]
        self.assertEqual([b[:3] for b in transient[:2]], [b[:3] for b in persistent[:2]])
        for suite, count in (("retention", 720), ("noise", 480), ("consolidation", 720)):
            blocks = blocks_for(suite, "transient")
            self.assertEqual(sum(n for _, n, target, _ in blocks if target is not None), count)


if __name__ == "__main__":
    unittest.main(verbosity=2)
