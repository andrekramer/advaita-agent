"""Frozen outcomes for strength inspection; Brier units throughout."""
import random
from statistics import mean

WINDOWS = dict(early=(0,64), active=(0,256), released=(256,384), returning=(384,512))
POLICIES = ('existing','raw_banks','direction_strength','no_op','disagreement','rotated')


def direction(x):
    return 'improvement' if x > .001 else 'harm' if x < -.001 else 'negligible'


def measure(record, world):
    losses = {}
    for action, trace in record['branches'].items():
        errors = [[(p-y)**2 for p,y in zip(ps, row['local']+[row['y']])]
                  for ps,row in zip(trace['predictions'],world['main'][640:1152])]
        losses[action] = {k:[mean(row[j] for row in errors[lo:hi]) for j in range(3)]
                          for k,(lo,hi) in WINDOWS.items()}
    target=record['packet']['target']; protected=record['packet']['protected']
    probe_errors={mode:mean(abs(p['forecasts'][mode][when][j]-p['actual'][when][j])
                            for p in record['probes'] for when in ('before','after') for j in range(3))
                  for mode in ('prediction_only','existing','raw_banks','direction_strength')}
    future={}
    for mode in ('existing','raw_banks','direction_strength'):
        effects=[]
        for a in ('0','1','2'):
            actual=losses['none']['early'][target]-losses[a]['early'][target]
            predicted=record['decisions'][mode]['gains'][a]
            effects.append(dict(action=a,actual=actual,predicted=predicted,
                                error=abs(actual-predicted),correct=direction(actual)==direction(predicted),
                                nonnegligible=abs(actual)>.001))
        future[mode]=dict(effects=effects,mae=mean(e['error'] for e in effects),accuracy=mean(e['correct'] for e in effects))
    policies={}
    best=min(losses[a]['active'][target] for a in losses)
    for policy in POLICIES:
        a=record['decisions'][policy]['choice'];gain=losses['none']['active'][target]-losses[a]['active'][target]
        policies[policy]=dict(choice=a,losses=losses[a],target=losses[a]['active'][target],gain=gain,
                              acted=a!='none',unnecessary=a!='none' and gain<=.001,
                              missed=a=='none' and losses['none']['active'][target]-best>.001,
                              regret=losses[a]['active'][target]-best)
    return dict(branches=losses,probe_errors=probe_errors,future=future,policies=policies,
                target=target,protected=protected)


def interval(xs, samples):
    vals=sorted(mean(xs[i] for i in sample) for sample in samples)
    def q(p):
        z=(len(vals)-1)*p;i=int(z)
        return vals[i]+(z-i)*(vals[min(i+1,len(vals)-1)]-vals[i])
    return dict(mean=mean(xs),low=q(.025),high=q(.975),positive=sum(x>1e-12 for x in xs),n=len(xs))


def summarize(records):
    seeds=sorted({r['seed'] for r in records});rng=random.Random(417)
    samples=[[rng.randrange(len(seeds)) for _ in seeds] for _ in range(5000)]
    def cluster(fn):return interval([mean(fn(r) for r in records if r['seed']==s) for s in seeds],samples)
    future=cluster(lambda r:r['metrics']['future']['raw_banks']['mae']-r['metrics']['future']['existing']['mae'])
    gains={p:cluster(lambda r,p=p:r['metrics']['policies'][p]['target']-r['metrics']['policies']['raw_banks']['target'])
           for p in ('existing','no_op','disagreement','rotated')}
    guards=[]
    for h in ('stable','forms','repeated'):
        rows=[r for r in records if r['history']==h]
        for win in ('active','released','returning'):
            for channel in range(3):
                use=[r for r in rows if win!='active' or h=='stable' or r['metrics']['protected']==channel]
                if not use:continue
                costs=[r['metrics']['policies']['raw_banks']['losses'][win][channel]-r['metrics']['policies']['no_op']['losses'][win][channel] for r in use]
                guards.append(dict(history=h,window=win,channel=channel,mean=mean(costs),maximum=max(costs),passed=mean(costs)<=.01 and max(costs)<=.05))
    effects=[e for r in records for e in r['metrics']['future']['raw_banks']['effects']]
    accuracy=mean(e['correct'] for e in effects);coverage=sum(e['nonnegligible'] for e in effects)
    groups=[]
    for h in ('stable','forms','repeated'):
        for task in ('local','composite'):
            rows=[r for r in records if r['history']==h and (r['metrics']['target']==2)==(task=='composite')]
            for p in POLICIES:
                ms=[r['metrics']['policies'][p] for r in rows]
                groups.append(dict(history=h,task=task,policy=p,n=len(ms),loss=mean(m['target'] for m in ms),
                                   gain=mean(m['gain'] for m in ms),actions=sum(m['acted'] for m in ms),
                                   unnecessary=sum(m['unnecessary'] for m in ms),missed=sum(m['missed'] for m in ms),regret=mean(m['regret'] for m in ms)))
    maxima={mode:max(abs(p['actual'][when][j]-p['forecasts'][mode][when][j])
                     for r in records for p in r['probes'] for when in ('before','after') for j in range(3))
            for mode in ('raw_banks','direction_strength')}
    gates=dict(mechanical=max(maxima.values())<=1e-10,
               information_forecast=future['high']<0,
               effect_direction=coverage>=24 and accuracy>=.75,
               steering_mean=gains['existing']['mean']>=.001 and gains['existing']['low']>0,
               steering_consistency=gains['existing']['positive']>=8,
               versus_no_op=gains['no_op']['low']>=-.001,
               preservation=all(g['passed'] for g in guards))
    return dict(gates=gates,information_pass=gates['information_forecast'] and gates['effect_direction'],
                steering_pass=all(gates[k] for k in ('steering_mean','steering_consistency','versus_no_op','preservation')),
                presentation_tested=False,future_error_difference=future,steering_gains=gains,guards=guards,
                future_accuracy=accuracy,nonnegligible_effects=coverage,groups=groups,mechanical_maxima=maxima,
                probe_mean_errors={mode:mean(r['metrics']['probe_errors'][mode] for r in records) for mode in records[0]['metrics']['probe_errors']})
