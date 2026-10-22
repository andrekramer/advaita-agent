import copy
import itertools
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from advaita.local import LocalLearner
from advaita.models import LocalModel, ProjectionModel, Upper, VisibleInput, view_for
from advaita.policies import Retention, Reclosure
from advaita.runtime import NestedLearner
from advaita.state import Archive, EvidenceLedger, FrozenPredictor, fingerprint

FIXTURE_LABELS = 0


def local_rows(form, n=32):
    global FIXTURE_LABELS
    FIXTURE_LABELS += n
    return [dict(x=i % 4, y=form[i % 4]) for i in range(n)]


def joint_rows(n=32, breach=False):
    global FIXTURE_LABELS
    FIXTURE_LABELS += 3*n
    contexts = list(itertools.product(range(4), range(4), range(2)))
    return [dict(x=[l, r], a=a, local=[l % 2, r % 2],
                 y=(l % 2) ^ (r % 2) ^ a ^ (int(l >= 2) if breach else 0))
            for l, r, a in (contexts[i % 32] for i in range(n))]


def runtime(policy='earned'):
    learner = NestedLearner([991, 992], policy)
    form = [0, 1, 0, 1]
    for j in range(2):
        learner.nodes[j].deck = [(0, 1, 0, 1), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 1, 1)]
        for i, row in enumerate(local_rows(form, 192)):
            learner.observe_local(j, f'warm{j}/{i}', row)
            if (i+1) % 64 == 0:
                batch = local_rows(form)
                learner.review_local(j, [f'warmselect{j}/{i}/{k}' for k in range(32)], batch)
    rows = joint_rows(256)
    learner.train_upper([f'compose/{i}' for i in range(256)], rows)
    return learner


class CoreTests(unittest.TestCase):
    def test_joint_relationship_cannot_be_replaced_by_singletons(self):
        global FIXTURE_LABELS
        rows = [dict(x=[s, t], a=a, y=s ^ t ^ a)
                for _ in range(16) for s, t, a in itertools.product(range(2), repeat=3)]
        FIXTURE_LABELS += len(rows)
        for subset in ((), (0,), (1,)):
            model = ProjectionModel(subset, rows)
            self.assertTrue(all(model.predict(r['x'], r['a']) == .5 for r in rows))
        joint = ProjectionModel((0, 1), rows)
        self.assertTrue(all((joint.predict(r['x'], r['a']) > .5) == bool(r['y']) for r in rows))

    def test_split_collapse_and_recreate_with_the_existing_local_rule(self):
        node = LocalLearner(990)
        for expected, data in [([0, 0, 1, 1], [0, 0, 1, 1]),
                               ([0, 0, 0, 0], [0, 0, 0, 0]),
                               ([0, 0, 1, 1], [0, 0, 1, 1])]:
            for row in local_rows(data, 192):
                node.update(row)
            node.deck = [tuple(expected), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 1, 1)]
            result = node.review(local_rows(data))
            self.assertTrue(result['accepted'])
            self.assertEqual(node.model.state()['groups'], expected)

    def test_hidden_ports_raise_and_allowed_reads_are_counted(self):
        view = VisibleInput([0, 1], [0])
        self.assertEqual(view[0], 0)
        with self.assertRaises(PermissionError):
            _ = view[1]
        self.assertEqual(view.reads, 1)
        models = [LocalModel(), LocalModel()]
        view = view_for([0, 1], models, 'coarse')
        with self.assertRaises(PermissionError):
            view.raw(0)
        self.assertEqual(view.raw_reads, 0)

    def test_archive_requires_same_meaning_not_same_name(self):
        ports = [dict(name='group', domain=[0, 1], meaning=[0, 0, 1, 1])]
        other = [dict(name='group', domain=[0, 1], meaning=[0, 1, 0, 1])]
        snap = FrozenPredictor.capture(LocalModel().state(), ports, 'hide-1', ['main-1'])
        with self.assertRaises(ValueError):
            snap.candidate(other)
        self.assertEqual(snap.candidate(copy.deepcopy(ports)), LocalModel().state())
        # Returning meanings are compatible; arbitrary revision counters are not inputs.
        self.assertEqual(fingerprint(ports), fingerprint(copy.deepcopy(ports)))
        with self.assertRaises(ValueError):
            fingerprint([dict(ports[0], revision=2)])

    def test_snapshot_is_detached_and_archive_eviction_is_bounded(self):
        state = LocalModel().state()
        ports = [dict(name='x', domain=[0, 1], meaning=[0, 1])]
        first = FrozenPredictor.capture(state, ports, 'first', ['m0'])
        state['counts']['0'][0] = 999
        value = first.candidate(ports)
        value['counts']['0'][0] = 888
        self.assertEqual(first.candidate(ports)['counts']['0'][0], 0)
        archive = Archive()
        self.assertIsNone(archive.capture(first))
        second = FrozenPredictor.capture(state, ports, 'second', ['m1'])
        self.assertEqual(archive.capture(second), first)
        self.assertEqual(archive.entry, second)
        self.assertEqual(FrozenPredictor.from_state(json.loads(json.dumps(second.state()))), second)
        self.assertEqual(archive.clear(), second)
        self.assertIsNone(archive.entry)

    def test_evidence_leakage_duplicate_labels_and_false_witnesses_rejected(self):
        ledger = EvidenceLedger()
        ledger.add_main(['m0'])
        ledger.fit(['m0'], 'fit')
        ledger.select(['s0'], 'replace')
        ledger.select(['s0'], 'reclose')
        self.assertEqual(ledger.uses[-1]['reused'], ['s0'])
        for operation in (lambda: ledger.fit(['s0'], 'bad-fit'),
                          lambda: ledger.select(['m0'], 'bad-selection'),
                          lambda: ledger.add_main(['m0']),
                          lambda: ledger.add_main(['s0']),
                          lambda: ledger.select(['s0'], 'replace')):
            with self.assertRaises(ValueError):
                operation()
        restored = EvidenceLedger.from_state(ledger.state())
        self.assertEqual(restored.state(), ledger.state())

    def test_earned_flag_and_pending_evidence_do_not_freeze_predictions(self):
        a, b = [0, 0, 1, 1], [0, 1, 0, 1]
        old, new = LocalModel(a, local_rows(a, 128)), LocalModel(b, local_rows(b, 128))
        p = Retention('earned')
        for _ in range(2):
            rows = local_rows(a)
            p.decide(old, new, old.loss(rows), new.loss(rows), rows)
        self.assertTrue(p.established)
        rows = local_rows(b)
        result, event = p.decide(old, new, old.loss(rows), new.loss(rows), rows)
        self.assertEqual(event['action'], 'pending_started')
        self.assertEqual(result.state(), old.state())
        frozen = copy.deepcopy(p.pending)
        new.counts[0][0] += 100
        self.assertEqual(p.pending, frozen)

    def test_changed_group_map_invalidates_pending_upper_evidence(self):
        models = [LocalModel([0, 1, 0, 1], local_rows([0, 1, 0, 1], 128)) for _ in range(2)]
        rows = joint_rows(64)
        fine, coarse = Upper('fine0', rows, models), Upper('coarse', rows, models)
        policy = Reclosure()
        policy.review(fine, coarse.state(), models, rows[:32],
                      dict(accepted=False, old_loss=fine.loss(rows[:32], models)))
        models[1] = LocalModel([0, 0, 1, 1], local_rows([0, 0, 1, 1], 128))
        fresh = Upper('coarse', rows, models)
        _, event = policy.review(fine, fresh.state(), models, rows[32:],
                                 dict(accepted=False, old_loss=fine.loss(rows[32:], models)))
        self.assertTrue(event['invalidated'])
        self.assertEqual(event['witness']['prior_passes'], 0)

    def test_checkpoint_restores_rng_buffers_and_pending_reclosure(self):
        learner = runtime()
        learner.upper = Upper('fine0', learner.buffer, learner.models())
        learner.upper_binding = fingerprint(learner.dependencies())
        learner.review('s0', joint_rows())
        self.assertIsNotNone(learner.reclosure.pending)
        frozen = copy.deepcopy(learner.reclosure.pending)
        restored = NestedLearner.restore(learner.checkpoint())
        self.assertEqual(learner.checkpoint(), restored.checkpoint())
        for i, row in enumerate(joint_rows(32)):
            self.assertEqual(learner.step(f'm{i}', row), restored.step(f'm{i}', row))
        self.assertEqual(learner.reclosure.pending, frozen)
        batch = joint_rows()
        self.assertEqual(learner.review('s1', batch), restored.review('s1', batch))
        self.assertEqual(learner.upper.mode, 'coarse')
        self.assertEqual(learner.checkpoint(), restored.checkpoint())

    def test_checkpoint_restores_local_protection_pending(self):
        learner = runtime()
        rows = local_rows([0, 0, 1, 1])
        learner.nodes[0].deck = [(0, 0, 1, 1), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 1, 1)]
        # Supply changed main experience before asking for its first witness.
        for i, row in enumerate(local_rows([0, 0, 1, 1], 192)):
            learner.observe_local(0, f'change/{i}', row)
        learner.review_local(0, [f'probe/{i}' for i in range(32)], rows)
        self.assertIsNotNone(learner.nodes[0].policy.pending)
        restored = NestedLearner.restore(learner.checkpoint())
        self.assertEqual(learner.review_local(0, [f'next/{i}' for i in range(32)], rows),
                         restored.review_local(0, [f'next/{i}' for i in range(32)], rows))
        self.assertEqual(learner.checkpoint(), restored.checkpoint())

    def test_prediction_is_pure_and_step_predicts_before_feedback(self):
        learner = runtime('immediate')
        before = learner.checkpoint()
        row = joint_rows()[0]
        prediction = learner.predict(row['x'], row['a'])
        self.assertEqual(before, learner.checkpoint())
        self.assertEqual(prediction, learner.step('m', row))
        before = learner.checkpoint()
        with self.assertRaises(ValueError):
            learner.step('m', row)
        self.assertEqual(before, learner.checkpoint())

    def test_repeated_review_cannot_count_as_fresh_confirmation(self):
        learner = runtime('immediate')
        learner.review('s', joint_rows())
        before = learner.checkpoint()
        with self.assertRaises(ValueError):
            learner.review('s', joint_rows())
        self.assertEqual(before, learner.checkpoint())

    def test_stale_deployed_upper_is_recorded_not_silently_repaired(self):
        learner = runtime('immediate')
        before = learner.upper.state()
        learner.nodes[0].model = LocalModel([0, 0, 1, 1], local_rows([0, 0, 1, 1], 192))
        self.assertNotEqual(learner.upper_binding, fingerprint(learner.dependencies()))
        self.assertEqual(learner.upper.state(), before)


if __name__ == '__main__':
    unittest.main()
