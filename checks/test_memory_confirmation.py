"""028 measurement fixtures and saved-trace replay; no new learning data."""
import copy
import gzip
import hashlib
import io
import json
import math
from pathlib import Path
import sys
import time
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import memory_confirmation as experiment
import memory_revision as old
from memory_confirmation_metrics import WINDOWS,metrics,summarize
from audit_memory_confirmation import verify_metrics,verify_summary,verify_run
REPLAYED=0


def synthetic_runs():
    runs=[]
    for seed in range(5):
        for proposal in range(2):
            for history in experiment.BRANCHES:
                for policy in experiment.POLICIES:
                    values={k:.45 for k in WINDOWS}
                    if policy=='combined':values['post']=.35
                    m=dict(observed=values.copy(),latent=values.copy(),transfer_valid=True,final_valid=True,
                        gap_valid=True,final_structure=True,gap_loss=.35,recovery=896,structure_errors=0,transfers=0,transferred_mass=0)
                    runs.append(dict(seed=seed,proposal_seed=proposal,branch=history,policy=policy,metrics=m,costs={}))
    return runs


class Contracts(unittest.TestCase):
    def test_a_boundaries_and_independent_metrics(self):
        row=dict(x=[0,0],a=1,local=[0,0],y=1)
        world=dict(branch='stable',forms=[[0]*4,[0]*4],affected=0,main=[copy.deepcopy(row) for _ in range(1280)])
        evaluation=dict(local_exact=[True,True],accuracy=1.,regret=0.,sufficient_minimal=True,expected_loss=.325)
        run=dict(policy='combined',predictions=[[.5,.5,.5] for _ in range(1280)],transfer=evaluation.copy(),
            evaluations=[dict(evaluation,index=t) for t in range(64,1281,64)],reviews=[],costs={})
        # Tick896 is excluded; ticks897 and1280 are both included.
        run['predictions'][895][2]=.9;run['predictions'][896][2]=.8;run['predictions'][1279][2]=.7
        run['metrics']=metrics(run,world,experiment.previous.target,experiment.previous.forms_at)
        verify_metrics(run,world)
        expected=(382*-math.log(.5)-math.log(.8)-math.log(.7))/384
        self.assertAlmostEqual(run['metrics']['observed']['post'],expected)
        self.assertEqual(WINDOWS['post'],(897,1280));self.assertEqual(WINDOWS['early'],(769,896))
        bad=copy.deepcopy(run);bad['metrics']['observed']['post']+=.001
        with self.assertRaises(AssertionError):verify_metrics(bad,world)

    def test_b_primary_uses_post_not_early_or_late(self):
        runs=synthetic_runs();s=summarize(runs);verify_summary(runs,s)
        self.assertTrue(s['primary_pass']);self.assertAlmostEqual(s['revision_pairs'][0]['gain'],.1)
        for r in runs:
            if r['policy']=='combined':
                r['metrics']['observed']['post']=.45
                r['metrics']['observed']['late']=.1
        s=summarize(runs);verify_summary(runs,s)
        self.assertFalse(s['gates']['revision_gain']);self.assertFalse(s['gates']['revision_pairs'])

    def test_c_individual_post_and_early_guards(self):
        for window,gate in [('post','post_worst'),('early','revision_worst')]:
            runs=synthetic_runs();r=next(r for r in runs if r['policy']=='combined' and r['branch']=='remap')
            r['metrics']['observed'][window]=.6
            s=summarize(runs);verify_summary(runs,s);self.assertFalse(s['gates'][gate]);self.assertFalse(s['primary_pass'])

    def test_d_frozen_trace_replay_and_adapter_identity(self):
        global REPLAYED
        self.assertIs(experiment.run.__globals__['MemoryLearner'],old.run.__globals__['MemoryLearner'])
        self.assertIs(experiment.run.__code__,old.run.__code__)
        self.assertIs(experiment.generate,old.generate)
        folder=ROOT/'results/memory-revision-v1'
        worlds=json.loads((folder/'worlds.json').read_text());world=next(w for w in worlds if w['seed']==1700 and w['branch']=='stable')
        with gzip.open(folder/'runs.jsonl.gz','rt') as f:
            run=next(r for line in f if (r:=json.loads(line))['seed']==1700 and r['branch']=='stable' and r['policy']=='combined')
        prior=copy.deepcopy(run['metrics']);run['metrics']=metrics(run,world,experiment.previous.target,experiment.previous.forms_at)
        for key,value in prior.items():
            if key in ('observed','latent'):self.assertEqual(value,{k:v for k,v in run['metrics'][key].items() if k!='post'})
            else:self.assertEqual(value,run['metrics'][key])
        with gzip.open(folder/run['checkpoint_file'],'rt') as f:checkpoint=json.load(f)
        REPLAYED+=run['costs']['feedback_labels'];verify_run(run,world,checkpoint)


def main():
    folder=ROOT/'results/memory-confirmation-fixtures';folder.mkdir(exist_ok=True)
    attempts=sorted(folder.glob('attempt-*.json'));stream=io.StringIO();started=time.monotonic()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    evidence=dict(status='pass' if result.wasSuccessful() else 'failed',tests=result.testsRun,new_learning_labels=0,
        replayed_saved_labels=REPLAYED,elapsed_seconds=time.monotonic()-started,log=stream.getvalue(),
        sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in experiment.FILES})
    (folder/f'attempt-{len(attempts)+1:02d}.json').write_text(json.dumps(evidence,indent=2)+'\n')
    print(stream.getvalue());sys.exit(not result.wasSuccessful())

if __name__=='__main__':main()
