"""032 fixed outcome classifications and paired gates."""
import math
from statistics import mean
from memory_lifecycle import target

def direction(gain):
    return 'improvement' if gain>.005 else 'harm' if gain<-.005 else 'no_effect'

def measure(record,world):
    tick=record['tick'];windows=dict(future=(tick+1,tick+256),remaining=(tick+1,2048),returning=(1025,1536),later=(1537,2048))
    out={}
    for name,b in record['branches'].items():
        ms={}
        for key,(lo,hi) in windows.items():
            rows=[(t,ps,world['main'][t-1]) for t,ps in enumerate(b['predictions'],tick+1) if lo<=t<=hi]
            observed=[mean(-math.log(ps[j] if (r['local'][j] if j<2 else r['y']) else 1-ps[j]) for _,ps,r in rows) for j in range(3)]
            latent=mean(-(.9*math.log(ps[2] if target(world,r['x'],r['a'],t) else 1-ps[2])+.1*math.log(1-ps[2] if target(world,r['x'],r['a'],t) else ps[2])) for t,ps,r in rows)
            ms[key]=dict(observed=observed,latent=latent)
        e=b['evaluation'];ms['valid']=all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10
        out[name]=ms
    forecasts=[]
    for f in record['decision']['forecasts']:
        j=f['channel'];a=out[str(j)];b=out['none'];gain=b['future']['observed'][2]-a['future']['observed'][2]
        own=b['future']['observed'][j]-a['future']['observed'][j]
        delta=max(abs(p[2]-q[2]) for p,q in zip(record['branches'][str(j)]['immediate'],record['branches']['none']['immediate']))
        forecasts.append(dict(channel=j,eligible=j in record['decision']['eligible'],gain=gain,own_gain=own,
            actual=direction(gain),own_actual=direction(own),immediate_delta=delta,
            immediate_actual='change' if delta>1e-12 else 'no_change'))
    return dict(branches=out,forecasts=forecasts)

def summarize(records):
    rows=[];forecasts=[];groups=[]
    for r in records:
        m=r['metrics'];choices=r['decision']['choices'];key=lambda p:'none' if choices[p] is None else str(choices[p])
        a=m['branches'][key('aware')];n=m['branches']['none'];d=m['branches'][key('disagreement')];rot=m['branches'][key('rotated')]
        rows.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],history=r['history'],choices=choices,
            gain_vs_disagreement=d['future']['observed'][2]-a['future']['observed'][2],gain_vs_none=n['future']['observed'][2]-a['future']['observed'][2],
            gain_vs_rotated=rot['future']['observed'][2]-a['future']['observed'][2],valid=a['valid'],
            costs={k:dict(observed=[a[k]['observed'][j]-n[k]['observed'][j] for j in range(3)],latent=a[k]['latent']-n[k]['latent']) for k in ('remaining','returning','later')}))
        for f,actual in zip(r['decision']['forecasts'],m['forecasts']):
            if actual['eligible']:
                forecasts.append(dict(seed=r['seed'],history=r['history'],proposal_seed=r['proposal_seed'],**actual,
                    correct=f['future']==actual['actual'],naive_correct=f['disagreement_future']==actual['actual'],
                    own_correct=f['own_future']==actual['own_actual'],immediate_correct=f['immediate']==actual['immediate_actual']))
    changing=[r for r in rows if r['history']!='stable'];fs=[f for f in forecasts if f['history']!='stable']
    avg=lambda xs:mean(xs) if xs else None
    accuracy=avg([f['correct'] for f in fs]);naive=avg([f['naive_correct'] for f in fs])
    for h in ('stable','repeated','forms'):
        rs=[r for r in records if r['history']==h]
        for p in ('no_op','disagreement','aware','rotated'):
            ms=[r['metrics']['branches']['none' if r['decision']['choices'][p] is None else str(r['decision']['choices'][p])] for r in rs]
            groups.append(dict(history=h,policy=p,actions=sum(r['decision']['choices'][p] is not None for r in rs),valid=sum(m['valid'] for m in ms),
                **{k:dict(observed=[mean(m[k]['observed'][j] for m in ms) for j in range(3)],latent=mean(m[k]['latent'] for m in ms)) for k in ('future','remaining','returning','later')}))
    preservation=[]
    for h in ('stable','repeated','forms'):
        rs=[r for r in rows if r['history']==h]
        for k in ('returning','later'):
            preservation.extend(mean(r['costs'][k]['observed'][j] for r in rs)<=.02 for j in range(3))
            preservation.extend(r['costs'][k]['observed'][j]<=.10 for r in rs for j in range(3))
            preservation.append(mean(r['costs'][k]['latent'] for r in rs)<=.02)
    gates=dict(mechanical=all(f['immediate_correct'] for f in forecasts),forecast_coverage=len(fs)>=8 and len({f['seed'] for f in fs})>=3,
        forecast_accuracy=accuracy is not None and accuracy>=.8,forecast_advantage=accuracy is not None and accuracy-naive>=.2,
        steering_gain=mean(r['gain_vs_disagreement'] for r in changing)>=.005,
        steering_consistency=sum(r['gain_vs_disagreement']>0 for r in changing)>=12,
        steering_vs_none=mean(r['gain_vs_none'] for r in changing)>=0,preservation=all(preservation),
        final_validity=all(g['valid']>=8 for g in groups if g['policy']=='aware'))
    return dict(gates=gates,primary_pass=all(gates.values()),forecast_pass=all(gates[k] for k in ('forecast_coverage','forecast_accuracy','forecast_advantage')),
        steering_pass=all(gates[k] for k in ('steering_gain','steering_consistency','steering_vs_none','preservation','final_validity')),
        eligible=len(forecasts),eligible_changing=len(fs),forecast_accuracy=accuracy,naive_accuracy=naive,own_accuracy=avg([f['own_correct'] for f in fs]),
        paired=rows,forecasts=forecasts,groups=groups,
        environment_means=[dict(seed=s,gain=mean(r['gain_vs_disagreement'] for r in changing if r['seed']==s)) for s in sorted({r['seed'] for r in changing})])
