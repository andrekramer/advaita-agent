"""037 intervention utility, retained recall and collateral costs."""
import types
from statistics import mean
import preserved_prediction_metrics as previous
HISTORIES=previous.HISTORIES
POLICIES=('shadow','current','command','evidence')
WINDOWS=dict(previous.WINDOWS,rechange=(1537,1600))
_measure=types.FunctionType(previous.measure.__code__,dict(previous.measure.__globals__,WINDOWS=WINDOWS))

def measure(r,w):
    m=_measure(r,w);s=r['checkpoint']['steering']
    m.update(withdrawals=s['withdrawals'],commands=len(s['commands']),blocked_uses=sum(e['source']=='archive' and e['externally_blocked'] for e in r['prediction_events']),monitor_windows=len(s['monitors']))
    return m

def summarize(rs):
    keys=sorted({(r['seed'],r['proposal_seed']) for r in rs});d={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r for r in rs};groups=[];pairs=[];guards=[];retention=[]
    for h in HISTORIES:
        for p in POLICIES:
            ms=[d[s,q,h,p]['metrics'] for s,q in keys]
            groups.append(dict(history=h,policy=p,confirmed=sum(m['confirmed'] for m in ms),uses=sum(m['uses'] for m in ms),withdrawals=sum(m['withdrawals'] for m in ms),commands=sum(m['commands'] for m in ms),blocked_uses=sum(m['blocked_uses'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),active_final_valid=sum(m['active_final_valid'] for m in ms),**{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed','active_expected')}))
        for seed,ps in keys:
            m={p:d[seed,ps,h,p]['metrics'] for p in POLICIES}
            pairs.append(dict(seed=seed,proposal_seed=ps,history=h,rechange_gain=m['current']['expected']['rechange'][2]-m['evidence']['expected']['rechange'][2],return_gain=m['shadow']['expected']['returning'][2]-m['evidence']['expected']['returning'][2],command_rechange_gain=m['current']['expected']['rechange'][2]-m['command']['expected']['rechange'][2],costs={p:{k:[m['evidence']['expected'][k][j]-m[p]['expected'][k][j] for j in range(3)] for k in WINDOWS} for p in ('current','shadow')}))
        for control in ('current','shadow'):
            for k in previous.WINDOWS:
                for j in range(3):
                    xs=[r['costs'][control][k][j] for r in pairs if r['history']==h]
                    guards.append(dict(history=h,control=control,window=k,channel=j,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02 and max(xs)<=.10))
        if h in ('forms','repeated'):
            for k in ('early_return','returning'):
                xs=[r['costs']['current'][k][2] for r in pairs if r['history']==h]
                retention.append(dict(history=h,window=k,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.01 and max(xs)<=.05))
    returns=[r for r in pairs if r['history'] in ('forms','repeated')]
    parity=all(d[s,q,h,p]['active_predictions']==d[s,q,h,'current']['active_predictions'] and d[s,q,h,p]['reviews']==d[s,q,h,'current']['reviews'] for h in HISTORIES for s,q in keys for p in POLICIES)
    gates=dict(rechange_mean=mean(r['rechange_gain'] for r in returns)>=.10,rechange_consistency=sum(r['rechange_gain']>1e-12 for r in returns)>=14,each_rechange_improves=all(mean(r['rechange_gain'] for r in returns if r['history']==h)>1e-12 for h in ('forms','repeated')),retained_recall=all(x['passed'] for x in retention),useful_recall_mean=mean(r['return_gain'] for r in returns)>=.01,useful_recall_consistency=sum(r['return_gain']>1e-12 for r in returns)>=14,preservation=all(x['passed'] for x in guards),final_validity=all(g['final_valid']>=8 and g['active_final_valid']>=8 for g in groups if g['policy']=='evidence'),active_parity=parity)
    return dict(gates=gates,empirical_pass=all(gates.values()),groups=groups,paired=pairs,guards=guards,retention_guards=retention,rechange_mean=mean(r['rechange_gain'] for r in returns),rechange_positive=sum(r['rechange_gain']>1e-12 for r in returns),return_mean=mean(r['return_gain'] for r in returns),return_positive=sum(r['return_gain']>1e-12 for r in returns),command_rechange_mean=mean(r['command_rechange_gain'] for r in returns),environment_means=[dict(seed=s,rechange_gain=mean(r['rechange_gain'] for r in returns if r['seed']==s),return_gain=mean(r['return_gain'] for r in returns if r['seed']==s)) for s in sorted({r['seed'] for r in returns})])
