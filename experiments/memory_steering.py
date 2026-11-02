"""031 bounded external steering using observed review diagnostics only."""
import gzip,hashlib,json,signal,sys,time
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.continuing import ContinuingLearner
from advaita.structural import StructuralLearner
from advaita.state import canonical
import memory_lifecycle as life
from memory_steering_metrics import metrics,summarize
BRANCHES=('stable','repeated');POLICIES=('unsteered','targeted','rotated')
FILES=['experiments/memory_steering.py','experiments/memory_steering_metrics.py','experiments/memory_steering_protocol.md','checks/audit_memory_steering.py','checks/test_memory_steering.py']
REASON='Scripted review diagnostic: weaken selected slow evidence once'

def choose(review):
    candidates=[e for e in review['weakenings'] if e['qualifies'] and not e['accepted']]
    return max(candidates,key=lambda e:(e['losses'][0]-e['losses'][1],-e['channel']))['channel'] if candidates else None

def run(w,policy,ps,measure=True):
    acq,c=life.legacy_run(w,ps,True);a=ContinuingLearner(StructuralLearner.restore(c),'combined')
    r=dict(seed=w['seed'],branch=w['branch'],policy=policy,proposal_seed=ps,acquisition=acq,acquisition_checkpoint=json.loads(c),
        transfer=life.evaluate(a.engine.locals,a.engine.upper,w,0,True),predictions=[],evaluations=[],reviews=[],trigger=None,control=None)
    for t,row in enumerate(w['main'],1):
        r['predictions'].append(a.observe(t,row))
        if str(t) in w['selection']:
            review=a.review(t,w['selection'][str(t)]);r['reviews'].append(review)
            if r['trigger'] is None and t<=1024:
                selected=choose(review)
                if selected is not None:
                    r['trigger']=dict(tick=t,channel=selected)
                    if policy!='unsteered':r['control']=a.weaken_slow(selected if policy=='targeted' else (selected+1)%3,review_tick=t,reason=REASON)
        if t%w['period']==0:r['evaluations'].append(life.evaluate(a.engine.locals,a.engine.upper,w,t))
    c=a.learning_checkpoint();r['runtime_checkpoint']=json.loads(a.checkpoint());r['checkpoint_sha256']=hashlib.sha256(c.encode()).hexdigest()
    r['costs']=a.engine.costs.copy();r['costs']['feedback_labels']=acq['costs']['feedback_labels']+3*len(w['main'])+3*sum(map(len,w['selection'].values()))
    if measure:r['metrics']=metrics(r,w)
    return r,c

def totals(runs,worlds):
    return dict(runs=len(runs),generated_labels=sum(sum(map(len,w['local_main']))+sum(len(x) for b in w['local_selection'] for x in b)+len(w['composition'])+3*len(w['main'])+3*sum(map(len,w['selection'].values())) for w in worlds),
        used_labels=sum(r['costs']['feedback_labels'] for r in runs),candidate_fits=sum(r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'] for r in runs),
        scoring_queries=sum(r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'] for r in runs),raw_bin_visits=sum(r['costs']['raw_bin_visits'] for r in runs),
        main_predictions=sum(3*len(r['predictions']) for r in runs),evaluation_predictions=sum(e['contexts'] for r in runs for e in [r['transfer']]+r['evaluations']),
        auxiliary_predictions=24*len(runs),oracle_context_queries=sum(32*(1+len(e['removal_costs'])+len(e['raw_addition_gains'])) for r in runs for e in [r['transfer'],r['acquisition']['transfer']]+r['evaluations']))

def hashes():
    parent=ROOT/'results/memory-lifecycle-v1';manifest=json.loads((parent/'manifest.json').read_text())
    for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    files=set(manifest)|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()}|{str(p.relative_to(ROOT)) for p in (ROOT/'results/memory-steering-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}

def main():
    assert json.loads((ROOT/'results/memory-lifecycle-v1/audit.json').read_text())['status']=='pass'
    fs=[json.loads(p.read_text()) for p in sorted((ROOT/'results/memory-steering-fixtures').glob('attempt-*.json'))];assert fs[-1]['status']=='pass' and sum(f['charged_labels'] for f in fs)<=1000
    for p,d in fs[-1]['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/memory-steering-v1';out.mkdir(exist_ok=False);(out/'checkpoints').mkdir();frozen=hashes()
    (out/'manifest.json').write_text(json.dumps(frozen,indent=2)+'\n');started=time.monotonic();runs=[];worlds=[]
    def timeout(*_):raise TimeoutError('900 second steering ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2000,2005):
            for h in BRANCHES:
                w=life.generate(seed,h);worlds.append(w);(out/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (2000,2001):
                    for p in POLICIES:
                        r,c=run(w,p,ps);path=f'checkpoints/{seed}-{h}-{ps}-{p}.json.gz'
                        with gzip.open(out/path,'wt') as f:f.write(c)
                        r['checkpoint_file']=path;runs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(runs)}/60',flush=True)
        assert hashes()==frozen;total=totals(runs,worlds)
        assert total['generated_labels']==102400 and total['used_labels']==614400
        for k,v in dict(candidate_fits=150000,scoring_queries=10000000,raw_bin_visits=40000000,oracle_context_queries=330000).items():assert total[k]<=v
        result=dict(status='completed_pending_audit',summary=summarize(runs),totals=total,hashes=frozen,elapsed_seconds=time.monotonic()-started)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed=len(runs)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
