"""Synthetic checks only; do not run benchmark learners during development."""
import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from bundles import Learner, Model, POOL, evaluate, generate, single_world


class BundlesTests(unittest.TestCase):
    def test_beta_counting_and_unseen_cell(self):
        model = Model((2,), [{'x': [0, 0, 1, 0, 0, 0], 'a': 0, 'y': 1}] * 3)
        self.assertEqual(model.predict([0, 0, 1, 0, 0, 0], 0), .8)
        self.assertEqual(model.predict([0, 0, 1, 0, 0, 0], 1), .5)
        self.assertEqual(model.predict([0] * 6, 0), .5)

    def test_joint_information_not_in_either_single_input(self):
        rows = [{'x': list(x), 'a': a, 'y': x[0] ^ x[1] ^ a}
                for x in itertools.product((0, 1), repeat=6) for a in (0, 1)]
        joint = Model((0, 1), rows)
        for row in rows:
            self.assertEqual(joint.predict(row['x'], row['a']) > .5, bool(row['y']))
            for feature in (0, 1):
                self.assertEqual(Model((feature,), rows).predict(row['x'], row['a']), .5)

    def test_prediction_does_not_inspect_hidden_inputs(self):
        class Restricted:
            def __getitem__(self, index):
                if index not in (1, 4):
                    raise AssertionError('Access to hidden feature')
                return 1
        self.assertEqual(Model((1, 4)).predict(Restricted(), 0), .5)

    def test_proposal_budget_and_deterministic_coverage(self):
        m = Learner('deterministic')
        m.update({'x': [0] * 6, 'a': 0, 'y': 0})
        observed = set()
        for _ in range(6):
            _, review = m.prepare()
            subsets = [tuple(c['subset']) for c in review['candidates']]
            self.assertEqual(len(subsets), 4)
            self.assertEqual(len(set(subsets)), 4)
            self.assertNotIn((), subsets)
            observed.update(subsets)
        self.assertEqual(observed, set(POOL) - {()})
        for variant in ('stochastic', 'singleton'):
            first, second = Learner(variant, 93), Learner(variant, 93)
            for learner in (first, second):
                learner.update({'x': [0] * 6, 'a': 0, 'y': 0})
            self.assertEqual(first.prepare()[1], second.prepare()[1])
            self.assertLessEqual(max(len(c['subset']) for c in first.prepare()[1]['candidates']),
                                 1 if variant == 'singleton' else 2)

    def test_window_expiration_without_reset(self):
        learner = Learner('stochastic', 93)
        for y in [1] * 192 + [0] * 64:
            learner.update({'x': [0] * 6, 'a': 0, 'y': y})
        self.assertEqual(len(learner.buffer), 192)
        self.assertEqual(learner.model.counts[0], [128, 192])

    def test_selection_does_not_fit_or_enter_buffer(self):
        rows = [{'x': [bit, 0, 0, 0, 0, 0], 'a': 0, 'y': bit} for bit in (0, 1)] * 16
        learner = Learner('stochastic', 93)
        for row in rows:
            learner.update(row)
        candidate = Model((0,), rows)
        before = copy.deepcopy((learner.buffer, candidate.state()))
        decision = learner.select(candidate, rows[:2])
        self.assertTrue(decision['accepted'])
        self.assertEqual((learner.buffer, candidate.state()), before)
        self.assertEqual(learner.costs['selection_outcomes'], 2)

    def test_frozen_evaluation_and_input_cut(self):
        world = {'permutation': list(range(6)), 'branch': 'persistent'}
        learner = Learner('stochastic', 93)
        rows = [{'x': list(x), 'a': a, 'y': x[0] ^ x[1] ^ a}
                for x in itertools.product((0, 1), repeat=6) for a in (0, 1)]
        learner.model = Model((0, 1), rows)
        before = copy.deepcopy((learner.model.state(), learner.buffer, learner.costs,
                                learner.rng.getstate(), learner.cursor))
        result = evaluate(learner, world, 64)
        self.assertEqual(result['accuracy'], 1)
        self.assertTrue(result['exact_structure'])
        self.assertEqual(result['nuisance_effect'], 0)
        self.assertTrue(all(x > .2 for x in result['cut_loss_increase'].values()))
        self.assertEqual(result['additional_ablation_predictions'], 256)
        self.assertEqual((learner.model.state(), learner.buffer, learner.costs,
                          learner.rng.getstate(), learner.cursor), before)

    def test_world_pairing_boundaries_and_rng_separation(self):
        changed, persistent = generate(97, 'reversible'), generate(97, 'persistent')
        self.assertEqual(changed, generate(97, 'reversible'))
        self.assertEqual(len(changed['main']), 1152)
        self.assertEqual([len(b) for b in changed['selection']], [32] * 18)
        t = changed['permutation'].index(1)
        for index, (a, b) in enumerate(zip(changed['main'], persistent['main']), 1):
            self.assertEqual((a['x'], a['a']), (b['x'], b['a']))
            self.assertEqual(a['y'] ^ b['y'], a['x'][t] if 384 < index <= 768 else 0)
            self.assertEqual(set(a), {'x', 'a', 'y'})
        self.assertEqual([single_world('reversible', t) for t in (384, 385, 768, 769)],
                         [False, True, True, False])
        rng = Learner('stochastic', 93).rng.getstate()
        generate(98, 'persistent')
        self.assertEqual(Learner('stochastic', 93).rng.getstate(), rng)


if __name__ == '__main__':
    unittest.main()
