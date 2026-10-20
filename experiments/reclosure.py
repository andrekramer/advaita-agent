"""Experiment 014: evidence-tested reclosure of nested prediction interfaces."""
import argparse
import copy
import hashlib
import itertools as it
import json
from pathlib import Path
import random
import statistics as st

from nested_abstractions import (
    LocalLearner, Upper, CONTEXTS, current_forms, target, evaluate, valid,
    upper_review, view_for, nll)

ROOT = Path(__file__).resolve().parents[1]
BRANCHES = ('persistent', 'remap', 'breach', 'transient')
VARIANTS = ('failure_only', 'reclose')
FILES = ('experiments/reclosure_protocol.md', 'experiments/reclosure.py',
         'checks/test_reclosure.py', 'checks/audit_reclosure.py',
         'experiments/nested_abstractions.py', 'checks/audit_nested_abstractions.py')


def hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}


def previous_manifests():
    for folder in ('bundles-v1', 'bundle-retention-v1', 'interfaces-v1', 'nested-abstractions-v1'):
        for p, digest in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest, p


def effective_world(w, index):
    if w['branch'] != 'transient':
        return w
    return dict(w, branch='breach' if index <= 384 else 'persistent')


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
            result.extend({'x': x, 'y': forms[j][x] ^ int(noise.random() < .1)} for x in block)
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

    def joint_rows(n, selection_index=None):
        result = []
        for _ in range(n//32):
            block = CONTEXTS.copy()
            inputs.shuffle(block)
            for left, right, a in block:
                x = [left, right]
                local = [forms_now[j][x[j]] ^ int(noise.random() < .1) for j in range(2)]
                index = selection_index if selection_index is not None else len(result)+1
                y = target(effective_world(w, index), x, a) ^ int(noise.random() < .1)
                result.append({'x': x, 'a': a, 'local': local, 'y': y})
        return result

    w['main'] = joint_rows(768)
    w['selection'] = [joint_rows(32, t) for t in range(64, 769, 64)]
    return w


def restore_upper(state):
    result = Upper(state['mode'])
    result.counts = copy.deepcopy(state['counts'])
    return result


class Reclosure:
    def __init__(self):
        self.pending = None
        self.costs = {'challenger_predictions': 0, 'challenger_starts': 0,
                      'group_invalidations': 0, 'failed_witnesses': 0,
                      'accepted_reclosures': 0, 'max_pending_cells': 0}

    def state(self):
        return copy.deepcopy(self.pending)

    def review(self, incumbent, prepared_coarse, models, selection, ordinary):
        before = self.state()
        groups = [m.state()['groups'] for m in models]
        detail = {'before': before, 'invalidated': False, 'witness': None}
        if ordinary['accepted']:
            self.pending = None
            detail['action'] = 'ordinary_replacement'
        elif incumbent.mode == 'coarse':
            self.pending = None
            detail['action'] = 'already_coarse'
        else:
            if self.pending is not None and self.pending['groups'] != groups:
                self.pending = None
                detail['invalidated'] = True
                self.costs['group_invalidations'] += 1
            if self.pending is None:
                self.pending = {'model': copy.deepcopy(prepared_coarse), 'groups': groups, 'passes': 0}
                self.costs['challenger_starts'] += 1
            challenger = restore_upper(self.pending['model'])
            self.costs['max_pending_cells'] = max(self.costs['max_pending_cells'], len(challenger.counts))
            loss = challenger.loss(selection, models)
            passed = loss <= .55 and loss-ordinary['old_loss'] <= .02
            self.costs['challenger_predictions'] += len(selection)
            detail['witness'] = {'model': challenger.state(), 'groups': groups,
                                 'loss': loss, 'fine_loss': ordinary['old_loss'],
                                 'passed': passed, 'prior_passes': self.pending['passes']}
            if not passed:
                self.pending = None
                self.costs['failed_witnesses'] += 1
                detail['action'] = 'witness_failed'
            else:
                self.pending['passes'] += 1
                if self.pending['passes'] == 2:
                    incumbent = challenger
                    self.pending = None
                    self.costs['accepted_reclosures'] += 1
                    detail['action'] = 'reclosed'
                else:
                    detail['action'] = 'awaiting_witness'
        detail['after'] = self.state()
        return incumbent, detail


def run(w, variant, ps):
    nodes = [LocalLearner(64000+2*ps+j) for j in range(2)]
    warm = []
    for i in range(256):
        for j in range(2):
            nodes[j].update(w['local_main'][j][i])
        if (i+1) % 64 == 0:
            warm.append([nodes[j].review(w['local_selection'][i//64][j]) for j in range(2)])
    models = [n.model for n in nodes]
    upper = Upper('coarse', w['composition'], models)
    initial = upper.state()
    transfer = evaluate(upper, models, w, False)
    policy = Reclosure()
    buffer = copy.deepcopy(w['composition'][-192:])
    predictions, reads, reviews = [], [], []
    refits = refit_rows = 0
    for t, row in enumerate(w['main'], 1):
        models = [n.model for n in nodes]
        view = view_for(row['x'], models, upper.mode)
        predictions.append(upper.predict(view, row['a']))
        reads.append(view.raw_reads)
        for j in range(2):
            nodes[j].update({'x': row['x'][j], 'y': row['local'][j]})
        buffer = (buffer+[row])[-192:]
        models = [n.model for n in nodes]
        if upper.mode != 'coarse':
            upper = Upper(upper.mode, buffer, models)
            refits += 1
            refit_rows += len(buffer)
        if t % 64:
            continue
        batch = w['selection'][t//64-1]
        rev = {'index': t, 'local': [nodes[j].review([
            {'x': r['x'][j], 'y': r['local'][j]} for r in batch]) for j in range(2)]}
        models = [n.model for n in nodes]
        upper, rev['ordinary'] = upper_review(upper, buffer, models, batch)
        if variant == 'reclose':
            upper, rev['reclosure'] = policy.review(
                upper, rev['ordinary']['candidates'][0]['state'], models, batch, rev['ordinary'])
        rev['upper_after'] = upper.state()
        snap = copy.deepcopy((upper.state(), policy.state(), policy.costs, buffer, [
            (n.model.state(), n.buffer, n.deck, n.rng.getstate(), n.costs) for n in nodes]))
        rev['evaluation'] = evaluate(upper, models, effective_world(w, t), True)
        assert snap == (upper.state(), policy.state(), policy.costs, buffer, [
            (n.model.state(), n.buffer, n.deck, n.rng.getstate(), n.costs) for n in nodes])
        reviews.append(rev)
    costs = {k: sum(n.costs[k] for n in nodes) for k in nodes[0].costs}
    costs.update(upper_refits=refits, upper_refit_rows=refit_rows, upper_candidate_fits=36,
                 upper_candidate_rows=36*192, feedback_labels=4480, prediction_raw_reads=sum(reads))
    costs.update(policy.costs)
    r = {'seed': w['seed'], 'branch': w['branch'], 'variant': variant, 'proposal_seed': ps,
         'warmup': warm, 'initial_upper': initial, 'transfer': transfer, 'predictions': predictions,
         'raw_reads': reads, 'reviews': reviews, 'final_upper': upper.state(),
         'final_local': [n.model.state() for n in nodes], 'pending': policy.state(), 'costs': costs}
    r['metrics'] = metrics(r, w)
    return r


def metrics(r, w):
    reviews = r['reviews']
    losses = [nll(p, row['y']) for p, row in zip(r['predictions'], w['main'])]
    reclosed = [v['index'] for v in reviews if v.get('reclosure', {}).get('action') == 'reclosed']
    # Includes ordinary-rule changes to coarse, kept separate from the new operation.
    hidden = [v['index'] for v in reviews if v['ordinary']['before']['mode'] != 'coarse'
              and v['upper_after']['mode'] == 'coarse']
    reopened = [v['index'] for v in reviews if v['ordinary']['before']['mode'] == 'coarse'
                and v['upper_after']['mode'] != 'coarse']
    middle, final = reviews[5]['evaluation'], reviews[-1]['evaluation']
    trajectory = (w['branch'] == 'transient' and valid(middle) and middle['mode'] == f"fine{w['affected']}" and valid(final)
                  and final['mode'] == 'coarse' and any(t > 384 for t in reclosed))
    return {'transfer_valid': valid(r['transfer']), 'final_valid': valid(final),
            'coarse_final_valid': valid(final) and final['mode'] == 'coarse',
            'affected_fine_final_valid': valid(final) and final['mode'] == f"fine{w['affected']}",
            'transient_trajectory': trajectory, 'reclosure_reviews': reclosed,
            'hide_reviews': hidden, 'reopen_reviews': reopened,
            'first_valid_after384': next((v['index'] for v in reviews if v['index'] > 384 and valid(v['evaluation'])), None),
            'first_coarse_valid_after384': next((v['index'] for v in reviews if v['index'] > 384 and
                valid(v['evaluation']) and v['evaluation']['mode'] == 'coarse'), None),
            'main_loss': st.mean(losses), 'after384_loss': st.mean(losses[384:]),
            'late_raw_reads': st.mean(r['raw_reads'][512:]),
            'mean_raw_reads': st.mean(r['raw_reads']),
            'reclosures_during_breach': sum(t <= 384 if w['branch'] == 'transient' else
                                          w['branch'] == 'breach' for t in reclosed)}


def summarize(runs):
    def get(b, v):
        return [r for r in runs if (r['branch'], r['variant']) == (b, v)]
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            rs = get(b, v)
            groups.append({'branch': b, 'variant': v,
                           'transfer_valid': sum(r['metrics']['transfer_valid'] for r in rs),
                           'final_valid': sum(r['metrics']['final_valid'] for r in rs),
                           'coarse_final_valid': sum(r['metrics']['coarse_final_valid'] for r in rs),
                           'affected_fine_final_valid': sum(r['metrics']['affected_fine_final_valid'] for r in rs),
                           'transient_trajectories': sum(r['metrics']['transient_trajectory'] for r in rs),
                           'main_loss': st.mean(r['metrics']['main_loss'] for r in rs),
                           'after384_loss': st.mean(r['metrics']['after384_loss'] for r in rs),
                           'late_raw_reads': st.mean(r['metrics']['late_raw_reads'] for r in rs),
                           'reclosures': sum(len(r['metrics']['reclosure_reviews']) for r in rs),
                           'reclosures_during_breach': sum(r['metrics']['reclosures_during_breach'] for r in rs)})
    paired = []
    for b in BRANCHES:
        for seed in range(400, 405):
            for ps in (400, 401):
                rr = {r['variant']: r['metrics'] for r in get(b, 'failure_only')+get(b, 'reclose')
                      if (r['seed'], r['proposal_seed']) == (seed, ps)}
                a, c = rr['reclose'], rr['failure_only']
                paired.append({'branch': b, 'seed': seed, 'proposal_seed': ps,
                               'main_cost': a['main_loss']-c['main_loss'],
                               'after384_cost': a['after384_loss']-c['after384_loss'],
                               'late_read_reduction': c['late_raw_reads']-a['late_raw_reads']})
    transient = [p for p in paired if p['branch'] == 'transient']
    a = st.mean(r['metrics']['late_raw_reads'] for r in get('transient', 'reclose'))
    c = st.mean(r['metrics']['late_raw_reads'] for r in get('transient', 'failure_only'))
    checks = {
        'transfer': all(sum(r['metrics']['transfer_valid'] for r in get('persistent', v)) >= 8 for v in VARIANTS),
        'persistent_coarse': sum(r['metrics']['coarse_final_valid'] for r in get('persistent', 'reclose')) >= 8,
        'remap_coarse': sum(r['metrics']['coarse_final_valid'] for r in get('remap', 'reclose')) >= 8,
        'persistent_loss_guard': st.mean(p['main_cost'] for p in paired if p['branch'] == 'persistent') <= .02,
        'breach_preserved': sum(r['metrics']['affected_fine_final_valid'] for r in get('breach', 'reclose')) >= 8,
        'breach_loss_guard': st.mean(p['main_cost'] for p in paired if p['branch'] == 'breach') <= .02,
        'transient_trajectories': sum(r['metrics']['transient_trajectory'] for r in get('transient', 'reclose')) >= 8,
        'transient_access_pairs': sum(p['late_read_reduction'] > 0 for p in transient) >= 8,
        'transient_access_mean': c > 0 and a <= .75*c,
        'transient_loss_guard': st.mean(p['after384_cost'] for p in transient) <= .02}
    return {'groups': groups, 'paired': paired, 'checks': checks, 'primary_pass': all(checks.values())}


def report(data):
    s = data['summary']
    lines = ['# Experiment 014: fixed benchmark', '',
             f"Primary criterion: **{'PASS' if s['primary_pass'] else 'FAIL'}**.", '',
             '| Branch | Variant | Exact + predictive | Coarse + valid | Affected fine + valid | Transient trajectory | Main loss | Late raw reads |',
             '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for g in s['groups']:
        lines.append(f"| {g['branch']} | {g['variant']} | {g['final_valid']}/10 | "
                     f"{g['coarse_final_valid']}/10 | {g['affected_fine_final_valid']}/10 | "
                     f"{g['transient_trajectories']}/10 | {g['main_loss']:.6f} | {g['late_raw_reads']:.3f} |")
    lines += ['', 'Transient trajectory is the new two-witness operation, so failure_only cannot satisfy it.',
              '', '## Fixed checks', '', '```json', json.dumps(s['checks'], indent=2), '```',
              '', '## Resources', '', '```json', json.dumps(data['totals'], indent=2), '```',
              '', '## Every run', '',
              '| Environment | Learner | Branch | Variant | Final valid | Mode | New reclosures | Reopenings | Late raw reads |',
              '| --- | --- | --- | --- | --- | --- | --- | --- | ---: |']
    for r in data['runs']:
        m = r['metrics']
        lines.append(f"| {r['seed']} | {r['proposal_seed']} | {r['branch']} | {r['variant']} | "
                     f"{m['final_valid']} | {r['final_upper']['mode']} | {m['reclosure_reviews']} | "
                     f"{m['reopen_reviews']} | {m['late_raw_reads']:.3f} |")
    return '\n'.join(lines)+'\n'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/reclosure-v1')
    args = parser.parse_args()
    previous_manifests()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    worlds = [generate(s, b) for s in range(400, 405) for b in BRANCHES]
    runs = [run(w, v, ps) for w in worlds for ps in (400, 401) for v in VARIANTS]
    totals = {'runs': 80, 'allocated_label_presentations': 358400, 'generated_labels': 89600,
              'evaluation_predictions': 32640,
              'max_pending_cells_per_run': max(r['costs']['max_pending_cells'] for r in runs),
              'costs': {k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs']
                        if k != 'max_pending_cells'}}
    data = {'hashes': provenance, 'worlds': worlds, 'runs': runs, 'summary': summarize(runs), 'totals': totals}
    previous_manifests()
    assert hashes() == provenance
    (args.output/'results.json').write_text(json.dumps(data, separators=(',', ':'))+'\n')
    (args.output/'metrics.json').write_text(json.dumps({
        'summary': data['summary'], 'totals': totals, 'runs': [
            {k: r[k] for k in ('seed', 'branch', 'variant', 'proposal_seed', 'metrics', 'costs')}
            for r in runs]}, indent=2)+'\n')
    (args.output/'report.md').write_text(report(data))
    print(json.dumps({'summary': data['summary'], 'totals': totals}, indent=2))


if __name__ == '__main__':
    main()
