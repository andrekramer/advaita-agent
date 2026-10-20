"""Experiment 015: earned versus uniform inertia for a local form."""
import argparse
import copy
import hashlib
import json
import random
import statistics as st
from pathlib import Path

from nested_abstractions import LocalLearner, LocalModel, H, expected, nll

ROOT = Path(__file__).resolve().parents[1]
BRANCHES = ('persistent', 'remap', 'transient')
VARIANTS = ('immediate', 'uniform', 'earned')
FILES = ('experiments/form_retention_protocol.md', 'experiments/form_retention.py',
         'checks/test_form_retention.py', 'checks/audit_form_retention.py',
         'experiments/nested_abstractions.py', 'checks/audit_nested_abstractions.py')


def hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}


def previous_manifests():
    for folder in ('bundles-v1', 'bundle-retention-v1', 'interfaces-v1',
                   'nested-abstractions-v1', 'reclosure-v1'):
        for p, h in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p


def truth(w, index, observed=False):
    shifted = w['branch'] == 'remap' and index > 512
    corrupted = observed and w['branch'] == 'transient' and 512 < index <= 576
    return w['forms'][int(shifted or corrupted)]


def generate(seed, branch):
    order = list(range(4))
    random.Random(71000+seed).shuffle(order)
    a = [int(order.index(x) >= 2) for x in range(4)]
    b = a.copy()
    for x in (order[0], order[2]):
        b[x] ^= 1
    w = {'seed': seed, 'branch': branch, 'forms': [a, b]}
    inputs, noise = random.Random(72000+seed), random.Random(73000+seed)

    def rows(n, review=None):
        out = []
        for start in range(0, n, 4):
            block = list(range(4))
            inputs.shuffle(block)
            for x in block:
                index = review if review is not None else len(out)+1
                out.append({'x': x, 'y': truth(w, index, True)[x] ^ int(noise.random() < .1)})
        return out

    w['main'] = rows(1024)
    w['selection'] = [rows(32, t) for t in range(64, 1025, 64)]
    return w


def restore(state):
    model = LocalModel(state['partition'])
    model.counts = {int(k): v.copy() for k, v in state['counts'].items()}
    return model


class Retention:
    def __init__(self, variant):
        self.variant = variant
        self.established = False
        self.adequate = 0
        self.pending = None
        self.costs = dict(pending_predictions=0, pending_starts=0, pending_failures=0,
                          confirmed_replacements=0, immediate_replacements=0,
                          establishments=0, max_pending_cells=0)

    def state(self):
        return copy.deepcopy(dict(established=self.established,
                                  adequate=self.adequate, pending=self.pending))

    def decide(self, incumbent, challenger, old_loss, new_loss, batch):
        before = self.state()
        accepted, action, pending_loss = False, 'keep', None
        result = incumbent
        if self.pending is not None:
            frozen = restore(self.pending)
            pending_loss = frozen.loss(batch)
            self.costs['pending_predictions'] += len(batch)
            if old_loss-pending_loss > .005:
                result, accepted, action = frozen, True, 'confirmed'
                self.costs['confirmed_replacements'] += 1
            else:
                action = 'pending_failed'
                self.costs['pending_failures'] += 1
            self.pending = None
        elif old_loss-new_loss > .005:
            protected = self.variant == 'uniform' or (
                self.variant == 'earned' and self.established)
            if protected:
                self.pending = challenger.state()
                action = 'pending_started'
                self.costs['pending_starts'] += 1
                self.costs['max_pending_cells'] = max(
                    self.costs['max_pending_cells'], len(challenger.counts))
            else:
                result, accepted, action = challenger, True, 'immediate'
                self.costs['immediate_replacements'] += 1
        if accepted:
            self.established, self.adequate = False, 0
        else:
            self.adequate = min(2, self.adequate+1) if old_loss <= .55 else 0
            if self.adequate == 2 and not self.established:
                self.established = True
                self.costs['establishments'] += 1
        return result, dict(before=before, after=self.state(), action=action,
                            accepted=accepted, pending_loss=pending_loss)


class Learner(LocalLearner):
    def __init__(self, seed, variant):
        super().__init__(seed)
        self.policy = Retention(variant)

    def review(self, batch):
        # Reuse the frozen 013 search exactly; replace only its acceptance step.
        ordinary = super().review(batch)
        incumbent = restore(ordinary['before'])
        candidate = restore(ordinary['candidates'][ordinary['winner']]['state'])
        self.model, policy = self.policy.decide(
            incumbent, candidate, ordinary['old_loss'], ordinary['new_loss'], batch)
        return {'ordinary': ordinary, 'policy': policy, 'after': self.model.state()}


def evaluate(model, forms):
    ps = [model.predict(x) for x in range(4)]
    loss = st.mean(expected(p, .9 if y else .1) for p, y in zip(ps, forms))
    exact = [model.group(x) for x in range(4)] == forms
    accuracy = st.mean(int(p >= .5) == y for p, y in zip(ps, forms))
    return dict(probabilities=ps, exact=exact, accuracy=accuracy,
                expected_loss=loss, regret=loss-H,
                valid=exact and accuracy == 1 and loss-H <= .10)


def snapshot(node):
    return copy.deepcopy((node.model.state(), node.buffer, node.deck,
                          node.rng.getstate(), node.costs, node.policy.state(), node.policy.costs))


def run(w, variant, ps):
    node = Learner(74000+ps, variant)
    evaluations = [{'index': 0, **evaluate(node.model, truth(w, 0))}]
    predictions, reviews = [], []
    for index, row in enumerate(w['main'], 1):
        p = node.model.predict(row['x'])
        predictions.append(p)
        node.update(row)
        if index % 64 == 0:
            detail = node.review(w['selection'][index//64-1])
            reviews.append({'index': index, **detail})
            before = snapshot(node)
            evaluations.append({'index': index, **evaluate(node.model, truth(w, index))})
            assert snapshot(node) == before
    costs = {**node.costs, **node.policy.costs,
             'used_labels': 1536, 'ordinary_selection_predictions': 1024}
    r = dict(seed=w['seed'], branch=w['branch'], variant=variant, proposal_seed=ps,
             predictions=predictions, reviews=reviews, evaluations=evaluations,
             final=node.model.state(), policy=node.policy.state(), costs=costs)
    r['metrics'] = metrics(r, w)
    return r


def metrics(r, w):
    ev = r['evaluations']
    recovery = next((a['index'] for a, b in zip(ev, ev[1:])
                     if a['index'] > 512 and a['valid'] and b['valid']), 1088)
    acquisition = next((e['index'] for e in ev if 0 < e['index'] <= 512 and e['valid']), 576)
    observed = [nll(p, row['y']) for p, row in zip(r['predictions'], w['main'])]
    latent = [expected(p, .9 if truth(w, i)[row['x']] else .1)
              for i, (p, row) in enumerate(zip(r['predictions'], w['main']), 1)]
    replacements, harmful, wrong_establishments = [], [], []
    for rev in r['reviews']:
        t, d = rev['index'], rev['policy']
        forms = truth(w, t)
        if d['accepted']:
            replacements.append(t)
            if rev['ordinary']['before']['groups'] == forms and rev['after']['groups'] != forms:
                harmful.append(t)
        if not d['before']['established'] and d['after']['established'] and rev['after']['groups'] != forms:
            wrong_establishments.append(t)
    return dict(initial_valid=ev[4]['valid'], initial_exact=ev[4]['exact'],
                first_acquisition=acquisition, stable_recovery=recovery,
                final_valid=ev[-1]['valid'], final_exact=ev[-1]['exact'],
                invalid_checkpoints=sum(not e['valid'] for e in ev if e['index'] >= 320),
                inexact_checkpoints=sum(not e['exact'] for e in ev if e['index'] >= 320),
                main_loss=st.mean(observed), change_loss=st.mean(observed[512:]),
                transient_latent_loss=st.mean(latent[512:768]),
                replacement_reviews=replacements, harmful_replacements=harmful,
                wrong_establishments=wrong_establishments)


def summarize(runs):
    groups, paired = [], []
    for b in BRANCHES:
        for v in VARIANTS:
            ms = [r['metrics'] for r in runs if (r['branch'], r['variant']) == (b, v)]
            groups.append(dict(branch=b, variant=v,
                **{k: sum(m[k] for m in ms) for k in (
                    'initial_valid', 'initial_exact', 'final_valid', 'final_exact',
                    'invalid_checkpoints', 'inexact_checkpoints')},
                **{k: st.mean(m[k] for m in ms) for k in (
                    'first_acquisition', 'stable_recovery', 'main_loss', 'change_loss',
                    'transient_latent_loss')},
                **{k: sum(len(m[k]) for m in ms) for k in (
                    'replacement_reviews', 'harmful_replacements', 'wrong_establishments')}))
        for seed in range(500, 505):
            for ps in (500, 501):
                ms = {r['variant']: r['metrics'] for r in runs
                      if (r['branch'], r['seed'], r['proposal_seed']) == (b, seed, ps)}
                paired.append(dict(branch=b, seed=seed, proposal_seed=ps,
                    invalid_reduction=ms['immediate']['invalid_checkpoints']-ms['earned']['invalid_checkpoints'],
                    acquisition_delay=ms['earned']['first_acquisition']-ms['immediate']['first_acquisition'],
                    recovery_delay=ms['earned']['stable_recovery']-ms['immediate']['stable_recovery']))
    def g(b, v):
        return next(x for x in groups if (x['branch'], x['variant']) == (b, v))
    a, c = g('persistent', 'earned'), g('persistent', 'immediate')
    bad_a = sum(g(b, 'earned')['invalid_checkpoints'] for b in ('persistent', 'transient'))
    bad_c = sum(g(b, 'immediate')['invalid_checkpoints'] for b in ('persistent', 'transient'))
    checks = dict(
        acquisition=a['initial_valid'] >= 8 and a['initial_valid'] >= c['initial_valid']-1
            and a['first_acquisition'] <= c['first_acquisition']+64,
        stable_final=all(g(b, 'earned')['final_valid'] >= 8 for b in ('persistent', 'transient')),
        protection=bad_c > 0 and bad_a <= .75*bad_c and sum(
            p['invalid_reduction'] > 0 for p in paired if p['branch'] != 'remap') >= 2,
        persistent_loss=a['main_loss'] <= c['main_loss']+.02,
        transient_loss=g('transient', 'earned')['transient_latent_loss']
            <= g('transient', 'immediate')['transient_latent_loss']+.02,
        remap_final=g('remap', 'earned')['final_valid'] >= 8,
        remap_latency=g('remap', 'earned')['stable_recovery']
            <= g('remap', 'immediate')['stable_recovery']+64,
        remap_loss=g('remap', 'earned')['change_loss'] <= g('remap', 'immediate')['change_loss']+.05)
    return dict(groups=groups, paired=paired, checks=checks, primary_pass=all(checks.values()))


def report(data):
    s = data['summary']
    lines = ['# Experiment 015: fixed benchmark', '',
             f"Primary criterion: **{'PASS' if s['primary_pass'] else 'FAIL'}**.", '',
             '| Branch | Rule | Initial valid | Final valid | Invalid checkpoints | Inexact checkpoints | Main loss | Recovery index |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in s['groups']:
        lines.append(f"| {g['branch']} | {g['variant']} | {g['initial_valid']}/10 | "
                     f"{g['final_valid']}/10 | {g['invalid_checkpoints']} | {g['inexact_checkpoints']} | "
                     f"{g['main_loss']:.6f} | {g['stable_recovery']:.1f} |")
    lines += ['', 'Recovery index is meaningful for remap; persistent/transient use unchanged latent forms.',
              '', '```json', json.dumps(s['checks'], indent=2), '```',
              '', '## Resources', '', '```json', json.dumps(data['totals'], indent=2), '```',
              '', '## Every run', '',
              '| Environment | Search | Branch | Rule | Initial | Final | Invalid | Acquisition | Recovery | Replacements |',
              '| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |']
    for r in data['runs']:
        m = r['metrics']
        lines.append(f"| {r['seed']} | {r['proposal_seed']} | {r['branch']} | {r['variant']} | "
                     f"{m['initial_valid']} | {m['final_valid']} | {m['invalid_checkpoints']} | "
                     f"{m['first_acquisition']} | {m['stable_recovery']} | {m['replacement_reviews']} |")
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/form-retention-v1')
    args = parser.parse_args()
    previous_manifests()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    worlds = [generate(seed, b) for seed in range(500, 505) for b in BRANCHES]
    runs = [run(w, v, ps) for w in worlds for ps in (500, 501) for v in VARIANTS]
    totals = dict(runs=len(runs), generated_labels=23040, allocated_labels=138240,
                  checkpoint_queries=6120, main_predictions=92160,
                  max_pending_cells=max(r['costs']['max_pending_cells'] for r in runs),
                  costs={k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs']
                         if k != 'max_pending_cells'})
    data = dict(hashes=provenance, worlds=worlds, runs=runs, totals=totals, summary=summarize(runs))
    previous_manifests()
    assert hashes() == provenance
    (args.output/'results.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
    (args.output/'metrics.json').write_text(json.dumps(dict(
        summary=data['summary'], totals=totals,
        runs=[{k: r[k] for k in ('seed', 'branch', 'variant', 'proposal_seed', 'metrics', 'costs')}
              for r in runs]), indent=2)+'\n')
    (args.output/'report.md').write_text(report(data))
    print(json.dumps(dict(summary=data['summary'], totals=totals), indent=2))


if __name__ == '__main__':
    main()
