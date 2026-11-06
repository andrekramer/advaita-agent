"""034 pre-outcome fixtures; reused7990 data, synthetic contracts and gates."""
import copy,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import coordinated_steering as e
from advaita.coordinated_steering import CoordinatedMemory
from coordinated_steering_metrics import summarize
from selective_steering_metrics import measure,WINDOWS
from audit_coordinated_steering import verify_run,verify_summary
from audit_selective_steering import verify_world,verify_metrics
from audit_nested_abstractions import close
CACHE={};PRESENTATIONS=0

class Contracts(unittest.TestCase):
    def test_a_all_policies_and_parity(self):
        global PRESENTATIONS
        w=e.prior.generate(7990,'forms',True);verify_world(w);records={}
        for policy in e.POLICIES:
            r=e.run(w,policy,7990,False);PRESENTATIONS+=r['feedback_labels'];verify_run(r,w,False);records[policy]=r
        for policy,oldpolicy in [('U','refreshed'),('P','lock_only'),('L','selective')]:
            old=e.prior.run(w,oldpolicy,7990,False);PRESENTATIONS+=old['feedback_labels'];r=records[policy]
            for key in ('predictions','reviews','evaluations','costs'):self.assertEqual(r[key],old[key])
        CACHE.update(records=records,w=w)
    def test_b_composite_decay_restore_and_release(self):
        a=CoordinatedMemory.restore(json.dumps(CACHE['records']['C']['checkpoint']))
        a.slow=[[[1.,2.] for _ in range(n)] for n in (4,4,32)];a.refit();before=a.checkpoint()
        for lock,plastic in [([2],[]),([0],[0,2]),([],[2,2]),([],[True]),([],[3]),([],'2')]:
            with self.assertRaises(ValueError):a.configure(lock=lock,plastic=plastic,reason='Fixture')
            self.assertEqual(before,a.checkpoint())
        a.configure(lock=[0],plastic=[1,2],reason='Fixture');saved=a.checkpoint();a=CoordinatedMemory.restore(saved);self.assertEqual(saved,a.checkpoint());self.assertEqual(a.half_lives,[1024,128,128])
        inspection=a.inspect();inspection['half_lives'][2]=1;self.assertEqual(saved,a.checkpoint())
        with self.assertRaises(ValueError):a.configure(lock=[],plastic=[],reason='Duplicate')
        self.assertEqual(saved,a.checkpoint());slow=copy.deepcopy(a.slow);fast=copy.deepcopy(a.fast)
        a.observe(a.tick+1,None)
        for j in range(3):
            for b,c in zip(slow[j],a.slow[j]):close(c,[x*2**(-1/(1024 if j==0 else 128)) for x in b])
            for b,c in zip(fast[j],a.fast[j]):close(c,[x*2**(-1/64) for x in b])
        row=dict(x=[0,0],a=0,local=[1,0],y=1);a.observe(a.tick+1,row);a.review(a.tick,[row]);banks=copy.deepcopy([a.fast,a.slow]);a.configure(lock=[],plastic=[],reason='Release')
        self.assertEqual(a.half_lives,[1024]*3);self.assertFalse(a.locked);self.assertEqual(banks,[a.fast,a.slow])
    def test_c_measurement_reuse(self):
        r=copy.deepcopy(CACHE['records']['C']);w=copy.deepcopy(CACHE['w']);r['predictions']*=64;w['main']*=64
        template=r['evaluations'][-1];r['evaluations']=[dict(copy.deepcopy(template),tick=t) for t in range(64,2049,64)]
        r['metrics']=measure(r,w);verify_metrics(r,w)
    def test_d_factorial_gates(self):
        records=[];values={'U':.52,'P':.50,'L':.48,'D':.45,'C':.40}
        for s in range(5):
            for q in range(2):
                for h in e.HISTORIES:
                    for policy in e.POLICIES:
                        v=values[policy];ms={typ:{k:[v]*3 for k in WINDOWS} for typ in ('expected','observed')};ms.update(protected=0,flexible=1,burst_correct=1,active_local_correct=[1,1],final_valid=True,final_local_exact=[True,True],final_spec=[1,1])
                        records.append(dict(seed=s,proposal_seed=q,history=h,policy=policy,metrics=ms))
        s=summarize(records);verify_summary(records,s);self.assertTrue(s['empirical_pass']);self.assertTrue(s['interaction_pass'])
        # Beating L does not suffice if downstream-only D is better.
        failed=copy.deepcopy(records)
        for r in failed:
            if r['policy']=='C':r['metrics']['expected']['active'][2]=.46
        s=summarize(failed);verify_summary(failed,s);self.assertFalse(s['incremental_pass']);self.assertTrue(s['gates']['C_vs_L_mean'])
        # Additive improvements may be useful without a positive interaction.
        additive=copy.deepcopy(records);values={'U':.52,'P':.50,'L':.45,'D':.40,'C':.35}
        for r in additive:r['metrics']['expected']['active'][2]=values[r['policy']]
        s=summarize(additive);verify_summary(additive,s);self.assertTrue(s['incremental_pass']);self.assertFalse(s['interaction_pass'])
        failed=copy.deepcopy(records)
        for r in failed:
            if r['policy']=='C':
                r['metrics']['burst_correct']=0;r['metrics']['final_valid']=False
                for k in WINDOWS:r['metrics']['expected'][k]=[.8]*3
        s=summarize(failed);verify_summary(failed,s);self.assertTrue(all(not x for x in s['gates'].values()))

def main():
    out=ROOT/'results/coordinated-steering-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'));assert len(old)<8
    start=time.monotonic();stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    data=dict(status='pass' if r.wasSuccessful() else 'failed',fresh_random_labels=0,transformed_replay_presentations=PRESENTATIONS,synthetic_labelled_steps=1,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(data,indent=2)+'\n');print(stream.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
