import copy
import itertools
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'))
from nested_abstractions import LocalModel, Upper, evaluate, target, view_for
from reclosure import Reclosure, effective_world, generate


def fixture(breach=False):
    models = [LocalModel((0, 1, 0, 1), [
        {'x': x, 'y': x % 2} for _ in range(32) for x in range(4)]) for j in range(2)]
    rows = [{'x': [l, r], 'a': a, 'y': (l % 2) ^ (r % 2) ^ a ^ (int(l >= 2) if breach else 0)}
            for _ in range(8) for l, r, a in itertools.product(range(4), range(4), range(2))]
    fine = Upper('fine0', rows, models)
    coarse = Upper('coarse', rows, models)
    return models, rows, fine, coarse


def decision(fine, rows, models, accepted=False):
    return {'accepted': accepted, 'old_loss': fine.loss(rows, models)}


class ReclosureTests(unittest.TestCase):
    def test_two_witnesses_required_and_challenger_not_refitted(self):
        models, rows, fine, coarse = fixture()
        policy = Reclosure()
        result, first = policy.review(fine, coarse.state(), models, rows[:32], decision(fine, rows[:32], models))
        self.assertEqual(first['action'], 'awaiting_witness')
        self.assertEqual(result.mode, 'fine0')
        frozen = policy.state()['model']
        changed_candidate = Upper('coarse', [dict(r, y=1-r['y']) for r in rows], models)
        result, second = policy.review(fine, changed_candidate.state(), models, rows[32:64],
                                       decision(fine, rows[32:64], models))
        self.assertEqual(second['action'], 'reclosed')
        self.assertEqual(result.state(), frozen)
        self.assertIsNone(policy.pending)

    def test_failed_witness_resets_consecutive_evidence(self):
        models, rows, fine, coarse = fixture()
        p = Reclosure()
        p.review(fine, coarse.state(), models, rows[:32], decision(fine, rows[:32], models))
        bad = [dict(r, y=1-r['y']) for r in rows[32:64]]
        _, detail = p.review(fine, coarse.state(), models, bad, decision(fine, bad, models))
        self.assertEqual(detail['action'], 'witness_failed')
        self.assertIsNone(p.pending)
        _, detail = p.review(fine, coarse.state(), models, rows[64:96], decision(fine, rows[64:96], models))
        self.assertEqual(detail['action'], 'awaiting_witness')

    def test_changed_exported_groups_invalidate_old_evidence(self):
        models, rows, fine, coarse = fixture()
        p = Reclosure()
        p.review(fine, coarse.state(), models, rows[:32], decision(fine, rows[:32], models))
        models[0] = LocalModel((0, 0, 1, 1), [{'x': x, 'y': int(x >= 2)} for _ in range(32) for x in range(4)])
        fresh = Upper('coarse', rows, models)
        _, detail = p.review(fine, fresh.state(), models, rows[32:64], decision(fine, rows[32:64], models))
        self.assertTrue(detail['invalidated'])
        self.assertEqual(detail['witness']['prior_passes'], 0)
        self.assertNotEqual(detail['action'], 'reclosed')

    def test_failure_replacement_has_priority(self):
        models, rows, fine, coarse = fixture()
        p = Reclosure()
        p.review(fine, coarse.state(), models, rows[:32], decision(fine, rows[:32], models))
        reads = p.costs['challenger_predictions']
        result, detail = p.review(fine, coarse.state(), models, rows[32:64],
                                  decision(fine, rows[32:64], models, accepted=True))
        self.assertEqual(detail['action'], 'ordinary_replacement')
        self.assertEqual(result.state(), fine.state())
        self.assertIsNone(p.pending)
        self.assertEqual(p.costs['challenger_predictions'], reads)

    def test_relevant_hidden_detail_is_not_reclosed(self):
        models, rows, fine, coarse = fixture(breach=True)
        p = Reclosure()
        for i in (0, 32, 64):
            batch = rows[i:i+32]
            result, detail = p.review(fine, coarse.state(), models, batch, decision(fine, batch, models))
            self.assertEqual(detail['action'], 'witness_failed')
            self.assertEqual(result.mode, 'fine0')
        self.assertEqual(p.costs['accepted_reclosures'], 0)

    def test_pending_model_not_used_by_predictions_or_mutated_by_feedback(self):
        models, rows, fine, coarse = fixture()
        p = Reclosure()
        saved = copy.deepcopy((fine.state(), coarse.state(), [m.state() for m in models]))
        result, _ = p.review(fine, coarse.state(), models, rows[:32], decision(fine, rows[:32], models))
        self.assertEqual(saved, (fine.state(), coarse.state(), [m.state() for m in models]))
        p.pending['model']['counts']['0|0|0'] = [1000, 1000]
        view = view_for([0, 0], models, result.mode)
        self.assertEqual(result.predict(view, 0), fine.predict(view_for([0, 0], models, fine.mode), 0))
        self.assertEqual(view.raw_reads, 1)

    def test_transient_switch_preserves_pairing_and_noise(self):
        persistent, breach, transient = [generate(909, b) for b in ('persistent', 'breach', 'transient')]
        for field in ('forms', 'representatives', 'affected', 'local_main', 'local_selection', 'composition'):
            self.assertEqual(transient[field], persistent[field])
            self.assertEqual(transient[field], breach[field])
        self.assertEqual(transient['main'][:384], breach['main'][:384])
        self.assertEqual(transient['main'][384:], persistent['main'][384:])
        self.assertEqual(transient['selection'][:6], breach['selection'][:6])
        self.assertEqual(transient['selection'][6:], persistent['selection'][6:])

    def test_evaluation_and_coarse_boundary_are_pure(self):
        models, rows, fine, coarse = fixture()
        p = Reclosure()
        p.review(fine, coarse.state(), models, rows[:32], decision(fine, rows[:32], models))
        w = {'forms': [[0, 1, 0, 1]]*2, 'representatives': [[0, 1]]*2,
             'affected': 0, 'branch': 'transient'}
        before = copy.deepcopy((p.state(), p.costs, fine.state(), [m.state() for m in models]))
        evaluate(fine, models, effective_world(w, 768), True)
        self.assertEqual(before, (p.state(), p.costs, fine.state(), [m.state() for m in models]))
        view = view_for([0, 0], models, 'coarse')
        with self.assertRaises(PermissionError):
            view.raw(0)


if __name__ == '__main__':
    unittest.main()
