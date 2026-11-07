"""035 prespecified windows and gates; no threshold selection from outcomes."""
import math
from statistics import mean
WINDOWS=dict(active=(513,1024),burst=(513,640),settled=(641,1024),early_return=(1025,1280),returning=(1025,1536),later=(1537,2048))
HISTORIES=('stable','forms','repeated','forms_persistent','repeated_persistent')
POLICIES=('P','D128','D256','D512','G')

def measure(r,w):
    from temporary_plasticity import forms_at,target
    values={'observed':[],'expected':[]}
    for t,(ps,row) in enumerate(zip(r['predictions'],w['main']),1):
        f=forms_at(w,t,True);truth=[f[j][row['x'][j]] for j in (0,1)]+[target(w,row['x'],row['a'],t)]
        values['observed'].append([-math.log(p if y else 1-p) for p,y in zip(ps,row['local']+[row['y']])])
        values['expected'].append([-.9*math.log(p if y else 1-p)-.1*math.log(1-p if y else p) for p,y in zip(ps,truth)])
    m={typ:{k:[mean(row[j] for row in rows[lo-1:hi]) for j in range(3)] for k,(lo,hi) in WINDOWS.items()} for typ,rows in values.items()}
    p=w['instruction']['protected'];s=r['checkpoint']['controller'];end=r['evaluations'][-1]
    m.update(protected=p,burst_correct=mean(e['local_exact'][p] for e in r['evaluations'] if 513<=e['tick']<=640),final_valid=end['valid'],final_local_exact=end['local_exact'],final_spec=end['spec'],closed_at=s['closed_at'],closure_reason=s['closure_reason'],duration=0 if s['closed_at'] is None else s['closed_at']-512)
    return m

def candidate(rs,policy):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in rs});d={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r['metrics'] for r in rs}
    guards=[];comparisons=[]
    for h in HISTORIES:
        for seed,ps in pairs:
            a=d[seed,ps,h,policy]
            comparisons.append(dict(seed=seed,proposal_seed=ps,history=h,active_gain_P=d[seed,ps,h,'P']['expected']['active'][2]-a['expected']['active'][2],early_gain_D512=d[seed,ps,h,'D512']['expected']['early_return'][2]-a['expected']['early_return'][2]))
        for control in ('P','D512'):
            for window in ('returning','later')+(('active',) if h=='stable' else ())+(('early_return',) if control=='P' and h in ('forms','repeated') else ()):
                for j in range(3):
                    xs=[d[s,q,h,policy]['expected'][window][j]-d[s,q,h,control]['expected'][window][j] for s,q in pairs]
                    guards.append(dict(history=h,control=control,window=window,channel=j,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02 and max(xs)<=.10))
    adaptation=[]
    for h in HISTORIES[1:]:
        xs=[d[s,q,h,policy]['expected']['active'][2]-d[s,q,h,'D512']['expected']['active'][2] for s,q in pairs]
        adaptation.append(dict(history=h,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02 and max(xs)<=.10))
    changed=[p for p in comparisons if p['history']!='stable'];returned=[p for p in comparisons if p['history'] in ('forms','repeated')]
    gates=dict(adaptation_preserved=all(x['passed'] for x in adaptation),active_gain=mean(p['active_gain_P'] for p in changed)>=.02,active_consistency=sum(p['active_gain_P']>1e-12 for p in changed)>=28,
               early_gain=mean(p['early_gain_D512'] for p in returned)>=.02,early_consistency=sum(p['early_gain_D512']>1e-12 for p in returned)>=14,
               each_return_improves=all(mean(p['early_gain_D512'] for p in returned if p['history']==h)>1e-12 for h in ('forms','repeated')),
               preservation=all(x['passed'] for x in guards),protection=all(mean(d[s,q,h,policy]['burst_correct'] for s,q in pairs)>=.95 for h in HISTORIES[1:]),final_validity=all(sum(d[s,q,h,policy]['final_valid'] for s,q in pairs)>=8 for h in HISTORIES))
    return dict(policy=policy,gates=gates,empirical_pass=all(gates.values()),adaptation_guards=adaptation,preservation_guards=guards,paired=comparisons,
                active_mean_gain=mean(p['active_gain_P'] for p in changed),active_positive=sum(p['active_gain_P']>1e-12 for p in changed),early_mean_gain=mean(p['early_gain_D512'] for p in returned),early_positive=sum(p['early_gain_D512']>1e-12 for p in returned),
                environment_means=[dict(seed=s,active_gain=mean(p['active_gain_P'] for p in changed if p['seed']==s),early_gain=mean(p['early_gain_D512'] for p in returned if p['seed']==s)) for s in sorted({p['seed'] for p in changed})])

def summarize(rs):
    groups=[]
    for h in HISTORIES:
        for p in POLICIES:
            ms=[r['metrics'] for r in rs if (r['history'],r['policy'])==(h,p)]
            groups.append(dict(history=h,policy=p,burst_correct=mean(m['burst_correct'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),final_raw_interface=sum(2 in m['final_spec'] for m in ms),mean_duration=mean(m['duration'] for m in ms),closure_counts={('null' if reason is None else reason):sum(m['closure_reason']==reason for m in ms) for reason in (None,'fixed','adequate','ceiling')},
                **{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed')}))
    direct=[]
    for h in HISTORIES:
        for p in ('D128','D256'):
            a=next(g for g in groups if (g['history'],g['policy'])==(h,'G'));b=next(g for g in groups if (g['history'],g['policy'])==(h,p))
            direct.append(dict(history=h,control=p,gain={k:b['expected'][k][2]-a['expected'][k][2] for k in WINDOWS}))
    return dict(primary=candidate(rs,'G'),secondary={p:candidate(rs,p) for p in ('D128','D256')},groups=groups,G_vs_fixed=direct)
