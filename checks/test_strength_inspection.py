"""Deterministic preflight fixtures; no fresh confirmation environments."""
import copy,hashlib,io,json,sys,time,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
from advaita.controlled import ControlledLearner
from test_controlled_learner import acquired
from strength_inspection import packet,describe,decode,decisions,probe,CONTEXTS,ACTIONS
from strength_inspection_run import run_probes,SOURCES
from audit_strength_inspection import Reference,inspect_reference,projections,verify_probes
from audit_nested_abstractions import close


class Contracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        core=acquired();cls.a=ControlledLearner(core);cls.ref=Reference(json.loads(core.checkpoint()),'shadow')
        cls.recent=[]
        for tick in range(1,641):
            x,y,act=CONTEXTS[(tick-1)%32]
            row=dict(x=[x,y],a=act,local=[int(x>=2),int(y>=2)],y=int(x>=2)^int(y>=2)^act)
            cls.recent.append(row)
            close(cls.a.observe(tick,row),cls.ref.observe(tick,row))
            if tick%64==0:
                cls.review=cls.a.review(tick,cls.recent[-32:]);cls.ref.review(tick,cls.recent[-32:],cls.review)
        cls.full=packet(cls.a,cls.recent[-64:],2,0)

    def test_detached_exact_bank_descriptions(self):
        a=self.a;saved=a.checkpoint()
        close(self.full,inspect_reference(self.ref,self.recent[-64:],2,0,self.review))
        for mode in ('raw_banks','direction_strength'):
            v=describe(self.full,mode)
            for j,table in enumerate(v['cells']):
                for key,c in table.items():
                    f,s=decode(v,j,c);close([f,s],[self.full['cells'][j][key]['fast'],self.full['cells'][j][key]['slow']])
            v['cells'][0].clear()
        self.assertEqual(a.checkpoint(),saved)
        self.assertEqual(ControlledLearner.restore(saved).checkpoint(),saved)
        ds=decisions(self.full)
        for mode in ('existing','raw_banks','direction_strength'):close(ds[mode],projections(self.full,mode))

    def test_probe_clock_priors_and_command_parity(self):
        saved=self.a.checkpoint();ps=run_probes(saved,self.full)
        record=dict(packet=self.full,probes=ps);verify_probes(self.ref,record)
        maximum=max(abs(p['actual'][w][j]-p['forecasts'][m][w][j]) for p in ps for w in ('before','after') for j in range(3) for m in ('raw_banks','direction_strength'))
        self.assertLessEqual(maximum,1e-10);self.assertEqual(saved,self.a.checkpoint())
        b=ControlledLearner.restore(saved)
        b.configure(lock=[],plastic=[2],reason='fixture',source='fixture')
        for _ in range(64):b.observe(b.tick+1,self.recent[-1])
        b.review(b.tick,self.recent[-32:]);before=json.loads(b.native_checkpoint())
        b.configure(lock=[],plastic=[],reason='release',source='fixture')
        after=json.loads(b.native_checkpoint())
        for k in ('fast','slow','locals','upper'):self.assertEqual(before[k],after[k])
        self.assertEqual(after['half_lives'],[1024]*3)

    def test_hidden_allocation_and_empty_bank(self):
        a=copy.deepcopy(self.full);b=copy.deepcopy(a)
        for j in range(3):
            for key in a['cells'][j]:
                for v in (a,b):v['cells'][j][key]['total']=[50.,100.]
                a['cells'][j][key].update(fast=[9.,10.],slow=[41.,90.])
                b['cells'][j][key].update(fast=[1.,10.],slow=[49.,90.])
        self.assertEqual(describe(a,'existing'),describe(b,'existing'))
        pa=probe(describe(a,'raw_banks'),'2',[0,0],0,[0,0,0])
        pb=probe(describe(b,'raw_banks'),'2',[0,0],0,[0,0,0])
        self.assertGreater(max(abs(x-y) for x,y in zip(pa['before'],pb['before'])),1e-5)
        for table in a['cells']:
            for cell in table.values():cell.update(fast=[0.,0.],slow=[0.,0.],total=[0.,0.])
        view=describe(a,'direction_strength')
        self.assertTrue(all(c['fast']['direction'] is None for t in view['cells'] for c in t.values()))
        prediction=probe(view,'none',[0,0],0,[1,0,1])
        self.assertEqual(prediction['before'],[.5]*3);close(prediction['after'],[2/3,1/3,2/3])


def main():
    out=ROOT/'results/strength-inspection-fixtures';out.mkdir(exist_ok=True)
    dest=out/f'attempt-{len(list(out.glob("attempt-*.json")))+1:02d}.json';assert not dest.exists()
    start=time.monotonic();log=io.StringIO();suite=unittest.defaultTestLoader.loadTestsFromTestCase(Contracts)
    result=unittest.TextTestRunner(stream=log,verbosity=2).run(suite)
    record=dict(status='pass' if result.wasSuccessful() else 'failed',tests=result.testsRun,log=log.getvalue(),
                elapsed_seconds=time.monotonic()-start,fresh_confirmation_labels=0,
                sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in SOURCES})
    dest.write_text(json.dumps(record,indent=2)+'\n');print(log.getvalue());print(dest)
    return not result.wasSuccessful()


if __name__=='__main__':sys.exit(main())
