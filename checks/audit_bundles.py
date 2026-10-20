"""Reconstruct Experiment 010 without importing any learner or experiment code."""
from collections import defaultdict
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics as st

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'results/bundles-v1'
CONTEXTS = list(itertools.product(range(2), repeat=6))
SUBSETS = [()] + list(itertools.combinations(range(6), 1)) + list(itertools.combinations(range(6), 2))
TIMES = (384, 768, 1152)
H = -sum(p * math.log(p) for p in (.1, .9))


def close(a, b):
    if isinstance(b, dict):
        assert a.keys() == b.keys(), (a.keys(), b.keys())
        for k in b:
            close(a[k], b[k])
    elif isinstance(b, (list, tuple)):
        assert len(a) == len(b)
        for x, y in zip(a, b):
            close(x, y)
    elif isinstance(b, float):
        assert math.isclose(a, b, rel_tol=1e-10, abs_tol=1e-12), (a, b)
    else:
        assert a == b, (a, b)


def table(subset, rows):
    counts = defaultdict(lambda: [0, 0])
    for r in rows:
        key = tuple(r['x'][d] for d in subset) + (r['a'],)
        counts[key][0] += r['y']
        counts[key][1] += 1
    return dict(counts)


def predict(subset, counts, x, a):
    ones, total = counts.get(tuple(x[d] for d in subset) + (a,), (0, 0))
    return (ones + 1.) / (total + 2.)


def saved_state(subset, counts):
    return {'subset': list(subset), 'counts': [
        list(counts.get(key, (0, 0))) for key in itertools.product((0, 1), repeat=len(subset) + 1)]}


def nll(p, y):
    return -math.log(p) if y else -math.log1p(-p)


def score(subset, counts, rows):
    return st.mean(nll(predict(subset, counts, r['x'], r['a']), r['y']) for r in rows)


def cost(subset):
    return .01 * 2 ** (len(subset) + 1)


def check_world(world):
    seed, branch = world['seed'], world['branch']
    permutation = list(range(6))
    random.Random(20000 + seed).shuffle(permutation)
    assert permutation == world['permutation']

    def expected(rng, index):
        x = [rng.randrange(2) for _ in range(6)]
        a = rng.randrange(2)
        flip = rng.random() < .10
        y = (x[0] + a + (0 if branch == 'reversible' and 385 <= index <= 768 else x[1])) % 2
        return {'x': [x[d] for d in permutation], 'a': a, 'y': (y + int(flip)) % 2}

    rng = random.Random(30000 + seed)
    assert world['main'] == [expected(rng, i) for i in range(1, 1153)]
    rng = random.Random(40000 + seed)
    assert world['selection'] == [[expected(rng, i) for _ in range(32)] for i in range(64, 1153, 64)]


def check_evaluation(ev, subset, counts, world, index):
    relevant = [world['permutation'].index(0)]
    if not (world['branch'] == 'reversible' and 385 <= index <= 768):
        relevant += [world['permutation'].index(1)]
    relevant.sort()
    base, losses, cut_losses = [], [], {str(d): [] for d in subset}
    correct = 0
    for x in CONTEXTS:
        for a in (0, 1):
            y = (a + sum(x[d] for d in relevant)) % 2
            q = .9 if y else .1
            p = predict(subset, counts, x, a)
            base.append(p)
            losses.append(-q * math.log(p) - (1 - q) * math.log1p(-p))
            correct += (p > .5) == bool(y)
            for d in subset:
                modified = list(x)
                modified[d] = 1 - modified[d]
                v = (p + predict(subset, counts, modified, a)) / 2
                cut_losses[str(d)].append(-q * math.log(v) - (1 - q) * math.log1p(-v))
    nuisance = 0.
    for i, x in enumerate(CONTEXTS):
        for d in range(6):
            if d not in relevant:
                other_index = i ^ (1 << (5 - d))
                nuisance = max(nuisance, *(abs(base[2*i+a] - base[2*other_index+a]) for a in (0, 1)))
    avg = st.mean(losses)
    close(ev, {'index': index, 'subset': list(subset), 'relevant': relevant,
               'predictions': base, 'expected_loss': avg, 'regret': avg - H,
               'accuracy': correct / 128, 'exact_structure': list(subset) == relevant,
               'cut_loss_increase': {d: st.mean(ls) - avg for d, ls in cut_losses.items()},
               'nuisance_effect': nuisance, 'base_predictions': 128,
               'additional_ablation_predictions': len(subset) * 128})


def check_run(run, world):
    subset = tuple(range(6)) if run['variant'] == 'full_context' else ()
    counts, buffer, cursor = {}, [], 0
    rng = random.Random(50000 + (run['proposal_seed'] or 0))
    keys = ('main_prediction_feature_reads', 'count_refits', 'count_refit_rows',
            'refit_feature_reads', 'candidate_fits', 'candidate_fit_rows',
            'candidate_fit_feature_reads', 'candidate_score_feature_reads',
            'selection_outcomes', 'selection_prediction_feature_reads')
    costs = dict.fromkeys(keys, 0)
    assert len(run['main_predictions']) == 1152
    assert len(run['reviews']) == len(run['evaluations']) == 18
    losses = []
    for index, row in enumerate(world['main'], 1):
        p = predict(subset, counts, row['x'], row['a'])
        close(run['main_predictions'][index - 1], p)
        losses.append(nll(p, row['y']))
        costs['main_prediction_feature_reads'] += len(subset)
        buffer.append(row)
        if len(buffer) > 192:
            buffer.pop(0)
        counts = table(subset, buffer)
        costs['count_refits'] += 1
        costs['count_refit_rows'] += len(buffer)
        costs['refit_feature_reads'] += len(buffer) * len(subset)
        if index % 64:
            continue
        review = run['reviews'][index // 64 - 1]
        assert review['index'] == index
        close(review['before'], saved_state(subset, counts))
        if run['variant'] != 'full_context':
            pool = SUBSETS[:7] if run['variant'] == 'singleton' else SUBSETS
            if run['variant'] == 'deterministic':
                proposals = []
                while len(proposals) < 4:
                    proposal = pool[cursor % len(pool)]
                    cursor += 1
                    if proposal != subset:
                        proposals.append(proposal)
            else:
                proposals = rng.sample([s for s in pool if s != subset], 4)
            assert [tuple(c['subset']) for c in review['candidates']] == proposals
            assert review['cursor'] == cursor
            fitted = [table(s, buffer) for s in proposals]
            scores = []
            for s, c, saved in zip(proposals, fitted, review['candidates']):
                loss = score(s, c, buffer)
                close(saved, {'subset': list(s), 'training_loss': loss,
                              'penalty': cost(s), 'objective': loss + cost(s)})
                # The saved values were independently checked above; use their
                # exact float bits to reproduce a possible machine-level tie.
                scores.append(saved['objective'])
            winner = min(range(4), key=lambda j: (scores[j], proposals[j]))
            assert winner == review['winner']
            candidate, cand_counts = proposals[winner], fitted[winner]
            batch = world['selection'][index // 64 - 1]
            old_loss, new_loss = score(subset, counts, batch), score(candidate, cand_counts, batch)
            gain = old_loss - new_loss + cost(subset) - cost(candidate)
            decision = {'incumbent_loss': old_loss, 'candidate_loss': new_loss,
                        'prediction_gain': old_loss - new_loss,
                        'complexity_gain': cost(subset) - cost(candidate),
                        'gain': gain, 'accepted': gain > .005}
            close(review['decision'], decision)
            costs['candidate_fits'] += 4
            costs['candidate_fit_rows'] += 4 * len(buffer)
            reads = len(buffer) * sum(len(s) for s in proposals)
            costs['candidate_fit_feature_reads'] += reads
            costs['candidate_score_feature_reads'] += reads
            costs['selection_outcomes'] += 32
            costs['selection_prediction_feature_reads'] += 32 * (len(subset) + len(candidate))
            if decision['accepted']:
                subset, counts = candidate, cand_counts
        else:
            assert set(review) == {'index', 'before', 'after'}
        close(review['after'], saved_state(subset, counts))
        check_evaluation(run['evaluations'][index // 64 - 1], subset, counts, world, index)
    close(run['costs'], costs)
    evaluations = run['evaluations']
    first = {str(end): next((e['index'] for e in evaluations
                            if end - 384 < e['index'] <= end and e['exact_structure']
                            and e['accuracy'] == 1 and e['regret'] <= .1), None) for end in TIMES}
    removals, pair_seen = [], False
    for r in run['reviews']:
        pair_seen = pair_seen or len(r['after']['subset']) == 2
        if pair_seen and len(r['before']['subset']) == 2 and len(r['after']['subset']) < 2:
            removals.append(r['index'])
    close(run['metrics'], {
        'phase_main_loss': [st.mean(losses[i:i+384]) for i in (0, 384, 768)],
        'transition64_loss': [st.mean(losses[i:i+64]) for i in (384, 768)],
        'main_loss': st.mean(losses), 'first_successful_review': first,
        'pair_removal_reviews': removals,
        'structural_predictive_pass': all(e['exact_structure'] and e['accuracy'] == 1
                                         and e['regret'] <= .1 for e in evaluations if e['index'] in TIMES)})


def main():
    data = json.loads((OUT / 'results.json').read_text())
    manifest = json.loads((OUT / 'manifest.json').read_text())
    assert set(manifest) == {'experiments/next_round_plan.md', 'experiments/bundles_protocol.md',
                            'experiments/bundles.py', 'checks/test_bundles.py', 'checks/audit_bundles.py'}
    assert manifest == data['hashes']
    for path, digest in manifest.items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest, path
    worlds = {f"{w['seed']}-{w['branch']}": w for w in data['worlds']}
    assert len(worlds) == len(data['worlds']) == 10
    assert set(worlds) == {f'{s}-{b}' for s in range(5) for b in ('reversible', 'persistent')}
    for w in worlds.values():
        check_world(w)
    ids = {(r['world'], r['variant'], r['proposal_seed']) for r in data['runs']}
    expected = {(w, v, s) for w in worlds for v, seeds in (
        ('stochastic', (0, 1)), ('singleton', (0, 1)),
        ('deterministic', (None,)), ('full_context', (None,))) for s in seeds}
    assert ids == expected and len(data['runs']) == 60
    records = []
    for r in data['runs']:
        assert r['world'] == f"{r['seed']}-{r['branch']}"
        check_run(r, worlds[r['world']])
        if r['variant'] != 'stochastic':
            continue
        singles = [s for s in data['runs'] if s['world'] == r['world'] and s['variant'] == 'singleton']
        margins, cuts = [], []
        for t in (384, 1152):
            ev = next(e for e in r['evaluations'] if e['index'] == t)
            margins.append(st.mean(next(e['expected_loss'] for e in s['evaluations'] if e['index'] == t)
                                   for s in singles) - ev['expected_loss'])
            cuts.append(min(ev['cut_loss_increase'].get(str(d), 0.) for d in ev['relevant']))
        records.append({'world': r['world'], 'proposal_seed': r['proposal_seed'],
                        'structure_prediction': r['metrics']['structural_predictive_pass'],
                        'singleton_margins': margins, 'minimum_cut_effects': cuts,
                        'pass': r['metrics']['structural_predictive_pass'] and min(margins) >= .15 and min(cuts) >= .15})
    counts = {b: sum(r['pass'] for r in records if r['world'].endswith(b)) for b in ('reversible', 'persistent')}
    close(data['comparison'], {'runs': records, 'passes_by_branch': counts,
                               'primary_pass': all(n >= 8 for n in counts.values())})
    costs = {k: sum(r['costs'][k] for r in data['runs']) for k in data['runs'][0]['costs']}
    close(data['totals'], {
        'runs': 60, 'generated_world_records': 17280, 'allocated_outcome_presentations': 103680,
        'used_outcome_presentations': 97920, 'base_evaluation_predictions': 138240,
        'additional_ablation_predictions': sum(128 * len(e['subset']) for r in data['runs'] for e in r['evaluations']),
        'costs': costs,
    })
    assert costs['candidate_fits'] == 3600 and costs['selection_outcomes'] == 28800
    metrics = json.loads((OUT / 'metrics.json').read_text())
    close(metrics, {'comparison': data['comparison'], 'totals': data['totals'],
                    'runs': [{k: r[k] for k in ('world', 'variant', 'proposal_seed', 'metrics', 'costs')}
                             for r in data['runs']]})
    print('PASS: all 60 traces, streams, proposals, predictions, decisions, evaluations, '
          'metrics, budgets, and source hashes independently verified.')


if __name__ == '__main__':
    main()
