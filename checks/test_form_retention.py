import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'experiments'))
from nested_abstractions import LocalLearner, LocalModel
from form_retention import Learner, Retention, evaluate, generate, snapshot, truth


def rows(form, n=32):
    return [{'x': x, 'y': form[x]} for _ in range(n//4) for x in range(4)]


class FormRetentionTests(unittest.TestCase):
    def setUp(self):
        self.a = [0, 0, 1, 1]
        self.b = [1, 0, 0, 1]
        self.incumbent = LocalModel(self.a, rows(self.a, 128))
        self.challenger = LocalModel([0, 1, 1, 0], rows(self.b, 128))

    def decide(self, policy, batch, incumbent=None, challenger=None):
        a = incumbent or self.incumbent
        b = challenger or self.challenger
        return policy.decide(a, b, a.loss(batch), b.loss(batch), batch)

    def test_immediate_is_original_local_rule(self):
        original, new = LocalLearner(22), Learner(22, 'immediate')
        for i, row in enumerate(rows(self.a, 192), 1):
            original.update(row)
            new.update(row)
            if i % 64 == 0:
                old = original.review(rows(self.a))
                detail = new.review(rows(self.a))
                self.assertEqual(old, detail['ordinary'])
                self.assertEqual(original.model.state(), new.model.state())
                self.assertEqual(original.costs, new.costs)
                self.assertEqual(original.rng.getstate(), new.rng.getstate())

    def test_earned_does_not_gate_unestablished_acquisition(self):
        collapsed = LocalModel(rows=rows(self.a, 128))
        p = Retention('earned')
        model, d = self.decide(p, rows(self.a), collapsed, self.incumbent)
        self.assertEqual(d['action'], 'immediate')
        self.assertEqual(model.state(), self.incumbent.state())
        self.assertFalse(p.established)
        self.assertEqual(p.adequate, 0)

    def test_two_adequate_batches_earn_latched_protection(self):
        p = Retention('earned')
        self.decide(p, rows(self.a))
        self.assertFalse(p.established)
        self.decide(p, rows(self.a))
        self.assertTrue(p.established)
        _, d = self.decide(p, rows(self.b))
        self.assertEqual(d['action'], 'pending_started')
        self.assertTrue(p.established)
        self.assertEqual(p.adequate, 0)

    def test_uniform_needs_two_witnesses_and_freezes_challenger(self):
        p = Retention('uniform')
        model, d = self.decide(p, rows(self.b))
        self.assertEqual(d['action'], 'pending_started')
        self.assertEqual(model.state(), self.incumbent.state())
        saved = copy.deepcopy(p.pending)
        changed = LocalModel(self.challenger.partition, rows(self.a, 128))
        model, d = self.decide(p, rows(self.b), challenger=changed)
        self.assertEqual(d['action'], 'confirmed')
        self.assertEqual(model.state(), saved)
        self.assertIsNone(p.pending)
        self.assertEqual(p.costs['pending_predictions'], 32)

    def test_failed_pending_blocks_new_proposal_in_same_review(self):
        p = Retention('uniform')
        self.decide(p, rows(self.b))
        # A fresh perfect A candidate would beat this weak incumbent, but the
        # pending B hypothesis must fail without starting A in the same batch.
        weak = LocalModel(rows=rows(self.a, 128))
        _, d = self.decide(p, rows(self.a), weak, self.incumbent)
        self.assertEqual(d['action'], 'pending_failed')
        self.assertIsNone(p.pending)
        self.assertFalse(d['accepted'])

    def test_adequacy_is_consecutive_and_acceptance_clears_establishment(self):
        p = Retention('earned')
        self.decide(p, rows(self.a))
        # Same challenger as incumbent prevents a replacement while loss is bad.
        self.decide(p, rows(self.b), challenger=self.incumbent)
        self.assertEqual(p.adequate, 0)
        self.decide(p, rows(self.a))
        self.assertFalse(p.established)
        self.decide(p, rows(self.a))
        self.assertTrue(p.established)
        self.decide(p, rows(self.b))
        _, d = self.decide(p, rows(self.b))
        self.assertTrue(d['accepted'])
        self.assertFalse(p.established)
        self.assertEqual(p.adequate, 0)

    def test_world_pairing_and_corruption_are_distinct_from_truth(self):
        a, b, c = [generate(919, branch) for branch in ('persistent', 'remap', 'transient')]
        self.assertEqual(a['main'][:512], b['main'][:512])
        self.assertEqual(b['main'][512:576], c['main'][512:576])
        self.assertEqual(a['main'][576:], c['main'][576:])
        self.assertEqual(b['selection'][8], c['selection'][8])
        self.assertEqual(a['selection'][9:], c['selection'][9:])
        self.assertEqual(truth(c, 550), a['forms'][0])
        self.assertEqual(truth(c, 550, True), b['forms'][1])
        self.assertNotEqual(truth(c, 550), truth(c, 550, True))

    def test_evaluation_and_selection_never_train_or_mutate_pending(self):
        node = Learner(31, 'uniform')
        for row in rows(self.a, 64):
            node.update(row)
        before_buffer = copy.deepcopy(node.buffer)
        node.review(rows(self.a))
        self.assertEqual(node.buffer, before_buffer)
        before = snapshot(node)
        evaluate(node.model, self.a)
        self.assertEqual(before, snapshot(node))
        self.assertIsNotNone(node.policy.pending)
        saved = copy.deepcopy(node.policy.pending)
        p = node.model.predict(0)
        node.policy.pending['counts']['0'] = [1000, 1000]
        self.assertEqual(p, node.model.predict(0))
        node.policy.pending = saved
        node.update({'x': 0, 'y': 1})
        self.assertEqual(node.policy.pending, saved)


if __name__ == '__main__':
    unittest.main()
