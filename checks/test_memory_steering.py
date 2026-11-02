"""031 bounded pre-outcome fixtures."""
import copy,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import memory_steering as e
from memory_steering_metrics import metrics,summarize,WINDOWS
from audit_memory_steering import verify_run,verify_metrics,verify_summary,selection,intervention
from memory_revision_reference import RevisionReference
from advaita.continuing import ContinuingLearner
from audit_nested_abstractions import close
LABELS=0;CACHE={}
class Contracts(unittest.TestCase):
    def test_a_all_control_paths(self):
        global LABELS
        w=e.life.generate(7990,'repeated',True)
        for p in e.POLICIES:
            LABELS+=224;r,c=e.run(w,p,7990,False);verify_run(r,w,json.loads(c),False);CACHE[p]=(r,w)
    def test_b_explicit_control_and_selector(self):
        r,w=CACHE['unsteered'];a=ContinuingLearner.restore(json.dumps(r['runtime_checkpoint']));ref=object.__new__(RevisionReference);ref.__dict__=copy.deepcopy(a.engine.__dict__)
        got=a.weaken_slow(0,review_tick=a.tick,reason=e.REASON);expected=intervention(ref,a.tick,0);close(got,expected);close(json.loads(a.learning_checkpoint()),ref.state())
        review=dict(weakenings=[dict(channel=j,qualifies=True,accepted=False,losses=[.9,.3,.7,.6]) for j in range(3)])
        self.assertEqual(e.choose(review),0);self.assertEqual(selection(review),0)
        review['weakenings'][0]['accepted']=True;self.assertEqual(e.choose(review),1);self.assertEqual(selection(review),1)
    def test_c_metrics_and_gates(self):
        r,w=copy.deepcopy(CACHE['targeted']);r['predictions']*=64;w['main']*=64;r['metrics']=metrics(r,w);verify_metrics(r,w)
        runs=[]
        for s in range(5):
            for q in range(2):
                for h in e.BRANCHES:
                    for p in e.POLICIES:
                        v=.35 if p=='targeted' else .45
                        m={n:{k:v for k in WINDOWS} for n in ('observed','latent','unaffected')};m.update(final_valid=True,trigger=None,controlled=False)
                        runs.append(dict(seed=s,proposal_seed=q,branch=h,policy=p,metrics=m))
        result=summarize(runs);verify_summary(runs,result);self.assertTrue(result['primary_pass'])
        next(r for r in runs if r['policy']=='targeted')['metrics']['unaffected']['whole']=.7
        result=summarize(runs);verify_summary(runs,result);self.assertFalse(result['gates']['unaffected_worst'])
def main():
    out=ROOT/'results/memory-steering-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'));used=sum(json.loads(p.read_text())['charged_labels'] for p in old);assert used+672<=1000
    stream=io.StringIO();start=time.monotonic();result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    record=dict(status='pass' if result.wasSuccessful() else 'failed',charged_labels=LABELS,cumulative_labels=used+LABELS,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(record,indent=2)+'\n');print(stream.getvalue());sys.exit(not result.wasSuccessful())
if __name__=='__main__':main()
