"""Independent replay of 015. Imports only independent 013 audit arithmetic."""
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import statistics as st

from audit_nested_abstractions import (
    ReplayNode, close, local_loss, local_p, local_state, logloss)

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/form-retention-v1'
BRANCHES = ('persistent', 'remap', 'transient')
VARIANTS = ('immediate', 'uniform', 'earned')


def form(w, t, observed=False):
    j = int((w['branch'] == 'remap' and t >= 513) or
            (observed and w['branch'] == 'transient' and 513 <= t <= 576))
    return w['forms'][j]


def verify_world(w):
    permutation = [0, 1, 2, 3]
    random.Random(71000+w['seed']).shuffle(permutation)
    first = [int(x in permutation[2:]) for x in range(4)]
    second = [1-y if x in (permutation[0], permutation[2]) else y
              for x, y in enumerate(first)]
    assert w['forms'] == [first, second]
    inp, noise = random.Random(72000+w['seed']), random.Random(73000+w['seed'])
    for field, batches in [('main', [(1024, None)]),
                          ('selection', [(32, t) for t in range(64, 1025, 64)])]:
        result = []
        for n, t in batches:
            rows = []
            for start in range(0, n, 4):
                xs = [0, 1, 2, 3]
                inp.shuffle(xs)
                for x in xs:
                    index = t if t is not None else len(rows)+1
                    rows.append(dict(x=x, y=(form(w, index, True)[x]+
                                            int(noise.random() < .1)) % 2))
            result.append(rows)
        assert w[field] == (result[0] if field == 'main' else result)


def table(state):
    return tuple(state['partition']), {int(k): v.copy() for k, v in state['counts'].items()}


def expectation(p, y):
    q = .1+.8*y
    return -q*math.log(p)-(1-q)*math.log1p(-p)


def evaluation(state, target, index):
    part, counts = table(state)
    probabilities = [local_p(part, counts, x) for x in range(4)]
    loss = st.mean(expectation(p, y) for p, y in zip(probabilities, target))
    regret = loss-(-.1*math.log(.1)-.9*math.log(.9))
    exact = state['groups'] == target
    accuracy = sum((p >= .5) == y for p, y in zip(probabilities, target))/4
    return dict(index=index, probabilities=probabilities, exact=exact,
                accuracy=accuracy, expected_loss=loss, regret=regret,
                valid=exact and accuracy == 1 and regret <= .10)


def verify_run(r, w):
    node = ReplayNode(74000+r['proposal_seed'])
    policy = dict(established=False, adequate=0, pending=None)
    costs = dict(pending_predictions=0, pending_starts=0, pending_failures=0,
                 confirmed_replacements=0, immediate_replacements=0,
                 establishments=0, max_pending_cells=0)
    evaluations = [evaluation(node.state(), form(w, 0), 0)]
    losses, latent, replacements, harmful, wrong = [], [], [], [], []
    for t, row in enumerate(w['main'], 1):
        p = local_p(node.partition, node.table, row['x'])
        close(r['predictions'][t-1], p)
        losses.append(logloss(p, row['y']))
        latent.append(expectation(p, form(w, t)[row['x']]))
        node.update(row)
        if t % 64:
            continue
        saved = r['reviews'][t//64-1]
        assert saved['index'] == t
        batch = w['selection'][t//64-1]
        incumbent = node.state()
        # Replay all original search, arithmetic and immediate decision first,
        # then independently replace its decision using the new policy.
        node.review(saved['ordinary'], batch)
        proposed = saved['ordinary']['candidates'][saved['ordinary']['winner']]['state']
        old = local_loss(*table(incumbent), batch)
        new = local_loss(*table(proposed), batch)
        before = copy.deepcopy(policy)
        chosen, accepted, action, pending_loss = incumbent, False, 'keep', None
        if policy['pending'] is not None:
            pending_loss = local_loss(*table(policy['pending']), batch)
            costs['pending_predictions'] += 32
            if old-pending_loss > .005:
                chosen = copy.deepcopy(policy['pending'])
                accepted, action = True, 'confirmed'
                costs['confirmed_replacements'] += 1
            else:
                action = 'pending_failed'
                costs['pending_failures'] += 1
            policy['pending'] = None
        elif old-new > .005:
            if r['variant'] == 'uniform' or (r['variant'] == 'earned' and policy['established']):
                policy['pending'] = copy.deepcopy(proposed)
                action = 'pending_started'
                costs['pending_starts'] += 1
                costs['max_pending_cells'] = max(costs['max_pending_cells'], len(proposed['counts']))
            else:
                chosen, accepted, action = proposed, True, 'immediate'
                costs['immediate_replacements'] += 1
        if accepted:
            policy.update(established=False, adequate=0)
            replacements.append(t)
            if incumbent['groups'] == form(w, t) and chosen['groups'] != form(w, t):
                harmful.append(t)
        else:
            policy['adequate'] = min(2, policy['adequate']+1) if old <= .55 else 0
            if policy['adequate'] == 2 and not policy['established']:
                policy['established'] = True
                costs['establishments'] += 1
        if not before['established'] and policy['established'] and chosen['groups'] != form(w, t):
            wrong.append(t)
        close(saved['policy'], dict(before=before, after=policy, action=action,
                                    accepted=accepted, pending_loss=pending_loss))
        node.partition, node.table = table(chosen)
        close(saved['after'], node.state())
        evaluations.append(evaluation(node.state(), form(w, t), t))
    close(r['evaluations'], evaluations)
    close(r['final'], node.state())
    close(r['policy'], policy)
    close(r['costs'], dict(**node.costs, **costs, used_labels=1536, ordinary_selection_predictions=1024))
    recovery = next((evaluations[i]['index'] for i in range(9, 16)
                     if evaluations[i]['valid'] and evaluations[i+1]['valid']), 1088)
    acquisition = min([e['index'] for e in evaluations[1:9] if e['valid']]+[576])
    calculated = dict(initial_valid=evaluations[4]['valid'], initial_exact=evaluations[4]['exact'],
        first_acquisition=acquisition, stable_recovery=recovery,
        final_valid=evaluations[-1]['valid'], final_exact=evaluations[-1]['exact'],
        invalid_checkpoints=sum(not e['valid'] for e in evaluations[5:]),
        inexact_checkpoints=sum(not e['exact'] for e in evaluations[5:]),
        main_loss=st.mean(losses), change_loss=st.mean(losses[512:]),
        transient_latent_loss=st.mean(latent[512:768]),
        replacement_reviews=replacements, harmful_replacements=harmful, wrong_establishments=wrong)
    close(r['metrics'], calculated)
    return calculated


def verify_summary(data):
    groups = {}
    for saved in data['summary']['groups']:
        b, v = saved['branch'], saved['variant']
        ms = [r['metrics'] for r in data['runs'] if (r['branch'], r['variant']) == (b, v)]
        assert len(ms) == 10
        calc = dict(branch=b, variant=v)
        for k in ('initial_valid', 'initial_exact', 'final_valid', 'final_exact',
                  'invalid_checkpoints', 'inexact_checkpoints'):
            calc[k] = sum(m[k] for m in ms)
        for k in ('first_acquisition', 'stable_recovery', 'main_loss', 'change_loss', 'transient_latent_loss'):
            calc[k] = st.mean(m[k] for m in ms)
        for k in ('replacement_reviews', 'harmful_replacements', 'wrong_establishments'):
            calc[k] = sum(len(m[k]) for m in ms)
        close(saved, calc)
        groups[b, v] = calc
    assert set(groups) == {(b, v) for b in BRANCHES for v in VARIANTS}
    pairs = []
    for b in BRANCHES:
        for seed in range(500, 505):
            for ps in (500, 501):
                ms = {r['variant']: r['metrics'] for r in data['runs']
                      if (r['branch'], r['seed'], r['proposal_seed']) == (b, seed, ps)}
                c, a = ms['immediate'], ms['earned']
                pairs.append(dict(branch=b, seed=seed, proposal_seed=ps,
                    invalid_reduction=c['invalid_checkpoints']-a['invalid_checkpoints'],
                    acquisition_delay=a['first_acquisition']-c['first_acquisition'],
                    recovery_delay=a['stable_recovery']-c['stable_recovery']))
    close(data['summary']['paired'], pairs)
    a, c = groups['persistent', 'earned'], groups['persistent', 'immediate']
    stable_a = sum(groups[b, 'earned']['invalid_checkpoints'] for b in ('persistent', 'transient'))
    stable_c = sum(groups[b, 'immediate']['invalid_checkpoints'] for b in ('persistent', 'transient'))
    ra, rc = groups['remap', 'earned'], groups['remap', 'immediate']
    checks = dict(
        acquisition=a['initial_valid'] >= 8 and a['initial_valid'] >= c['initial_valid']-1
                    and a['first_acquisition']-c['first_acquisition'] <= 64,
        stable_final=all(groups[b, 'earned']['final_valid'] >= 8 for b in ('persistent', 'transient')),
        protection=stable_c > 0 and stable_a <= .75*stable_c
                   and sum(p['invalid_reduction'] > 0 for p in pairs if p['branch'] != 'remap') >= 2,
        persistent_loss=a['main_loss']-c['main_loss'] <= .02,
        transient_loss=groups['transient', 'earned']['transient_latent_loss']
                       -groups['transient', 'immediate']['transient_latent_loss'] <= .02,
        remap_final=ra['final_valid'] >= 8,
        remap_latency=ra['stable_recovery']-rc['stable_recovery'] <= 64,
        remap_loss=ra['change_loss']-rc['change_loss'] <= .05)
    close(data['summary']['checks'], checks)
    assert data['summary']['primary_pass'] == all(checks.values())


def main():
    for folder in ('bundles-v1', 'bundle-retention-v1', 'interfaces-v1',
                   'nested-abstractions-v1', 'reclosure-v1', 'form-retention-v1'):
        for p, h in json.loads((ROOT/'results'/folder/'manifest.json').read_text()).items():
            assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest() == h, p
    data = json.loads((OUT/'results.json').read_text())
    assert data['hashes'] == json.loads((OUT/'manifest.json').read_text())
    assert len(data['worlds']) == 15 and len(data['runs']) == 90
    worlds = {(w['seed'], w['branch']): w for w in data['worlds']}
    assert set(worlds) == {(s, b) for s in range(500, 505) for b in BRANCHES}
    for w in worlds.values():
        verify_world(w)
    keys = {(r['seed'], r['proposal_seed'], r['branch'], r['variant']) for r in data['runs']}
    assert keys == {(s, ps, b, v) for s in range(500, 505) for ps in (500, 501)
                    for b in BRANCHES for v in VARIANTS}
    for r in data['runs']:
        verify_run(r, worlds[r['seed'], r['branch']])
    verify_summary(data)
    totals = dict(runs=90, generated_labels=23040, allocated_labels=138240,
                  checkpoint_queries=6120, main_predictions=92160,
                  max_pending_cells=max(r['costs']['max_pending_cells'] for r in data['runs']),
                  costs={k: sum(r['costs'][k] for r in data['runs'])
                         for k in data['runs'][0]['costs'] if k != 'max_pending_cells'})
    close(data['totals'], totals)
    assert totals['costs']['used_labels'] == 138240
    assert totals['costs']['candidate_fits'] == 5760
    assert totals['costs']['pending_predictions'] <= 30720
    assert totals['max_pending_cells'] <= 2
    metrics = json.loads((OUT/'metrics.json').read_text())
    close(metrics, dict(summary=data['summary'], totals=totals,
        runs=[{k: r[k] for k in ('seed', 'branch', 'variant', 'proposal_seed', 'metrics', 'costs')}
              for r in data['runs']]))
    print('PASS: 90 runs independently replayed; streams, decisions, outputs, metrics, costs and six manifests verified.')


if __name__ == '__main__':
    main()
