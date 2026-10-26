"""Small synthetic C1 integration tests, charged once before the benchmark."""
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
import protection_interfaces as experiment
from protection_interfaces_metrics import summarize
from audit_protection_interfaces import verify_world, verify_run, truth


class InteractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds = [experiment.generate(990, b, sizes=(4, 1, 8, 4, 4, 1), review_every=4)
                      for b in experiment.BRANCHES]

    def test_small_streams_are_independently_reconstructible_and_paired(self):
        for w in self.worlds:
            verify_world(w, review_every=4)
            self.assertEqual(w['main'], self.worlds[0]['main'])
            self.assertEqual(w['local_main'], self.worlds[0]['local_main'])

    def test_only_the_local_channel_is_corrupted_and_boundaries_are_exact(self):
        persistent, remap, burst = self.worlds
        for t in (0, 128, 129, 192, 193, 512):
            for w in self.worlds:
                self.assertEqual(experiment.forms_at(w, t), truth(w, t))
                self.assertEqual(experiment.forms_at(w, t, True), truth(w, t, True))
            self.assertEqual(experiment.forms_at(burst, t), persistent['forms'])
            self.assertEqual(experiment.forms_at(burst, t, True) != persistent['forms'], 128 < t <= 192)
            self.assertEqual(experiment.forms_at(remap, t) != persistent['forms'], t > 128)

    def test_all_four_combinations_match_independent_state_replay(self):
        for variant in experiment.VARIANTS:
            r, checkpoint = experiment.run(self.worlds[0], variant, 990, review_every=4, measure=False)
            self.assertEqual(r['costs']['feedback_labels'], 48)
            verify_run(r, self.worlds[0], json.loads(checkpoint), review_every=4, measure=False)

    def test_zero_control_errors_do_not_prove_protection_and_gate_is_separate(self):
        scalar = ('main_observed', 'main_latent', 'main_affected_latent', 'change_observed', 'change_latent',
                  'change_affected_latent', 'burst_latent', 'burst_affected_latent', 'confirmation_censored',
                  'raw_reads', 'bypass_wrong_records', 'invalid_affected_checkpoints')
        m = dict.fromkeys(scalar, 0)
        m.update({f: True for f in ('transfer_valid', 'final_valid', 'final_predictive_valid', 'final_local_valid', 'coarse_final_valid')})
        m.update(reopen_reviews=[], reclosure_reviews=[])
        # Synthetic metric records, not generated observation streams or learner seeds.
        runs = [dict(seed=s, proposal_seed=p, branch=b, variant=v, metrics=copy.deepcopy(m))
                for s in range(5) for p in range(2) for b in experiment.BRANCHES for v in experiment.VARIANTS]
        summary = summarize(runs)
        self.assertFalse(summary['primary_pass'])
        self.assertTrue(summary['progression_gate'])
        for r in runs:
            if r['variant'] == 'immediate_reclosure' and r['seed'] < 2:
                r['metrics']['final_valid'] = False
        self.assertFalse(summarize(runs)['progression_gate'])


if __name__ == '__main__':
    out = ROOT/'results/protection-interfaces-fixtures.json'
    if out.exists():
        raise FileExistsError('Fixture invocation already recorded; do not silently spend the remaining budget again')
    stream, start = io.StringIO(), time.monotonic()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(InteractionTests))
    files = ['experiments/protection_interfaces.py', 'experiments/protection_interfaces_metrics.py',
             'checks/audit_protection_interfaces.py', 'checks/test_protection_interfaces.py']
    record = dict(status='pass' if result.wasSuccessful() else 'failed', tests=result.testsRun,
                  charged_labels=336, elapsed_seconds=time.monotonic()-start, log=stream.getvalue(),
                  tested_sources={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in files})
    out.write_text(json.dumps(record, indent=2)+'\n')
    print(stream.getvalue())
    print(json.dumps({k: v for k, v in record.items() if k not in ('log', 'tested_sources')}, indent=2))
    sys.exit(not result.wasSuccessful())
