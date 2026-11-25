"""Paired active-group capacity pilot. Run with python3 experiments/managed_growth.py."""
import copy
import json
import random
import sys
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.memory_control import PARTS, fit_local, local_p
from advaita.recall_withdrawal import RecallWithdrawal
from advaita.structural import StructuralLearner

OUT = ROOT / "results/managed-growth-v1"
POOL = (0, 0, 0, 0)
DECIDE, RETURN, END = 384, 640, 832
SOURCES = "ABCD"


class BudgetLearner(RecallWithdrawal):
    """Constrain local proposals together before the upper channel sees their groups."""
    budget = 3

    def review_channel(self, j, rows):
        result = super().review_channel(j, rows)
        if j == 1 and sum(len(m["counts"]) for m in self.locals) > self.budget:
            pooled = [fit_local(POOL, self.combined(k)) for k in (0, 1)]
            costs = [self.loss(k, pooled[k], rows) - self.loss(k, self.locals[k], rows)
                     for k in (0, 1)]
            sacrifice = costs.index(min(costs))
            self.locals[sacrifice] = pooled[sacrifice]
            self.pending[sacrifice] = None
        return result


def inspection(learner):
    costs, splits = [], []
    for table in learner.fast[:2]:
        mass = sum(n for _, n in table)
        def error(part):
            model = fit_local(part, table)
            return sum(s * (1 - local_p(model, i))**2 + (n - s) * local_p(model, i)**2
                       for i, (s, n) in enumerate(table)) / mass
        split = min(PARTS[1:], key=error)
        costs.append(error(POOL) - error(split))
        splits.append(split)
    gain = min(costs) / 2
    return dict(pool_cost=costs, splits=splits, predicted_gain=gain,
                cheaper_channel=costs.index(min(costs)), permit=gain > .01)


def make_world(seed, valuable, *, end=END):
    rng = random.Random(seed)
    maps = [rng.sample([0, 0, 1, 1], 4) for _ in (0, 1)]
    def sample(t):
        x = [rng.randrange(4), rng.randrange(4)]
        b, d = [mapping[i] for mapping, i in zip(maps, x)]
        p = .1 if b and 256 < t <= RETURN else .9
        q = (.2 if d else .8) if valuable or t <= 256 else .5
        labels = [int(rng.random() < v) for v in (p, q)]
        action = rng.randrange(2)
        return dict(x=x, a=action, local=labels, y=labels[0] ^ labels[1] ^ action)
    stream = {t: sample(t) for t in range(1, end + 1)}
    batches = {t: [sample(t) for _ in range(96)] for t in range(64, end+1, 64)}
    return maps, stream, batches


def parts(learner):
    return [m["partition"].copy() for m in learner.locals]


def continuation(learner, budget, maps, stream, batches):
    learner.budget = budget
    reviews = {}
    windows = {}
    for tick in range(DECIDE, END + 1):
        if tick > DECIDE:
            row = stream[tick]
            groups = [len(m["counts"]) for m in learner.locals]
            assert sum(groups) <= budget
            phase = 'changed' if tick <= RETURN else 'return'
            window = windows.setdefault(phase, dict(errors={s: [] for s in SOURCES},
                                                    extra_ticks=0, pooled_ticks=[0, 0]))
            window['extra_ticks'] += int(sum(groups) == 4)
            predictions = learner.observe(tick, row)
            for j in (0, 1):
                window['pooled_ticks'][j] += int(groups[j] == 1)
                name = SOURCES[2*j + maps[j][row['x'][j]]]
                window['errors'][name].append((predictions[j] - row['local'][j])**2)
        if tick in batches:
            learner.review(tick, batches[tick])
            reviews[tick] = parts(learner)
            assert sum(len(set(part)) for part in reviews[tick]) <= budget
    for window in windows.values():
        errors = window.pop('errors')
        window['source_loss'] = {s: mean(v) for s, v in errors.items()}
        window['loss'] = mean(mean(errors[a]+errors[b]) for a,b in ('AB','CD'))
    return dict(windows=windows, reviews=reviews)


def case(seed, valuable):
    maps, stream, batches = make_world(seed, valuable)
    core = StructuralLearner([seed*3, seed*3+1], seed*3+2)
    core.train_upper([], [])
    learner = BudgetLearner(core, 'shadow')
    for t in range(1, DECIDE + 1):
        learner.observe(t, stream[t])
        if t in batches and t < DECIDE:
            learner.review(t, batches[t])
        if t == 256:
            acquired = parts(learner)
    forecast = inspection(learner)
    branches = {b: continuation(copy.deepcopy(learner), b, maps, stream, batches) for b in (3, 4)}
    return dict(seed=seed, condition='valuable' if valuable else 'redundant', maps=maps,
                acquired=acquired, before=parts(learner), forecast=forecast, branches=branches)


def interval(values):
    rng = random.Random(829)
    boot = sorted(mean(rng.choices(values, k=len(values))) for _ in range(3000))
    return [mean(values), boot[74], boot[2924]]


def summarize(cases):
    summary = {}
    for condition in ('valuable','redundant'):
        rows = [r for r in cases if r['condition'] == condition]
        permits = [r['forecast']['permit'] for r in rows]
        out = dict(cases=len(rows), permissions=sum(permits))
        for phase in ('changed','return'):
            fixed = [r['branches'][3]['windows'][phase] for r in rows]
            extra = [r['branches'][4]['windows'][phase] for r in rows]
            gains = [a['loss']-b['loss'] for a,b in zip(fixed,extra)]
            selected = [g if permit else 0 for g,permit in zip(gains,permits)]
            out[phase] = dict(fourth_group_gain=interval(gains), selected_gain=interval(selected),
                selected_cost_vs_always_four=mean(g-s for g,s in zip(gains,selected)),
                forecast_hits=sum((g>.01)==p for g,p in zip(gains,permits)),
                extra_ticks_when_permitted=sum(w['extra_ticks'] for w,p in zip(extra,permits) if p),
                extra_ticks_always=sum(w['extra_ticks'] for w in extra),
                fixed_pooled_ticks=[sum(w['pooled_ticks'][j] for w in fixed) for j in (0,1)],
                source_gain={s:mean(a['source_loss'][s]-b['source_loss'][s] for a,b in zip(fixed,extra))
                             for s in SOURCES},
                B_loss_fixed=mean(w['source_loss']['B'] for w in fixed),
                B_loss_four=mean(w['source_loss']['B'] for w in extra))
        summary[condition] = out
    return summary


if __name__ == '__main__':
    cases = [case(seed, valuable) for seed in range(4100,4124) for valuable in (True,False)]
    OUT.mkdir(exist_ok=True)
    (OUT/'cases.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in cases))
    (OUT/'summary.json').write_text(json.dumps(summarize(cases), indent=2)+'\n')
