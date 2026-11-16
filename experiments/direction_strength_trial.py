"""Paired scripted decision experiment for a meaning-bound slow-evidence budget."""
import argparse
import gzip
import hashlib
import json
import random
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT / 'experiments')]
from advaita.controlled import ControlledLearner
from advaita.direction_strength import DirectionStrengthLearner
from advaita.structural import StructuralLearner
import memory_lifecycle as life

ARMS = ('none', 'channel', 'cell', 'budget')
HISTORIES = ('stable', 'burst', 'lasting', 'repeated', 'forms')
WINDOWS = {'early': (0, 64), 'active': (0, 256), 'release': (256, 384), 'return': (384, 512)}
OUT = ROOT / 'results/direction-strength-v1'


def world(seed, history):
    base = history if history in ('forms', 'repeated') else 'stable'
    w = life.generate(seed, base)
    if history in ('burst', 'lasting'):
        j = w['affected']
        def change(t, rows):
            if (history == 'burst' and 577 <= t <= 640) or (history == 'lasting' and t >= 513):
                for row in rows:
                    row['local'][j] ^= 1
                    row['y'] ^= 1
        for t, row in enumerate(w['main'], 1):
            change(t, [row])
        for t, rows in w['selection'].items():
            change(int(t), rows)
    return w


def raw_index(channel, row):
    x, y = row['x']
    return row['x'][channel] if channel < 2 else 8*x + 2*y + row['a']


def labels(row):
    return row['local'] + [row['y']]


def describe(learner, target, recent):
    cells = {}
    for x, y, a in life.CONTEXTS:
        info = learner.inspect_cell(target, [x, y], a)
        key = tuple(info['binding']['members'])
        if key in cells:
            continue
        visits = [labels(r)[target] for r in recent if raw_index(target, r) in key]
        raw = [[sum(bank[target][i][k] for i in key) for k in (0, 1)]
               for bank in (learner._engine.fast, learner._engine.slow)]
        cells[key] = dict(info=info, raw=raw, x=[x, y], a=a, frequency=len(visits)/len(recent),
                          rate=(sum(visits)+1)/(len(visits)+2))
    return sorted(cells.values(), key=lambda cell: cell['info']['binding']['members'])


def project(cell, arm, allocation, fraction):
    (u, n), (v, s) = cell['raw']
    if allocation == 'named':
        u, n = pair(cell['info']['fast'])
        v, s = pair(cell['info']['slow'])
    elif allocation != 'raw':
        successes, mass = u+v, n+s
        u, n = successes*allocation, mass*allocation
        v, s = successes*(1-allocation), mass*(1-allocation)
    limit = fraction
    weight, rate = cell['frequency'], cell['rate']
    loss = 0.
    for _ in range(64):
        u *= 2**(-1/64)
        n *= 2**(-1/64)
        decay = 2**(-1/1024)
        if arm != 'none' and s:
            extra = (decay-2**(-1/128))*s
            if arm == 'budget':
                extra = min(limit, extra)
                limit -= extra
            decay -= extra/s
        v *= decay
        s *= decay
        p = (1+u+v)/(2+n+s)
        loss += weight*(rate*(1-p)**2+(1-rate)*p*p)/64
        u += weight*rate
        n += weight
    return loss


def pair(bank):
    return (bank['direction'] or 0.)*bank['strength'], bank['strength']


def choose(cells):
    slow = sum(c['raw'][1][1] for c in cells)
    fast = sum(c['raw'][0][1] for c in cells)
    share = fast/(fast+slow) if fast+slow else .5
    gains = [project(c,'none','named',0)-project(c,'cell','named',0) for c in cells]
    best = max(range(len(cells)), key=gains.__getitem__)
    chosen = cells[best]
    budget = .25*chosen['raw'][1][1]
    enabled = gains[best] > .0005 and budget > 0
    forecast = {}
    for name, allocation in [('named','named'),('raw','raw'),('aggregate',share)]:
        forecast[name] = {}
        for arm in ARMS:
            total = 0.
            for i,c in enumerate(cells):
                mode = arm if enabled and (arm=='channel' or i==best) else 'none'
                total += project(c,'none',allocation,budget)-project(c,mode,allocation,budget)
            forecast[name][arm] = total
    assert max(abs(forecast['raw'][a]-forecast['named'][a]) for a in ARMS)<1e-12
    return dict(selected=chosen['info']['binding'], x=chosen['x'], a=chosen['a'], enabled=enabled,
                budget=budget, gain=gains[best], forecast=forecast)


def one_step(learner, row, target):
    # Independent analytical readout. Include the command only for its bound cell.
    info = learner.inspect_cell(target,row['x'],row['a'])
    f, n = pair(info['fast'])
    s, m = pair(info['slow'])
    slow_decay = 2**(-1/info['slow_half_life'])
    cmd = info['command']
    if cmd and cmd['binding']==info['binding'] and m:
        extra = (slow_decay-2**(-1/128))*m
        if cmd['remaining'] is not None:
            extra = min(extra,cmd['remaining'])
        slow_decay -= extra/m
    u = 1 + f*2**(-1/64) + s*slow_decay
    total = 2 + n*2**(-1/64) + m*slow_decay
    return u/total, [u/(total+1),(u+1)/(total+1)]


def configure(b, target, decision, arm):
    if not decision['enabled'] or arm=='none':
        return
    if arm=='channel':
        b.configure(lock=[],plastic=[target],reason='supplied target',source='script')
    else:
        b.open_cell(target,decision['x'],decision['a'],budget=decision['budget'] if arm=='budget' else None,
                    through_tick=896,reason='supplied target')


def probe(b, target, decision):
    error = 0.
    for label in (0,1):
        c = DirectionStrengthLearner.restore(b.checkpoint())
        row = dict(x=decision['x'], a=decision['a'], local=[label,label], y=label)
        before, after = one_step(c,row,target)
        observed = c.observe(c.tick+1,row)[target]
        current = c.predict(row['x'],row['a'])['active'][target]
        error = max(error,abs(observed-before),abs(current-after[label]))
    return error


def partition_correct(part, form):
    return all((part[i]==part[j])==(form[i]==form[j]) for i in range(4) for j in range(4))


def run_arm(checkpoint, native_checkpoint, w, history, target, decision, arm):
    b = DirectionStrengthLearner.restore(checkpoint)
    reference = ControlledLearner.restore(native_checkpoint) if arm=='none' else None
    configure(b,target,decision,arm)
    error = probe(b,target,decision)
    rows = w['main'][640:1152]
    losses = []
    predictions = []
    subset = []
    native_removed = []
    for t,row in enumerate(rows,641):
        ps = b.observe(t,row)
        predictions.append(ps)
        losses.append([(p-y)**2 for p,y in zip(ps,labels(row))])
        if t<=896 and raw_index(target,row) in decision['selected']['members']:
            subset.append(losses[-1][target])
        if reference:
            assert reference.observe(t,row)==ps
        if t%64==0:
            batch = w['selection'][str(t)]
            review = b.review(t,batch)
            native_removed.extend(x['removed_mass'] for x in review['weakenings'])
            if reference:
                assert review==reference.review(t,batch)
            if t==896 and decision['enabled'] and arm=='channel':
                b.configure(lock=[],plastic=[],reason='scheduled release',source='script')
        if t==660:
            saved=b.checkpoint()
            b=DirectionStrengthLearner.restore(saved)
            assert b.checkpoint()==saved
    if reference:
        assert reference.native_checkpoint()==b.native_checkpoint()
    spent = 0.
    for event in b.cell_events:
        if event['kind']!='debit':
            continue
        difference = event['before']*2**(-1/1024)-event['after']
        error = max(error,abs(event['debit']-difference))
        spent += event['debit']
        error = max(error,abs(spent-event['spent']))
    if arm=='budget':
        assert spent<=decision['budget']+1e-10
    assert b.cell_command is None
    forms=life.forms_at(w,1152,True)
    if history=='lasting':
        j=w['affected']
        forms[j]=[1-v for v in forms[j]]
    local=[partition_correct(m['partition'],form) for m,form in zip(b._engine.locals,forms)]
    correct=0
    for x,y,a in life.CONTEXTS:
        p=b.predict([x,y],a)['active'][2]
        correct+=int((p>=.5)==bool(forms[0][x]^forms[1][y]^a))
    return dict(losses={k:[mean(row[j] for row in losses[start:end]) for j in range(3)]
                        for k,(start,end) in WINDOWS.items()},cell_loss=mean(subset),error=error,
                closed=[e['reason'] for e in b.cell_events if e['kind']=='close'],
                spent=spent,native_removed=sum(native_removed),local_correct=local,upper_accuracy=correct/32,
                predictions=predictions,cell_events=b.cell_events)


def run_trunk(w,history,ps):
    acquisition, encoded = life.legacy_run(w,ps,True)
    core=StructuralLearner.restore(encoded)
    learner=DirectionStrengthLearner(core)
    native=ControlledLearner(core)
    initial={ctx:native.predict(list(ctx[:2]),ctx[2])['active'] for ctx in life.CONTEXTS}
    pooled=[]
    for model in native._engine.locals:
        sums=[sum(v[k] for v in model['counts'].values()) for k in (0,1)]
        pooled.append((sums[0]+1)/(sums[1]+2))
    for t,row in enumerate(w['main'][:640],1):
        assert native.observe(t,row)==learner.observe(t,row)
        if t%64==0:
            batch=w['selection'][str(t)]
            assert native.review(t,batch)==learner.review(t,batch)
    assert native.native_checkpoint()==learner.native_checkpoint()
    saved, original=learner.checkpoint(),native.checkpoint()
    active=w['main'][640:896]
    def frozen(row):
        return initial[(*row['x'],row['a'])]
    frozen_loss=mean(mean((p-y)**2 for p,y in zip(frozen(row),labels(row))) for row in active)
    split=[]
    for j in range(2):
        created=any(len(set(batch[j]['decision']['before']['partition']))==1 and
                    len(set(batch[j]['decision']['after']['partition']))>1 for batch in acquisition['warmup'])
        gain=mean((pooled[j]-labels(row)[j])**2-(frozen(row)[j]-labels(row)[j])**2 for row in active)
        split.append(created and gain>0)
    for target in (w['affected'],2):
        d=choose(describe(learner,target,w['main'][576:640]))
        branches={arm:run_arm(saved,original,w,history,target,d,arm) for arm in ARMS}
        yield dict(seed=w['seed'],proposal=ps,history=history,target=target,protected=1-w['affected'],
                   decision=d,branches=branches,frozen_loss=frozen_loss,split=split,
                   transfer_accuracy=acquisition['transfer']['accuracy'])


def ci(xs):
    rng=random.Random(429)
    vals=sorted(mean(rng.choices(xs,k=len(xs))) for _ in range(5000))
    def q(frac):
        z=(len(vals)-1)*frac
        return vals[int(z)]+(z-int(z))*(vals[int(z)+1]-vals[int(z)])
    return [mean(xs),q(.025),q(.975)]


def summary(records):
    seeds=sorted({r['seed'] for r in records})
    def gain(r,arm,window='active'):
        t=r['target']
        return r['branches']['none']['losses'][window][t]-r['branches'][arm]['losses'][window][t]
    improvements={a:ci([mean(gain(r,a) for r in records if r['seed']==s) for s in seeds]) for a in ARMS}
    errors={name:[] for name in ('named','aggregate')}
    material=correct=material_correct=0
    for r in records:
        for a in ARMS[1:]:
            actual=gain(r,a,'early')
            for name in errors:
                predicted=r['decision']['forecast'][name][a]
                errors[name].append(abs(predicted-actual))
            classify=lambda x: 1 if x>.001 else -1 if x<-.001 else 0
            right=classify(r['decision']['forecast']['named'][a])==classify(actual)
            correct+=right
            material+=abs(actual)>.001
            material_correct+=right and abs(actual)>.001
    guards=[]
    for h in HISTORIES:
        for win in ('active','release','return'):
            for j in range(3):
                rs=[r for r in records if r['history']==h and (win!='active' or h=='stable' or j==r['protected'])]
                if not rs:
                    continue
                costs=[r['branches']['budget']['losses'][win][j]-r['branches']['none']['losses'][win][j] for r in rs]
                guards.append(dict(history=h,window=win,output=j,mean=mean(costs),worst=max(costs),
                                   passed=mean(costs)<=.01 and max(costs)<=.05))
    changing=[r for r in records if r['history'] in ('lasting','forms','repeated')]
    learning_gain=mean(r['frozen_loss']-mean(r['branches']['none']['losses']['active']) for r in changing)
    useful=sum(any(any(r['split']) and r['transfer_accuracy']>=.875 for r in records if r['seed']==s and r['history']=='stable') for s in seeds)
    actions=sum(r['decision']['enabled'] for r in records)
    exhausted=sum('exhausted' in r['branches']['budget']['closed'] for r in records)
    maximum=max(b['error'] for r in records for b in r['branches'].values())
    effects=len(errors['named'])
    mae={k:mean(v) for k,v in errors.items()}
    gates=dict(learn=learning_gain>=.001 and useful==len(seeds),
               interpret=maximum<=1e-10 and mae['named']<=mae['aggregate']+1e-12 and correct/effects>=.75 and material>=16,
               steer=improvements['budget'][0]>=.001 and improvements['budget'][1]>0 and actions/len(records)>=.2 and exhausted>0 and all(g['passed'] for g in guards))
    return dict(gates=gates, cases=len(records), arms=len(records)*4, active_gains=improvements,
                budget_minus_uncapped_gain=ci([mean(gain(r,'budget')-gain(r,'cell') for r in records if r['seed']==s) for s in seeds]),
                cell_minus_channel_gain=ci([mean(gain(r,'cell')-gain(r,'channel') for r in records if r['seed']==s) for s in seeds]),
                actions=actions,exhausted=exhausted,guards=guards,one_step_and_debit_max_error=maximum,
                effect_mae=mae,correct=correct,effects=effects,material=material,material_correct=material_correct,
                learning_gain=learning_gain,useful_split_environments=useful,
                recovery={h:{'both_local_correct':mean(all(r['branches']['budget']['local_correct']) for r in records if r['history']==h),
                             'upper_accuracy':mean(r['branches']['budget']['upper_accuracy'] for r in records if r['history']==h)} for h in HISTORIES})


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=OUT)
    out=parser.parse_args().output
    out.mkdir(exist_ok=False)
    sources=['experiments/direction_strength_protocol.md','experiments/direction_strength_trial.py',
             'advaita/direction_strength.py','checks/test_direction_strength.py']
    sources += [str(p.relative_to(ROOT)) for p in (ROOT/'advaita').glob('*.py')]
    sources += ['experiments/memory_lifecycle.py','experiments/memory_control_v2.py']
    manifest={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(set(sources))}
    (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    records=[]
    with gzip.open(out/'cases.jsonl.gz','wt') as stream:
        for seed in range(3200,3208):
            for h in HISTORIES:
                w=world(seed,h)
                for ps in (3200,3201):
                    for rec in run_trunk(w,h,ps):
                        stream.write(json.dumps(rec)+'\n')
                        for b in rec['branches'].values():
                            del b['predictions'],b['cell_events']
                        records.append(rec)
            print(f'{seed}: {len(records)} cases',flush=True)
    result=summary(records)
    (out/'summary.json').write_text(json.dumps(result,indent=2)+'\n')
    print(result['gates'])


if __name__=='__main__':
    main()
