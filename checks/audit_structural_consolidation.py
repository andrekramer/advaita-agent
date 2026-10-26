"""Independent C2 reconstruction; no runtime/experiment imports."""
import copy
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import signal
from statistics import mean
import time

from audit_nested_abstractions import close, CONTEXTS, H, logloss, local_p
from audit_protection_interfaces import canonical, sha
from structural_reference import Local, Upper, fit, predict, ports, fingerprint

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/structural-consolidation-v1'
BRANCHES = ('forms', 'detail', 'reversed')
VARIANTS = ('integrated', 'delete', 'raw', 'fixed')


def truth(w, t, observed=False):
    f = copy.deepcopy(w['forms'])
    if w['branch'] == 'forms' and 241 <= t <= 528:
        f[w['affected']] = [0]*4
    return f


def label(w, x, a, t):
    f = truth(w, t)
    result = (f[0][x[0]]+f[1][x[1]]+a) % 2
    if w['branch'] != 'forms' and t != 0 and not 241 <= t <= 528:
        j = w['affected']
        result = (result+int(x[j] != w['representatives'][j][f[j][x[j]]])) % 2
        if w['branch'] == 'reversed' and t > 528: result = 1-result
    return result


def verify_world(w, review_every=64):
    rng = random.Random(91000+w['seed'])
    f, reps = [], []
    for _ in range(2):
        order = list(range(4))
        rng.shuffle(order)
        f.append([int(x in order[2:]) for x in range(4)])
        reps.append([order[0], order[2]])
    assert (w['forms'], w['representatives'], w['affected']) == (f, reps, rng.randrange(2))
    inputs, noise = random.Random(92000+w['seed']), random.Random(93000+w['seed'])
    def local(n, j):
        rows = []
        for start in range(0, n, 4):
            block = list(range(4))
            inputs.shuffle(block)
            rows += [dict(x=x, y=(f[j][x]+(noise.random() < .1)) % 2) for x in block[:n-start]]
        return rows
    assert w['local_main'] == [local(len(w['local_main'][j]), j) for j in range(2)]
    for batch in w['local_selection']:
        assert batch == [local(len(batch[j]), j) for j in range(2)]
    training = []
    n = len(w['composition'])
    for start in range(0, n, 8):
        block = list(itertools.product(*reps, range(2)))
        inputs.shuffle(block)
        for l, r, a in block[:n-start]:
            training.append(dict(x=[l, r], a=a, y=(f[0][l]+f[1][r]+a+(noise.random() < .1)) % 2))
    assert w['composition'] == training
    def joint(n, when=None):
        rows = []
        for start in range(0, n, 32):
            block = CONTEXTS.copy()
            inputs.shuffle(block)
            for l, r, a in block[:n-start]:
                t = len(rows)+1 if when is None else when
                true, obs = truth(w, t), truth(w, t, True)
                local = [(obs[j][x]+(noise.random() < .1)) % 2 for j, x in enumerate((l, r))]
                y = (label(w, [l, r], a, t)+(noise.random() < .1)) % 2
                rows.append(dict(x=[l, r], a=a, local=local, y=y))
        return rows
    assert w['main'] == joint(len(w['main']))
    for i, batch in enumerate(w['selection'], 1):
        assert batch == joint(len(batch), i*review_every)


def same_partition(a, b):
    return all({i for i in range(4) if a[i] == a[x]} == {i for i in range(4) if b[i] == b[x]} for x in range(4))


def oracle(spec, nodes, w, t):
    bins = {}
    for l, r, a in CONTEXTS:
        x = (l, r)
        k = tuple(x[j] if s == 2 else nodes[j].state()['groups'][x[j]] for j, s in enumerate(spec) if s)+(a,)
        bins.setdefault(k, []).append(.1+.8*label(w, x, a, t))
    total = 0
    for ps in bins.values():
        p = sum(ps)/len(ps)
        total += len(ps)*(-p*math.log(p)-(1-p)*math.log1p(-p))
    return total/32


def verify_eval(saved, model, nodes, w, t, transfer=False):
    contexts = [c for c in CONTEXTS if not transfer or c[0] not in w['representatives'][0] or c[1] not in w['representatives'][1]]
    ps = [predict(model, nodes, [l, r], a) for l, r, a in contexts]
    ys = [label(w, [l, r], a, t) for l, r, a in contexts]
    value = mean(.9*logloss(p, y)+.1*logloss(p, 1-y) for p, y in zip(ps, ys))
    spec = model['spec']; baseline = oracle(spec, nodes, w, t)
    drops, additions = {}, {}
    for j, s in enumerate(spec):
        if s:
            new = spec.copy(); new[j] = 0
            drops[str(j)] = oracle(new, nodes, w, t)-baseline
        if s != 2:
            new = spec.copy(); new[j] = 2
            additions[str(j)] = baseline-oracle(new, nodes, w, t)
    expected = dict(index=t, predictions=ps, expected_loss=value, regret=value-H,
        accuracy=sum(int((p > .5) == bool(y)) for p, y in zip(ps, ys))/len(ps),
        local_exact=[same_partition(n.partition, f) for n, f in zip(nodes, truth(w, t))],
        semantic_alignment=[n.state()['groups'] == f for n, f in zip(nodes, truth(w, t))],
        local_groups=[len(n.table) for n in nodes], spec=spec, contexts=len(ps), oracle_regret=baseline-H,
        removal_costs=drops, raw_addition_gains=additions,
        sufficient_minimal=baseline-H <= .10 and all(v > .02 for v in drops.values()) and all(v <= .02 for v in additions.values()))
    close(saved, expected)


def verify_run(r, w, checkpoint, review_every=64, measure=True):
    variant = r['variant']
    seeds = [94000+2*r['proposal_seed']+j for j in range(2)]
    nodes = [Local(s) for s in seeds]
    upper = Upper(95000+r['proposal_seed'], variant)
    main, selection, uses, events, ids = set(), set(), [], [], [[], []]
    def use(records, operation, kind):
        if kind == 'fit':
            assert set(records) <= main and not set(records) & selection
            uses.append(dict(kind=kind, operation=operation, ids=records.copy()))
        else:
            assert not set(records) & main
            assert not any(u['kind'] == kind and u['operation'] == operation and set(records) & set(u['ids']) for u in uses)
            uses.append(dict(kind=kind, operation=operation, ids=records.copy(), reused=sorted(set(records)&selection)))
            selection.update(records)
    def update(j, identity, row):
        assert identity not in main | selection
        main.add(identity); nodes[j].update(row)
        ids[j] = (ids[j]+[identity])[-192:]
        use(ids[j], f'local{j}.refit', 'fit')
    def review(j, records, batch, saved):
        use(ids[j], f'local{j}.proposals', 'fit')
        use(records, f'local{j}.replacement', 'selection')
        nodes[j].review(saved, batch)
        events.append(dict(operation='local_review', node=j, ids=records, detail=saved))
    for i in range(len(w['local_main'][0])):
        for j in range(2): update(j, f'warm/{j}/{i}', w['local_main'][j][i])
        if (i+1) % review_every == 0:
            for j in range(2):
                batch = w['local_selection'][i//review_every][j]
                review(j, [f'warm-select/{j}/{i}/{k}' for k in range(len(batch))], batch, r['warmup'][i//review_every][j])
    records = [f'composition/{i}' for i in range(len(w['composition']))]
    main.update(records); use(records, 'upper.initialise', 'fit')
    model = fit((2, 2) if variant == 'raw' else (1, 1), w['composition'], nodes)
    upper.deploy(model, ports(model['spec'], nodes), records)
    close(r['initial_upper'], model)
    for n in nodes: n.structural = True
    events.append(dict(operation='upper_initialise', ids=records, after=model))
    buffer, buffer_ids = w['composition'][-192:], records[-192:]
    verify_eval(r['transfer'], upper.model, nodes, w, 0, True)
    runtime = dict(main_predictions=0, raw_reads=0, upper_refits=0, upper_refit_rows=0, upper_candidate_fits=0, upper_candidate_rows=0)
    assert all(len(r[k]) == len(w['main']) for k in ('predictions', 'raw_reads', 'local_predictions'))
    assert len(r['reviews']) == len(w['main'])//review_every
    endpoint = 0
    for t, row in enumerate(w['main'], 1):
        p = predict(upper.model, nodes, row['x'], row['a']); close(r['predictions'][t-1], p)
        if variant == 'raw': assert r['local_predictions'][t-1] is None
        else: close(r['local_predictions'][t-1], [local_p(n.partition, n.table, row['x'][j]) for j, n in enumerate(nodes)])
        raw = upper.model['spec'].count(2)
        assert r['raw_reads'][t-1] == raw
        runtime['main_predictions'] += 1; runtime['raw_reads'] += raw
        if variant != 'raw':
            for j in range(2): update(j, f'main/{t}/local{j}', dict(x=row['x'][j], y=row['local'][j]))
        record = f'main/{t}/upper'
        assert record not in main | selection
        main.add(record); buffer = (buffer+[row])[-192:]; buffer_ids = (buffer_ids+[record])[-192:]
        if 2 in upper.model['spec']:
            use(buffer_ids, 'upper.refit', 'fit')
            upper.deploy(fit(upper.model['spec'], buffer, nodes), ports(upper.model['spec'], nodes), buffer_ids)
            runtime['upper_refits'] += 1; runtime['upper_refit_rows'] += len(buffer)
        events.append(dict(operation='main', id=f'main/{t}', prediction=r['predictions'][t-1], raw_reads=raw))
        if t % review_every == 0:
            rev, batch = r['reviews'][t//review_every-1], w['selection'][t//review_every-1]
            assert rev['index'] == t
            if variant in ('integrated', 'delete'):
                for j in range(2):
                    records = [f'select/{t}/{i}/local{j}' for i in range(len(batch))]
                    review(j, records, [dict(x=z['x'][j], y=z['local'][j]) for z in batch], rev['local'][j])
                    use(records, f'local{j}.reduction', 'selection')
            else: assert rev['local'] == []
            if variant != 'raw':
                records = [f'select/{t}/{i}/upper' for i in range(len(batch))]
                use(buffer_ids, 'upper.proposals', 'fit')
                use(records, 'upper.replacement', 'selection'); use(records, 'upper.reduction', 'selection')
                upper.review(rev['upper'], buffer, buffer_ids, nodes, batch, f'select/{t}')
                events.append(dict(operation='upper_review', ids=records,
                    detail=dict(local=rev['local'], upper=rev['upper']),
                    stale_binding=fingerprint(upper.ports) != fingerprint(ports(upper.model['spec'], nodes))))
            else: assert rev['upper'] is None
            verify_eval(rev['evaluation'], upper.model, nodes, w, t)
        if t in (240, 528, 768):
            verify_eval(r['endpoints'][endpoint], upper.model, nodes, w, t); endpoint += 1
    assert len(r['endpoints']) == endpoint
    runtime['upper_candidate_fits'], runtime['upper_candidate_rows'] = upper.fits, upper.fitrows
    costs = {k: sum(n.costs[k] for n in nodes) for k in nodes[0].costs}; costs.update(runtime)
    costs.update(feedback_labels=len(main)+len(selection), scoring_queries=upper.scoring+sum(n.queries for n in nodes),
                 local_pending_peak=max(n.pending_peak for n in nodes), **upper.peaks)
    close(r['costs'], costs)
    close(r['final_upper'], upper.model); close(r['final_local'], [n.state() for n in nodes]); close(r['archive'], upper.archive)
    assert r['evidence'] == dict(main=len(main), selection=len(selection), reused=sum(len(u.get('reused', [])) for u in uses), events=len(events))
    expected = dict(schema=2, seeds=seeds, upper_seed=95000+r['proposal_seed'], variant=variant,
        nodes=[dict(model=n.state(), buffer=n.buffer, deck=n.deck, rng=n.random.getstate(), costs=n.costs,
                    pending=n.pending, structural=n.structural, queries=n.queries, pending_peak=n.pending_peak) for n in nodes],
        upper=upper.model, upper_ports=upper.ports, upper_training_ids=upper.ids, upper_binding=fingerprint(upper.ports),
        upper_rng=upper.rng.getstate(), upper_deck=upper.deck, pending=upper.pending, archive=upper.archive,
        local_ids=ids, revisions=[n.revision for n in nodes], buffer=buffer, buffer_ids=buffer_ids,
        ledger=dict(main=sorted(main), selection=sorted(selection), uses=uses), events=events, costs=runtime,
        scoring=upper.scoring, peaks=upper.peaks)
    close(checkpoint, expected)
    assert sha(checkpoint) == r['checkpoint_sha256']
    assert costs['local_pending_peak'] <= 1 and costs['upper_pending'] <= 8 and costs['archive'] <= 16
    if measure: verify_metrics(r, w)


def good(e):
    return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10


def verify_metrics(r, w):
    obs = [logloss(p, row['y']) for p, row in zip(r['predictions'], w['main'])]
    latent = [.9*logloss(p, label(w, row['x'], row['a'], t))+.1*logloss(p, 1-label(w, row['x'], row['a'], t))
              for t, (p, row) in enumerate(zip(r['predictions'], w['main']), 1)]
    j = w['affected']; events = {k: [] for k in ('collapse_reviews', 'recreation_reviews', 'dependency_removals',
        'increases', 'captures', 'retrievals', 'incompatible_archive_reviews')}
    for v in r['reviews']:
        t = v['index']
        if v['local']:
            node = v['local'][j]
            if node['action'] == 'collapsed': events['collapse_reviews'].append(t)
            if len(node['before']['counts']) == 1 and len(node['after']['counts']) == 2: events['recreation_reviews'].append(t)
        u = v['upper']
        if u is not None:
            if u['before']['spec'][j] and not u['after']['spec'][j]: events['dependency_removals'].append(t)
            if u['after']['spec'][j] > u['before']['spec'][j]: events['increases'].append(t)
            if u['captured'] is not None: events['captures'].append(t)
            if u['action'] == 'retrieved': events['retrievals'].append(t)
            if u['archive_check'] is not None and not u['archive_check']['compatible']: events['incompatible_archive_reviews'].append(t)
    endpoints = []
    for e in r['endpoints']:
        expected = [1, 1]
        if e['index'] == 528 and w['branch'] == 'forms': expected[j] = 0
        if e['index'] != 528 and w['branch'] != 'forms': expected[j] = 2
        endpoints.append(good(e) and e['spec'] == expected and e['sufficient_minimal'])
    if w['branch'] == 'forms':
        ops = all(any(241 <= t <= 528 for t in events[k]) for k in ('collapse_reviews', 'dependency_removals')) and all(
            any(t >= 529 for t in events[k]) for k in ('recreation_reviews', 'increases'))
    else: ops = any(241 <= t <= 528 for t in events['captures']) and any(t >= 529 for t in events['increases'])
    expected = dict(transfer_valid=good(r['transfer']), endpoint_valid=endpoints, final_full_valid=good(r['endpoints'][-1]),
        final_minimal_valid=endpoints[-1], operations=ops, trajectory=good(r['transfer']) and all(endpoints) and ops,
        main_observed=mean(obs), main_latent=mean(latent), return_observed=mean(obs[528:656]),
        return_latent=mean(latent[528:656]), hidden_raw_reads=sum(r['raw_reads'][240:528]), all_raw_reads=sum(r['raw_reads']), **events)
    close(r['metrics'], expected)


def verify_summary(runs, saved):
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            ms = [r['metrics'] for r in runs if r['branch'] == b and r['variant'] == v]
            assert len(ms) == 10
            g = dict(branch=b, variant=v, runs=10)
            g.update({k: sum(m[k] for m in ms) for k in ('transfer_valid', 'final_full_valid', 'final_minimal_valid', 'operations', 'trajectory')})
            g['endpoint_passes'] = [sum(m['endpoint_valid'][i] for m in ms) for i in range(3)]
            g.update({k: mean(m[k] for m in ms) for k in ('main_observed', 'main_latent', 'return_observed', 'return_latent', 'hidden_raw_reads', 'all_raw_reads')})
            g.update({k: sum(len(m[k]) for m in ms) for k in ('captures', 'retrievals', 'incompatible_archive_reviews')})
            groups.append(g)
    close(saved['groups'], groups)
    paired = []
    for s, p, b in sorted({(r['seed'], r['proposal_seed'], r['branch']) for r in runs}):
        data = {r['variant']: r['metrics'] for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (s, p, b)}
        paired.append(dict(seed=s, proposal_seed=p, branch=b,
            return_gain=data['delete']['return_observed']-data['integrated']['return_observed'],
            latent_return_gain=data['delete']['return_latent']-data['integrated']['return_latent'],
            hidden_read_saving=data['raw']['hidden_raw_reads']-data['integrated']['hidden_raw_reads']))
    close(saved['paired'], paired)
    checks = {f'{b}_trajectory': next(g['trajectory'] for g in groups if g['branch'] == b and g['variant'] == 'integrated') >= 8 for b in BRANCHES}
    detail = [p for p in paired if p['branch'] == 'detail']; reversed_ = [p for p in paired if p['branch'] == 'reversed']
    checks.update(memory_mean_gain=mean(p['return_gain'] for p in detail) >= .02,
                  memory_pairs=sum(p['return_gain'] > 0 for p in detail) >= 8,
                  reversed_cost=mean(-p['return_gain'] for p in reversed_) <= .02,
                  hidden_read_saving=all(mean(p['hidden_read_saving'] for p in paired if p['branch'] == b) > 0 for b in BRANCHES))
    assert saved['checks'] == checks and saved['primary_pass'] == all(checks.values())


def main():
    start = time.monotonic()
    def timeout(*_): raise TimeoutError('600-second C2 audit limit')
    signal.signal(signal.SIGALRM, timeout); signal.alarm(600)
    manifest = json.loads((OUT/'manifest.json').read_text())
    for name, digest in manifest.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest() == digest, name
    data = json.loads((OUT/'results.json').read_text())
    assert data['hashes'] == manifest and data['status'] == 'completed_pending_audit'
    worlds = json.loads((OUT/'worlds.json').read_text())
    assert len(worlds) == 15
    lookup = {(w['seed'], w['branch']): w for w in worlds}
    assert set(lookup) == set(itertools.product(range(700, 705), BRANCHES))
    for w in worlds:
        assert list(map(len, w['local_main'])) == [256, 256] and len(w['local_selection']) == 4
        assert all(list(map(len, b)) == [32, 32] for b in w['local_selection'])
        assert len(w['composition']) == 256 and len(w['main']) == 768 and list(map(len, w['selection'])) == [32]*12
        verify_world(w)
    with gzip.open(OUT/'runs.jsonl.gz', 'rt') as stream: runs = [json.loads(line) for line in stream]
    assert len(runs) == 120 and {(r['seed'], r['proposal_seed'], r['branch'], r['variant']) for r in runs} == set(
        itertools.product(range(700, 705), (700, 701), BRANCHES, VARIANTS))
    for i, r in enumerate(runs, 1):
        with gzip.open(OUT/r['checkpoint_file'], 'rt') as stream: checkpoint = json.load(stream)
        verify_run(r, lookup[r['seed'], r['branch']], checkpoint)
        assert r['costs']['feedback_labels'] == {'integrated': 4480, 'delete': 4480, 'raw': 1792, 'fixed': 3712}[r['variant']]
        if i % 24 == 0: print(f'{i}/120 C2 full traces and checkpoints verified', flush=True)
    for seed in range(700, 705):
        d, rev = lookup[seed, 'detail'], lookup[seed, 'reversed']
        assert d['main'][:528] == rev['main'][:528] and d['selection'][:8] == rev['selection'][:8]
        for ps in (700, 701):
            rs = [r for r in runs if (r['seed'], r['proposal_seed']) == (seed, ps)]
            assert all(r['warmup'] == rs[0]['warmup'] for r in rs)
    verify_summary(runs, data['summary'])
    totals = dict(runs=120, allocated_labels=120*4480, generated_labels=15*4480,
        used_labels=sum(r['costs']['feedback_labels'] for r in runs),
        candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
        scoring_queries=sum(r['costs']['scoring_queries'] for r in runs), composite_predictions=120*768,
        local_predictions=90*768*2, evaluation_predictions=120*(24+15*32))
    close(data['totals'], totals)
    assert totals['used_labels'] == 433920 and totals['candidate_fits'] <= 17160 and totals['scoring_queries'] <= 3000000
    assert data['elapsed_seconds'] < 600
    fixture = json.loads((ROOT/'results/structural-consolidation-fixtures.json').read_text())
    assert fixture['status'] == 'pass' and fixture['charged_labels'] <= 720 and 19216+fixture['charged_labels'] <= 20000
    result = dict(status='pass', runs=120, independently_replayed_labels=433920, elapsed_seconds=time.monotonic()-start,
                  result_sha256=hashlib.sha256((OUT/'results.json').read_bytes()).hexdigest(),
                  runs_sha256=hashlib.sha256((OUT/'runs.jsonl.gz').read_bytes()).hexdigest(),
                  worlds_sha256=hashlib.sha256((OUT/'worlds.json').read_bytes()).hexdigest())
    signal.alarm(0)
    (OUT/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: 120 C2 runs independently reconstructed, including structural choices, archive provenance, checkpoints, metrics and costs.')


if __name__ == '__main__': main()
