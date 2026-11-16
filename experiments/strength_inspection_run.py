"""Frozen strength-information study; writes once and never tunes on outcomes."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.controlled import ControlledLearner
from advaita.structural import StructuralLearner
from advaita.state import canonical
import selective_steering as worlds
from strength_inspection import ACTIONS,CONTEXTS,VIEWS,packet,describe,probe,decisions
from strength_inspection_metrics import measure,summarize

OUT=ROOT/'results/strength-inspection-v1'
SOURCES=['experiments/strength_inspection_protocol.md','experiments/strength_inspection.py',
         'experiments/strength_inspection_run.py','experiments/strength_inspection_metrics.py',
         'experiments/report_strength_inspection.py','checks/test_strength_inspection.py',
         'checks/audit_strength_inspection.py']
REASON='Strength inspection: bounded selected-channel plasticity'
RELEASE='Strength inspection: scheduled release'


def sha(value):return hashlib.sha256(canonical(value).encode()).hexdigest()


def command(a,action,release=False):
    return a.configure(lock=[],plastic=[] if release or action=='none' else [int(action)],
                       reason=RELEASE if release else REASON,source='frozen scripted experiment')


def run_probes(checkpoint,full):
    result=[];views={m:describe(full,m) for m in (*VIEWS,'prediction_only')}
    base=ControlledLearner.restore(checkpoint)
    for action in ACTIONS:
        b=ControlledLearner.restore(checkpoint);command(b,action)
        start=b.checkpoint()
        for l,r,a in CONTEXTS:
            labels=[int(p<.5) for p in base.predict([l,r],a)['active']]
            row=dict(x=[l,r],a=a,local=labels[:2],y=labels[2])
            c=ControlledLearner.restore(start)
            actual=dict(before=c.observe(c.tick+1,row),after=c.predict([l,r],a)['active'])
            forecasts={m:probe(v,action,[l,r],a,labels) for m,v in views.items()}
            result.append(dict(action=action,row=row,actual=actual,forecasts=forecasts))
    return result


def run(w,ps):
    acquisition,core=worlds.life.legacy_run(w,ps,True)
    a=ControlledLearner(StructuralLearner.restore(core),recall_policy='shadow')
    r=dict(seed=w['seed'],history=w['branch'],proposal_seed=ps,acquisition=acquisition,
           acquisition_checkpoint=json.loads(core),prefix_predictions=[],prefix_reviews=[],branches={})
    for t,row in enumerate(w['main'][:640],1):
        r['prefix_predictions'].append(a.observe(t,row))
        if str(t) in w['selection']:r['prefix_reviews'].append(a.review(t,w['selection'][str(t)]))
    checkpoint=a.checkpoint();r['checkpoint']=json.loads(checkpoint)
    target=w['affected'] if ps==3100 else 2
    r['packet']=packet(a,w['main'][576:640],target,1-w['affected'])
    r['decisions']=decisions(json.loads(canonical(r['packet'])))
    r['decision_sha256']=sha(dict(packet=r['packet'],decisions=r['decisions']))
    # No future branch is executed until every view's decisions are committed.
    r['probes']=run_probes(checkpoint,r['packet'])
    r['restore_checks']=0
    for action in ACTIONS:
        b=ControlledLearner.restore(checkpoint);assert b.checkpoint()==checkpoint;r['restore_checks']+=1
        trace=dict(commands=[command(b,action)],predictions=[],reviews=[])
        for t,row in enumerate(w['main'][640:1152],641):
            trace['predictions'].append(b.observe(t,row))
            if str(t) in w['selection']:
                trace['reviews'].append(b.review(t,w['selection'][str(t)]))
                if t==896:
                    trace['commands'].append(command(b,action,True))
                    saved=b.checkpoint();b=ControlledLearner.restore(saved);assert b.checkpoint()==saved;r['restore_checks']+=1
        trace['checkpoint']=json.loads(b.checkpoint());r['branches'][action]=trace
    r['metrics']=measure(r,w)
    return r


def frozen():
    parent=ROOT/'results/heaviside-native-v1'
    old=json.loads((parent/'manifest.json').read_text())
    expected={**old['sources'],**old['frozen_dependencies']}
    for path,digest in expected.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    names=set(expected)|set(SOURCES)|{str(p.relative_to(ROOT)) for p in parent.iterdir() if p.is_file()}
    names|={str(p.relative_to(ROOT)) for p in (ROOT/'results/strength-inspection-fixtures').glob('attempt-*.json')}
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(names)}


def totals(rs,ws):
    generated=sum(sum(map(len,w['local_main']))+sum(len(a) for batch in w['local_selection'] for a in batch)+len(w['composition'])+3*(len(w['main'])+sum(map(len,w['selection'].values()))) for w in ws)
    acquisition=sum(r['acquisition']['costs']['feedback_labels'] for r in rs)
    prefix=3*len(rs)*(640+10*32)
    future=3*len(rs)*4*(512+8*32)
    return dict(environments=len({w['seed'] for w in ws}),worlds=len(ws),trunks=len(rs),continuations=4*len(rs),
                generated_scalar_labels=generated,acquisition_label_presentations=acquisition,
                prefix_label_presentations=prefix,future_label_presentations=future,
                training_label_presentations=acquisition+prefix+future,
                controller_reused_scalar_labels=3*64*len(rs),
                synthetic_probe_scalar_labels=3*128*len(rs),probe_clones=128*len(rs),
                restores=sum(r['restore_checks'] for r in rs))


def main():
    fixture_files=sorted((ROOT/'results/strength-inspection-fixtures').glob('attempt-*.json'))
    assert fixture_files
    fixture=json.loads(fixture_files[-1].read_text());assert fixture['status']=='pass'
    for p,d in fixture['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    hashes=frozen();OUT.mkdir(exist_ok=False)
    (OUT/'manifest.json').write_text(json.dumps(hashes,indent=2)+'\n')
    start=time.monotonic();rs=[];ws=[]
    def timeout(*_):raise TimeoutError('Strength inspection runner900s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(3100,3112):
            for history in ('stable','forms','repeated'):
                w=worlds.generate(seed,history);ws.append(w)
                (OUT/'worlds.json').write_text(json.dumps(ws)+'\n')
                for ps in (3100,3101):
                    r=run(w,ps);rs.append(r)
                    with gzip.open(OUT/'runs.jsonl.gz','at') as stream:stream.write(canonical(r)+'\n')
            print(f'{seed}: {len(rs)}/72 cases',flush=True)
        assert frozen()==hashes
        result=dict(status='completed_pending_audit',summary=summarize(rs),totals=totals(rs,ws),elapsed_seconds=time.monotonic()-start)
        (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
        files=('manifest.json','worlds.json','runs.jsonl.gz','results.json')
        (OUT/'artifact-hashes.json').write_text(json.dumps({p:hashlib.sha256((OUT/p).read_bytes()).hexdigest() for p in files},indent=2)+'\n')
        print(result['summary']['gates'],flush=True)
    except BaseException as exc:
        (OUT/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),cases=len(rs)))+'\n');raise
    finally:signal.alarm(0)


if __name__=='__main__':main()
