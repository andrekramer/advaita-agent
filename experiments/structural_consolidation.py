"""018: continuing forms, dependencies, exposure and retained memory."""
import argparse
import copy
import gzip
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import random
import signal
from statistics import mean
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.structural import StructuralLearner
from advaita.state import canonical
from structural_consolidation_metrics import metrics, summarize

BRANCHES = ('forms', 'detail', 'reversed')
VARIANTS = ('integrated', 'delete', 'raw', 'fixed')
CONTEXTS = list(it.product(range(4), range(4), range(2)))
H = -.1*math.log(.1)-.9*math.log(.9)


def forms_at(w, t, observed=False):
    f = copy.deepcopy(w['forms'])
    if w['branch'] == 'forms' and 240 < t <= 528:
        f[w['affected']] = [0, 0, 0, 0]
    return f


def target(w, x, a, t):
    f = forms_at(w, t)
    y = f[0][x[0]] ^ f[1][x[1]] ^ a
    if w['branch'] != 'forms' and (0 < t <= 240 or t > 528):
        j = w['affected']
        y ^= int(x[j] != w['representatives'][j][f[j][x[j]]])
        if w['branch'] == 'reversed' and t > 528:
            y ^= 1
    return y


def generate(seed, branch, sizes=(256, 4, 256, 768, 32, 12), review_every=64):
    local_n, warm_reviews, composition_n, main_n, selection_n, reviews = sizes
    layout = random.Random(91000+seed)
    forms, representatives = [], []
    for _ in range(2):
        order = list(range(4))
        layout.shuffle(order)
        forms.append([int(order.index(x) >= 2) for x in range(4)])
        representatives.append([order[0], order[2]])
    w = dict(seed=seed, branch=branch, forms=forms, representatives=representatives,
             affected=layout.randrange(2))
    inputs, noise = random.Random(92000+seed), random.Random(93000+seed)

    def shuffled(n, contexts):
        out = []
        while len(out) < n:
            block = list(contexts)
            inputs.shuffle(block)
            out.extend(block[:n-len(out)])
        return out

    def local(n, j):
        # Consume input shuffles and noise block by block, as in 013.
        out = []
        for start in range(0, n, 4):
            for x in shuffled(min(4, n-start), range(4)):
                out.append(dict(x=x, y=forms[j][x] ^ int(noise.random() < .1)))
        return out

    w['local_main'] = [local(local_n, j) for j in range(2)]
    w['local_selection'] = [[local(selection_n, j) for j in range(2)] for _ in range(warm_reviews)]
    training = []
    for start in range(0, composition_n, 8):
        for l, r, a in shuffled(min(8, composition_n-start), list(it.product(*representatives, (0, 1)))):
            training.append(dict(x=[l, r], a=a, y=target(w, [l, r], a, 0) ^ int(noise.random() < .1)))
    w['composition'] = training

    def joint(n, review=None):
        out = []
        for start in range(0, n, 32):
            for l, r, a in shuffled(min(32, n-start), CONTEXTS):
                t = review if review is not None else len(out)+1
                f = forms_at(w, t, True)
                x = [l, r]
                labels = [f[j][x[j]] ^ int(noise.random() < .1) for j in range(2)]
                out.append(dict(x=x, a=a, local=labels,
                                y=target(w, x, a, t) ^ int(noise.random() < .1)))
        return out
    w['main'] = joint(main_n)
    w['selection'] = [joint(selection_n, review_every*(i+1)) for i in range(reviews)]
    return w


def expectation(p, y):
    q = .9 if y else .1
    return -q*math.log(p)-(1-q)*math.log1p(-p)


def partitions_equal(a, b):
    return all((a[i] == a[j]) == (b[i] == b[j]) for i in range(4) for j in range(4))


def oracle_risk(spec, groups, w, t):
    buckets = {}
    for l, r, a in CONTEXTS:
        x = [l, r]
        key = tuple(x[j] if s == 2 else groups[j][x[j]] for j, s in enumerate(spec) if s)+(a,)
        buckets.setdefault(key, []).append(.9 if target(w, x, a, t) else .1)
    return sum(len(qs)*(-mean(qs)*math.log(mean(qs))-(1-mean(qs))*math.log1p(-mean(qs)))
               for qs in buckets.values())/32


def evaluate(learner, w, t, transfer=False):
    contexts = [c for c in CONTEXTS if not transfer or not(
        c[0] in w['representatives'][0] and c[1] in w['representatives'][1])]
    before = (learner.upper.state(), [n.model.state() for n in learner.nodes])
    ps = [learner.predict([l, r], a)[0] for l, r, a in contexts]
    ys = [target(w, [l, r], a, t) for l, r, a in contexts]
    loss = mean(expectation(p, y) for p, y in zip(ps, ys))
    states = [n.model.state() for n in learner.nodes]
    groups = [s['groups'] for s in states]
    spec = learner.upper.spec
    risk = oracle_risk(spec, groups, w, t)
    drops, additions = {}, {}
    for j, s in enumerate(spec):
        if s:
            reduced = list(spec); reduced[j] = 0
            drops[str(j)] = oracle_risk(reduced, groups, w, t)-risk
        if s != 2:
            enlarged = list(spec); enlarged[j] = 2
            additions[str(j)] = risk-oracle_risk(enlarged, groups, w, t)
    assert before == (learner.upper.state(), [n.model.state() for n in learner.nodes])
    return dict(index=t, predictions=ps, expected_loss=loss, regret=loss-H,
        accuracy=mean((p > .5) == bool(y) for p, y in zip(ps, ys)),
        local_exact=[partitions_equal(s['partition'], f) for s, f in zip(states, forms_at(w, t))],
        semantic_alignment=[g == f for g, f in zip(groups, forms_at(w, t))],
        local_groups=[len(s['counts']) for s in states], spec=list(spec), contexts=len(contexts),
        oracle_regret=risk-H, removal_costs=drops, raw_addition_gains=additions,
        sufficient_minimal=risk-H <= .10 and all(v > .02 for v in drops.values()) and all(v <= .02 for v in additions.values()))


def run(w, variant, ps, review_every=64, measure=True):
    learner = StructuralLearner([94000+2*ps+j for j in range(2)], 95000+ps, variant)
    warm = []
    for i in range(len(w['local_main'][0])):
        for j in range(2):
            learner.observe_local(j, f'warm/{j}/{i}', w['local_main'][j][i])
        if (i+1) % review_every == 0:
            batch = w['local_selection'][i//review_every]
            warm.append([learner.review_local(j, [f'warm-select/{j}/{i}/{k}' for k in range(len(batch[j]))], batch[j]) for j in range(2)])
    learner.train_upper([f'composition/{i}' for i in range(len(w['composition']))], w['composition'])
    r = dict(seed=w['seed'], branch=w['branch'], variant=variant, proposal_seed=ps, warmup=warm,
             initial_upper=learner.upper.state(), transfer=evaluate(learner, w, 0, True),
             predictions=[], local_predictions=[], raw_reads=[], reviews=[], endpoints=[])
    for t, row in enumerate(w['main'], 1):
        r['local_predictions'].append(None if variant == 'raw' else [n.model.predict(row['x'][j]) for j, n in enumerate(learner.nodes)])
        p, reads = learner.step(f'main/{t}', row)
        r['predictions'].append(p); r['raw_reads'].append(reads)
        if t % review_every == 0:
            review = learner.review(f'select/{t}', w['selection'][t//review_every-1])
            r['reviews'].append(dict(index=t, **review, evaluation=evaluate(learner, w, t)))
        if t in (240, 528, 768):
            r['endpoints'].append(evaluate(learner, w, t))
    costs = {k: sum(n.costs[k] for n in learner.nodes) for k in learner.nodes[0].costs}
    costs.update(learner.costs)
    costs.update(feedback_labels=len(learner.ledger.main)+len(learner.ledger.selection),
                 scoring_queries=learner.scoring+sum(n.queries for n in learner.nodes),
                 local_pending_peak=max(n.pending_peak for n in learner.nodes), **learner.peaks)
    r.update(costs=costs, final_upper=learner.upper.state(), final_local=[n.model.state() for n in learner.nodes],
        archive=learner.archive.state(), evidence=dict(main=len(learner.ledger.main), selection=len(learner.ledger.selection),
            reused=sum(len(u.get('reused', [])) for u in learner.ledger.uses), events=len(learner.events)))
    checkpoint = learner.checkpoint()
    r['checkpoint_sha256'] = hashlib.sha256(checkpoint.encode()).hexdigest()
    if measure:
        r['metrics'] = metrics(r, w)
    return r, checkpoint


def hashes():
    previous = json.loads((ROOT/'results/protection-interfaces-v1/manifest.json').read_text())
    files = set(previous) | {'results/protection-interfaces-v1/manifest.json', 'results/protection-interfaces-v1/results.json',
        'results/protection-interfaces-v1/audit.json', 'results/protection-interfaces-v1/runs.jsonl.gz',
        'advaita/structural.py', 'experiments/structural_consolidation_protocol.md',
        'experiments/structural_consolidation.py', 'experiments/structural_consolidation_metrics.py',
        'checks/structural_reference.py', 'checks/audit_structural_consolidation.py',
        'checks/test_structural_consolidation.py', 'results/structural-consolidation-fixtures.json'}
    for name, expected in previous.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == expected, name
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/structural-consolidation-v1')
    args = parser.parse_args()
    fixture = json.loads((ROOT/'results/structural-consolidation-fixtures.json').read_text())
    assert fixture['status'] == 'pass' and fixture['charged_labels'] <= 720
    for name, digest in fixture['tested_sources'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    c1 = json.loads((ROOT/'results/protection-interfaces-v1/audit.json').read_text())
    assert c1['status'] == 'pass' and c1['progression_gate']
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'checkpoints').mkdir()
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    def timeout(*_):
        raise TimeoutError('600-second C2 benchmark limit')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(600)
    started, runs, worlds = time.monotonic(), [], []
    try:
        for seed in range(700, 705):
            for branch in BRANCHES:
                w = generate(seed, branch); worlds.append(w)
                (args.output/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (700, 701):
                    for variant in VARIANTS:
                        r, checkpoint = run(w, variant, ps)
                        path = f'checkpoints/{seed}-{branch}-{ps}-{variant}.json.gz'
                        with gzip.open(args.output/path, 'wt') as stream: stream.write(checkpoint)
                        r['checkpoint_file'] = path; runs.append(r)
                        with gzip.open(args.output/'runs.jsonl.gz', 'at') as stream: stream.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/120 runs saved', flush=True)
        assert hashes() == provenance
        totals = dict(runs=len(runs), allocated_labels=537600, generated_labels=67200,
            used_labels=sum(r['costs']['feedback_labels'] for r in runs),
            candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
            scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),
            composite_predictions=sum(len(r['predictions']) for r in runs),
            local_predictions=sum(2*sum(p is not None for p in r['local_predictions']) for r in runs),
            evaluation_predictions=sum(r['transfer']['contexts']+sum(e['contexts'] for e in r['endpoints'])+
                sum(v['evaluation']['contexts'] for v in r['reviews']) for r in runs))
        assert totals['used_labels'] == 433920 and totals['candidate_fits'] <= 17160
        assert totals['scoring_queries'] <= 3000000 and totals['evaluation_predictions'] == 60480
        data = dict(summary=summarize(runs), totals=totals, hashes=provenance,
                    elapsed_seconds=time.monotonic()-started, status='completed_pending_audit')
        (args.output/'results.json').write_text(json.dumps(data, indent=2)+'\n')
        print(json.dumps(data['summary']['checks'], indent=2), flush=True)
    except Exception as exc:
        (args.output/'incomplete.json').write_text(json.dumps(dict(error=str(exc), completed_runs=len(runs),
            elapsed_seconds=time.monotonic()-started), indent=2)+'\n')
        raise
    finally:
        signal.alarm(0)


if __name__ == '__main__':
    main()
