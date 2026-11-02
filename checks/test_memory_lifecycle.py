"""030 bounded fixtures; fixed seed6990 and no reserved outcomes."""
import copy,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import memory_lifecycle as e
from memory_lifecycle_metrics import metrics,summarize,WINDOWS
from audit_memory_lifecycle import verify_world,verify_run,verify_metrics,verify_summary
LABELS=0;CACHE={}
class Contracts(unittest.TestCase):
    def test_a_worlds_and_all_backends(self):
        global LABELS
        for h in e.BRANCHES:
            w=e.generate(6990,h,True);verify_world(w)
            policies=e.POLICIES if h=='repeated' else ('baseline','combined')
            for p in policies:
                LABELS+=224;r,c=e.run(w,p,6990,False);verify_run(r,w,json.loads(c),False);CACHE[h,p]=(r,w)
    def test_b_measurement_reconstruction(self):
        r,w=copy.deepcopy(CACHE['repeated','combined']);r['predictions']*=64;w['main']*=64
        ev=r['evaluations'][-1];r['evaluations']=[dict(ev,index=t) for t in range(64,2049,64)]
        r['metrics']=metrics(r,w,e.target,e.forms_at);verify_metrics(r,w)
        bad=copy.deepcopy(r);bad['metrics']['rare_loss']+=.01
        with self.assertRaises(AssertionError):verify_metrics(bad,w)
    def test_c_summary_gates(self):
        runs=[]
        for s in range(5):
            for q in range(2):
                for h in e.BRANCHES:
                    for p in e.POLICIES:
                        v=.4 if p=='combined' else .5
                        m=dict(observed={k:v for k in WINDOWS},latent={k:v for k in WINDOWS},endpoint_valid=[True]*4,final_valid=True,rare_loss=v,structure_errors=0,weakenings=0,transfers=0)
                        runs.append(dict(seed=s,proposal_seed=q,branch=h,policy=p,metrics=m))
        a=summarize(runs);verify_summary(runs,a);self.assertTrue(a['primary_pass'])
        next(r for r in runs if r['policy']=='combined' and r['branch']=='rare')['metrics']['observed']['whole']=.7
        a=summarize(runs);verify_summary(runs,a);self.assertFalse(a['gates']['preservation_worst'])
def main():
    out=ROOT/'results/memory-lifecycle-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'))
    used=sum(json.loads(p.read_text())['charged_labels'] for p in old);assert used+1792<=2000
    log=io.StringIO();start=time.monotonic();r=unittest.TextTestRunner(stream=log,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    record=dict(status='pass' if r.wasSuccessful() else 'failed',charged_labels=LABELS,cumulative_labels=used+LABELS,elapsed_seconds=time.monotonic()-start,log=log.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(record,indent=2)+'\n');print(log.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
