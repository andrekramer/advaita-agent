"""026 predeclared predictive, structural and paired memory-control measurements."""
import math
from statistics import mean
BRANCHES=('stable','burst','return','reversal','remap')
POLICIES=('baseline','fast','slow','always','selective','permanent','activity')
WINDOWS=dict(whole=(1,1280),early=(769,896),late=(1153,1280),burst=(257,320),recovery=(321,448))
CASES=(('stable','whole'),('burst','burst'),('burst','recovery'),('reversal','early'),('remap','early'))

def good(e):return all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10
def loss(p,y):return -math.log(p if y else 1-p)
def avg(xs):return mean(xs) if xs else None

def metrics(r,w,target,forms_at):
    observed=[];latent=[];local=[[],[]]
    for t,(ps,row) in enumerate(zip(r['predictions'],w['main']),1):
        if row is None:continue
        p=ps[2];y=target(w,row['x'],row['a'],t)
        observed.append((t,loss(p,row['y'])));latent.append((t,.9*loss(p,y)+.1*loss(p,1-y)))
        for j in (0,1):local[j].append(loss(ps[j],row['local'][j]))
    e={v['index']:v for v in r['evaluations']}
    recovery=next((v for u,v in zip(range(832,1280,64),range(896,1281,64)) if good(e[u]) and good(e[v])),None)
    return dict(observed={k:avg([v for t,v in observed if a<=t<=b]) for k,(a,b) in WINDOWS.items()},
        latent={k:avg([v for t,v in latent if a<=t<=b]) for k,(a,b) in WINDOWS.items()},local_loss=[mean(v) for v in local],
        transfer_valid=good(r['transfer']),final_valid=good(e[1280]),gap_valid=good(e[768]),gap_loss=e[768]['expected_loss'],
        recovery=recovery,structure_errors=sum(not(all(v['local_exact']) and v['sufficient_minimal']) for v in e.values()),
        final_structure=all(e[1280]['local_exact']) and e[1280]['sufficient_minimal'],
        transfers=sum(m['accepted'] for v in r['reviews'] for m in v['migrations']),
        proposals=r['costs'].get('proposals',0),transferred_mass=r['costs'].get('transferred_mass',0),
        group_changes=0 if r['policy']=='baseline' else sum(v['channels'][j]['before']['groups']!=v['channels'][j]['after']['groups'] for v in r['reviews'] for j in (0,1)))


def summarize(runs):
    lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});groups=[]
    for h in BRANCHES:
        for p in POLICIES:
            ms=[lookup[s,q,h,p] for s,q in pairs]
            groups.append(dict(branch=h,policy=p,runs=len(ms),**{k:sum(m[k] for m in ms) for k in ('transfer_valid','final_valid','gap_valid','final_structure')},
                **{k:mean(m[k] for m in ms) for k in ('gap_loss','structure_errors','transfers','proposals','transferred_mass','group_changes')},
                observed={k:avg([m['observed'][k] for m in ms if m['observed'][k] is not None]) for k in WINDOWS},
                latent={k:avg([m['latent'][k] for m in ms if m['latent'][k] is not None]) for k in WINDOWS},
                recovery_censored=sum(m['recovery'] is None for m in ms)))
    contrasts=[('selective',c) for c in ('fast','baseline','always','slow')]+[('permanent','selective'),('activity','selective'),('always','fast'),('slow','fast')]
    paired=[]
    for a,b in contrasts:
        for s,q in pairs:
            for h in BRANCHES:
                x,y=lookup[s,q,h,a],lookup[s,q,h,b]
                paired.append(dict(candidate=a,control=b,seed=s,proposal_seed=q,branch=h,
                    observed_cost={k:None if x['observed'][k] is None else x['observed'][k]-y['observed'][k] for k in WINDOWS},
                    latent_cost={k:None if x['latent'][k] is None else x['latent'][k]-y['latent'][k] for k in WINDOWS},
                    gap_cost=x['gap_loss']-y['gap_loss'],recovery_delay=(x['recovery'] or 1344)-(y['recovery'] or 1344)))
    def rows(control,h):return [p for p in paired if p['candidate']=='selective' and p['control']==control and p['branch']==h]
    def guard(controls):
        mean_ok=all(mean(p[measure][window] for p in rows(c,h))<=.02 for c in controls for h,window in CASES for measure in ('observed_cost','latent_cost'))
        worst=all(p['observed_cost'][window]<=.10 for c in controls for h,window in CASES for p in rows(c,h))
        recovery=all(mean(p['recovery_delay'] for p in rows(c,h))<=64 for c in controls for h in ('reversal','remap'))
        return dict(mean_cost=mean_ok,worst_pair=worst,recovery=recovery)
    return_rows=rows('fast','return')
    selection=[];revision=[]
    for s,q in pairs:
        selection.append(dict(seed=s,proposal_seed=q,gain=mean(lookup[s,q,h,'always']['observed'][k]-lookup[s,q,h,'selective']['observed'][k] for h,k in (('burst','recovery'),('reversal','early'),('remap','early')))))
        revision.append(dict(seed=s,proposal_seed=q,gain=mean(lookup[s,q,h,'slow']['observed']['early']-lookup[s,q,h,'selective']['observed']['early'] for h in ('reversal','remap'))))
    guards=guard(('fast','baseline'));selection_guards=guard(('always',));slow_guards=guard(('slow',))
    gates=dict(return_mean_gain=-mean(p['observed_cost']['early'] for p in return_rows)>=.02,
        return_pairs=sum(p['observed_cost']['early']<0 for p in return_rows)>=8,
        gap_gain=-mean(p['gap_cost'] for p in return_rows)>=.02,
        gap_validity=next(g['gap_valid'] for g in groups if g['branch']=='return' and g['policy']=='selective')>=8,
        final_validity=all(g['final_valid']>=8 for g in groups if g['policy']=='selective'),
        **guards,selection_mean_gain=mean(p['gain'] for p in selection)>=.01,selection_pairs=sum(p['gain']>0 for p in selection)>=8,
        **{'selection_'+k:v for k,v in selection_guards.items()})
    dual=dict(return_noninferiority=mean(p['observed_cost']['early'] for p in rows('slow','return'))<=.02,
        revision_mean_gain=mean(p['gain'] for p in revision)>=.02,revision_pairs=sum(p['gain']>0 for p in revision)>=8,**slow_guards)
    environment=[]
    for s in sorted({s for s,q in pairs}):
        for h in BRANCHES:
            for p in POLICIES:
                ms=[lookup[z,q,h,p] for z,q in pairs if z==s]
                environment.append(dict(seed=s,branch=h,policy=p,whole_loss=mean(m['observed']['whole'] for m in ms),early_loss=mean(m['observed']['early'] for m in ms),gap_loss=mean(m['gap_loss'] for m in ms)))
    return dict(groups=groups,paired=paired,environment_means=environment,selection_pairs=selection,revision_pairs=revision,
        gates=gates,primary_pass=all(gates.values()),dual_store_gates=dual,dual_store_pass=all(dual.values()))
