"""Experiment 010: bounded stochastic discovery of joint feature relationships."""
import argparse
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics

ROOT = Path(__file__).resolve().parents[1]
N = 6
STEPS = 1152
WINDOW = 192
PERIOD = 64
SELECT = 32
ENDPOINTS = (384, 768, 1152)
XS = list(itertools.product((0, 1), repeat=N))
POOL = [()] + [(i,) for i in range(N)] + list(itertools.combinations(range(N), 2))
ORACLE = -.1 * math.log(.1) - .9 * math.log(.9)
HASHED = (
    'experiments/next_round_plan.md', 'experiments/bundles_protocol.md',
    'experiments/bundles.py', 'checks/test_bundles.py', 'checks/audit_bundles.py',
)


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in HASHED}


def single_world(branch, index):
    return branch == 'reversible' and 384 < index <= 768


def generate(seed, branch):
    permutation = list(range(N))
    random.Random(20000 + seed).shuffle(permutation)

    def row(rng, index):
        raw = [rng.randrange(2) for _ in range(N)]
        action = rng.randrange(2)
        noise = int(rng.random() < .1)
        target = raw[0] ^ action
        if not single_world(branch, index):
            target ^= raw[1]
        return {'x': [raw[j] for j in permutation], 'a': action, 'y': target ^ noise}

    train_rng, select_rng = random.Random(30000 + seed), random.Random(40000 + seed)
    return {
        'seed': seed, 'branch': branch, 'permutation': permutation,
        'main': [row(train_rng, i) for i in range(1, STEPS + 1)],
        'selection': [[row(select_rng, i) for _ in range(SELECT)]
                      for i in range(PERIOD, STEPS + 1, PERIOD)],
    }


def nll(p, y):
    return -math.log(p if y else 1 - p)


def expected_loss(p, q):
    return q * nll(p, 1) + (1 - q) * nll(p, 0)


def cells(subset):
    return 2 ** (len(subset) + 1)


def penalty(subset):
    return .01 * cells(subset)


class Model:
    def __init__(self, subset=(), rows=()):
        self.subset = tuple(subset)
        self.counts = [[0, 0] for _ in range(cells(subset))]
        for row in rows:
            index = self.index(row['x'], row['a'])
            self.counts[index][0] += row['y']
            self.counts[index][1] += 1

    def index(self, x, action):
        index = 0
        for feature in self.subset:
            index = 2 * index + x[feature]
        return 2 * index + action

    def predict(self, x, action):
        ones, total = self.counts[self.index(x, action)]
        return (ones + 1) / (total + 2)

    def mean_loss(self, rows):
        return statistics.mean(nll(self.predict(r['x'], r['a']), r['y']) for r in rows)

    def state(self):
        return {'subset': list(self.subset), 'counts': copy.deepcopy(self.counts)}


class Learner:
    def __init__(self, variant, proposal_seed=None):
        self.variant = variant
        self.model = Model(range(N) if variant == 'full_context' else ())
        self.buffer = []
        self.rng = random.Random(50000 + (proposal_seed or 0))
        self.cursor = 0
        self.costs = dict.fromkeys((
            'main_prediction_feature_reads', 'count_refits', 'count_refit_rows',
            'refit_feature_reads', 'candidate_fits', 'candidate_fit_rows',
            'candidate_fit_feature_reads', 'candidate_score_feature_reads',
            'selection_outcomes', 'selection_prediction_feature_reads',
        ), 0)

    def predict(self, x, action):
        self.costs['main_prediction_feature_reads'] += len(self.model.subset)
        return self.model.predict(x, action)

    def update(self, row):
        self.buffer = (self.buffer + [row])[-WINDOW:]
        self.model = Model(self.model.subset, self.buffer)
        self.costs['count_refits'] += 1
        self.costs['count_refit_rows'] += len(self.buffer)
        self.costs['refit_feature_reads'] += len(self.buffer) * len(self.model.subset)

    def prepare(self):
        pool = POOL[:N + 1] if self.variant == 'singleton' else POOL
        if self.variant == 'deterministic':
            candidates = []
            while len(candidates) < 4:
                subset = pool[self.cursor % len(pool)]
                self.cursor += 1
                if subset != self.model.subset:
                    candidates.append(subset)
        else:
            candidates = self.rng.sample([s for s in pool if s != self.model.subset], 4)
        fitted = [Model(s, self.buffer) for s in candidates]
        summaries = [{'subset': list(m.subset), 'training_loss': m.mean_loss(self.buffer),
                      'penalty': penalty(m.subset)} for m in fitted]
        for s in summaries:
            s['objective'] = s['training_loss'] + s['penalty']
        winner = min(range(4), key=lambda i: (summaries[i]['objective'], fitted[i].subset))
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4 * len(self.buffer)
        reads = len(self.buffer) * sum(len(s) for s in candidates)
        self.costs['candidate_fit_feature_reads'] += reads
        self.costs['candidate_score_feature_reads'] += reads
        return fitted[winner], {'candidates': summaries, 'winner': winner, 'cursor': self.cursor}

    def select(self, candidate, rows):
        current_loss, new_loss = self.model.mean_loss(rows), candidate.mean_loss(rows)
        prediction_gain = current_loss - new_loss
        complexity_gain = penalty(self.model.subset) - penalty(candidate.subset)
        accepted = prediction_gain + complexity_gain > .005
        self.costs['selection_outcomes'] += len(rows)
        self.costs['selection_prediction_feature_reads'] += (
            len(rows) * (len(self.model.subset) + len(candidate.subset)))
        if accepted:
            self.model = candidate
        return {'incumbent_loss': current_loss, 'candidate_loss': new_loss,
                'prediction_gain': prediction_gain, 'complexity_gain': complexity_gain,
                'gain': prediction_gain + complexity_gain, 'accepted': accepted}


def evaluate(learner, world, index):
    snapshot = copy.deepcopy((learner.model.state(), learner.buffer, learner.costs,
                              learner.cursor, learner.rng.getstate()))
    relevant = [world['permutation'].index(0)]
    if not single_world(world['branch'], index):
        relevant.append(world['permutation'].index(1))
    relevant.sort()
    predictions, targets, cuts = [], [], {str(d): [] for d in learner.model.subset}
    for x in XS:
        for action in (0, 1):
            target = action
            for d in relevant:
                target ^= x[d]
            q = .9 if target else .1
            p = learner.model.predict(x, action)
            predictions.append(p)
            targets.append(q)
            for d in learner.model.subset:
                alternate = list(x)
                alternate[d] = 1 - alternate[d]
                cut = .5 * (p + learner.model.predict(alternate, action))
                cuts[str(d)].append(expected_loss(cut, q))
    loss = statistics.mean(expected_loss(p, q) for p, q in zip(predictions, targets))
    correct = sum((p > .5) == (q > .5) for p, q in zip(predictions, targets)) / 128
    lookup = {(x, a): predictions[2 * i + a] for i, x in enumerate(XS) for a in (0, 1)}
    nuisance = 0.
    for x in XS:
        for d in set(range(N)) - set(relevant):
            other = tuple(1 - b if j == d else b for j, b in enumerate(x))
            for a in (0, 1):
                nuisance = max(nuisance, abs(lookup[x, a] - lookup[other, a]))
    result = {
        'index': index, 'subset': list(learner.model.subset), 'relevant': relevant,
        'predictions': predictions, 'expected_loss': loss, 'regret': loss - ORACLE,
        'accuracy': correct, 'exact_structure': list(learner.model.subset) == relevant,
        'cut_loss_increase': {d: statistics.mean(ls) - loss for d, ls in cuts.items()},
        'nuisance_effect': nuisance, 'base_predictions': 128,
        'additional_ablation_predictions': 128 * len(learner.model.subset),
    }
    assert snapshot == (learner.model.state(), learner.buffer, learner.costs,
                        learner.cursor, learner.rng.getstate())
    return result


def run(world, variant, proposal_seed=None):
    learner = Learner(variant, proposal_seed)
    predictions, reviews, evaluations = [], [], []
    for index, row in enumerate(world['main'], 1):
        predictions.append(learner.predict(row['x'], row['a']))
        learner.update(row)
        if index % PERIOD == 0:
            review = {'index': index, 'before': learner.model.state()}
            if variant != 'full_context':
                candidate, details = learner.prepare()
                review.update(details)
                review['decision'] = learner.select(candidate, world['selection'][index // PERIOD - 1])
            review['after'] = learner.model.state()
            reviews.append(review)
            evaluations.append(evaluate(learner, world, index))
    losses = [nll(p, r['y']) for p, r in zip(predictions, world['main'])]
    endpoint = [e for e in evaluations if e['index'] in ENDPOINTS]
    first = {}
    for start, end in ((0, 384), (384, 768), (768, 1152)):
        first[str(end)] = next((e['index'] for e in evaluations
                               if start < e['index'] <= end and e['exact_structure']
                               and e['accuracy'] == 1 and e['regret'] <= .10), None)
    removals = []
    acquired_pair = False
    for r in reviews:
        if len(r['after']['subset']) == 2:
            acquired_pair = True
        if acquired_pair and len(r['before']['subset']) == 2 and len(r['after']['subset']) < 2:
            removals.append(r['index'])
    return {
        'world': f"{world['seed']}-{world['branch']}", 'seed': world['seed'],
        'branch': world['branch'], 'variant': variant, 'proposal_seed': proposal_seed,
        'main_predictions': predictions, 'reviews': reviews, 'evaluations': evaluations,
        'costs': learner.costs,
        'metrics': {
            'phase_main_loss': [statistics.mean(losses[i:i + 384]) for i in (0, 384, 768)],
            'transition64_loss': [statistics.mean(losses[i:i + 64]) for i in (384, 768)],
            'main_loss': statistics.mean(losses), 'first_successful_review': first,
            'pair_removal_reviews': removals,
            'structural_predictive_pass': all(e['exact_structure'] and e['accuracy'] == 1
                                              and e['regret'] <= .10 for e in endpoint),
        },
    }


def compare(runs):
    records = []
    for run_data in runs:
        if run_data['variant'] != 'stochastic':
            continue
        singles = [r for r in runs if r['world'] == run_data['world'] and r['variant'] == 'singleton']
        margins, ablations = [], []
        for time in (384, 1152):
            ev = next(e for e in run_data['evaluations'] if e['index'] == time)
            baseline = statistics.mean(next(e['expected_loss'] for e in r['evaluations']
                                            if e['index'] == time) for r in singles)
            margins.append(baseline - ev['expected_loss'])
            ablations.append(min((ev['cut_loss_increase'].get(str(d), 0.) for d in ev['relevant'])))
        passed = (run_data['metrics']['structural_predictive_pass'] and
                  min(margins) >= .15 and min(ablations) >= .15)
        records.append({'world': run_data['world'], 'proposal_seed': run_data['proposal_seed'],
                        'structure_prediction': run_data['metrics']['structural_predictive_pass'],
                        'singleton_margins': margins, 'minimum_cut_effects': ablations, 'pass': passed})
    counts = {b: sum(r['pass'] for r in records if r['world'].endswith(b))
              for b in ('reversible', 'persistent')}
    return {'runs': records, 'passes_by_branch': counts,
            'primary_pass': all(n >= 8 for n in counts.values())}


def report(runs, comparison, totals):
    lines = [
        '# Experiment 010: stochastic minimal bundles', '',
        f"Primary criterion: **{'PASS' if comparison['primary_pass'] else 'FAIL'}**.",
        f"Passing stochastic runs: {comparison['passes_by_branch']} (10 per branch).", '',
        'Five environment seeds crossed with two proposal seeds; controls are not duplicated.',
        'Expected loss uses the known noisy world distribution only inside frozen evaluation.',
        'These are future-distribution predictions, not withheld-context or task-family transfer.', '',
        '## Endpoint performance', '',
        '| Branch | Learner | Runs | Loss at 384 | Loss at 768 | Loss at 1152 | Main loss | Prediction features/read |',
        '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |',
    ]
    for branch in ('reversible', 'persistent'):
        for variant in ('stochastic', 'deterministic', 'singleton', 'full_context'):
            subset = [r for r in runs if r['branch'] == branch and r['variant'] == variant]
            endpoints = [statistics.mean(next(e['expected_loss'] for e in r['evaluations']
                                             if e['index'] == t) for r in subset) for t in ENDPOINTS]
            main = statistics.mean(r['metrics']['main_loss'] for r in subset)
            reads = statistics.mean(r['costs']['main_prediction_feature_reads'] / STEPS for r in subset)
            lines.append(f'| {branch} | {variant} | {len(subset)} | ' +
                         ' | '.join(f'{x:.6f}' for x in endpoints + [main, reads]) + ' |')
    lines += ['', f'Noise oracle expected log loss: {ORACLE:.6f} nats.', '',
              '## All stochastic runs', '',
              '| World | Proposal seed | Correct structure/prediction | Singleton margins A1 / A2 | Cut effects A1 / A2 | Pass |',
              '| --- | ---: | --- | --- | --- | --- |']
    for row in comparison['runs']:
        lines.append(f"| {row['world']} | {row['proposal_seed']} | {row['structure_prediction']} | " +
                     ' / '.join(f'{x:.4f}' for x in row['singleton_margins']) + ' | ' +
                     ' / '.join(f'{x:.4f}' for x in row['minimum_cut_effects']) + f" | {row['pass']} |")
    lines += ['', '## Endpoint subsets and discovery', '',
              '| World | Learner | Proposal seed | Subsets at 384 / 768 / 1152 | First successful reviews in each phase |',
              '| --- | --- | --- | --- | --- |']
    for r in runs:
        subsets = [e['subset'] for e in r['evaluations'] if e['index'] in ENDPOINTS]
        lines.append(f"| {r['world']} | {r['variant']} | {r['proposal_seed']} | {subsets} | "
                     f"{list(r['metrics']['first_successful_review'].values())} |")
    lines += ['', '## Resource accounting', '', '```json', json.dumps(totals, indent=2), '```', '',
              'Full traces include every proposal, decision, accepted subset, prediction, and ablation.',
              'Selection data never fit models. Raw feature buffers remain accessible to search.',
              'No learned folds, meta-learning, autonomous actions, or fast/slow advantage are established.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'results/bundles-v1')
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    (args.output / 'manifest.json').write_text(json.dumps(provenance, indent=2) + '\n')
    worlds = [generate(seed, branch) for seed in range(5) for branch in ('reversible', 'persistent')]
    runs = []
    for world in worlds:
        for variant in ('stochastic', 'singleton'):
            runs.extend(run(world, variant, seed) for seed in (0, 1))
        runs.extend(run(world, variant) for variant in ('deterministic', 'full_context'))
    comparison = compare(runs)
    totals = {
        'runs': len(runs), 'generated_world_records': len(worlds) * (STEPS + 18 * SELECT),
        'allocated_outcome_presentations': len(runs) * (STEPS + 18 * SELECT),
        'used_outcome_presentations': len(runs) * STEPS + sum(r['costs']['selection_outcomes'] for r in runs),
        'base_evaluation_predictions': sum(e['base_predictions'] for r in runs for e in r['evaluations']),
        'additional_ablation_predictions': sum(e['additional_ablation_predictions'] for r in runs for e in r['evaluations']),
        'costs': {k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs']},
    }
    assert hashes() == provenance
    payload = {'hashes': provenance, 'worlds': worlds, 'runs': runs, 'comparison': comparison, 'totals': totals}
    (args.output / 'results.json').write_text(json.dumps(payload, separators=(',', ':')) + '\n')
    (args.output / 'metrics.json').write_text(json.dumps({
        'comparison': comparison, 'totals': totals,
        'runs': [{k: r[k] for k in ('world', 'variant', 'proposal_seed', 'metrics', 'costs')}
                 for r in runs]}, indent=2) + '\n')
    (args.output / 'report.md').write_text(report(runs, comparison, totals))
    print(json.dumps({'primary_pass': comparison['primary_pass'],
                      'passes': comparison['passes_by_branch'], 'totals': totals}, indent=2))


if __name__ == '__main__':
    main()
