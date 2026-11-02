"""030 fixed lifecycle measurements and paired decision."""
import math
from statistics import mean
BRANCHES=('repeated','forms','rare');POLICIES=('baseline','fast','relaxed','combined')
WINDOWS=dict(whole=[(1,2048)],initial=[(1,512)],settled=[(641,1024),(1153,1536),(1665,2048)],early=[(513,640),(1025,1152),(1537,1664)],rare=[(513,1536)],returning=[(1537,2048)])
def good(e):return all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10
def nll(p,y):return -math.log(p if y else 1-p)
def metrics(r,w,target,forms_at):
    obs=[];latent=[]
    for t,(ps,row) in enumerate(zip(r['predictions'],w['main']),1):
        y=target(w,row['x'],row['a'],t);obs.append((t,nll(ps[2],row['y'])));latent.append((t,.9*nll(ps[2],y)+.1*nll(ps[2],1-y)))
    result={name:{k:mean(v for t,v in rows if any(a<=t<=b for a,b in intervals)) for k,intervals in WINDOWS.items()} for name,rows in [('observed',obs),('latent',latent)]}
    ev={e['index']:e for e in r['evaluations']};rare=[]
    for i,p in enumerate(ev[1536]['predictions']):
        x=[i//8,i//2%4];a=i%2
        if w['forms'][w['affected']][x[w['affected']]]:
            y=target(w,x,a,1536);rare.append(.9*nll(p,y)+.1*nll(p,1-y))
    result.update(endpoint_valid=[good(ev[t]) for t in (512,1024,1536,2048)],final_valid=good(ev[2048]),rare_loss=mean(rare),
        structure_errors=sum(not(all(e['local_exact']) and e['sufficient_minimal']) for e in ev.values()),
        weakenings=r['costs'].get('weakenings',0),transfers=r['costs'].get('transfers',0))
    return result

def summarize(runs):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    def m(s,q,h,p):return lookup[s,q,h,p]
    groups=[]
    for h in BRANCHES:
        for p in POLICIES:
            ms=[m(s,q,h,p) for s,q in pairs]
            groups.append(dict(branch=h,policy=p,final_valid=sum(x['final_valid'] for x in ms),endpoint_valid=[sum(x['endpoint_valid'][i] for x in ms) for i in range(4)],
                rare_loss=mean(x['rare_loss'] for x in ms),structure_errors=mean(x['structure_errors'] for x in ms),weakenings=sum(x['weakenings'] for x in ms),transfers=sum(x['transfers'] for x in ms),
                **{n:{k:mean(x[n][k] for x in ms) for k in WINDOWS} for n in ('observed','latent')}))
    paired=[]
    for control in ('relaxed','fast','baseline'):
        for s,q in pairs:
            for h in BRANCHES:
                a,b=m(s,q,h,'combined'),m(s,q,h,control)
                paired.append(dict(seed=s,proposal_seed=q,branch=h,control=control,rare_gain=b['rare_loss']-a['rare_loss'],
                    **{n+'_cost':{k:a[n][k]-b[n][k] for k in WINDOWS} for n in ('observed','latent')}))
    revision=[dict(seed=s,proposal_seed=q,gain=mean(m(s,q,h,'relaxed')['observed']['settled']-m(s,q,h,'combined')['observed']['settled'] for h in ('repeated','forms'))) for s,q in pairs]
    rare=[m(s,q,'rare','fast')['rare_loss']-m(s,q,'rare','combined')['rare_loss'] for s,q in pairs]
    preserve=[r for r in paired if r['control'] in ('relaxed','baseline')]
    cases=lambda r:['initial','whole','returning'] if r['branch']=='rare' else ['initial']
    revision_rows=[r for r in paired if r['control']=='relaxed' and r['branch']!='rare']
    gates=dict(revision_gain=mean(x['gain'] for x in revision)>=.02,revision_pairs=sum(x['gain']>0 for x in revision)>=8,
        final_validity=all(g['final_valid']>=8 for g in groups if g['policy']=='combined'),rare_gain=mean(rare)>=.02,rare_pairs=sum(x>0 for x in rare)>=8,
        preservation_mean=all(mean(r[n+'_cost'][k] for r in preserve if r['control']==c and r['branch']==h)<=.02 for c in ('relaxed','baseline') for h in BRANCHES for k in (['initial','whole','returning'] if h=='rare' else ['initial']) for n in ('observed','latent')),
        preservation_worst=all(r['observed_cost'][k]<=.10 for r in preserve for k in cases(r)),
        revision_mean=all(mean(r[n+'_cost'][k] for r in revision_rows if r['branch']==h)<=.02 for h in ('repeated','forms') for k in ('early','settled') for n in ('observed','latent')),
        revision_worst=all(r['observed_cost'][k]<=.10 for r in revision_rows for k in ('early','settled')))
    environments=[dict(seed=s,revision_gain=mean(r['gain'] for r in revision if r['seed']==s),rare_gain=mean(m(z,q,'rare','fast')['rare_loss']-m(z,q,'rare','combined')['rare_loss'] for z,q in pairs if z==s)) for s in sorted({s for s,q in pairs})]
    return dict(groups=groups,paired=paired,revision_pairs=revision,rare_gains=rare,environment_means=environments,gates=gates,primary_pass=all(gates.values()))
