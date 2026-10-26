"""022 bounded synthetic fixtures; reserved-world outcomes are never inspected."""
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
from advaita.memory_selection import MemorySelection
from advaita.prospective_memory import ProspectiveMemory
from advaita.structural import JointModel
from advaita.models import LocalModel
from advaita.state import FrozenPredictor
from memory_selection import generate,run,FILES,BRANCHES,POLICIES
from memory_selection_metrics import metrics,summarize
from audit_memory_selection import verify_world,verify_run,verify_metrics,verify_summary
from memory_selection_reference import SelectionUpper,Local
from structural_reference import unpack

LABELS=0


class SelectionTests(unittest.TestCase):
    def build(self,policy,old_bad=False,compatible=True):
        global LABELS
        n=MemorySelection([2992,2993],2992,policy)
        for j in range(2):
            rows=[dict(x=x,y=x//2) for x in range(4)]
            for i,r in enumerate(rows): n.observe_local(j,f'w/{j}/{i}',r)
            n.nodes[j].model=LocalModel((0,0,1,1),rows)
        rows=[dict(x=[0,0],a=0,local=[0,0],y=0) for _ in range(4)]
        ids=[f'composition/{i}' for i in range(4)]
        n.train_upper(ids,rows)
        for k in n.upper.counts: n.upper.counts[k]=[64,64] if old_bad else [1,2]
        memory=JointModel((2,1),rows*16,n.models())
        ports=n.dependencies((2,1))
        if not compatible: ports[-1]['meaning']=[1,1,0,0]
        n.archive.capture(FrozenPredictor.capture(memory.state(),ports,'fixture',[f'old/{i}' for i in range(64)]))
        n.reservation=dict(pending=None,completed=True)
        n.peaks['archive']=16
        batch=[dict(r,y=int(i==3)) for i,r in enumerate(rows)]
        LABELS+=76
        return n,batch

    def independent_ordinary(self,n,batch):
        global LABELS
        ns=[]
        for j,node in enumerate(n.nodes):
            local=Local(2992+j); local.partition,local.table=unpack(node.model.state()); ns.append(local)
        ref=SelectionUpper(n.upper_seed,'delete',n.selection_policy)
        ref.deploy(n.upper.state(),n.upper_ports,n.upper_training_ids)
        ref.rng.setstate(n.upper_rng.getstate()); ref.deck=copy.deepcopy(n.upper_deck)
        ref.archive=n.archive.state(); ref.pending=copy.deepcopy(n.pending); ref.peaks=copy.deepcopy(n.peaks)
        n.variant='delete'; result=n.ordinary_review(batch,'fixture-review'); n.variant='integrated'; LABELS+=len(batch)
        ref.review(result,n.buffer,n.buffer_ids,ns,batch,'fixture-review')
        self.assertEqual(ref.model,n.upper.state())
        self.assertEqual(ref.scoring,n.scoring)
        return result

    def test_failed_archive_cannot_block_separate_or_shadow(self):
        outcomes={}
        for p in POLICIES:
            n,b=self.build(p); r=self.independent_ordinary(n,b); outcomes[p]=r
            self.assertTrue(r['selection']['fit_pass']); self.assertFalse(r['selection']['archive_pass'])
            self.assertEqual(r['selection']['ranked_source'],'archive')
        for p in ('shadow','separate'): self.assertEqual(outcomes[p]['action'],'improved')
        for p in ('veto','joint'): self.assertFalse(outcomes[p]['ordinary_accepted'])

    def test_passing_archive_joint_retrieval_and_veto_are_distinct(self):
        outcomes={}
        for p in POLICIES:
            n,b=self.build(p,old_bad=True); r=self.independent_ordinary(n,b); outcomes[p]=r
            self.assertTrue(r['selection']['archive_pass'])
            self.assertLess(r['selection']['fit_loss'],r['selection']['archive_loss'])
        self.assertEqual(outcomes['joint']['action'],'retrieved')
        self.assertTrue(outcomes['veto']['selection']['vetoed'])
        self.assertFalse(outcomes['veto']['ordinary_accepted'])
        for p in ('shadow','separate'): self.assertEqual(outcomes[p]['action'],'improved')

    def test_incompatible_memory_is_excluded(self):
        states=[]
        for p in POLICIES:
            n,b=self.build(p,compatible=False); r=self.independent_ordinary(n,b)
            self.assertFalse(r['archive_check']['compatible'])
            self.assertIsNone(r['selection']['archive_loss']); states.append(r['after'])
        self.assertTrue(all(s==states[0] for s in states))

    def test_original_behavior_and_checkpoint_continuation(self):
        global LABELS
        for p,old_mode in [('joint','reserve'),('shadow','discard')]:
            n,b=self.build(p,old_bad=True)
            old=ProspectiveMemory(n.seeds,n.upper_seed,old_mode)
            old.__dict__.update(copy.deepcopy(n.__dict__)); old.memory_mode=old_mode
            if old_mode=='discard': old.archive.clear()
            for t in range(3):
                new_review=n.review(f's/{t}',b); old_review=old.review(f's/{t}',b); LABELS+=24
                self.assertEqual(n.upper.state(),old.upper.state())
                self.assertEqual(new_review['upper']['ordinary']['action'],old_review['upper']['ordinary']['action'])
                self.assertEqual(n.step(f'm/{t}',b[0]),old.step(f'm/{t}',b[0])); LABELS+=6
            clone=MemorySelection.restore(n.checkpoint()); self.assertEqual(clone.checkpoint(),n.checkpoint())
            self.assertEqual(n.review('after',b),clone.review('after',b)); LABELS+=24
            self.assertEqual(n.checkpoint(),clone.checkpoint())

    def test_full_replay_all_policies_and_frozen_qualification(self):
        global LABELS
        w=generate(2992,'detail',sizes=(4,1,8,4,4,1),review_every=4); LABELS+=48
        verify_world(w,review_every=4)
        for p in POLICIES:
            r,c=run(w,p,2992,review_every=4,measure=False); LABELS+=r['costs']['feedback_labels']
            verify_run(r,w,json.loads(c),review_every=4,measure=False)
            self.assertEqual(MemorySelection.restore(c).checkpoint(),c)
            n,b=self.build(p); n.archive.clear(); n.reservation=dict(pending=None,completed=False)
            rows=[dict(x=[0,0],a=0,local=[0,0],y=0) for _ in range(32)]
            n.deploy(JointModel((2,1),rows,n.models()),n.dependencies((2,1)),n.buffer_ids); LABELS+=32
            first=n.review('qualify1',rows[:4]); LABELS+=12
            pending=copy.deepcopy(n.reservation['pending']); self.assertIsNotNone(pending)
            clone=MemorySelection.restore(n.checkpoint())
            second=n.review('qualify2',rows[:4]); other=clone.review('qualify2',rows[:4]); LABELS+=24
            self.assertEqual(second,other); self.assertEqual(n.checkpoint(),clone.checkpoint())
            self.assertEqual(n.archive.entry.payload,pending['snapshot']['payload'])
            self.assertIsNone(second['upper']['ordinary']['archive_check'])

    def test_independent_metrics_and_threshold(self):
        p=ROOT/'results/prospective-memory-v1'
        with gzip.open(p/'runs.jsonl.gz','rt') as f:
            r=next(json.loads(line) for line in f if '"policy":"reserve"' in line)
        w=next(w for w in json.loads((p/'worlds.json').read_text()) if (w['seed'],w['branch'])==(r['seed'],r['branch']))
        r['policy']='joint'; r['metrics']=metrics(r,w); verify_metrics(r,w)
        runs=[]
        for seed in range(2990,2995):
            for ps in (2990,2991):
                for b in BRANCHES:
                    for policy in POLICIES:
                        m=copy.deepcopy(r['metrics']); m['final_full']=True
                        m['early_observed']=0 if policy=='separate' else .03
                        m['pre_observed']=m['pre_latent']=0
                        runs.append(dict(seed=seed,proposal_seed=ps,branch=b,policy=policy,metrics=m,
                            memory_costs=r['memory_costs'],predictions=[.5],reviews=[]))
        s=summarize(runs); verify_summary(runs,s); self.assertTrue(s['primary_pass'])
        changed=0
        for rr in runs:
            if changed<3 and rr['branch']=='detail' and rr['policy']=='separate':
                rr['metrics']['early_observed']=.03; changed+=1
        s=summarize(runs); verify_summary(runs,s)
        self.assertTrue(s['checks']['early_gain']); self.assertFalse(s['checks']['improving_pairs'])


if __name__=='__main__':
    directory=ROOT/'results'
    previous=sorted(directory.glob('memory-selection-fixtures*.json'))
    path=directory/('memory-selection-fixtures.json' if not previous else f'memory-selection-fixtures-attempt{len(previous)+1}.json')
    charged=sum(json.loads(p.read_text())['charged_labels'] for p in previous)
    started,stream=time.monotonic(),io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(SelectionTests))
    record=dict(status='pass' if result.wasSuccessful() and charged+LABELS<=3500 else 'failed',tests=result.testsRun,
        charged_labels=LABELS,cumulative_labels=charged+LABELS,elapsed_seconds=time.monotonic()-started,log=stream.getvalue(),
        sources={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in FILES})
    path.write_text(json.dumps(record,indent=2)+'\n')
    print(stream.getvalue()); print('Charged fixture labels:',LABELS,'cumulative:',charged+LABELS)
    sys.exit(record['status']!='pass')
