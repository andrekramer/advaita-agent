"""021 synthetic contracts; no reserved seeds or benchmark outcomes."""
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
from advaita.prospective_memory import ProspectiveMemory
from advaita.structural import StructuralLearner, JointModel
from advaita.models import LocalModel
from prospective_memory import generate, run, FILES, BRANCHES, POLICIES
from prospective_memory_metrics import metrics, summarize
from audit_prospective_memory import verify_world, verify_run, verify_metrics, verify_summary

LABELS=0


class MemoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        global LABELS
        cls.worlds=[generate(2990,b,sizes=(4,1,8,4,4,1),review_every=4) for b in BRANCHES]
        LABELS+=96

    def build(self,mode='reserve'):
        global LABELS
        n=(StructuralLearner([2990,2991],2990,'delete') if mode=='plain_delete'
           else ProspectiveMemory([2990,2991],2990,mode))
        for j in range(2):
            for x in range(4): n.observe_local(j,f'warm/{j}/{x}',dict(x=x,y=0))
        rows=[dict(x=[0,0],a=0,local=[0,0],y=0) for _ in range(64)]
        ids=[f'composition/{i}' for i in range(64)]
        n.train_upper(ids,rows)
        # Supplied fine state isolates capture mechanics; the benchmark does not inject it.
        n.deploy(JointModel((2,1),rows,n.models()),n.dependencies((2,1)),ids)
        LABELS+=72
        return n,rows[:4]

    def test_small_worlds_and_all_three_full_checkpoints(self):
        global LABELS
        for w in self.worlds: verify_world(w,review_every=4)
        for p in POLICIES:
            r,checkpoint=run(self.worlds[0],p,2990,review_every=4,measure=False)
            LABELS+=r['costs']['feedback_labels']
            verify_run(r,self.worlds[0],json.loads(checkpoint),review_every=4,measure=False)
            if p!='legacy': self.assertEqual(ProspectiveMemory.restore(checkpoint).checkpoint(),checkpoint)

    def test_frozen_confirmation_is_delayed_and_reduction_cannot_overwrite(self):
        global LABELS
        n,batch=self.build()
        first=n.review('one',batch); LABELS+=12
        self.assertEqual(first['upper']['qualification']['action'],'awaiting_confirmation')
        pending=copy.deepcopy(n.reservation['pending'])
        self.assertIsNone(n.archive.entry)
        clone=ProspectiveMemory.restore(n.checkpoint())
        row=dict(x=[0,0],a=0,local=[0,0],y=1)
        self.assertEqual(n.step('extra',row),clone.step('extra',row)); LABELS+=6
        self.assertEqual(n.reservation['pending'],pending)
        second=n.review('two',batch); other=clone.review('two',batch); LABELS+=24
        self.assertEqual(second,other)
        self.assertEqual(n.checkpoint(),clone.checkpoint())
        self.assertEqual(second['upper']['qualification']['action'],'reserved')
        self.assertIsNone(second['upper']['ordinary']['archive_check'])
        self.assertEqual(n.archive.entry.payload,pending['snapshot']['payload'])
        self.assertEqual(n.archive.entry.capture_event,'two')
        self.assertEqual(n.archive.entry.record_ids,tuple(pending['snapshot']['record_ids']))
        archived=n.archive.state()
        n.deploy(JointModel((2,1),n.buffer,n.models()),n.dependencies((2,1)),n.buffer_ids)
        n.review('three',batch); last=n.review('four',batch); LABELS+=24
        self.assertEqual(last['upper']['ordinary']['action'],'reduced')
        self.assertFalse(last['upper']['ordinary']['captured']['retained'])
        self.assertEqual(n.archive.state(),archived)
        before=n.checkpoint()
        with self.assertRaises(ValueError): n.review('four',batch)
        self.assertEqual(before,n.checkpoint())

    def test_changed_port_meaning_invalidates_pending(self):
        global LABELS
        n,batch=self.build(); n.review('one',batch); LABELS+=12
        rows=[dict(x=i%4,y=i%2) for i in range(32)]
        n.nodes[1].model=LocalModel((0,1,0,1),rows); LABELS+=32
        result=n.review('two',batch); LABELS+=12
        self.assertEqual(result['upper']['qualification']['action'],'invalidated')
        self.assertIsNone(n.reservation['pending']); self.assertIsNone(n.archive.entry)

    def test_failed_witness_does_not_confirm_memory(self):
        global LABELS
        n,batch=self.build()
        result=n.review('bad',[dict(row,y=1) for row in batch]); LABELS+=12
        self.assertEqual(result['upper']['qualification']['action'],'failed')
        self.assertFalse(n.reservation['completed']); self.assertIsNone(n.archive.entry)

    def test_discard_matches_plain_deletion_predictions(self):
        global LABELS
        a,batch=self.build('discard'); b,_=self.build('plain_delete')
        for t in range(4):
            self.assertEqual(a.step(f'm/{t}',batch[0]),b.step(f'm/{t}',batch[0])); LABELS+=6
            a.review(f's/{t}',batch); b.review(f's/{t}',batch); LABELS+=24
            self.assertEqual(a.upper.state(),b.upper.state())
            self.assertIsNone(a.archive.entry)
        self.assertTrue(a.reservation['completed'])

    def test_independent_metrics_and_improving_pair_threshold(self):
        old=ROOT/'results/consolidated-recovery-v1'
        with gzip.open(old/'runs.jsonl.gz','rt') as f:
            r=next(json.loads(line) for line in f if '"branch":"detail"' in line)
        w=next(w for w in json.loads((old/'worlds.json').read_text()) if (w['seed'],w['branch'])==(r['seed'],r['branch']))
        r['policy']='legacy'; r['memory_costs']=None
        r['metrics']=metrics(r,w); verify_metrics(r,w)
        runs=[]
        for s in range(2990,2995):
            for ps in (2990,2991):
                for b in BRANCHES:
                    for p in POLICIES:
                        m=copy.deepcopy(r['metrics']); m['final_full']=True
                        m['early_observed']=0 if p=='reserve' else .03
                        for k in ('pre_observed','pre_latent'): m[k]=0
                        runs.append(dict(seed=s,proposal_seed=ps,branch=b,policy=p,metrics=m,memory_costs=None,predictions=[.5]))
        s=summarize(runs); verify_summary(runs,s); self.assertTrue(s['primary_pass'])
        changed=0
        for rr in runs:
            if changed<3 and rr['branch']=='detail' and rr['policy']=='reserve':
                rr['metrics']['early_observed']=.03; changed+=1
        s=summarize(runs); verify_summary(runs,s)
        self.assertTrue(s['checks']['discard_early_gain'])
        self.assertFalse(s['checks']['discard_improving_pairs'])


if __name__=='__main__':
    path=ROOT/'results/prospective-memory-fixtures.json'
    if path.exists(): raise FileExistsError('Preserve prior fixture attempt')
    started,stream=time.monotonic(),io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(MemoryTests))
    record=dict(status='pass' if result.wasSuccessful() and LABELS<=2500 else 'failed',tests=result.testsRun,
        charged_labels=LABELS,elapsed_seconds=time.monotonic()-started,log=stream.getvalue(),
        sources={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES})
    path.write_text(json.dumps(record,indent=2)+'\n')
    print(stream.getvalue()); print('Charged fixture labels:',LABELS)
    sys.exit(record['status']!='pass')
