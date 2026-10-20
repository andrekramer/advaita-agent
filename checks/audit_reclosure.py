"""Independent replay of Experiment 014, using the independent 013 arithmetic."""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
from statistics import mean

from audit_nested_abstractions import (
    close, true_forms, true_y, CONTEXTS, ReplayNode, upper_table, upper_state,
    upper_loss, probability, verify_upper, verify_eval, logloss, good)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/reclosure-v1'
BRANCHES = ('persistent', 'remap', 'breach', 'transient')
VARIANTS = ('failure_only', 'reclose')


def world_at(w, t):
    branch = w['branch']
    if branch == 'transient':
        branch = 'breach' if t <= 384 else 'persistent'
    return dict(w, branch=branch)


def verify_world(w):
    layout = random.Random(61000+w['seed'])
    forms, reps = [], []
    for j in range(2):
        order = list(range(4))
        layout.shuffle(order)
        forms.append([int(x in order[2:]) for x in range(4)])
        reps.append([order[0], order[2]])
    assert (w['forms'], w['representatives'], w['affected']) == (forms, reps, layout.randrange(2))
    inputs, noise = random.Random(62000+w['seed']), random.Random(63000+w['seed'])

    def local(n, j):
        out = []
        for start in range(0, n, 4):
            block = list(range(4))
            inputs.shuffle(block)
            for x in block:
                out.append({'x': x, 'y': (forms[j][x]+int(noise.random() < .1)) % 2})
        return out

    assert w['local_main'] == [local(256, j) for j in range(2)]
    assert w['local_selection'] == [[local(32, j) for j in range(2)] for _ in range(4)]
    training = []
    for start in range(0, 256, 8):
        block = list(itertools.product(*reps, range(2)))
        inputs.shuffle(block)
        for left, right, a in block:
            x = [left, right]
            training.append({'x': x, 'a': a, 'y': (true_y(w, x, a, False)+(noise.random() < .1)) % 2})
    assert training == w['composition']
    forms = true_forms(w, True)

    def joint(n, review=None):
        out = []
        for start in range(0, n, 32):
            block = CONTEXTS.copy()
            inputs.shuffle(block)
            for left, right, a in block:
                x = [left, right]
                local = [(forms[j][x[j]]+(noise.random() < .1)) % 2 for j in range(2)]
                t = review if review is not None else len(out)+1
                y = (true_y(world_at(w, t), x, a, True)+(noise.random() < .1)) % 2
                out.append({'x': x, 'a': a, 'local': local, 'y': y})
        return out

    assert w['main'] == joint(768)
    assert w['selection'] == [joint(32, t) for t in range(64, 769, 64)]


def verify_reclosure(saved, ordinary, mode, counts, pending, nodes, buffer, batch, costs):
    close(saved['before'], pending)
    invalidated = False
    witness = None
    groups = [n.state()['groups'] for n in nodes]
    if ordinary['accepted']:
        pending = None
        action = 'ordinary_replacement'
    elif mode == 'coarse':
        pending = None
        action = 'already_coarse'
    else:
        if pending is not None and pending['groups'] != groups:
            pending = None
            invalidated = True
            costs['group_invalidations'] += 1
        if pending is None:
            pending = {'model': upper_state('coarse', upper_table('coarse', buffer, nodes)),
                       'groups': groups, 'passes': 0}
            costs['challenger_starts'] += 1
        coarse = pending['model']['counts']
        costs['max_pending_cells'] = max(costs['max_pending_cells'], len(coarse))
        loss = upper_loss('coarse', coarse, nodes, batch)
        old = upper_loss(mode, counts, nodes, batch)
        passed = loss <= .55 and loss-old <= .02
        costs['challenger_predictions'] += len(batch)
        witness = {'model': copy.deepcopy(pending['model']), 'groups': groups,
                   'loss': loss, 'fine_loss': old, 'passed': passed, 'prior_passes': pending['passes']}
        if passed:
            pending['passes'] += 1
            if pending['passes'] == 2:
                mode, counts = 'coarse', copy.deepcopy(coarse)
                pending = None
                costs['accepted_reclosures'] += 1
                action = 'reclosed'
            else:
                action = 'awaiting_witness'
        else:
            pending = None
            costs['failed_witnesses'] += 1
            action = 'witness_failed'
    close(saved, {'before': saved['before'], 'invalidated': invalidated,
                  'witness': witness, 'action': action, 'after': pending})
    return mode, counts, pending


def verify_metrics(r, w, losses):
    reviews = r['reviews']
    reclosed = [v['index'] for v in reviews if v.get('reclosure', {}).get('action') == 'reclosed']
    hidden = [v['index'] for v in reviews if v['ordinary']['before']['mode'] != 'coarse'
              and v['upper_after']['mode'] == 'coarse']
    reopened = [v['index'] for v in reviews if v['ordinary']['before']['mode'] == 'coarse'
                and v['upper_after']['mode'] != 'coarse']
    middle, final = reviews[5]['evaluation'], reviews[-1]['evaluation']
    trajectory = (w['branch'] == 'transient' and good(middle) and middle['mode'] == f"fine{w['affected']}"
                  and good(final) and final['mode'] == 'coarse' and any(t > 384 for t in reclosed))
    close(r['metrics'], {
        'transfer_valid': good(r['transfer']), 'final_valid': good(final),
        'coarse_final_valid': good(final) and final['mode'] == 'coarse',
        'affected_fine_final_valid': good(final) and final['mode'] == f"fine{w['affected']}",
        'transient_trajectory': trajectory, 'reclosure_reviews': reclosed,
        'hide_reviews': hidden, 'reopen_reviews': reopened,
        'first_valid_after384': next((v['index'] for v in reviews if v['index'] > 384 and good(v['evaluation'])), None),
        'first_coarse_valid_after384': next((v['index'] for v in reviews if v['index'] > 384 and
            good(v['evaluation']) and v['evaluation']['mode'] == 'coarse'), None),
        'main_loss': mean(losses), 'after384_loss': mean(losses[384:]),
        'late_raw_reads': mean(r['raw_reads'][512:]), 'mean_raw_reads': mean(r['raw_reads']),
        'reclosures_during_breach': sum(1 for t in reclosed if w['branch'] == 'breach' or
                                       (w['branch'] == 'transient' and t <= 384))})


def verify_run(r, w):
    nodes = [ReplayNode(64000+2*r['proposal_seed']+j) for j in range(2)]
    labels = 0
    assert len(r['warmup']) == 4
    for i in range(256):
        for j in range(2):
            nodes[j].update(w['local_main'][j][i])
            labels += 1
        if (i+1) % 64 == 0:
            for j in range(2):
                nodes[j].review(r['warmup'][i//64][j], w['local_selection'][i//64][j])
                labels += 32
    mode, counts = 'coarse', upper_table('coarse', w['composition'], nodes)
    labels += 256
    close(r['initial_upper'], upper_state(mode, counts))
    verify_eval(r['transfer'], mode, counts, nodes, w, False)
    buffer = w['composition'][-192:]
    pending, losses, reads = None, [], []
    refits = refit_rows = upper_fits = upper_fit_rows = 0
    pcosts = dict(challenger_predictions=0, challenger_starts=0, group_invalidations=0,
                  failed_witnesses=0, accepted_reclosures=0, max_pending_cells=0)
    assert len(r['predictions']) == len(r['raw_reads']) == 768 and len(r['reviews']) == 12
    for t, row in enumerate(w['main'], 1):
        p = probability(mode, counts, nodes, row['x'], row['a'])
        close(r['predictions'][t-1], p)
        losses.append(logloss(p, row['y']))
        raw = int(mode != 'coarse')
        reads.append(raw)
        assert r['raw_reads'][t-1] == raw
        for j in range(2):
            nodes[j].update({'x': row['x'][j], 'y': row['local'][j]})
        buffer = (buffer+[row])[-192:]
        labels += 3
        if mode != 'coarse':
            counts = upper_table(mode, buffer, nodes)
            refits += 1
            refit_rows += len(buffer)
        if t % 64:
            continue
        rev, batch = r['reviews'][t//64-1], w['selection'][t//64-1]
        assert rev['index'] == t and len(rev['local']) == 2
        for j in range(2):
            nodes[j].review(rev['local'][j], [{'x': z['x'][j], 'y': z['local'][j]} for z in batch])
        labels += 3*len(batch)
        mode, counts = verify_upper(rev['ordinary'], mode, counts, nodes, buffer, batch)
        upper_fits += 3
        upper_fit_rows += 3*len(buffer)
        if r['variant'] == 'reclose':
            mode, counts, pending = verify_reclosure(
                rev['reclosure'], rev['ordinary'], mode, counts, pending, nodes, buffer, batch, pcosts)
        else:
            assert 'reclosure' not in rev
        close(rev['upper_after'], upper_state(mode, counts))
        verify_eval(rev['evaluation'], mode, counts, nodes, world_at(w, t), True)
    close(r['final_upper'], upper_state(mode, counts))
    close(r['final_local'], [n.state() for n in nodes])
    close(r['pending'], pending)
    costs = {k: sum(n.costs[k] for n in nodes) for k in nodes[0].costs}
    costs.update(upper_refits=refits, upper_refit_rows=refit_rows, upper_candidate_fits=upper_fits,
                 upper_candidate_rows=upper_fit_rows, feedback_labels=labels, prediction_raw_reads=sum(reads))
    costs.update(pcosts)
    close(r['costs'], costs)
    verify_metrics(r, w, losses)


def verify_summary(runs, saved):
    def get(b, v):
        return [r for r in runs if (r['branch'], r['variant']) == (b, v)]
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            rs = get(b, v)
            assert len(rs) == 10
            groups.append({
                'branch': b, 'variant': v,
                'transfer_valid': sum(r['metrics']['transfer_valid'] for r in rs),
                'final_valid': sum(r['metrics']['final_valid'] for r in rs),
                'coarse_final_valid': sum(r['metrics']['coarse_final_valid'] for r in rs),
                'affected_fine_final_valid': sum(r['metrics']['affected_fine_final_valid'] for r in rs),
                'transient_trajectories': sum(r['metrics']['transient_trajectory'] for r in rs),
                'main_loss': mean(r['metrics']['main_loss'] for r in rs),
                'after384_loss': mean(r['metrics']['after384_loss'] for r in rs),
                'late_raw_reads': mean(r['metrics']['late_raw_reads'] for r in rs),
                'reclosures': sum(len(r['metrics']['reclosure_reviews']) for r in rs),
                'reclosures_during_breach': sum(r['metrics']['reclosures_during_breach'] for r in rs)})
    pairs = []
    for b in BRANCHES:
        for seed in range(400, 405):
            for ps in (400, 401):
                data = {r['variant']: r['metrics'] for r in runs
                        if (r['branch'], r['seed'], r['proposal_seed']) == (b, seed, ps)}
                a, c = data['reclose'], data['failure_only']
                pairs.append({'branch': b, 'seed': seed, 'proposal_seed': ps,
                              'main_cost': a['main_loss']-c['main_loss'],
                              'after384_cost': a['after384_loss']-c['after384_loss'],
                              'late_read_reduction': c['late_raw_reads']-a['late_raw_reads']})
    tp = [p for p in pairs if p['branch'] == 'transient']
    a = mean(r['metrics']['late_raw_reads'] for r in get('transient', 'reclose'))
    c = mean(r['metrics']['late_raw_reads'] for r in get('transient', 'failure_only'))
    checks = {
        'transfer': all(sum(r['metrics']['transfer_valid'] for r in get('persistent', v)) >= 8 for v in VARIANTS),
        'persistent_coarse': sum(r['metrics']['coarse_final_valid'] for r in get('persistent', 'reclose')) >= 8,
        'remap_coarse': sum(r['metrics']['coarse_final_valid'] for r in get('remap', 'reclose')) >= 8,
        'persistent_loss_guard': mean(p['main_cost'] for p in pairs if p['branch'] == 'persistent') <= .02,
        'breach_preserved': sum(r['metrics']['affected_fine_final_valid'] for r in get('breach', 'reclose')) >= 8,
        'breach_loss_guard': mean(p['main_cost'] for p in pairs if p['branch'] == 'breach') <= .02,
        'transient_trajectories': sum(r['metrics']['transient_trajectory'] for r in get('transient', 'reclose')) >= 8,
        'transient_access_pairs': sum(p['late_read_reduction'] > 0 for p in tp) >= 8,
        'transient_access_mean': c > 0 and a <= .75*c,
        'transient_loss_guard': mean(p['after384_cost'] for p in tp) <= .02}
    close(saved, {'groups': groups, 'paired': pairs, 'checks': checks, 'primary_pass': all(checks.values())})


def main():
    data = json.loads((OUT/'results.json').read_text())
    manifest = json.loads((OUT/'manifest.json').read_text())
    assert manifest == data['hashes']
    assert set(manifest) == {'experiments/reclosure_protocol.md', 'experiments/reclosure.py',
                             'checks/test_reclosure.py', 'checks/audit_reclosure.py',
                             'experiments/nested_abstractions.py', 'checks/audit_nested_abstractions.py'}
    for folder in ('bundles-v1', 'bundle-retention-v1', 'interfaces-v1',
                   'nested-abstractions-v1', 'reclosure-v1'):
        for p, digest in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == digest, p
    worlds = {(w['seed'], w['branch']): w for w in data['worlds']}
    assert len(worlds) == len(data['worlds']) == 20
    assert set(worlds) == {(s, b) for s in range(400, 405) for b in BRANCHES}
    for w in worlds.values():
        verify_world(w)
    runs = data['runs']
    assert len(runs) == 80
    assert {(r['seed'], r['branch'], r['variant'], r['proposal_seed']) for r in runs} == {
        (s, b, v, ps) for s in range(400, 405) for b in BRANCHES for v in VARIANTS for ps in (400, 401)}
    for r in runs:
        verify_run(r, worlds[(r['seed'], r['branch'])])
    for s in range(400, 405):
        for ps in (400, 401):
            rows = [r for r in runs if (r['seed'], r['proposal_seed']) == (s, ps)]
            assert all(r['warmup'] == rows[0]['warmup'] and r['initial_upper'] == rows[0]['initial_upper']
                       for r in rows)
            for b in BRANCHES:
                a, c = [r for r in rows if r['branch'] == b]
                assert [v['local'] for v in a['reviews']] == [v['local'] for v in c['reviews']]
    verify_summary(runs, data['summary'])
    costs = {k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs'] if k != 'max_pending_cells'}
    peak = max(r['costs']['max_pending_cells'] for r in runs)
    assert costs['candidate_fits'] == 10240 and costs['upper_candidate_fits'] == 2880
    assert costs['challenger_predictions'] <= 15360 and costs['feedback_labels'] == 358400 and peak <= 8
    close(data['totals'], {'runs': 80, 'allocated_label_presentations': 358400,
                           'generated_labels': 89600, 'evaluation_predictions': 32640,
                           'max_pending_cells_per_run': peak, 'costs': costs})
    close(json.loads((OUT/'metrics.json').read_text()), {
        'summary': data['summary'], 'totals': data['totals'], 'runs': [
            {k: r[k] for k in ('seed', 'branch', 'variant', 'proposal_seed', 'metrics', 'costs')}
            for r in runs]})
    print('PASS: 80 runs independently replayed, including paired local learning, '
          'frozen challengers, consecutive witnesses, resets, reclosure, metrics, costs and five manifests.')


if __name__ == '__main__':
    main()
