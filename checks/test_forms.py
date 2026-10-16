"""Synthetic correctness fixtures; does not run benchmark seeds."""
import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from forms import (Baseline, CONTEXTS, FormModel, ROOT, Structural, canonical,
                   collapse, evaluate, features, group_for, neighbours, validate)


class FormsTests(unittest.TestCase):
    def test_split_refit_preserves_real_counts(self):
        rows = [{'x': [0, 0, 1], 'a': 0, 'y': 1},
                {'x': [1, 0, 1], 'a': 1, 'y': 0},
                {'x': [1, 1, 0], 'a': 1, 'y': 1}]
        for structure in neighbours(ROOT):
            m = FormModel.fit(structure, rows)
            self.assertEqual(sum(n for group in m.counts for _, n in group), 3)
            self.assertEqual(sum(r for group in m.counts for r, _ in group), 2)
            for group in m.counts:
                for r, n in group:
                    self.assertLessEqual(r, n)
                    self.assertGreaterEqual(r, 0)
        split = canonical([((0, -1, -1), 0), ((1, -1, -1), 1)])
        m = FormModel.fit(split, rows[:1])
        self.assertEqual(m.predict((1, 1, 1), 0), .5)
        self.assertEqual(m.predict((0, 0, 0), 0), 2 / 3)

    def test_merge_collapses_geometry(self):
        leaves = [(x, 0) for x in CONTEXTS]
        self.assertEqual(collapse(leaves), ROOT)
        split = canonical([((-1, 0, -1), 0), ((-1, 1, -1), 1)])
        self.assertIn(ROOT, neighbours(split))
        merged = FormModel.fit(ROOT, [{'x': [0, 0, 0], 'a': 0, 'y': 1},
                                     {'x': [1, 1, 1], 'a': 0, 'y': 0}])
        self.assertEqual(merged.counts[0][0], [1, 2])

    def test_candidate_coverage_caps_and_determinism(self):
        frontier = {ROOT}
        for _ in range(3):
            frontier = {n for s in frontier for n in neighbours(s)}
        for structure in sorted(frontier):
            validate(structure)
            pool = neighbours(structure)
            self.assertEqual(pool, neighbours(structure))
            self.assertEqual(pool, sorted(set(pool)))
            self.assertLessEqual(len(pool), 31)
            for candidate in pool:
                validate(candidate)

    def test_provisional_update_and_retention(self):
        dual, single = Structural(True), Structural(False)
        old = copy.deepcopy(dual.model.state())
        for m in (dual, single):
            m.update((1, 0, 1), 0, 1)
        self.assertEqual(dual.model.state(), old)
        self.assertEqual(dual.provisional.state(), single.model.state())
        self.assertEqual(dual.predict((1, 0, 1), 0), .5)
        self.assertEqual(single.predict((1, 0, 1), 0), 2 / 3)

    def test_selection_is_not_training_and_rejects_harm(self):
        learner = Structural(True)
        for _ in range(8):
            learner.update((1, 0, 0), 0, 1)
        candidate, _ = learner.prepare([((1, 0, 0), 0)])
        old_buffer = copy.deepcopy(learner.buffer)
        old_model = learner.model.state()
        outcome = learner.select(candidate, [{'x': [1, 0, 0], 'a': 0, 'y': 0}])
        self.assertFalse(outcome['accepted'])
        self.assertEqual(learner.buffer, old_buffer)
        self.assertEqual(learner.model.state(), old_model)
        self.assertEqual(learner.provisional.counts[0][0], [8, 8])

    def test_acceptance_promotes_without_copy_alias(self):
        learner = Structural(True)
        for _ in range(8):
            learner.update((0, 1, 0), 1, 1)
        candidate, _ = learner.prepare([((0, 1, 0), 1)])
        decision = learner.select(candidate, [{'x': [0, 1, 0], 'a': 1, 'y': 1}])
        self.assertTrue(decision['accepted'])
        retained = learner.model.state()
        learner.update((0, 1, 0), 1, 0)
        self.assertEqual(learner.model.state(), retained)
        self.assertEqual(learner.provisional.counts[0][1], [8, 9])

    def test_baseline_update_and_unseen_prior(self):
        lookup = Baseline('lookup')
        lookup.update((0, 0, 1), 1, 1)
        self.assertEqual(lookup.predict((0, 0, 1), 1), 2 / 3)
        self.assertEqual(lookup.predict((1, 0, 1), 1), .5)
        fixed = Baseline('fixed_features')
        fixed.update((0, 1, 0), 1, 1)
        self.assertEqual(fixed.weights, [.05 * f for f in features((0, 1, 0), 1)])
        self.assertEqual(fixed.clips, 0)

    def test_evaluation_does_not_mutate_any_state(self):
        for learner in (Structural(False), Structural(True),
                        Baseline('lookup'), Baseline('fixed_features')):
            learner.update((0, 1, 0), 1, 0)
            old = copy.deepcopy(learner.state())
            result = evaluate(learner, 2)
            self.assertEqual(learner.state(), old)
            self.assertEqual(len(result['table']), 16)
            self.assertEqual(len(result['withheld']), 4)


if __name__ == '__main__':
    unittest.main()
