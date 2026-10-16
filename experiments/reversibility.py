"""Experiment 009: structural reversibility with the unchanged Experiment 008 learner."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import statistics

from collapse import Learner, acquisition_pass, evaluate
from forms import CONTEXTS, loss

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ('merge_enabled', 'merge_disabled')
REVIEWS = tuple(range(48, 337, 48))
CHANGES = (108, 228)


def phase(index):
    return 'A1' if index <= 108 else 'B' if index <= 228 else 'A2'


def stream(seed):
    permutation = [0, 1, 2]
    random.Random(seed).shuffle(permutation)
    support = [(x, a) for x in CONTEXTS if x not in ((0, 0, 0), (1, 1, 1)) for a in (0, 1)]
    tr, vr = random.Random(10000 + seed), random.Random(11000 + seed)
    training, selection = [], []
    for _ in range(28):
        rows = support.copy()
        tr.shuffle(rows)
        for x, a in rows:
            index = len(training) + 1
            training.append({'x': [x[j] for j in permutation], 'a': a,
                             'y': a if phase(index) == 'B' else x[0] ^ a})
    for boundary in REVIEWS:
        rows = support.copy()
        vr.shuffle(rows)
        selection.append([{'x': [x[j] for j in permutation], 'a': a,
                           'y': a if phase(boundary) == 'B' else x[0] ^ a} for x, a in rows])
    return permutation, training, selection


def prediction_pass(m):
    return m['accuracy'] == 1 and m['loss'] < .25


def invariant_pass(m):
    return prediction_pass(m) and m['context_effect'] <= 1e-12 and m['action_effect'] >= .5


def delay(index, change):
    if index is None:
        return None
    return {'review': index, 'main_since_change': index - change,
            'selection_since_change': 12 * sum(change < t <= index for t in REVIEWS)}


def summarise(events, checkpoints, variant):
    by_index = {c['index']: c['metrics'] for c in checkpoints}
    reviews = [e for e in events if e['kind'] == 'review']
    main = [e for e in events if e['kind'] == 'train']
    merges = [e['index'] for e in reviews if e['decision']['merge']]
    splits = [e['index'] for e in reviews if e['decision']['accepted'] and
              len(e['after']['model']['counts']) > len(e['before']['model']['counts'])]
    first_merge = next((t for t in merges if phase(t) == 'B'), None)
    first_one = next((t for t in REVIEWS if phase(t) == 'B' and by_index[t]['forms'] == 1), None)
    first_collapse = next((t for t in REVIEWS if phase(t) == 'B' and
                           by_index[t]['forms'] == by_index[t]['leaves'] == 1 and
                           invariant_pass(by_index[t])), None)
    first_split = next((t for t in splits if t > 228), None)
    recovered = next((t for t in REVIEWS if t > 228 and acquisition_pass(by_index[t])), None)
    checks = {'acquisition': acquisition_pass(by_index[96]),
              'no_initial_merge': not any(t <= 108 for t in merges),
              'B_prediction_and_invariance': invariant_pass(by_index[192]),
              'final_acquisition': acquisition_pass(by_index[336])}
    if variant == 'merge_enabled':
        checks.update(
            actual_collapse=first_merge is not None and by_index[192]['forms'] == by_index[192]['leaves'] == 1,
            B_stability=first_one is not None and all(by_index[t]['forms'] == 1 for t in REVIEWS if first_one <= t <= 228),
            actual_reopening=first_merge is not None and first_split is not None and first_split > first_merge,
            recovery_stability=recovered is not None and all(acquisition_pass(by_index[t]) for t in REVIEWS if t >= recovered))
    else:
        checks.update(no_merge=not merges,
                      B_retains_two=by_index[192]['forms'] == by_index[192]['leaves'] == 2)
    phase_losses = {name: statistics.mean(loss(e['p'], e['row']['y']) for e in main if phase(e['index']) == name)
                    for name in ('A1', 'B', 'A2')}
    transition_losses = {str(c): statistics.mean(loss(e['p'], e['row']['y']) for e in main if c < e['index'] <= c + 48)
                         for c in CHANGES}
    return {'checks': checks, 'own_pass': all(checks.values()),
            'merges': merges, 'splits': splits,
            'first_merge': delay(first_merge, 108), 'successful_collapse': delay(first_collapse, 108),
            'first_return_split': delay(first_split, 228), 'successful_recovery': delay(recovered, 228),
            'phase_main_loss': phase_losses, 'transition_48_main_loss': transition_losses,
            'review_metrics': [{'index': t, 'phase': phase(t), **by_index[t]} for t in REVIEWS]}


def run(seed, variant):
    perm, training, selection = stream(seed)
    learner = Learner(variant == 'merge_enabled')
    events, checkpoints = [], []
    for index, row in enumerate(training, 1):
        event = {'kind': 'train', 'index': index, 'row': row, 'before': learner.state(),
                 'p': learner.predict(row['x'], row['a'])}
        learner.update(**row)
        event['after'] = learner.state()
        events.append(event)
        if index in REVIEWS:
            event = {'kind': 'review', 'index': index, 'before': learner.state()}
            candidate, prepared = learner.prepare()
            event.update(prepared)
            event['selection'] = selection[index // 48 - 1]
            event['decision'] = learner.select(candidate, event['selection'])
            event['after'] = learner.state()
            events.append(event)
            checkpoints.append({'index': index, **evaluate(learner, perm.index(0), phase(index) == 'B')})
    return {'seed': seed, 'variant': variant, 'permutation': perm,
            'events': events, 'checkpoints': checkpoints,
            'metrics': summarise(events, checkpoints, variant),
            'final_buffer': learner.buffer, 'costs': learner.costs}


def compare(runs):
    pairs = []
    for seed in range(5):
        by = {r['variant']: r for r in runs if r['seed'] == seed}
        preservation = {}
        for index in (192, 336):
            losses = {v: next(c['metrics']['loss'] for c in r['checkpoints'] if c['index'] == index)
                      for v, r in by.items()}
            preservation[str(index)] = {'enabled_loss': losses['merge_enabled'],
                                        'disabled_loss': losses['merge_disabled'],
                                        'passed': losses['merge_enabled'] <= losses['merge_disabled'] + .01}
        pairs.append({'seed': seed, 'loss_preservation': preservation,
                      'all_conditions_pass': all(p['passed'] for p in preservation.values()) and
                      all(r['metrics']['own_pass'] for r in by.values())})
    return {'per_seed': pairs, 'passed_seeds': sum(p['all_conditions_pass'] for p in pairs),
            'overall_pass': all(p['all_conditions_pass'] for p in pairs)}


def hashes():
    paths = ('experiments/reversibility_protocol.md', 'experiments/reversibility.py',
             'experiments/collapse.py', 'experiments/forms.py', 'checks/test_reversibility.py',
             'checks/audit_reversibility.py', 'checks/audit_collapse.py')
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}


def report(runs, comparison):
    lines = ['# Experiment 009 results', '',
             f"Declared criterion: **{comparison['overall_pass']}**, {comparison['passed_seeds']}/5 seeds.", '',
             'Changes follow main observations 108 and 228. Checkpoints are frozen evaluations.', '',
             '| Learner | Seed | Review | Phase | Forms | Leaves | Accuracy | Log loss |',
             '| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |']
    for r in runs:
        for m in r['metrics']['review_metrics']:
            lines.append(f"| {r['variant']} | {r['seed']} | {m['index']} | {m['phase']} | {m['forms']} | "
                         f"{m['leaves']} | {m['accuracy']:.0%} | {m['loss']:.6f} |")
    lines += ['', '## Successful collapse and recovery', '',
              'Delays are main / selection observations since the relevant change; observed at reviews only.', '',
              '| Learner | Seed | Collapse delay | Recovery delay |', '| --- | ---: | --- | --- |']
    for r in runs:
        def display(d):
            return '—' if d is None else f"{d['main_since_change']} / {d['selection_since_change']}"
        lines.append(f"| {r['variant']} | {r['seed']} | {display(r['metrics']['successful_collapse'])} | "
                     f"{display(r['metrics']['successful_recovery'])} |")
    lines += ['', '## Pre-feedback main losses', '',
              '| Learner | Seed | A1 | B | A2 | First 48 after 108 | First 48 after 228 |',
              '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in runs:
        m = r['metrics']
        values = list(m['phase_main_loss'].values()) + list(m['transition_48_main_loss'].values())
        lines.append(f"| {r['variant']} | {r['seed']} | " + ' | '.join(f'{v:.6f}' for v in values) + ' |')
    lines += ['', '## Accepted structural changes', '',
              '| Learner | Seed | Review | Forms before → after | Prediction gain | Complexity gain |',
              '| --- | ---: | ---: | --- | ---: | ---: |']
    for r in runs:
        for e in r['events']:
            if e['kind'] == 'review' and e['decision']['accepted']:
                before, after = len(e['before']['model']['counts']), len(e['after']['model']['counts'])
                if before != after:
                    d = e['decision']
                    lines.append(f"| {r['variant']} | {r['seed']} | {e['index']} | {before} → {after} | "
                                 f"{d['prediction_gain']:.6f} | {d['complexity_gain']:.6f} |")
    lines += ['', '## Computation', '', '| Learner | Candidate fits | Candidate fit rows | Count refit rows |',
              '| --- | ---: | ---: | ---: |']
    for variant in VARIANTS:
        selected = [r for r in runs if r['variant'] == variant]
        values = [sum(r['costs'][k] for r in selected) for k in ('candidate_fits', 'candidate_fit_rows', 'count_refit_rows')]
        lines.append(f'| {variant} | ' + ' | '.join(map(str, values)) + ' |')
    lines += ['', '4,480 outcome-bearing presentations and 840 unlabelled checkpoint predictions.',
              'See metrics.json for all criteria, delays, and costs; results.json for complete traces.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/reversibility-v1')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    (args.output / 'manifest.json').write_text(json.dumps(provenance, indent=2) + '\n')
    runs = [run(seed, variant) for seed in range(5) for variant in VARIANTS]
    comparison = compare(runs)
    assert provenance == hashes()
    payload = {'hashes': provenance, 'runs': runs, 'comparison': comparison,
               'outcome_presentations': 4480, 'unlabelled_predictions': 840}
    (args.output / 'results.json').write_text(json.dumps(payload, separators=(',', ':')) + '\n')
    (args.output / 'metrics.json').write_text(json.dumps({
        'runs': [{k: r[k] for k in ('seed', 'variant', 'permutation', 'metrics', 'costs')} for r in runs],
        'comparison': comparison}, indent=2) + '\n')
    (args.output / 'report.md').write_text(report(runs, comparison))
    print(f'Saved 10 runs, 4,480 outcome-bearing presentations to {args.output}')
    print(json.dumps(comparison))


if __name__ == '__main__':
    main()
