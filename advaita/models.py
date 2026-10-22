"""Shared conditional counts with explicit encodings and prediction boundaries.

Encodings and trace layouts preserve Experiments 012–015. No experiment code
is imported at runtime. Access restrictions here are API contracts, not a sandbox.
"""
import copy
import itertools as it
import math
import statistics as st


def nll(p, y):
    return -math.log(p if y else 1-p)


class CountTable:
    """Beta(1,1) probabilities; input encoders own the meaning of each cell."""
    def __init__(self, keys, *, positional=False):
        self.counts = [[0, 0] for _ in keys] if positional else {k: [0, 0] for k in keys}

    def add(self, key, outcome):
        self.counts[key][0] += outcome
        self.counts[key][1] += 1

    def probability(self, key):
        ones, total = self.counts[key]
        return (ones+1)/(total+2)


class CountModel:
    @property
    def counts(self):
        return self.table.counts

    @counts.setter
    def counts(self, value):
        self.table.counts = copy.deepcopy(value)


class ProjectionModel(CountModel):
    def __init__(self, subset=(), rows=()):
        self.subset = tuple(subset)
        self.table = CountTable(range(2**(len(subset)+1)), positional=True)
        for row in rows:
            self.table.add(self.index(row['x'], row['a']), row['y'])

    def index(self, x, action):
        index = 0
        for feature in self.subset:
            index = 2*index+x[feature]
        return 2*index+action

    def predict(self, x, action):
        return self.table.probability(self.index(x, action))

    def mean_loss(self, rows):
        return st.mean(nll(self.predict(r['x'], r['a']), r['y']) for r in rows)

    def state(self):
        return {'subset': list(self.subset), 'counts': copy.deepcopy(self.counts)}


class LocalModel(CountModel):
    def __init__(self, partition=(0, 0, 0, 0), rows=()):
        self.partition = tuple(partition)
        self.table = CountTable(sorted(set(partition)))
        for row in rows:
            self.table.add(self.partition[row['x']], row['y'])

    def predict(self, x):
        return self.table.probability(self.partition[x])

    def group(self, x):
        ordered = sorted(self.counts, key=lambda g: (self.table.probability(g), g))
        return ordered.index(self.partition[x])

    def state(self):
        return {'partition': list(self.partition),
                'counts': {str(k): v.copy() for k, v in self.counts.items()},
                'groups': [self.group(x) for x in range(4)]}

    def loss(self, rows):
        return st.mean(nll(self.predict(r['x']), r['y']) for r in rows)


class RestrictedView:
    def __init__(self, values, allowed):
        self._values = values
        self.allowed = frozenset(allowed)

    def read(self, key):
        if key not in self.allowed:
            raise PermissionError(f'Port {key} is hidden')
        return self._values[key]


class VisibleInput(RestrictedView):
    def __init__(self, raw, allowed):
        super().__init__(raw, allowed)
        self.reads = 0

    def __getitem__(self, key):
        value = self.read(key)
        self.reads += 1
        return value


class InterfaceView(RestrictedView):
    def __init__(self, groups, raw, mode):
        values = {('group', j): g for j, g in enumerate(groups)}
        values.update({('raw', j): x for j, x in enumerate(raw)})
        allowed = [('group', j) for j in range(len(groups))]
        allowed += [('raw', j) for j in range(len(raw)) if mode in ('flat', f'fine{j}')]
        super().__init__(values, allowed)
        self.mode = mode
        self.raw_reads = 0

    def group(self, j):
        return self.read(('group', j))

    def raw(self, j):
        value = self.read(('raw', j))
        self.raw_reads += 1
        return value


def view_for(x, models, mode):
    return InterfaceView([m.group(x[j]) for j, m in enumerate(models)], x, mode)


class Upper(CountModel):
    def __init__(self, mode='coarse', rows=(), models=()):
        if mode not in ('coarse', 'fine0', 'fine1', 'flat'):
            raise ValueError(f'Unknown exposure mode: {mode}')
        self.mode = mode
        dimensions = (4 if mode in ('flat', 'fine0') else 2,
                      4 if mode in ('flat', 'fine1') else 2, 2)
        keys = ['|'.join(map(str, key)) for key in it.product(*(range(n) for n in dimensions))]
        self.table = CountTable(keys)
        for row in rows:
            self.table.add(self.key(view_for(row['x'], models, mode), row['a']), row['y'])

    def key(self, view, a):
        values = [view.raw(j) if self.mode in ('flat', f'fine{j}') else view.group(j) for j in range(2)]
        return '|'.join(map(str, values+[a]))

    def predict(self, view, a):
        return self.table.probability(self.key(view, a))

    def state(self):
        return {'mode': self.mode, 'counts': copy.deepcopy(self.counts)}

    def loss(self, rows, models):
        return st.mean(nll(self.predict(view_for(r['x'], models, self.mode), r['a']), r['y']) for r in rows)


def restore_local(state):
    result = LocalModel(state['partition'])
    result.counts = {int(k): v for k, v in state['counts'].items()}
    return result


def restore_upper(state):
    result = Upper(state['mode'])
    result.counts = state['counts']
    return result


def restore_projection(state):
    result = ProjectionModel(state['subset'])
    result.counts = state['counts']
    return result
