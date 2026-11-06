"""033 pre-outcome contracts, reused fixtures and saved-state prerequisite."""
import copy,gzip,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import selective_steering as e
from selective_steering_metrics import measure,summarize,WINDOWS
from audit_selective_steering import verify_world,verify_run,verify_parity,verify_metrics,verify_summary
from advaita.selective_steering import SteerableMemory
from advaita.continuing import ContinuingLearner
from memory_control_reference import local_fit,upper_fit,up
from audit_nested_abstractions import close
CACHE={};PRESENTATIONS=0;PREREQUISITE=[]

class Contracts(unittest.TestCase):
    def test_a_saved_refresh_failures(self):
        with gzip.open(ROOT/'results/introspection-v1/runs.jsonl.gz','rt') as f:records=[json.loads(x) for x in f]
        for r in records:
            failures=[m for m,f in zip(r['metrics']['forecasts'],r['decision']['forecasts']) if m['eligible'] and m['immediate_actual']!=f['immediate']]
            for failure in failures:
                a=ContinuingLearner.restore(json.dumps(r['checkpoint']));j=failure['channel'];a.engine.refit();before=[a.engine.predictions([x,y],act)[2] for x,y,act in e.life.CONTEXTS]
                raw=[[[f[k]+s[k] for k in (0,1)] for f,s in zip(fs,ss)] for fs,ss in zip(a.engine.fast,a.engine.slow)]
                local=[local_fit(m['partition'],raw[k]) for k,m in enumerate(a.engine.locals)];upper=upper_fit(a.engine.upper['spec'],raw[2],local)
                close(before,[up(upper,local,[x,y],act) for x,y,act in e.life.CONTEXTS])
                a.weaken_slow(j,review_tick=a.tick,reason='Fixture: separate refresh from evidence change')
                after=[a.engine.predictions([x,y],act)[2] for x,y,act in e.life.CONTEXTS];delta=max(abs(x-y) for x,y in zip(before,after));self.assertLessEqual(delta,1e-12)
                PREREQUISITE.append(dict(seed=r['seed'],history=r['history'],proposal_seed=r['proposal_seed'],channel=j,delta_after_refresh=delta))
        self.assertEqual(len(PREREQUISITE),5)
    def test_b_six_paths_and_world(self):
        global PRESENTATIONS
        w=e.generate(7990,'forms',True);verify_world(w);records=[]
        for policy in e.POLICIES:
            r=e.run(w,policy,7990,False);PRESENTATIONS+=r['feedback_labels'];verify_run(r,w,False);records.append(r)
        verify_parity(records);CACHE.update(records=records,w=w)
    def test_c_control_semantics_and_resume(self):
        r=next(r for r in CACHE['records'] if r['policy']=='selective');a=SteerableMemory.restore(json.dumps(r['checkpoint']))
        # Explicit synthetic mass makes the selective elapsed-time decay measurable.
        a.slow[1]=[[1.,2.] for _ in range(4)];a.refit();old=a.checkpoint()
        for args in [dict(lock=[2],plastic=[]),dict(lock=[0],plastic=[0]),dict(lock=[True],plastic=[]),dict(lock=[0,0],plastic=[])]:
            with self.assertRaises(ValueError):a.configure(**args,reason='Fixture')
            self.assertEqual(a.checkpoint(),old)
        a.configure(lock=[0],plastic=[1],reason='Fixture');saved=a.checkpoint();a=SteerableMemory.restore(saved);self.assertEqual(saved,a.checkpoint())
        with self.assertRaises(ValueError):a.configure(lock=[],plastic=[],reason='Duplicate')
        v=a.inspect();v['locked']['0'][0]=99;self.assertEqual(saved,a.checkpoint())
        slow=copy.deepcopy(a.slow);fast=copy.deepcopy(a.fast);part=a.locals[0]['partition'].copy()
        with self.assertRaises(ValueError):a.observe(a.tick,None)
        self.assertEqual(saved,a.checkpoint());a.observe(a.tick+1,None)
        for j in range(3):
            for before,after in zip(slow[j],a.slow[j]):close(after,[v*2**(-1/(128 if j==1 else 1024)) for v in before])
            for before,after in zip(fast[j],a.fast[j]):close(after,[v*2**(-1/64) for v in before])
        row=dict(x=[0,0],a=0,local=[1,0],y=1);before=a.predictions(row['x'],row['a'])[0];mass=a.mass()['fast'][0]
        a.observe(a.tick+1,row);a.review(a.tick,[row]);self.assertEqual(part,a.locals[0]['partition']);self.assertNotEqual(before,a.predictions(row['x'],row['a'])[0]);self.assertNotEqual(mass,a.mass()['fast'][0])
        banks=copy.deepcopy([a.fast,a.slow]);a.configure(lock=[],plastic=[],reason='Release');self.assertEqual(a.locked,{});self.assertEqual(a.half_lives,[1024]*3);self.assertEqual([a.fast,a.slow],banks)
    def test_d_metrics(self):
        r=copy.deepcopy(CACHE['records'][-2]);w=copy.deepcopy(CACHE['w']);r['predictions']*=64;w['main']*=64
        template=r['evaluations'][-1];r['evaluations']=[dict(copy.deepcopy(template),tick=t) for t in range(64,2049,64)]
        r['metrics']=measure(r,w);verify_metrics(r,w)
    def test_e_summary_gates(self):
        rs=[]
        for s in range(5):
            for q in range(2):
                for h in e.HISTORIES:
                    for policy in e.POLICIES:
                        v=.35 if policy=='selective' else .4
                        ms={typ:{k:[v]*3 for k in WINDOWS} for typ in ('expected','observed')};ms.update(protected=0,flexible=1,burst_correct=1,active_local_correct=[1,1],final_valid=True,final_local_exact=[True,True],final_spec=[1,1])
                        rs.append(dict(seed=s,proposal_seed=q,history=h,policy=policy,metrics=ms))
        result=summarize(rs);verify_summary(rs,result);self.assertTrue(result['empirical_pass'])
        for r in rs:
            if r['policy']=='selective':
                r['metrics']['burst_correct']=0;r['metrics']['final_valid']=False
                for k in WINDOWS:r['metrics']['expected'][k]=[.6]*3
        result=summarize(rs);verify_summary(rs,result);self.assertTrue(all(not g for g in result['gates'].values()))

def main():
    out=ROOT/'results/selective-steering-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'));assert len(old)<8
    start=time.monotonic();stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    result=dict(status='pass' if r.wasSuccessful() else 'failed',fresh_random_labels=0,transformed_replay_presentations=PRESENTATIONS,prerequisite_cases=PREREQUISITE,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(result,indent=2)+'\n');print(stream.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
