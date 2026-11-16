"""Independent reconstruction; imports no predictor, runner or metric code."""
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import signal
import time

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/heaviside-prediction-v1'
FUTURES = ('stable', 'streak', 'reversal')
GRIDS = dict(vector=[.9, .97, .99], fixed=[.01, .03, .10],
             rotor=[.02, .06, .20], prior_selected=[.9, .97, .99])


def equal(a, b):
    if isinstance(a, dict):
        assert set(a) == set(b), (set(a), set(b))
        for k in a: equal(a[k], b[k])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b): equal(x, y)
    elif isinstance(a, float):
        assert math.isfinite(a) and abs(a-b) <= 1e-12, (a, b)
    else:
        assert a == b, (a, b)


def regenerate(seed):
    mirror = bool(seed % 2)
    prefixes = {}
    for h, length, offset in [('short', 10, 100000), ('long', 1000, 200000)]:
        ys = [1]*(length*4//5)+[0]*(length//5)
        random.Random(seed+offset).shuffle(ys)
        prefixes[h] = [1-y if mirror else y for y in ys]
    rng = random.Random(seed+300000)
    stable = [int(rng.random() < .8) for _ in range(128)]
    rng = random.Random(seed+400000)
    reverse = [int(rng.random() < .2) for _ in range(128)]
    futures = dict(stable=stable, streak=[0]*4+stable[4:], reversal=reverse)
    return dict(seed=seed, mirrored=mirror, prefixes=prefixes,
                futures={k: [1-y if mirror else y for y in ys] for k, ys in futures.items()})


def reconstruct(w, suite, h, arm, par, future):
    initial_p = (.2 if w['mirrored'] else .8) if suite == 'A' else .5
    initial_mass = (10. if h == 'short' else 1000.) if suite == 'A' else 2.
    success, total, p = initial_p*initial_mass, initial_mass, initial_p
    if arm.startswith('prior_'):
        success = total = 0.
    buffer = []

    def read():
        if arm in ('vector', 'scalar', 'full'):
            return success/total
        if arm.startswith('prior_'):
            return (par*success+1)/(par*total+2)
        if arm == 'window':
            return (sum(buffer)+1)/(len(buffer)+2)
        return p

    def snap():
        if arm in ('vector', 'scalar', 'full'):
            stored, effective = total, par*total
        elif arm.startswith('prior_'):
            stored, effective = total+2, par*total+2
        elif arm == 'window':
            stored = effective = len(buffer)+2
        else:
            stored = effective = None
        q = read()
        return dict(p=q, S_stored=stored, S_prediction=effective, theta=math.atan2(1-q, q))

    def update(y):
        nonlocal success, total, p, buffer
        if arm in ('vector', 'scalar', 'full') or arm.startswith('prior_'):
            success, total = par*success+y, par*total+1
            return (success+1)/(total+2) if arm.startswith('prior_') else success/total
        if arm in ('fixed', 'matched'):
            p = (1-par)*p+par*y
            return p
        if arm == 'rotor':
            theta = math.atan2(1-p, p)
            theta += par*math.sqrt(p*(1-p))*math.sin((math.pi/2 if y == 0 else 0)-theta)
            p = 1/(1+math.tan(theta))
            return p
        buffer = (buffer+[y])[-192:]
        return read()

    if suite == 'B':
        for y in w['prefixes'][h]: update(y)
    initial = snap()
    ps, events = [], []
    for i, y in enumerate(w['futures'][future]):
        before = snap()
        ps.append(before['p'])
        after = update(y)
        events.append(dict(observations_seen=i, y=y, **before, p_after_label=after,
                           delta_p=after-before['p'], row='category0|action0', output_source='isolated_row'))
    return initial, ps, events


def measure(ps, labels, future, mirror):
    bounds = dict(stable=(0, 128), streak=(4, 20), reversal=(0, 64))
    lo, hi = bounds[future]
    targets = [(.2 if future == 'reversal' else .8) for _ in ps]
    if future == 'streak': targets[:4] = [0.]*4
    if mirror: targets = [1-q for q in targets]
    loss = [(p-y)*(p-y) for p, y in zip(ps, labels)]
    delay = None
    if future == 'reversal':
        for i in range(125):
            if all((p > .5 if mirror else p < .5) for p in ps[i:i+4]):
                delay = i
                break
    return dict(brier=sum(loss[lo:hi])/(hi-lo), whole_brier=sum(loss)/128,
                mean_forecast=sum(ps[lo:hi])/(hi-lo), mean_target=sum(targets[lo:hi])/(hi-lo),
                excess_brier=sum((ps[i]-targets[i])**2 for i in range(lo, hi))/(hi-lo),
                forced_brier=sum(loss[:4])/4 if future == 'streak' else None,
                recovery_seen=delay, censored=delay is None if future == 'reversal' else None,
                recovery_capped=(128 if delay is None else delay) if future == 'reversal' else None)


def hashes():
    manifest = json.loads((OUT/'manifest.json').read_text())
    for path, digest in {**manifest['sources'], **manifest['frozen_dependencies']}.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == digest, path
    for path, digest in json.loads((OUT/'artifact-hashes.json').read_text()).items():
        assert hashlib.sha256((OUT/path).read_bytes()).hexdigest() == digest, path


def main():
    start = time.monotonic()
    destination = OUT/'audit.json'
    assert not destination.exists()
    def timeout(*_): raise TimeoutError('Independent audit 900-second ceiling')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(900)
    checked = 0
    try:
        hashes()
        dev = json.loads((OUT/'development-worlds.json').read_text())
        confirmation = json.loads((OUT/'confirmation-worlds.json').read_text())
        equal(dev, [regenerate(s) for s in range(32)])
        equal(confirmation, [regenerate(s) for s in range(1000, 1200)])
        selected = json.loads((OUT/'selection.json').read_text())
        with (OUT/'development-metrics.csv').open() as f:
            development_rows = iter(list(csv.DictReader(f)))
        for arm, grid in GRIDS.items():
            values = []
            for value in grid:
                losses = []
                for w in dev:
                    for h in ('short', 'long'):
                        for future in FUTURES:
                            _, ps, _ = reconstruct(w, 'B', h, arm, value, future)
                            loss = measure(ps, w['futures'][future], future, w['mirrored'])['brier']
                            losses.append(loss)
                            row = next(development_rows)
                            equal((int(row['seed']), row['history'], row['future'], row['arm'], float(row['parameter'])),
                                  (w['seed'], h, future, arm, value))
                            equal(float(row['brier']), loss)
                values.append(sum(losses)/len(losses))
            equal(selected['scores'][arm], [dict(parameter=p, objective=v) for p, v in zip(grid, values)])
            equal(selected['chosen'][arm], grid[min(range(3), key=lambda i: (values[i], i))])
        assert next(development_rows, None) is None
        print('Development worlds, 2,304 scores and selections reconstructed.', flush=True)
        worlds = {w['seed']: w for w in confirmation}
        index = {}
        with (OUT/'metrics.csv').open() as f:
            metrics_rows = iter(list(csv.DictReader(f)))
        with gzip.open(OUT/'runs.jsonl.gz', 'rt') as stream:
            for line in stream:
                r = json.loads(line)
                w = worlds[r['seed']]
                arm = r['arm']
                chosen = selected['chosen']
                par = (chosen['vector'] if arm in ('vector', 'scalar', 'prior_matched') else
                       1-chosen['vector'] if arm == 'matched' else 1. if arm == 'full' else
                       192 if arm == 'window' else chosen[arm])
                equal(r['parameter'], par)
                initial, ps, events = reconstruct(w, r['suite'], r['history'], arm, par, r['future'])
                equal(r['initial'], initial)
                equal(r['predictions'], ps)
                equal(r['first_turn'], events[0]['delta_p'])
                if r['seed'] in (1000, 1001): equal(r['events'], events)
                else: equal(r['events'], [])
                equal(r['metrics'], measure(ps, w['futures'][r['future']], r['future'], w['mirrored']))
                equal(r['mirrored'], w['mirrored'])
                row = next(metrics_rows)
                for k in ('seed', 'suite', 'history', 'future', 'arm'):
                    equal(row[k], str(r[k]))
                equal(row['mirrored'], str(r['mirrored']))
                equal(float(row['parameter']), par)
                equal(float(row['first_turn']), r['first_turn'])
                for k, value in {**r['metrics'], **{'initial_'+k: v for k, v in r['initial'].items()}}.items():
                    equal(row[k], '' if value is None else str(value))
                equal(int(row['effective_updates']), (len(w['prefixes'][r['history']]) if r['suite'] == 'B' else 0)+128)
                equal((row['row'], row['output_source']), ('category0|action0', 'isolated_row'))
                key = r['seed'], r['suite'], r['history'], r['future'], arm
                assert key not in index
                index[key] = r
                checked += 1
                if checked % 4500 == 0: print(f'Reconstructed {checked}/18000 runs.', flush=True)
        assert next(metrics_rows, None) is None
        arms_a = ('vector', 'scalar', 'full', 'fixed', 'matched', 'rotor')
        arms_b = arms_a+('prior_matched', 'prior_selected', 'window')
        expected = {(s, suite, h, f, a) for s in range(1000, 1200)
                    for suite, arms in [('A', arms_a), ('B', arms_b)]
                    for h in ('short', 'long') for f in FUTURES for a in arms}
        assert set(index) == expected
        result = json.loads((OUT/'results.json').read_text())
        equal(result['selection'], chosen)
        equal(result['selection_sha256'], hashlib.sha256((OUT/'selection.json').read_bytes()).hexdigest())
        equal(selected['development_world_sha256'], hashlib.sha256((OUT/'development-worlds.json').read_bytes()).hexdigest())
        equal(selected['development_metrics_sha256'], hashlib.sha256((OUT/'development-metrics.csv').read_bytes()).hexdigest())
        equal(selected['sources'], json.loads((OUT/'manifest.json').read_text())['sources'])
        summary = result['summary']
        for row in summary['aggregates']:
            rs = [index[s, row['suite'], row['history'], row['future'], row['arm']] for s in range(1000, 1200)]
            for k, value in row.items():
                if k in ('suite', 'history', 'future', 'arm'): continue
                equal(value, None if rs[0]['metrics'][k] is None else sum(r['metrics'][k] for r in rs)/200)
        differences, samples = {}, {}
        for a, futures in summary['contrasts'].items():
            for f, value in futures.items():
                pairs = [[index[s, 'B', h, f, 'vector']['metrics']['brier']-index[s, 'B', h, f, a]['metrics']['brier']
                          for s in range(1000, 1200)] for h in ('short', 'long')]
                ds = [(x+y)/2 for x, y in zip(*pairs)]
                equal(value['mean'], sum(ds)/200)
                equal(value['by_history'], dict(short=sum(pairs[0])/200, long=sum(pairs[1])/200))
                differences[a, f], samples[a, f] = ds, []
        rng = random.Random(77)
        for _ in range(10000):
            multiplicity = [0]*200
            for _ in range(200): multiplicity[rng.randrange(200)] += 1
            for key, ds in differences.items():
                samples[key].append(sum(n*d for n, d in zip(multiplicity, ds))/200)
        for (a, f), values in samples.items():
            values.sort()
            for name, q in [('low', .025), ('high', .975)]:
                x = 9999*q
                i = int(x)
                equal(summary['contrasts'][a][f][name], values[i]*(1-(x-i))+values[i+1]*(x-i))
        passed = all(summary['contrasts'][a][f]['high'] < (0 if f == 'streak' else .01)
                     for a in ('window', 'fixed') for f in FUTURES)
        equal(passed, summary['tradeoff_pass'])
        maximum = max(abs(p-q) for key, r in index.items() if key[-1] == 'vector'
                      for p, q in zip(r['predictions'], index[(*key[:-1], 'scalar')]['predictions']))
        assert maximum <= 1e-12
        equal(maximum, summary['scalar_max_error'])
        equal(result['counts'], dict(development_runs=2304, confirmation_runs=18000,
              development_prefix_updates=387840, development_future_updates=294912,
              confirmation_prefix_updates=1818000, confirmation_future_updates=2304000,
              materialized_label_entries=323408, distinct_constructed_labels_including_forced=294640))
        hashes()
        data = dict(status='pass', reconstructed_confirmation_runs=checked,
                    reconstructed_development_runs=2304, tradeoff_pass=passed,
                    scalar_max_error=maximum, elapsed_seconds=time.monotonic()-start)
    except BaseException as exc:
        data = dict(status='failed', error=repr(exc), reconstructed_confirmation_runs=checked,
                    elapsed_seconds=time.monotonic()-start)
        raise
    finally:
        signal.alarm(0)
        with destination.open('x') as stream:
            json.dump(data, stream, indent=2)
            stream.write('\n')
    print(json.dumps(data), flush=True)


if __name__ == '__main__':
    main()
