"""Predeclared run measurements and paired architecture gates for 024/025."""
import math
from statistics import mean

BRANCHES = ('stable','probability','forms','detail','reversed')
WINDOWS = dict(whole=(0,1280), adapt1=(240,496), adapt2=(528,784), late=(1024,1280))


def full(e): return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10

def structure(e): return all(e['local_exact']) and e['sufficient_minimal']

def loss(p,y): return -math.log(p if y else 1-p)


def metrics(r,w,target,forms_at):
    observed = [loss(p,row['y']) for p,row in zip(r['predictions'],w['main'])]
    latent = []
    locals_ = [[],[]]
    for t,(p,row,lp) in enumerate(zip(r['predictions'],w['main'],r['local_predictions']),1):
        y = target(w,row['x'],row['a'],t)
        latent.append(.9*loss(p,y)+.1*loss(p,1-y))
        for j in range(2): locals_[j].append(loss(lp[j],row['local'][j]))
    result = dict(transfer_valid=full(r['transfer']), final_valid=full(r['evaluations'][-1]),
        structure_errors=sum(not structure(e) for e in r['evaluations'] if e['index']>=256),
        observed={k:mean(observed[a:b]) for k,(a,b) in WINDOWS.items()},
        latent={k:mean(latent[a:b]) for k,(a,b) in WINDOWS.items()},
        local_observed=[mean(xs) for xs in locals_], recovery=[],
        late_prediction_stable=all(full(e) for e in r['evaluations'] if e['index']>=1024),
        late_structure_stable=all(structure(e) for e in r['evaluations'] if e['index']>=1024),
        raw_reads=sum(r['raw_reads']), raw_bypass=sum(d['raw_bypass'] for d in r['diagnostics']),
        group_changes=sum(sum(d['group_changes']) for d in r['diagnostics']),
        partition_changes=sum(sum(d['partition_changes']) for d in r['diagnostics']))
    for a,b in ((256,512),(576,1280)):
        es=[e for e in r['evaluations'] if a<=e['index']<=b]
        result['recovery'].append(next((v['index'] for u,v in zip(es,es[1:]) if full(u) and full(v)),None))
    result['retrievals']=sum(v['upper']['action']=='retrieved' for v in r['reviews'])
    result['incompatible_archive']=sum(v['upper']['archive_check'] is not None and not v['upper']['archive_check']['compatible'] for v in r['reviews'])
    return result


def summarize(runs, candidate='R128', confirmation=False):
    lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs})
    policies=sorted({r['policy'] for r in runs})
    groups=[]
    for b in BRANCHES:
        for p in policies:
            ms=[lookup[s,q,b,p] for s,q in pairs]
            groups.append(dict(branch=b,policy=p,runs=len(ms),
                **{k:sum(m[k] for m in ms) for k in ('transfer_valid','final_valid','late_prediction_stable','late_structure_stable')},
                **{k:mean(m[k] for m in ms) for k in ('structure_errors','raw_reads','raw_bypass','group_changes','partition_changes','retrievals','incompatible_archive')},
                observed={k:mean(m['observed'][k] for m in ms) for k in WINDOWS},
                latent={k:mean(m['latent'][k] for m in ms) for k in WINDOWS},
                recovery_censored=[sum(m['recovery'][i] is None for m in ms) for i in range(2)]))
    contrasts=[(candidate,'U128')] if confirmation else [('B128','B64'),('U64','B64'),('U128','B128'),('U128','U64'),('R128','U128'),('H128','R128'),('R128','B64'),('H128','B64'),('H128','U128')]
    paired=[]
    for a,b in contrasts:
        for s,q in pairs:
            for history in BRANCHES:
                x,y=lookup[s,q,history,a],lookup[s,q,history,b]
                paired.append(dict(candidate=a,control=b,seed=s,proposal_seed=q,branch=history,
                    observed_cost={k:x['observed'][k]-y['observed'][k] for k in WINDOWS},
                    latent_cost={k:x['latent'][k]-y['latent'][k] for k in WINDOWS},
                    recovery_delay=[(x['recovery'][i] if x['recovery'][i] is not None else c)-(y['recovery'][i] if y['recovery'][i] is not None else c) for i,c in enumerate((592,1344))],
                    representation_gain=y['structure_errors']-x['structure_errors']))
    def valid(ps):
        return all(g[k]>=8 for g in groups if g['policy'] in ps for k in ('transfer_valid','final_valid'))
    def guard(p,controls):
        rows=[x for x in paired if x['candidate']==p and x['control'] in controls]
        assert len(rows)==len(controls)*len(pairs)*5
        mean_ok=all(mean(x[measure][k] for x in rows if x['branch']==h and x['control']==c)<=.02 for h in BRANCHES for c in controls for measure in ('observed_cost','latent_cost') for k in ('whole','adapt1','adapt2'))
        recovery_ok=all(mean(x['recovery_delay'][i] for x in rows if x['branch']==h and x['control']==c)<=64 for h in BRANCHES for c in controls for i in range(2))
        worst_ok=all(x['observed_cost'][k]<=.10 for x in rows for k in ('adapt1','adapt2'))
        return dict(mean_cost=mean_ok,recovery=recovery_ok,worst_pair=worst_ok)
    rep=[]
    for s,q in pairs:
        control=sum(lookup[s,q,h,'U128']['structure_errors'] for h in ('forms','detail'))
        value=sum(lookup[s,q,h,candidate]['structure_errors'] for h in ('forms','detail'))
        rep.append(dict(seed=s,proposal_seed=q,control_errors=control,candidate_errors=value,gain=control-value))
    total=sum(x['control_errors'] for x in rep); gain=sum(x['gain'] for x in rep)
    checks=dict(representation_reduction=total>0 and gain/total>=.25,
        representation_pairs=sum(x['gain']>0 for x in rep)>=8,
        validity=valid([candidate,'U128']),**guard(candidate,['U128'] if confirmation else ['U128','B64']))
    history_pairs=[]; history_checks=None
    if not confirmation:
        for s,q in pairs:
            gain=mean(lookup[s,q,h,'R128']['observed'][k]-lookup[s,q,h,'H128']['observed'][k] for h in BRANCHES[1:] for k in ('adapt1','adapt2'))
            history_pairs.append(dict(seed=s,proposal_seed=q,gain=gain))
        history_checks=dict(mean_gain=mean(p['gain'] for p in history_pairs)>=.02,
            positive_pairs=sum(p['gain']>0 for p in history_pairs)>=8,
            validity=valid(['H128','R128','U128','B64']),**guard('H128',['R128','U128','B64']))
    environment=[]
    for s in sorted({s for s,q in pairs}):
        for h in BRANCHES:
            for p in policies:
                ms=[lookup[z,q,h,p] for z,q in pairs if z==s]
                environment.append(dict(seed=s,branch=h,policy=p,
                    observed={k:mean(m['observed'][k] for m in ms) for k in WINDOWS},
                    structure_errors=mean(m['structure_errors'] for m in ms)))
    return dict(groups=groups,paired=paired,environment_means=environment,representation_pairs=rep,
        representation_fraction=None if not total else sum(x['gain'] for x in rep)/total,checks=checks,primary_pass=all(checks.values()),
        history_pairs=history_pairs,history_checks=history_checks,
        history_pass=history_checks is not None and all(history_checks.values()))
