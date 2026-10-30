"""Bounded 026 contracts; preserve all fixture attempts and charge before use."""
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
import memory_control_v2 as experiment
from advaita.memory_control import MemoryLearner,fit_local,fit_upper,RF,RS
from advaita.structural import StructuralLearner
from audit_memory_control_v2 import verify_world,verify_run,verify_metrics,verify_summary,forms,truth
from memory_control_metrics import metrics,summarize
LABELS=0;CACHE={}

def charge(n):
    global LABELS
    LABELS+=n


class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        charge(568)
        cls.worlds={b:experiment.generate(4990,b,small=True) for b in experiment.BRANCHES}
    def test_a_world_streams_and_new_form(self):
        for w in self.worlds.values():
            verify_world(w)
            for t in (0,256,257,320,321,768,769,1280):
                for observed in (False,True):self.assertEqual(experiment.forms_at(w,t,observed),forms(w,t,observed))
                for x in ([0,0],[2,3]):self.assertEqual(experiment.target(w,x,1,t),truth(w,x,1,t))
        w=self.worlds['remap'];self.assertFalse(experiment.same(w['forms'][w['affected']],w['alternative']))
    def test_b_full_family_and_baseline_replay(self):
        for branch in ('stable','return'):
            w=self.worlds[branch]
            for policy in experiment.POLICIES:
                charge(128 if branch=='stable' else 104)
                r,c=experiment.run(w,policy,4990,measure=False);verify_run(r,w,json.loads(c),measure=False)
                CACHE[branch,policy]=(r,c)
                if policy=='baseline':continue
                clone=MemoryLearner.restore(c);self.assertEqual(clone.checkpoint(),c)
                before=clone.checkpoint()
                with self.assertRaises(ValueError):clone.observe(16,w['main'][-1])
                self.assertEqual(before,clone.checkpoint())
                with self.assertRaises(ValueError):clone.review(16,w['selection']['16'])
                self.assertEqual(before,clone.checkpoint())
                other=MemoryLearner.restore(c);charge(6)
                self.assertEqual(clone.observe(17,w['main'][-1]),other.observe(17,w['main'][-1]))
                self.assertEqual(clone.checkpoint(),other.checkpoint())
    def test_c_conservation_capacity_and_blank_clocks(self):
        a=MemoryLearner.restore(CACHE['stable','always'][1])
        # Construct 64 all-zero labelled joint observations (192 channel labels).
        charge(192)
        a.fast=[[[0.,16.] for _ in range(4)] for _ in range(2)]+[[[0.,2.] for _ in range(32)]]
        a.slow=[[[0.,0.] for _ in table] for table in a.fast];a.refit()
        rows=[dict(x=[i%4,(i//2)%4],a=i%2,local=[0,0],y=0) for i in range(8)]
        before=[a.combined(j) for j in range(3)];pred=a.predictions([0,1],0)
        for j in range(3):
            charge(8);event=a.migrate(j,rows);self.assertTrue(event['accepted']);self.assertAlmostEqual(event['moved_mass'],16.)
        for j in range(3):self.assertEqual(before[j],a.combined(j))
        self.assertEqual(pred,a.predictions([0,1],0))
        a.policy='selective';baseline=a.mass();start=a.tick
        for t in range(start+1,start+65):self.assertIsNone(a.observe(t,None))
        for j in range(3):
            self.assertAlmostEqual(a.mass()['fast'][j],baseline['fast'][j]/2,places=10)
            self.assertAlmostEqual(a.mass()['slow'][j],baseline['slow'][j]*RS**64,places=10)
        b=MemoryLearner.restore(a.checkpoint());b.policy='activity';before=b.checkpoint();mass=b.mass();n=len(b.main_ids)
        b.observe(b.tick+1,None);self.assertEqual(b.mass(),mass);self.assertEqual(len(b.main_ids),n)
        p=MemoryLearner.restore(a.checkpoint());p.policy='permanent';mass=p.mass();p.observe(p.tick+1,None);self.assertEqual(p.mass()['slow'],mass['slow'])
        # A full slow store admits zero transfer, never negative or excess mass.
        a.slow[0]=[[0.,128.] for _ in range(4)];charge(8);event=a.migrate(0,rows)
        self.assertEqual(event['fraction'],0);self.assertFalse(event['accepted'])
    def test_d_selection_rejects_conflicting_evidence(self):
        a=MemoryLearner.restore(CACHE['stable','selective'][1])
        # Numerical state isolates gate arithmetic; no additional training is run.
        a.locals[0]=fit_local((0,0,0,0),[[16.,16.]]*4)
        a.slow[0]=[[16.,16.]]*4;a.fast[0]=[[0.,16.]]*4
        rows=[dict(x=[i%4,0],a=0,local=[1,0],y=0) for i in range(8)]
        charge(8);before=copy.deepcopy(a.slow[0]);event=a.migrate(0,rows)
        self.assertFalse(event['gate']);self.assertFalse(event['accepted']);self.assertEqual(before,a.slow[0])
        a.policy='always';charge(8);self.assertTrue(a.migrate(0,rows)['accepted'])
    def test_e_frozen_pending_reduction(self):
        a=MemoryLearner.restore(CACHE['stable','fast'][1]);a.fast[0]=[[0.,16.] for _ in range(4)];a.slow[0]=[[0.,0.] for _ in range(4)]
        a.locals[0]=fit_local((0,0,1,1),a.fast[0]);a.pending[0]=None
        rows=[dict(x=[i%4,0],a=0,local=[0,0],y=0) for i in range(8)]
        charge(8);first=a.review_channel(0,rows);self.assertEqual(first['action'],'awaiting_reduction')
        pending=copy.deepcopy(a.pending[0]);a.fast[0][0][1]+=1;a.refit();self.assertEqual(a.pending[0],pending)
        charge(8);second=a.review_channel(0,rows);self.assertEqual(second['action'],'collapsed')
    def test_f_metrics_arithmetic_and_guard_failure(self):
        r=copy.deepcopy(CACHE['stable','fast'][0]);w=copy.deepcopy(self.worlds['stable'])
        r['predictions']*=80;w['main']*=80;base=r['evaluations'][-1]
        r['evaluations']=[dict(base,index=t) for t in range(64,1281,64)]
        r['metrics']=metrics(r,w,experiment.target,experiment.forms_at);verify_metrics(r,w)
        runs=[]
        for seed in range(5):
            for ps in range(2):
                for h in experiment.BRANCHES:
                    for p in experiment.POLICIES:
                        score=.35 if p=='selective' else .45
                        m=dict(observed={k:score for k in ('whole','early','late','burst','recovery')},latent={k:score for k in ('whole','early','late','burst','recovery')},
                            transfer_valid=True,final_valid=True,gap_valid=True,final_structure=True,gap_loss=score,recovery=896,
                            structure_errors=0,transfers=0,proposals=0,transferred_mass=0,group_changes=0)
                        runs.append(dict(seed=seed,proposal_seed=ps,branch=h,policy=p,metrics=m))
        summary=summarize(runs);verify_summary(runs,summary);self.assertTrue(summary['primary_pass']);self.assertTrue(summary['dual_store_pass'])
        r=next(r for r in runs if r['policy']=='selective' and r['branch']=='reversal');r['metrics']['observed']['early']=.56
        summary=summarize(runs);verify_summary(runs,summary);self.assertFalse(summary['gates']['worst_pair'])


def main():
    folder=ROOT/'results/memory-control-fixtures';folder.mkdir(exist_ok=True)
    previous=sorted(folder.glob('attempt-*.json'));used=sum(json.loads(p.read_text())['charged_labels'] for p in previous)
    assert used+2600<=5000,(used,'insufficient fixture headroom')
    stream=io.StringIO();start=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    record=dict(status='pass' if result.wasSuccessful() and used+LABELS<=5000 else 'failed',tests=result.testsRun,charged_labels=LABELS,cumulative_labels=used+LABELS,
        elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in experiment.FILES})
    (folder/f'attempt-{len(previous)+1:02d}.json').write_text(json.dumps(record,indent=2)+'\n');print(stream.getvalue());print('Charged:',LABELS,'cumulative:',used+LABELS)
    sys.exit(record['status']!='pass')

if __name__=='__main__':main()
