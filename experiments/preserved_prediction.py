"""036 frozen-predictor recall separated from continuing active learning."""
import copy,gzip,hashlib,json,signal,sys,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.preserved_prediction import PreservedPrediction
from advaita.structural import StructuralLearner
from advaita.state import canonical
import temporary_plasticity as prior
from preserved_prediction_metrics import measure,summarize
HISTORIES=('stable','forms','repeated','forms_persistent','repeated_persistent','forms_other')
POLICIES=('discard','shadow','recall')
FILES=['advaita/preserved_prediction.py','experiments/preserved_prediction.py','experiments/preserved_prediction_metrics.py','experiments/preserved_prediction_protocol.md','checks/audit_preserved_prediction.py','checks/test_preserved_prediction.py']

def third_form(w):
    equivalent=lambda a,b:all((a[x]==a[y])==(b[x]==b[y]) for x in range(4) for y in range(4))
    return next(list(f) for f in ((0,0,1,1),(0,1,0,1),(0,1,1,0)) if not equivalent(f,w['forms'][w['affected']]) and not equivalent(f,w['alternative']))

def forms_at(w,t,observed=False):
    if w['branch']=='forms_other':
        f=prior.forms_at(dict(w,branch='forms'),t,observed)
        if 1025<=t<=1536:f[w['affected']]=third_form(w)
        return f
    return prior.forms_at(w,t,observed)

def target(w,x,a,t):
    f=forms_at(w,t,True);return f[0][x[0]]^f[1][x[1]]^a

world_eval=types.SimpleNamespace(CONTEXTS=prior.life.CONTEXTS,forms_at=forms_at,target=target)
_evaluate=types.FunctionType(prior.prior.evaluate.__code__,dict(prior.prior.evaluate.__globals__,life=world_eval))

def evaluate(a,w,t):
    deployed=_evaluate(a,w,t)
    class Active:
        locals=a.locals;upper=a.upper
        predictions=a.active_predictions
    active=_evaluate(Active(),w,t)
    using=a.recall=='recall' and a.memory['route'] and a.memory['confirmed'] and a.compatible()
    deployed['spec']=a.memory['slot']['upper']['spec'].copy() if using else a.upper['spec'].copy()
    deployed.update(active=active,source='archive' if using else 'active')
    return deployed

def generate(seed,h):
    w=prior.generate(seed,'forms' if h=='forms_other' else h)
    if h=='forms_other':
        original=copy.deepcopy(w);w['branch']=h
        for t,rows in [(t,[r]) for t,r in enumerate(w['main'],1)]+[(int(t),rows) for t,rows in w['selection'].items()]:
            if 1025<=t<=1536:
                old=prior.forms_at(original,t,True);new=forms_at(w,t,True);q=w['affected']
                for row in rows:
                    d=old[q][row['x'][q]]^new[q][row['x'][q]];row['local'][q]^=d;row['y']^=d
    return w

def run(w,policy,ps):
    acq,c=prior.life.legacy_run(w,ps,True);a=PreservedPrediction(StructuralLearner.restore(c),policy)
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,policy=policy,acquisition=acq,acquisition_checkpoint=json.loads(c),predictions=[],active_predictions=[],prediction_events=[],reviews=[],evaluations=[],inspections=[],controls=[],restore_checks=[],capture=None)
    extra=0
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(a.slow[j]) for j,h in enumerate(a.half_lives) if h!=1024)
        r['predictions'].append(a.observe(t,row));r['active_predictions'].append(a._prediction_event['active']);r['prediction_events'].append(copy.deepcopy(a._prediction_event))
        if str(t) in w['selection']:
            r['reviews'].append(a.review(t,w['selection'][str(t)]))
            if t==384:r['capture']=copy.deepcopy(a.memory['slot'])
            if t in (512,1024):r['controls'].append(a.configure(lock=[w['instruction']['protected']] if t==512 else [],plastic=[2] if t==512 else [],reason='036 supplied downstream boost' if t==512 else '036 supplied release'))
            r['inspections'].append(a.inspect());r['evaluations'].append(evaluate(a,w,t))
        if t in (448,1152):
            saved=a.checkpoint();a=PreservedPrediction.restore(saved);assert a.checkpoint()==saved
            r['restore_checks'].append(dict(tick=t,sha256=hashlib.sha256(saved.encode()).hexdigest()))
    r['checkpoint']=json.loads(a.checkpoint());r['costs']=a.costs.copy();r['memory_events']=a.memory['events'];r['extra_decay_cell_visits']=extra
    r['feedback_labels']=acq['costs']['feedback_labels']+3*(len(w['main'])+sum(map(len,w['selection'].values())))
    r['metrics']=measure(r,w);return r

def hashes():
    parent=ROOT/'results/temporary-plasticity-v1';m=json.loads((parent/'manifest.json').read_text())
    for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    completion=json.loads((parent/'completion.json').read_text())
    for p,d in completion['verification_hashes'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    paths=set(m)|set(completion['verification_hashes'])|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.glob('*') if p.is_file()}|{str(p.relative_to(ROOT)) for p in (ROOT/'results/preserved-prediction-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}

def main():
    assert json.loads((ROOT/'results/temporary-plasticity-v1/audit-serialization-supplement.json').read_text())['status']=='pass'
    fs=sorted((ROOT/'results/preserved-prediction-fixtures').glob('attempt-*.json'));f=json.loads(fs[-1].read_text());assert f['status']=='pass' and len(fs)<=8
    for p,d in f['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/preserved-prediction-v1';out.mkdir(exist_ok=False);m=hashes();(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');start=time.monotonic();rs=[];ws=[]
    def timeout(*_):raise TimeoutError('036 runner 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2500,2505):
            for h in HISTORIES:
                w=generate(seed,h);ws.append(w);(out/'worlds.json').write_text(json.dumps(ws)+'\n')
                for ps in (2500,2501):
                    for policy in POLICIES:
                        r=run(w,policy,ps);rs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(rs)}/180',flush=True)
        assert hashes()==m;total=prior.prior.totals(rs,ws)
        total.update(extra_decay_cell_visits=sum(r['extra_decay_cell_visits'] for r in rs),memory_diagnostic_queries=sum(r['checkpoint']['memory']['diagnostic_queries'] for r in rs),archive_prediction_queries=sum(r['checkpoint']['memory']['archive_prediction_queries'] for r in rs),grid_predictions=2*total['grid_predictions'])
        assert total['generated_labels']==307200 and total['used_labels']==1843200 and total['memory_diagnostic_queries']==299520
        for k,v in dict(candidate_fits=350000,scoring_queries=22000000,raw_bin_visits=110000000,grid_predictions=400000,extra_decay_cell_visits=2949120).items():assert total[k]<=v
        data=dict(status='completed_pending_audit',summary=summarize(rs),totals=total,hashes=m,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(data,indent=2)+'\n');print(data['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),runs=len(rs)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
