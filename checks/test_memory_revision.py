"""027 bounded mechanics fixtures, parity and independent replay before outcomes."""
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
import memory_revision as experiment
from advaita.memory_revision import RevisionLearner
from advaita.memory_control import fit_local
from audit_memory_revision import verify_run,verify_summary
from memory_revision_reference import RevisionReference
from audit_memory_control_v2 import verify_world
from audit_nested_abstractions import close
from memory_revision_metrics import summarize
LABELS=0;CACHE={}


def charge(n):
    global LABELS
    LABELS+=n


def prepared(mode='combined'):
    learner=RevisionLearner.restore(CACHE['stable','combined'][1]);learner.mode=mode
    learner.fast[0]=[[0.,16.] for _ in range(4)];learner.slow[0]=[[16.,16.] for _ in range(4)]
    learner.locals[0]=fit_local([0,0,0,0],learner.combined(0));learner.revision_pending=[None]*3
    rows=[dict(x=[i%4,0],a=0,local=[0,0],y=0) for i in range(8)]
    return learner,rows


class Contracts(unittest.TestCase):
    def test_a_all_policies_replay_and_control_parity(self):
        for h in ['stable','return']:
            w=experiment.generate(5990,h,True);verify_world(w)
            for p in experiment.POLICIES:
                charge(128 if h=='stable' else 104)
                r,c=experiment.run(w,p,5990,measure=False);verify_run(r,w,json.loads(c),measure=False)
                CACHE[h,p]=(r,c)
                if p=='baseline':continue
                clone=RevisionLearner.restore(c);self.assertEqual(c,clone.checkpoint());before=clone.checkpoint()
                with self.assertRaises(ValueError):clone.observe(16,w['main'][-1])
                self.assertEqual(before,clone.checkpoint())
                with self.assertRaises(ValueError):clone.review(16,w['selection']['16'])
                self.assertEqual(before,clone.checkpoint())
                other=RevisionLearner.restore(c);charge(6)
                self.assertEqual(clone.observe(17,w['main'][-1]),other.observe(17,w['main'][-1]));self.assertEqual(clone.checkpoint(),other.checkpoint())
                if p in ('fast','selective'):
                    charge(128 if h=='stable' else 104)
                    old,oc=experiment.previous.run(w,p,5990,measure=False)
                    for key in ['predictions','evaluations','transfer','snapshots']:self.assertEqual(r[key],old[key])
                    for v,ov in zip(r['reviews'],old['reviews']):self.assertEqual({k:x for k,x in v.items() if k!='weakenings'},ov)
                    oldstate=json.loads(oc);state=json.loads(c)
                    for key in ['fast','slow','locals','upper','pending','decks','rngs','main_ids','selection_ids']:self.assertEqual(state[key],oldstate[key])

    def test_b_two_witnesses_and_independent_mass_replay(self):
        a,rows=prepared();ref=object.__new__(RevisionReference);ref.__dict__=copy.deepcopy(a.__dict__)
        a.tick=ref.tick=64;charge(8);first=a.weaken(0,rows);ref.revision(0,rows,first)
        self.assertTrue(first['qualifies']);self.assertFalse(first['accepted'])
        close(json.loads(a.checkpoint()),ref.state())
        a=RevisionLearner.restore(a.checkpoint());before=copy.deepcopy(a.fast[0]);a.tick=ref.tick=128
        a.pending[0]=ref.pending[0]={'synthetic':'old reduction'}
        charge(8);second=a.weaken(0,rows);ref.revision(0,rows,second)
        self.assertTrue(second['accepted']);self.assertEqual(second['removed_mass'],32)
        self.assertEqual(a.fast[0],before);self.assertIsNone(a.pending[0]);self.assertIsNone(a.revision_pending[0])
        close(json.loads(a.checkpoint()),ref.state())
        bad=copy.deepcopy(second);bad['removed_mass']+=1
        ref2=object.__new__(RevisionReference);ref2.__dict__=copy.deepcopy(a.__dict__)
        # Recomputed decision must reject a tampered trace, not trust the saved flag.
        with self.assertRaises(AssertionError):ref2.revision(0,rows,bad)

    def test_c_gap_changed_binding_and_brief_contradiction(self):
        for case in ['gap','binding','restored']:
            a,rows=prepared();a.tick=64;charge(8);self.assertTrue(a.weaken(0,rows)['qualifies'])
            a.tick=192 if case=='gap' else 128
            if case=='binding':a.locals[0]=fit_local([0,0,1,1],a.combined(0))
            if case=='restored':rows=[dict(r,local=[1,0]) for r in rows]
            charge(8);self.assertFalse(a.weaken(0,rows)['accepted'])
        a,rows=prepared('uniform');a.tick=64;charge(8);self.assertTrue(a.weaken(0,rows)['accepted'])
        a,rows=prepared('selective');a.tick=64;charge(8);a.weaken(0,rows);a.tick=128;charge(8)
        self.assertFalse(a.weaken(0,rows)['accepted'])

    def test_d_relaxed_admission_and_conservation(self):
        a,rows=prepared('selective');charge(8);before=[a.combined(j) for j in range(3)]
        event=a.migrate(0,rows);self.assertGreater(event['old_loss'],event['new_loss']);self.assertGreater(event['new_loss'],.55)
        self.assertFalse(event['accepted']);a.mode='relaxed';charge(8);event=a.migrate(0,rows)
        self.assertTrue(event['accepted']);close(before,[a.combined(j) for j in range(3)])

    def test_e_summary_gate_and_guard_arithmetic(self):
        runs=[]
        for s in range(5):
            for q in range(2):
                for h in experiment.BRANCHES:
                    for p in experiment.POLICIES:
                        value=.35 if p=='combined' else .45
                        m=dict(observed={k:value for k in ['whole','early','late','burst','recovery']},latent={k:value for k in ['whole','early','late','burst','recovery']},
                            transfer_valid=True,final_valid=True,gap_valid=True,final_structure=True,gap_loss=value,recovery=896,structure_errors=0,transfers=0,transferred_mass=0)
                        runs.append(dict(seed=s,proposal_seed=q,branch=h,policy=p,metrics=m,costs={}))
        result=summarize(runs);verify_summary(runs,result);self.assertTrue(result['primary_pass']);self.assertTrue(result['selectivity_pass'])
        row=next(r for r in runs if r['policy']=='combined' and r['branch']=='burst');row['metrics']['observed']['recovery']=.7
        result=summarize(runs);verify_summary(runs,result);self.assertFalse(result['gates']['preservation_worst'])


def main():
    folder=ROOT/'results/memory-revision-fixtures';folder.mkdir(exist_ok=True)
    attempts=sorted(folder.glob('attempt-*.json'));used=sum(json.loads(p.read_text())['charged_labels'] for p in attempts)
    assert used+2500<=5000,'Insufficient fixture budget'
    stream=io.StringIO();started=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    record=dict(status='pass' if result.wasSuccessful() and used+LABELS<=5000 else 'failed',tests=result.testsRun,charged_labels=LABELS,cumulative_labels=used+LABELS,
        elapsed_seconds=time.monotonic()-started,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in experiment.FILES})
    (folder/f'attempt-{len(attempts)+1:02d}.json').write_text(json.dumps(record,indent=2)+'\n');print(stream.getvalue());print('Charged',LABELS,'cumulative',used+LABELS)
    sys.exit(record['status']!='pass')

if __name__=='__main__':main()
