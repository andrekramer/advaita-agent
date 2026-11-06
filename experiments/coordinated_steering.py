"""034 fixed2x2 local/downstream plasticity comparison plus unsteered control."""
import gzip,hashlib,json,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.coordinated_steering import CoordinatedMemory
from advaita.structural import StructuralLearner
from advaita.state import canonical
import selective_steering as prior
from selective_steering_metrics import measure
from coordinated_steering_metrics import summarize
HISTORIES=('stable','forms','repeated');POLICIES=('U','P','L','D','C')
FILES=['advaita/coordinated_steering.py','experiments/coordinated_steering.py','experiments/coordinated_steering_metrics.py','experiments/coordinated_steering_protocol.md','checks/audit_coordinated_steering.py','checks/test_coordinated_steering.py']
REASON='034 supplied instruction: protected local form with factorial plasticity'
RELEASE='034 release: restore ordinary learning in all channels'

def run(w,policy,ps,measured=True):
    acq,c=prior.life.legacy_run(w,ps,True);a=CoordinatedMemory(StructuralLearner.restore(c))
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,policy=policy,acquisition=acq,acquisition_checkpoint=json.loads(c),predictions=[],reviews=[],evaluations=[],controls=[],inspections=[],restore_check=None)
    n=w['phase_length'];p=w['instruction']['protected'];q=1-p
    for t,row in enumerate(w['main'],1):
        r['predictions'].append(a.observe(t,row))
        if str(t) in w['selection']:
            r['reviews'].append(a.review(t,w['selection'][str(t)]))
            if policy!='U' and t in (n,2*n):
                lock=[p] if t==n else [];plastic=[]
                if t==n:
                    if policy in ('L','C'):plastic.append(q)
                    if policy in ('D','C'):plastic.append(2)
                r['controls'].append(a.configure(lock=lock,plastic=plastic,reason=REASON if t==n else RELEASE))
            r['inspections'].append(a.inspect());r['evaluations'].append(prior.evaluate(a,w,t))
        if t==3*n//2:
            saved=a.checkpoint();a=CoordinatedMemory.restore(saved);assert saved==a.checkpoint();r['restore_check']=dict(tick=t,sha256=hashlib.sha256(saved.encode()).hexdigest())
    r['checkpoint']=json.loads(a.checkpoint());r['costs']=a.costs.copy();r['feedback_labels']=acq['costs']['feedback_labels']+3*(len(w['main'])+sum(map(len,w['selection'].values())))
    r['extra_decay_cell_visits']=n*((4 if policy in ('L','C') else 0)+(32 if policy in ('D','C') else 0))
    if measured:r['metrics']=measure(r,w)
    return r

def hashes():
    parent=ROOT/'results/selective-steering-v1';m=json.loads((parent/'manifest.json').read_text())
    for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    files=set(m)|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()}|{str(p.relative_to(ROOT)) for p in (ROOT/'results/coordinated-steering-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}

def main():
    assert json.loads((ROOT/'results/selective-steering-v1/audit.json').read_text())['status']=='pass'
    fs=sorted((ROOT/'results/coordinated-steering-fixtures').glob('attempt-*.json'));f=json.loads(fs[-1].read_text());assert len(fs)<=8 and f['status']=='pass'
    for p,d in f['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/coordinated-steering-v1';out.mkdir(exist_ok=False);m=hashes();(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');start=time.monotonic();rs=[];ws=[]
    def timeout(*_):raise TimeoutError('034 runner900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2300,2305):
            for h in HISTORIES:
                w=prior.generate(seed,h);ws.append(w);(out/'worlds.json').write_text(json.dumps(ws)+'\n')
                for ps in (2300,2301):
                    for policy in POLICIES:
                        r=run(w,policy,ps);rs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(rs)}/150',flush=True)
        assert hashes()==m;total=prior.totals(rs,ws);total['extra_decay_cell_visits']=sum(r['extra_decay_cell_visits'] for r in rs)
        assert total['generated_labels']==153600 and total['used_labels']==1536000 and total['extra_decay_cell_visits']==1105920
        for k,v in dict(candidate_fits=250000,scoring_queries=18000000,raw_bin_visits=90000000,grid_predictions=200000).items():assert total[k]<=v
        data=dict(status='completed_pending_audit',summary=summarize(rs),totals=total,hashes=m,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(data,indent=2)+'\n');print(data['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),runs=len(rs)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
