"""Deterministic native-adapter preflight; no confirmation-world generation."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
from advaita.continuing import ContinuingLearner
from advaita.structural import StructuralLearner
from advaita.state import canonical
from heaviside_native import ContextOutputs, initial, metrics
from audit_heaviside_native import Native, Heads, replay


class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.setup=initial()

    def test_native_parity_routing_mirroring_and_read_only_reviews(self):
        for b in ('reference','relaxed','combined'):
            for mirror in (False,True):
                a=ContextOutputs(self.setup,b,mirror)
                plain=ContinuingLearner(StructuralLearner.restore(canonical(self.setup['core'])),memory=b)
                for i,y in enumerate(([1,1,0,1]*16),1):
                    external=1-y if mirror else y
                    event=a.observe(external)
                    expected=plain.observe(i,dict(self.setup['target'],y=y))
                    self.assertEqual(event['native_internal'],expected)
                    self.assertEqual(event['outputs']['native'],1-expected[2] if mirror else expected[2])
                    self.assertEqual(a.native.checkpoint(),plain.checkpoint())
                labels=[0,1]*16
                heads=copy.deepcopy(a.checkpoint())
                returned=a.review(labels)
                expected=plain.review(64,[dict(self.setup['target'],y=1-y if mirror else y) for y in labels])
                self.assertEqual(returned['native'],expected)
                self.assertEqual(json.loads(heads)['heads'],json.loads(a.checkpoint())['heads'])
                self.assertEqual(a.native.checkpoint(),plain.checkpoint())
                saved=a.checkpoint();restored=ContextOutputs.restore(saved)
                self.assertEqual(restored.checkpoint(),saved)
                self.assertEqual(a.observe(0),restored.observe(0))
                self.assertEqual(a.checkpoint(),restored.checkpoint())
                off=dict(x=[1,0],a=0,local=[0,0]);before=copy.deepcopy(json.loads(a.checkpoint())['heads'])
                e=a.observe(1,off)
                self.assertFalse(e['target_matched'])
                self.assertTrue(all(p==e['outputs']['native'] for p in e['outputs'].values()))
                self.assertEqual(before,json.loads(a.checkpoint())['heads'])

    def test_independent_references_on_synthetic_trajectory(self):
        for b in ('reference','relaxed','combined'):
            a=ContextOutputs(self.setup,b,True);labels=([0,0,1,0]*32)+([1,1,0,1]*32)
            selections={str(t):[1 if t>128 else 0]*32 for t in (64,128,192,256)}
            events=[];reviews=[]
            for i,y in enumerate(labels,1):
                events.append(a.observe(y))
                if str(i) in selections:reviews.append(a.review(selections[str(i)]))
                if i==128:
                    s=a.checkpoint();a=ContextOutputs.restore(s);self.assertEqual(a.checkpoint(),s)
            n=Native(self.setup['core'],b);heads=Heads(self.setup)
            replay(n,heads,self.setup,True,labels,selections,events,reviews)
            checkpoint=json.loads(a.checkpoint());n.verify_state(checkpoint['native']);heads.verify(checkpoint['heads'])

    def test_metrics_observe_the_post_second_review_interval(self):
        ps=[.9]*128+[.1]*128+[.5]*256
        m=metrics(ps,[0]*512,'reversal',False)
        self.assertAlmostEqual(m['primary'],.01)
        self.assertAlmostEqual(m['early'],.81)
        self.assertAlmostEqual(m['late'],.25)
        self.assertEqual(m['recovery_seen'],128)
        self.assertEqual(metrics([.9]*509+[.1]*3,[0]*512,'reversal',False)['recovery_capped'],512)
        self.assertEqual(metrics([.9]*508+[.1]*4,[0]*512,'reversal',False)['recovery_seen'],508)


def main():
    out=ROOT/'results/heaviside-native-fixtures';out.mkdir(exist_ok=True)
    path=out/f"attempt-{len(list(out.glob('attempt-*.json')))+1:02d}.json"
    log=io.StringIO();start=time.monotonic()
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    sources=['experiments/heaviside_native.py','checks/test_heaviside_native.py','checks/audit_heaviside_native.py']
    with path.open('x') as f:
        json.dump(dict(status='pass' if result.wasSuccessful() else 'failed',date='2026-11-13',tests=result.testsRun,
            confirmation_worlds=0,log=log.getvalue(),elapsed_seconds=time.monotonic()-start,
            sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources}),f,indent=2);f.write('\n')
    print(log.getvalue());print(path);return not result.wasSuccessful()


if __name__=='__main__':sys.exit(main())
