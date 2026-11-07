"""035 temporary downstream plasticity; freeze before fresh outcomes."""
import copy,gzip,hashlib,json,signal,sys,time,types
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.temporary_plasticity import TemporaryPlasticity
from advaita.coordinated_steering import CoordinatedMemory
from advaita.structural import StructuralLearner
from advaita.state import canonical
import selective_steering as prior
import memory_lifecycle as life
from temporary_plasticity_metrics import measure,summarize
HISTORIES=('stable','forms','repeated','forms_persistent','repeated_persistent')
POLICIES=('P','D128','D256','D512','G')
FILES=['advaita/temporary_plasticity.py','experiments/temporary_plasticity.py','experiments/temporary_plasticity_metrics.py','experiments/temporary_plasticity_protocol.md','checks/test_temporary_plasticity.py','checks/audit_temporary_plasticity.py','experiments/diagnose_downstream_retention.py']

def forms_at(w,t,observed=False):
    v=dict(w,branch=w['branch'].removesuffix('_persistent'))
    if w['branch'].endswith('_persistent') and t>w['phase_length']:t=w['phase_length']+1
    return life.forms_at(v,t,observed)

def target(w,x,a,t):
    f=forms_at(w,t,True);return f[0][x[0]]^f[1][x[1]]^a

# Reuse evaluation arithmetic without altering the frozen module's globals.
eval_life=types.SimpleNamespace(CONTEXTS=life.CONTEXTS,forms_at=forms_at,target=target)
evaluate=types.FunctionType(prior.evaluate.__code__,dict(prior.evaluate.__globals__,life=eval_life))

def generate(seed,h):
    base=h.removesuffix('_persistent');w=prior.generate(seed,base)
    if h!=base:
        previous=copy.deepcopy(w);w['branch']=h
        batches=[(t,[row]) for t,row in enumerate(w['main'],1)]+[(int(t),rows) for t,rows in w['selection'].items()]
        for t,rows in batches:
            old=life.forms_at(previous,t,True);new=forms_at(w,t,True)
            for row in rows:
                for j in (0,1):row['local'][j]^=old[j][row['x'][j]]^new[j][row['x'][j]]
                row['y']^=life.target(previous,row['x'],row['a'],t)^target(w,row['x'],row['a'],t)
    return w

def run(w,policy,ps,measured=True):
    # Acquisition is before all changes, with identical original mappings.
    acq,c=life.legacy_run(w,ps,True)
    a=CoordinatedMemory(StructuralLearner.restore(c));controller=TemporaryPlasticity(a,policy,w['instruction']['protected'])
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,policy=policy,acquisition=acq,acquisition_checkpoint=json.loads(c),predictions=[],reviews=[],evaluations=[],controls=[],inspections=[],diagnostics=[],restore_checks=[])
    extra=0
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(a.slow[j]) for j,h in enumerate(a.half_lives) if h!=1024)
        r['predictions'].append(a.observe(t,row))
        if str(t) in w['selection']:
            review,control,diagnostic=controller.review(t,w['selection'][str(t)])
            r['reviews'].append(review)
            if control:r['controls'].append(control)
            if diagnostic:r['diagnostics'].append(diagnostic)
            r['inspections'].append(a.inspect());r['evaluations'].append(evaluate(a,w,t))
        if t in (576,768):
            saved=controller.checkpoint();controller=TemporaryPlasticity.restore(saved);a=controller.learner
            assert saved==controller.checkpoint();r['restore_checks'].append(dict(tick=t,sha256=hashlib.sha256(saved.encode()).hexdigest()))
    r['checkpoint']=json.loads(controller.checkpoint());r['costs']=a.costs.copy()
    r['feedback_labels']=acq['costs']['feedback_labels']+3*(len(w['main'])+sum(map(len,w['selection'].values())))
    r['extra_decay_cell_visits']=extra;r['controller_queries']=sum(len(d['predictions']) for d in r['diagnostics'])
    if measured:r['metrics']=measure(r,w)
    return r

def hashes():
    parent=ROOT/'results/coordinated-steering-v1';m=json.loads((parent/'manifest.json').read_text())
    for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    paths=set(m)|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()}
    for directory in ('temporary-plasticity-fixtures','downstream-retention-diagnosis'):
        paths|={str(p.relative_to(ROOT)) for p in (ROOT/'results'/directory).glob('*') if p.is_file()}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}

def main():
    assert json.loads((ROOT/'results/coordinated-steering-v1/audit.json').read_text())['status']=='pass'
    fs=sorted((ROOT/'results/temporary-plasticity-fixtures').glob('attempt-*.json'));f=json.loads(fs[-1].read_text());assert len(fs)<=8 and f['status']=='pass'
    for p,d in f['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/temporary-plasticity-v1';out.mkdir(exist_ok=False);m=hashes();(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');start=time.monotonic();rs=[];ws=[]
    def timeout(*_):raise TimeoutError('035 runner 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2400,2405):
            for h in HISTORIES:
                w=generate(seed,h);ws.append(w);(out/'worlds.json').write_text(json.dumps(ws)+'\n')
                for ps in (2400,2401):
                    for policy in POLICIES:
                        r=run(w,policy,ps);rs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(rs)}/250',flush=True)
        assert hashes()==m;total=prior.totals(rs,ws)
        for k in ('extra_decay_cell_visits','controller_queries'):total[k]=sum(r[k] for r in rs)
        assert total['generated_labels']==256000 and total['used_labels']==2560000 and total['controller_queries']==64000
        for k,v in dict(candidate_fits=400000,scoring_queries=25000000,raw_bin_visits=130000000,grid_predictions=300000).items():assert total[k]<=v
        data=dict(status='completed_pending_audit',summary=summarize(rs),totals=total,hashes=m,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(data,indent=2)+'\n');print(data['summary']['primary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),runs=len(rs)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
