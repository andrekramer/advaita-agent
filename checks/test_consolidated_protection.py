"""020 synthetic contracts and metric boundaries; no reserved worlds."""
import copy
import gzip
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
from advaita.corroboration import CorroboratedLocal, CorroboratedLearner
from advaita.models import LocalModel
from consolidated_protection import generate, run, FILES, BRANCHES, POLICIES
from consolidated_protection_metrics import metrics, summarize
from audit_consolidated_protection import verify_world, verify_run, verify_metrics, verify_summary

LABELS=0


class ProtectionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global LABELS
        cls.worlds=[generate(1990,b,sizes=(4,1,8,4,4,1),review_every=4) for b in BRANCHES]
        LABELS+=144

    def node(self, changed=True):
        global LABELS
        n=CorroboratedLocal(1990); n.structural=True
        original=[dict(x=i%4,y=int(i%4>=2)) for i in range(192)]
        n.model=LocalModel((0,0,1,1),original)
        n.buffer=[dict(x=i%4,y=i%2 if changed else int(i%4>=2)) for i in range(192)]
        n.deck=[(0,1,0,1),(0,0,0,1),(0,0,1,0),(0,1,1,1)]
        LABELS+=384
        return n

    def test_tiny_streams_and_both_full_checkpoints(self):
        global LABELS
        for w in self.worlds: verify_world(w,review_every=4)
        for p in POLICIES:
            r,checkpoint=run(self.worlds[0],p,1990,review_every=4,measure=False)
            LABELS+=r['costs']['feedback_labels']
            verify_run(r,self.worlds[0],json.loads(checkpoint),review_every=4,measure=False)
            if p=='corroborated':
                learner=CorroboratedLearner.restore(checkpoint)
                self.assertEqual(learner.checkpoint(),checkpoint)
                learner.nodes[0].protection.update(established=True,pending=learner.nodes[0].model.state())
                clone=CorroboratedLearner.restore(learner.checkpoint())
                self.assertEqual(learner.checkpoint(),clone.checkpoint())
                row=dict(x=[0,0],a=0,local=[0,0],y=0)
                self.assertEqual(learner.step('extra',row),clone.step('extra',row)); LABELS+=6
                self.assertEqual(learner.review('extra-review',[row]*4),clone.review('extra-review',[row]*4)); LABELS+=24
                self.assertEqual(learner.checkpoint(),clone.checkpoint())
                before=learner.checkpoint()
                with self.assertRaises(ValueError): learner.review('extra-review',[row]*4)
                self.assertEqual(before,learner.checkpoint())

    def test_pending_model_is_frozen_and_requires_another_witness(self):
        global LABELS
        n=self.node(); n.protection.update(established=True,adequate=2)
        incumbent=n.model.state()
        batch=[dict(x=i%4,y=i%2) for i in range(32)]
        first=n.review(batch); LABELS+=32
        self.assertEqual(first['protection']['action'],'awaiting_confirmation')
        self.assertEqual(n.model.state(),incumbent)
        frozen=copy.deepcopy(n.protection['pending'])
        n.update(dict(x=0,y=1)); LABELS+=1
        self.assertEqual(n.protection['pending'],frozen)
        second=n.review(batch); LABELS+=32
        self.assertEqual(second['protection']['action'],'confirmed')
        self.assertEqual(n.model.state(),frozen)
        self.assertFalse(n.protection['established'])

    def test_failed_confirmation_does_not_replace_incumbent(self):
        global LABELS
        n=self.node(); n.protection.update(established=True,adequate=2)
        incumbent=n.model.state()
        n.review([dict(x=i%4,y=i%2) for i in range(32)]); LABELS+=32
        result=n.review([dict(x=i%4,y=int(i%4>=2)) for i in range(32)]); LABELS+=32
        self.assertEqual(result['protection']['action'],'confirmation_failed')
        self.assertEqual(n.model.state(),incumbent)
        self.assertIsNone(n.protection['pending'])

    def test_protection_is_earned_only_after_two_adequate_reviews(self):
        global LABELS
        n=self.node(changed=False)
        batch=[dict(x=i%4,y=int(i%4>=2)) for i in range(32)]
        n.review(batch); LABELS+=32
        self.assertFalse(n.protection['established'])
        n.review(batch); LABELS+=32
        self.assertTrue(n.protection['established'])

    def test_metrics_independent_arithmetic_and_zero_error_baseline(self):
        old=ROOT/'results/consolidated-recovery-v1'
        with gzip.open(old/'runs.jsonl.gz','rt') as f: r=json.loads(next(f))
        w=json.loads((old/'worlds.json').read_text())[0]
        # Reinterpret saved evidence as a fabricated stable-world arithmetic
        # fixture. This is never used as an experimental run or world audit.
        r['branch']=w['branch']='persistent'; r['policy']='baseline'
        r['pre_specs']=[[1,1] for _ in w['main']]
        r['pre_local_exact']=[[True,True] for _ in w['main']]
        r['metrics']=metrics(r,w); verify_metrics(r,w)
        runs=[]
        for s in range(1990,1995):
            for ps in (1990,1991):
                for b in BRANCHES:
                    for p in POLICIES:
                        m=copy.deepcopy(r['metrics']); m.update(transfer_valid=True,final_full=True,
                            affected_errors=2 if p=='baseline' else 1,recovery_for_comparison=256 if p=='baseline' else 320)
                        for k in ('composite_observed','composite_latent','affected_latent'):
                            m[k]=0 if p=='baseline' else (.05 if b=='remap' else .02)
                        runs.append(dict(seed=s,proposal_seed=ps,branch=b,policy=p,metrics=m))
        summary=summarize(runs); verify_summary(runs,summary)
        self.assertTrue(summary['primary_pass'])
        for rr in runs:
            if rr['branch']=='persistent': rr['metrics']['affected_errors']=0
        summary=summarize(runs); verify_summary(runs,summary)
        self.assertFalse(summary['checks']['persistent_error_benefit'])


if __name__=='__main__':
    path=ROOT/'results/consolidated-protection-fixtures.json'
    if path.exists(): raise FileExistsError('Preserve previous fixture attempt')
    started,stream=time.monotonic(),io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ProtectionTests))
    record=dict(status='pass' if result.wasSuccessful() and LABELS<=2000 else 'failed',tests=result.testsRun,
        charged_labels=LABELS,elapsed_seconds=time.monotonic()-started,log=stream.getvalue(),
        sources={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES})
    path.write_text(json.dumps(record,indent=2)+'\n')
    print(stream.getvalue()); print('Charged fixture labels:',LABELS)
    sys.exit(record['status']!='pass')
