"""Synthetic mechanism tests; no benchmark learner executions."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'experiments'))
from bundle_retention import Learner, Model, POOL, evaluate, metrics


def record(y):
    return {'x': [0]*6, 'a': 0, 'y': y}


class RetentionTests(unittest.TestCase):
    def test_deck_covers_pool_and_no_review_duplicates(self):
        learner = Learner('deck_single', 907)
        learner.update(record(1))
        visited = set()
        for _ in range(6):
            _, review = learner.prepare()
            proposals = [tuple(c['subset']) for c in review['candidates']]
            self.assertEqual(len(set(proposals)), 4)
            self.assertNotIn((), proposals)
            visited.update(proposals)
        self.assertEqual(visited, set(POOL)-{()})
        self.assertEqual(learner.costs['candidate_fits'], 24)
        self.assertGreaterEqual(learner.deck_number, 2)

    def test_shuffle_boundary_and_changing_incumbent(self):
        learner = Learner('deck_split', 908)
        learner.update(record(1))
        learner.deck = [(), (0,)]
        learner.model = Model((0,), [record(1)])
        _, details = learner.prepare()
        proposals = [tuple(c['subset']) for c in details['candidates']]
        self.assertEqual(len(proposals), len(set(proposals)))
        self.assertEqual(len(proposals), 4)
        self.assertNotIn((0,), proposals)
        self.assertEqual(learner.deck_number, 1)

    def test_split_vetoes_positive_pooled_gain(self):
        candidate = Model((0,), [record(1)]*8)  # .9 for the observed cell
        rows = [record(1)]*24 + [record(0)]*8
        single, split = Learner('iid_single', 907), Learner('iid_split', 907)
        before = copy.deepcopy((candidate.state(), split.buffer))
        a, b = single.select(candidate, rows), split.select(candidate, rows)
        self.assertTrue(a['accepted'])
        self.assertTrue(b['pooled_accept'])
        self.assertFalse(b['accepted'])
        self.assertTrue(b['veto'])
        self.assertGreater(b['half_gains'][0], .005)
        self.assertLess(b['half_gains'][1], .005)
        self.assertEqual((candidate.state(), split.buffer), before)
        self.assertEqual(single.costs, split.costs)
        self.assertEqual(split.costs['selection_outcomes'], 32)

    def test_agreement_accepts_without_fitting(self):
        learner = Learner('deck_split', 907)
        candidate = Model((0,), [record(1)]*8)
        before = candidate.state()
        result = learner.select(candidate, [record(1)]*32)
        self.assertTrue(result['accepted'])
        self.assertFalse(result['veto'])
        self.assertEqual(candidate.state(), before)
        self.assertEqual(learner.buffer, [])

    def test_frozen_evaluation_preserves_search_state(self):
        learner = Learner('deck_split', 907)
        learner.update(record(1))
        learner.prepare()
        before = copy.deepcopy((learner.deck, learner.deck_number, learner.rng.getstate(),
                                learner.buffer, learner.model.state(), learner.costs))
        evaluate(learner, {'permutation': list(range(6)), 'branch': 'persistent'}, 64)
        self.assertEqual((learner.deck, learner.deck_number, learner.rng.getstate(),
                          learner.buffer, learner.model.state(), learner.costs), before)

    def test_endpoint_recovery_does_not_hide_departure(self):
        world = {'main': [record(1)]*1152, 'permutation': list(range(6)), 'branch': 'persistent'}
        evaluations = [
            {'index': t, 'subset': [0,1], 'relevant': [0,1], 'exact_structure': True,
             'accuracy': 1., 'regret': 0., 'cut_loss_increase': {'0': .3, '1': .3}}
            for t in (64,384,768,1152)]
        reviews = [
            {'index': t, 'before': {'subset': a}, 'after': {'subset': b},
             'candidates': [{'subset': b}], 'decision': {'accepted': a != b, 'veto': False}}
            for t,a,b in ((64,[],[0,1]), (384,[0,1],[0,1]), (768,[0,1],[0,1]),
                          (832,[0,1],[2]), (896,[2],[0,1]), (1152,[0,1],[0,1]))]
        result = metrics({'evaluations': evaluations, 'reviews': reviews,
                          'main_predictions': [.9]*1152}, world)
        self.assertTrue(result['endpoint_pass'])
        self.assertEqual(result['correct_pair_departures'], [832])
        self.assertFalse(result['persistent_preservation'])
        self.assertFalse(result['pass'])


if __name__ == '__main__':
    unittest.main()
