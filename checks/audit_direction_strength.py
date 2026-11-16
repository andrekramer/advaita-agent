"""Re-score saved forecasts against seeded labels and independently reconcile command spending."""
import gzip
import hashlib
import itertools
import json
import math
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
import memory_lifecycle as life

OUT=ROOT/'results/direction-strength-v1'
ARMS=('none','channel','cell','budget')


def near(a,b):
    assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)


def fingerprint(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    manifest=json.loads((OUT/'manifest.json').read_text())
    for name,value in manifest.items():
        assert fingerprint(ROOT/name)==value,name
    saved=json.loads((OUT/'summary.json').read_text())
    seen=set()
    gains=defaultdict(list)
    guards=defaultdict(list)
    close_reasons=defaultdict(Counter)
    future_errors=defaultdict(list)
    learning=[]
    actions=exhausted=material=material_correct=correct=debits=0
    splits=set()
    for_seed={}
    source=gzip.open(OUT/'cases.jsonl.gz','rt')
    with source:
        for line in source:
            case=json.loads(line)
            seed,history,j,ps=(case[k] for k in ('seed','history','target','proposal'))
            uid=(seed,history,j,ps)
            assert uid not in seen
            seen.add(uid)
            key=(seed,history)
            if key not in for_seed:
                base=history if history in ('repeated','forms') else 'stable'
                w=life.generate(seed,base)
                ys=[]
                for tick,row in enumerate(w['main'][640:1152],641):
                    y=[*row['local'],row['y']]
                    if history=='lasting':
                        y[w['affected']]^=1
                        y[2]^=1
                    ys.append(y)
                for_seed[key]=(w['affected'],ys)
            affected,labels=for_seed[key]
            assert case['protected']==1-affected and j in (affected,2)
            if history=='stable' and any(case['split']) and case['transfer_accuracy']>=.875:
                splits.add(seed)
            decision=case['decision']
            actions+=decision['enabled']
            costs={}
            for arm,branch in case['branches'].items():
                assert len(branch['predictions'])==512
                squared=[[(prob-y)**2 for prob,y in zip(pred,outcomes)] for pred,outcomes in zip(branch['predictions'],labels)]
                costs[arm]={}
                for win,(lo,hi) in dict(early=(0,64),active=(0,256),release=(256,384),**{'return':(384,512)}).items():
                    means=[sum(row[q] for row in squared[lo:hi])/(hi-lo) for q in range(3)]
                    for q in range(3):
                        near(means[q],branch['losses'][win][q])
                    costs[arm][win]=means
                events=branch['cell_events']
                commanded=decision['enabled'] and arm in ('cell','budget')
                assert bool(events)==commanded
                if commanded:
                    assert events[0]['kind']=='open' and events[0]['tick']==640
                    assert events[0]['binding']==decision['selected']
                    remaining=decision['budget'] if arm=='budget' else None
                    assert events[0]['budget']==remaining
                    spent=0.
                    for tick,event in enumerate(events[1:-1],641):
                        assert event['kind']=='debit' and event['tick']==tick
                        amount=event['before']*(2**(-1/1024)-2**(-1/128))
                        if remaining is not None:
                            amount=min(remaining,amount)
                            remaining-=amount
                            near(remaining,event['remaining'])
                        spent+=amount
                        near(amount,event['debit'])
                        near(event['after'],event['before']*2**(-1/1024)-amount)
                        near(spent,event['spent'])
                        debits+=1
                    end=events[-1]
                    assert end['kind']=='close' and end['tick']==events[-2]['tick']<=896
                    if end['reason']=='exhausted':
                        assert arm=='budget'
                        near(remaining,0.)
                        exhausted+=1
                    elif end['reason']=='expired':
                        assert end['tick']==896
                    else:
                        assert end['reason']=='meaning changed' and end['tick']%64==0
                    near(spent,branch['spent'])
                    close_reasons[arm][end['reason']]+=1
                if not decision['enabled']:
                    assert branch['predictions']==case['branches']['none']['predictions']
            for arm in ARMS:
                gains[seed,arm].append(costs['none']['active'][j]-costs[arm]['active'][j])
            for arm in ARMS[1:]:
                actual=costs['none']['early'][j]-costs[arm]['early'][j]
                sign=lambda x:int(x>.001)-int(x<-.001)
                right=sign(actual)==sign(decision['forecast']['named'][arm])
                correct+=right
                material+=abs(actual)>.001
                material_correct+=right and abs(actual)>.001
                for mode in ('named','aggregate'):
                    future_errors[mode].append(abs(actual-decision['forecast'][mode][arm]))
            if history in ('lasting','forms','repeated'):
                learning.append(case['frozen_loss']-mean(costs['none']['active']))
            for win in ('active','release','return'):
                for q in range(3):
                    if win!='active' or history=='stable' or q==1-affected:
                        guards[history,win,q].append(costs['budget'][win][q]-costs['none'][win][q])
    assert len(seen)==160 and len(for_seed)==40
    seeds=list(range(3200,3208))
    def verify_interval(xs,values):
        rng=random.Random(429)
        sims=sorted(sum(rng.choices(xs,k=8))/8 for _ in range(5000))
        near(mean(xs),values[0])
        for f,limit in zip((.025,.975),values[1:]):
            pos=f*4999
            i=int(pos)
            near(sims[i]*(i+1-pos)+sims[i+1]*(pos-i),limit)
    for arm in ARMS:
        verify_interval([mean(gains[s,arm]) for s in seeds],saved['active_gains'][arm])
    for first,second,key in [('budget','cell','budget_minus_uncapped_gain'),('cell','channel','cell_minus_channel_gain')]:
        verify_interval([mean(gains[s,first])-mean(gains[s,second]) for s in seeds],saved[key])
    assert len(guards)==len(saved['guards'])
    passes=True
    for guard in saved['guards']:
        values=guards[guard['history'],guard['window'],guard['output']]
        near(mean(values),guard['mean'])
        near(max(values),guard['worst'])
        passed=mean(values)<=.01 and max(values)<=.05
        assert guard['passed']==passed
        passes &= passed
    for mode,values in future_errors.items():
        near(saved['effect_mae'][mode],mean(values))
    assert (actions,exhausted,correct,material,material_correct)==tuple(saved[k] for k in ('actions','exhausted','correct','material','material_correct'))
    near(mean(learning),saved['learning_gain'])
    interval=saved['active_gains']['budget']
    gates=dict(learn=len(splits)==8 and mean(learning)>=.001,
               interpret=saved['one_step_and_debit_max_error']<=1e-10 and mean(future_errors['named'])<=mean(future_errors['aggregate'])+1e-12 and correct/480>=.75 and material>=16,
               steer=interval[0]>=.001 and interval[1]>0 and actions>=32 and exhausted>0 and passes)
    assert gates==saved['gates']
    result=dict(status='pass',cases=len(seen),branches=len(seen)*4,scored_observations=len(seen)*4*512,
                reconciled_debits=debits,closure_reasons=close_reasons,gates=gates,
                scope='independent scoring of saved predictions and debit records, paired outcomes and decision criteria. Native no-command parity and cloned one-step checks ran in the trial.',
                hashes={name:fingerprint(OUT/name) for name in ('manifest.json','cases.jsonl.gz','summary.json')})
    with (OUT/'audit.json').open('x') as stream:
        json.dump(result,stream,indent=2)
        stream.write('\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    main()
