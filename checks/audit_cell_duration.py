"""Re-score the fresh five-arm study and verify event timing and decision rules."""
import argparse
import gzip
import hashlib
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path
from statistics import mean

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
import memory_lifecycle as life

ARMS=('none','channel','cell','budget','duration')
HISTORIES=('stable','burst','lasting','repeated','forms')
SEEDS=range(3300,3312)
WINDOWS=dict(early=(0,64),active=(0,256),release=(256,384))
WINDOWS['return']=(384,512)


def near(a,b):
    assert math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(a,b)


def filehash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def interval(values):
    rng=random.Random(429)
    draws=sorted(sum(rng.choices(values,k=12))/12 for _ in range(5000))
    def percentile(p):
        index=4999*p
        low=int(index)
        return draws[low]*(low+1-index)+draws[low+1]*(index-low)
    return [mean(values),percentile(.025),percentile(.975)]


def check_events(branch, name, decision):
    events=branch['cell_events']
    if not decision['enabled'] or name in ('none','channel'):
        assert not events
        return 0
    opening,*debits,closing=events
    assert opening['kind']=='open' and opening['tick']==640
    assert opening['binding']==decision['selected']
    remaining=decision['budget'] if name=='budget' else None
    assert opening['budget']==remaining
    assert opening['through_tick']==(703 if name=='duration' else 896)
    spent=0.
    for tick,event in enumerate(debits,641):
        assert event['tick']==tick and event['kind']=='debit'
        debit=event['before']*(2**(-1/1024)-2**(-1/128))
        if remaining is not None:
            debit=min(remaining,debit)
            remaining-=debit
            near(event['remaining'],remaining)
        spent+=debit
        near(debit,event['debit'])
        near(event['after'],event['before']*2**(-1/1024)-debit)
        near(spent,event['spent'])
    assert closing['tick']==640+len(debits) and closing['kind']=='close'
    near(branch['spent'],spent)
    if name in ('budget','duration'):
        assert len(debits)==63 and closing['reason']==('expired' if name=='duration' else 'exhausted')
        if name=='budget':
            near(spent,decision['budget'])
        else:
            initial=opening['tick']
            s=debits[0]['before']
            for t,event in enumerate(debits,initial+1):
                near(event['before'],s*2**(-(t-initial-1)/128))
    else:
        assert (closing['reason']=='expired' and closing['tick']==896 or
                closing['reason']=='meaning changed' and closing['tick']%64==0)
    return len(debits)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/cell-duration-confirmation-v1')
    out=parser.parse_args().output
    if not __debug__:
        raise RuntimeError('Audit requires enabled assertions')
    s=json.loads((out/'summary.json').read_text())
    for name,digest in json.loads((out/'manifest.json').read_text()).items():
        assert filehash(ROOT/name)==digest,name
    seen=set()
    cases=[]
    env_worlds={}
    required=set()
    debit_count=0
    for seed in SEEDS:
        for h in HISTORIES:
            w=life.generate(seed,h if h in ('forms','repeated') else 'stable')
            rows=w['main'][640:1152]
            for r in rows if h=='lasting' else []:
                r['local'][w['affected']]^=1
                r['y']^=1
            env_worlds[seed,h]=rows
            required.update((seed,h,p,j) for p in (3300,3301) for j in (w['affected'],2))
    with gzip.open(out/'cases.jsonl.gz','rt') as stream:
        for line in stream:
            r=json.loads(line)
            key=(r['seed'],r['history'],r['proposal'],r['target'])
            assert key in required and key not in seen
            seen.add(key)
            rows=env_worlds[key[:2]]
            labels=[[*row['local'],row['y']] for row in rows]
            frozen=r.pop('fixed_predictions')
            near(r['frozen_loss'],mean((p-y)**2 for ps,ys in zip(frozen,labels) for p,y in zip(ps,ys)))
            for j in (0,1):
                improvement=mean((r['pooled'][j]-y[j])**2-(ps[j]-y[j])**2 for ps,y in zip(frozen,labels))
                assert r['split'][j]==(r['created'][j] and improvement>0)
            assert set(r['branches'])==set(ARMS)
            d=r['decision']
            b=r['branches']['budget']
            duration=r['branches']['duration']
            assert b['predictions'][:62]==duration['predictions'][:62]
            for a in ARMS:
                near(d['forecast']['named'][a],d['forecast']['raw'][a])
                branch=r['branches'][a]
                preds=branch['predictions']
                assert len(preds)==512 and all(len(ps)==3 and all(0<=p<=1 for p in ps) for ps in preds)
                if not d['enabled']:
                    assert preds==r['branches']['none']['predictions']
                debit_count+=check_events(branch,a,d)
                for win,(lo,hi) in WINDOWS.items():
                    for j in range(3):
                        near(branch['losses'][win][j],sum((preds[k][j]-labels[k][j])**2 for k in range(lo,hi))/(hi-lo))
            if d['enabled']:
                assert b['cell_events'][-2]['debit']<duration['cell_events'][-2]['debit']
                for eb,ed in zip(b['cell_events'][1:-2],duration['cell_events'][1:-2]):
                    near(eb['debit'],ed['debit'])
            near(r['timing']['gap'],max(abs(p-q) for bs,ds in zip(b['predictions'],duration['predictions']) for p,q in zip(bs,ds)))
            for branch in r['branches'].values():
                del branch['predictions'],branch['cell_events']
            cases.append(r)
    assert seen==required and len(seen)==240
    def gain(r,a,w='active'):
        j=r['target']
        return r['branches']['none']['losses'][w][j]-r['branches'][a]['losses'][w][j]
    def contrast(a,b):
        return interval([mean(gain(r,a)-gain(r,b) for r in cases if r['seed']==seed) for seed in SEEDS])
    for a in ARMS:
        for actual,expected in zip(contrast(a,'none'),s['arms'][a]['gain']):
            near(actual,expected)
        for guard in s['arms'][a]['guards']:
            j=guard['output']
            win=guard['window']
            xs=[r['branches'][a]['losses'][win][j]-r['branches']['none']['losses'][win][j] for r in cases
                if r['history']==guard['history'] and (r['history']=='stable' or win!='active' or r['protected']==j)]
            near(mean(xs),guard['mean'])
            near(max(xs),guard['worst'])
            assert guard['passed']==(mean(xs)<=.01 and max(xs)<=.05)
    paired=contrast('budget','duration')
    for actual,expected in zip(paired,s['budget_over_duration']):
        near(actual,expected)
    maximum=max(abs(r['branches']['duration']['losses'][w][j]-r['branches']['budget']['losses'][w][j])
                for r in cases for w in ('release','return') for j in range(3))
    near(maximum,s['maximum_release_return_difference'])
    assert s['equivalent']==(paired[1]>=-.0001 and paired[2]<=.0001 and maximum<=.005)
    eligible=[r for r in cases if r['history'] in ('lasting','forms','repeated')]
    learn=mean(r['frozen_loss']-mean(r['branches']['none']['losses']['active']) for r in eligible)
    near(learn,s['learning_gain'])
    split=sum(any(any(r['split']) and r['transfer_accuracy']>=.875 for r in cases if r['history']=='stable' and r['seed']==seed) for seed in SEEDS)
    effects=[(gain(r,a,'early'),r['decision']['forecast']['named'][a],r['decision']['forecast']['aggregate'][a]) for r in cases for a in ('channel','cell','budget')]
    classify=lambda x: int(x>.001)-int(x<-.001)
    correct=sum(classify(v)==classify(f) for v,f,_ in effects)
    material=sum(abs(v)>.001 for v,_,_ in effects)
    original=s['original_effects']
    assert (correct,material)==(original['correct'],original['material'])
    for index,name in ((1,'named'),(2,'aggregate')):
        near(mean(abs(row[0]-row[index]) for row in effects),original['effect_mae'][name])
    actions=sum(r['decision']['enabled'] for r in cases)
    assert actions==s['actions']
    cell=s['arms']['cell']
    gates=dict(learn=learn>=.001 and split==12,interpret=max(b['error'] for r in cases for b in r['branches'].values())<=1e-10 and
               original['effect_mae']['named']<=original['effect_mae']['aggregate']+1e-12 and correct/len(effects)>=.75 and material>=16,
               steer=cell['gain'][0]>=.001 and cell['gain'][1]>0 and actions/240>=.2 and all(g['passed'] for g in cell['guards']))
    assert s['gates']==gates
    record=dict(status='pass',cases=len(cases),continuations=len(cases)*5,observations=len(cases)*5*512,debits=debit_count,
                criteria=gates,equivalent=s['equivalent'],hashes={name:filehash(out/name) for name in ('summary.json','cases.jsonl.gz','manifest.json')},
                scope='Rescored saved predictions, timing, debits, paired intervals and decision criteria. Native parity and clone probes are runner checks.')
    with (out/'audit.json').open('x') as stream:
        json.dump(record,stream,indent=2)
        stream.write('\n')
    print(record)


if __name__=='__main__':
    main()
