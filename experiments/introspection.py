"""032 counterfactual experiment; policy receives only a copied inspection packet."""
import copy,gzip,hashlib,itertools,json,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.continuing import ContinuingLearner
from advaita.structural import StructuralLearner
from advaita.state import canonical
import memory_lifecycle as life
from introspection_controller import packet,decide
from introspection_metrics import measure,summarize
FILES=['experiments/introspection.py','experiments/introspection_controller.py','experiments/introspection_metrics.py','experiments/introspection_protocol.md','checks/test_introspection.py','checks/audit_introspection.py']
HISTORIES=('stable','repeated','forms')
REASON='032 diagnostic counterfactual: one slow-evidence weakening'
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))

def grid(a):return [a.engine.predictions([x,y],action) for x,y,action in CONTEXTS]

def run(w,ps,measured=True):
    acq,c=life.legacy_run(w,ps,True);a=ContinuingLearner(StructuralLearner.restore(c),'combined')
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,acquisition=acq,acquisition_checkpoint=json.loads(c),prefix_predictions=[],prefix_reviews=[])
    cutoff=16 if w['small'] else 1024
    for t,row in enumerate(w['main'][:cutoff],1):
        r['prefix_predictions'].append(a.observe(t,row))
        if str(t) in w['selection']:
            review=a.review(t,w['selection'][str(t)]);r['prefix_reviews'].append(review)
            view=packet(a);decision=decide(json.loads(canonical(view)))
            if decision['eligible'] or t==cutoff:break
    r.update(tick=t,packet=view,decision=decision,checkpoint=json.loads(a.checkpoint()),branches={})
    # Commit the decision into the record before any branch executes.
    r['decision_sha256']=hashlib.sha256(canonical(dict(packet=view,decision=decision)).encode()).hexdigest()
    checkpoint=a.checkpoint()
    for j in (None,0,1,2):
        b=ContinuingLearner.restore(checkpoint);event=None
        if j is not None:event=b.weaken_slow(j,review_tick=t,reason=REASON)
        trace=dict(control=event,immediate=grid(b),predictions=[],reviews=[])
        for u,row in enumerate(w['main'][t:],t+1):
            trace['predictions'].append(b.observe(u,row))
            if str(u) in w['selection']:trace['reviews'].append(b.review(u,w['selection'][str(u)]))
        trace.update(evaluation=life.evaluate(b.engine.locals,b.engine.upper,w,len(w['main'])),checkpoint=json.loads(b.checkpoint()))
        r['branches']['none' if j is None else str(j)]=trace
    if measured:r['metrics']=measure(r,w)
    return r

def totals(records,worlds):
    generated=sum(sum(map(len,w['local_main']))+sum(len(a) for batch in w['local_selection'] for a in batch)+len(w['composition'])+3*len(w['main'])+3*sum(map(len,w['selection'].values())) for w in worlds)
    used=0;fits=queries=visits=preds=oracle=0
    for r in records:
        p=r['checkpoint']['engine']['costs'];c=r['acquisition']['costs']
        used+=c['feedback_labels']+3*len(r['prefix_predictions'])+sum(3*len(w['selection'][str(review['index'])]) for review in r['prefix_reviews'] for w in worlds if w['seed']==r['seed'] and w['branch']==r['history'])
        fits+=c['candidate_fits']+p['candidate_fits'];queries+=c['scoring_queries']+p['scoring_queries'];visits+=p['raw_bin_visits'];preds+=3*len(r['prefix_predictions'])
        ev=r['acquisition']['transfer'];oracle+=32*(1+len(ev['removal_costs'])+len(ev['raw_addition_gains']))
        for b in r['branches'].values():
            q=b['checkpoint']['engine']['costs'];fits+=q['candidate_fits']-p['candidate_fits'];queries+=q['scoring_queries']-p['scoring_queries'];visits+=q['raw_bin_visits']-p['raw_bin_visits'];preds+=3*len(b['predictions'])
            used+=3*len(b['predictions'])+sum(3*len(w['selection'][str(review['index'])]) for review in b['reviews'] for w in worlds if w['seed']==r['seed'] and w['branch']==r['history'])
            ev=b['evaluation'];oracle+=32*(1+len(ev['removal_costs'])+len(ev['raw_addition_gains']))
    return dict(trunks=len(records),continuations=4*len(records),generated_labels=generated,used_labels=used,candidate_fits=fits,scoring_queries=queries,raw_bin_visits=visits,main_predictions=preds,immediate_predictions=384*len(records),final_grid_predictions=128*len(records),auxiliary_predictions=24*len(records),oracle_context_queries=oracle)

def hashes():
    parent=ROOT/'results/memory-steering-v1';m=json.loads((parent/'manifest.json').read_text())
    for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    files=set(m)|set(FILES)|{str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file()}|{str(p.relative_to(ROOT)) for p in (ROOT/'results/introspection-fixtures').glob('*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}

def main():
    assert json.loads((ROOT/'results/memory-steering-v1/audit.json').read_text())['status']=='pass'
    fs=sorted((ROOT/'results/introspection-fixtures').glob('attempt-*.json'));f=json.loads(fs[-1].read_text());assert len(fs)<=8 and f['status']=='pass'
    for p,d in f['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/introspection-v1';out.mkdir(exist_ok=False);m=hashes();(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    start=time.monotonic();records=[];worlds=[]
    def timeout(*_):raise TimeoutError('032 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(2100,2105):
            for h in HISTORIES:
                w=life.generate(seed,h);worlds.append(w);(out/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (2100,2101):
                    r=run(w,ps);records.append(r)
                    with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {h}: {len(records)}/30 trunks',flush=True)
        assert hashes()==m;total=totals(records,worlds)
        assert total['generated_labels']==153600
        for k,v in dict(used_labels=1228800,candidate_fits=200000,scoring_queries=15000000,raw_bin_visits=60000000,oracle_context_queries=50000).items():assert total[k]<=v,(k,total[k])
        result=dict(status='completed_pending_audit',summary=summarize(records),totals=total,elapsed_seconds=time.monotonic()-start,hashes=m)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(result['summary']['gates'])
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),trunks=len(records)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
