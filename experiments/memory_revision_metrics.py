"""027 predeclared summaries; unchanged per-run measures come from 026."""
from statistics import mean
from memory_control_metrics import BRANCHES,WINDOWS
POLICIES=('baseline','fast','selective','relaxed','weaken','combined','uniform')
CONTRASTS=(('combined','relaxed'),('weaken','selective'),('combined','selective'),('relaxed','selective'),
           ('combined','uniform'),('combined','fast'),('combined','baseline'))
PRESERVE=(('stable','whole'),('return','early'),('burst','burst'),('burst','recovery'))


def summarize(runs):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs})
    table={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r for r in runs}
    def m(s,q,h,p):return table[s,q,h,p]['metrics']
    groups=[]
    for h in BRANCHES:
        for p in POLICIES:
            rs=[table[s,q,h,p] for s,q in pairs];ms=[r['metrics'] for r in rs]
            group=dict(branch=h,policy=p,runs=len(rs))
            for k in ('transfer_valid','final_valid','gap_valid','final_structure'):group[k]=sum(x[k] for x in ms)
            for k in ('gap_loss','structure_errors','transfers','transferred_mass'):group[k]=mean(x[k] for x in ms)
            for name in ('observed','latent'):
                group[name]={k:mean(v) if (v:=[x[name][k] for x in ms if x[name][k] is not None]) else None for k in WINDOWS}
            group['recovery_censored']=sum(x['recovery'] is None for x in ms)
            group['recoveries']=[x['recovery'] for x in ms]
            group['weakenings']=sum(r['costs'].get('weakenings',0) for r in rs)
            group['removed_mass']=sum(r['costs'].get('removed_mass',0) for r in rs)
            groups.append(group)
    paired=[]
    for a,b in CONTRASTS:
        for s,q in pairs:
            for h in BRANCHES:
                x,y=m(s,q,h,a),m(s,q,h,b)
                paired.append(dict(candidate=a,control=b,seed=s,proposal_seed=q,branch=h,gap_cost=x['gap_loss']-y['gap_loss'],
                    **{name+'_cost':{k:x[name][k]-y[name][k] if x[name][k] is not None else None for k in WINDOWS} for name in ('observed','latent')}))
    def costs(c,h,k,name='observed'):
        return [m(s,q,h,'combined')[name][k]-m(s,q,h,c)[name][k] for s,q in pairs]
    revision=[dict(seed=s,proposal_seed=q,gain=mean(m(s,q,h,'relaxed')['observed']['early']-m(s,q,h,'combined')['observed']['early'] for h in ('reversal','remap'))) for s,q in pairs]
    selection=[dict(seed=s,proposal_seed=q,gain=mean(m(s,q,h,'uniform')['observed'][k]-m(s,q,h,'combined')['observed'][k] for h,k in (('stable','whole'),('return','early'),('burst','recovery')))) for s,q in pairs]
    gates=dict(revision_gain=mean(x['gain'] for x in revision)>=.02,revision_pairs=sum(x['gain']>0 for x in revision)>=8,
        final_validity=all(sum(m(s,q,h,'combined')['final_valid'] for s,q in pairs)>=8 for h in BRANCHES),
        gap_validity=sum(m(s,q,'return','combined')['gap_valid'] for s,q in pairs)>=8,
        preservation_mean=all(mean(costs(c,h,k,n))<=.02 for c in ('selective','relaxed') for h,k in PRESERVE for n in ('observed','latent')),
        preservation_worst=all(max(costs(c,h,k))<=.10 for c in ('selective','relaxed') for h,k in PRESERVE),
        gap_cost=all(mean(m(s,q,'return','combined')['gap_loss']-m(s,q,'return',c)['gap_loss'] for s,q in pairs)<=.02 for c in ('selective','relaxed')),
        revision_mean_cost=all(mean(costs('relaxed',h,'early',n))<=.02 for h in ('reversal','remap') for n in ('observed','latent')),
        revision_worst=all(max(costs('relaxed',h,'early'))<=.10 for h in ('reversal','remap')),
        recovery_censoring=all(sum(m(s,q,h,'combined')['recovery'] is None for s,q in pairs)<=sum(m(s,q,h,'relaxed')['recovery'] is None for s,q in pairs) for h in ('reversal','remap')))
    selectivity=dict(mean_gain=mean(x['gain'] for x in selection)>=.01,positive_pairs=sum(x['gain']>0 for x in selection)>=8)
    environments=[dict(seed=s,branch=h,policy=p,whole_loss=mean(m(s,q,h,p)['observed']['whole'] for z,q in pairs if z==s),
        early_loss=mean(m(s,q,h,p)['observed']['early'] for z,q in pairs if z==s)) for s in sorted({s for s,q in pairs}) for h in BRANCHES for p in POLICIES]
    return dict(groups=groups,paired=paired,environment_means=environments,revision_pairs=revision,selection_pairs=selection,
        gates=gates,primary_pass=all(gates.values()),selectivity_gates=selectivity,selectivity_pass=all(selectivity.values()))
