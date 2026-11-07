"""035 pre-outcome fixtures: saved worlds, independent replay and synthetic gates."""
import copy,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import temporary_plasticity as e
import coordinated_steering as prior
from advaita.temporary_plasticity import TemporaryPlasticity
from advaita.state import canonical
from temporary_plasticity_metrics import summarize,WINDOWS
from audit_temporary_plasticity import verify_run,verify_world,verify_summary
CACHE={};PRESENTATIONS=0;SYNTHETIC=0

class Fake:
    def __init__(self):
        self.tick=0;self.reviewed=False;self.p=.9;self.locals=[];self.upper={};self.half_lives=[1024]*3;self.commands=[]
    def predictions(self,x,a):
        assert not self.reviewed
        return [.5,.5,self.p]
    def checkpoint(self):return canonical(self.__dict__)
    def review(self,t,rows):
        global SYNTHETIC
        SYNTHETIC+=3*len(rows);self.reviewed=True;self.p=.01
        return {'tick':t}
    def configure(self,*,lock,plastic,reason):
        assert not any(c['tick']==self.tick for c in self.commands)
        self.half_lives=[128 if j in plastic else 1024 for j in range(3)]
        c=dict(tick=self.tick,lock=lock,plastic=plastic,reason=reason);self.commands.append(c);return c

def step(c,t,p=.9):
    c.learner.tick=t;c.learner.p=p;c.learner.reviewed=False
    return c.review(t,[dict(x=[0,0],a=0,local=[1,1],y=1)]*32)

class Contracts(unittest.TestCase):
    def test_a_reused_runs_and_parity(self):
        global PRESENTATIONS
        saved=json.loads((ROOT/'results/coordinated-steering-v1/worlds.json').read_text())
        worlds={w['branch']:w for w in saved if w['seed']==2300}
        for h in e.HISTORIES:
            # Regenerate only an already released seed/noise stream; no reserved seeds.
            w=e.generate(2300,h);verify_world(w)
            if h in worlds:self.assertEqual(w,worlds[h])
            policies=e.POLICIES if h=='forms' else ('G',)
            for policy in policies:
                r=e.run(w,policy,2300);PRESENTATIONS+=r['feedback_labels'];verify_run(r,w);CACHE[h,policy]=r
            if h=='forms':
                for policy,oldpolicy in [('P','P'),('D512','D')]:
                    old=prior.run(worlds[h],oldpolicy,2300);PRESENTATIONS+=old['feedback_labels']
                    for k in ('predictions','reviews','evaluations','costs'):self.assertEqual(CACHE[h,policy][k],old[k])
        for h in ('forms','repeated'):
            a=e.generate(2300,h);b=e.generate(2300,h+'_persistent')
            self.assertEqual(a['main'][:1024],b['main'][:1024])
    def test_b_closure_and_label_ordering(self):
        for policy,end in [('D128',640),('D256',768),('D512',1024),('G',640),('P',None)]:
            c=TemporaryPlasticity(Fake(),policy,0);step(c,512)
            for t in range(576,1025,64):step(c,t)
            self.assertEqual(c.state['closed_at'],end);self.assertEqual(c.learner.commands[-1]['lock'],[])
            self.assertEqual(c.learner.half_lives,[1024]*3)
        c=TemporaryPlasticity(Fake(),'G',0);step(c,512)
        step(c,576);_,_,d=step(c,640,.1);self.assertEqual(d['streak'],0)
        step(c,704);step(c,768);self.assertEqual(c.state['closed_at'],768)
        step(c,832,.1);self.assertEqual(c.state['closed_at'],768)
        before=c.checkpoint()
        with self.assertRaises(ValueError):c.review(832,[dict(x=[0,0],a=0,y=1)])
        self.assertEqual(c.checkpoint(),before)
        for late in (False,True):
            c=TemporaryPlasticity(Fake(),'G',0);step(c,512)
            for t in range(576,1025,64):step(c,t,.9 if late and t>=960 else .1)
            self.assertEqual(c.state['closed_at'],1024);self.assertEqual(c.state['closure_reason'],'ceiling')
        # Two misleading but adequate batches still close the hand-coded rule;
        # the controller has no oracle granting knowledge of a later reversal.
        c=TemporaryPlasticity(Fake(),'G',0);step(c,512);step(c,576);step(c,640)
        self.assertEqual(c.state['closure_reason'],'adequate')
    def test_c_checkpoint_and_inspection(self):
        r=CACHE['forms','G'];c=TemporaryPlasticity.restore(canonical(r['checkpoint']));before=c.checkpoint()
        self.assertEqual(json.loads(before),r['checkpoint'])
        x=c.learner.inspect();x['half_lives'][2]=1;x['locals'].clear();self.assertEqual(c.checkpoint(),before)
        self.assertEqual([x['tick'] for x in r['restore_checks']],[576,768])
    def test_d_gates(self):
        rs=[]
        for seed in range(5):
            for ps in range(2):
                for h in e.HISTORIES:
                    for p in e.POLICIES:
                        v=.4 if p in ('G','D128','D256') else .5 if p=='P' else .41
                        m={typ:{k:[v]*3 for k in WINDOWS} for typ in ('expected','observed')}
                        m['expected']['early_return']=[.4]*3 if p!='D512' else [.45]*3
                        m.update(protected=0,burst_correct=1.,final_valid=True,final_local_exact=[True,True],final_spec=[1,1],closed_at=None if p=='P' else 640,closure_reason=None if p=='P' else 'adequate',duration=0 if p=='P' else 128)
                        rs.append(dict(seed=seed,proposal_seed=ps,history=h,policy=p,metrics=m))
        s=summarize(rs);verify_summary(rs,s);self.assertTrue(s['primary']['empirical_pass'])
        for kind in ('adaptation','return','preservation','protection','endpoint'):
            bad=copy.deepcopy(rs)
            for r in bad:
                if r['policy']!='G':continue
                m=r['metrics']
                if kind=='adaptation':m['expected']['active'][2]=.7
                if kind=='return':m['expected']['early_return'][2]=.6
                if kind=='preservation':m['expected']['later'][0]=.8
                if kind=='protection':m['burst_correct']=0
                if kind=='endpoint':m['final_valid']=False
            s=summarize(bad);verify_summary(bad,s);self.assertFalse(s['primary']['empirical_pass'])

def main():
    out=ROOT/'results/temporary-plasticity-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'));assert len(old)<8
    start=time.monotonic();stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    data=dict(status='pass' if r.wasSuccessful() else 'failed',fresh_random_labels=0,reused_world_training_presentations=PRESENTATIONS,synthetic_scalar_presentations=SYNTHETIC,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(data,indent=2)+'\n');print(stream.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
