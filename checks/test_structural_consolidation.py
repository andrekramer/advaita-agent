"""C2 synthetic contracts, within the remaining round fixture budget."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'experiments'), str(ROOT/'checks')]
import structural_consolidation as experiment
from advaita.structural import StructuralLearner, ReducingLocal, JointModel
from advaita.models import LocalModel
from audit_structural_consolidation import verify_world, verify_run, truth, label

LABELS = 0


class StructuralTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global LABELS
        cls.worlds = [experiment.generate(990, b, sizes=(4, 1, 8, 4, 4, 1), review_every=4) for b in experiment.BRANCHES]
        LABELS += 3*48

    def test_streams_boundaries_and_reversed_return_are_independently_defined(self):
        for w in self.worlds:
            verify_world(w, review_every=4)
            for t in (0, 240, 241, 528, 529, 768):
                self.assertEqual(experiment.forms_at(w, t), truth(w, t))
                for x in ([0, 0], [1, 3]):
                    self.assertEqual(experiment.target(w, x, 1, t), label(w, x, 1, t))
        self.assertEqual(self.worlds[1]['main'], self.worlds[2]['main'])
        for x in ([0, 1], [3, 2]):
            self.assertEqual(experiment.target(self.worlds[1], x, 0, 529), 1-experiment.target(self.worlds[2], x, 0, 529))

    def test_all_four_variants_match_independent_checkpoint_replay(self):
        global LABELS
        for v in experiment.VARIANTS:
            r, checkpoint = experiment.run(self.worlds[0], v, 990, review_every=4, measure=False)
            LABELS += r['costs']['feedback_labels']
            verify_run(r, self.worlds[0], json.loads(checkpoint), review_every=4, measure=False)
            restored = StructuralLearner.restore(checkpoint)
            self.assertEqual(restored.checkpoint(), checkpoint)
            before = restored.checkpoint()
            restored.predict([0, 1], 0)
            self.assertEqual(before, restored.checkpoint())

    def test_collapse_requires_two_witnesses_and_can_be_recreated(self):
        global LABELS
        n = ReducingLocal(990)
        n.structural = True
        # A supplied empty two-group state isolates reduction from acquisition.
        n.model = LocalModel((0, 0, 1, 1))
        for i in range(64): n.update(dict(x=i % 4, y=0))
        LABELS += 64
        batch = [dict(x=i % 4, y=0) for i in range(8)]
        a = n.review(batch); LABELS += 8
        self.assertEqual(a['action'], 'awaiting_reduction')
        frozen = copy.deepcopy(n.pending)
        n.update(dict(x=0, y=0)); LABELS += 1
        self.assertEqual(n.pending, frozen)
        b = n.review(batch); LABELS += 8
        self.assertEqual(b['action'], 'collapsed')
        for i in range(64): n.update(dict(x=i % 4, y=int(i % 4 >= 2)))
        LABELS += 64
        n.deck = [(0, 0, 1, 1), (0, 0, 0, 1), (0, 0, 1, 0), (0, 1, 1, 1)]
        c = n.review([dict(x=i % 4, y=int(i % 4 >= 2)) for i in range(8)]); LABELS += 8
        self.assertEqual(c['action'], 'improved')
        self.assertEqual(n.model.state()['groups'], [0, 0, 1, 1])

    def test_capture_at_reduction_frozen_memory_semantics_and_pending_restore(self):
        global LABELS
        learner = StructuralLearner([990, 991], 990, 'fixed')
        rows = [dict(x=[0, 0], a=0, local=[0, 0], y=0) for _ in range(32)]
        ids = [f'init/{i}' for i in range(32)]
        learner.train_upper(ids, rows); LABELS += 32
        # Supplied fine state isolates capture timing; the benchmark never injects it.
        learner.deploy(JointModel((2, 1), rows, learner.models()), learner.dependencies((2, 1)), ids)
        first = learner.review('first', rows[:4]); LABELS += 4
        self.assertEqual(first['upper']['action'], 'awaiting_reduction')
        self.assertIsNone(learner.archive.entry)
        clone = StructuralLearner.restore(learner.checkpoint())
        second = learner.review('second', rows[:4]); LABELS += 4
        other = clone.review('second', rows[:4]); LABELS += 4
        self.assertEqual(second, other)
        self.assertEqual(learner.checkpoint(), clone.checkpoint())
        self.assertEqual(second['upper']['action'], 'reduced')
        self.assertEqual(learner.archive.entry.capture_event, 'second')
        archived = learner.archive.state()
        learner.step('new', dict(x=[0, 0], a=0, local=[0, 0], y=1)); LABELS += 3
        self.assertEqual(learner.archive.state(), archived)
        learner.nodes[1].model = LocalModel((0, 1, 0, 1))
        review = learner.review('changed', rows[:4]); LABELS += 4
        self.assertFalse(review['upper']['archive_check']['compatible'])
        self.assertEqual(learner.archive.state(), archived)
        view = JointModel((0, 1)).view([0, 0], learner.models())
        with self.assertRaises(PermissionError): view.read((0, 2))


if __name__ == '__main__':
    path = ROOT/'results/structural-consolidation-fixtures.json'
    if path.exists(): raise FileExistsError('Fixture record exists; preserve budget and prior attempts')
    start, stream = time.monotonic(), io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(StructuralTests))
    files = ['advaita/structural.py', 'experiments/structural_consolidation.py', 'experiments/structural_consolidation_metrics.py',
             'checks/structural_reference.py', 'checks/audit_structural_consolidation.py', 'checks/test_structural_consolidation.py']
    record = dict(status='pass' if result.wasSuccessful() and LABELS <= 720 else 'failed',
        tests=result.testsRun, charged_labels=LABELS, elapsed_seconds=time.monotonic()-start, log=stream.getvalue(),
        tested_sources={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files})
    path.write_text(json.dumps(record, indent=2)+'\n')
    print(stream.getvalue()); print('Charged synthetic labels:', LABELS)
    sys.exit(record['status'] != 'pass')
