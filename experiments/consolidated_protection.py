"""020: paired corroboration of established forms in the structural learner."""
import copy
import gzip
import hashlib
import itertools as it
import json
import math
from pathlib import Path
import signal
from statistics import mean
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from advaita.structural import StructuralLearner
from advaita.corroboration import CorroboratedLearner
from advaita.state import canonical
from protection_interfaces import generate, forms_at, target
from consolidated_protection_metrics import metrics, summarize

BRANCHES = ('persistent', 'burst', 'remap')
POLICIES = ('baseline', 'corroborated')
CONTEXTS = list(it.product(range(4), range(4), range(2)))
H = -.1*math.log(.1)-.9*math.log(.9)
OUT = ROOT/'results/consolidated-protection-v1'
FILES = ('advaita/corroboration.py', 'experiments/consolidated_protection_protocol.md',
    'experiments/consolidated_protection.py', 'experiments/consolidated_protection_metrics.py',
    'checks/audit_consolidated_protection.py', 'checks/test_consolidated_protection.py')

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
    variant = "integrated"
    seeds = [94000+2*ps+j for j in range(2)]
    learner = (StructuralLearner(seeds, 95000+ps, variant) if policy == "baseline"
               else CorroboratedLearner(seeds, 95000+ps))
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
             predictions=[], local_predictions=[], raw_reads=[], pre_specs=[], pre_local_exact=[], reviews=[], endpoints=[])
    for t, row in enumerate(w['main'], 1):
        r['pre_specs'].append(list(learner.upper.spec))
        r['pre_local_exact'].append([partitions_equal(n.model.partition, f) for n, f in zip(learner.nodes, forms_at(w, t))])
        r['local_predictions'].append(None if variant == 'raw' else [n.model.predict(row['x'][j]) for j, n in enumerate(learner.nodes)])
        p, reads = learner.step(f'main/{t}', row)
        r['predictions'].append(p); r['raw_reads'].append(reads)
        if t % review_every == 0:
            review = learner.review(f'select/{t}', w['selection'][t//review_every-1])
            r['reviews'].append(dict(index=t, **review, evaluation=evaluate(learner, w, t)))
        if t in (128, 192, 320, 512, 1280):
            r['endpoints'].append(evaluate(learner, w, t))
    costs = {k: sum(n.costs[k] for n in learner.nodes) for k in learner.nodes[0].costs}
    costs.update(learner.costs)
    costs.update(feedback_labels=len(learner.ledger.main)+len(learner.ledger.selection),
                 scoring_queries=learner.scoring+sum(n.queries for n in learner.nodes),
                 local_pending_peak=max(n.pending_peak for n in learner.nodes), **learner.peaks)
    r.update(costs=costs, final_upper=learner.upper.state(), final_local=[n.model.state() for n in learner.nodes],
        archive=learner.archive.state(), evidence=dict(main=len(learner.ledger.main), selection=len(learner.ledger.selection),
            reused=sum(len(u.get('reused', [])) for u in learner.ledger.uses), events=len(learner.events)))
    r['protection'] = [copy.deepcopy(getattr(n, 'protection', None)) for n in learner.nodes]
    r['protection_costs'] = [copy.deepcopy(getattr(n, 'protection_costs', None)) for n in learner.nodes]
    checkpoint = learner.checkpoint()
    r['checkpoint_sha256'] = hashlib.sha256(checkpoint.encode()).hexdigest()
    if measure:
        r['metrics'] = metrics(r, w)
    return r, checkpoint


def hashes():
    previous=json.loads((ROOT/'results/consolidated-recovery-v1/manifest.json').read_text())
    for name,digest in previous.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    names=set(previous)|set(FILES)|{'results/consolidated-protection-fixtures.json'}
    names.update('results/consolidated-recovery-v1/'+n for n in ('manifest.json','results.json','audit.json','runs.jsonl.gz','worlds.json'))
    return {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in sorted(names)}


def main():
    fixture=json.loads((ROOT/'results/consolidated-protection-fixtures.json').read_text())
    assert fixture['status']=='pass' and fixture['charged_labels']<=2000
    for name,digest in fixture['sources'].items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    OUT.mkdir(exist_ok=False); (OUT/'checkpoints').mkdir()
    provenance=hashes(); (OUT/'manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
    def timeout(*_): raise TimeoutError('600-second 020 benchmark limit')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(600)
    started,worlds,runs=time.monotonic(),[],[]
    try:
        for seed in range(900,905):
            for branch in BRANCHES:
                w=generate(seed,branch,sizes=(256,4,256,1280,32,20)); worlds.append(w)
                (OUT/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (900,901):
                    for policy in POLICIES:
                        r,checkpoint=run(w,policy,ps)
                        path=f'checkpoints/{seed}-{branch}-{ps}-{policy}.json.gz'
                        with gzip.open(OUT/path,'wt') as f: f.write(checkpoint)
                        r['checkpoint_file']=path; runs.append(r)
                        with gzip.open(OUT/'runs.jsonl.gz','at') as f: f.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/60 saved',flush=True)
        assert hashes()==provenance
        es=[e for r in runs for e in [r['transfer'],*r['endpoints'],*(v['evaluation'] for v in r['reviews'])]]
        resources=dict(runs=len(runs),allocated_labels=407040,generated_labels=101760,
            used_labels=sum(r['costs']['feedback_labels'] for r in runs),
            candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
            scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),
            composite_predictions=sum(len(r['predictions']) for r in runs),local_predictions=2*sum(len(r['local_predictions']) for r in runs),
            evaluation_predictions=sum(e['contexts'] for e in es),
            oracle_context_queries=32*sum(1+len(e['removal_costs'])+len(e['raw_addition_gains']) for e in es),
            confirmation_queries=sum(c['confirmation_queries'] for r in runs for c in r['protection_costs'] if c is not None))
        assert resources['used_labels']==407040 and resources['candidate_fits']<=19920 and resources['scoring_queries']<=3000000
        assert resources['composite_predictions']==76800 and resources['local_predictions']==153600
        assert resources['evaluation_predictions']==49440 and resources['oracle_context_queries']<=249600
        data=dict(status='completed_pending_audit',summary=summarize(runs),totals=resources,hashes=provenance,elapsed_seconds=time.monotonic()-started)
        (OUT/'results.json').write_text(json.dumps(data,indent=2)+'\n')
        print(json.dumps(data['summary']['checks'],indent=2),flush=True)
    except Exception as exc:
        (OUT/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed_runs=len(runs),elapsed_seconds=time.monotonic()-started),indent=2)+'\n')
        raise
    finally: signal.alarm(0)


if __name__=='__main__': main()
