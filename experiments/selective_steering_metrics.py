"""033 expected and observed outcomes, frozen comparisons."""
import math
from statistics import mean
import memory_lifecycle as life
WINDOWS=dict(active=(513,1024),burst=(513,640),settled=(641,1024),returning=(1025,1536),later=(1537,2048))
POLICIES=('legacy','refreshed','lock_only','plastic_only','selective','swapped')

def measure(r,w):
    values={'observed':[],'expected':[]}
    for t,(ps,row) in enumerate(zip(r['predictions'],w['main']),1):
        forms=life.forms_at(w,t,True);truth=[forms[j][row['x'][j]] for j in range(2)]+[life.target(w,row['x'],row['a'],t)]
        observed=row['local']+[row['y']]
        values['observed'].append([-math.log(p if y else 1-p) for p,y in zip(ps,observed)])
        values['expected'].append([-.9*math.log(p if y else 1-p)-.1*math.log(1-p if y else p) for p,y in zip(ps,truth)])
    result={typ:{k:[mean(v[j] for v in rows[lo-1:hi]) for j in range(3)] for k,(lo,hi) in WINDOWS.items()} for typ,rows in values.items()}
    p=w['instruction']['protected'];q=1-p
    result.update(protected=p,flexible=q,burst_correct=mean(e['local_exact'][p] for e in r['evaluations'] if 513<=e['tick']<=640),
        active_local_correct=[mean(e['local_exact'][j] for e in r['evaluations'] if 513<=e['tick']<=1024) for j in range(2)],
        final_valid=r['evaluations'][-1]['valid'],final_local_exact=r['evaluations'][-1]['local_exact'],final_spec=r['evaluations'][-1]['spec'])
    return result

def summarize(rs):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in rs});lookup={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r['metrics'] for r in rs};groups=[];paired=[]
    for h in ('stable','forms','repeated'):
        for policy in POLICIES:
            ms=[lookup[s,q,h,policy] for s,q in pairs]
            groups.append(dict(history=h,policy=policy,burst_correct=mean(m['burst_correct'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),
                **{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed')}))
        for s,q in pairs:
            a=lookup[s,q,h,'selective'];b=lookup[s,q,h,'refreshed'];lock=lookup[s,q,h,'lock_only'];flex=a['flexible']
            paired.append(dict(seed=s,proposal_seed=q,history=h,plastic_gain=lock['expected']['active'][flex]-a['expected']['active'][flex],composite_gain=b['expected']['active'][2]-a['expected']['active'][2],
                costs={k:[a['expected'][k][j]-b['expected'][k][j] for j in range(3)] for k in WINDOWS}))
    changed=[p for p in paired if p['history']!='stable'];get=lambda h,p:next(g for g in groups if g['history']==h and g['policy']==p)
    gates=dict(protection=all(get(h,'selective')['burst_correct']>=.95 and get(h,'selective')['burst_correct']>=get(h,'refreshed')['burst_correct'] for h in ('forms','repeated')),
        plastic_gain=mean(p['plastic_gain'] for p in changed)>=.01,plastic_consistency=sum(p['plastic_gain']>0 for p in changed)>=14,
        composite_gain=mean(p['composite_gain'] for p in changed)>=.005,composite_consistency=sum(p['composite_gain']>0 for p in changed)>=12,
        preservation=True,final_validity=all(get(h,'selective')['final_valid']>=8 for h in ('stable','forms','repeated')))
    for h in ('stable','forms','repeated'):
        for k in ('returning','later')+(('active',) if h=='stable' else ()):
            for j in range(3):
                xs=[p['costs'][k][j] for p in paired if p['history']==h]
                if mean(xs)>.02 or max(xs)>.10:gates['preservation']=False
    return dict(gates=gates,empirical_pass=all(gates.values()),groups=groups,paired=paired,
        environment_means=[dict(seed=s,plastic_gain=mean(p['plastic_gain'] for p in changed if p['seed']==s),composite_gain=mean(p['composite_gain'] for p in changed if p['seed']==s)) for s in sorted({p['seed'] for p in changed})])
