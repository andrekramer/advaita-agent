"""017: fixed factorial study of local protection and interface reclosure."""
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
import statistics as st
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.runtime import NestedLearner
from advaita.state import canonical
from protection_interfaces_metrics import metrics, summarize

BRANCHES = ('persistent', 'remap', 'burst')
VARIANTS = ('immediate_opening', 'immediate_reclosure', 'earned_opening', 'earned_reclosure')
CONTEXTS = list(it.product(range(4), range(4), range(2)))
H = -.1*math.log(.1)-.9*math.log(.9)


def forms_at(w, t, observed=False):
    forms = copy.deepcopy(w['forms'])
    shifted = w['branch'] == 'remap' and t > 128
    corrupted = observed and w['branch'] == 'burst' and 128 < t <= 192
    if shifted or corrupted:
        for x in w['representatives'][w['affected']]:
            forms[w['affected']][x] ^= 1
    return forms


def target(w, x, a, t):
    f = forms_at(w, t)
    return f[0][x[0]] ^ f[1][x[1]] ^ a


def generate(seed, branch, sizes=(256, 4, 256, 512, 32, 8), review_every=64):
    local_n, warm_reviews, composition_n, main_n, selection_n, reviews = sizes
    layout = random.Random(81000+seed)
    forms, representatives = [], []
    for _ in range(2):
        order = list(range(4))
        layout.shuffle(order)
        forms.append([int(order.index(x) >= 2) for x in range(4)])
        representatives.append([order[0], order[2]])
    w = dict(seed=seed, branch=branch, forms=forms, representatives=representatives,
             affected=layout.randrange(2))
    inputs, noise = random.Random(82000+seed), random.Random(83000+seed)

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


def expectation(p, bit):
    q = .9 if bit else .1
    return -q*math.log(p)-(1-q)*math.log1p(-p)


def evaluate(learner, w, t, transfer=False):
    contexts = [c for c in CONTEXTS if not transfer or not(
        c[0] in w['representatives'][0] and c[1] in w['representatives'][1])]
    ps, losses, correct = [], [], 0
    for l, r, a in contexts:
        p, _ = learner.predict([l, r], a)
        y = target(w, [l, r], a, t)
        ps.append(p)
        losses.append(expectation(p, y))
        correct += (p > .5) == bool(y)
    value = st.mean(losses)
    return dict(predictions=ps, expected_loss=value, regret=value-H,
                accuracy=correct/len(contexts), local_exact=[
                    n.model.state()['groups'] == f for n, f in zip(learner.nodes, forms_at(w, t))],
                mode=learner.upper.mode, cells=len(learner.upper.counts), contexts=len(contexts))


def run(w, variant, ps, review_every=64, measure=True):
    local, exposure = variant.split('_')
    learner = NestedLearner([84000+2*ps+j for j in range(2)], local, exposure == 'reclosure')
    warm = []
    for i in range(len(w['local_main'][0])):
        for j in range(2):
            learner.observe_local(j, f'warm/{j}/{i}', w['local_main'][j][i])
        if (i+1) % review_every == 0:
            batch = w['local_selection'][i//review_every]
            warm.append([learner.review_local(j, [f'warm-select/{j}/{i}/{k}' for k in range(len(batch[j]))],
                                               batch[j]) for j in range(2)])
    learner.train_upper([f'composition/{i}' for i in range(len(w['composition']))], w['composition'])
    r = dict(seed=w['seed'], branch=w['branch'], variant=variant, proposal_seed=ps,
             warmup=warm, initial_upper=learner.upper.state(), transfer=evaluate(learner, w, 0, True),
             predictions=[], local_predictions=[], raw_reads=[], pre_modes=[], pre_local_exact=[], reviews=[])
    for t, row in enumerate(w['main'], 1):
        r['local_predictions'].append([n.model.predict(row['x'][j]) for j, n in enumerate(learner.nodes)])
        r['pre_modes'].append(learner.upper.mode)
        r['pre_local_exact'].append([n.model.state()['groups'] == f
                                    for n, f in zip(learner.nodes, forms_at(w, t))])
        p, raw = learner.step(f'main/{t}', row)
        r['predictions'].append(p)
        r['raw_reads'].append(raw)
        if t % review_every == 0:
            detail = learner.review(f'select/{t}', w['selection'][t//review_every-1])
            r['reviews'].append(dict(index=t, **detail, evaluation=evaluate(learner, w, t)))
    r.update(final_upper=learner.upper.state(), final_local=[n.model.state() for n in learner.nodes],
             pending=learner.reclosure.state(), local_policies=[n.policy.state() if hasattr(n, 'policy') else None
                                                             for n in learner.nodes])
    costs = {k: sum(n.costs[k] for n in learner.nodes) for k in learner.nodes[0].costs}
    costs.update(learner.costs)
    costs['feedback_labels'] = len(learner.ledger.main)+len(learner.ledger.selection)
    costs['reclosure'] = copy.deepcopy(learner.reclosure.costs)
    costs['local_retention'] = [copy.deepcopy(n.policy.costs) if hasattr(n, 'policy') else None for n in learner.nodes]
    # Existing main labels are repeatedly scored, not newly acquired.
    local_reviews = [v for pair in warm for v in pair]+[v for rev in r['reviews'] for v in rev['local']]
    costs['scoring_queries'] = sum(
        4*min(64, sum(c[1] for c in (v.get('ordinary', v)['before']['counts']).values()))+2*len(batch)
        for v, batch in zip(local_reviews,
            [b for pair in w['local_selection'] for b in pair]+[b for batch in w['selection'] for b in (batch, batch)]))
    costs['scoring_queries'] += sum(3*sum(c[1] for c in rev['ordinary']['candidates'][0]['state']['counts'].values())
                                    +2*len(batch) for rev, batch in zip(r['reviews'], w['selection']))
    costs['scoring_queries'] += learner.reclosure.costs['challenger_predictions']+sum(
        n.policy.costs['pending_predictions'] for n in learner.nodes if hasattr(n, 'policy'))
    r['costs'] = costs
    r['evidence'] = dict(main=len(learner.ledger.main), selection=len(learner.ledger.selection),
                        reused=sum(len(u.get('reused', [])) for u in learner.ledger.uses), events=len(learner.events))
    checkpoint = learner.checkpoint()
    ledger = canonical(learner.ledger.state())
    r['checkpoint_sha256'] = hashlib.sha256(checkpoint.encode()).hexdigest()
    r['ledger_sha256'] = hashlib.sha256(ledger.encode()).hexdigest()
    if measure:
        r['metrics'] = metrics(r, w)
    return r, checkpoint


def hashes():
    previous = json.loads((ROOT/'results/consolidation-core-v1/manifest.json').read_text())
    files = set(previous) | {'results/consolidation-core-v1/manifest.json',
        'results/consolidation-core-v1/compatibility.json', 'results/consolidation-core-v1/replayed-runs.jsonl.gz',
        'experiments/protection_interfaces_protocol.md', 'experiments/protection_interfaces.py',
        'experiments/protection_interfaces_metrics.py', 'checks/test_protection_interfaces.py',
        'checks/audit_protection_interfaces.py', 'results/protection-interfaces-fixtures.json'}
    for name, digest in previous.items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    return {name: hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(files)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'results/protection-interfaces-v1')
    args = parser.parse_args()
    fixture = json.loads((ROOT/'results/protection-interfaces-fixtures.json').read_text())
    assert fixture['status'] == 'pass' and fixture['charged_labels'] <= 336
    args.output.mkdir(parents=True, exist_ok=False)
    (args.output/'checkpoints').mkdir()
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance, indent=2)+'\n')
    started = time.monotonic()
    def timeout(*_):
        raise TimeoutError('600-second benchmark limit')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(600)
    runs, worlds = [], []
    try:
        for seed in range(600, 605):
            for branch in BRANCHES:
                w = generate(seed, branch)
                worlds.append(w)
                for ps in (600, 601):
                    for variant in VARIANTS:
                        r, checkpoint = run(w, variant, ps)
                        path = f'checkpoints/{seed}-{branch}-{ps}-{variant}.json.gz'
                        with gzip.open(args.output/path, 'wt') as stream:
                            stream.write(checkpoint)
                        r['checkpoint_file'] = path
                        runs.append(r)
                        with gzip.open(args.output/'runs.jsonl.gz', 'at') as stream:
                            stream.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/120 runs saved', flush=True)
        assert hashes() == provenance
        total = dict(runs=len(runs), generated_labels=49920, allocated_labels=399360,
                     used_labels=sum(r['costs']['feedback_labels'] for r in runs),
                     candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
                     scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),
                     composite_predictions=sum(len(r['predictions']) for r in runs),
                     local_predictions=sum(2*len(r['local_predictions']) for r in runs),
                     evaluation_predictions=sum(r['transfer']['contexts']+sum(v['evaluation']['contexts'] for v in r['reviews']) for r in runs))
        assert total['used_labels'] == 399360 and total['candidate_fits'] == 14400
        assert total['scoring_queries'] <= 1700000
        data = dict(worlds=worlds, summary=summarize(runs), totals=total, hashes=provenance,
                    elapsed_seconds=time.monotonic()-started, status='completed_pending_audit')
        (args.output/'results.json').write_text(json.dumps(data, indent=2)+'\n')
    except Exception as exc:
        (args.output/'incomplete.json').write_text(json.dumps(dict(error=str(exc), completed_runs=len(runs),
            elapsed_seconds=time.monotonic()-started), indent=2)+'\n')
        raise
    finally:
        signal.alarm(0)
    print(json.dumps(data['summary']['checks'], indent=2), flush=True)
    print(f"C2 empirical gate: {data['summary']['progression_gate']}; independent audit required", flush=True)


if __name__ == '__main__':
    main()
