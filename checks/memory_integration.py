"""029 exact replay through the optional common runtime; no generated worlds."""
import copy,gzip,hashlib,json,signal,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.continuing import ContinuingLearner
from advaita.structural import StructuralLearner
from advaita.state import canonical
from memory_control_v2 import legacy_run
FILES=['advaita/continuing.py','experiments/memory_integration_plan.md','checks/memory_integration.py','checks/audit_memory_integration.py']

def fixtures(saved,world):
    a=ContinuingLearner(StructuralLearner.restore(canonical(saved['acquisition_checkpoint'])),'combined')
    before=a.checkpoint();view=a.inspect();view['locals'][0]['partition'][0]=99
    assert a.checkpoint()==before
    for tick,row in [(2,world['main'][0]),(1,dict(world['main'][0],y=2))]:
        try:a.observe(tick,row)
        except ValueError:pass
        else:raise AssertionError('Invalid observation accepted')
        assert a.checkpoint()==before
    for t,row in enumerate(world['main'][:64],1):a.observe(t,row)
    a.review(64,world['selection']['64']);before=a.checkpoint()
    try:a.review(64,world['selection']['64'])
    except ValueError:pass
    else:raise AssertionError('Repeated review accepted')
    assert a.checkpoint()==before
    fast=copy.deepcopy(a.engine.fast);slow=copy.deepcopy(a.engine.slow[0])
    event=a.weaken_slow(0,review_tick=64,reason='Fixture: explicit evidence discount')
    assert a.engine.fast==fast and a.engine.slow[0]==[[v/2 for v in cell] for cell in slow]
    assert event['removed_mass']==sum(v[1] for v in slow)/2
    before=a.checkpoint()
    try:a.weaken_slow(0,review_tick=64,reason='Duplicate')
    except ValueError:pass
    else:raise AssertionError('Duplicate intervention accepted')
    assert a.checkpoint()==before
    b=ContinuingLearner.restore(before);assert b.checkpoint()==before
    assert a.observe(65,world['main'][64])==b.observe(65,world['main'][64])
    assert a.checkpoint()==b.checkpoint()
    core=StructuralLearner.restore(canonical(saved['acquisition_checkpoint']))
    ref=ContinuingLearner(core);assert ref.memory=='reference'
    assert ref.learning_checkpoint()==core.checkpoint()
    return dict(status='pass',new_labels=0,contracts=['input_atomicity','inspection_copy','review_reuse','explicit_mass_discount','fast_unchanged','duplicate_control','checkpoint_continuation','reference_default'])

def main():
    folder=ROOT/'results/memory-confirmation-v1';out=ROOT/'results/memory-integration-v1';out.mkdir(exist_ok=False)
    manifest=json.loads((folder/'manifest.json').read_text())
    for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    files=set(manifest)|set(FILES)|{str(p.relative_to(ROOT)) for p in folder.rglob('*') if p.is_file()}
    frozen={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}
    (out/'manifest.json').write_text(json.dumps(frozen,indent=2)+'\n')
    worlds={(w['seed'],w['branch']):w for w in json.loads((folder/'worlds.json').read_text())}
    with gzip.open(folder/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
    first=next(r for r in runs if r['policy']=='combined');fixture=fixtures(first,worlds[first['seed'],first['branch']])
    (out/'fixtures.json').write_text(json.dumps(fixture,indent=2)+'\n')
    records=[];started=time.monotonic()
    def timeout(*_):raise TimeoutError('900 second compatibility ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for i,r in enumerate(runs,1):
            w=worlds[r['seed'],r['branch']]
            initial=legacy_run(w,r['proposal_seed'],True)[1] if r['policy']=='baseline' else canonical(r['acquisition_checkpoint'])
            a=ContinuingLearner(StructuralLearner.restore(initial),'reference' if r['policy']=='baseline' else r['policy'])
            pos=0
            for t,row in enumerate(w['main'],1):
                assert a.observe(t,row)==r['predictions'][t-1],(i,t,'prediction')
                if str(t) in w['selection']:
                    got=a.review(t,w['selection'][str(t)])
                    expected=r['legacy']['reviews'][pos] if r['policy']=='baseline' else r['reviews'][pos]
                    if r['policy']=='baseline':expected={k:expected[k] for k in ('local','upper')}
                    assert got==expected,(i,t,'review');pos+=1
                if r['policy']!='baseline' and t in (256,768):
                    a.engine.fit(2,a.engine.upper['spec'],a.engine.slow[2],'probe')
                    for j in (0,1):a.engine.fit(j,a.engine.locals[j]['partition'],a.engine.slow[j],'probe')
                if t==640:
                    state=a.checkpoint();a=ContinuingLearner.restore(state);assert a.checkpoint()==state
            digest=hashlib.sha256(a.learning_checkpoint().encode()).hexdigest()
            assert digest==r['checkpoint_sha256'],(i,'checkpoint')
            records.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],branch=r['branch'],policy=r['policy'],checkpoint_sha256=digest,
                predictions=len(r['predictions']),reviews=pos,feedback_labels=r['costs']['feedback_labels']))
            if i%25==0:print(f'{i}/350 exact common-runtime replays',flush=True)
        for p,d in frozen.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        result=dict(status='pass',runs=len(records),new_labels=0,replayed_labels=sum(x['feedback_labels'] for x in records),
            records=records,elapsed_seconds=time.monotonic()-started)
        (out/'compatibility.json').write_text(json.dumps(result,indent=2)+'\n')
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed=len(records)))+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
