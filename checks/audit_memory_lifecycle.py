"""030 independent world, policy, measurements and coverage reconstruction."""
import copy,gzip,hashlib,itertools,json,math,random,signal,time,types
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close,logloss
import audit_memory_control_v2 as old
from memory_revision_reference import RevisionReference
from audit_memory_revision import totals
ROOT=Path(__file__).resolve().parents[1]
BRANCHES=('repeated','forms','rare');POLICIES=('baseline','fast','relaxed','combined')
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))
WINDOWS={'whole':[(1,2048)],'initial':[(1,512)],'settled':[(641,1024),(1153,1536),(1665,2048)],'early':[(513,640),(1025,1152),(1537,1664)],'rare':[(513,1536)],'returning':[(1537,2048)]}

def forms(w,t,observed=False):
    fs=copy.deepcopy(w['forms']);odd=(max(0,t-1)//w['phase_length'])%2;j=w['affected']
    if w['branch']=='forms' and odd:fs[j]=list(w['alternative'])
    if w['branch']=='repeated' and observed and odd:fs[j]=[1-v for v in fs[j]]
    return fs

def truth(w,x,a,t):
    f=forms(w,t,True);return (f[0][x[0]]+f[1][x[1]]+a)%2

def verify_world(w):
    layout=random.Random(201000+w['seed']);orders=[];fs=[];representatives=[]
    for _ in range(2):
        states=list(range(4));layout.shuffle(states);orders.append(states)
        fs.append([int(x in states[2:]) for x in range(4)]);representatives.append([states[0],states[2]])
    j=layout.randrange(2);alt=list(orders[j]);alt[1],alt[2]=alt[2],alt[1]
    assert w['forms']==fs and w['affected']==j and w['representatives']==representatives and w['alternative']==[int(x in alt[2:]) for x in range(4)]
    small=w['small'];phase=8 if small else 512;period=4 if small else 64
    assert w['phase_length']==phase and w['period']==period
    xr=random.Random(202000+w['seed']);yr=[random.Random(b+w['seed']) for b in (203000,204000,205000)]
    def sample(domain,n):
        domain=list(domain);out=[]
        while len(out)<n:
            part=list(domain);xr.shuffle(part);out+=part[:n-len(out)]
        return out
    n,ns,nc,nr=(4,4,16,1) if small else (256,32,256,4)
    def local(k,n):return [dict(x=x,y=(fs[k][x]+(yr[k].random()<.1))%2) for x in sample(range(4),n)]
    assert w['local_main']==[local(0,n),local(1,n)]
    assert w['local_selection']==[[local(0,ns),local(1,ns)] for _ in range(nr)]
    composition=[]
    for l,r,a in sample(itertools.product(*representatives,(0,1)),nc):composition.append(dict(x=[l,r],a=a,y=(truth(w,[l,r],a,0)+(yr[2].random()<.1))%2))
    assert composition==w['composition']
    def block(t):
        if w['branch']=='rare' and phase<t<=3*phase:
            majority=[c for c in CONTEXTS if fs[j][c[j]]==0];minority=[c for c in CONTEXTS if fs[j][c[j]]==1]
            batch=sample(majority,30)+sample(minority,2);xr.shuffle(batch);return batch
        return sample(CONTEXTS,32)
    def row(t,c):
        x=list(c[:2]);a=c[2];f=forms(w,t,True)
        return dict(x=x,a=a,local=[(f[k][x[k]]+(yr[k].random()<.1))%2 for k in (0,1)],y=(truth(w,x,a,t)+(yr[2].random()<.1))%2)
    main=[];pending=[]
    for t in range(1,phase*4+1):
        if t%phase==1:pending=[]
        if not pending:pending=block(t)
        main.append(row(t,pending.pop(0)))
    assert w['main']==main
    assert w['selection']=={str(t):[row(t,c) for c in block(t)[:ns]] for t in range(period,len(main)+1,period)}

oracle=types.FunctionType(old.oracle.__code__,dict(old.oracle.__globals__,truth=truth))
expected_eval=types.FunctionType(old.expected_eval.__code__,dict(old.expected_eval.__globals__,truth=truth,forms=forms,oracle=oracle),argdefs=old.expected_eval.__defaults__)
verify_legacy=types.FunctionType(old.verify_legacy.__code__,dict(old.verify_legacy.__globals__,expected_eval=expected_eval),argdefs=old.verify_legacy.__defaults__)

def verify_metrics(r,w):
    values={'observed':[],'latent':[]}
    for t,row in enumerate(w['main'],1):
        p=r['predictions'][t-1][2];y=truth(w,row['x'],row['a'],t)
        values['observed'].append((t,logloss(p,row['y'])));values['latent'].append((t,.9*logloss(p,y)+.1*logloss(p,1-y)))
    expected={}
    for name,seq in values.items():
        expected[name]={}
        for window,intervals in WINDOWS.items():
            xs=[v for t,v in seq if any(lo<=t<=hi for lo,hi in intervals)];expected[name][window]=sum(xs)/len(xs)
    ev={e['index']:e for e in r['evaluations']};rare=[]
    for p,c in zip(ev[1536]['predictions'],CONTEXTS):
        if w['forms'][w['affected']][c[w['affected']]]:
            y=truth(w,list(c[:2]),c[2],1536);rare.append(.9*logloss(p,y)+.1*logloss(p,1-y))
    good=lambda e:all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10
    expected.update(endpoint_valid=[good(ev[t]) for t in (512,1024,1536,2048)],final_valid=good(ev[2048]),rare_loss=sum(rare)/len(rare),
        structure_errors=sum(not(all(e['local_exact']) and e['sufficient_minimal']) for e in ev.values()),weakenings=r['costs'].get('weakenings',0),transfers=r['costs'].get('transfers',0))
    close(r['metrics'],expected)

_replay=types.FunctionType(old.verify_run.__code__,dict(old.verify_run.__globals__,Reference=RevisionReference,POLICIES=POLICIES,
    expected_eval=expected_eval,verify_legacy=verify_legacy,forms=forms,truth=truth,verify_metrics=verify_metrics),argdefs=old.verify_run.__defaults__)
def verify_run(r,w,c,measure=True):
    _replay(r,w,c,measure)
    if r['policy']!='baseline':
        close(r['runtime_checkpoint'],dict(schema=29,memory=r['policy'],tick=len(w['main']),active=len(w['main']),last_labelled=True,
            review_ticks=[int(t) for t in w['selection']],last_review=r['reviews'][-1],controls=[],engine=c))

def verify_summary(runs,saved):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});assert len(pairs)==10
    d={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    get=lambda s,q,h,p:d[s,q,h,p]
    expected_groups=[]
    for h,p in itertools.product(BRANCHES,POLICIES):
        ms=[get(s,q,h,p) for s,q in pairs]
        g=dict(branch=h,policy=p,final_valid=sum(m['final_valid'] for m in ms),endpoint_valid=[sum(m['endpoint_valid'][i] for m in ms) for i in range(4)],
            rare_loss=sum(m['rare_loss'] for m in ms)/10,structure_errors=sum(m['structure_errors'] for m in ms)/10,weakenings=sum(m['weakenings'] for m in ms),transfers=sum(m['transfers'] for m in ms))
        for name in ('observed','latent'):g[name]={k:sum(m[name][k] for m in ms)/10 for k in WINDOWS}
        expected_groups.append(g)
    close(saved['groups'],expected_groups);paired=[]
    for c in ('relaxed','fast','baseline'):
        for s,q in pairs:
            for h in BRANCHES:
                a,b=get(s,q,h,'combined'),get(s,q,h,c)
                row=dict(seed=s,proposal_seed=q,branch=h,control=c,rare_gain=b['rare_loss']-a['rare_loss'])
                for n in ('observed','latent'):row[n+'_cost']={k:a[n][k]-b[n][k] for k in WINDOWS}
                paired.append(row)
    close(saved['paired'],paired)
    revision=[dict(seed=s,proposal_seed=q,gain=sum(get(s,q,h,'relaxed')['observed']['settled']-get(s,q,h,'combined')['observed']['settled'] for h in ('repeated','forms'))/2) for s,q in pairs]
    rare=[get(s,q,'rare','fast')['rare_loss']-get(s,q,'rare','combined')['rare_loss'] for s,q in pairs]
    close(saved['revision_pairs'],revision);close(saved['rare_gains'],rare)
    gates=dict(revision_gain=sum(x['gain'] for x in revision)/10>=.02,revision_pairs=sum(x['gain']>0 for x in revision)>=8,
        final_validity=all(sum(get(s,q,h,'combined')['final_valid'] for s,q in pairs)>=8 for h in BRANCHES),rare_gain=sum(rare)/10>=.02,rare_pairs=sum(x>0 for x in rare)>=8,
        preservation_mean=True,preservation_worst=True,revision_mean=True,revision_worst=True)
    for c in ('relaxed','baseline'):
        for h in BRANCHES:
            for k in (['initial','whole','returning'] if h=='rare' else ['initial']):
                for n in ('observed','latent'):
                    xs=[get(s,q,h,'combined')[n][k]-get(s,q,h,c)[n][k] for s,q in pairs]
                    if sum(xs)/10>.02:gates['preservation_mean']=False
                    if n=='observed' and max(xs)>.10:gates['preservation_worst']=False
    for h in ('repeated','forms'):
        for k in ('early','settled'):
            for n in ('observed','latent'):
                xs=[get(s,q,h,'combined')[n][k]-get(s,q,h,'relaxed')[n][k] for s,q in pairs]
                if sum(xs)/10>.02:gates['revision_mean']=False
                if n=='observed' and max(xs)>.10:gates['revision_worst']=False
    close(saved['gates'],gates);assert saved['primary_pass']==all(gates.values())
    env=[dict(seed=s,revision_gain=sum(r['gain'] for r in revision if r['seed']==s)/2,rare_gain=sum(get(z,q,'rare','fast')['rare_loss']-get(z,q,'rare','combined')['rare_loss'] for z,q in pairs if z==s)/2) for s in sorted({s for s,q in pairs})]
    close(saved['environment_means'],env)

def main():
    out=ROOT/'results/memory-lifecycle-v1';started=time.monotonic()
    def timeout(*_):raise TimeoutError('900 second audit ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        result=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text());assert result['hashes']==manifest
        for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==15 and set(ws)==set(itertools.product(range(1900,1905),BRANCHES))
        for w in worlds:assert not w['small'];verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
        assert len(runs)==120 and {(r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs}==set(itertools.product(range(1900,1905),(1900,1901),BRANCHES,POLICIES))
        for i,r in enumerate(runs,1):
            with gzip.open(out/r['checkpoint_file'],'rt') as f:c=json.load(f)
            verify_run(r,ws[r['seed'],r['branch']],c)
            if i%20==0:print(f'{i}/120 independently reconstructed',flush=True)
        verify_summary(runs,result['summary']);total=totals(runs,worlds);close(result['totals'],total)
        for k,v in dict(used_labels=1228800,generated_labels=153600,main_predictions=737280,evaluation_predictions=125760,slow_probe_predictions=7200,legacy_auxiliary_predictions=5040).items():assert total[k]==v,(k,total[k])
        for k,v in dict(candidate_fits=200000,scoring_queries=15000000,raw_bin_visits=60000000,oracle_context_queries=800000).items():assert total[k]<=v
        assert result['elapsed_seconds']<900
        audit=dict(status='pass',runs=120,primary_pass=result['summary']['primary_pass'],elapsed_seconds=time.monotonic()-started,
            **{n+'_sha256':hashlib.sha256((out/f).read_bytes()).hexdigest() for n,f in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(audit)
    finally:signal.alarm(0)
if __name__=='__main__':main()
