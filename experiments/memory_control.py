"""026 memory control: frozen worlds, original reference, and paired policies."""
import copy
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import signal
from statistics import mean
import sys
import time
import types
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.structural import StructuralLearner
from advaita.memory_control import MemoryLearner,fit_local,fit_upper,upper_p,local_p
from advaita.state import canonical
import structural_consolidation as legacy
from memory_control_metrics import metrics,summarize
BRANCHES=('stable','burst','return','reversal','remap')
POLICIES=('baseline','fast','slow','always','selective','permanent','activity')
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))
H=-.9*math.log(.9)-.1*math.log(.1)
FILES=('advaita/memory_control.py','experiments/memory_control.py','experiments/memory_control_metrics.py',
 'experiments/memory_control_protocol.md','checks/memory_control_reference.py','checks/audit_memory_control.py','checks/test_memory_control.py')


def forms_at(w,t,observed=False):
    f=copy.deepcopy(w['forms']);j=w['affected']
    if w['branch']=='remap' and t>768:f[j]=w['alternative'].copy()
    if observed and ((w['branch']=='burst' and 256<t<=320) or (w['branch']=='reversal' and t>768)):f[j]=[1-v for v in f[j]]
    return f

def target(w,x,a,t):
    f=forms_at(w,t,True)
    return f[0][x[0]]^f[1][x[1]]^a


def generate(seed,branch,small=False):
    rng=random.Random(201000+seed);orders=[];forms=[];reps=[]
    for j in range(2):
        order=list(range(4));rng.shuffle(order);orders.append(order)
        forms.append([int(order.index(x)>=2) for x in range(4)]);reps.append([order[0],order[2]])
    affected=rng.randrange(2);order=orders[affected].copy();order[1],order[2]=order[2],order[1]
    w=dict(seed=seed,branch=branch,forms=forms,representatives=reps,affected=affected,
        alternative=[int(order.index(x)>=2) for x in range(4)],small=small)
    inputs=random.Random(202000+seed);noise=[random.Random(base+seed) for base in (203000,204000,205000)]
    def shuffled(n,contexts):
        rows=[]
        while len(rows)<n:
            block=list(contexts);inputs.shuffle(block);rows+=block[:n-len(rows)]
        return rows
    def local(n,j):return [dict(x=x,y=forms[j][x]^int(noise[j].random()<.1)) for x in shuffled(n,range(4))]
    n,wreviews,composition,selection,horizon,period=(4,1,8,4,16,4) if small else (256,4,256,32,1280,64)
    w['period']=period
    w['local_main']=[local(n,j) for j in range(2)]
    w['local_selection']=[[local(selection,j) for j in range(2)] for _ in range(wreviews)]
    w['composition']=[dict(x=[l,r],a=a,y=target(w,[l,r],a,0)^int(noise[2].random()<.1)) for l,r,a in shuffled(composition,itertools.product(*reps,(0,1)))]
    def labelled(t,x,a):
        f=forms_at(w,t,True)
        return dict(x=list(x),a=a,local=[f[j][x[j]]^int(noise[j].random()<.1) for j in range(2)],y=target(w,x,a,t)^int(noise[2].random()<.1))
    w['main']=[];block=[]
    for t in range(1,horizon+1):
        blank=branch in ('return','reversal','remap') and (5<=t<=8 if small else 257<=t<=768)
        if blank:w['main'].append(None);block=[];continue
        if not block:block=shuffled(32,CONTEXTS)
        l,r,a=block.pop(0);w['main'].append(labelled(t,[l,r],a))
    w['selection']={str(t):[labelled(t,[l,r],a) for l,r,a in shuffled(selection,CONTEXTS)]
        for t in range(period,horizon+1,period) if w['main'][t-1] is not None}
    return w


def same(a,b):return all((a[i]==a[j])==(b[i]==b[j]) for i in range(4) for j in range(4))
def expectation(p,y):return -.9*math.log(p if y else 1-p)-.1*math.log(1-p if y else p)
def oracle(spec,locals_,w,t):
    bins={}
    for l,r,a in CONTEXTS:
        x=[l,r];k=tuple(x[j] if s==2 else locals_[j]['groups'][x[j]] for j,s in enumerate(spec) if s)+(a,)
        bins.setdefault(k,[]).append(.1+.8*target(w,x,a,t))
    return sum(len(v)*(-mean(v)*math.log(mean(v))-(1-mean(v))*math.log1p(-mean(v))) for v in bins.values())/32

def evaluate(locals_,upper,w,t,transfer=False):
    contexts=[c for c in CONTEXTS if not transfer or c[0] not in w['representatives'][0] or c[1] not in w['representatives'][1]]
    ps=[upper_p(upper,locals_,[l,r],a) for l,r,a in contexts];ys=[target(w,[l,r],a,t) for l,r,a in contexts]
    value=mean(expectation(p,y) for p,y in zip(ps,ys));spec=upper['spec'];risk=oracle(spec,locals_,w,t)
    drops={};adds={}
    for j,s in enumerate(spec):
        if s:
            alt=spec.copy();alt[j]=0;drops[str(j)]=oracle(alt,locals_,w,t)-risk
        if s!=2:
            alt=spec.copy();alt[j]=2;adds[str(j)]=risk-oracle(alt,locals_,w,t)
    return dict(index=t,predictions=ps,expected_loss=value,regret=value-H,accuracy=mean((p>.5)==bool(y) for p,y in zip(ps,ys)),
        local_exact=[same(n['partition'],f) for n,f in zip(locals_,forms_at(w,t))],semantic_alignment=[n['groups']==f for n,f in zip(locals_,forms_at(w,t))],
        local_groups=[len(n['counts']) for n in locals_],spec=spec.copy(),contexts=len(contexts),oracle_regret=risk-H,
        removal_costs=drops,raw_addition_gains=adds,sufficient_minimal=risk-H<=.10 and all(v>.02 for v in drops.values()) and all(v<=.02 for v in adds.values()))

def compressed(w,empty=False):
    c=copy.deepcopy(w);c['clock']=[t for t,row in enumerate(w['main'],1) if row is not None]
    c['main']=[] if empty else [r for r in w['main'] if r is not None]
    c['selection']=[] if empty else list(w['selection'].values())
    return c

def legacy_run(w,ps,empty=False):
    c=compressed(w,empty)
    def ev(learner,world,t,transfer=False):
        clock=0 if t==0 else world['clock'][t-1]
        result=evaluate([n.model.state() for n in learner.nodes],learner.upper.state(),w,clock,transfer)
        result['index']=t;return result
    fn=types.FunctionType(legacy.run.__code__,dict(legacy.run.__globals__,evaluate=ev),argdefs=legacy.run.__defaults__)
    return fn(c,'integrated',ps,review_every=w['period'],measure=False)


def run(w,policy,ps,measure=True):
    if policy=='baseline':
        old,checkpoint=legacy_run(w,ps);clock=[t for t,r in enumerate(w['main'],1) if r is not None]
        predictions=[];pos=0;evaluations=[];previous=old['transfer'];lookup={clock[v['index']-1]:v['evaluation'] for v in old['reviews']}
        for t,row in enumerate(w['main'],1):
            if row is None:predictions.append(None)
            else:predictions.append(old['local_predictions'][pos]+[old['predictions'][pos]]);pos+=1
            if t%w['period']==0:
                if t in lookup:previous=lookup[t]
                e=copy.deepcopy(previous);e['index']=t;evaluations.append(e)
        r=dict(seed=w['seed'],branch=w['branch'],policy=policy,proposal_seed=ps,transfer=old['transfer'],predictions=predictions,
            evaluations=evaluations,reviews=[],snapshots=[],legacy=old,costs=old['costs'])
    else:
        acquisition,initial=legacy_run(w,ps,True);core=StructuralLearner.restore(initial);learner=MemoryLearner(core,policy)
        r=dict(seed=w['seed'],branch=w['branch'],policy=policy,proposal_seed=ps,acquisition=acquisition,acquisition_checkpoint=json.loads(initial),
            transfer=evaluate(learner.locals,learner.upper,w,0,True),predictions=[],evaluations=[],reviews=[],snapshots=[])
        for t,row in enumerate(w['main'],1):
            r['predictions'].append(learner.observe(t,row))
            if str(t) in w['selection']:r['reviews'].append(learner.review(t,w['selection'][str(t)]))
            if t%w['period']==0:r['evaluations'].append(evaluate(learner.locals,learner.upper,w,t))
            if t in ((4,8) if w['small'] else (256,768)):
                # Slow-only probes use actual current meanings; no latent/oracle forms in fitting.
                m=learner.fit(2,learner.upper['spec'],learner.slow[2],'probe')
                slow_loss=mean(expectation(upper_p(m,learner.locals,[l,z],a),target(w,[l,z],a,t)) for l,z,a in CONTEXTS)
                local_loss=[]
                for j in (0,1):
                    lm=learner.fit(j,learner.locals[j]['partition'],learner.slow[j],'probe')
                    local_loss.append(mean(expectation(local_p(lm,x),forms_at(w,t,True)[j][x]) for x in range(4)))
                r['snapshots'].append(dict(index=t,mass=learner.mass(),slow_loss=slow_loss,slow_local_loss=local_loss,
                    partitions=[n['partition'].copy() for n in learner.locals],spec=learner.upper['spec'].copy()))
        r['costs']=learner.costs.copy();r['costs']['feedback_labels']=acquisition['costs']['feedback_labels']+3*sum(row is not None for row in w['main'])+3*sum(map(len,w['selection'].values()))
        checkpoint=learner.checkpoint()
    r['checkpoint_sha256']=hashlib.sha256(checkpoint.encode()).hexdigest()
    if measure:r['metrics']=metrics(r,w,target,forms_at)
    return r,checkpoint


def hashes():
    previous=json.loads((ROOT/'results/explicit-roles-v1/manifest.json').read_text())
    for p,digest in previous.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==digest,p
    files=set(previous)|set(FILES)
    files.update('results/explicit-roles-v1/'+p for p in ('manifest.json','results.json','audit.json','worlds.json','runs.jsonl.gz'))
    files.update(str(p.relative_to(ROOT)) for p in (ROOT/'results/memory-control-fixtures').glob('*') if p.is_file())
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}


def totals(runs,worlds):
    new=[r for r in runs if r['policy']!='baseline'];old=[r for r in runs if r['policy']=='baseline']
    labels=lambda w:sum(map(len,w['local_main']))+sum(sum(map(len,b)) for b in w['local_selection'])+len(w['composition'])+3*sum(x is not None for x in w['main'])+3*sum(map(len,w['selection'].values()))
    es=[e for r in runs for e in [r['transfer'],*r['evaluations']]]
    auxiliary=[e for r in old for e in r['legacy']['endpoints']]+[r['acquisition']['transfer'] for r in new]
    reused=32*sum(sum(row is None for row in next(w for w in worlds if (w['seed'],w['branch'])==(r['seed'],r['branch']))['main'][63::64]) for r in old)
    return dict(legacy_auxiliary_predictions=sum(e['contexts'] for e in auxiliary),reused_grid_predictions=reused,
        runs=len(runs),generated_labels=sum(labels(w) for w in worlds),used_labels=sum(r['costs']['feedback_labels'] for r in runs),
        candidate_fits=sum(r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'] for r in new)+sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in old),
        active_fits=sum(r['costs']['active_fits'] for r in new),probe_fits=sum(r['costs']['probe_fits'] for r in new),
        raw_bin_visits=sum(r['costs']['raw_bin_visits'] for r in new),
        scoring_queries=sum(r['costs']['scoring_queries']+(r['acquisition']['costs']['scoring_queries'] if r['policy']!='baseline' else 0) for r in runs),
        main_predictions=3*sum(sum(p is not None for p in r['predictions']) for r in runs),evaluation_predictions=sum(e['contexts'] for e in es),
        slow_probe_predictions=40*sum(len(r['snapshots']) for r in new),
        oracle_context_queries=32*sum(1+len(e['removal_costs'])+len(e['raw_addition_gains']) for e in es+auxiliary))


def main():
    fixturefiles=sorted((ROOT/'results/memory-control-fixtures').glob('attempt-*.json'));assert fixturefiles
    fs=[json.loads(p.read_text()) for p in fixturefiles];assert fs[-1]['status']=='pass' and sum(f['charged_labels'] for f in fs)<=5000
    for p,d in fs[-1]['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/memory-control-v1';out.mkdir(exist_ok=False);(out/'checkpoints').mkdir()
    provenance=hashes();(out/'manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
    start=time.monotonic();runs=[];worlds=[]
    def timeout(*_):raise TimeoutError('900-second memory-control benchmark ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(1600,1605):
            for branch in BRANCHES:
                w=generate(seed,branch);worlds.append(w);(out/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (1600,1601):
                    for policy in POLICIES:
                        r,checkpoint=run(w,policy,ps);path=f'checkpoints/{seed}-{branch}-{ps}-{policy}.json.gz'
                        with gzip.open(out/path,'wt') as f:f.write(checkpoint)
                        r['checkpoint_file']=path;runs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/350 saved',flush=True)
        assert hashes()==provenance;resources=totals(runs,worlds)
        assert resources['used_labels']==1890560 and resources['generated_labels']==135040
        assert resources['main_predictions']==1021440 and resources['evaluation_predictions']==232400 and resources['slow_probe_predictions']==24000
        for k,v in dict(candidate_fits=250000,scoring_queries=15000000,raw_bin_visits=100000000,oracle_context_queries=1300000).items():assert resources[k]<=v,(k,resources[k])
        result=dict(status='completed_pending_audit',summary=summarize(runs),totals=resources,hashes=provenance,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary']['gates'],indent=2))
    except Exception as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed_runs=len(runs),elapsed_seconds=time.monotonic()-start),indent=2)+'\n');raise
    finally:signal.alarm(0)

if __name__=='__main__':main()
