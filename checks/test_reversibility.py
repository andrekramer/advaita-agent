"""Synthetic fixtures and schedule checks, not benchmark pilot runs."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from reversibility import Learner, acquisition_pass, delay, evaluate, phase, stream


class ReversibilityTests(unittest.TestCase):
    def test_phase_boundaries_and_review_world(self):
        self.assertEqual([phase(t) for t in (108, 109, 144, 192, 228, 229, 240, 336)],
                         ['A1', 'B', 'B', 'B', 'B', 'A2', 'A2', 'A2'])

    def test_generated_evidence_and_withholding(self):
        perm, main, selection = stream(7)
        self.assertEqual((perm, main, selection), stream(7))
        self.assertEqual((len(main), len(selection)), (336, 7))
        relevant = perm.index(0)
        for index, r in enumerate(main, 1):
            self.assertNotIn(tuple(r['x']), ((0, 0, 0), (1, 1, 1)))
            self.assertEqual(r['y'], r['a'] if phase(index) == 'B' else r['x'][relevant] ^ r['a'])
            self.assertEqual(set(r), {'x', 'a', 'y'})
        for review, batch in enumerate(selection, 1):
            self.assertEqual(len({(tuple(r['x']), r['a']) for r in batch}), 12)
            for r in batch:
                self.assertNotIn(tuple(r['x']), ((0, 0, 0), (1, 1, 1)))
                self.assertEqual(r['y'], r['a'] if phase(review * 48) == 'B' else r['x'][relevant] ^ r['a'])

    def test_mixed_windows_are_not_reset(self):
        m = Learner(True)
        for _ in range(48):
            m.update((0, 1, 0), 0, 1)
        for _ in range(36):
            m.update((0, 1, 0), 0, 0)
        self.assertEqual(m.model.counts, [[[12, 48], [0, 0]]])
        for _ in range(48):
            m.update((0, 1, 0), 0, 0)
        for _ in range(12):
            m.update((0, 1, 0), 0, 1)
        self.assertEqual(m.model.counts, [[[12, 48], [0, 0]]])
        self.assertEqual(m.seen, 144)

    def test_one_form_can_split_again_from_new_evidence(self):
        m = Learner(True)
        batch = [{'x': [s, 0, 1], 'a': a, 'y': s ^ a} for s in (0, 1) for a in (0, 1)]
        for _ in range(12):
            for r in batch:
                m.update(r['x'], r['a'], r['a'])
        self.assertEqual(len(m.model.counts), 1)
        for _ in range(12):
            for r in batch:
                m.update(**r)
        candidate, _ = m.prepare()
        before = copy.deepcopy(m.buffer)
        decision = m.select(candidate, batch)
        self.assertTrue(decision['accepted'])
        self.assertFalse(decision['merge'])
        self.assertEqual(m.buffer, before)
        self.assertTrue(acquisition_pass(evaluate(m, 0, False)['metrics']))

    def test_evaluation_isolated_in_each_world(self):
        m = Learner(True)
        m.update((1, 0, 1), 0, 1)
        before = copy.deepcopy((m.state(), m.buffer, m.costs))
        for collapsed in (False, True, False):
            ev = evaluate(m, 0, collapsed)
            self.assertEqual(ev['before'], ev['after'])
            self.assertEqual(len(ev['withheld']), 4)
            self.assertEqual((m.state(), m.buffer, m.costs), before)

    def test_delay_counts_only_post_change_selection(self):
        self.assertIsNone(delay(None, 108))
        self.assertEqual(delay(192, 108), {'review': 192, 'main_since_change': 84, 'selection_since_change': 24})
        self.assertEqual(delay(240, 228), {'review': 240, 'main_since_change': 12, 'selection_since_change': 12})
        self.assertEqual(delay(288, 228), {'review': 288, 'main_since_change': 60, 'selection_since_change': 24})


if __name__ == '__main__':
    unittest.main()
