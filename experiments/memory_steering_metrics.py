"""031 fixed future-outcome utility and unaffected-channel costs."""
import math
from statistics import mean
from memory_lifecycle import target
WINDOWS={'whole':(1,2048),'early':(513,576),'benefit':(577,1024),'returning':(1025,1536),'later':(1537,2048)}
def loss(p,y):return -math.log(p if y else 1-p)
def metrics(r,w):
    records={'observed':[],'latent':[],'unaffected':[]};j=1-w['affected']
    for t,(row,ps) in enumerate(zip(w['main'],r['predictions']),1):
        y=target(w,row['x'],row['a'],t);records['observed'].append((t,loss(ps[2],row['y'])));records['latent'].append((t,.9*loss(ps[2],y)+.1*loss(ps[2],1-y)))
        records['unaffected'].append((t,loss(ps[j],row['local'][j])))
    m={n:{k:mean(v for t,v in seq if lo<=t<=hi) for k,(lo,hi) in WINDOWS.items()} for n,seq in records.items()};e=r['evaluations'][-1]
    m.update(final_valid=all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10,trigger=r['trigger'],controlled=r['control'] is not None)
    return m

def summarize(runs):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});get={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    groups=[]
    for h in ('stable','repeated'):
        for p in ('unsteered','targeted','rotated'):
            ms=[get[s,q,h,p] for s,q in pairs]
            groups.append(dict(branch=h,policy=p,final_valid=sum(m['final_valid'] for m in ms),triggers=sum(m['trigger'] is not None for m in ms),controls=sum(m['controlled'] for m in ms),
                **{n:{k:mean(m[n][k] for m in ms) for k in WINDOWS} for n in ('observed','latent','unaffected')}))
    paired=[]
    for c in ('unsteered','rotated'):
        for s,q in pairs:
            for h in ('stable','repeated'):
                a,b=get[s,q,h,'targeted'],get[s,q,h,c]
                paired.append(dict(seed=s,proposal_seed=q,branch=h,control=c,**{n+'_cost':{k:a[n][k]-b[n][k] for k in WINDOWS} for n in ('observed','latent','unaffected')}))
    gains=[dict(seed=s,proposal_seed=q,gain=get[s,q,'repeated','unsteered']['observed']['benefit']-get[s,q,'repeated','targeted']['observed']['benefit']) for s,q in pairs]
    specificity=[get[s,q,'repeated','rotated']['observed']['benefit']-get[s,q,'repeated','targeted']['observed']['benefit'] for s,q in pairs]
    controlrows=[r for r in paired if r['control']=='unsteered']
    cases=[('stable','whole'),('repeated','early'),('repeated','returning'),('repeated','later')]
    gates=dict(benefit=mean(r['gain'] for r in gains)>=.01,benefit_pairs=sum(r['gain']>0 for r in gains)>=8,
        specificity=mean(specificity)>=.01,specificity_pairs=sum(x>0 for x in specificity)>=8,
        final_validity=all(g['final_valid']>=8 for g in groups if g['policy']=='targeted'),
        cost_mean=all(mean(r[n+'_cost'][k] for r in controlrows if r['branch']==h)<=.02 for h,k in cases for n in ('observed','latent')),
        cost_worst=all(r['observed_cost'][k]<=.10 for h,k in cases for r in controlrows if r['branch']==h),
        unaffected_mean=all(mean(r['unaffected_cost']['whole'] for r in controlrows if r['branch']==h)<=.02 for h in ('stable','repeated')),
        unaffected_worst=all(r['unaffected_cost']['whole']<=.10 for r in controlrows))
    return dict(groups=groups,paired=paired,gains=gains,specificity_gains=specificity,gates=gates,primary_pass=all(gates.values()),
        environment_means=[dict(seed=s,gain=mean(r['gain'] for r in gains if r['seed']==s)) for s in sorted({s for s,q in pairs})])
