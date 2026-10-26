"""019 harness checks on fabricated records; no fresh learning or reserved seeds."""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'experiments'), str(ROOT/'checks'), str(ROOT)]
from consolidated_recovery import FILES
from consolidated_recovery_metrics import score, summarize, BRANCHES, VARIANTS
from audit_consolidated_recovery import verify_recovery, verify_summary


class HarnessTests(unittest.TestCase):
    def setUp(self):
        old = ROOT/'results/structural-consolidation-v1'
        with gzip.open(old/'runs.jsonl.gz', 'rt') as stream: self.r = json.loads(next(stream))
        worlds = json.loads((old/'worlds.json').read_text())
        self.w = next(w for w in worlds if (w['seed'], w['branch']) == (self.r['seed'], self.r['branch']))
        # Deliberately fabricated extension for arithmetic tests, never a world run.
        self.w['main'] += copy.deepcopy(self.w['main'][-512:])
        self.r['predictions'] += self.r['predictions'][-512:]
        self.r['raw_reads'] += self.r['raw_reads'][-512:]
        last = self.r['reviews'][-1]
        for t in range(832, 1281, 64):
            v = copy.deepcopy(last)
            v['index'] = v['evaluation']['index'] = t
            self.r['reviews'].append(v)

    def test_reference_window_is_preserved_and_new_metrics_agree_independently(self):
        original = self.r['metrics']
        self.r['recovery'] = score(self.r, self.w)
        self.assertEqual(self.r['recovery']['reference_768'], original)
        verify_recovery(self.r, self.w)

    def test_one_good_final_checkpoint_cannot_hide_instability(self):
        self.r['transfer'].update(accuracy=1, regret=0, local_exact=[True, True])
        for v in self.r['reviews']:
            if v['index'] >= 1024:
                v['evaluation'].update(accuracy=1, regret=0, local_exact=[True, True],
                    sufficient_minimal=True, spec=[1, 1])
        self.r['recovery'] = score(self.r, self.w)
        self.assertTrue(self.r['recovery']['stable_structural'])
        next(v for v in self.r['reviews'] if v['index'] == 1088)['evaluation']['accuracy'] = .9
        self.r['recovery'] = score(self.r, self.w)
        self.assertTrue(self.r['recovery']['checkpoints'][-1]['structural'])
        self.assertFalse(self.r['recovery']['stable_predictive'])
        self.assertFalse(self.r['recovery']['stable_structural'])
        verify_recovery(self.r, self.w)

    def test_denominators_pairing_and_thresholds(self):
        base = score(self.r, self.w)
        runs = []
        for seed in range(1900, 1905):
            for ps in (1900, 1901):
                for branch in BRANCHES:
                    for variant in VARIANTS:
                        m = copy.deepcopy(base)
                        m['stable_structural'] = seed != 1900
                        m['return_observed'] = .47 if branch == 'detail' and variant == 'integrated' else .5
                        runs.append(dict(seed=seed, proposal_seed=ps, branch=branch, variant=variant,
                            recovery=m, predictions=[.5]))
        s = summarize(runs)
        verify_summary(runs, s)
        self.assertTrue(s['representation_pass'])  # exactly 8/10
        self.assertTrue(s['memory_pass'])
        self.assertEqual(len(s['environments']), 15)
        self.assertTrue(all(e['proposals'] == 2 for e in s['environments']))
        r = next(r for r in runs if (r['seed'], r['proposal_seed'], r['branch'], r['variant']) == (1901, 1900, 'forms', 'integrated'))
        r['recovery']['stable_structural'] = False
        r['recovery']['reference_768']['transfer_valid'] = False
        s = summarize(runs)
        verify_summary(runs, s)
        self.assertFalse(s['representation_pass'])  # 7/10, failure not dropped
        self.assertEqual(next(g['runs'] for g in s['groups'] if (g['branch'], g['variant']) == ('forms', 'integrated')), 10)


if __name__ == '__main__':
    path = ROOT/'results/consolidated-recovery-fixtures.json'
    if path.exists(): raise FileExistsError('Preserve the previous fixture attempt')
    started, stream = time.monotonic(), io.StringIO()
    result = unittest.TextTestRunner(stream=stream, verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(HarnessTests))
    record = dict(status='pass' if result.wasSuccessful() else 'failed', tests=result.testsRun,
        new_learning_labels=0, elapsed_seconds=time.monotonic()-started, log=stream.getvalue(),
        sources={name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES})
    path.write_text(json.dumps(record, indent=2)+'\n')
    print(stream.getvalue())
    sys.exit(not result.wasSuccessful())
