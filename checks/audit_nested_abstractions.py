"""Independent arithmetic and stream replay; does not import the experiment."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/nested-abstractions-v1'
PARTS = [(0,)+p for p in itertools.product(range(2), repeat=3)]
CONTEXTS = list(itertools.product(range(4), range(4), range(2)))
BRANCHES = ('persistent', 'remap', 'breach')
VARIANTS = ('reopen', 'closed', 'frozen', 'flat')
H = -.1*math.log(.1)-.9*math.log(.9)
mean = statistics.mean


def close(a, b):
    if isinstance(a, dict):
        assert isinstance(b, dict) and a.keys() == b.keys(), (a.keys(), b.keys())
        for k in a:
            close(a[k], b[k])
    elif isinstance(a, (list, tuple)):
        assert len(a) == len(b), (len(a), len(b))
        for x, y in zip(a, b):
            close(x, y)
    elif isinstance(a, float) or isinstance(b, float):
        assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-10), (a, b)
    else:
        assert a == b, (a, b)


def logloss(p, y):
    return -math.log(p) if y else -math.log1p(-p)


def true_forms(w, phase):
    forms = copy.deepcopy(w['forms'])
    if phase and w['branch'] == 'remap':
        j = w['affected']
        for x in w['representatives'][j]:
            forms[j][x] = 1-forms[j][x]
    return forms


def true_y(w, x, a, phase):
    forms = true_forms(w, phase)
    y = (forms[0][x[0]]+forms[1][x[1]]+a) % 2
    if phase and w['branch'] == 'breach':
        j = w['affected']
        y = (y+int(x[j] != w['representatives'][j][forms[j][x[j]]])) % 2
    return y


def verify_world(w):
    rng = random.Random(61000+w['seed'])
    groups, reps = [], []
    for j in range(2):
        permutation = list(range(4))
        rng.shuffle(permutation)
        groups.append([0 if x in permutation[:2] else 1 for x in range(4)])
        reps.append([permutation[0], permutation[2]])
    assert w['forms'] == groups and w['representatives'] == reps
    assert w['affected'] == rng.randrange(2)
    inputs, noise = random.Random(62000+w['seed']), random.Random(63000+w['seed'])

    def local(n, j):
        output = []
        for start in range(0, n, 4):
            xs = [0, 1, 2, 3]
            inputs.shuffle(xs)
            for x in xs:
                output.append({'x': x, 'y': (groups[j][x]+(noise.random() < .1)) % 2})
        return output

    assert w['local_main'] == [local(256, j) for j in range(2)]
    assert w['local_selection'] == [[local(32, j) for j in range(2)] for _ in range(4)]
    composition = []
    for start in range(0, 256, 8):
        block = [(x, z, a) for x in reps[0] for z in reps[1] for a in range(2)]
        inputs.shuffle(block)
        for x, z, a in block:
            composition.append({'x': [x, z], 'a': a,
                                'y': (true_y(w, [x, z], a, False)+(noise.random() < .1)) % 2})
    assert w['composition'] == composition
    forms = true_forms(w, True)

    def joint(n):
        out = []
        for start in range(0, n, 32):
            block = CONTEXTS.copy()
            inputs.shuffle(block)
            for x, z, a in block:
                pair = [x, z]
                local_effects = [(forms[j][pair[j]]+(noise.random() < .1)) % 2 for j in range(2)]
                y = (true_y(w, pair, a, True)+(noise.random() < .1)) % 2
                out.append({'x': pair, 'a': a, 'local': local_effects, 'y': y})
        return out

    assert w['main'] == joint(512)
    assert w['selection'] == [joint(32) for _ in range(8)]


def local_table(partition, rows):
    return {g: [sum(r['y'] for r in rows if partition[r['x']] == g),
                sum(partition[r['x']] == g for r in rows)] for g in sorted(set(partition))}


def local_p(partition, table, x):
    ones, total = table[partition[x]]
    return (ones+1)/(total+2)


def exported(partition, table):
    order = sorted(table, key=lambda g: ((table[g][0]+1)/(table[g][1]+2), g))
    return [order.index(partition[x]) for x in range(4)]


def local_state(partition, table):
    return {'partition': list(partition), 'counts': {str(k): v for k, v in table.items()},
            'groups': exported(partition, table)}


def local_loss(partition, table, rows):
    return mean(logloss(local_p(partition, table, r['x']), r['y']) for r in rows)


class ReplayNode:
    def __init__(self, seed):
        self.partition = (0, 0, 0, 0)
        self.table = {0: [0, 0]}
        self.buffer, self.deck = [], []
        self.random = random.Random(seed)
        self.costs = dict(candidate_fits=0, candidate_fit_rows=0, refits=0, refit_rows=0)

    def state(self):
        return local_state(self.partition, self.table)

    def update(self, row):
        self.buffer = (self.buffer+[row])[-192:]
        self.table = local_table(self.partition, self.buffer)
        self.costs['refits'] += 1
        self.costs['refit_rows'] += len(self.buffer)

    def review(self, saved, batch):
        close(saved['before'], self.state())
        proposed = []
        while len(proposed) != 4:
            if len(self.deck) == 0:
                self.deck = PARTS.copy()
                self.random.shuffle(self.deck)
            p = self.deck.pop(0)
            if p != self.partition and p not in proposed:
                proposed.append(p)
        tables = [local_table(p, self.buffer) for p in proposed]
        assert len(saved['candidates']) == 4
        for p, counts, c in zip(proposed, tables, saved['candidates']):
            close(c, {'state': local_state(p, counts),
                      'ranking_loss': local_loss(p, counts, self.buffer[-64:])})
        # Use saved float bits only after verifying arithmetic, for exact ties.
        winner = min(range(4), key=lambda i: (
            saved['candidates'][i]['ranking_loss'], len(tables[i]), proposed[i]))
        assert saved['winner'] == winner
        old = local_loss(self.partition, self.table, batch)
        new = local_loss(proposed[winner], tables[winner], batch)
        close(saved['old_loss'], old)
        close(saved['new_loss'], new)
        close(saved['gain'], old-new)
        assert saved['accepted'] == (old-new > .005)
        if old-new > .005:
            self.partition, self.table = proposed[winner], tables[winner]
        close(saved['after'], self.state())
        close(saved['deck'], self.deck)
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4*len(self.buffer)


def key(mode, nodes, x, a):
    values = [x[j] if mode in ('flat', f'fine{j}') else
              exported(nodes[j].partition, nodes[j].table)[x[j]] for j in range(2)]
    return '|'.join(str(v) for v in values+[a])


def upper_table(mode, rows, nodes):
    axes = (range(4 if mode in ('flat', 'fine0') else 2),
            range(4 if mode in ('flat', 'fine1') else 2), range(2))
    counts = {'|'.join(str(v) for v in cell): [0, 0] for cell in itertools.product(*axes)}
    for row in rows:
        cell = counts[key(mode, nodes, row['x'], row['a'])]
        cell[0] += row['y']
        cell[1] += 1
    return counts


def probability(mode, counts, nodes, x, a):
    ones, n = counts[key(mode, nodes, x, a)]
    return (ones+1)/(n+2)


def upper_loss(mode, counts, nodes, rows):
    return mean(logloss(probability(mode, counts, nodes, r['x'], r['a']), r['y']) for r in rows)


def upper_state(mode, counts):
    return {'mode': mode, 'counts': copy.deepcopy(counts)}


def verify_upper(saved, mode, counts, nodes, buffer, batch):
    close(saved['before'], upper_state(mode, counts))
    modes = ('coarse', 'fine0', 'fine1')
    tables = [upper_table(m, buffer, nodes) for m in modes]
    assert len(saved['candidates']) == 3
    for m, c, candidate in zip(modes, tables, saved['candidates']):
        close(candidate, {'state': upper_state(m, c),
                          'ranking_loss': upper_loss(m, c, nodes, buffer)})
    best = min(range(3), key=lambda i: (saved['candidates'][i]['ranking_loss'], i))
    assert saved['winner'] == best
    old, new = upper_loss(mode, counts, nodes, batch), upper_loss(modes[best], tables[best], nodes, batch)
    close(saved['old_loss'], old)
    close(saved['new_loss'], new)
    close(saved['gain'], old-new)
    assert saved['failure_gate'] == (old > .55)
    accepted = old > .55 and old-new > .02
    assert saved['accepted'] == accepted
    if accepted:
        mode, counts = modes[best], tables[best]
    close(saved['after'], upper_state(mode, counts))
    return mode, counts


def verify_eval(saved, mode, counts, nodes, w, phase):
    contexts = CONTEXTS if phase else [
        c for c in CONTEXTS if c[0] not in w['representatives'][0] or c[1] not in w['representatives'][1]]
    ps, losses, correct = [], [], 0
    for x, z, a in contexts:
        p = probability(mode, counts, nodes, [x, z], a)
        truth = true_y(w, [x, z], a, phase)
        q = .1+.8*truth
        ps.append(p)
        losses.append(-q*math.log(p)-(1-q)*math.log1p(-p))
        correct += (p > .5) == bool(truth)
    value = mean(losses)
    close(saved, {'predictions': ps, 'expected_loss': value, 'regret': value-H,
                  'accuracy': correct/len(contexts), 'local_exact': [
                      exported(n.partition, n.table) == f for n, f in zip(nodes, true_forms(w, phase))],
                  'mode': mode, 'cells': len(counts), 'contexts': len(contexts)})


def good(e):
    return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10


def verify_run(r, w):
    nodes = [ReplayNode(64000+2*r['proposal_seed']+j) for j in range(2)]
    feedback = 0
    assert len(r['warmup']) == 4
    for i in range(256):
        for j in range(2):
            nodes[j].update(w['local_main'][j][i])
            feedback += 1
        if (i+1) % 64 == 0:
            for j in range(2):
                nodes[j].review(r['warmup'][i//64][j], w['local_selection'][i//64][j])
                feedback += 32
    mode = 'flat' if r['variant'] == 'flat' else 'coarse'
    counts = upper_table(mode, w['composition'], nodes)
    feedback += len(w['composition'])
    initial = upper_state(mode, counts)
    close(r['initial_upper'], initial)
    verify_eval(r['transfer'], mode, counts, nodes, w, False)
    buffer = w['composition'][-192:]
    reads, losses = [], []
    refits = refit_rows = candidates = candidate_rows = 0
    assert len(r['predictions']) == len(r['raw_reads']) == 512 and len(r['reviews']) == 8
    for t, row in enumerate(w['main'], 1):
        p = probability(mode, counts, nodes, row['x'], row['a'])
        close(r['predictions'][t-1], p)
        losses.append(logloss(p, row['y']))
        raw = 2 if mode == 'flat' else int(mode.startswith('fine'))
        reads.append(raw)
        assert r['raw_reads'][t-1] == raw
        if r['variant'] in ('reopen', 'closed'):
            for j in range(2):
                nodes[j].update({'x': row['x'][j], 'y': row['local'][j]})
                feedback += 1
        if r['variant'] in ('reopen', 'flat'):
            buffer = (buffer+[row])[-192:]
            feedback += 1
        if r['variant'] == 'flat' or (r['variant'] == 'reopen' and mode != 'coarse'):
            counts = upper_table(mode, buffer, nodes)
            refits += 1
            refit_rows += len(buffer)
        if t % 64:
            continue
        rev, batch = r['reviews'][t//64-1], w['selection'][t//64-1]
        assert rev['index'] == t
        if r['variant'] in ('reopen', 'closed'):
            assert len(rev['local']) == 2
            for j in range(2):
                nodes[j].review(rev['local'][j], [{'x': x['x'][j], 'y': x['local'][j]} for x in batch])
                feedback += 32
        else:
            assert 'local' not in rev
        if r['variant'] == 'reopen':
            mode, counts = verify_upper(rev['upper'], mode, counts, nodes, buffer, batch)
            feedback += 32
            candidates += 3
            candidate_rows += 3*len(buffer)
        else:
            assert 'upper' not in rev
        verify_eval(rev['evaluation'], mode, counts, nodes, w, True)
    close(r['final_upper'], upper_state(mode, counts))
    close(r['final_local'], [n.state() for n in nodes])
    costs = {k: sum(n.costs[k] for n in nodes) for k in nodes[0].costs}
    costs.update(upper_refits=refits, upper_refit_rows=refit_rows,
                 upper_candidate_fits=candidates, upper_candidate_rows=candidate_rows,
                 prediction_raw_reads=sum(reads), feedback_labels=feedback)
    close(r['costs'], costs)
    close(r['metrics'], {
        'main_loss': mean(losses), 'first192_loss': mean(losses[:192]),
        'final_valid': good(r['reviews'][-1]['evaluation']), 'transfer_valid': good(r['transfer']),
        'upper_unchanged': upper_state(mode, counts) == initial,
        'always_coarse': all(v['evaluation']['mode'] == 'coarse' for v in r['reviews']),
        'first_recovery': next((v['index'] for v in r['reviews'] if good(v['evaluation'])), None),
        'upper_accepts': [v['index'] for v in r['reviews'] if v.get('upper', {}).get('accepted')],
        'mean_raw_reads': mean(reads)})


def verify_summary(runs, worlds, saved):
    def rs(branch, variant):
        return [r for r in runs if (r['branch'], r['variant']) == (branch, variant)]
    def final(r):
        return r['reviews'][-1]['evaluation']
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            rows = rs(b, v)
            assert len(rows) == 10
            groups.append({'branch': b, 'variant': v, 'runs': len(rows),
                           'transfer_passes': sum(good(r['transfer']) for r in rows),
                           'final_passes': sum(final(r)['accuracy'] == 1 and final(r)['regret'] <= .10 for r in rows),
                           'transfer_loss': mean(r['transfer']['expected_loss'] for r in rows),
                           'final_loss': mean(final(r)['expected_loss'] for r in rows),
                           'main_loss': mean(r['metrics']['main_loss'] for r in rows),
                           'mean_raw_reads': mean(r['metrics']['mean_raw_reads'] for r in rows)})
    checks = {
        'transfer_count': sum(good(r['transfer']) for r in rs('persistent', 'closed')) >= 8,
        'transfer_gain': mean(r['transfer']['expected_loss'] for r in rs('persistent', 'flat'))-
                         mean(r['transfer']['expected_loss'] for r in rs('persistent', 'closed')) >= .15,
        'remap_closed': sum(good(final(r)) for r in rs('remap', 'closed')) >= 8,
        'remap_upper_frozen': all(r['initial_upper'] == r['final_upper'] for r in rs('remap', 'closed')),
        'remap_frozen_challenged': sum(final(r)['accuracy'] <= .80 for r in rs('remap', 'frozen')) >= 8,
        'remap_reopen_stays_coarse': sum(good(final(r)) and final(r)['mode'] == 'coarse'
                                       for r in rs('remap', 'reopen')) >= 8,
        'breach_correct_interface': sum(good(final(r)) and final(r)['mode'] ==
            f"fine{worlds[(r['seed'], r['branch'])]['affected']}" for r in rs('breach', 'reopen')) >= 8,
        'breach_closed_challenged': sum(final(r)['accuracy'] <= .75 for r in rs('breach', 'closed')) >= 8,
        'breach_gain': mean(final(r)['expected_loss'] for r in rs('breach', 'closed'))-
                       mean(final(r)['expected_loss'] for r in rs('breach', 'reopen')) >= .15,
        'persistent_structure': sum(good(final(r)) and r['metrics']['always_coarse']
                                    for r in rs('persistent', 'reopen')) >= 8,
        'persistent_cost': mean(r['metrics']['main_loss'] for r in rs('persistent', 'reopen'))-
                           mean(r['metrics']['main_loss'] for r in rs('persistent', 'closed')) <= .02}
    close(saved, {'groups': groups, 'checks': checks, 'primary_pass': all(checks.values())})


def main():
    data = json.loads((OUT/'results.json').read_text())
    manifest = json.loads((OUT/'manifest.json').read_text())
    assert manifest == data['hashes']
    assert set(manifest) == {'experiments/nested_abstractions_protocol.md',
                             'experiments/nested_abstractions.py',
                             'checks/test_nested_abstractions.py', 'checks/audit_nested_abstractions.py'}
    for folder in ('bundles-v1', 'bundle-retention-v1', 'interfaces-v1', 'nested-abstractions-v1'):
        for p, digest in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest, p
    worlds = {(w['seed'], w['branch']): w for w in data['worlds']}
    assert len(worlds) == len(data['worlds']) == 15
    assert set(worlds) == {(s, b) for s in range(300, 305) for b in BRANCHES}
    for w in worlds.values():
        verify_world(w)
    runs = data['runs']
    assert len(runs) == 120
    assert {(r['seed'], r['branch'], r['variant'], r['proposal_seed']) for r in runs} == {
        (s, b, v, ps) for s in range(300, 305) for b in BRANCHES for v in VARIANTS for ps in (300, 301)}
    for r in runs:
        verify_run(r, worlds[(r['seed'], r['branch'])])
    for s in range(300, 305):
        for ps in (300, 301):
            rows = [r for r in runs if (r['seed'], r['proposal_seed']) == (s, ps)]
            assert all(r['warmup'] == rows[0]['warmup'] for r in rows)
            nested = [r for r in rows if r['variant'] != 'flat']
            assert all(r['initial_upper'] == nested[0]['initial_upper'] for r in nested)
    verify_summary(runs, worlds, data['summary'])
    costs = {k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs']}
    assert costs['candidate_fits'] <= 11520 and costs['upper_candidate_fits'] <= 720
    assert costs['feedback_labels'] == 253440
    close(data['totals'], {'runs': 120, 'allocated_label_presentations': 399360,
                           'generated_labels': 49920, 'evaluation_predictions': 120*(24+8*32),
                           'costs': costs})
    close(json.loads((OUT/'metrics.json').read_text()), {
        'summary': data['summary'], 'totals': data['totals'],
        'runs': [{k: r[k] for k in ('seed', 'branch', 'variant', 'proposal_seed', 'metrics', 'costs')}
                 for r in runs]})
    print('PASS: 120 runs independently replayed; paired worlds, local group learning, '
          'upper interfaces, feedback isolation, transfer, metrics, budgets and four manifests verified.')


if __name__ == '__main__':
    main()
