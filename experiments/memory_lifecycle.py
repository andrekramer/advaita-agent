"""030 continuing memory stress test; frozen policies and common runtime."""
import copy,gzip,hashlib,itertools,json,math,random,signal,sys,time,types
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.continuing import ContinuingLearner
from advaita.state import canonical
import memory_control_v2 as old
from memory_lifecycle_metrics import metrics,summarize
BRANCHES=('repeated','forms','rare');POLICIES=('baseline','fast','relaxed','combined')
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))
FILES=['experiments/memory_lifecycle.py','experiments/memory_lifecycle_metrics.py','experiments/memory_lifecycle_protocol.md','checks/audit_memory_lifecycle.py','checks/test_memory_lifecycle.py']

def forms_at(w,t,observed=False):
    f=copy.deepcopy(w['forms']);phase=max(0,t-1)//w['phase_length'];j=w['affected']
    if w['branch']=='forms' and phase%2:f[j]=w['alternative'].copy()
    if observed and w['branch']=='repeated' and phase%2:f[j]=[1-x for x in f[j]]
    return f

def target(w,x,a,t):
    f=forms_at(w,t,True);return f[0][x[0]]^f[1][x[1]]^a

def generate(seed,branch,small=False):
    layout=random.Random(201000+seed);orders=[];forms=[];reps=[]
    for _ in range(2):
        order=list(range(4));layout.shuffle(order);orders.append(order)
        forms.append([int(order.index(x)>=2) for x in range(4)]);reps.append([order[0],order[2]])
    affected=layout.randrange(2);alt=orders[affected].copy();alt[1],alt[2]=alt[2],alt[1]
    w=dict(seed=seed,branch=branch,forms=forms,representatives=reps,affected=affected,
        alternative=[int(alt.index(x)>=2) for x in range(4)],small=small,phase_length=8 if small else 512,period=4 if small else 64)
    inputs=random.Random(202000+seed);noise=[random.Random(b+seed) for b in (203000,204000,205000)]
    def draws(n,contexts):
        contexts=list(contexts);out=[]
        while len(out)<n:
            block=contexts.copy();inputs.shuffle(block);out.extend(block[:n-len(out)])
        return out
    def local(n,j):return [dict(x=x,y=forms[j][x]^int(noise[j].random()<.1)) for x in draws(n,range(4))]
    n,ns,nc,nr=(4,4,16,1) if small else (256,32,256,4)
    w['local_main']=[local(n,j) for j in (0,1)]
    w['local_selection']=[[local(ns,j) for j in (0,1)] for _ in range(nr)]
    w['composition']=[dict(x=[l,r],a=a,y=target(w,[l,r],a,0)^int(noise[2].random()<.1)) for l,r,a in draws(nc,itertools.product(*reps,(0,1)))]
    def contexts(t):
        if branch=='rare' and w['phase_length']<t<=3*w['phase_length']:
            common=[c for c in CONTEXTS if not forms[affected][c[affected]]];rare=[c for c in CONTEXTS if forms[affected][c[affected]]]
            block=draws(30,common)+draws(2,rare);inputs.shuffle(block);return block
        return draws(32,CONTEXTS)
    def row(t,c):
        l,r,a=c;f=forms_at(w,t,True)
        return dict(x=[l,r],a=a,local=[f[j][x]^int(noise[j].random()<.1) for j,x in enumerate((l,r))],y=target(w,[l,r],a,t)^int(noise[2].random()<.1))
    w['main']=[];block=[]
    for t in range(1,4*w['phase_length']+1):
        if (t-1)%w['phase_length']==0:block=[]
        if not block:block=contexts(t)
        w['main'].append(row(t,block.pop(0)))
    w['selection']={str(t):[row(t,c) for c in contexts(t)[:ns]] for t in range(w['period'],len(w['main'])+1,w['period'])}
    return w

oracle=types.FunctionType(old.oracle.__code__,dict(old.oracle.__globals__,target=target))
evaluate=types.FunctionType(old.evaluate.__code__,dict(old.evaluate.__globals__,target=target,forms_at=forms_at,oracle=oracle),argdefs=old.evaluate.__defaults__)
legacy_run=types.FunctionType(old.legacy_run.__code__,dict(old.legacy_run.__globals__,evaluate=evaluate),argdefs=old.legacy_run.__defaults__)

class Bridge:
    def __init__(self,core,policy):self.runtime=ContinuingLearner(core,policy)
    def observe(self,t,row):return self.runtime.observe(t,row)
    def review(self,t,rows):return self.runtime.review(t,rows)
    def checkpoint(self):return self.runtime.learning_checkpoint()
    def __getattr__(self,name):return getattr(self.runtime.engine,name)

def run(w,policy,ps,measure=True):
    capture=[]
    def factory(core,p):
        b=Bridge(core,p);capture.append(b);return b
    fn=types.FunctionType(old.run.__code__,dict(old.run.__globals__,MemoryLearner=factory,legacy_run=legacy_run,evaluate=evaluate,target=target,forms_at=forms_at,metrics=metrics),argdefs=old.run.__defaults__)
    r,c=fn(w,policy,ps,measure)
    if capture:r['runtime_checkpoint']=json.loads(capture[0].runtime.checkpoint())
    return r,c

def hashes():
    folder=ROOT/'results/memory-integration-v1';parent=json.loads((folder/'manifest.json').read_text())
    for p,d in parent.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    paths=set(parent)|set(FILES)|{str(p.relative_to(ROOT)) for p in folder.glob('*') if p.is_file()}
    paths|={str(p.relative_to(ROOT)) for p in (ROOT/'results/memory-lifecycle-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(paths)}

def main():
    assert json.loads((ROOT/'results/memory-integration-v1/audit.json').read_text())['status']=='pass'
    fixtures=[json.loads(p.read_text()) for p in sorted((ROOT/'results/memory-lifecycle-fixtures').glob('attempt-*.json'))]
    assert fixtures[-1]['status']=='pass' and sum(f['charged_labels'] for f in fixtures)<=2000
    for p,d in fixtures[-1]['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/memory-lifecycle-v1';out.mkdir(exist_ok=False);(out/'checkpoints').mkdir()
    frozen=hashes();(out/'manifest.json').write_text(json.dumps(frozen,indent=2)+'\n');started=time.monotonic();runs=[];worlds=[]
    def timeout(*_):raise TimeoutError('900 second lifecycle ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(1900,1905):
            for branch in BRANCHES:
                w=generate(seed,branch);worlds.append(w);(out/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (1900,1901):
                    for p in POLICIES:
                        r,c=run(w,p,ps);path=f'checkpoints/{seed}-{branch}-{ps}-{p}.json.gz'
                        with gzip.open(out/path,'wt') as f:f.write(c)
                        r['checkpoint_file']=path;runs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/120',flush=True)
        assert hashes()==frozen;total=old.totals(runs,worlds)
        for k,v in dict(candidate_fits=200000,scoring_queries=15000000,raw_bin_visits=60000000,oracle_context_queries=800000).items():assert total[k]<=v
        assert total['used_labels']==1228800 and total['generated_labels']==153600
        result=dict(status='completed_pending_audit',summary=summarize(runs),totals=total,hashes=frozen,elapsed_seconds=time.monotonic()-started)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed=len(runs)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
