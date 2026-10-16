"""Audit Experiment 009 saved traces; no experiment/learner code is imported."""
import hashlib
import json
from pathlib import Path
import random
import statistics

from audit_collapse import XS, acquired, checkpoint, close, fit, nll, p, penalty, pool, prediction_loss

ROOT = Path(__file__).resolve().parents[1]
TIMES = (48, 96, 144, 192, 240, 288, 336)


def stage(t):
    if t < 109:
        return 'A1'
    if t < 229:
        return 'B'
    return 'A2'


def evidence(seed):
    perm = [0, 1, 2]
    random.Random(seed).shuffle(perm)
    support = [(x, a) for x in XS if x not in ((0, 0, 0), (1, 1, 1)) for a in (0, 1)]
    main_rng, select_rng = random.Random(seed + 10000), random.Random(seed + 11000)
    main, batches = [], []
    for block in range(28):
        pairs = support.copy()
        main_rng.shuffle(pairs)
        for x, a in pairs:
            t = len(main) + 1
            main.append({'x': [x[d] for d in perm], 'a': a, 'y': a if 108 < t <= 228 else x[0] ^ a})
    for t in TIMES:
        pairs = support.copy()
        select_rng.shuffle(pairs)
        batches.append([{'x': [x[d] for d in perm], 'a': a, 'y': a if 108 < t <= 228 else x[0] ^ a} for x, a in pairs])
    return perm, main, batches


def elapsed(t, change):
    return None if t is None else {'review': t, 'main_since_change': t - change,
                                  'selection_since_change': 12 * len([v for v in TIMES if change < v <= t])}


def invariant(m):
    return m['accuracy'] == 1 and m['loss'] < .25 and m['context_effect'] <= 1e-12 and m['action_effect'] >= .5


def verify(run):
    perm, training, selection = evidence(run['seed'])
    assert run['permutation'] == perm
    enabled = run['variant'] == 'merge_enabled'
    model = fit((((-1, -1, -1), 0),), [])
    window, snapshots = [], {}
    seen = review = 0
    costs = dict.fromkeys(('count_refits', 'count_refit_rows', 'candidate_fits', 'candidate_fit_rows', 'selection_outcomes'), 0)
    losses, merges, splits = [], [], []
    def state():
        return {'model': model, 'seen': seen, 'window_size': len(window), 'window_start': max(1, seen - 47)}
    assert len(run['events']) == 343
    for e in run['events']:
        close(e['before'], state())
        if e['kind'] == 'train':
            assert e['index'] == seen + 1
            assert e['row'] == training[seen]
            row = e['row']
            assert tuple(row['x']) not in ((0, 0, 0), (1, 1, 1))
            close(e['p'], p(model, row['x'], row['a']))
            losses.append((seen + 1, nll(e['p'], row['y'])))
            window = (window + [row])[-48:]
            seen += 1
            model = fit(model['structure'], window)
            costs['count_refits'] += 1
            costs['count_refit_rows'] += len(window)
        else:
            assert e['kind'] == 'review' and e['index'] == seen == TIMES[review]
            rows = selection[review]
            review += 1
            assert e['selection'] == rows
            structures = pool(model['structure'], enabled)
            close([c['state']['structure'] for c in e['candidates']], structures)
            costs['candidate_fits'] += len(structures)
            costs['candidate_fit_rows'] += len(structures) * len(window)
            scores = []
            for c, structure in zip(e['candidates'], structures):
                fitted = fit(structure, window)
                close(c['state'], fitted)
                value = prediction_loss(fitted, window)
                close(c['training_loss'], value)
                close(c['penalty'], penalty(fitted))
                # Match the declared executable's sum/divide order for exact
                # floating-point ties; loss reporting uses the mean helper.
                scores.append(sum(nll(p(fitted, r['x'], r['a']), r['y']) for r in window)
                              / len(window) + penalty(fitted))
                close(c['training_objective'], scores[-1])
            winner = min(range(len(structures)), key=lambda i: (scores[i], structures[i]))
            assert e['winner'] == winner
            assert [c['advanced'] for c in e['candidates']] == [i == winner for i in range(len(structures))]
            candidate = e['candidates'][winner]['state']
            old_loss, new_loss = prediction_loss(model, rows), prediction_loss(candidate, rows)
            cg = penalty(model) - penalty(candidate)
            gain = old_loss - new_loss + cg
            accepted = gain > .001
            merge = accepted and len(candidate['counts']) < len(model['counts'])
            split = accepted and len(candidate['counts']) > len(model['counts'])
            close(e['decision'], {
                'incumbent_predictions': [p(model, r['x'], r['a']) for r in rows],
                'candidate_predictions': [p(candidate, r['x'], r['a']) for r in rows],
                'incumbent_loss': old_loss, 'candidate_loss': new_loss,
                'prediction_gain': old_loss - new_loss, 'complexity_gain': cg,
                'gain': gain, 'accepted': accepted, 'merge': merge})
            if merge:
                merges.append(seen)
            if split:
                splits.append(seen)
            if accepted:
                model = candidate
            costs['selection_outcomes'] += 12
            snapshots[seen] = state()
        close(e['after'], state())
    assert seen == 336 and review == 7
    close(run['costs'], costs)
    close(run['final_buffer'], window)
    assert [c['index'] for c in run['checkpoints']] == list(TIMES)
    for c in run['checkpoints']:
        t = c['index']
        close(c['before'], snapshots[t])
        checkpoint(c, snapshots[t]['model'], perm.index(0), stage(t) == 'B')
    ms = {c['index']: c['metrics'] for c in run['checkpoints']}
    first_merge = next((t for t in merges if 108 < t <= 228), None)
    one = next((t for t in TIMES if stage(t) == 'B' and ms[t]['forms'] == 1), None)
    collapsed = next((t for t in TIMES if stage(t) == 'B' and ms[t]['forms'] == ms[t]['leaves'] == 1 and invariant(ms[t])), None)
    reopened = next((t for t in splits if t > 228), None)
    recovered = next((t for t in TIMES if t > 228 and acquired(ms[t])), None)
    checks = {'acquisition': acquired(ms[96]), 'no_initial_merge': not any(t <= 108 for t in merges),
              'B_prediction_and_invariance': invariant(ms[192]), 'final_acquisition': acquired(ms[336])}
    if enabled:
        checks.update(actual_collapse=first_merge is not None and ms[192]['forms'] == ms[192]['leaves'] == 1,
                      B_stability=one is not None and all(ms[t]['forms'] == 1 for t in TIMES if one <= t <= 228),
                      actual_reopening=first_merge is not None and reopened is not None and reopened > first_merge,
                      recovery_stability=recovered is not None and all(acquired(ms[t]) for t in TIMES if t >= recovered))
    else:
        checks.update(no_merge=not merges, B_retains_two=ms[192]['forms'] == ms[192]['leaves'] == 2)
    expected = {'checks': checks, 'own_pass': all(checks.values()), 'merges': merges, 'splits': splits,
                'first_merge': elapsed(first_merge, 108), 'successful_collapse': elapsed(collapsed, 108),
                'first_return_split': elapsed(reopened, 228), 'successful_recovery': elapsed(recovered, 228),
                'phase_main_loss': {s: statistics.mean(v for t, v in losses if stage(t) == s) for s in ('A1', 'B', 'A2')},
                'transition_48_main_loss': {str(c): statistics.mean(v for t, v in losses if c < t <= c + 48) for c in (108, 228)},
                'review_metrics': [{'index': t, 'phase': stage(t), **ms[t]} for t in TIMES]}
    close(run['metrics'], expected)


def main():
    directory = ROOT / 'results/reversibility-v1'
    data = json.loads((directory / 'results.json').read_text())
    assert data['hashes'] == json.loads((directory / 'manifest.json').read_text())
    for name, digest in data['hashes'].items():
        assert hashlib.sha256((ROOT / name).read_bytes()).hexdigest() == digest, name
    assert [(r['seed'], r['variant']) for r in data['runs']] == [
        (s, v) for s in range(5) for v in ('merge_enabled', 'merge_disabled')]
    for r in data['runs']:
        verify(r)
    pairs = []
    for seed in range(5):
        enabled, disabled = [r for r in data['runs'] if r['seed'] == seed]
        for kind, key in (('train', 'row'), ('review', 'selection')):
            assert [e[key] for e in enabled['events'] if e['kind'] == kind] == [e[key] for e in disabled['events'] if e['kind'] == kind]
        preservation = {}
        for t in (192, 336):
            a, b = [next(c['metrics']['loss'] for c in r['checkpoints'] if c['index'] == t) for r in (enabled, disabled)]
            preservation[str(t)] = {'enabled_loss': a, 'disabled_loss': b, 'passed': a <= b + .01}
        pairs.append({'seed': seed, 'loss_preservation': preservation,
                      'all_conditions_pass': all(p['passed'] for p in preservation.values()) and
                      enabled['metrics']['own_pass'] and disabled['metrics']['own_pass']})
    close(data['comparison'], {'per_seed': pairs, 'passed_seeds': sum(p['all_conditions_pass'] for p in pairs),
                               'overall_pass': all(p['all_conditions_pass'] for p in pairs)})
    assert data['outcome_presentations'] == 10 * (336 + 84 + 28) == 4480
    assert data['unlabelled_predictions'] == 10 * 7 * 12 == 840
    metrics = json.loads((directory / 'metrics.json').read_text())
    close(metrics, {'runs': [{k: r[k] for k in ('seed', 'variant', 'permutation', 'metrics', 'costs')} for r in data['runs']],
                    'comparison': data['comparison']})
    print('PASS: all 10 saved runs, streams, candidate search, rolling counts, decisions,')
    print('frozen evaluations, recovery chronology, criteria, pairing, budgets and hashes.')


if __name__ == '__main__':
    main()
