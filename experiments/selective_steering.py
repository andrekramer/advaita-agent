"""033 predeclared selective locking/plasticity study."""
import copy,gzip,hashlib,itertools,json,math,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.memory_revision import RevisionLearner
from advaita.selective_steering import SteerableMemory
from advaita.structural import StructuralLearner
from advaita.state import canonical
import memory_lifecycle as life
from selective_steering_metrics import measure,summarize
HISTORIES=('stable','forms','repeated')
POLICIES=('legacy','refreshed','lock_only','plastic_only','selective','swapped')
FILES=['advaita/selective_steering.py','experiments/selective_steering.py','experiments/selective_steering_metrics.py','experiments/selective_steering_protocol.md','checks/audit_selective_steering.py','checks/test_selective_steering.py']
REASON='Supplied task instruction: protect one form and adapt the other'
RELEASE='Scheduled release: restore ordinary structural and memory learning'

def delta(w):
    p=1-w['affected'];f=w['forms'][p];mask=[0,1,0,1]
    if len({a^b for a,b in zip(f,mask)})==1:mask=[0,0,1,1]
    return mask

def generate(seed,h,small=False):
    w=life.generate(seed,h,small);p=1-w['affected'];n=w['phase_length'];mask=delta(w)
    w['instruction']=dict(protected=p,flexible=1-p)
    if h!='stable':
        for t,row in enumerate(w['main'],1):
            if n<t<=n+n//4:
                d=mask[row['x'][p]];row['local'][p]^=d;row['y']^=d
        for tick,rows in w['selection'].items():
            if n<int(tick)<=n+n//4:
                for row in rows:
                    d=mask[row['x'][p]];row['local'][p]^=d;row['y']^=d
    return w

def evaluate(a,w,t):
    ps=[a.predictions([x,y],action) for x,y,action in life.CONTEXTS]
    forms=life.forms_at(w,t,True)
    exact=[all((a.locals[j]['partition'][x]==a.locals[j]['partition'][y])==(forms[j][x]==forms[j][y]) for x in range(4) for y in range(4)) for j in range(2)]
    expected=[];correct=0
    for pred,(x,y,action) in zip(ps,life.CONTEXTS):
        truth=life.target(w,[x,y],action,t);p=pred[2];expected.append(-.9*math.log(p if truth else 1-p)-.1*math.log(1-p if truth else p));correct+=int((p>=.5)==bool(truth))
    regret=sum(expected)/32-(-.9*math.log(.9)-.1*math.log(.1))
    return dict(tick=t,predictions=ps,partitions=[m['partition'].copy() for m in a.locals],spec=a.upper['spec'].copy(),local_exact=exact,accuracy=correct/32,regret=regret,valid=all(exact) and correct==32 and regret<=.10)

def run(w,policy,ps,measured=True):
    acq,c=life.legacy_run(w,ps,True);core=StructuralLearner.restore(c)
    a=RevisionLearner(core,'combined') if policy=='legacy' else SteerableMemory(core)
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,policy=policy,acquisition=acq,acquisition_checkpoint=json.loads(c),predictions=[],reviews=[],evaluations=[],controls=[],inspections=[],restore_check=None)
    n=w['phase_length'];p=w['instruction']['protected'];q=1-p
    for t,row in enumerate(w['main'],1):
        r['predictions'].append(a.observe(t,row))
        if str(t) in w['selection']:
            r['reviews'].append(a.review(t,w['selection'][str(t)]))
            if policy not in ('legacy','refreshed') and t in (n,2*n):
                lock=([p] if policy in ('lock_only','selective') else [q] if policy=='swapped' else []) if t==n else []
                plastic=([q] if policy in ('plastic_only','selective') else [p] if policy=='swapped' else []) if t==n else []
                r['controls'].append(a.configure(lock=lock,plastic=plastic,reason=REASON if t==n else RELEASE))
            if policy!='legacy':r['inspections'].append(a.inspect())
            r['evaluations'].append(evaluate(a,w,t))
        if t==3*n//2:
            saved=a.checkpoint();a=(RevisionLearner if policy=='legacy' else SteerableMemory).restore(saved)
            assert a.checkpoint()==saved;r['restore_check']=dict(tick=t,sha256=hashlib.sha256(saved.encode()).hexdigest())
    r['checkpoint']=json.loads(a.checkpoint());r['costs']=a.costs.copy()
    r['feedback_labels']=acq['costs']['feedback_labels']+3*(len(w['main'])+sum(map(len,w['selection'].values())))
    if measured:r['metrics']=measure(r,w)
    return r

def totals(rs,ws):
    return dict(runs=len(rs),generated_labels=sum(sum(map(len,w['local_main']))+sum(len(xs) for batch in w['local_selection'] for xs in batch)+len(w['composition'])+3*(len(w['main'])+sum(map(len,w['selection'].values()))) for w in ws),used_labels=sum(r['feedback_labels'] for r in rs),candidate_fits=sum(r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'] for r in rs),scoring_queries=sum(r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'] for r in rs),raw_bin_visits=sum(r['costs']['raw_bin_visits'] for r in rs),main_predictions=sum(3*len(r['predictions']) for r in rs),grid_predictions=sum(32*len(r['evaluations']) for r in rs))

def hashes():
    parent=ROOT/'results/introspection-v1';m=json.loads((parent/'manifest.json').read_text())
    for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    files=set(m)|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()}|{str(p.relative_to(ROOT)) for p in (ROOT/'results/selective-steering-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}

def main():
    assert json.loads((ROOT/'results/introspection-v1/audit.json').read_text())['status']=='pass'
    fixtures=sorted((ROOT/'results/selective-steering-fixtures').glob('attempt-*.json'));f=json.loads(fixtures[-1].read_text());assert f['status']=='pass' and len(fixtures)<=8
    for p,d in f['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/selective-steering-v1';out.mkdir(exist_ok=False);m=hashes();(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');start=time.monotonic();rs=[];ws=[]
    def timeout(*_):raise TimeoutError('033 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2200,2205):
            for h in HISTORIES:
                w=generate(seed,h);ws.append(w);(out/'worlds.json').write_text(json.dumps(ws)+'\n')
                for ps in (2200,2201):
                    for policy in POLICIES:
                        r=run(w,policy,ps);rs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(rs)}/180',flush=True)
        assert hashes()==m;total=totals(rs,ws);assert total['generated_labels']==153600 and total['used_labels']==1843200
        for k,v in dict(candidate_fits=300000,scoring_queries=20000000,raw_bin_visits=100000000,grid_predictions=250000).items():assert total[k]<=v
        result=dict(status='completed_pending_audit',summary=summarize(rs),totals=total,hashes=m,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),runs=len(rs)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
