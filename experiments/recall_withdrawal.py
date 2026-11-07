"""037 final bounded steering study: explicit and evidence-responsive withdrawal."""
import copy,gzip,hashlib,json,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.recall_withdrawal import RecallWithdrawal
from advaita.structural import StructuralLearner
from advaita.state import canonical
import preserved_prediction as prior
from recall_withdrawal_metrics import measure,summarize
HISTORIES=prior.HISTORIES
POLICIES=('shadow','current','command','evidence')
FILES=['advaita/recall_withdrawal.py','experiments/recall_withdrawal.py','experiments/recall_withdrawal_metrics.py','experiments/recall_withdrawal_protocol.md','checks/audit_recall_withdrawal.py','checks/test_recall_withdrawal.py']

def run(w,policy,ps):
    acq,c=prior.prior.life.legacy_run(w,ps,True);a=RecallWithdrawal(StructuralLearner.restore(c),policy)
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,policy=policy,acquisition=acq,acquisition_checkpoint=json.loads(c),predictions=[],active_predictions=[],prediction_events=[],reviews=[],evaluations=[],inspections=[],controls=[],restore_checks=[],capture=None,steering_commands=[])
    extra=0
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(a.slow[j]) for j,h in enumerate(a.half_lives) if h!=1024)
        r['predictions'].append(a.observe(t,row));r['active_predictions'].append(a._prediction_event['active']);r['prediction_events'].append(copy.deepcopy(a._prediction_event))
        if str(t) in w['selection']:
            r['reviews'].append(a.review(t,w['selection'][str(t)]))
            if t==384:r['capture']=copy.deepcopy(a.memory['slot'])
            if t in (512,1024):r['controls'].append(a.configure(lock=[w['instruction']['protected']] if t==512 else [],plastic=[2] if t==512 else [],reason='037 supplied downstream boost' if t==512 else '037 supplied release'))
        if policy=='command' and t in (1552,1664):
            r['steering_commands'].append(a.set_recall_block(t==1552,reason='037 scheduled recall block' if t==1552 else '037 scheduled block release',source='supplied experiment schedule'))
        if str(t) in w['selection']:
            r['inspections'].append(a.inspect());r['evaluations'].append(prior.evaluate(a,w,t))
        if t in (448,1544,1552,1664):
            saved=a.checkpoint();a=RecallWithdrawal.restore(saved);assert a.checkpoint()==saved
            r['restore_checks'].append(dict(tick=t,sha256=hashlib.sha256(saved.encode()).hexdigest()))
    r['checkpoint']=json.loads(a.checkpoint());r['costs']=a.costs.copy();r['memory_events']=a.memory['events'];r['extra_decay_cell_visits']=extra
    r['feedback_labels']=acq['costs']['feedback_labels']+3*(len(w['main'])+sum(map(len,w['selection'].values())))
    r['metrics']=measure(r,w);return r

def hashes():
    parent=ROOT/'results/preserved-prediction-v1';m=json.loads((parent/'manifest.json').read_text())
    completion=json.loads((parent/'completion.json').read_text());m.update(completion['verification_hashes'])
    for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    paths=set(m)|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.glob('*') if p.is_file()}|{str(p.relative_to(ROOT)) for p in (ROOT/'results/recall-withdrawal-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}

def main():
    assert json.loads((ROOT/'results/preserved-prediction-v1/audit.json').read_text())['status']=='pass'
    fs=sorted((ROOT/'results/recall-withdrawal-fixtures').glob('attempt-*.json'));f=json.loads(fs[-1].read_text());assert f['status']=='pass' and len(fs)<=8
    for p,d in f['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/recall-withdrawal-v1';out.mkdir(exist_ok=False);m=hashes();(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');start=time.monotonic();rs=[];ws=[]
    def timeout(*_):raise TimeoutError('037 runner 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2600,2605):
            for h in HISTORIES:
                w=prior.generate(seed,h);ws.append(w);(out/'worlds.json').write_text(json.dumps(ws)+'\n')
                for ps in (2600,2601):
                    for policy in POLICIES:
                        r=run(w,policy,ps);rs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(rs)}/240',flush=True)
        assert hashes()==m;total=prior.prior.prior.totals(rs,ws)
        total.update(extra_decay_cell_visits=sum(r['extra_decay_cell_visits'] for r in rs),memory_diagnostic_queries=sum(r['checkpoint']['memory']['diagnostic_queries'] for r in rs),archive_prediction_queries=sum(r['checkpoint']['memory']['archive_prediction_queries'] for r in rs),monitor_queries=sum(r['checkpoint']['steering']['monitor_queries'] for r in rs),grid_predictions=2*total['grid_predictions'])
        assert total['generated_labels']==307200 and total['used_labels']==2457600 and total['memory_diagnostic_queries']==399360
        for k,v in dict(candidate_fits=450000,scoring_queries=30000000,raw_bin_visits=140000000,grid_predictions=500000,extra_decay_cell_visits=3932160,monitor_queries=491520).items():assert total[k]<=v
        data=dict(status='completed_pending_audit',summary=summarize(rs),totals=total,hashes=m,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(data,indent=2)+'\n');print(data['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),runs=len(rs),elapsed_seconds=time.monotonic()-start))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
