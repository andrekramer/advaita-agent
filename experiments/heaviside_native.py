"""Stage2 native replay and contextual readout intervention; no engine edits."""
import copy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import signal
import sys
import time
from collections import deque

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT), str(ROOT/'experiments')]
from advaita.continuing import ContinuingLearner
from advaita.structural import StructuralLearner
from advaita.state import canonical
from advaita.memory_control import key as weighted_key
from heaviside_predictors import Predictor, percentile

OUT = ROOT/'results/heaviside-native-v1'
BACKBONES = ('reference', 'relaxed', 'combined')
HEADS = ('vector', 'scalar', 'fixed', 'window', 'prior_selected')
FUTURES = ('stable', 'streak', 'reversal')
HISTORIES = ('short', 'long')
FILES = ['experiments/heaviside_native_protocol.md', 'experiments/heaviside_native.py',
         'checks/test_heaviside_native.py', 'checks/audit_heaviside_native.py',
         'experiments/report_heaviside_native.py', 'results/heaviside-native-fixtures/attempt-01.json',
         'checks/structural_reference.py', 'checks/memory_revision_reference.py',
         'checks/memory_control_reference.py', 'checks/audit_nested_abstractions.py',
         'checks/audit_protection_interfaces.py']


def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()


def initial():
    with gzip.open(ROOT/'results/recall-withdrawal-v1/runs.jsonl.gz', 'rt') as f:
        r = json.loads(next(f))
    assert (r['seed'], r['history'], r['proposal_seed']) == (2600, 'stable', 2600)
    core = StructuralLearner.restore(canonical(r['acquisition_checkpoint']))
    core.variant = 'delete'
    assert core.archive.entry is None
    w = next(w for w in json.loads((ROOT/'results/recall-withdrawal-v1/worlds.json').read_text())
             if w['seed'] == 2600 and w['branch'] == 'stable')
    row_key = core.upper.key(core.upper.view([0, 0], core.models()), 0)
    labels = [row['y'] for row in w['composition'] if
              core.upper.key(core.upper.view(row['x'], core.models()), row['a']) == row_key]
    assert core.upper.counts[row_key] == [sum(labels), len(labels)] == [27, 32]
    return dict(core=json.loads(core.checkpoint()), acquisition_labels=labels,
                target=dict(x=[0, 0], a=0, local=[m.group(0) for m in core.models()]),
                initial_row=row_key, initial_counts=[27, 32], source='037 acquisition 2600/stable/2600')


def world(seed):
    mirror = bool(seed % 2)
    prefixes, prefix_reviews = {}, {}
    for h, n, offset, review_offset in [('short', 10, 600000, 1000000), ('long', 1000, 700000, 1100000)]:
        ys = [1]*(4*n//5)+[0]*(n//5)
        random.Random(seed+offset).shuffle(ys)
        prefixes[h] = ys
        rng = random.Random(seed+review_offset)
        prefix_reviews[h] = {str(t): [int(rng.random() < .8) for _ in range(32)]
                             for t in sorted(set(range(64, n+1, 64)) | {n})}
    rng = random.Random(800000+seed)
    stable = [int(rng.random() < .8) for _ in range(512)]
    rng = random.Random(900000+seed)
    futures = dict(stable=stable, streak=[0]*4+stable[4:],
                   reversal=[int(rng.random() < .2) for _ in range(512)])
    review = {}
    for f, offset, q in [('stable', 1200000, .8), ('reversal', 1300000, .2)]:
        rng = random.Random(seed+offset)
        review[f] = {str(t): [int(rng.random() < q) for _ in range(32)] for t in range(64, 513, 64)}
    review['streak'] = copy.deepcopy(review['stable'])
    flip = lambda ys: [1-y if mirror else y for y in ys]
    return dict(seed=seed, mirrored=mirror, prefixes={h: flip(ys) for h, ys in prefixes.items()},
                prefix_reviews={h: {t: flip(ys) for t, ys in rs.items()} for h, rs in prefix_reviews.items()},
                futures={f: flip(ys) for f, ys in futures.items()},
                reviews={f: {t: flip(ys) for t, ys in rs.items()} for f, rs in review.items()})


class ContextOutputs:
    def __init__(self, setup, backbone, mirrored):
        self.native = ContinuingLearner(StructuralLearner.restore(canonical(setup['core'])), memory=backbone)
        self.target, self.mirrored = copy.deepcopy(setup['target']), mirrored
        self.heads = {}
        n, total = setup['initial_counts']
        for arm in HEADS:
            p = Predictor(arm, .1 if arm == 'fixed' else 192 if arm == 'window' else .9, 'B', 'short', False)
            p.a, p.b = n+1., total-n+1.
            p.p, p.mass = (n+1)/(total+2), total+2.
            p.raw_a, p.raw_b = float(n), float(total-n)
            p.buffer = deque(setup['acquisition_labels'])
            self.heads[arm] = p

    def row(self, external_y, target=None):
        return dict(copy.deepcopy(self.target if target is None else target),
                    y=1-external_y if self.mirrored else external_y)

    def observe(self, external_y, target=None):
        row = self.row(external_y, target)
        matches = row['x'] == self.target['x'] and row['a'] == self.target['a']
        heads = {a: p.predict() for a, p in self.heads.items()}
        e = self.native.engine
        name = 'predict' if self.native.memory == 'reference' else 'predictions'
        original = getattr(e, name)
        assert name not in e.__dict__
        captured = {}
        def trace(x, action):
            result = original(x, action)
            if self.native.memory == 'reference':
                locals_, upper = [m.state() for m in e.models()], e.upper.state()
                k = e.upper.key(e.upper.view(x, e.models()), action)
            else:
                locals_, upper = e.locals, e.upper
                k = weighted_key(upper['spec'], locals_, x, action)
            captured.update(key=k, counts=upper['counts'][k].copy(), spec=upper['spec'].copy(),
                            groups=[m['groups'].copy() for m in locals_])
            return result
        setattr(e, name, trace)
        try:
            native = self.native.observe(self.native.tick+1, row)
        finally:
            delattr(e, name)
        assert abs(native[2]-(captured['counts'][0]+1)/(captured['counts'][1]+2)) < 1e-12
        outputs = dict(native=native[2], **{a: p if matches else native[2] for a, p in heads.items()})
        if self.mirrored: outputs = {a: 1-p for a, p in outputs.items()}
        pre = {a: p.state() for a, p in self.heads.items()}
        if matches:
            for p in self.heads.values(): p.update(row['y'])
        return dict(tick=self.native.tick, native_internal=native, outputs=outputs,
                    native_row=captured, head_state=pre, target_matched=matches,
                    sources={a: ('native' if a == 'native' or not matches else 'context_'+a) for a in outputs})

    def review(self, labels):
        before = copy.deepcopy({a: p.__dict__ for a, p in self.heads.items()})
        scores = {}
        for a, p in self.heads.items():
            q = 1-p.predict() if self.mirrored else p.predict()
            scores[a] = sum((q-y)**2 for y in labels)/len(labels)
        result = self.native.review(self.native.tick, [self.row(y) for y in labels])
        assert before == {a: p.__dict__ for a, p in self.heads.items()}
        return dict(tick=self.native.tick, native=result, head_review_brier=scores)

    def checkpoint(self):
        heads = {a: {k: list(v) if k == 'buffer' else v for k, v in p.__dict__.items()} for a, p in self.heads.items()}
        return canonical(dict(native=json.loads(self.native.checkpoint()), target=self.target,
                              mirrored=self.mirrored, heads=heads))

    @classmethod
    def restore(cls, saved):
        d = json.loads(saved)
        obj = object.__new__(cls)
        obj.native = ContinuingLearner.restore(canonical(d['native']))
        obj.target, obj.mirrored, obj.heads = d['target'], d['mirrored'], {}
        for a, value in d['heads'].items():
            p = object.__new__(Predictor)
            p.__dict__.update(value); p.buffer = deque(p.buffer)
            obj.heads[a] = p
        return obj


def metrics(ps, ys, future, mirrored):
    intervals = dict(stable=(0, 512), streak=(4, 20), reversal=(128, 256))
    loss = [(p-y)**2 for p, y in zip(ps, ys)]
    mean = lambda lo, hi: sum(loss[lo:hi])/(hi-lo)
    recovery = None
    if future == 'reversal':
        recovery = next((i for i in range(509) if all(p > .5 if mirrored else p < .5 for p in ps[i:i+4])), None)
    return dict(primary=mean(*intervals[future]), whole=mean(0, 512), early=mean(0, 64),
                late=mean(256, 512), forced=mean(0, 4) if future == 'streak' else None,
                recovery_seen=recovery, censored=recovery is None if future == 'reversal' else None,
                recovery_capped=(512 if recovery is None else recovery) if future == 'reversal' else None)


def summarize(records):
    index = {(r['seed'], r['history'], r['future'], r['backbone']): r for r in records}
    seeds = sorted({r['seed'] for r in records})
    # All alternative outputs must be identical across native backbones.
    for s in seeds:
        for h in HISTORIES:
            for f in FUTURES:
                for b in ('relaxed', 'combined'):
                    for a in HEADS:
                        assert index[s,h,f,b]['predictions'][a] == index[s,h,f,'reference']['predictions'][a]
    specs = {f'vector_vs_{b}': ('reference', 'vector', b, 'native') for b in BACKBONES}
    specs.update({f'vector_vs_{a}': ('reference', 'vector', 'reference', a) for a in ('fixed','window','prior_selected')})
    specs['combined_vs_relaxed'] = ('combined', 'native', 'relaxed', 'native')
    differences, result = {}, {k: {} for k in specs}
    for name, (cb, ca, bb, ba) in specs.items():
        for f in FUTURES:
            pairs = {h: [index[s,h,f,cb]['metrics'][ca]['primary']-index[s,h,f,bb]['metrics'][ba]['primary'] for s in seeds] for h in HISTORIES}
            ds = [(x+y)/2 for x,y in zip(pairs['short'], pairs['long'])]
            differences[name,f] = ds
            result[name][f] = dict(mean=sum(ds)/len(ds), by_history={h: sum(xs)/len(xs) for h,xs in pairs.items()})
    rng = random.Random(177); boot = {k: [] for k in differences}
    for _ in range(10000):
        indices = [rng.randrange(len(seeds)) for _ in seeds]
        for k, ds in differences.items(): boot[k].append(sum(ds[i] for i in indices)/len(seeds))
    for (name,f), xs in boot.items():
        result[name][f].update(low=percentile(xs,.025), high=percentile(xs,.975))
    passed = lambda name: all(result[name][f]['high'] < (0 if f == 'streak' else .01) for f in FUTURES)
    error = max(abs(p-q) for r in records for p,q in zip(r['predictions']['vector'],r['predictions']['scalar']))
    assert error <= 1e-12
    weakenings = []
    for r in records:
        if r['backbone'] == 'reference': continue
        for event in r['reviews']:
            for decision in event['native']['weakenings']:
                if decision['accepted']:
                    weakenings.append(dict(seed=r['seed'],history=r['history'],future=r['future'],
                        backbone=r['backbone'],relative_tick=event['relative_tick'],channel=decision['channel'],removed_mass=decision['removed_mass']))
    return dict(contrasts=result,native_pass=passed('vector_vs_reference') and passed('vector_vs_combined'),
                attribution_pass=passed('vector_vs_fixed'), scalar_max_error=error,
                accepted_future_weakenings=weakenings)


def write(name, data):
    with (OUT/name).open('x') as f: json.dump(data,f,indent=2); f.write('\n')


def run():
    OUT.mkdir(exist_ok=False); started=time.monotonic()
    def timeout(*_): raise TimeoutError('Native runner 900-second ceiling')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(900)
    try:
        fixture=json.loads((ROOT/'results/heaviside-native-fixtures/attempt-01.json').read_text())
        assert fixture['status']=='pass'
        for p,d in fixture['sources'].items(): assert sha(ROOT/p)==d,p
        parent=ROOT/'results/heaviside-prediction-v1'
        m=json.loads((parent/'manifest.json').read_text())
        frozen={**m['sources'],**m['frozen_dependencies']}
        for name in ('artifact-hashes.json','completion.json'):
            values=json.loads((parent/name).read_text())
            if name=='completion.json': values=values['verification_hashes']
            frozen.update({str((parent/p).relative_to(ROOT)):d for p,d in values.items()})
        for p,d in frozen.items(): assert sha(ROOT/p)==d,p
        sources={p:sha(ROOT/p) for p in FILES}
        setup=initial(); write('initial.json',setup)
        write('manifest.json',dict(date='2026-11-13',sources=sources,frozen_dependencies=frozen,
              initial_sha256=sha(OUT/'initial.json'),scope='one supplied familiar context; native updates unchanged'))
        worlds=[world(s) for s in range(3000,3040)];write('worlds.json',worlds)
        records=[]; prefix_count=0; restore_count=0
        with gzip.open(OUT/'prefixes.jsonl.gz','xt') as pf, gzip.open(OUT/'runs.jsonl.gz','xt') as rf:
            for w in worlds:
                for h in HISTORIES:
                    for b in BACKBONES:
                        learner=ContextOutputs(setup,b,w['mirrored']);events=[];reviews=[]
                        for t,y in enumerate(w['prefixes'][h],1):
                            events.append(learner.observe(y))
                            if str(t) in w['prefix_reviews'][h]: reviews.append(learner.review(w['prefix_reviews'][h][str(t)]))
                        saved=learner.checkpoint()
                        prefix=dict(seed=w['seed'],history=h,backbone=b,events=events,reviews=reviews,checkpoint=json.loads(saved))
                        pf.write(canonical(prefix)+'\n');prefix_count+=1
                        for future in FUTURES:
                            a=ContextOutputs.restore(saved);assert a.checkpoint()==saved;restore_count+=1
                            r=dict(seed=w['seed'],mirrored=w['mirrored'],history=h,future=future,backbone=b,
                                   predictions={arm:[] for arm in ('native',*HEADS)},events=[],reviews=[],restores=[])
                            for i,y in enumerate(w['futures'][future],1):
                                event=a.observe(y);event['relative_tick']=i;r['events'].append(event)
                                for arm,p in event['outputs'].items(): r['predictions'][arm].append(p)
                                if str(i) in w['reviews'][future]:
                                    rev=a.review(w['reviews'][future][str(i)]);rev['relative_tick']=i;r['reviews'].append(rev)
                                if i==128:
                                    c=a.checkpoint();a=ContextOutputs.restore(c);assert a.checkpoint()==c;restore_count+=1
                                    r['restores'].append(dict(relative_tick=i,sha256=hashlib.sha256(c.encode()).hexdigest()))
                            r['metrics']={arm:metrics(ps,w['futures'][future],future,w['mirrored']) for arm,ps in r['predictions'].items()}
                            r['checkpoint']=json.loads(a.checkpoint());rf.write(canonical(r)+'\n')
                            records.append({k:v for k,v in r.items() if k not in ('events','checkpoint')})
                print(f"Native comparison: {w['seed']-2999}/40 seeds",flush=True)
        with (OUT/'metrics.csv').open('x',newline='') as f:
            writer=None
            for r in records:
                for arm,m in r['metrics'].items():
                    row={k:r[k] for k in ('seed','history','future','backbone')};row.update(arm=arm,**m)
                    if writer is None: writer=csv.DictWriter(f,fieldnames=list(row));writer.writeheader()
                    writer.writerow(row)
        summary=summarize(records)
        for p,d in {**frozen,**sources}.items(): assert sha(ROOT/p)==d,p
        counts=dict(prefixes=prefix_count,native_futures=len(records),output_records=len(records)*6,
                    checkpoint_roundtrips=restore_count,main_rows=489840,review_rows=249600,
                    main_scalar_presentations=1469520,review_scalar_presentations=748800,
                    head_updates=2449200,materialized_composite_labels=154320,
                    distinct_constructed_composite_labels=123760)
        write('results.json',dict(status='completed_pending_audit',summary=summary,counts=counts,elapsed_seconds=time.monotonic()-started))
        artifacts=['initial.json','manifest.json','worlds.json','prefixes.jsonl.gz','runs.jsonl.gz','metrics.csv','results.json']
        write('artifact-hashes.json',{p:sha(OUT/p) for p in artifacts})
        print('Native gate:',summary['native_pass'],'Attribution gate:',summary['attribution_pass'],flush=True)
    except BaseException as exc:
        write('incomplete.json',dict(error=repr(exc),elapsed_seconds=time.monotonic()-started));raise
    finally: signal.alarm(0)


if __name__=='__main__': run()
