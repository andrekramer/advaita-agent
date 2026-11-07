"""037 reused trajectories, intervention contracts and prespecified gate fixtures."""
import copy,hashlib,io,json,sys,time,unittest
from unittest.mock import patch
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import recall_withdrawal as e
from advaita.recall_withdrawal import RecallWithdrawal
from advaita.preserved_prediction import PreservedPrediction,ports
from advaita.state import canonical,fingerprint
from recall_withdrawal_metrics import summarize,WINDOWS
from audit_recall_withdrawal import verify_run,verify_summary
CACHE={};PRESENTATIONS=0;SYNTHETIC=0

def step(a,row=None):
    global SYNTHETIC
    if row is not None:SYNTHETIC+=3
    return a.observe(a.tick+1,row)

class Contracts(unittest.TestCase):
    def test_a_replay_and_reference_parity(self):
        global PRESENTATIONS
        saved=json.loads((ROOT/'results/preserved-prediction-v1/worlds.json').read_text());ws={w['branch']:w for w in saved if w['seed']==2500}
        for h in e.HISTORIES:
            w=e.prior.generate(2500,h);self.assertEqual(w,ws[h])
            for policy in e.POLICIES:
                r=e.run(w,policy,2500);PRESENTATIONS+=r['feedback_labels'];verify_run(r,w);CACHE[h,policy]=r
        for policy,oldpolicy in [('shadow','shadow'),('current','recall')]:
            old=e.prior.run(ws['forms'],oldpolicy,2500);PRESENTATIONS+=old['feedback_labels'];r=CACHE['forms',policy]
            for k in ('predictions','active_predictions','reviews','evaluations','costs'):self.assertEqual(r[k],old[k])
    def model(self,policy='evidence',bad=True):
        a=RecallWithdrawal.restore(canonical(CACHE['stable','current']['checkpoint']));a.steering.update(policy=policy,blocked=False,window=[],commands=[],monitors=[],reviews=[],withdrawals=0)
        upper=dict(spec=[0,0],counts={'0':[999. if bad else 0.,1000.],'1':[999. if bad else 0.,1000.]})
        a.memory.update(confirmed=True,route=True,slot=dict(upper=upper,locals=[dict(groups=m['groups'].copy()) for m in a.locals],dependency=fingerprint(ports(a.locals,[0,0]))))
        return a
    def test_b_causal_withdrawal_and_partial_restore(self):
        row=dict(x=[0,0],a=0,local=[0,0],y=0);a=self.model()
        for _ in range(8):step(a,row)
        self.assertTrue(a.memory['route']);self.assertEqual(len(a.steering['window']),8)
        saved=a.checkpoint();b=RecallWithdrawal.restore(saved);self.assertEqual(saved,b.checkpoint())
        for _ in range(8):self.assertEqual(step(a,row),step(b,row))
        self.assertEqual(a.checkpoint(),b.checkpoint());self.assertFalse(a.memory['route']);self.assertEqual(a._prediction_event['source'],'archive')
        step(a,row);self.assertEqual(a._prediction_event['source'],'active');self.assertEqual(a.steering['withdrawals'],1)
        for policy in ('current','command'):
            a=self.model(policy)
            for _ in range(16):step(a,row)
            self.assertTrue(a.memory['route']);self.assertTrue(a.steering['monitors'][-1]['triggered']);self.assertFalse(a.steering['monitors'][-1]['withdrawn'])
        a=self.model(bad=False)
        for _ in range(16):step(a,row)
        self.assertTrue(a.memory['route']);self.assertFalse(a.steering['monitors'][-1]['triggered'])
        a=self.model()
        for _ in range(8):step(a,row)
        step(a,None);self.assertEqual(a.steering['window'],[])
    def test_c_block_precedence_release_and_validation(self):
        global SYNTHETIC
        a=self.model('command');before=a.checkpoint()
        for blocked,reason,source in [(1,'x','y'),(True,'','y'),(True,'x','')]:
            with self.assertRaises(ValueError):a.set_recall_block(blocked,reason=reason,source=source)
            self.assertEqual(a.checkpoint(),before)
        a.set_recall_block(True,reason='Fixture block',source='fixture');blocked=a.checkpoint()
        with self.assertRaises(ValueError):a.set_recall_block(False,reason='Duplicate',source='fixture')
        self.assertEqual(a.checkpoint(),blocked);a=RecallWithdrawal.restore(blocked);self.assertEqual(a.checkpoint(),blocked)
        packet=a.inspect_steering();packet['steering']['blocked']=False;self.assertTrue(a.steering['blocked'])
        row=dict(x=[0,0],a=0,local=[0,0],y=0);step(a,row);self.assertEqual(a._prediction_event['source'],'active')
        def admit(obj,t,rows):obj.memory['route']=True;return {'fixture_admit':True}
        with patch.object(PreservedPrediction,'review',admit):
            SYNTHETIC+=3;a.review(a.tick,[row]);self.assertFalse(a.memory['route'])
            a.set_recall_block(False,reason='Fixture release',source='fixture');self.assertFalse(a.memory['route'])
            step(a,row);self.assertEqual(a._prediction_event['source'],'active')
            SYNTHETIC+=3;a.review(a.tick,[row]);self.assertTrue(a.memory['route'])
        step(a,None);before=a.checkpoint()
        with self.assertRaises(ValueError):a.set_recall_block(True,reason='Missing label',source='fixture')
        self.assertEqual(a.checkpoint(),before)
    def test_d_gates(self):
        records=[]
        for seed in range(5):
            for ps in range(2):
                for h in e.HISTORIES:
                    for p in e.POLICIES:
                        m={typ:{k:[.4]*3 for k in WINDOWS} for typ in ('expected','observed','active_expected')}
                        if p=='current':m['expected']['rechange'][2]=.7
                        if p in ('evidence','current') and h in ('forms','repeated'):m['expected']['returning'][2]=.37
                        m.update(confirmed=True,uses=64,withdrawals=1 if p=='evidence' else 0,commands=2 if p=='command' else 0,blocked_uses=0,final_valid=True,active_final_valid=True)
                        records.append(dict(seed=seed,proposal_seed=ps,history=h,policy=p,metrics=m,active_predictions=[[.5]],reviews=[]))
        s=summarize(records);verify_summary(records,s);self.assertTrue(s['empirical_pass'])
        for case in ('effect','usefulness','retention','collateral','endpoint','parity'):
            bad=copy.deepcopy(records)
            for r in bad:
                if r['policy']!='evidence':continue
                m=r['metrics']
                if case=='effect':m['expected']['rechange'][2]=.7
                if case=='usefulness':m['expected']['returning'][2]=.4
                if case=='retention':m['expected']['early_return'][2]=.42
                if case=='collateral':m['expected']['later'][0]=.6
                if case=='endpoint':m['final_valid']=False
                if case=='parity':r['active_predictions']=[[.6]]
            s=summarize(bad);verify_summary(bad,s);self.assertFalse(s['empirical_pass'])

def main():
    out=ROOT/'results/recall-withdrawal-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'));assert len(old)<8
    start=time.monotonic();stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    data=dict(status='pass' if r.wasSuccessful() else 'failed',fresh_random_labels=0,reused_training_presentations=PRESENTATIONS,synthetic_scalar_presentations=SYNTHETIC,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(data,indent=2)+'\n');print(stream.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
