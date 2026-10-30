"""Independent 026 world, policy, checkpoint and decision reconstruction."""
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
import time
import types
from audit_nested_abstractions import close,logloss
from audit_protection_interfaces import canonical,sha
import audit_structural_consolidation as old_audit
from memory_control_reference import Reference,lp,up,local_fit,upper_fit
ROOT=Path(__file__).resolve().parents[1]
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))
BRANCHES=('stable','burst','return','reversal','remap')
POLICIES=('baseline','fast','slow','always','selective','permanent','activity')
WINDOWS={'whole':(1,1280),'early':(769,896),'late':(1153,1280),'burst':(257,320),'recovery':(321,448)}
H=-.9*math.log(.9)-.1*math.log(.1)


def forms(w,t,observed=False):
    value=copy.deepcopy(w['forms']);j=w['affected']
    if w['branch']=='remap' and t>=769:value[j]=list(w['alternative'])
    flipped=(w['branch']=='burst' and 257<=t<=320) or (w['branch']=='reversal' and t>=769)
    if observed and flipped:value[j]=[1-y for y in value[j]]
    return value

def truth(w,x,a,t):
    f=forms(w,t,True);return (f[0][x[0]]+f[1][x[1]]+a)%2


def verify_world(w):
    rng=random.Random(201000+w['seed']);orders=[];expected=[];reps=[]
    for _ in range(2):
        order=list(range(4));rng.shuffle(order);orders.append(order);expected.append([int(x in order[2:]) for x in range(4)]);reps.append([order[0],order[2]])
    affected=rng.randrange(2);alt=orders[affected].copy();alt[1],alt[2]=alt[2],alt[1]
    assert w['forms']==expected and w['representatives']==reps and w['affected']==affected and w['alternative']==[int(x in alt[2:]) for x in range(4)]
    x_rng=random.Random(202000+w['seed']);y_rng=[random.Random(k+w['seed']) for k in (203000,204000,205000)]
    def draws(contexts,n):
        contexts=list(contexts)
        out=[]
        while len(out)<n:
            block=list(contexts);x_rng.shuffle(block);out.extend(block[:n-len(out)])
        return out
    n,reviews,nc,ns,horizon,period=(4,1,16,4,16,4) if w['small'] else (256,4,256,32,1280,64)
    assert w['period']==period
    def local(j):return [dict(x=x,y=(expected[j][x]+(y_rng[j].random()<.1))%2) for x in draws(range(4),n)]
    assert w['local_main']==[local(0),local(1)]
    for b in w['local_selection']:
        assert b==[[dict(x=x,y=(expected[j][x]+(y_rng[j].random()<.1))%2) for x in draws(range(4),ns)] for j in (0,1)]
    assert len(w['local_selection'])==reviews
    composed=[]
    for l,r,a in draws(itertools.product(*reps,range(2)),nc):composed.append(dict(x=[l,r],a=a,y=(expected[0][l]+expected[1][r]+a+(y_rng[2].random()<.1))%2))
    assert w['composition']==composed
    def row(t,l,r,a):
        f=forms(w,t,True);ys=[(f[j][x]+(y_rng[j].random()<.1))%2 for j,x in enumerate((l,r))]
        return dict(x=[l,r],a=a,local=ys,y=(truth(w,[l,r],a,t)+(y_rng[2].random()<.1))%2)
    main=[];block=[]
    for t in range(1,horizon+1):
        low,high=(5,8) if w['small'] else (257,768)
        if w['branch'] in ('return','reversal','remap') and low<=t<=high:main.append(None);block=[]
        else:
            if not block:block=draws(CONTEXTS,32)
            main.append(row(t,*block.pop(0)))
    assert w['main']==main
    selection={str(t):[row(t,*c) for c in draws(CONTEXTS,ns)] for t in range(period,horizon+1,period) if main[t-1] is not None}
    assert w['selection']==selection


def same(a,b):return all((a[i]==a[j])==(b[i]==b[j]) for i in range(4) for j in range(4))
def expectation(p,y):return .9*logloss(p,y)+.1*logloss(p,1-y)
def oracle(spec,local,w,t):
    buckets={}
    for l,r,a in CONTEXTS:
        x=(l,r);key=tuple(x[j] if s==2 else local[j]['groups'][x[j]] for j,s in enumerate(spec) if s)+(a,)
        buckets.setdefault(key,[]).append(.1+.8*truth(w,x,a,t))
    result=0
    for values in buckets.values():
        q=sum(values)/len(values);result+=len(values)*(-q*math.log(q)-(1-q)*math.log1p(-q))
    return result/32

def expected_eval(local,upper,w,t,transfer=False):
    contexts=[x for x in CONTEXTS if not transfer or x[0] not in w['representatives'][0] or x[1] not in w['representatives'][1]]
    predictions=[up(upper,local,[l,r],a) for l,r,a in contexts];ys=[truth(w,[l,r],a,t) for l,r,a in contexts]
    loss=mean(expectation(p,y) for p,y in zip(predictions,ys));spec=upper['spec'];risk=oracle(spec,local,w,t);drops={};adds={}
    for j,s in enumerate(spec):
        if s:
            other=spec.copy();other[j]=0;drops[str(j)]=oracle(other,local,w,t)-risk
        if s!=2:
            other=spec.copy();other[j]=2;adds[str(j)]=risk-oracle(other,local,w,t)
    return dict(index=t,predictions=predictions,expected_loss=loss,regret=loss-H,accuracy=sum((p>.5)==bool(y) for p,y in zip(predictions,ys))/len(predictions),
        local_exact=[same(m['partition'],f) for m,f in zip(local,forms(w,t))],semantic_alignment=[m['groups']==f for m,f in zip(local,forms(w,t))],
        local_groups=[len(m['counts']) for m in local],spec=spec,contexts=len(contexts),oracle_regret=risk-H,removal_costs=drops,raw_addition_gains=adds,
        sufficient_minimal=risk-H<=.10 and all(v>.02 for v in drops.values()) and all(v<=.02 for v in adds.values()))


def verify_legacy(r,w,checkpoint,empty=False):
    c=copy.deepcopy(w);clock=[t for t,row in enumerate(w['main'],1) if row is not None]
    c['main']=[] if empty else [row for row in w['main'] if row is not None];c['selection']=[] if empty else list(w['selection'].values())
    def ev(saved,model,nodes,world,t,transfer=False):
        result=expected_eval([n.state() for n in nodes],model,w,0 if not t else clock[t-1],transfer)
        result['index']=t;close(saved,result)
    replay=types.FunctionType(old_audit.verify_run.__code__,dict(old_audit.verify_run.__globals__,verify_eval=ev),argdefs=old_audit.verify_run.__defaults__)
    replay(r,c,checkpoint,review_every=w['period'],measure=False)


def verify_run(r,w,checkpoint,measure=True):
    assert r['seed']==w['seed'] and r['branch']==w['branch'] and r['policy'] in POLICIES
    assert len(r['predictions'])==len(w['main']) and len(r['evaluations'])==len(w['main'])//w['period']
    if r['policy']=='baseline':
        verify_legacy(r['legacy'],w,checkpoint)
        clock=[t for t,row in enumerate(w['main'],1) if row is not None];pos=0;last=r['legacy']['transfer']
        lookup={clock[v['index']-1]:v['evaluation'] for v in r['legacy']['reviews']}
        for t,row in enumerate(w['main'],1):
            if row is None:assert r['predictions'][t-1] is None
            else:
                close(r['predictions'][t-1],r['legacy']['local_predictions'][pos]+[r['legacy']['predictions'][pos]]);pos+=1
            if t%w['period']==0:
                if t in lookup:last=lookup[t]
                expected=copy.deepcopy(last);expected['index']=t;close(r['evaluations'][t//w['period']-1],expected)
        close(r['transfer'],r['legacy']['transfer']);close(r['costs'],r['legacy']['costs']);assert r['reviews']==[] and r['snapshots']==[]
    else:
        verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
        ref=Reference(r['acquisition_checkpoint'],r['policy']);close(r['transfer'],expected_eval(ref.locals,ref.upper,w,0,True))
        rev=0;snapshot=0
        for t,row in enumerate(w['main'],1):
            close(r['predictions'][t-1],ref.observe(t,row))
            if str(t) in w['selection']:ref.review(t,w['selection'][str(t)],r['reviews'][rev]);rev+=1
            if t%w['period']==0:close(r['evaluations'][t//w['period']-1],expected_eval(ref.locals,ref.upper,w,t))
            if t in ((4,8) if w['small'] else (256,768)):
                upper=ref.fit(2,ref.upper['spec'],ref.slow[2],'probe')
                value=mean(expectation(up(upper,ref.locals,[l,z],a),truth(w,[l,z],a,t)) for l,z,a in CONTEXTS)
                ls=[]
                for j in (0,1):
                    m=ref.fit(j,ref.locals[j]['partition'],ref.slow[j],'probe');ls.append(mean(expectation(lp(m,x),forms(w,t,True)[j][x]) for x in range(4)))
                close(r['snapshots'][snapshot],dict(index=t,mass=ref.mass(),slow_loss=value,slow_local_loss=ls,
                    partitions=[m['partition'] for m in ref.locals],spec=ref.upper['spec']));snapshot+=1
        assert len(r['reviews'])==rev and len(r['snapshots'])==snapshot
        close(checkpoint,ref.state())
        costs=ref.costs.copy();costs['feedback_labels']=r['acquisition']['costs']['feedback_labels']+3*len(ref.main_ids)+3*sum(map(len,w['selection'].values()))
        close(r['costs'],costs)
        assert len(ref.fast)==len(ref.slow)==3 and sum(map(len,ref.fast))==40
        for bank in (ref.fast,ref.slow):assert all(-1e-8<=v[0]<=v[1]+1e-8 for table in bank for v in table)
    assert sha(checkpoint)==r['checkpoint_sha256']
    if measure:verify_metrics(r,w)


def good(e):return all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10

def verify_metrics(r,w):
    obs=[];latent=[];local=[[],[]]
    for t,row in enumerate(w['main'],1):
        if row is None:continue
        ps=r['predictions'][t-1];obs.append((t,logloss(ps[2],row['y'])));latent.append((t,expectation(ps[2],truth(w,row['x'],row['a'],t))))
        for j in (0,1):local[j].append(logloss(ps[j],row['local'][j]))
    m={}
    for name,values in [('observed',obs),('latent',latent)]:
        m[name]={}
        for window,(lo,hi) in WINDOWS.items():
            selected=[v for t,v in values if lo<=t<=hi];m[name][window]=sum(selected)/len(selected) if selected else None
    es={e['index']:e for e in r['evaluations']};recovery=None;prior=False
    for t in range(832,1281,64):
        if prior and good(es[t]):recovery=t;break
        prior=good(es[t])
    m.update(local_loss=[sum(xs)/len(xs) for xs in local],transfer_valid=good(r['transfer']),final_valid=good(es[1280]),gap_valid=good(es[768]),gap_loss=es[768]['expected_loss'],recovery=recovery,
        structure_errors=sum(not(all(e['local_exact']) and e['sufficient_minimal']) for e in es.values()),final_structure=all(es[1280]['local_exact']) and es[1280]['sufficient_minimal'],
        transfers=sum(mig['accepted'] for rev in r['reviews'] for mig in rev['migrations']),proposals=r['costs'].get('proposals',0),transferred_mass=r['costs'].get('transferred_mass',0),
        group_changes=sum(rev['channels'][j]['before']['groups']!=rev['channels'][j]['after']['groups'] for rev in r['reviews'] for j in (0,1)))
    close(r['metrics'],m)


def verify_summary(runs,saved):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});assert len(pairs)==10
    get={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    assert len(saved['groups'])==35
    for group,(h,p) in zip(saved['groups'],itertools.product(BRANCHES,POLICIES)):
        ms=[get[s,q,h,p] for s,q in pairs];expected=dict(branch=h,policy=p,runs=10)
        for k in ('transfer_valid','final_valid','gap_valid','final_structure'):expected[k]=sum(m[k] for m in ms)
        for k in ('gap_loss','structure_errors','transfers','proposals','transferred_mass','group_changes'):expected[k]=sum(m[k] for m in ms)/10
        for name in ('observed','latent'):
            expected[name]={}
            for window in WINDOWS:
                values=[m[name][window] for m in ms if m[name][window] is not None];expected[name][window]=sum(values)/len(values) if values else None
        expected['recovery_censored']=sum(m['recovery'] is None for m in ms);close(group,expected)
    contrasts=[('selective',c) for c in ('fast','baseline','always','slow')]+[('permanent','selective'),('activity','selective'),('always','fast'),('slow','fast')]
    keys=[(a,b,s,q,h) for a,b in contrasts for s,q in pairs for h in BRANCHES]
    assert len(saved['paired'])==len(keys)
    for row,(a,b,s,q,h) in zip(saved['paired'],keys):
        x,y=get[s,q,h,a],get[s,q,h,b]
        expected=dict(candidate=a,control=b,seed=s,proposal_seed=q,branch=h,gap_cost=x['gap_loss']-y['gap_loss'],
            recovery_delay=(1344 if x['recovery'] is None else x['recovery'])-(1344 if y['recovery'] is None else y['recovery']))
        for name in ('observed','latent'):expected[name+'_cost']={k:x[name][k]-y[name][k] if x[name][k] is not None else None for k in WINDOWS}
        close(row,expected)
    selection=[];revision=[]
    for s,q in pairs:
        gains=[get[s,q,h,'always']['observed'][k]-get[s,q,h,'selective']['observed'][k] for h,k in [('burst','recovery'),('reversal','early'),('remap','early')]]
        selection.append(dict(seed=s,proposal_seed=q,gain=sum(gains)/3))
        gains=[get[s,q,h,'slow']['observed']['early']-get[s,q,h,'selective']['observed']['early'] for h in ('reversal','remap')]
        revision.append(dict(seed=s,proposal_seed=q,gain=sum(gains)/2))
    close(saved['selection_pairs'],selection);close(saved['revision_pairs'],revision)
    def guards(controls):
        flags=dict(mean_cost=True,worst_pair=True,recovery=True)
        for control in controls:
            for h,window in [('stable','whole'),('burst','burst'),('burst','recovery'),('reversal','early'),('remap','early')]:
                for name in ('observed','latent'):
                    costs=[get[s,q,h,'selective'][name][window]-get[s,q,h,control][name][window] for s,q in pairs]
                    if sum(costs)/10>.02:flags['mean_cost']=False
                    if name=='observed' and max(costs)>.10:flags['worst_pair']=False
            for h in ('reversal','remap'):
                delays=[(get[s,q,h,'selective']['recovery'] or 1344)-(get[s,q,h,control]['recovery'] or 1344) for s,q in pairs]
                if sum(delays)/10>64:flags['recovery']=False
        return flags
    return_gains=[get[s,q,'return','fast']['observed']['early']-get[s,q,'return','selective']['observed']['early'] for s,q in pairs]
    gap_gains=[get[s,q,'return','fast']['gap_loss']-get[s,q,'return','selective']['gap_loss'] for s,q in pairs]
    flags=dict(return_mean_gain=sum(return_gains)/10>=.02,return_pairs=sum(g>0 for g in return_gains)>=8,
        gap_gain=sum(gap_gains)/10>=.02,gap_validity=sum(get[s,q,'return','selective']['gap_valid'] for s,q in pairs)>=8,
        final_validity=all(sum(get[s,q,h,'selective']['final_valid'] for s,q in pairs)>=8 for h in BRANCHES),
        **guards(('fast','baseline')),selection_mean_gain=sum(r['gain'] for r in selection)/10>=.01,
        selection_pairs=sum(r['gain']>0 for r in selection)>=8,**{'selection_'+k:v for k,v in guards(('always',)).items()})
    close(saved['gates'],flags);assert saved['primary_pass']==all(flags.values())
    dual=dict(return_noninferiority=sum(get[s,q,'return','selective']['observed']['early']-get[s,q,'return','slow']['observed']['early'] for s,q in pairs)/10<=.02,
        revision_mean_gain=sum(r['gain'] for r in revision)/10>=.02,revision_pairs=sum(r['gain']>0 for r in revision)>=8,**guards(('slow',)))
    close(saved['dual_store_gates'],dual);assert saved['dual_store_pass']==all(dual.values())
    expected=[]
    for seed in sorted({s for s,q in pairs}):
        for h in BRANCHES:
            for p in POLICIES:
                ms=[get[s,q,h,p] for s,q in pairs if s==seed]
                expected.append(dict(seed=seed,branch=h,policy=p,whole_loss=sum(m['observed']['whole'] for m in ms)/len(ms),
                    early_loss=sum(m['observed']['early'] for m in ms)/len(ms),gap_loss=sum(m['gap_loss'] for m in ms)/len(ms)))
    close(saved['environment_means'],expected)


def main():
    out=ROOT/'results/memory-control-v2';started=time.monotonic()
    def timeout(*_):raise TimeoutError('900-second memory audit ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
        assert data['status']=='completed_pending_audit' and data['hashes']==manifest
        for path,digest in manifest.items():assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
        worlds=json.loads((out/'worlds.json').read_text());lookup={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==25 and set(lookup)==set(itertools.product(range(1600,1605),BRANCHES))
        for w in worlds:assert not w['small'];verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
        assert len(runs)==350 and {(r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs}==set(itertools.product(range(1600,1605),(1600,1601),BRANCHES,POLICIES))
        for i,r in enumerate(runs,1):
            with gzip.open(out/r['checkpoint_file'],'rt') as f:checkpoint=json.load(f)
            verify_run(r,lookup[r['seed'],r['branch']],checkpoint)
            assert r['costs']['feedback_labels']==(6784 if r['branch'] in ('stable','burst') else 4480)
            if i%25==0:print(f'{i}/350 complete memory traces independently reconstructed',flush=True)
        verify_summary(runs,data['summary'])
        total=dict(runs=350,generated_labels=135040,used_labels=0,candidate_fits=0,active_fits=0,probe_fits=0,raw_bin_visits=0,
            scoring_queries=0,main_predictions=0,evaluation_predictions=0,slow_probe_predictions=0,oracle_context_queries=0,
            legacy_auxiliary_predictions=0,reused_grid_predictions=0)
        for r in runs:
            c=r['costs'];total['used_labels']+=c['feedback_labels']
            if r['policy']=='baseline':
                total['candidate_fits']+=c['candidate_fits']+c['upper_candidate_fits'];total['scoring_queries']+=c['scoring_queries']
                auxiliary=r['legacy']['endpoints'];total['reused_grid_predictions']+=32*sum(row is None for row in lookup[r['seed'],r['branch']]['main'][63::64])
            else:
                a=r['acquisition']['costs'];total['candidate_fits']+=c['candidate_fits']+a['candidate_fits'];total['scoring_queries']+=c['scoring_queries']+a['scoring_queries']
                for key in ('active_fits','probe_fits','raw_bin_visits'):total[key]+=c[key]
                total['slow_probe_predictions']+=40*len(r['snapshots']);auxiliary=[r['acquisition']['transfer']]
            total['legacy_auxiliary_predictions']+=sum(e['contexts'] for e in auxiliary)
            total['main_predictions']+=3*sum(p is not None for p in r['predictions'])
            for e in [r['transfer']]+r['evaluations']:total['evaluation_predictions']+=e['contexts']
            for e in [r['transfer']]+r['evaluations']+auxiliary:total['oracle_context_queries']+=32*(1+len(e['removal_costs'])+len(e['raw_addition_gains']))
        close(data['totals'],total)
        assert total['used_labels']==1890560 and total['main_predictions']==1021440 and total['evaluation_predictions']==232400
        assert total['slow_probe_predictions']==24000 and total['legacy_auxiliary_predictions']==12000 and total['reused_grid_predictions']==7680
        for key,bound in [('candidate_fits',250000),('scoring_queries',15000000),('raw_bin_visits',100000000),('oracle_context_queries',1300000)]:assert total[key]<=bound
        assert data['elapsed_seconds']<900
        attempts=[json.loads(p.read_text()) for p in sorted((ROOT/'results/memory-control-fixtures').glob('attempt-*.json'))]
        assert attempts[-1]['status']=='pass' and sum(a['charged_labels'] for a in attempts)<=5000
        result=dict(status='pass',runs=350,independently_replayed_labels=total['used_labels'],primary_pass=data['summary']['primary_pass'],
            dual_store_pass=data['summary']['dual_store_pass'],elapsed_seconds=time.monotonic()-started,
            **{name+'_sha256':hashlib.sha256((out/path).read_bytes()).hexdigest() for name,path in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    except Exception as exc:
        (out/'audit-failure.json').write_text(json.dumps(dict(status='failed',error=repr(exc),elapsed_seconds=time.monotonic()-started),indent=2)+'\n');raise
    finally:signal.alarm(0)

if __name__=='__main__':main()
