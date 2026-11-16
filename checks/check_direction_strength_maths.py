"""Check the evidence equations using two pole tallies per bank on recorded histories.

Review choices are supplied by the working learner. Reconstruct evidence from
the acquisition buffers and subsequent labels, never from a fitted bank.
"""
import gzip
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'experiments'))
from advaita.direction_strength import DirectionStrengthLearner
from advaita.structural import StructuralLearner
from direction_strength_trial import world, life

FAST, SLOW, STEERED = (2 ** (-1/h) for h in (64, 1024, 128))
TOL = 1e-10


def empty_tables():
    return [[[0., 0.] for _ in range(n)] for n in (4, 4, 32)]


def indices(x, action):
    return [*x, 8*x[0] + 2*x[1] + action]


def members(partitions, spec, x, action):
    local = [[i for i, group in enumerate(part) if group == part[x[j]]]
             for j, part in enumerate(partitions)]
    upper_inputs = [range(4) if mode == 0 else local[j] if mode == 1 else [x[j]]
                    for j, mode in enumerate(spec)]
    upper = [8*i + 2*k + action for i in upper_inputs[0] for k in upper_inputs[1]]
    return [*local, upper]


def totals(fast, slow, channel, cell):
    return [sum(bank[channel][i][pole] for bank in (fast, slow) for i in cell)
            for pole in (0, 1)]


def probability(poles):
    return (1 + poles[1]) / (2 + sum(poles))


def replay(case, counts, maxima):
    def compare(field, actual, expected):
        error = abs(actual - expected)
        if not error <= TOL:
            raise AssertionError((field, actual, expected))
        maxima[field] = max(maxima.get(field, 0.), error)

    w = world(case['seed'], case['history'])
    _, encoded = life.legacy_run(w, case['proposal'], True)
    core = StructuralLearner.restore(encoded)
    learner = DirectionStrengthLearner(core)
    fast, slow = empty_tables(), empty_tables()
    for j, node in enumerate(core.nodes):
        for r in node.buffer:
            fast[j][r['x']][r['y']] += 1
    for r in core.buffer:
        fast[2][indices(r['x'], r['a'])[2]][r['y']] += 1
    parts = [n.model.state()['partition'] for n in core.nodes]
    spec = core.upper.state()['spec']
    branch = case['branches']['cell']
    closes = {e['tick'] for e in branch['cell_events'] if e['kind'] == 'close'}
    d = case['decision']
    target = case['target']
    bound = set()
    for t, row in enumerate(w['main'][:1152], 1):
        cell_members = members(parts, spec, row['x'], row['a'])
        cell = cell_members[target]
        preview = None
        if bound and set(cell) == bound:
            slow_poles = [sum(slow[target][i][k] for i in cell) for k in (0, 1)]
            baseline = [FAST * sum(fast[target][i][k] for i in cell) + SLOW * slow_poles[k]
                        for k in (0, 1)]
            extra = (SLOW - STEERED) * sum(slow_poles)
            p = probability(baseline)
            if extra:
                direction = slow_poles[1]/sum(slow_poles)
                preview = p + extra*(p-direction)/(2+sum(baseline)-extra)
            else:
                preview = p
        for j in range(3):
            for i, (f, s) in enumerate(zip(fast[j], slow[j])):
                rate = STEERED if j == target and i in bound else SLOW
                for pole in (0, 1):
                    f[pole] *= FAST
                    s[pole] *= rate
        observed = learner.observe(t, row)
        if preview is not None:
            compare('steering_preview', preview, observed[target])
            counts['targeted_previews'] += 1
        actual_after = learner.predict(row['x'], row['a'])['active']
        for j, (i, y, cell) in enumerate(zip(indices(row['x'], row['a']), row['local']+[row['y']], cell_members)):
            poles = totals(fast, slow, j, cell)
            p = probability(poles)
            compare('emitted_probability', p, observed[j])
            if t > 640:
                compare('saved_probability', p, branch['predictions'][t-641][j])
            fast[j][i][y] += 1
            compare('post_label_gain', p+(y-p)/(3+sum(poles)), actual_after[j])
        counts['ticks'] += 1
        counts['steered_ticks'] += bool(bound)
        if t % 64 == 0:
            review = learner.review(t, w['selection'][str(t)])
            counts['reviews'] += 1
            new_parts = [m['partition'] for m in review['post_review']['locals']]
            new_spec = review['post_review']['upper']['spec']
            counts['reviews_changing_partition_or_interface'] += (new_parts != parts or new_spec != spec)
            parts, spec = new_parts, new_spec
            for j, (weakening, transfer) in enumerate(zip(review['weakenings'], review['migrations'])):
                keep = .5 if weakening['accepted'] else 1.
                fraction = transfer['fraction'] if transfer['accepted'] else 0.
                counts['accepted_weakenings'] += weakening['accepted']
                counts['accepted_transfers'] += transfer['accepted']
                for f,s in zip(fast[j],slow[j]):
                    for pole in (0, 1):
                        moved = fraction * f[pole]
                        s[pole] = keep*s[pole]+moved
                        f[pole] -= moved
            # Check each pole separately after regrouping, across all contexts.
            for x,z,a in life.CONTEXTS:
                for j,cell in enumerate(members(parts,spec,[x,z],a)):
                    info = learner.inspect_cell(j,[x,z],a)
                    if sorted(cell) != info['binding']['members']:
                        raise AssertionError('raw members differ')
                    for bank, name in ((fast,'fast'), (slow,'slow')):
                        values = [sum(bank[j][i][pole] for i in cell) for pole in (0,1)]
                        compare('inspected_strength', sum(values), info[name]['strength'])
                        if sum(values):
                            compare('inspected_direction', values[1]/sum(values), info[name]['direction'])
                        elif info[name]['direction'] is not None:
                            raise AssertionError('empty bank has a direction')
        if t in closes:
            bound.clear()
        if t == 640 and d['enabled']:
            bound.update(d['selected']['members'])
            learner.open_cell(target,d['x'],d['a'],budget=None,through_tick=896,reason='maths replay')
        if bool(learner.cell_command) != bool(bound):
            raise AssertionError('command lifetime differs from recorded branch')
    counts['paths'] += 1


def main():
    counts, maxima = Counter(), {}
    folder = ROOT/'results/cell-duration-confirmation-v1'
    with gzip.open(folder/'cases.jsonl.gz','rt') as stream:
        for line in stream:
            r = json.loads(line)
            if r['seed']==3300 and r['proposal']==3300 and r['history'] in ('forms','repeated'):
                replay(r, counts, maxima)
    required = ('targeted_previews','reviews_changing_partition_or_interface','accepted_weakenings','accepted_transfers')
    if counts['paths'] != 4 or not all(counts[k] for k in required):
        raise AssertionError(f'Incomplete replay coverage: {counts}')
    print(json.dumps(dict(status='pass', tolerance=TOL, counts=counts, maximum_absolute_errors=maxima),indent=2))


if __name__=='__main__':
    main()
