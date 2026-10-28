"""024: controlled comparison of explicit predictive and structural roles."""
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
from advaita.explicit_roles import RoleLearner
from advaita.state import canonical
from explicit_roles_metrics import metrics, summarize

BRANCHES = ('stable','probability','forms','detail','reversed')
POLICIES = ('B64','B128','U64','U128','R128','H128')
CONTEXTS = list(it.product(range(4), range(4), range(2)))
H = -.1*math.log(.1)-.9*math.log(.9)


def forms_at(w, t, observed=False):
    f = copy.deepcopy(w['forms'])
    if w['branch'] == 'forms' and 240 < t <= 528:
        f[w['affected']] = [0, 0, 0, 0]
    if observed and w['branch'] == 'probability' and 240 < t <= 528:
        f[w['affected']] = [1-v for v in f[w['affected']]]
    return f


def target(w, x, a, t):
    f = forms_at(w, t)
    y = f[0][x[0]] ^ f[1][x[1]] ^ a
    if w['branch'] in ('detail','reversed') and (0 < t <= 240 or t > 528):
        j = w['affected']
        y ^= int(x[j] != w['representatives'][j][f[j][x[j]]])
        if w['branch'] == 'reversed' and t > 528:
            y ^= 1
    if w['branch'] == 'probability' and 240 < t <= 528: y ^= 1
    return y


def generate(seed, branch, sizes=(256, 4, 256, 1280, 32, 20), review_every=64):
    local_n, warm_reviews, composition_n, main_n, selection_n, reviews = sizes
    layout = random.Random(151000+seed)
    forms, representatives = [], []
    for _ in range(2):
        order = list(range(4))
        layout.shuffle(order)
        forms.append([int(order.index(x) >= 2) for x in range(4)])
        representatives.append([order[0], order[2]])
    w = dict(seed=seed, branch=branch, forms=forms, representatives=representatives,
             affected=layout.randrange(2))
    inputs = random.Random(152000+seed)
    noise = [random.Random(base+seed) for base in (153000,154000,155000)]

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
                out.append(dict(x=x, y=forms[j][x] ^ int(noise[j].random() < .1)))
        return out

    w['local_main'] = [local(local_n, j) for j in range(2)]
    w['local_selection'] = [[local(selection_n, j) for j in range(2)] for _ in range(warm_reviews)]
    training = []
    for start in range(0, composition_n, 8):
        for l, r, a in shuffled(min(8, composition_n-start), list(it.product(*representatives, (0, 1)))):
            training.append(dict(x=[l, r], a=a, y=target(w, [l, r], a, 0) ^ int(noise[2].random() < .1)))
    w['composition'] = training

    def joint(n, review=None):
        out = []
        for start in range(0, n, 32):
            for l, r, a in shuffled(min(32, n-start), CONTEXTS):
                t = review if review is not None else len(out)+1
                f = forms_at(w, t, True)
                x = [l, r]
                labels = [f[j][x[j]] ^ int(noise[j].random() < .1) for j in range(2)]
                out.append(dict(x=x, a=a, local=labels,
                                y=target(w, x, a, t) ^ int(noise[2].random() < .1)))
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


def run(w, policy, ps, review_every=64, measure=True):
    variant = 'integrated'
    learner = RoleLearner([94000+2*ps+j for j in range(2)], 95000+ps, variant, policy)
    period = review_every if policy in ('B64','U64') else review_every*2
    warm = []
    for i in range(len(w['local_main'][0])):
        for j in range(2):
            learner.observe_local(j, f'warm/{j}/{i}', w['local_main'][j][i])
        if (i+1) % review_every == 0:
            batch = w['local_selection'][i//review_every]
            warm.append([learner.review_local(j, [f'warm-select/{j}/{i}/{k}' for k in range(len(batch[j]))], batch[j]) for j in range(2)])
    learner.train_upper([f'composition/{i}' for i in range(len(w['composition']))], w['composition'])
    r = dict(seed=w['seed'], branch=w['branch'], variant=variant, policy=policy, proposal_seed=ps, warmup=warm,
             initial_upper=learner.upper.state(), transfer=evaluate(learner, w, 0, True),
             predictions=[], local_predictions=[], raw_reads=[], reviews=[], evaluations=[], endpoints=[], diagnostics=[])
    for t, row in enumerate(w['main'], 1):
        r['local_predictions'].append(None if variant == 'raw' else [n.model.predict(row['x'][j]) for j, n in enumerate(learner.nodes)])
        before = [n.model.state() for n in learner.nodes]
        spec = list(learner.upper.spec)
        p, reads = learner.step(f'main/{t}', row)
        r['predictions'].append(p); r['raw_reads'].append(reads)
        if t % period == 0:
            review = learner.review(f'select/{t}', w['selection'][t//review_every-1])
            r['reviews'].append(dict(index=t, **review))
        if t % review_every == 0: r['evaluations'].append(evaluate(learner, w, t))
        after = [n.model.state() for n in learner.nodes]
        r['diagnostics'].append(dict(
            group_changes=[a['groups'] != b['groups'] for a,b in zip(before,after)],
            partition_changes=[not partitions_equal(a['partition'], b['partition']) for a,b in zip(before,after)],
            raw_bypass=sum(spec[j]==2 and not partitions_equal(before[j]['partition'], forms_at(w,t)[j]) for j in range(2))))
        if t in (240, 528):
            r['endpoints'].append(evaluate(learner, w, t))
    costs = {k: sum(n.costs[k] for n in learner.nodes) for k in learner.nodes[0].costs}
    costs.update(learner.costs)
    costs.update(feedback_labels=len(learner.ledger.main)+len(learner.ledger.selection),
                 scoring_queries=learner.scoring+sum(n.queries for n in learner.nodes)+learner.history_costs['feature_predictions'],
                 history_rows=learner.history_costs['proposal_rows']+sum(n.history_rows for n in learner.nodes),
                 history_feature_predictions=learner.history_costs['feature_predictions'],
                 local_pending_peak=max(n.pending_peak for n in learner.nodes), **learner.peaks)
    r.update(costs=costs, final_upper=learner.upper.state(), final_local=[n.model.state() for n in learner.nodes],
        archive=learner.archive.state(), evidence=dict(main=len(learner.ledger.main), selection=len(learner.ledger.selection),
            reused=sum(len(u.get('reused', [])) for u in learner.ledger.uses), events=len(learner.events)))
    checkpoint = learner.checkpoint()
    r['checkpoint_sha256'] = hashlib.sha256(checkpoint.encode()).hexdigest()
    if measure:
        r['metrics'] = metrics(r, w, target, forms_at)
    return r, checkpoint



def hashes():
    previous=json.loads((ROOT/'results/memory-selection-v1/manifest.json').read_text())
    for name,digest in previous.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    names=set(previous)
    names.update('results/memory-selection-v1/'+n for n in ('manifest.json','results.json','audit.json','worlds.json','runs.jsonl.gz'))
    names.update(('advaita/explicit_roles.py','experiments/explicit_roles.py','experiments/explicit_roles_metrics.py',
        'checks/roles_reference.py','checks/audit_explicit_roles.py','checks/test_explicit_roles.py','checks/roles_compatibility.py',
        'experiments/explicit_roles_spec.md','experiments/explicit_roles_protocol.md','experiments/explicit_roles_test_plan.md'))
    names.update(str(p.relative_to(ROOT)) for p in (ROOT/'results/explicit-roles-r0').glob('*.json'))
    return {n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in sorted(names)}


def totals(runs):
    es=[e for r in runs for e in [r['transfer'],*r['evaluations'],*r['endpoints']]]
    return dict(runs=len(runs),allocated_labels=len(runs)*6784,generated_labels=25*6784,
        used_labels=sum(r['costs']['feedback_labels'] for r in runs),
        candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
        scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),
        history_rows=sum(r['costs']['history_rows'] for r in runs),
        history_feature_predictions=sum(r['costs']['history_feature_predictions'] for r in runs),
        composite_predictions=sum(len(r['predictions']) for r in runs),local_predictions=2*sum(len(r['predictions']) for r in runs),
        evaluation_predictions=sum(e['contexts'] for e in es),
        oracle_context_queries=32*sum(1+len(e['removal_costs'])+len(e['raw_addition_gains']) for e in es))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--confirmation',action='store_true')
    args=parser.parse_args();confirmation=args.confirmation
    folder=ROOT/'results/explicit-roles-r0'
    fixtures=[json.loads(p.read_text()) for p in sorted(folder.glob('fixtures-*.json'))]
    assert fixtures and fixtures[-1]['status']=='pass'
    assert sum(f['charged_labels'] for f in fixtures)<=5000
    parity=json.loads((folder/'compatibility.json').read_text());assert parity['status']=='pass' and parity['runs']==30
    for proof in (fixtures[-1],parity):
        for name,digest in proof['tested_sources'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    candidate='R128';policies=POLICIES;seedbase=1200
    if confirmation:
        first=ROOT/'results/explicit-roles-v1'
        audit=json.loads((first/'audit.json').read_text());result=json.loads((first/'results.json').read_text())
        assert audit['status']=='pass' and result['summary']['primary_pass']
        assert audit['result_sha256']==hashlib.sha256((first/'results.json').read_bytes()).hexdigest()
        candidate='H128' if result['summary']['history_pass'] else 'R128'
        policies=('U128',candidate);seedbase=1300
    out=ROOT/('results/explicit-roles-confirmation-v1' if confirmation else 'results/explicit-roles-v1')
    out.mkdir(exist_ok=False);(out/'checkpoints').mkdir()
    provenance=hashes()
    if confirmation:
        original=json.loads((ROOT/'results/explicit-roles-v1/manifest.json').read_text())
        assert provenance==original
    (out/'manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
    start=time.monotonic();runs=[];worlds=[]
    def timeout(*_):raise TimeoutError('900-second role comparison benchmark limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(seedbase,seedbase+5):
            for branch in BRANCHES:
                w=generate(seed,branch);worlds.append(w)
                (out/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (seedbase,seedbase+1):
                    for policy in policies:
                        r,checkpoint=run(w,policy,ps)
                        path=f'checkpoints/{seed}-{branch}-{ps}-{policy}.json.gz'
                        with gzip.open(out/path,'wt') as f:f.write(checkpoint)
                        r['checkpoint_file']=path;runs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/{100 if confirmation else 300} saved',flush=True)
        assert hashes()==provenance
        resources=totals(runs)
        assert resources['used_labels']==(582400 if confirmation else 1843200)
        for key,limit in dict(candidate_fits=33200 if confirmation else 99600,
                scoring_queries=5000000 if confirmation else 15000000,history_rows=3000000,
                oracle_context_queries=368000 if confirmation else 1104000).items():assert resources[key]<=limit,(key,resources[key],limit)
        assert resources['evaluation_predictions']==(72800 if confirmation else 218400)
        result=dict(status='completed_pending_audit',candidate=candidate,confirmation=confirmation,
            summary=summarize(runs,candidate,confirmation),totals=resources,hashes=provenance,elapsed_seconds=time.monotonic()-start)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(checks=result['summary']['checks'],primary_pass=result['summary']['primary_pass'],history_checks=result['summary']['history_checks']),indent=2))
    except Exception as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed_runs=len(runs),elapsed_seconds=time.monotonic()-start),indent=2)+'\n');raise
    finally:signal.alarm(0)

if __name__=='__main__':main()
