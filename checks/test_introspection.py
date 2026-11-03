"""032 pre-outcome fixtures. Only replay seed7990, already used in031."""
import copy,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import introspection as e
from introspection_controller import packet,decide
from introspection_metrics import direction,measure,summarize
from audit_introspection import verify_record,verify_metrics,verify_summary,decision
from advaita.continuing import ContinuingLearner
from audit_nested_abstractions import close
CACHE={};PRESENTATIONS=0

class Contracts(unittest.TestCase):
    def test_a_replay_all_four_branches(self):
        global PRESENTATIONS
        w=e.life.generate(7990,'repeated',True);r=e.run(w,7990,False)
        PRESENTATIONS=r['acquisition']['costs']['feedback_labels']+3*r['tick']+3*sum(len(xs) for t,xs in w['selection'].items() if int(t)<=r['tick'])+12*(len(w['main'])-r['tick']+sum(len(xs) for t,xs in w['selection'].items() if int(t)>r['tick']))
        verify_record(r,w,False);CACHE.update(r=r,w=w)
    def test_b_readonly_and_accurate_packet(self):
        a=ContinuingLearner.restore(json.dumps(CACHE['r']['checkpoint']));before=a.checkpoint();v=packet(a)
        self.assertEqual(before,a.checkpoint());close(v,CACHE['r']['packet'])
        v['observed']['locals'][0]['partition'][0]=99;v['observed']['last_review']['channels'].clear();v['observed']['pending'].append('bad')
        self.assertEqual(before,a.checkpoint());self.assertNotEqual(v,packet(a))
        # Neither observations nor inferred fields admit world/future/checkpoint data.
        self.assertEqual(set(packet(a)),{'observed','inferred'})
        self.assertEqual(set(packet(a)['observed']),{'memory','tick','active','locals','upper','evidence_mass','last_review','controls','costs','pending','revision_pending'})
    def test_c_choices_ports_and_uncertainty(self):
        v=copy.deepcopy(CACHE['r']['packet'])
        for spec in ([0,1],[1,2],[2,0]):
            v['observed']['upper']['spec']=spec
            v['inferred']['upper_ports']=[('absent','group_membership','raw_state')[s] for s in spec]
            events=v['observed']['last_review']['weakenings']
            for ev in events:ev.update(qualifies=True,accepted=False,losses=[.9,.3,.6,.5])
            d=decide(v);close(d,decision(v));self.assertEqual(d['choices'],dict(no_op=None,disagreement=0,aware=2,rotated=1))
            events[2]['accepted']=True;self.assertIsNone(decide(v)['choices']['aware'])
            for ev in events:ev['qualifies']=False
            d=decide(v);self.assertTrue(all(j is None for j in d['choices'].values()));self.assertTrue(all(f['future']=='uncertain' for f in d['forecasts']))
    def test_d_control_invalid_reuse_stale_and_noop(self):
        a=ContinuingLearner.restore(json.dumps(CACHE['r']['checkpoint']));before=a.checkpoint()
        with self.assertRaises(ValueError):a.weaken_slow(0,review_tick=a.tick-1,reason=e.REASON)
        self.assertEqual(before,a.checkpoint());a.weaken_slow(0,review_tick=a.tick,reason=e.REASON);after=a.checkpoint()
        with self.assertRaises(ValueError):a.weaken_slow(0,review_tick=a.tick,reason=e.REASON)
        self.assertEqual(after,a.checkpoint())
    def test_e_metrics_classification(self):
        for g,label in [(-.006,'harm'),(-.005,'no_effect'),(0,'no_effect'),(.005,'no_effect'),(.006,'improvement')]:self.assertEqual(direction(g),label)
        r=copy.deepcopy(CACHE['r']);w=copy.deepcopy(CACHE['w']);w['main']*=64
        for b in r['branches'].values():b['predictions']=(b['predictions']*128)[:2048-r['tick']]
        r['metrics']=measure(r,w);verify_metrics(r,w)
    def test_f_summary_pass_and_fail(self):
        records=[]
        for seed in range(5):
            for ps in range(2):
                for h in e.HISTORIES:
                    view=copy.deepcopy(CACHE['r']['packet'])
                    for ev in view['observed']['last_review']['weakenings']:ev.update(qualifies=ev['channel'] in (0,2),accepted=False,losses=[.9,.3,.6,.5])
                    d=decide(view);branches={}
                    for name in ('none','0','1','2'):
                        value=.38 if name=='2' else .4
                        branches[name]={k:dict(observed=[.4,.4,value],latent=value) for k in ('future','remaining','returning','later')};branches[name]['valid']=True
                    forecasts=[dict(channel=j,eligible=j in (0,2),gain=.02 if j==2 else 0.,own_gain=.02,actual='improvement' if j==2 else 'no_effect',own_actual='improvement',immediate_delta=.1 if j==2 else 0.,immediate_actual='change' if j==2 else 'no_change') for j in range(3)]
                    records.append(dict(seed=seed,proposal_seed=ps,history=h,decision=d,metrics=dict(branches=branches,forecasts=forecasts)))
        s=summarize(records);verify_summary(records,s);self.assertTrue(s['primary_pass'])
        records[0]['metrics']['branches']['2']['returning']['observed'][0]=.8
        s=summarize(records);verify_summary(records,s);self.assertFalse(s['gates']['preservation'])
        for r in records:
            for f in r['metrics']['forecasts']:f['actual']='harm';f['immediate_actual']='change'
            r['metrics']['branches']['2']['future']['observed'][2]=.5;r['metrics']['branches']['2']['valid']=False
        s=summarize(records);verify_summary(records,s)
        for key in ('mechanical','forecast_accuracy','steering_gain','steering_vs_none','final_validity'):self.assertFalse(s['gates'][key])

def main():
    out=ROOT/'results/introspection-fixtures';out.mkdir(exist_ok=True);old=sorted(out.glob('attempt-*.json'));assert len(old)<8
    start=time.monotonic();stream=io.StringIO();r=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Contracts))
    record=dict(status='pass' if r.wasSuccessful() else 'failed',new_labels=0,replayed_presentations=PRESENTATIONS,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in e.FILES})
    (out/f'attempt-{len(old)+1:02d}.json').write_text(json.dumps(record,indent=2)+'\n');print(stream.getvalue());sys.exit(not r.wasSuccessful())
if __name__=='__main__':main()
