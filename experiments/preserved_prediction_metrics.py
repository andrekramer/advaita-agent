"""036 recall utility and collateral guards, fixed before fresh generation."""
import math
from statistics import mean
HISTORIES=('stable','forms','repeated','forms_persistent','repeated_persistent','forms_other')
POLICIES=('discard','shadow','recall')
WINDOWS=dict(active=(513,1024),early_return=(1025,1280),returning=(1025,1536),later=(1537,2048))

def measure(r,w):
    from preserved_prediction import forms_at,target
    values={'expected':[],'observed':[],'active_expected':[]}
    for t,(ps,row) in enumerate(zip(r['predictions'],w['main']),1):
        f=forms_at(w,t,True);ys=[f[j][row['x'][j]] for j in (0,1)]+[target(w,row['x'],row['a'],t)]
        nll=lambda p,y:-math.log(p if y else 1-p)
        values['expected'].append([.9*nll(p,y)+.1*nll(p,1-y) for p,y in zip(ps,ys)])
        values['active_expected'].append([.9*nll(p,y)+.1*nll(p,1-y) for p,y in zip(r['active_predictions'][t-1],ys)])
        values['observed'].append([nll(p,y) for p,y in zip(ps,row['local']+[row['y']])])
    m={typ:{k:[mean(v[j] for v in rows[lo-1:hi]) for j in range(3)] for k,(lo,hi) in WINDOWS.items()} for typ,rows in values.items()}
    state=r['checkpoint']['memory'];end=r['evaluations'][-1]
    m.update(confirmed=state['confirmed'],retained=state['slot'] is not None,uses=state['prediction_uses'],blocked=state['blocked_predictions'],admitted_reviews=sum(e['admitted'] for e in r['memory_events']),eligible_reviews=sum(e['eligible'] for e in r['memory_events']),final_valid=end['valid'],active_final_valid=end['active']['valid'],final_spec=end['spec'],uses_by_window={k:sum(e['source']=='archive' for e in r['prediction_events'][lo-1:hi]) for k,(lo,hi) in WINDOWS.items()})
    return m

def summarize(rs):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in rs});lookup={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r for r in rs};groups=[];paired=[];guards=[]
    for h in HISTORIES:
        for policy in POLICIES:
            ms=[lookup[s,q,h,policy]['metrics'] for s,q in pairs]
            groups.append(dict(history=h,policy=policy,confirmed=sum(m['confirmed'] for m in ms),retained=sum(m['retained'] for m in ms),uses=sum(m['uses'] for m in ms),blocked=sum(m['blocked'] for m in ms),eligible_reviews=sum(m['eligible_reviews'] for m in ms),admitted_reviews=sum(m['admitted_reviews'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),active_final_valid=sum(m['active_final_valid'] for m in ms),**{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed','active_expected')}))
        for s,q in pairs:
            a=lookup[s,q,h,'recall']['metrics'];b=lookup[s,q,h,'shadow']['metrics']
            paired.append(dict(seed=s,proposal_seed=q,history=h,gain={k:b['expected'][k][2]-a['expected'][k][2] for k in WINDOWS},observed_gain={k:b['observed'][k][2]-a['observed'][k][2] for k in WINDOWS},costs={k:[a['expected'][k][j]-b['expected'][k][j] for j in range(3)] for k in WINDOWS},uses=a['uses'],confirmed=a['confirmed']))
        for k in WINDOWS:
            for j in range(3):
                xs=[r['costs'][k][j] for r in paired if r['history']==h]
                guards.append(dict(history=h,window=k,channel=j,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02 and max(xs)<=.10))
    returned=[p for p in paired if p['history'] in ('forms','repeated')]
    parity=all(lookup[s,q,h,'discard']['predictions']==lookup[s,q,h,'shadow']['predictions'] and all(lookup[s,q,h,p]['active_predictions']==lookup[s,q,h,'discard']['active_predictions'] and lookup[s,q,h,p]['reviews']==lookup[s,q,h,'discard']['reviews'] for p in POLICIES) for h in HISTORIES for s,q in pairs)
    gates=dict(mean_recall_gain=mean(p['gain']['early_return'] for p in returned)>=.02,recall_consistency=sum(p['gain']['early_return']>1e-12 for p in returned)>=14,each_return_improves=all(mean(p['gain']['early_return'] for p in returned if p['history']==h)>1e-12 for h in ('forms','repeated')),preservation=all(g['passed'] for g in guards),final_validity=all(g['final_valid']>=8 and g['active_final_valid']>=8 for g in groups if g['policy']=='recall'),control_parity=parity)
    return dict(gates=gates,empirical_pass=all(gates.values()),groups=groups,paired=paired,guards=guards,mean_gain=mean(p['gain']['early_return'] for p in returned),positive=sum(p['gain']['early_return']>1e-12 for p in returned),environment_means=[dict(seed=s,gain=mean(p['gain']['early_return'] for p in returned if p['seed']==s)) for s in sorted({p['seed'] for p in returned})])
