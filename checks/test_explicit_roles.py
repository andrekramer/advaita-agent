"""R0 synthetic contracts; cumulative fixture budget and all attempts preserved."""
import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import time
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
import explicit_roles as experiment
from advaita.explicit_roles import RoleLearner, RoleLocal, BoundLocal, JointModel, aligned, history_score
from advaita.models import LocalModel
from audit_explicit_roles import verify_world,verify_run,truth,label
from roles_reference import align,priority
from explicit_roles_metrics import summarize, metrics
from audit_explicit_roles import verify_summary, verify_metrics
LABELS=0
CACHE={}
FILES=('advaita/explicit_roles.py','experiments/explicit_roles.py','experiments/explicit_roles_metrics.py',
    'checks/roles_reference.py','checks/audit_explicit_roles.py','checks/test_explicit_roles.py',
    'checks/roles_compatibility.py','experiments/explicit_roles_spec.md','experiments/explicit_roles_protocol.md',
    'experiments/explicit_roles_test_plan.md')


def charge(n):
    global LABELS
    LABELS+=n


class RolesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.worlds=[experiment.generate(3990,b,sizes=(4,1,8,16,4,4),review_every=4) for b in experiment.BRANCHES]
        charge(600)

    def test_a_worlds_and_latent_boundaries(self):
        for w in self.worlds:
            verify_world(w,4)
            for t in (0,240,241,528,529,1280):
                for observed in (False,True): self.assertEqual(experiment.forms_at(w,t,observed),truth(w,t,observed))
                for x in ([0,1],[2,3]): self.assertEqual(experiment.target(w,x,1,t),label(w,x,1,t))
        probability=self.worlds[1]
        self.assertEqual(experiment.forms_at(probability,240),experiment.forms_at(probability,241))
        self.assertNotEqual(experiment.forms_at(probability,240,True),experiment.forms_at(probability,241,True))

    def test_b_all_policies_full_independent_replay_restore_and_atomic_evidence(self):
        for policy in experiment.POLICIES:
            # Charge allocated presentation ceiling BEFORE running, including a failing run.
            charge(120 if policy in ('B64','U64') else 96)
            r,checkpoint=experiment.run(self.worlds[2],policy,3990,review_every=4,measure=False)
            verify_run(r,self.worlds[2],json.loads(checkpoint),review_every=4,measure=False)
            a=RoleLearner.restore(checkpoint);b=RoleLearner.restore(checkpoint)
            self.assertEqual(a.checkpoint(),checkpoint)
            before=a.checkpoint();a.predict([0,1],1);self.assertEqual(a.checkpoint(),before)
            with self.assertRaises(ValueError):a.step('main/1',self.worlds[2]['main'][0])
            self.assertEqual(a.checkpoint(),before)
            with self.assertRaises(ValueError):a.review('select/16',self.worlds[2]['selection'][-1])
            self.assertEqual(a.checkpoint(),before)
            row=self.worlds[2]['main'][0];charge(6)
            self.assertEqual(a.step('continuation',row),b.step('continuation',row))
            charge(24)
            self.assertEqual(a.review('continuation-select',self.worlds[2]['selection'][0]),b.review('continuation-select',self.worlds[2]['selection'][0]))
            self.assertEqual(a.checkpoint(),b.checkpoint())
            CACHE[policy]=(r,checkpoint)

    def test_c_stable_meanings_through_probability_crossing(self):
        n=RoleLocal(3990);n.model=LocalModel((0,0,1,1));n.stable=True
        n.model=BoundLocal(n.model,[0,0,1,1]);n.structural=True
        for i in range(32): n.update(dict(x=i%4,y=int(i%4<2)))
        charge(32)
        self.assertEqual(n.model.state()['groups'],[0,0,1,1])
        self.assertGreater(n.model.predict(0),n.model.predict(2))
        self.assertEqual(aligned((0,0,0,0),[1,1,1,0]),[1,1,1,1])
        for partition in ((0,0,0,0),(0,0,1,1),(0,1,0,1)):
            for old in ([0,0,0,0],[1,1,1,0],[1,0,0,1]): self.assertEqual(aligned(partition,old),align(partition,old))

    def test_d_history_bounded_and_deterministic_scores(self):
        _,checkpoint=CACHE['H128']; a=RoleLearner.restore(checkpoint)
        h=a.history[0]
        a.history=[dict(h,id=f'artificial/{i}') for i in range(192)]
        for n in a.nodes:n.history=a.history
        charge(3);a.step('bound',self.worlds[0]['main'][0]);self.assertEqual(len(a.history),192)
        self.assertEqual(a.history[-1]['id'],'bound')
        
        for x,y in zip(history_score(a.history,lambda r:r['x'][0],0),priority(a.history,lambda r:r['x'][0],0)): self.assertAlmostEqual(x,y,places=12)
        self.assertGreater(a.history_costs['feature_predictions'],0)
        self.assertGreater(sum(n.history_rows for n in a.nodes),0)
        for policy in ('B64','B128','U64','U128','R128'):
            c=json.loads(CACHE[policy][1]);self.assertEqual(c['history'],[])
            self.assertEqual(c['history_costs'],dict(feature_predictions=0,proposal_rows=0,records=0))

    def test_e_group_only_refits_and_empty_history_equivalence(self):
        rows=[dict(x=[0,0],a=0,local=[0,0],y=0)]*8
        learners=[]
        for policy in ('B64','U64','R128','H128'):
            a=RoleLearner([3990,3991],3990,policy=policy)
            for j in range(2):
                for i in range(8): a.observe_local(j,f'w/{j}/{i}',dict(x=i%4,y=0))
            charge(16)
            charge(8);a.train_upper([f'c/{i}' for i in range(8)],rows);learners.append(a)
        r,h=learners[-2:]
        # Before main history exists, H and R draw exactly the same proposals.
        charge(48)
        self.assertEqual(r.review('empty',rows),h.review('empty',rows))
        b,u=learners[:2];b_before=b.upper.state();u_before=u.upper.state()
        charge(6)
        b.step('new',dict(rows[0],y=1));u.step('new',dict(rows[0],y=1))
        self.assertEqual(b.upper.state(),b_before);self.assertNotEqual(u.upper.state(),u_before)

    def test_f_two_witness_collapse_recreation_and_frozen_archive(self):
        n=RoleLocal(3990);n.structural=True;n.stable=True;n.model=BoundLocal(LocalModel((0,0,1,1)),[1,1,0,0])
        for i in range(64):n.update(dict(x=i%4,y=0))
        charge(64);batch=[dict(x=i%4,y=0) for i in range(8)]
        charge(8);self.assertEqual(n.review(batch)['action'],'awaiting_reduction');pending=copy.deepcopy(n.pending)
        charge(1);n.update(dict(x=0,y=0));self.assertEqual(n.pending,pending)
        charge(8);self.assertEqual(n.review(batch)['action'],'collapsed')
        for i in range(64):n.update(dict(x=i%4,y=int(i%4>=2)))
        charge(64);n.deck=[(0,0,1,1),(0,0,0,1),(0,0,1,0),(0,1,1,1)]
        charge(8);self.assertEqual(n.review([dict(x=i%4,y=int(i%4>=2)) for i in range(8)])['action'],'improved')
        a=RoleLearner([3990,3991],3990,'fixed','R128')
        rows=[dict(x=[0,0],a=0,local=[0,0],y=0)]*32;ids=[f'i/{i}' for i in range(32)]
        charge(32);a.train_upper(ids,rows)
        a.deploy(JointModel((2,1),rows,a.models()),a.dependencies((2,1)),ids)
        charge(4);self.assertEqual(a.review('one',rows[:4])['upper']['action'],'awaiting_reduction')
        clone=RoleLearner.restore(a.checkpoint());charge(8)
        self.assertEqual(a.review('two',rows[:4]),clone.review('two',rows[:4]))
        self.assertEqual(a.checkpoint(),clone.checkpoint());archived=a.archive.state()
        self.assertIsNotNone(archived)
        charge(3);a.step('new',dict(rows[0],y=1));self.assertEqual(a.archive.state(),archived)
        a.nodes[1].model=BoundLocal(LocalModel((0,1,0,1)),[0,1,0,1])
        charge(4);self.assertFalse(a.review('three',rows[:4])['upper']['archive_check']['compatible'])
        self.assertEqual(a.archive.state(),archived)
        with self.assertRaises(PermissionError):JointModel((0,1)).view([0,0],a.models()).read((0,2))

    def test_g_summary_gates_arithmetic_and_failure_retention(self):
        # Derived scores, not learner presentations: independently check gates and pairing.
        runs=[]
        for seed in range(5):
            for ps in range(2):
                for branch in experiment.BRANCHES:
                    for policy in experiment.POLICIES:
                        candidate=policy in ('R128','H128')
                        m=dict(transfer_valid=True,final_valid=True,late_prediction_stable=True,late_structure_stable=True,
                            structure_errors=2 if candidate else 4,raw_reads=0,raw_bypass=0,group_changes=0,partition_changes=0,
                            retrievals=0,incompatible_archive=0,recovery=[384,640],
                            observed={k:(.37 if policy=='H128' else .40) for k in ('whole','adapt1','adapt2','late')},
                            latent={k:.4 for k in ('whole','adapt1','adapt2','late')})
                        runs.append(dict(seed=seed,proposal_seed=ps,branch=branch,policy=policy,metrics=m))
        summary=summarize(runs);verify_summary(runs,summary)
        self.assertTrue(summary['primary_pass']);self.assertTrue(summary['history_pass'])
        # A single damaging adaptation pair must fail even when the mean guard passes.
        r=next(r for r in runs if r['policy']=='R128')
        r['metrics']['observed']['adapt1']=.51
        summary=summarize(runs);verify_summary(runs,summary)
        self.assertFalse(summary['checks']['worst_pair']);self.assertFalse(summary['primary_pass'])
        # No structural errors in the control provides no evidence for a relative gain.
        for r in runs:r['metrics']['structure_errors']=0
        summary=summarize(runs);verify_summary(runs,summary)
        self.assertFalse(summary['checks']['representation_reduction'])

    def test_h_measurement_windows_and_censored_recovery(self):
        # Reuse already charged fixture rows, predictions and evaluations as arithmetic inputs.
        r=copy.deepcopy(CACHE['B64'][0]);w=copy.deepcopy(self.worlds[2])
        w['main']=(w['main']*80)[:1280]
        for key in ('predictions','local_predictions','raw_reads','diagnostics'):r[key]=(r[key]*80)[:1280]
        base=r['evaluations'][-1]
        r['evaluations']=[dict(base,index=t) for t in range(64,1281,64)]
        r['metrics']=metrics(r,w,experiment.target,experiment.forms_at)
        verify_metrics(r,w)


def main():
    folder=ROOT/'results/explicit-roles-r0';folder.mkdir(exist_ok=True)
    previous=list(folder.glob('fixtures-*.json'))
    used=sum(json.loads(p.read_text())['charged_labels'] for p in previous)
    summary_only='--summary-only' in sys.argv
    assert used+(0 if summary_only else 2000)<=5000,(used,'fixture ceiling')
    if summary_only:
        # Resume only the failed arithmetic contract. All seven other contracts passed
        # in attempt02 and their dependencies are unchanged. Verify that provenance.
        import ast
        parent=json.loads((folder/'fixtures-02.json').read_text())
        assert 'FAILED (failures=1)' in parent['log'] and 'test_g_summary' in parent['log']
        for name,digest in parent['tested_sources'].items():
            if name not in ('checks/test_explicit_roles.py','experiments/explicit_roles_metrics.py'):
                assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        oldtests=(folder/'fixture02-tests.py').read_text()
        oldmetrics=(folder/'fixture02-metrics.py').read_text()
        assert hashlib.sha256(oldtests.encode()).hexdigest()==parent['tested_sources']['checks/test_explicit_roles.py']
        assert hashlib.sha256(oldmetrics.encode()).hexdigest()==parent['tested_sources']['experiments/explicit_roles_metrics.py']
        oldclass=next(n for n in ast.parse(oldtests).body if isinstance(n,ast.ClassDef))
        newclass=next(n for n in ast.parse(Path(__file__).read_text()).body if isinstance(n,ast.ClassDef))
        assert ast.dump(oldclass)==ast.dump(newclass)
        expected=oldmetrics.replace('representation_fraction=None if not total else gain/total',
            "representation_fraction=None if not total else sum(x['gain'] for x in rep)/total")
        assert (ROOT/'experiments/explicit_roles_metrics.py').read_text()==expected
        RolesTests.setUpClass=classmethod(lambda cls:None)
    path=folder/f'fixtures-{len(previous)+1:02d}.json';start=time.monotonic();stream=io.StringIO()
    suite=unittest.TestSuite([RolesTests('test_g_summary_gates_arithmetic_and_failure_retention')]) if summary_only else unittest.defaultTestLoader.loadTestsFromTestCase(RolesTests)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    record=dict(resumed_from='fixtures-02.json (seven passed contracts)' if summary_only else None,
        verified_contracts=8 if result.wasSuccessful() else result.testsRun, status='pass' if result.wasSuccessful() and used+LABELS<=5000 else 'failed',tests=result.testsRun,
        charged_labels=LABELS,cumulative_labels=used+LABELS,elapsed_seconds=time.monotonic()-start,log=stream.getvalue(),
        tested_sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES})
    path.write_text(json.dumps(record,indent=2)+'\n');print(stream.getvalue());print('Labels:',LABELS,'cumulative:',used+LABELS)
    sys.exit(record['status']!='pass')

if __name__=='__main__':main()
