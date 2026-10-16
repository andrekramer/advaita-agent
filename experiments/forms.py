"""Experiment 006: bounded structural acquisition; standard library only."""

import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random

CONTEXTS = tuple(itertools.product((0, 1), repeat=3))
ROOT = (((-1, -1, -1), 0),)
VARIANTS = ('lookup', 'single_structure', 'retained_structure', 'fixed_features')
ROOT_DIR = Path(__file__).resolve().parents[1]


def loss(p, y):
    assert 0 < p < 1
    return -math.log(p if y else 1 - p)


def canonical(leaves):
    labels, result = {}, []
    for cube, group in sorted(leaves):
        labels.setdefault(group, len(labels))
        result.append((tuple(cube), labels[group]))
    return tuple(result)


def group_for(structure, x):
    hits = [k for cube, k in structure
            if all(v == -1 or v == bit for v, bit in zip(cube, x))]
    assert len(hits) == 1
    return hits[0]


def validate(structure):
    assert structure == canonical(structure)
    assert 1 <= len(structure) <= 8
    assert 1 <= len({k for _, k in structure}) <= 4
    for cube, _ in structure:
        assert len(cube) == 3 and all(v in (-1, 0, 1) for v in cube)
    for x in CONTEXTS:
        group_for(structure, x)


def collapse(leaves):
    leaves = sorted(leaves)
    while True:
        pair = None
        for i, (left, kl) in enumerate(leaves):
            for j in range(i + 1, len(leaves)):
                right, kr = leaves[j]
                differing = [d for d in range(3) if left[d] != right[d]]
                if (kl == kr and len(differing) == 1
                        and {left[differing[0]], right[differing[0]]} == {0, 1}):
                    pair = (i, j, differing[0])
                    break
            if pair is not None:
                break
        if pair is None:
            return canonical(leaves)
        i, j, d = pair
        cube = list(leaves[i][0])
        cube[d] = -1
        leaves = sorted([item for n, item in enumerate(leaves) if n not in (i, j)]
                        + [(tuple(cube), leaves[i][1])])


def neighbours(structure):
    pool = {structure}
    groups = sorted({k for _, k in structure})
    fresh = max(groups) + 1
    for index, (cube, _) in enumerate(structure):
        for d, bit in enumerate(cube):
            if bit != -1:
                continue
            children = []
            for value in (0, 1):
                child = list(cube)
                child[d] = value
                children.append((tuple(child), fresh + value))
            candidate = canonical([item for i, item in enumerate(structure)
                                   if i != index] + children)
            if len(candidate) <= 8 and len({k for _, k in candidate}) <= 4:
                pool.add(candidate)
    for first, second in itertools.combinations(groups, 2):
        pool.add(collapse([(cube, first if k == second else k)
                          for cube, k in structure]))
    assert len(pool) <= 31
    for candidate in pool:
        validate(candidate)
    return sorted(pool)


class FormModel:
    def __init__(self, structure=ROOT):
        self.structure = canonical(structure)
        validate(self.structure)
        self.counts = [[[0, 0], [0, 0]]
                       for _ in {k for _, k in self.structure}]

    def predict(self, x, a):
        r, n = self.counts[group_for(self.structure, x)][a]
        return (r + 1) / (n + 2)

    def update(self, x, a, y):
        cell = self.counts[group_for(self.structure, x)][a]
        cell[0] += y
        cell[1] += 1

    @classmethod
    def fit(cls, structure, records):
        model = cls(structure)
        for row in records:
            model.update(row['x'], row['a'], row['y'])
        return model

    def state(self):
        return {'structure': [[list(cube), k] for cube, k in self.structure],
                'counts': copy.deepcopy(self.counts)}

    def objective(self, rows):
        return (sum(loss(self.predict(r['x'], r['a']), r['y']) for r in rows)
                / len(rows) + .01 * len(self.counts) + .005 * len(self.structure))


class Structural:
    def __init__(self, retained):
        self.retained = retained
        self.model = FormModel()
        self.provisional = FormModel() if retained else None
        self.buffer = []
        self.dbar = 0.0

    def predict(self, x, a):
        return self.model.predict(x, a)

    def update(self, x, a, y):
        assert len(self.buffer) < 192
        self.buffer.append({'x': list(x), 'a': a, 'y': y})
        target = self.provisional if self.retained else self.model
        target.update(x, a, y)

    def state(self):
        return {'model': self.model.state(),
                'provisional': self.provisional.state() if self.retained else None,
                'buffer_size': len(self.buffer), 'dbar': self.dbar}

    def prepare(self, probes):
        """No selection data or evaluator information is accepted here."""
        diagnostic = None
        if self.retained:
            gaps = [self.provisional.predict(x, a) - self.model.predict(x, a)
                    for x, a in probes]
            distance = sum(abs(g) for g in gaps) / len(gaps)
            self.dbar = .75 * self.dbar + .25 * distance
            diagnostic = {'gaps': gaps, 'D': distance, 'Dbar': self.dbar}
        candidates = [FormModel.fit(s, self.buffer)
                      for s in neighbours(self.model.structure)]
        scores = [m.objective(self.buffer) for m in candidates]
        best = min(range(len(scores)), key=lambda i: (scores[i], candidates[i].structure))
        return candidates[best], {
            'diagnostic': diagnostic, 'winner': best,
            'candidates': [{'state': m.state(), 'training_objective': score,
                            'advanced': i == best}
                           for i, (m, score) in enumerate(zip(candidates, scores))]}

    def select(self, candidate, rows):
        incumbent = self.model.objective(rows)
        proposed = candidate.objective(rows)
        before = [self.model.predict(r['x'], r['a']) for r in rows]
        after = [candidate.predict(r['x'], r['a']) for r in rows]
        accepted = incumbent - proposed > .001
        if accepted:
            self.model = candidate
        if self.retained:
            self.provisional = FormModel.fit(self.model.structure, self.buffer)
        return {'incumbent_objective': incumbent, 'candidate_objective': proposed,
                'gain': incumbent - proposed, 'accepted': accepted,
                'incumbent_predictions': before, 'candidate_predictions': after,
                'max_prediction_change': max(abs(a - b) for a, b in zip(before, after))
                if accepted else 0.0}


def features(x, a):
    u = [2 * bit - 1 for bit in x]
    b = 2 * a - 1
    return [1, b] + u + [b * bit for bit in u]


class Baseline:
    def __init__(self, variant):
        self.variant = variant
        self.counts = [[[0, 0], [0, 0]] for _ in CONTEXTS]
        self.weights = [0.0] * 8
        self.clips = 0

    def predict(self, x, a):
        if self.variant == 'lookup':
            r, n = self.counts[CONTEXTS.index(tuple(x))][a]
            return (r + 1) / (n + 2)
        z = sum(w * f for w, f in zip(self.weights, features(x, a)))
        # Numerically stable sigmoid; the registered bound still keeps |z| <=64.
        return 1 / (1 + math.exp(-z)) if z >= 0 else math.exp(z) / (1 + math.exp(z))

    def update(self, x, a, y):
        if self.variant == 'lookup':
            cell = self.counts[CONTEXTS.index(tuple(x))][a]
            cell[0] += y
            cell[1] += 1
        else:
            p = self.predict(x, a)
            raw = [w + .1 * (y - p) * f
                   for w, f in zip(self.weights, features(x, a))]
            self.clips += sum(abs(w) > 8 for w in raw)
            self.weights = [max(-8, min(8, w)) for w in raw]

    def state(self):
        if self.variant == 'lookup':
            return {'counts': copy.deepcopy(self.counts)}
        return {'weights': self.weights.copy(), 'clips': self.clips}


def streams(seed):
    permutation = [0, 1, 2]
    random.Random(seed).shuffle(permutation)
    admissible = []
    for raw in CONTEXTS:
        if raw in ((0, 0, 0), (1, 1, 1)):
            continue
        for action in (0, 1):
            admissible.append({'x': [raw[j] for j in permutation],
                               'a': action, 'y': raw[0] ^ action})
    train_rng, selection_rng = random.Random(1000 + seed), random.Random(2000 + seed)
    training, selections = [], []
    for _ in range(16):
        block = copy.deepcopy(admissible)
        train_rng.shuffle(block)
        training.extend(block)
    for _ in range(4):
        block = copy.deepcopy(admissible)
        selection_rng.shuffle(block)
        selections.append(block)
    return permutation, training, selections


def evaluate(learner, relevant):
    before = copy.deepcopy(learner.state())
    table = [{'x': list(x), 'a': a, 'p': learner.predict(x, a)}
             for x in CONTEXTS for a in (0, 1)]
    withheld = [{**r, 'y': r['x'][relevant] ^ r['a']} for r in table
                if tuple(r['x']) in ((0, 0, 0), (1, 1, 1))]
    metrics = {'accuracy': sum((r['p'] > .5) == r['y'] for r in withheld) / 4,
               'loss': sum(loss(r['p'], r['y']) for r in withheld) / 4}
    probs = {(tuple(r['x']), r['a']): r['p'] for r in table}
    effects = [[], [], []]
    for x in CONTEXTS:
        for d in range(3):
            other = list(x)
            other[d] ^= 1
            for a in (0, 1):
                effects[d].append(abs(probs[x, a] - probs[tuple(other), a]))
    metrics['nuisance_effect'] = max(max(effects[d]) for d in range(3) if d != relevant)
    metrics['relevant_effect'] = min(effects[relevant])
    if isinstance(learner, Structural):
        structure = learner.model.structure
        assignments = [group_for(structure, x) for x in CONTEXTS]
        exact = all((assignments[i] == assignments[j]) == (x[relevant] == y[relevant])
                    for i, x in enumerate(CONTEXTS) for j, y in enumerate(CONTEXTS) if i < j)
        metrics.update(forms=len(set(assignments)), leaves=len(structure), partition_exact=exact)
        metrics['acquisition_pass'] = (
            metrics['accuracy'] == 1 and metrics['loss'] < .25
            and metrics['forms'] == 2 and metrics['leaves'] == 2 and exact
            and metrics['nuisance_effect'] <= 1e-12 and metrics['relevant_effect'] >= .5)
    assert learner.state() == before
    return {'table': table, 'withheld': withheld, 'metrics': metrics,
            'state_before': before, 'state_after': learner.state()}


def run(seed, variant):
    permutation, training, selections = streams(seed)
    learner = (Structural(variant == 'retained_structure') if 'structure' in variant
               else Baseline(variant))
    probes = sorted({(tuple(r['x']), r['a']) for r in training})
    events = []
    for index, row in enumerate(training, 1):
        event = {'kind': 'train', 'index': index, 'row': row, 'before': learner.state(),
                 'p': learner.predict(row['x'], row['a'])}
        if isinstance(learner, Structural) and learner.retained:
            event['provisional_p'] = learner.provisional.predict(row['x'], row['a'])
        learner.update(**row)
        event['after'] = learner.state()
        events.append(event)
        if index % 48:
            continue
        batch = selections[index // 48 - 1]
        if isinstance(learner, Structural):
            event = {'kind': 'review', 'index': index, 'before': learner.state()}
            # Freeze the candidate before selection outcomes enter the learner.
            candidate, prepared = learner.prepare(probes)
            event.update(prepared)
            event['selection'] = batch
            event['decision'] = learner.select(candidate, batch)
            event['after'] = learner.state()
            events.append(event)
        else:
            for selection_row in batch:
                event = {'kind': 'selection_update', 'index': index, 'row': selection_row,
                         'before': learner.state(),
                         'p': learner.predict(selection_row['x'], selection_row['a'])}
                learner.update(**selection_row)
                event['after'] = learner.state()
                events.append(event)
    final = evaluate(learner, permutation.index(0))
    final['metrics']['training_loss'] = sum(loss(e['p'], e['row']['y']) for e in events
                                          if e['kind'] == 'train') / 192
    final['metrics']['candidate_count'] = sum(len(e['candidates']) for e in events
                                            if e['kind'] == 'review')
    final['metrics']['accepted_reviews'] = sum(e['decision']['accepted'] for e in events
                                             if e['kind'] == 'review')
    return {'seed': seed, 'variant': variant, 'permutation': permutation,
            'probes': [[list(x), a] for x, a in probes], 'events': events, 'final': final}


def hashes():
    paths = ['experiments/forms_protocol.md', 'experiments/forms.py',
             'checks/test_forms.py', 'checks/audit_forms_results.py']
    return {p: hashlib.sha256((ROOT_DIR / p).read_bytes()).hexdigest() for p in paths}


def report(runs):
    lines = ['# Experiment 006: acquisition results', '',
             'One registered run per seed and learner; no tuning.', '',
             '| Learner | Seed | Withheld accuracy | Withheld loss | Training loss | Forms | Leaves | Acquisition |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |']
    for run_data in runs:
        m = run_data['final']['metrics']
        passed = str(m.get('acquisition_pass', 'not applicable'))
        lines.append(f"| {run_data['variant']} | {run_data['seed']} | {m['accuracy']:.0%} | "
                     f"{m['loss']:.6f} | {m['training_loss']:.6f} | {m.get('forms', '—')} | "
                     f"{m.get('leaves', '—')} | {passed} |")
    lines += ['', '## Learned structures', '',
              'Feature positions were permuted per seed. Rules use encoded feature positions;',
              'names are identifiers within each final model, not supplied semantic labels.', '']
    for r in runs:
        if 'structure' not in r['variant']:
            continue
        state = r['final']['state_before']['model']
        lines += [f"### {r['variant']}, seed {r['seed']}", '',
                  f"Encoding: {r['permutation']}; simulator-relevant position: {r['permutation'].index(0)}.", '']
        for cube, k in state['structure']:
            rule = ' AND '.join(f'x{d}={v}' for d, v in enumerate(cube) if v != -1) or 'all contexts'
            ps = [(success + 1) / (total + 2) for success, total in state['counts'][k]]
            lines.append(f'- {rule} → form-{k + 1}; P(y=1 | a=0,1) = ({ps[0]:.6f}, {ps[1]:.6f}).')
        m = r['final']['metrics']
        lines += ['', f"Candidates scored: {m['candidate_count']}; reviews accepted: {m['accepted_reviews']}.", '']
    lines += ['## Accounting', '',
              '20 runs × (192 main + 48 selection + 4 final outcomes) = 4,880 presentations.',
              '240 additional unlabelled final predictions; 240 paired A/N diagnostic probes.',
              'Structural learners fit counts on 192 main records and use 48 selection outcomes',
              'only for selection. Baselines update on all 240 feedback records.',
              'All traces, candidates, probabilities, counts and decisions are in results.json.',
              'See findings.md for interpretation and audit status.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT_DIR / 'results/forms-v1')
    args = parser.parse_args()
    # Refuse accidental overwriting or a second benchmark run in the same output.
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    runs = [run(seed, variant) for seed in range(5) for variant in VARIANTS]
    assert provenance == hashes()
    payload = {'hashes': provenance, 'runs': runs, 'outcome_presentations': 4880,
               'unlabelled_final_predictions': 240, 'paired_diagnostic_probes': 240}
    (args.output / 'results.json').write_text(json.dumps(payload, separators=(',', ':')) + '\n')
    (args.output / 'metrics.json').write_text(json.dumps(
        [{'seed': r['seed'], 'variant': r['variant'], **r['final']['metrics']} for r in runs], indent=2) + '\n')
    (args.output / 'report.md').write_text(report(runs))
    print(f'Saved {len(runs)} runs; 4,880 outcome-bearing presentations to {args.output}')


if __name__ == '__main__':
    main()
