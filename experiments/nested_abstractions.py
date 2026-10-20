"""Experiment 013: local effect abstractions composed through restricted interfaces."""
import argparse
import copy
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import random
import statistics as st

ROOT = Path(__file__).resolve().parents[1]
PARTITIONS = [(0,)+bits for bits in it.product((0, 1), repeat=3)]
BRANCHES = ('persistent', 'remap', 'breach')
VARIANTS = ('reopen', 'closed', 'frozen', 'flat')
MODES = ('coarse', 'fine0', 'fine1')
CONTEXTS = list(it.product(range(4), range(4), range(2)))
H = -.1*math.log(.1)-.9*math.log(.9)
FILES = ('experiments/nested_abstractions_protocol.md',
         'experiments/nested_abstractions.py', 'checks/test_nested_abstractions.py',
         'checks/audit_nested_abstractions.py')


def nll(p, y):
    return -math.log(p if y else 1-p)


def expected(p, q):
    return -q*math.log(p)-(1-q)*math.log1p(-p)


def hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}


def old_manifests():
    for folder in ('bundles-v1', 'bundle-retention-v1', 'interfaces-v1'):
        for p, h in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p


def current_forms(world, adaptation=True):
    forms = copy.deepcopy(world['forms'])
    if adaptation and world['branch'] == 'remap':
        j = world['affected']
        for x in world['representatives'][j]:
            forms[j][x] ^= 1
    return forms


def target(world, x, a, adaptation=True):
    forms = current_forms(world, adaptation)
    value = forms[0][x[0]] ^ forms[1][x[1]] ^ a
    if adaptation and world['branch'] == 'breach':
        j = world['affected']
        value ^= x[j] != world['representatives'][j][forms[j][x[j]]]
    return int(value)


def generate(seed, branch):
    layout = random.Random(61000+seed)
    forms, representatives = [], []
    for _ in range(2):
        order = list(range(4))
        layout.shuffle(order)
        forms.append([int(order.index(x) >= 2) for x in range(4)])
        representatives.append([order[0], order[2]])
    w = {'seed': seed, 'branch': branch, 'forms': forms,
         'representatives': representatives, 'affected': layout.randrange(2)}
    inputs, noise = random.Random(62000+seed), random.Random(63000+seed)

    def local_rows(j, n):
        result = []
        for _ in range(n//4):
            block = list(range(4))
            inputs.shuffle(block)
            result.extend({'x': x, 'y': forms[j][x] ^ int(noise.random() < .1)}
                          for x in block)
        return result

    w['local_main'] = [local_rows(j, 256) for j in range(2)]
    w['local_selection'] = [[local_rows(j, 32) for j in range(2)] for _ in range(4)]
    training = []
    for _ in range(32):
        block = list(it.product(*representatives, (0, 1)))
        inputs.shuffle(block)
        for left, right, a in block:
            x = [left, right]
            training.append({'x': x, 'a': a,
                             'y': target(w, x, a, False) ^ int(noise.random() < .1)})
    w['composition'] = training
    forms_now = current_forms(w)

    def joint_rows(n):
        result = []
        for _ in range(n//32):
            block = CONTEXTS.copy()
            inputs.shuffle(block)
            for left, right, a in block:
                x = [left, right]
                local = [forms_now[j][x[j]] ^ int(noise.random() < .1) for j in range(2)]
                y = target(w, x, a) ^ int(noise.random() < .1)
                result.append({'x': x, 'a': a, 'local': local, 'y': y})
        return result

    w['main'] = joint_rows(512)
    w['selection'] = [joint_rows(32) for _ in range(8)]
    return w


class LocalModel:
    def __init__(self, partition=(0, 0, 0, 0), rows=()):
        self.partition = tuple(partition)
        self.counts = {g: [0, 0] for g in sorted(set(partition))}
        for r in rows:
            cell = self.counts[self.partition[r['x']]]
            cell[0] += r['y']
            cell[1] += 1

    def predict(self, x):
        ones, total = self.counts[self.partition[x]]
        return (ones+1)/(total+2)

    def group(self, x):
        ordered = sorted(self.counts, key=lambda g: (
            (self.counts[g][0]+1)/(self.counts[g][1]+2), g))
        return ordered.index(self.partition[x])

    def state(self):
        return {'partition': list(self.partition),
                'counts': {str(k): v.copy() for k, v in self.counts.items()},
                'groups': [self.group(x) for x in range(4)]}

    def loss(self, rows):
        return st.mean(nll(self.predict(r['x']), r['y']) for r in rows)


class LocalLearner:
    def __init__(self, seed):
        self.model = LocalModel()
        self.buffer, self.deck = [], []
        self.rng = random.Random(seed)
        self.costs = {'candidate_fits': 0, 'candidate_fit_rows': 0,
                      'refits': 0, 'refit_rows': 0}

    def update(self, row):
        self.buffer = (self.buffer+[row])[-192:]
        self.model = LocalModel(self.model.partition, self.buffer)
        self.costs['refits'] += 1
        self.costs['refit_rows'] += len(self.buffer)

    def review(self, selection):
        before = self.model.state()
        proposals = []
        while len(proposals) < 4:
            if not self.deck:
                self.deck = PARTITIONS.copy()
                self.rng.shuffle(self.deck)
            p = self.deck.pop(0)
            if p != self.model.partition and p not in proposals:
                proposals.append(p)
        models = [LocalModel(p, self.buffer) for p in proposals]
        losses = [m.loss(self.buffer[-64:]) for m in models]
        best = min(range(4), key=lambda i: (
            losses[i], len(models[i].counts), models[i].partition))
        old_loss, new_loss = self.model.loss(selection), models[best].loss(selection)
        gain = old_loss-new_loss
        if gain > .005:
            self.model = models[best]
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4*len(self.buffer)
        return {'before': before, 'candidates': [
            {'state': m.state(), 'ranking_loss': loss} for m, loss in zip(models, losses)],
            'winner': best, 'old_loss': old_loss, 'new_loss': new_loss,
            'gain': gain, 'accepted': gain > .005,
            'after': self.model.state(), 'deck': [list(p) for p in self.deck]}


class InterfaceView:
    """Only an explicitly reopened module exposes raw identity to its parent."""
    def __init__(self, groups, raw, mode):
        self._groups, self._raw, self.mode = groups, raw, mode
        self.raw_reads = 0

    def group(self, j):
        return self._groups[j]

    def raw(self, j):
        if self.mode not in ('flat', f'fine{j}'):
            raise PermissionError(f'Raw module {j} is hidden')
        self.raw_reads += 1
        return self._raw[j]


def view_for(x, models, mode):
    return InterfaceView([m.group(x[j]) for j, m in enumerate(models)], x, mode)


class Upper:
    def __init__(self, mode='coarse', rows=(), models=()):
        self.mode = mode
        dimensions = (4 if mode in ('flat', 'fine0') else 2,
                      4 if mode in ('flat', 'fine1') else 2, 2)
        self.counts = {'|'.join(map(str, key)): [0, 0]
                       for key in it.product(*(range(n) for n in dimensions))}
        for r in rows:
            key = self.key(view_for(r['x'], models, mode), r['a'])
            self.counts[key][0] += r['y']
            self.counts[key][1] += 1

    def key(self, view, a):
        values = [view.raw(j) if self.mode in ('flat', f'fine{j}') else view.group(j)
                  for j in range(2)]
        return '|'.join(map(str, values+[a]))

    def predict(self, view, a):
        ones, total = self.counts[self.key(view, a)]
        return (ones+1)/(total+2)

    def state(self):
        return {'mode': self.mode, 'counts': copy.deepcopy(self.counts)}

    def loss(self, rows, models):
        return st.mean(nll(self.predict(view_for(r['x'], models, self.mode), r['a']), r['y'])
                       for r in rows)


def upper_review(upper, buffer, models, selection):
    # Construction and ranking complete before composite selection labels are read.
    candidates = [Upper(mode, buffer, models) for mode in MODES]
    losses = [m.loss(buffer, models) for m in candidates]
    best = min(range(3), key=lambda i: (losses[i], i))
    old_loss = upper.loss(selection, models)
    new_loss = candidates[best].loss(selection, models)
    accepted = old_loss > .55 and old_loss-new_loss > .02
    details = {'before': upper.state(), 'candidates': [
        {'state': m.state(), 'ranking_loss': loss} for m, loss in zip(candidates, losses)],
        'winner': best, 'old_loss': old_loss, 'new_loss': new_loss,
        'gain': old_loss-new_loss, 'failure_gate': old_loss > .55, 'accepted': accepted}
    result = candidates[best] if accepted else upper
    details['after'] = result.state()
    return result, details


def evaluate(upper, models, world, adaptation):
    before = (upper.state(), [m.state() for m in models])
    contexts = CONTEXTS if adaptation else [
        (l, r, a) for l, r, a in CONTEXTS
        if not(l in world['representatives'][0] and r in world['representatives'][1])]
    loss, correct, predictions = [], 0, []
    for l, r, a in contexts:
        y = target(world, [l, r], a, adaptation)
        p = upper.predict(view_for([l, r], models, upper.mode), a)
        predictions.append(p)
        loss.append(expected(p, .9 if y else .1))
        correct += (p > .5) == bool(y)
    exact = [m.state()['groups'] == forms for m, forms in zip(models, current_forms(world, adaptation))]
    value = st.mean(loss)
    assert before == (upper.state(), [m.state() for m in models])
    return {'predictions': predictions, 'expected_loss': value, 'regret': value-H,
            'accuracy': correct/len(contexts), 'local_exact': exact, 'mode': upper.mode,
            'cells': len(upper.counts), 'contexts': len(contexts)}


def valid(e):
    return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10


def run(world, variant, proposal_seed):
    local = [LocalLearner(64000+2*proposal_seed+j) for j in range(2)]
    warm = []
    for i in range(256):
        for j in range(2):
            local[j].update(world['local_main'][j][i])
        if (i+1) % 64 == 0:
            warm.append([local[j].review(world['local_selection'][i//64][j])
                         for j in range(2)])
    models = [l.model for l in local]
    upper = Upper('flat' if variant == 'flat' else 'coarse', world['composition'], models)
    initial = upper.state()
    transfer = evaluate(upper, models, world, False)
    buffer = copy.deepcopy(world['composition'][-192:])
    predictions, reads, reviews = [], [], []
    upper_refits = upper_refit_rows = upper_candidates = upper_candidate_rows = 0
    for t, row in enumerate(world['main'], 1):
        models = [l.model for l in local]
        view = view_for(row['x'], models, upper.mode)
        predictions.append(upper.predict(view, row['a']))
        reads.append(view.raw_reads)
        if variant in ('reopen', 'closed'):
            for j in range(2):
                local[j].update({'x': row['x'][j], 'y': row['local'][j]})
        if variant in ('reopen', 'flat'):
            buffer = (buffer+[row])[-192:]
        models = [l.model for l in local]
        if variant == 'flat' or (variant == 'reopen' and upper.mode != 'coarse'):
            upper = Upper(upper.mode, buffer, models)
            upper_refits += 1
            upper_refit_rows += len(buffer)
        if t % 64:
            continue
        selection = world['selection'][t//64-1]
        review = {'index': t}
        if variant in ('reopen', 'closed'):
            review['local'] = [local[j].review([
                {'x': r['x'][j], 'y': r['local'][j]} for r in selection]) for j in range(2)]
        models = [l.model for l in local]
        if variant == 'reopen':
            upper, review['upper'] = upper_review(upper, buffer, models, selection)
            upper_candidates += 3
            upper_candidate_rows += 3*len(buffer)
        snapshot = copy.deepcopy((upper.state(), buffer, [
            (l.model.state(), l.buffer, l.deck, l.rng.getstate(), l.costs) for l in local]))
        review['evaluation'] = evaluate(upper, models, world, True)
        assert snapshot == (upper.state(), buffer, [
            (l.model.state(), l.buffer, l.deck, l.rng.getstate(), l.costs) for l in local])
        reviews.append(review)
    losses = [nll(p, r['y']) for p, r in zip(predictions, world['main'])]
    final = reviews[-1]['evaluation']
    costs = {k: sum(l.costs[k] for l in local) for k in local[0].costs}
    costs.update(upper_refits=upper_refits, upper_refit_rows=upper_refit_rows,
                 upper_candidate_fits=upper_candidates, upper_candidate_rows=upper_candidate_rows,
                 prediction_raw_reads=sum(reads),
                 feedback_labels={'reopen': 3328, 'closed': 2560, 'frozen': 1024, 'flat': 1536}[variant])
    return {'seed': world['seed'], 'branch': world['branch'], 'variant': variant,
            'proposal_seed': proposal_seed, 'warmup': warm, 'initial_upper': initial,
            'transfer': transfer, 'predictions': predictions, 'raw_reads': reads,
            'reviews': reviews, 'final_upper': upper.state(),
            'final_local': [l.model.state() for l in local], 'costs': costs,
            'metrics': {'main_loss': st.mean(losses), 'first192_loss': st.mean(losses[:192]),
                        'final_valid': valid(final), 'transfer_valid': valid(transfer),
                        'upper_unchanged': upper.state() == initial,
                        'always_coarse': all(r['evaluation']['mode'] == 'coarse' for r in reviews),
                        'first_recovery': next((r['index'] for r in reviews if valid(r['evaluation'])), None),
                        'upper_accepts': [r['index'] for r in reviews if r.get('upper', {}).get('accepted')],
                        'mean_raw_reads': st.mean(reads)}}


def summarize(runs, worlds):
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            rs = [r for r in runs if (r['branch'], r['variant']) == (b, v)]
            groups.append({'branch': b, 'variant': v, 'runs': len(rs),
                           'transfer_passes': sum(r['metrics']['transfer_valid'] for r in rs),
                           'final_passes': sum(r['reviews'][-1]['evaluation']['accuracy'] == 1 and
                               r['reviews'][-1]['evaluation']['regret'] <= .10 for r in rs),
                           'transfer_loss': st.mean(r['transfer']['expected_loss'] for r in rs),
                           'final_loss': st.mean(r['reviews'][-1]['evaluation']['expected_loss'] for r in rs),
                           'main_loss': st.mean(r['metrics']['main_loss'] for r in rs),
                           'mean_raw_reads': st.mean(r['metrics']['mean_raw_reads'] for r in rs)})
    def get(b, v):
        return [r for r in runs if (r['branch'], r['variant']) == (b, v)]
    def final(r):
        return r['reviews'][-1]['evaluation']
    transfer = get('persistent', 'closed')
    remap, remap_open = get('remap', 'closed'), get('remap', 'reopen')
    breach, closed = get('breach', 'reopen'), get('breach', 'closed')
    persistent = get('persistent', 'reopen')
    checks = {
        'transfer_count': sum(r['metrics']['transfer_valid'] for r in transfer) >= 8,
        'transfer_gain': st.mean(r['transfer']['expected_loss'] for r in get('persistent', 'flat'))-
                         st.mean(r['transfer']['expected_loss'] for r in transfer) >= .15,
        'remap_closed': sum(valid(final(r)) for r in remap) >= 8,
        'remap_upper_frozen': all(r['metrics']['upper_unchanged'] for r in remap),
        'remap_frozen_challenged': sum(final(r)['accuracy'] <= .80 for r in get('remap', 'frozen')) >= 8,
        'remap_reopen_stays_coarse': sum(valid(final(r)) and final(r)['mode'] == 'coarse'
                                       for r in remap_open) >= 8,
        'breach_correct_interface': sum(valid(final(r)) and final(r)['mode'] ==
            f"fine{worlds[(r['seed'], r['branch'])]['affected']}" for r in breach) >= 8,
        'breach_closed_challenged': sum(final(r)['accuracy'] <= .75 for r in closed) >= 8,
        'breach_gain': st.mean(final(r)['expected_loss'] for r in closed)-
                       st.mean(final(r)['expected_loss'] for r in breach) >= .15,
        'persistent_structure': sum(valid(final(r)) and r['metrics']['always_coarse'] for r in persistent) >= 8,
        'persistent_cost': st.mean(r['metrics']['main_loss'] for r in persistent)-
                           st.mean(r['metrics']['main_loss'] for r in get('persistent', 'closed')) <= .02}
    return {'groups': groups, 'checks': checks, 'primary_pass': all(checks.values())}


def report(data):
    summary = data['summary']
    lines = ['# Experiment 013: fixed benchmark', '',
             f"Primary criterion: **{'PASS' if summary['primary_pass'] else 'FAIL'}**.", '',
             '| Branch | Variant | Transfer passes | Final predictive passes | Transfer loss | Final loss | Main loss | Parent raw reads/main |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in summary['groups']:
        lines.append(f"| {g['branch']} | {g['variant']} | {g['transfer_passes']}/10 | "
                     f"{g['final_passes']}/10 | {g['transfer_loss']:.6f} | {g['final_loss']:.6f} | "
                     f"{g['main_loss']:.6f} | {g['mean_raw_reads']:.3f} |")
    lines += ['', 'Final predictive passes require accuracy 1 and regret <=.10;',
              'the primary criterion additionally tests local exactness, interface choices and controls.',
              '', '## Fixed checks', '', '```json', json.dumps(summary['checks'], indent=2),
              '```', '', '## Resources', '', '```json', json.dumps(data['totals'], indent=2), '```', '',
              '## Every run', '', '| Environment | Learner seed | Branch | Variant | Transfer | Final exact + predictive | Final mode | First valid review | Upper accepts |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | --- |']
    for r in data['runs']:
        m = r['metrics']
        lines.append(f"| {r['seed']} | {r['proposal_seed']} | {r['branch']} | {r['variant']} | "
                     f"{m['transfer_valid']} | {m['final_valid']} | {r['final_upper']['mode']} | "
                     f"{m['first_recovery']} | {m['upper_accepts']} |")
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/nested-abstractions-v1')
    args = parser.parse_args()
    old_manifests()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    worlds = [generate(s, b) for s in range(300, 305) for b in BRANCHES]
    runs = [run(w, v, ps) for w in worlds for ps in (300, 301) for v in VARIANTS]
    summary = summarize(runs, {(w['seed'], w['branch']): w for w in worlds})
    totals = {'runs': len(runs), 'allocated_label_presentations': 399360,
              'generated_labels': 49920,
              'evaluation_predictions': sum(r['transfer']['contexts']+sum(
                  rev['evaluation']['contexts'] for rev in r['reviews']) for r in runs),
              'costs': {k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs']}}
    old_manifests()
    assert hashes() == provenance
    data = {'hashes': provenance, 'worlds': worlds, 'runs': runs, 'summary': summary, 'totals': totals}
    (args.output/'results.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
    (args.output/'metrics.json').write_text(json.dumps({
        'summary': summary, 'totals': totals, 'runs': [
            {k: r[k] for k in ('seed', 'branch', 'variant', 'proposal_seed', 'metrics', 'costs')}
            for r in runs]}, indent=2)+'\n')
    (args.output/'report.md').write_text(report(data))
    print(json.dumps({'summary': summary, 'totals': totals}, indent=2))


if __name__ == '__main__':
    main()
