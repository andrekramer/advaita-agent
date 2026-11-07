"""036 reused streams and synthetic memory contracts, before fresh outcomes."""
import copy,hashlib,io,itertools,json,sys,time,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import preserved_prediction as e
from advaita.preserved_prediction import PreservedPrediction,ports
from advaita.coordinated_steering import CoordinatedMemory
from advaita.state import canonical,fingerprint
from preserved_prediction_metrics import summarize,WINDOWS
from audit_preserved_prediction import verify_run,verify_world,verify_summary
CACHE={};PRESENTATIONS=0;SYNTHETIC=0

class Contracts(unittest.TestCase):
    def test_a_reused_worlds_and_active_parity(self):
        global PRESENTATIONS
        original=json.loads((ROOT/'results/temporary-plasticity-v1/worlds.json').read_text())
        ws={w['branch']:w for w in original if w['seed']==2400}
        for h in e.HISTORIES:
            w=e.generate(2400,h);verify_world(w)
            if h in ws:self.assertEqual(w,ws[h])
            rs=[]
            for policy in e.POLICIES:
                r=e.run(w,policy,2400);PRESENTATIONS+=r['feedback_labels'];verify_run(r,w);CACHE[h,policy]=r;rs.append(r)
            self.assertEqual(rs[0]['predictions'],rs[1]['predictions'])
            for r in rs:
                self.assertEqual(r['active_predictions'],rs[0]['active_predictions']);self.assertEqual(r['reviews'],rs[0]['reviews'])
        old=e.prior.run(ws['forms'],'D512',2400);PRESENTATIONS+=old['feedback_labels'];r=CACHE['forms','discard']
        self.assertEqual(r['predictions'],old['predictions']);self.assertEqual(r['reviews'],old['reviews']);self.assertEqual(r['costs'],old['costs'])
    def model(self,policy):
        a=PreservedPrediction.restore(canonical(CACHE['stable','recall']['checkpoint']));a.recall=policy;a.selection_ids=[]
        a.memory.update(passes=0,confirmed=False,attempt_complete=False,route=False,events=[])
        a.upper=dict(spec=[0,0],counts={'0':[10.,100.],'1':[10.,100.]})
        a.memory['slot']=dict(upper=dict(spec=[0,0],counts={'0':[90.,100.],'1':[90.,100.]}),locals=[dict(groups=m['groups'].copy()) for m in a.locals],dependency=fingerprint(ports(a.locals,[0,0])))
        return a
    def review(self,a,t,y=1):
        global SYNTHETIC
        rows=[dict(x=[0,0],a=0,local=[0,0],y=y)]*32;SYNTHETIC+=96;a.tick=t
        return a.review(t,rows)
    def test_b_confirmation_admission_and_no_same_batch_use(self):
        with patch.object(CoordinatedMemory,'review',lambda a,t,rows:{}):
            for policy in e.POLICIES:
                a=self.model(policy);self.review(a,448);self.assertEqual(a.memory['passes'],1)
                self.review(a,512);self.assertTrue(a.memory['confirmed']);self.assertFalse(a.memory['route'])
                self.assertEqual(a.memory['slot'] is None,policy=='discard')
                self.review(a,576);self.assertEqual(a.memory['route'],policy=='recall')
                if policy=='recall':self.assertGreater(a.predictions([0,0],0)[2],a.active_predictions([0,0],0)[2])
                self.review(a,640,0);self.assertFalse(a.memory['route'])
            a=self.model('recall');self.review(a,448,0);self.review(a,512)
            self.assertFalse(a.memory['confirmed']);self.assertIsNone(a.memory['slot'])
    def test_c_meanings_and_immutable_parameters(self):
        a=self.model('recall');a.memory.update(confirmed=True,route=True)
        a.memory['slot']['upper']=dict(spec=[1,0],counts={f'{g}|{act}':[90.,100.] for g,act in itertools.product(range(2),repeat=2)})
        a.memory['slot']['dependency']=fingerprint(ports(a.locals,[1,0]));self.assertTrue(a.compatible())
        saved=canonical(a.memory['slot']);a.locals[0]['groups']=[1-x for x in a.locals[0]['groups']]
        self.assertFalse(a.compatible());self.assertEqual(a.predictions([0,0],0),a.active_predictions([0,0],0))
        a.refit();self.assertEqual(saved,canonical(a.memory['slot']))
        state=a.checkpoint();b=PreservedPrediction.restore(state);self.assertEqual(state,b.checkpoint());self.assertEqual(a.predictions([0,0],0),b.predictions([0,0],0))
        # Raw ports and omitted ports do not depend on a local category ordering.
        a.memory['slot']['upper']['spec']=[2,0];a.memory['slot']['dependency']=fingerprint(ports(a.locals,[2,0]));a.locals[0]['groups'].reverse();self.assertTrue(a.compatible())
        # A fresh gate cannot guarantee future correctness: it accepts the two
        # adequate confirmation batches and admission even if the next label flips.
        with patch.object(CoordinatedMemory,'review',lambda a,t,rows:{}):
            a=self.model('recall');self.review(a,448);self.review(a,512);self.review(a,576)
            self.assertTrue(a.memory['route']);self.assertGreater(a.predictions([0,0],0)[2],.5)
    def test_d_all_gates(self):
        rs=[]
        for s in range(5):
            for q in range(2):
                for h in e.HISTORIES:
                    for p in e.POLICIES:
                        m={typ:{k:[.4]*3 for k in WINDOWS} for typ in ('expected','observed','active_expected')}
                        if p=='recall' and h in ('forms','repeated'):m['expected']['early_return'][2]=.35
                        m.update(confirmed=True,retained=p!='discard',uses=64 if p=='recall' else 0,blocked=0,admitted_reviews=1,eligible_reviews=2,final_valid=True,active_final_valid=True,final_spec=[1,1],uses_by_window={k:0 for k in WINDOWS})
                        rs.append(dict(seed=s,proposal_seed=q,history=h,policy=p,metrics=m,predictions=[[.5]],active_predictions=[[.5]],reviews=[]))
        summary=summarize(rs);verify_summary(rs,summary);self.assertTrue(summary['empirical_pass'])
        for case in ('gain','cost','endpoint','parity'):
            bad=copy.deepcopy(rs)
            for r in bad:
                if r['policy']!='recall':continue
                if case=='gain':r['metrics']['expected']['early_return'][2]=.4
                if case=='cost':r['metrics']['expected']['active'][2]=.6
                if case=='endpoint':r['metrics']['final_valid']=False
                if case=='parity':r['active_predictions']=[[.6]]
            summary=summarize(bad);verify_summary(bad,summary);self.assertFalse(summary['empirical_pass'])

def main():
    out=ROOT/'results/preserved-prediction-fixtures';out.mkdir(exist_ok=True);previous=sorted(out.glob('attempt-*.json'));assert len(previous)<8
    start=time.monotonic();stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    data=dict(status='pass' if r.wasSuccessful() else 'failed',fresh_random_labels=0,reused_training_presentations=PRESENTATIONS,synthetic_scalar_presentations=SYNTHETIC,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(previous)+1:02d}.json').write_text(json.dumps(data,indent=2)+'\n');print(stream.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
