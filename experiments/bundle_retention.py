"""Experiment 011: factorial test of stochastic coverage and corroboration."""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import statistics as st

from bundles import Learner as BaseLearner, Model, POOL, generate, evaluate, nll, penalty

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ('iid_single', 'deck_single', 'iid_split', 'deck_split')
ENDPOINTS = (384, 768, 1152)
FILES = ('experiments/bundle_retention_protocol.md', 'experiments/bundle_retention.py',
         'checks/test_bundle_retention.py', 'checks/audit_bundle_retention.py',
         'experiments/bundles.py', 'checks/audit_bundles.py')


def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in FILES}


def old_hashes_unchanged():
    old = json.loads((ROOT / 'results/bundles-v1/manifest.json').read_text())
    return all(hashlib.sha256((ROOT / p).read_bytes()).hexdigest() == h for p, h in old.items())


class Learner(BaseLearner):
    def __init__(self, variant, proposal_seed):
        assert variant in VARIANTS
        super().__init__(variant, proposal_seed)
        self.deck = []
        self.deck_number = 0

    def prepare(self):
        if self.variant.startswith('iid'):
            candidate, details = super().prepare()
        else:
            subsets = []
            while len(subsets) < 4:
                if not self.deck:
                    self.deck = list(POOL)
                    self.rng.shuffle(self.deck)
                    self.deck_number += 1
                subset = self.deck.pop(0)
                if subset != self.model.subset and subset not in subsets:
                    subsets.append(subset)
            models = [Model(s, self.buffer) for s in subsets]
            candidates = [{'subset': list(m.subset), 'training_loss': m.mean_loss(self.buffer),
                           'penalty': penalty(m.subset)} for m in models]
            for c in candidates:
                c['objective'] = c['training_loss'] + c['penalty']
            winner = min(range(4), key=lambda i: (candidates[i]['objective'], models[i].subset))
            candidate = models[winner]
            details = {'candidates': candidates, 'winner': winner, 'cursor': self.cursor}
            self.costs['candidate_fits'] += 4
            self.costs['candidate_fit_rows'] += 4 * len(self.buffer)
            reads = sum(len(s) for s in subsets) * len(self.buffer)
            self.costs['candidate_fit_feature_reads'] += reads
            self.costs['candidate_score_feature_reads'] += reads
        details.update(deck=[list(s) for s in self.deck], deck_number=self.deck_number)
        return candidate, details

    def select(self, candidate, rows):
        assert len(rows) == 32
        old_losses = [nll(self.model.predict(r['x'], r['a']), r['y']) for r in rows]
        new_losses = [nll(candidate.predict(r['x'], r['a']), r['y']) for r in rows]
        predictive = [a - b for a, b in zip(old_losses, new_losses)]
        complexity = penalty(self.model.subset) - penalty(candidate.subset)
        gain = st.mean(predictive) + complexity
        halves = [st.mean(predictive[i:i+16]) + complexity for i in (0, 16)]
        pooled = gain > .005
        corroborated = all(g > .005 for g in halves)
        accepted = corroborated if self.variant.endswith('split') else pooled
        self.costs['selection_outcomes'] += 32
        self.costs['selection_prediction_feature_reads'] += 32 * (len(self.model.subset) + len(candidate.subset))
        if accepted:
            self.model = candidate
        return {'incumbent_loss': st.mean(old_losses), 'candidate_loss': st.mean(new_losses),
                'prediction_gain': st.mean(predictive), 'complexity_gain': complexity,
                'gain': gain, 'half_gains': halves, 'pooled_accept': pooled,
                'corroborated_accept': corroborated, 'accepted': accepted,
                'veto': self.variant.endswith('split') and pooled and not corroborated}


def metrics(run_data, world):
    evs, reviews = run_data['evaluations'], run_data['reviews']
    losses = [nll(p, r['y']) for p, r in zip(run_data['main_predictions'], world['main'])]
    endpoints = [e for e in evs if e['index'] in ENDPOINTS]
    basic = all(e['exact_structure'] and e['accuracy'] == 1 and e['regret'] <= .10 for e in endpoints)
    cuts = all(min(e['cut_loss_increase'].get(str(d), 0.) for d in e['relevant']) >= .15
               for e in endpoints if e['index'] != 768)
    first = {str(t): next((e['index'] for e in evs if t-384 < e['index'] <= t
                          and e['exact_structure'] and e['accuracy'] == 1 and e['regret'] <= .10), None)
             for t in ENDPOINTS}
    pair = sorted([world['permutation'].index(0), world['permutation'].index(1)])
    acquired = next((e['index'] for e in evs if e['subset'] == pair
                     and e['accuracy'] == 1 and e['regret'] <= .10), None)
    departures = [r['index'] for r in reviews if acquired is not None and r['index'] > acquired
                  and r['before']['subset'] == pair and r['after']['subset'] != pair]
    preserved = acquired is not None and not departures
    coverage = {}
    for t in (384, 1152):
        seen = set()
        for r in reviews:
            if t-384 < r['index'] <= t:
                seen.add(tuple(r['before']['subset']))
                seen.update(tuple(c['subset']) for c in r['candidates'])
        coverage[str(t)] = {'relevant_seen': tuple(pair) in seen, 'visited': len(seen),
                            'fraction': len(seen) / len(POOL)}
    return {
        'phase_main_loss': [st.mean(losses[i:i+384]) for i in (0, 384, 768)],
        'transition64_loss': [st.mean(losses[i:i+64]) for i in (384, 768)],
        'main_loss': st.mean(losses), 'first_successful_review': first,
        'first_successful_pair': acquired, 'correct_pair_departures': departures,
        'persistent_preservation': preserved if world['branch'] == 'persistent' else None,
        'endpoint_pass': basic and cuts, 'coverage': coverage,
        'accepted_changes': sum(r['decision']['accepted'] for r in reviews),
        'vetoes': sum(r['decision']['veto'] for r in reviews),
        'pass': basic and cuts and (world['branch'] != 'persistent' or preserved),
    }


def run(world, variant, proposal_seed):
    learner = Learner(variant, proposal_seed)
    result = {'world': f"{world['seed']}-{world['branch']}", 'seed': world['seed'],
              'branch': world['branch'], 'variant': variant, 'proposal_seed': proposal_seed,
              'main_predictions': [], 'reviews': [], 'evaluations': []}
    for index, row in enumerate(world['main'], 1):
        result['main_predictions'].append(learner.predict(row['x'], row['a']))
        learner.update(row)
        if index % 64 == 0:
            review = {'index': index, 'before': learner.model.state()}
            candidate, details = learner.prepare()
            review.update(details)
            review['decision'] = learner.select(candidate, world['selection'][index//64 - 1])
            review['after'] = learner.model.state()
            result['reviews'].append(review)
            deck_state = copy.deepcopy((learner.deck, learner.deck_number))
            result['evaluations'].append(evaluate(learner, world, index))
            assert deck_state == (learner.deck, learner.deck_number)
    result['costs'] = learner.costs
    result['metrics'] = metrics(result, world)
    return result


def compare(runs):
    groups = []
    for branch in ('reversible', 'persistent'):
        for variant in VARIANTS:
            rs = [r for r in runs if r['branch'] == branch and r['variant'] == variant]
            groups.append({
                'branch': branch, 'variant': variant, 'runs': len(rs),
                'passes': sum(r['metrics']['pass'] for r in rs),
                'endpoint_passes': sum(r['metrics']['endpoint_pass'] for r in rs),
                'persistent_preserved': sum(bool(r['metrics']['persistent_preservation']) for r in rs)
                if branch == 'persistent' else None,
                'departures': sum(len(r['metrics']['correct_pair_departures']) for r in rs)
                if branch == 'persistent' else None,
                'pair_phase_coverage': [sum(r['metrics']['coverage'][str(t)]['relevant_seen'] for r in rs)
                                        for t in (384, 1152)],
                'mean_visited_fraction': [st.mean(r['metrics']['coverage'][str(t)]['fraction'] for r in rs)
                                          for t in (384, 1152)],
                'endpoint_loss': [st.mean(next(e['expected_loss'] for e in r['evaluations']
                                              if e['index'] == t) for r in rs) for t in ENDPOINTS],
                'main_loss': st.mean(r['metrics']['main_loss'] for r in rs),
                'phase_main_loss': [st.mean(r['metrics']['phase_main_loss'][i] for r in rs) for i in range(3)],
                'transition64_loss': [st.mean(r['metrics']['transition64_loss'][i] for r in rs) for i in range(2)],
                'vetoes': sum(r['metrics']['vetoes'] for r in rs),
            })
    paired = []
    for branch in ('reversible', 'persistent'):
        for first, second in (('iid_single', 'deck_single'), ('iid_split', 'deck_split'),
                              ('iid_single', 'iid_split'), ('deck_single', 'deck_split')):
            pairs = []
            for seed in range(100, 105):
                for ps in (100, 101):
                    a = next(r for r in runs if (r['seed'], r['proposal_seed'], r['branch'], r['variant'])
                             == (seed, ps, branch, first))
                    b = next(r for r in runs if (r['seed'], r['proposal_seed'], r['branch'], r['variant'])
                             == (seed, ps, branch, second))
                    pairs.append({'seed': seed, 'proposal_seed': ps,
                                  'main_loss_delta': b['metrics']['main_loss'] - a['metrics']['main_loss'],
                                  'pass_delta': int(b['metrics']['pass']) - int(a['metrics']['pass'])})
            paired.append({'branch': branch, 'from': first, 'to': second, 'pairs': pairs})
    return {'groups': groups, 'paired': paired,
            'primary_pass': all(g['passes'] >= 8 for g in groups if g['variant'] == 'deck_split')}


def report(runs, summary, totals):
    lines = ['# Experiment 011: coverage and corroboration', '',
             f"Primary criterion: **{'PASS' if summary['primary_pass'] else 'FAIL'}**.", '',
             'All figures use fresh environment seeds 100–104 and proposal seeds 100,101.',
             'Persistent passes require preservation after acquisition, not just endpoint recovery.', '',
             '| Branch | Variant | Pass / 10 | Endpoint / 10 | Departures | Pair coverage A1 / A2 | Main loss |',
             '| --- | --- | ---: | ---: | ---: | --- | ---: |']
    for g in summary['groups']:
        lines.append(f"| {g['branch']} | {g['variant']} | {g['passes']} | {g['endpoint_passes']} | "
                     f"{g['departures']} | {g['pair_phase_coverage']} | {g['main_loss']:.6f} |")
    lines += ['', '## Prediction and adaptation', '',
              '| Branch | Variant | Endpoint losses | Phase main losses | First 64 after each change | Gate vetoes |',
              '| --- | --- | --- | --- | --- | ---: |']
    for g in summary['groups']:
        fields = [' / '.join(f'{v:.6f}' for v in g[k])
                  for k in ('endpoint_loss', 'phase_main_loss', 'transition64_loss')]
        lines.append(f"| {g['branch']} | {g['variant']} | " + ' | '.join(fields) + f" | {g['vetoes']} |")
    lines += ['', '## Per-run outcomes', '',
              '| World | Variant | Proposal seed | Endpoint subsets | First successful reviews | Departures | Pass |',
              '| --- | --- | ---: | --- | --- | --- | --- |']
    for r in runs:
        subsets = [e['subset'] for e in r['evaluations'] if e['index'] in ENDPOINTS]
        m = r['metrics']
        lines.append(f"| {r['world']} | {r['variant']} | {r['proposal_seed']} | {subsets} | "
                     f"{list(m['first_successful_review'].values())} | {m['correct_pair_departures']} | {m['pass']} |")
    lines += ['', '## Resource accounting', '', '```json', json.dumps(totals, indent=2), '```', '',
              'Complete traces and paired differences are in results.json and metrics.json.',
              'No learning of the proposal rule or gate; no learned interface or meta-learning.', '']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/bundle-retention-v1')
    args = parser.parse_args()
    assert old_hashes_unchanged()
    args.output.mkdir(parents=True, exist_ok=False)
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    worlds = [generate(s, b) for s in range(100, 105) for b in ('reversible', 'persistent')]
    runs = [run(w, v, ps) for w in worlds for ps in (100, 101) for v in VARIANTS]
    summary = compare(runs)
    totals = {'runs': len(runs), 'generated_world_records': 17280,
              'outcome_presentations': len(runs)*1728, 'base_evaluation_predictions': len(runs)*18*128,
              'additional_ablation_predictions': sum(e['additional_ablation_predictions'] for r in runs for e in r['evaluations']),
              'costs': {k: sum(r['costs'][k] for r in runs) for k in runs[0]['costs']}}
    assert hashes() == provenance and old_hashes_unchanged()
    payload = {'hashes': provenance, 'worlds': worlds, 'runs': runs, 'comparison': summary, 'totals': totals}
    (args.output/'results.json').write_text(json.dumps(payload, separators=(',', ':'))+'\n')
    (args.output/'metrics.json').write_text(json.dumps({
        'comparison': summary, 'totals': totals,
        'runs': [{k:r[k] for k in ('world','variant','proposal_seed','metrics','costs')} for r in runs]}, indent=2)+'\n')
    (args.output/'report.md').write_text(report(runs, summary, totals))
    print(json.dumps({'primary_pass': summary['primary_pass'], 'groups': summary['groups'],
                      'totals': totals}, indent=2))


if __name__ == '__main__':
    main()
