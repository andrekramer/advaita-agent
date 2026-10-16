"""Audit saved experiment 006 arithmetic without importing the learner code."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

ROOT = Path(__file__).resolve().parents[1]
XS = list(itertools.product((0, 1), repeat=3))


def near(a, b):
    assert math.isfinite(a) and math.isfinite(b)
    assert abs(a - b) < 1e-11, (a, b)


def nll(p, y):
    assert 0 < p < 1
    return -math.log(p if y else 1 - p)


def assignment(state, x):
    matching = [k for rule, k in state['structure']
                if all(v < 0 or v == x[i] for i, v in enumerate(rule))]
    assert len(matching) == 1
    return matching[0]


def structural_p(state, x, a):
    r, n = state['counts'][assignment(state, x)][a]
    return (r + 1) / (n + 2)


def vector(x, a):
    bits = [2 * v - 1 for v in x]
    action = 2 * a - 1
    return [1, action, *bits, *(v * action for v in bits)]


def predict(state, variant, x, a):
    if 'structure' in variant:
        return structural_p(state['model'], x, a)
    if variant == 'lookup':
        r, n = state['counts'][XS.index(tuple(x))][a]
        return (r + 1) / (n + 2)
    z = sum(w * v for w, v in zip(state['weights'], vector(x, a)))
    return 1 / (1 + math.exp(-z))


def refit(state, records):
    result = copy.deepcopy(state)
    result['counts'] = [[[0, 0], [0, 0]] for _ in state['counts']]
    for row in records:
        pair = result['counts'][assignment(result, row['x'])][row['a']]
        pair[0] += row['y']
        pair[1] += 1
    return result


def objective(state, rows):
    return (sum(nll(structural_p(state, r['x'], r['a']), r['y']) for r in rows) / len(rows)
            + .01 * len(state['counts']) + .005 * len(state['structure']))


def step(state, variant, row):
    result = copy.deepcopy(state)
    x, a, y = row['x'], row['a'], row['y']
    if 'structure' in variant:
        model = result['provisional'] if variant == 'retained_structure' else result['model']
        pair = model['counts'][assignment(model, x)][a]
        pair[0] += y
        pair[1] += 1
        result['buffer_size'] += 1
    elif variant == 'lookup':
        pair = result['counts'][XS.index(tuple(x))][a]
        pair[0] += y
        pair[1] += 1
    else:
        p = predict(state, variant, x, a)
        raw = [w + .1 * (y - p) * v for w, v in zip(state['weights'], vector(x, a))]
        result['weights'] = [min(8, max(-8, w)) for w in raw]
        result['clips'] += sum(abs(w) > 8 for w in raw)
    return result


def equal_state(first, second):
    # Sigmoid implementations may differ in the last bit.
    if 'weights' in first:
        assert first.keys() == second.keys()
        assert first['clips'] == second['clips']
        for a, b in zip(first['weights'], second['weights']):
            near(a, b)
    else:
        assert first == second


def audit_run(run):
    seed, variant = run['seed'], run['variant']
    perm = [0, 1, 2]
    random.Random(seed).shuffle(perm)
    assert run['permutation'] == perm
    relevant = perm.index(0)
    support = [{'x': [x[j] for j in perm], 'a': a, 'y': x[0] ^ a}
               for x in XS if x not in ((0, 0, 0), (1, 1, 1)) for a in (0, 1)]
    rng, vrng = random.Random(1000 + seed), random.Random(2000 + seed)
    training, selection = [], []
    for _ in range(16):
        block = copy.deepcopy(support)
        rng.shuffle(block)
        training.extend(block)
    for _ in range(4):
        block = copy.deepcopy(support)
        vrng.shuffle(block)
        selection.append(block)
    probes = sorted((r['x'], r['a']) for r in support)
    assert run['probes'] == [[x, a] for x, a in probes]
    history, selection_seen, main_losses = [], [], []
    previous, review_count, candidates_total, accepted_total = None, 0, 0, 0
    for event in run['events']:
        before, after = event['before'], event['after']
        if previous is not None:
            equal_state(previous, before)
        else:
            if 'structure' in variant:
                assert before['model'] == {'structure': [[[-1, -1, -1], 0]],
                                            'counts': [[[0, 0], [0, 0]]]}
                assert before['buffer_size'] == 0 and before['dbar'] == 0
                assert before['provisional'] == (before['model'] if variant == 'retained_structure' else None)
            elif variant == 'lookup':
                assert before['counts'] == [[[0, 0], [0, 0]] for _ in XS]
            else:
                assert before == {'weights': [0.] * 8, 'clips': 0}
        if event['kind'] != 'review':
            row = event['row']
            assert tuple(row['x']) not in ((0, 0, 0), (1, 1, 1))
            near(event['p'], predict(before, variant, row['x'], row['a']))
            equal_state(step(before, variant, row), after)
            if event['kind'] == 'train':
                assert event['index'] == len(history) + 1
                assert row == training[len(history)]
                history.append(row)
                main_losses.append(nll(event['p'], row['y']))
                if variant == 'retained_structure':
                    near(event['provisional_p'], structural_p(before['provisional'], row['x'], row['a']))
            else:
                assert 'structure' not in variant and event['index'] in (48, 96, 144, 192)
                selection_seen.append(row)
        else:
            review_count += 1
            assert event['index'] == 48 * review_count == len(history)
            rows = event['selection']
            assert rows == selection[review_count - 1]
            selection_seen.extend(rows)
            candidates = event['candidates']
            candidates_total += len(candidates)
            assert 1 <= len(candidates) <= 31
            structures = [c['state']['structure'] for c in candidates]
            assert structures == sorted(structures)
            assert len({json.dumps(s) for s in structures}) == len(structures)
            for candidate in candidates:
                state = candidate['state']
                assert 1 <= len(state['counts']) <= 4 and 1 <= len(state['structure']) <= 8
                for x in XS:
                    assignment(state, x)
                assert state == refit(state, history)
                near(candidate['training_objective'], objective(state, history))
            winner = min(range(len(candidates)), key=lambda i: (
                candidates[i]['training_objective'], candidates[i]['state']['structure']))
            assert winner == event['winner']
            assert [c['advanced'] for c in candidates] == [i == winner for i in range(len(candidates))]
            candidate = candidates[winner]['state']
            decision = event['decision']
            inc, cand = objective(before['model'], rows), objective(candidate, rows)
            near(decision['incumbent_objective'], inc)
            near(decision['candidate_objective'], cand)
            near(decision['gain'], inc - cand)
            accepted = inc - cand > .001
            assert accepted == decision['accepted']
            accepted_total += accepted
            before_ps = [structural_p(before['model'], r['x'], r['a']) for r in rows]
            after_ps = [structural_p(candidate, r['x'], r['a']) for r in rows]
            for a, b in zip(before_ps, decision['incumbent_predictions']):
                near(a, b)
            for a, b in zip(after_ps, decision['candidate_predictions']):
                near(a, b)
            near(decision['max_prediction_change'], max(abs(a-b) for a,b in zip(before_ps, after_ps)) if accepted else 0.)
            expected = copy.deepcopy(before)
            if accepted:
                expected['model'] = candidate
            if variant == 'retained_structure':
                gaps = [structural_p(before['provisional'], x, a) - structural_p(before['model'], x, a)
                        for x, a in probes]
                d = sum(abs(g) for g in gaps) / 12
                expected['dbar'] = .75 * before['dbar'] + .25 * d
                assert event['diagnostic']['gaps'] == gaps
                near(event['diagnostic']['D'], d)
                near(event['diagnostic']['Dbar'], expected['dbar'])
                expected['provisional'] = refit(expected['model'], history)
            else:
                assert event['diagnostic'] is None
            equal_state(expected, after)
        previous = after
    assert history == training
    assert selection_seen == [r for batch in selection for r in batch]
    assert review_count == (4 if 'structure' in variant else 0)
    final = run['final']
    equal_state(previous, final['state_before'])
    assert final['state_before'] == final['state_after']
    table = final['table']
    assert [(r['x'], r['a']) for r in table] == [(list(x), a) for x in XS for a in (0, 1)]
    for row in table:
        near(row['p'], predict(previous, variant, row['x'], row['a']))
    held = [{**r, 'y': r['x'][relevant] ^ r['a']} for r in table
            if tuple(r['x']) in ((0, 0, 0), (1, 1, 1))]
    assert final['withheld'] == held and len(held) == 4
    metrics = final['metrics']
    near(metrics['accuracy'], sum((r['p'] > .5) == r['y'] for r in held) / 4)
    near(metrics['loss'], sum(nll(r['p'], r['y']) for r in held) / 4)
    near(metrics['training_loss'], sum(main_losses) / 192)
    assert metrics['candidate_count'] == candidates_total
    assert metrics['accepted_reviews'] == accepted_total
    values = {(tuple(r['x']), r['a']): r['p'] for r in table}
    effects = [[], [], []]
    for x in XS:
        for d in range(3):
            other = list(x)
            other[d] ^= 1
            effects[d].extend(abs(values[x, a] - values[tuple(other), a]) for a in (0, 1))
    nuisance, relevant_effect = max(max(effects[d]) for d in range(3) if d != relevant), min(effects[relevant])
    near(metrics['nuisance_effect'], nuisance)
    near(metrics['relevant_effect'], relevant_effect)
    if 'structure' in variant:
        model = previous['model']
        exact = all((assignment(model, x) == assignment(model, y)) == (x[relevant] == y[relevant])
                    for x, y in itertools.combinations(XS, 2))
        assert metrics['partition_exact'] == exact
        assert metrics['forms'] == len(model['counts'])
        assert metrics['leaves'] == len(model['structure'])
        passed = (metrics['accuracy'] == 1 and metrics['loss'] < .25 and exact
                  and len(model['counts']) == len(model['structure']) == 2
                  and nuisance <= 1e-12 and relevant_effect >= .5)
        assert metrics['acquisition_pass'] == passed


def main():
    path = ROOT / 'results/forms-v1/results.json'
    data = json.loads(path.read_text())
    for name, digest in data['hashes'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    assert [(r['seed'], r['variant']) for r in data['runs']] == [
        (seed, variant) for seed in range(5)
        for variant in ('lookup', 'single_structure', 'retained_structure', 'fixed_features')]
    for run in data['runs']:
        audit_run(run)
    assert data['outcome_presentations'] == len(data['runs']) * (192 + 48 + 4) == 4880
    assert data['unlabelled_final_predictions'] == 240
    assert data['paired_diagnostic_probes'] == 240
    print('PASS: 20 runs; streams, updates, feedback separation, candidate fits, selection,')
    print('frozen evaluation, acquisition metrics, budgets and source hashes independently audited.')


if __name__ == '__main__':
    main()
