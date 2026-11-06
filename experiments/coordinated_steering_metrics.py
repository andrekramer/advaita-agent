"""034 factorial comparisons with fixed preservation and validity guards."""
from statistics import mean
from selective_steering_metrics import WINDOWS
POLICIES=('U','P','L','D','C')
COMPARISONS={'C_vs_D':('D','C'),'C_vs_L':('L','C'),'C_vs_U':('U','C'),'D_vs_P':('P','D'),'L_vs_P':('P','L'),'C_vs_P':('P','C')}

def summarize(rs):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in rs});d={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r['metrics'] for r in rs};groups=[];paired=[]
    for h in ('stable','forms','repeated'):
        for policy in POLICIES:
            ms=[d[s,q,h,policy] for s,q in pairs]
            groups.append(dict(history=h,policy=policy,burst_correct=mean(m['burst_correct'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),final_local_correct=[sum(m['final_local_exact'][j] for m in ms) for j in range(2)],final_raw_interface=sum(2 in m['final_spec'] for m in ms),
                **{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed')}))
        for s,q in pairs:
            get=lambda p:d[s,q,h,p]
            gains={name:get(a)['expected']['active'][2]-get(b)['expected']['active'][2] for name,(a,b) in COMPARISONS.items()}
            observed={name:get(a)['observed']['active'][2]-get(b)['observed']['active'][2] for name,(a,b) in COMPARISONS.items()}
            paired.append(dict(seed=s,proposal_seed=q,history=h,gains=gains,observed_gains=observed,interaction=gains['C_vs_D']-gains['L_vs_P'],
                costs={p:{k:[get('C')['expected'][k][j]-get(p)['expected'][k][j] for j in range(3)] for k in WINDOWS} for p in ('U','D')}))
    changed=[r for r in paired if r['history']!='stable'];group=lambda h,p:next(g for g in groups if g['history']==h and g['policy']==p)
    gates=dict(protection=all(group(h,p)['burst_correct']>=.95 for h in ('forms','repeated') for p in ('P','L','D','C')))
    for name in ('C_vs_D','C_vs_L','C_vs_U'):
        xs=[r['gains'][name] for r in changed];gates[name+'_mean']=mean(xs)>=.005;gates[name+'_consistency']=sum(x>1e-12 for x in xs)>=12
    guards=[]
    for h in ('stable','forms','repeated'):
        for control in ('U','D'):
            for window in ('returning','later')+(('active',) if h=='stable' else ()):
                for j in range(3):
                    xs=[r['costs'][control][window][j] for r in paired if r['history']==h]
                    guards.append(dict(history=h,control=control,window=window,channel=j,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02 and max(xs)<=.10))
            if h!='stable':
                xs=[r['costs'][control]['active'][2] for r in paired if r['history']==h]
                guards.append(dict(history=h,control=control,window='active',channel=2,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02))
    gates['preservation']=all(g['passed'] for g in guards);gates['final_validity']=all(group(h,'C')['final_valid']>=8 for h in ('stable','forms','repeated'))
    interactions=[r['interaction'] for r in changed]
    return dict(groups=groups,paired=paired,guards=guards,gates=gates,empirical_pass=all(gates.values()),
        incremental_pass=gates['C_vs_D_mean'] and gates['C_vs_D_consistency'],interaction_mean=mean(interactions),interaction_positive=sum(x>1e-12 for x in interactions),interaction_pass=mean(interactions)>=.005 and sum(x>1e-12 for x in interactions)>=12,
        environment_means=[dict(seed=s,**{name:mean(r['gains'][name] for r in changed if r['seed']==s) for name in COMPARISONS},interaction=mean(r['interaction'] for r in changed if r['seed']==s)) for s in sorted({r['seed'] for r in changed})])
