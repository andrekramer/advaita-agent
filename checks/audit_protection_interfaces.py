"""Independent C1 stream/arithmetic/state audit. No experiment or learner imports."""
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

from audit_nested_abstractions import (ReplayNode, close, local_loss, local_p, exported,
    upper_table, upper_state, probability, verify_upper, verify_eval, good, logloss, CONTEXTS)
from audit_reclosure import verify_reclosure

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/protection-interfaces-v1'
BRANCHES = ('persistent', 'remap', 'burst')
VARIANTS = ('immediate_opening', 'immediate_reclosure', 'earned_opening', 'earned_reclosure')


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def sha(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def truth(w, t, observed=False):
    out = copy.deepcopy(w['forms'])
    if (w['branch'] == 'remap' and t >= 129) or (observed and w['branch'] == 'burst' and 129 <= t <= 192):
        j = w['affected']
        for x in w['representatives'][j]:
            out[j][x] = 1-out[j][x]
    return out


def effective(w, t):
    return dict(w, branch='remap' if w['branch'] == 'remap' and t > 128 else 'persistent')


def verify_world(w, review_every=64):
    rng = random.Random(81000+w['seed'])
    f, reps = [], []
    for _ in range(2):
        order = list(range(4))
        rng.shuffle(order)
        f.append([int(x in order[2:]) for x in range(4)])
        reps.append([order[0], order[2]])
    assert (w['forms'], w['representatives'], w['affected']) == (f, reps, rng.randrange(2))
    inputs, noise = random.Random(82000+w['seed']), random.Random(83000+w['seed'])
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
                y = (true[0][l]+true[1][r]+a+(noise.random() < .1)) % 2
                rows.append(dict(x=[l, r], a=a, local=local, y=y))
        return rows
    assert w['main'] == joint(len(w['main']))
    for i, batch in enumerate(w['selection'], 1):
        assert batch == joint(len(batch), i*review_every)


def unpack(s):
    return tuple(s['partition']), {int(k): v.copy() for k, v in s['counts'].items()}


class Node(ReplayNode):
    def __init__(self, seed, protected):
        super().__init__(seed)
        self.protected = protected
        self.policy = dict(established=False, adequate=0, pending=None)
        self.pcosts = dict(pending_predictions=0, pending_starts=0, pending_failures=0,
                          confirmed_replacements=0, immediate_replacements=0, establishments=0, max_pending_cells=0)
        self.revision = 0

    def update(self, row):
        before = self.state()['groups']
        super().update(row)
        self.revision += before != self.state()['groups']

    def review(self, saved, batch):
        before_state = self.state()
        ordinary = saved['ordinary'] if self.protected else saved
        super().review(ordinary, batch)
        if self.protected:
            proposed = ordinary['candidates'][ordinary['winner']]['state']
            old = local_loss(*unpack(before_state), batch)
            new = local_loss(*unpack(proposed), batch)
            before = copy.deepcopy(self.policy)
            chosen, accepted, action, pending_loss = before_state, False, 'keep', None
            if self.policy['pending'] is not None:
                pending_loss = local_loss(*unpack(self.policy['pending']), batch)
                self.pcosts['pending_predictions'] += len(batch)
                if old-pending_loss > .005:
                    chosen, accepted, action = copy.deepcopy(self.policy['pending']), True, 'confirmed'
                    self.pcosts['confirmed_replacements'] += 1
                else:
                    action = 'pending_failed'
                    self.pcosts['pending_failures'] += 1
                self.policy['pending'] = None
            elif old-new > .005:
                if self.policy['established']:
                    self.policy['pending'] = copy.deepcopy(proposed)
                    action = 'pending_started'
                    self.pcosts['pending_starts'] += 1
                    self.pcosts['max_pending_cells'] = max(self.pcosts['max_pending_cells'], len(proposed['counts']))
                else:
                    chosen, accepted, action = proposed, True, 'immediate'
                    self.pcosts['immediate_replacements'] += 1
            if accepted:
                self.policy.update(established=False, adequate=0)
            else:
                self.policy['adequate'] = min(2, self.policy['adequate']+1) if old <= .55 else 0
                if self.policy['adequate'] == 2 and not self.policy['established']:
                    self.policy['established'] = True
                    self.pcosts['establishments'] += 1
            close(saved['policy'], dict(before=before, after=self.policy, action=action,
                                        accepted=accepted, pending_loss=pending_loss))
            self.partition, self.table = unpack(chosen)
            close(saved['after'], self.state())
        self.revision += before_state['groups'] != self.state()['groups']


def binding(mode, nodes):
    ports = [dict(name='action', domain=[0, 1], meaning=[0, 1])]
    for j, n in enumerate(nodes):
        raw = mode == f'fine{j}'
        ports.append(dict(name=f'node{j}.raw' if raw else f'node{j}.group',
                          domain=list(range(4 if raw else 2)),
                          meaning=list(range(4)) if raw else n.state()['groups']))
    return sha(sorted(ports, key=lambda p: p['name']))


def verify_run(r, w, checkpoint, review_every=64, measure=True):
    protected = r['variant'].startswith('earned')
    reclose = r['variant'].endswith('reclosure')
    seeds = [84000+2*r['proposal_seed']+j for j in range(2)]
    nodes = [Node(s, protected) for s in seeds]
    ids, main, selection, uses, events = [[], []], set(), set(), [], []
    def fit(records, operation):
        assert set(records) <= main and not set(records) & selection
        uses.append(dict(kind='fit', operation=operation, ids=records.copy()))
    def select(records, operation):
        assert not set(records) & main
        assert not any(u['kind'] == 'selection' and u['operation'] == operation and set(records) & set(u['ids']) for u in uses)
        uses.append(dict(kind='selection', operation=operation, ids=records.copy(), reused=sorted(set(records) & selection)))
        selection.update(records)
    def update(j, identity, row):
        assert identity not in main | selection
        main.add(identity)
        nodes[j].update(row)
        ids[j] = (ids[j]+[identity])[-192:]
        fit(ids[j], f'local{j}.refit')
    scoring = 0
    def review(j, records, batch, saved):
        nonlocal scoring
        scoring += 4*min(64, len(nodes[j].buffer))+2*len(batch)
        fit(ids[j], f'local{j}.proposals')
        select(records, f'local{j}.replacement')
        if protected:
            select(records, f'local{j}.retention')
        nodes[j].review(saved, batch)
        events.append(dict(operation='local_review', node=j, ids=records, detail=saved))
    for i in range(len(w['local_main'][0])):
        for j in range(2):
            update(j, f'warm/{j}/{i}', w['local_main'][j][i])
        if (i+1) % review_every == 0:
            for j in range(2):
                batch = w['local_selection'][i//review_every][j]
                review(j, [f'warm-select/{j}/{i}/{k}' for k in range(len(batch))], batch, r['warmup'][i//review_every][j])
    mode, counts = 'coarse', upper_table('coarse', w['composition'], nodes)
    initial = upper_state(mode, counts)
    close(r['initial_upper'], initial)
    records = [f'composition/{i}' for i in range(len(w['composition']))]
    main.update(records)
    fit(records, 'upper.initialise')
    events.append(dict(operation='upper_initialise', ids=records, after=initial))
    buffer, buffer_ids = w['composition'][-192:], records[-192:]
    bound = binding(mode, nodes)
    verify_eval(r['transfer'], mode, counts, nodes, effective(w, 0), False)
    pcosts = dict(challenger_predictions=0, challenger_starts=0, group_invalidations=0,
                  failed_witnesses=0, accepted_reclosures=0, max_pending_cells=0)
    runtime_costs = dict(main_predictions=0, raw_reads=0, upper_refits=0,
                         upper_refit_rows=0, upper_candidate_fits=0, upper_candidate_rows=0)
    pending = None
    n = len(w['main'])
    assert all(len(r[k]) == n for k in ('predictions', 'local_predictions', 'raw_reads', 'pre_modes', 'pre_local_exact'))
    assert len(r['reviews']) == n//review_every
    for t, row in enumerate(w['main'], 1):
        p = probability(mode, counts, nodes, row['x'], row['a'])
        close(r['predictions'][t-1], p)
        close(r['local_predictions'][t-1], [local_p(n.partition, n.table, row['x'][j]) for j, n in enumerate(nodes)])
        assert r['pre_modes'][t-1] == mode
        assert r['pre_local_exact'][t-1] == [n.state()['groups'] == f for n, f in zip(nodes, truth(w, t))]
        raw = int(mode != 'coarse')
        assert r['raw_reads'][t-1] == raw
        runtime_costs['main_predictions'] += 1
        runtime_costs['raw_reads'] += raw
        for j in range(2):
            update(j, f'main/{t}/local{j}', dict(x=row['x'][j], y=row['local'][j]))
        record = f'main/{t}/upper'
        assert record not in main | selection
        main.add(record)
        buffer = (buffer+[row])[-192:]
        buffer_ids = (buffer_ids+[record])[-192:]
        if mode != 'coarse':
            fit(buffer_ids, 'upper.refit')
            counts = upper_table(mode, buffer, nodes)
            bound = binding(mode, nodes)
            runtime_costs['upper_refits'] += 1
            runtime_costs['upper_refit_rows'] += len(buffer)
        # Use saved prediction bits after checking arithmetic, for checkpoint hashing.
        events.append(dict(operation='main', id=f'main/{t}', prediction=r['predictions'][t-1], raw_reads=raw))
        if t % review_every:
            continue
        rev, batch = r['reviews'][t//review_every-1], w['selection'][t//review_every-1]
        assert rev['index'] == t
        for j in range(2):
            review(j, [f'select/{t}/{i}/local{j}' for i in range(len(batch))],
                   [dict(x=z['x'][j], y=z['local'][j]) for z in batch], rev['local'][j])
        records = [f'select/{t}/{i}/upper' for i in range(len(batch))]
        fit(buffer_ids, 'upper.proposals')
        select(records, 'upper.replacement')
        mode, counts = verify_upper(rev['ordinary'], mode, counts, nodes, buffer, batch)
        if rev['ordinary']['accepted']:
            bound = binding(mode, nodes)
        runtime_costs['upper_candidate_fits'] += 3
        runtime_costs['upper_candidate_rows'] += 3*len(buffer)
        scoring += 3*len(buffer)+2*len(batch)
        if reclose:
            select(records, 'upper.reclosure')
            mode, counts, pending = verify_reclosure(rev['reclosure'], rev['ordinary'], mode, counts,
                                                     pending, nodes, buffer, batch, pcosts)
            if rev['reclosure']['action'] == 'reclosed':
                bound = binding(mode, nodes)
        else:
            assert 'reclosure' not in rev
        close(rev['upper_after'], upper_state(mode, counts))
        verify_eval(rev['evaluation'], mode, counts, nodes, effective(w, t), True)
        events.append(dict(operation='upper_review', ids=records,
            detail={k: v for k, v in rev.items() if k not in ('index', 'evaluation')},
            stale_binding=bound != binding(mode, nodes)))
    costs = {k: sum(n.costs[k] for n in nodes) for k in nodes[0].costs}
    costs.update(runtime_costs)
    costs.update(feedback_labels=len(main)+len(selection), reclosure=pcosts,
                 local_retention=[n.pcosts if protected else None for n in nodes],
                 scoring_queries=scoring+pcosts['challenger_predictions']+sum(n.pcosts['pending_predictions'] for n in nodes))
    close(r['costs'], costs)
    close(r['final_upper'], upper_state(mode, counts))
    close(r['final_local'], [n.state() for n in nodes])
    close(r['pending'], pending)
    close(r['local_policies'], [n.policy if protected else None for n in nodes])
    ledger = dict(main=sorted(main), selection=sorted(selection), uses=uses)
    assert r['ledger_sha256'] == sha(ledger)
    assert r['evidence'] == dict(main=len(main), selection=len(selection),
        reused=sum(len(u.get('reused', [])) for u in uses), events=len(events))
    node_states = []
    for node in nodes:
        state = dict(model=node.state(), buffer=node.buffer, deck=node.deck,
                     rng=node.random.getstate(), costs=node.costs)
        if protected:
            state.update(policy=node.policy, policy_costs=node.pcosts)
        node_states.append(state)
    expected = dict(schema=1, seeds=seeds, local_policy='earned' if protected else 'immediate', reclose=reclose,
        nodes=node_states, local_ids=ids, revisions=[n.revision for n in nodes], upper=upper_state(mode, counts),
        upper_binding=bound, buffer=buffer, buffer_ids=buffer_ids, pending=pending, reclosure_costs=pcosts,
        ledger=ledger, events=events, costs=runtime_costs)
    close(checkpoint, expected)
    assert r['checkpoint_sha256'] == sha(checkpoint)
    assert max(n.pcosts['max_pending_cells'] for n in nodes) <= 2 and pcosts['max_pending_cells'] <= 8
    if measure:
        verify_metrics(r, w)


def verify_metrics(r, w):
    expected = {}
    traces = dict(observed=[], latent=[], local_observed=[[], []], local_latent=[[], []])
    for t, row in enumerate(w['main'], 1):
        f = truth(w, t)
        bits = [f[j][row['x'][j]] for j in range(2)]
        p = r['predictions'][t-1]
        y = (sum(bits)+row['a']) % 2
        traces['observed'].append(logloss(p, row['y']))
        traces['latent'].append(.9*logloss(p, y)+.1*logloss(p, 1-y))
        for j, prob in enumerate(r['local_predictions'][t-1]):
            traces['local_observed'][j].append(logloss(prob, row['local'][j]))
            traces['local_latent'][j].append(.9*logloss(prob, bits[j])+.1*logloss(prob, 1-bits[j]))
    for label, bounds in (('main', (0, 512)), ('change', (128, 512)), ('burst', (128, 320))):
        a, b = bounds
        for kind in ('observed', 'latent'):
            expected[f'{label}_{kind}'] = mean(traces[kind][a:b])
            expected[f'{label}_local_{kind}'] = [mean(x[a:b]) for x in traces[f'local_{kind}']]
        expected[f'{label}_affected_latent'] = expected[f'{label}_local_latent'][w['affected']]
    final = r['reviews'][-1]['evaluation']
    expected.update(transfer_valid=good(r['transfer']), final_valid=good(final),
        final_predictive_valid=final['accuracy'] == 1 and final['regret'] <= .10,
        final_local_valid=all(final['local_exact']), coarse_final_valid=good(final) and final['mode'] == 'coarse',
        invalid_affected_checkpoints=sum(v['index'] > 128 and not v['evaluation']['local_exact'][w['affected']] for v in r['reviews']),
        invalid_local_checkpoints=sum(v['evaluation']['local_exact'].count(False) for v in r['reviews']),
        raw_reads=sum(r['raw_reads']), exposed_records=sum(x != 'coarse' for x in r['pre_modes']),
        bypass_wrong_records=sum(x == f"fine{w['affected']}" and not exact[w['affected']]
                                  for x, exact in zip(r['pre_modes'], r['pre_local_exact'])))
    threshold = 128 if w['branch'] == 'remap' else 192 if w['branch'] == 'burst' else 0
    eligible = [v for v in r['reviews'] if v['index'] > threshold]
    valid_indices = [v['index'] for v in eligible if good(v['evaluation'])]
    pairs = [(a['index'], b['index']) for a, b in zip(eligible, eligible[1:]) if good(a['evaluation']) and good(b['evaluation'])]
    expected.update(first_valid=valid_indices[0] if valid_indices else None,
        first_confirmed_pair_start=pairs[0][0] if pairs else None,
        confirmation=pairs[0][1] if pairs else None, confirmation_censored=pairs[0][1] if pairs else 576)
    openings, hides, closures, intervals = [], [], [], []
    for v in r['reviews']:
        old, new = v['ordinary']['before']['mode'], v['upper_after']['mode']
        if old == 'coarse' and new != 'coarse':
            openings.append(v['index'])
            intervals.append(dict(opened=v['index'], hidden=None, latency=None))
        if old != 'coarse' and new == 'coarse':
            hides.append(v['index'])
            assert intervals and intervals[-1]['hidden'] is None
            intervals[-1].update(hidden=v['index'], latency=v['index']-intervals[-1]['opened'])
        if v.get('reclosure', {}).get('action') == 'reclosed':
            closures.append(v['index'])
    expected.update(reopen_reviews=openings, hide_reviews=hides, reclosure_reviews=closures, reclosure_latencies=intervals)
    close(r['metrics'], expected)


def verify_summary(runs, saved):
    groups = []
    fields = ('main_observed', 'main_latent', 'main_affected_latent', 'change_observed', 'change_latent',
              'change_affected_latent', 'burst_latent', 'burst_affected_latent', 'confirmation_censored',
              'raw_reads', 'bypass_wrong_records')
    for b in BRANCHES:
        for v in VARIANTS:
            ms = [r['metrics'] for r in runs if r['branch'] == b and r['variant'] == v]
            assert len(ms) == 10
            g = dict(branch=b, variant=v, runs=10)
            for f in ('transfer_valid', 'final_valid', 'final_predictive_valid', 'final_local_valid', 'coarse_final_valid'):
                g[f] = sum(m[f] for m in ms)
            g.update({f: mean(m[f] for m in ms) for f in fields})
            g.update(invalid_affected_checkpoints=sum(m['invalid_affected_checkpoints'] for m in ms),
                     reopenings=sum(len(m['reopen_reviews']) for m in ms), reclosures=sum(len(m['reclosure_reviews']) for m in ms))
            groups.append(g)
    close(saved['groups'], groups)
    lookup = {(g['branch'], g['variant']): g for g in groups}
    pairs, interactions = [], []
    difference_fields = fields[:-1]+('invalid_affected_checkpoints',)
    for seed, ps, b in sorted({(r['seed'], r['proposal_seed'], r['branch']) for r in runs}):
        ms = {r['variant']: r['metrics'] for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (seed, ps, b)}
        for axis, setting, av, cv in (
            ('protection', 'opening', 'earned_opening', 'immediate_opening'),
            ('protection', 'reclosure', 'earned_reclosure', 'immediate_reclosure'),
            ('reclosure', 'immediate', 'immediate_reclosure', 'immediate_opening'),
            ('reclosure', 'earned', 'earned_reclosure', 'earned_opening')):
            pairs.append(dict(seed=seed, proposal_seed=ps, branch=b, axis=axis, setting=setting,
                              differences={f: ms[av][f]-ms[cv][f] for f in difference_fields}))
        interactions.append(dict(seed=seed, proposal_seed=ps, branch=b, differences={
            f: ms['earned_reclosure'][f]+ms['immediate_opening'][f]-ms['earned_opening'][f]-ms['immediate_reclosure'][f]
            for f in ('main_latent', 'raw_reads', 'invalid_affected_checkpoints')}))
    close(saved['paired'], pairs)
    close(saved['interactions'], interactions)
    checks = {}
    for upper in ('opening', 'reclosure'):
        def difference(b, field):
            return lookup[b, 'earned_'+upper][field]-lookup[b, 'immediate_'+upper][field]
        control = lookup['burst', 'immediate_'+upper]['invalid_affected_checkpoints']
        earned = lookup['burst', 'earned_'+upper]['invalid_affected_checkpoints']
        checks[upper] = dict(
            endpoint_validity=all(lookup[b, local+'_'+upper][field] >= 8 for b in BRANCHES
                for local in ('immediate', 'earned') for field in ('transfer_valid', 'final_valid')),
            persistent_loss=max(difference('persistent', f) for f in ('main_observed', 'main_latent', 'main_affected_latent')) <= .02,
            remap_loss=max(difference('remap', f) for f in ('change_observed', 'change_latent', 'change_affected_latent')) <= .05,
            remap_delay=difference('remap', 'confirmation_censored') <= 64,
            burst_loss=max(difference('burst', f) for f in ('burst_latent', 'burst_affected_latent')) <= .02,
            protection=control > 0 and earned <= .75*control and sum(
                p['differences']['invalid_affected_checkpoints'] < 0 for p in pairs
                if p['axis'] == 'protection' and p['branch'] == 'burst' and p['setting'] == upper) >= 2)
    close(saved['checks'], checks)
    assert saved['primary_pass'] == all(all(v.values()) for v in checks.values())
    gate = {b: min(lookup[b, 'immediate_reclosure']['transfer_valid'], lookup[b, 'immediate_reclosure']['final_valid']) >= 8 for b in BRANCHES}
    assert saved['progression_checks'] == gate and saved['progression_gate'] == all(gate.values())


def main():
    started = time.monotonic()
    def timeout(*_):
        raise TimeoutError('600-second audit limit')
    signal.signal(signal.SIGALRM, timeout)
    signal.alarm(600)
    manifest = json.loads((OUT/'manifest.json').read_text())
    for path, expected in manifest.items():
        assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest() == expected, path
    data = json.loads((OUT/'results.json').read_text())
    assert data['hashes'] == manifest and data['status'] == 'completed_pending_audit'
    with gzip.open(OUT/'runs.jsonl.gz', 'rt') as stream:
        runs = [json.loads(line) for line in stream]
    worlds = {(w['seed'], w['branch']): w for w in data['worlds']}
    assert len(worlds) == len(data['worlds']) == 15
    assert set(worlds) == set(itertools.product(range(600, 605), BRANCHES))
    for w in worlds.values():
        assert [len(rows) for rows in w['local_main']] == [256, 256]
        assert len(w['local_selection']) == 4 and all(list(map(len, b)) == [32, 32] for b in w['local_selection'])
        assert len(w['composition']) == 256 and len(w['main']) == 512 and len(w['selection']) == 8
        assert all(len(b) == 32 for b in w['selection'])
        verify_world(w)
    assert len(runs) == 120
    assert {(r['seed'], r['proposal_seed'], r['branch'], r['variant']) for r in runs} == set(
        itertools.product(range(600, 605), (600, 601), BRANCHES, VARIANTS))
    for i, r in enumerate(runs, 1):
        with gzip.open(OUT/r['checkpoint_file'], 'rt') as stream:
            checkpoint = json.load(stream)
        verify_run(r, worlds[r['seed'], r['branch']], checkpoint)
        if i % 24 == 0:
            print(f'{i}/120 traces and checkpoints independently verified', flush=True)
    for seed in range(600, 605):
        for ps in (600, 601):
            for local in ('immediate', 'earned'):
                rs = [r for r in runs if r['seed'] == seed and r['proposal_seed'] == ps and r['variant'].startswith(local)]
                assert all(r['warmup'] == rs[0]['warmup'] and r['transfer'] == rs[0]['transfer'] for r in rs)
            for b in BRANCHES:
                for local in ('immediate', 'earned'):
                    rs = [r for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (seed, ps, b) and r['variant'].startswith(local)]
                    assert [v['local'] for v in rs[0]['reviews']] == [v['local'] for v in rs[1]['reviews']]
    verify_summary(runs, data['summary'])
    totals = dict(runs=120, generated_labels=sum(2*256+4*64+256+3*(512+8*32) for _ in worlds),
        allocated_labels=120*3328, used_labels=sum(r['costs']['feedback_labels'] for r in runs),
        candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
        scoring_queries=sum(r['costs']['scoring_queries'] for r in runs), composite_predictions=120*512,
        local_predictions=120*1024, evaluation_predictions=120*(24+8*32))
    close(data['totals'], totals)
    assert totals['used_labels'] == 399360 and totals['candidate_fits'] == 14400 and totals['scoring_queries'] <= 1700000
    assert data['elapsed_seconds'] < 600
    fixture = json.loads((ROOT/'results/protection-interfaces-fixtures.json').read_text())
    assert fixture['status'] == 'pass' and fixture['charged_labels'] <= 336 and 18880+fixture['charged_labels'] <= 20000
    result = dict(status='pass', runs=120, independently_replayed_labels=399360,
                  elapsed_seconds=time.monotonic()-started, progression_gate=data['summary']['progression_gate'],
                  result_sha256=hashlib.sha256((OUT/'results.json').read_bytes()).hexdigest(),
                  runs_sha256=hashlib.sha256((OUT/'runs.jsonl.gz').read_bytes()).hexdigest())
    signal.alarm(0)
    (OUT/'audit.json').write_text(json.dumps(result, indent=2)+'\n')
    print('PASS: all 120 streams, full decision traces, checkpoint/ledger states, metrics, costs and frozen dependencies verified.')


if __name__ == '__main__':
    main()
