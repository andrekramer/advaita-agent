"""Stage-1 numerical predictors; deliberately separate from the agent runtime."""
import copy
import math
import random
from collections import deque

ARMS_A = ('vector', 'scalar', 'full', 'fixed', 'matched', 'rotor')
ARMS_B = ARMS_A + ('prior_matched', 'prior_selected', 'window')
FUTURES = ('stable', 'streak', 'reversal')
HISTORIES = ('short', 'long')
WINDOWS = dict(stable=(0, 128), streak=(4, 20), reversal=(0, 64))
GRIDS = dict(vector=[.90, .97, .99], fixed=[.01, .03, .10],
             rotor=[.02, .06, .20], prior_selected=[.90, .97, .99])


def world(seed):
    prefixes = {}
    for history, n, offset in [('short', 10, 100000), ('long', 1000, 200000)]:
        rows = [1]*(4*n//5) + [0]*(n//5)
        random.Random(offset+seed).shuffle(rows)
        prefixes[history] = rows
    stable_rng, reversal_rng = random.Random(300000+seed), random.Random(400000+seed)
    stable = [int(stable_rng.random() < .8) for _ in range(128)]
    futures = dict(stable=stable, streak=[0]*4+stable[4:],
                   reversal=[int(reversal_rng.random() < .2) for _ in range(128)])
    mirrored = bool(seed % 2)
    if mirrored:
        prefixes = {k: [1-y for y in v] for k, v in prefixes.items()}
        futures = {k: [1-y for y in v] for k, v in futures.items()}
    return dict(seed=seed, mirrored=mirrored, prefixes=prefixes, futures=futures)


class Predictor:
    def __init__(self, arm, parameter, suite, history, mirrored):
        self.arm, self.parameter = arm, parameter
        p = (.2 if mirrored else .8) if suite == 'A' else .5
        mass = (10. if history == 'short' else 1000.) if suite == 'A' else 2.
        self.a, self.b = p*mass, (1-p)*mass
        self.p, self.mass = p, mass
        self.theta = math.atan2(1-p, p)
        self.raw_a = self.raw_b = 0.
        self.buffer = deque()

    def clone(self):
        return copy.deepcopy(self)

    def predict(self):
        if self.arm in ('vector', 'full'):
            return self.a/(self.a+self.b)
        if self.arm in ('scalar', 'fixed', 'matched'):
            return self.p
        if self.arm == 'rotor':
            return math.cos(self.theta)/(math.cos(self.theta)+math.sin(self.theta))
        if self.arm.startswith('prior_'):
            rho = self.parameter
            return (rho*self.raw_a+1)/(rho*(self.raw_a+self.raw_b)+2)
        return (sum(self.buffer)+1)/(len(self.buffer)+2)

    def state(self):
        p = self.predict()
        if self.arm in ('vector', 'full'):
            mass = self.a+self.b
            effective = self.parameter*mass
        elif self.arm == 'scalar':
            mass, effective = self.mass, self.parameter*self.mass
        elif self.arm.startswith('prior_'):
            mass = self.raw_a+self.raw_b+2
            effective = self.parameter*(mass-2)+2
        elif self.arm == 'window':
            mass = effective = len(self.buffer)+2
        else:
            mass = effective = None
        return dict(p=p, S_stored=mass, S_prediction=effective,
                    theta=math.atan2(1-p, p))

    def update(self, y):
        if self.arm in ('vector', 'full'):
            self.a = self.parameter*self.a+y
            self.b = self.parameter*self.b+1-y
            return self.a/(self.a+self.b)
        if self.arm == 'scalar':
            self.mass = self.parameter*self.mass+1
            self.p += (y-self.p)/self.mass
            return self.p
        if self.arm in ('fixed', 'matched'):
            self.p += self.parameter*(y-self.p)
            return self.p
        if self.arm == 'rotor':
            p = self.predict()
            self.theta += self.parameter*math.sqrt(p*(1-p))*math.sin((0 if y else math.pi/2)-self.theta)
            assert 0 <= self.theta <= math.pi/2
            return self.predict()
        if self.arm.startswith('prior_'):
            self.raw_a = self.parameter*self.raw_a+y
            self.raw_b = self.parameter*self.raw_b+1-y
            return (self.raw_a+1)/(self.raw_a+self.raw_b+2)
        self.buffer.append(y)
        if len(self.buffer) > 192:
            self.buffer.popleft()
        return self.predict()


def parameter(arm, chosen):
    if arm in ('vector', 'scalar', 'prior_matched'):
        return chosen['vector']
    if arm == 'matched':
        return 1-chosen['vector']
    if arm == 'full':
        return 1.
    if arm == 'window':
        return 192
    return chosen[arm]


def metrics(ps, labels, future, mirrored):
    start, stop = WINDOWS[future]
    q = [.2 if future == 'reversal' else .8]*128
    if future == 'streak':
        q[:4] = [0.]*4
    if mirrored:
        q = [1-x for x in q]
    losses = [(p-y)**2 for p, y in zip(ps, labels)]
    mean = lambda values: sum(values)/len(values)
    recovery = None
    if future == 'reversal':
        correct = [p > .5 if mirrored else p < .5 for p in ps]
        recovery = next((i for i in range(125) if all(correct[i:i+4])), None)
    return dict(brier=mean(losses[start:stop]), whole_brier=mean(losses),
                mean_forecast=mean(ps[start:stop]), mean_target=mean(q[start:stop]),
                excess_brier=mean([(ps[i]-q[i])**2 for i in range(start, stop)]),
                forced_brier=mean(losses[:4]) if future == 'streak' else None,
                recovery_seen=recovery, censored=(recovery is None) if future == 'reversal' else None,
                recovery_capped=(128 if recovery is None else recovery) if future == 'reversal' else None)


def simulate(w, suite, history, arm, value, traces=False):
    base = Predictor(arm, value, suite, history, w['mirrored'])
    if suite == 'B':
        for y in w['prefixes'][history]:
            base.predict()
            base.update(y)
    records = []
    for future in FUTURES:
        model = base.clone()
        initial = model.state()
        ps, events = [], []
        first_turn = None
        for i, y in enumerate(w['futures'][future]):
            p = model.predict()
            before = model.state() if traces else None
            assert 0 <= p <= 1 and math.isfinite(p)
            ps.append(p)
            after = model.update(y)
            if i == 0:
                first_turn = after-p
            if traces:
                events.append(dict(observations_seen=i, y=y, **before,
                                   p_after_label=after, delta_p=after-p,
                                   row='category0|action0', output_source='isolated_row'))
        records.append(dict(seed=w['seed'], mirrored=w['mirrored'], suite=suite,
                            history=history, future=future, arm=arm, parameter=value,
                            initial=initial, first_turn=first_turn, predictions=ps,
                            metrics=metrics(ps, w['futures'][future], future, w['mirrored']),
                            events=events))
    return records


def percentile(values, q):
    values = sorted(values)
    index = (len(values)-1)*q
    left = int(index)
    return values[left]+(values[min(left+1, len(values)-1)]-values[left])*(index-left)


def gate(contrasts):
    return all(contrasts[control][future]['high'] < (0 if future == 'streak' else .01)
               for control in ('window', 'fixed') for future in FUTURES)


def summarize(records):
    index = {(r['seed'], r['suite'], r['history'], r['future'], r['arm']): r for r in records}
    seeds = sorted({r['seed'] for r in records})
    controls = [a for a in ARMS_B if a not in ('vector', 'scalar')]
    differences = {}
    contrasts = {a: {} for a in controls}
    for a in controls:
        for f in FUTURES:
            ds = [sum(index[s, 'B', h, f, 'vector']['metrics']['brier']-
                      index[s, 'B', h, f, a]['metrics']['brier'] for h in HISTORIES)/2 for s in seeds]
            differences[a, f] = ds
            contrasts[a][f] = dict(mean=sum(ds)/len(ds),
                by_history={h: sum(index[s, 'B', h, f, 'vector']['metrics']['brier']-
                                   index[s, 'B', h, f, a]['metrics']['brier'] for s in seeds)/len(seeds)
                            for h in HISTORIES})
    boot = {k: [] for k in differences}
    rng = random.Random(77)
    for _ in range(10000):
        sampled = [rng.randrange(len(seeds)) for _ in seeds]
        for k, ds in differences.items():
            boot[k].append(sum(ds[i] for i in sampled)/len(seeds))
    for (a, f), values in boot.items():
        contrasts[a][f].update(low=percentile(values, .025), high=percentile(values, .975))
    aggregates = []
    for suite, arms in [('A', ARMS_A), ('B', ARMS_B)]:
        for h in HISTORIES:
            for f in FUTURES:
                for a in arms:
                    rows = [index[s, suite, h, f, a] for s in seeds]
                    fields = ('brier', 'whole_brier', 'mean_forecast', 'mean_target',
                              'excess_brier', 'forced_brier', 'recovery_capped', 'censored')
                    aggregates.append(dict(suite=suite, history=h, future=f, arm=a,
                        **{k: (None if rows[0]['metrics'][k] is None else
                               sum(r['metrics'][k] for r in rows)/len(rows)) for k in fields}))
    error = max(abs(p-q) for r in records if r['arm'] == 'vector'
                for p, q in zip(r['predictions'], index[r['seed'], r['suite'], r['history'], r['future'], 'scalar']['predictions']))
    assert error <= 1e-12, error
    return dict(contrasts=contrasts, aggregates=aggregates,
                tradeoff_pass=gate(contrasts), scalar_max_error=error)
