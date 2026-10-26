"""021 fixed memory benefit and outdated-memory cost criteria."""
import math
from statistics import mean

from structural_consolidation_metrics import bit, desired, valid

BRANCHES = ('detail', 'reversed')
POLICIES = ('legacy', 'reserve', 'discard')
WINDOWS = dict(pre=(0,528), early=(528,656), returned=(528,1280), late=(1024,1280))


def metrics(r, w):
    observed, latent = [], []
    for t, (p,row) in enumerate(zip(r['predictions'],w['main']),1):
        observed.append(-math.log(p if row['y'] else 1-p))
        q=.9 if bit(w,row,t) else .1
        latent.append(-q*math.log(p)-(1-q)*math.log1p(-p))
    tail=[v['evaluation'] for v in r['reviews'] if v['index']>=1024]
    assert len(tail)==5
    captures, retrievals, incompatible = [], [], []
    for v in r['reviews']:
        u=v['upper']; ordinary=u.get('ordinary',u)
        if ordinary['action']=='retrieved': retrievals.append(v['index'])
        if ordinary['archive_check'] is not None and not ordinary['archive_check']['compatible']:
            incompatible.append(v['index'])
        snapshot, nominated, retained = None, None, True
        if r['policy']=='legacy':
            if ordinary['captured'] is not None: snapshot=ordinary['archive_after']
        elif u['qualification']['confirmed'] is not None:
            snapshot=u['qualification']['confirmed']
            nominated=u['qualification']['witness']['snapshot']['capture_event']
            retained=r['policy']=='reserve'
        if snapshot is not None:
            ids=snapshot['record_ids']
            main=[int(i.split('/')[1]) for i in ids if i.startswith('main/')]
            captures.append(dict(index=v['index'],nominated=nominated,retained=retained,
                main_first=min(main) if main else None,main_last=max(main) if main else None,
                construction_labels=len(ids),contains_pre_simplification=any(i<=240 for i in main) or any(i.startswith('composition/') for i in ids)))
    result=dict(transfer_valid=valid(r['transfer']),final_full=valid(tail[-1]),
        stable_full=all(valid(e) for e in tail),
        stable_structure=valid(r['transfer']) and all(valid(e) and e['spec']==desired(w,e['index']) and e['sufficient_minimal'] for e in tail),
        raw_reads=sum(r['raw_reads']),captures=captures,retrievals=retrievals,incompatible=incompatible)
    for name,(start,stop) in WINDOWS.items():
        result[name+'_observed']=mean(observed[start:stop])
        result[name+'_latent']=mean(latent[start:stop])
    return result


def summarize(runs):
    groups=[]
    for b in BRANCHES:
        for p in POLICIES:
            rs=[r for r in runs if (r['branch'],r['policy'])==(b,p)]
            assert len(rs)==10
            ms=[r['metrics'] for r in rs]
            g=dict(branch=b,policy=p,runs=10)
            for k in ('transfer_valid','final_full','stable_full','stable_structure'):
                g[k]=sum(m[k] for m in ms)
            for k in ('raw_reads',*(n+'_'+kind for n in WINDOWS for kind in ('observed','latent'))):
                g[k]=mean(m[k] for m in ms)
            for k in ('captures','retrievals','incompatible'): g[k]=sum(len(m[k]) for m in ms)
            g['pre_simplification_captures']=sum(c['contains_pre_simplification'] for m in ms for c in m['captures'])
            g['early_confirmations']=sum(any(c['index']<=240 for c in m['captures']) for m in ms)
            g['qualification_queries']=sum(r['memory_costs']['qualification_queries'] for r in rs if r['memory_costs'] is not None)
            groups.append(g)
    pairs=[]
    for s,ps,b in sorted({(r['seed'],r['proposal_seed'],r['branch']) for r in runs}):
        rs={r['policy']:r for r in runs if (r['seed'],r['proposal_seed'],r['branch'])==(s,ps,b)}
        a=rs['reserve']['metrics']
        for control in ('discard','legacy'):
            c=rs[control]['metrics']
            pairs.append(dict(seed=s,proposal_seed=ps,branch=b,control=control,
                identical_predictions=rs['reserve']['predictions']==rs[control]['predictions'],
                **{n+'_'+kind+'_gain':c[n+'_'+kind]-a[n+'_'+kind] for n in WINDOWS for kind in ('observed','latent')}))
    checks={}
    for b in BRANCHES:
        checks[b+'_final']=all(g['final_full']>=8 for g in groups if g['branch']==b)
    for control in ('discard','legacy'):
        ds=[p for p in pairs if p['branch']=='detail' and p['control']==control]
        rev=[p for p in pairs if p['branch']=='reversed' and p['control']==control]
        checks[control+'_early_gain']=mean(p['early_observed_gain'] for p in ds)>=.02
        checks[control+'_improving_pairs']=sum(p['early_observed_gain']>0 for p in ds)>=8
        checks[control+'_reversed_cost']=-mean(p['early_observed_gain'] for p in rev)<=.02
        for b in BRANCHES:
            for kind in ('observed','latent'):
                checks[control+'_'+b+'_pre_'+kind]=-mean(p['pre_'+kind+'_gain'] for p in pairs if p['branch']==b and p['control']==control)<=.02
    env=[]
    for s,b,c in sorted({(p['seed'],p['branch'],p['control']) for p in pairs}):
        ps=[p for p in pairs if (p['seed'],p['branch'],p['control'])==(s,b,c)]
        env.append(dict(seed=s,branch=b,control=c,proposals=len(ps),early_gain=mean(p['early_observed_gain'] for p in ps),
            early_latent_gain=mean(p['early_latent_gain'] for p in ps)))
    return dict(groups=groups,paired=pairs,environments=env,checks=checks,primary_pass=all(checks.values()))
