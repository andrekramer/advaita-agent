"""Independent explicit-role reconstruction; no runtime/experiment imports."""
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
from roles_reference import Local, Upper, fit, predict, ports, fingerprint

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/structural-consolidation-v1'
BRANCHES = ('forms', 'detail', 'reversed')
VARIANTS = ('integrated', 'delete', 'raw', 'fixed')


def truth(w, t, observed=False):
    f = copy.deepcopy(w['forms'])
    if w['branch'] == 'forms' and 241 <= t <= 528:
        f[w['affected']] = [0]*4
    if observed and w['branch'] == 'probability' and 241 <= t <= 528:
        f[w['affected']] = [1-v for v in f[w['affected']]]
    return f


def label(w, x, a, t):
    f = truth(w, t)
    result = (f[0][x[0]]+f[1][x[1]]+a) % 2
    if w['branch'] in ('detail', 'reversed') and t != 0 and not 241 <= t <= 528:
        j = w['affected']
        result = (result+int(x[j] != w['representatives'][j][f[j][x[j]]])) % 2
        if w['branch'] == 'reversed' and t > 528: result = 1-result
    if w['branch'] == 'probability' and 241 <= t <= 528: result = 1-result
    return result


def verify_world(w, review_every=64):
    rng = random.Random(151000+w['seed'])
    f, reps = [], []
    for _ in range(2):
        order = list(range(4))
        rng.shuffle(order)
        f.append([int(x in order[2:]) for x in range(4)])
        reps.append([order[0], order[2]])
    assert (w['forms'], w['representatives'], w['affected']) == (f, reps, rng.randrange(2))
    inputs = random.Random(152000+w['seed'])
    noise = [random.Random(base+w['seed']) for base in (153000,154000,155000)]
    def local(n, j):
        rows = []
        for start in range(0, n, 4):
            block = list(range(4))
            inputs.shuffle(block)
            rows += [dict(x=x, y=(f[j][x]+(noise[j].random() < .1)) % 2) for x in block[:n-start]]
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
            training.append(dict(x=[l, r], a=a, y=(f[0][l]+f[1][r]+a+(noise[2].random() < .1)) % 2))
    assert w['composition'] == training
    def joint(n, when=None):
        rows = []
        for start in range(0, n, 32):
            block = CONTEXTS.copy()
            inputs.shuffle(block)
            for l, r, a in block[:n-start]:
                t = len(rows)+1 if when is None else when
                true, obs = truth(w, t), truth(w, t, True)
                local = [(obs[j][x]+(noise[j].random() < .1)) % 2 for j, x in enumerate((l, r))]
                y = (label(w, [l, r], a, t)+(noise[2].random() < .1)) % 2
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
    policy = r['policy']
    period = review_every if policy in ('B64','U64') else 2*review_every
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
    for j,n in enumerate(nodes):
        n.structural = True
        n.groups = n.state()['groups']
        n.stable = policy in ('R128','H128')
        n.history_node, n.history_enabled = j, policy == 'H128'
    upper.history_enabled = policy == 'H128'
    history, hcost = [], dict(feature_predictions=0, proposal_rows=0, records=0)
    events.append(dict(operation='upper_initialise', ids=records, after=model))
    buffer, buffer_ids = w['composition'][-192:], records[-192:]
    verify_eval(r['transfer'], upper.model, nodes, w, 0, True)
    runtime = dict(main_predictions=0, raw_reads=0, upper_refits=0, upper_refit_rows=0, upper_candidate_fits=0, upper_candidate_rows=0)
    assert all(len(r[k]) == len(w['main']) for k in ('predictions', 'raw_reads', 'local_predictions'))
    assert len(r['reviews']) == len(w['main'])//period
    assert len(r['evaluations']) == len(w['main'])//review_every
    endpoint = 0
    for t, row in enumerate(w['main'], 1):
        before_nodes = [n.state() for n in nodes]
        before_spec = upper.model['spec'].copy()
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
        if 2 in upper.model['spec'] or policy in ('U64','U128','R128','H128'):
            use(buffer_ids, 'upper.refit', 'fit')
            upper.deploy(fit(upper.model['spec'], buffer, nodes), ports(upper.model['spec'], nodes), buffer_ids)
            runtime['upper_refits'] += 1; runtime['upper_refit_rows'] += len(buffer)
        if policy == 'H128':
            history = (history+[dict(id=f'main/{t}', x=row['x'], a=row['a'],
                before=r['local_predictions'][t-1]+[p],
                after=[local_p(n.partition,n.table,row['x'][j]) for j,n in enumerate(nodes)]+[predict(upper.model,nodes,row['x'],row['a'])],
                outcomes=row['local']+[row['y']], groups=[n.state()['groups'] for n in nodes])])[-192:]
            hcost['records'] += 1; hcost['feature_predictions'] += 5
            upper.history = history
            for n in nodes: n.history = history
        events.append(dict(operation='main', id=f'main/{t}', prediction=r['predictions'][t-1], raw_reads=raw))
        if t % period == 0:
            rev, batch = r['reviews'][t//period-1], w['selection'][t//review_every-1]
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
        if t % review_every == 0:
            verify_eval(r['evaluations'][t//review_every-1], upper.model, nodes, w, t)
        close(r['diagnostics'][t-1],dict(
            group_changes=[a['groups']!=n.state()['groups'] for a,n in zip(before_nodes,nodes)],
            partition_changes=[not same_partition(a['partition'],n.partition) for a,n in zip(before_nodes,nodes)],
            raw_bypass=sum(before_spec[j]==2 and not same_partition(before_nodes[j]['partition'],truth(w,t)[j]) for j in range(2))))
        if t in (240, 528):
            verify_eval(r['endpoints'][endpoint], upper.model, nodes, w, t); endpoint += 1
    assert len(r['endpoints']) == endpoint
    runtime['upper_candidate_fits'], runtime['upper_candidate_rows'] = upper.fits, upper.fitrows
    costs = {k: sum(n.costs[k] for n in nodes) for k in nodes[0].costs}; costs.update(runtime)
    costs.update(feedback_labels=len(main)+len(selection), scoring_queries=upper.scoring+sum(n.queries for n in nodes)+hcost['feature_predictions'],
                 history_rows=upper.history_rows+sum(n.history_rows for n in nodes),
                 history_feature_predictions=hcost['feature_predictions'],
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
    hcost['proposal_rows'] = upper.history_rows
    expected = dict(schema=24, core=expected, policy=policy, stable=[n.stable for n in nodes],
        history=history, history_costs=hcost, local_history_rows=[n.history_rows for n in nodes])
    close(checkpoint, expected)
    assert sha(checkpoint) == r['checkpoint_sha256']
    assert costs['local_pending_peak'] <= 1 and costs['upper_pending'] <= 8 and costs['archive'] <= 16
    if measure: verify_metrics(r, w)



def good(e): return min(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10


def verify_metrics(r,w):
    values={'observed':[], 'latent':[]}; local=[[],[]]
    for index,row in enumerate(w['main']):
        p=r['predictions'][index]; y=label(w,row['x'],row['a'],index+1)
        values['observed'].append(logloss(p,row['y']))
        values['latent'].append(.9*logloss(p,y)+.1*logloss(p,1-y))
        for j in (0,1): local[j].append(logloss(r['local_predictions'][index][j],row['local'][j]))
    ranges=[('whole',0,1280),('adapt1',240,496),('adapt2',528,784),('late',1024,1280)]
    m={k:{name:sum(xs[a:b])/len(xs[a:b]) for name,a,b in ranges} for k,xs in values.items()}
    evaluations=r['evaluations']; late=[e for e in evaluations if e['index']>=1024]
    m.update(transfer_valid=bool(good(r['transfer'])),final_valid=bool(good(evaluations[-1])),
        structure_errors=sum(not (all(e['local_exact']) and e['sufficient_minimal']) for e in evaluations if e['index']>=256),
        local_observed=[sum(xs)/len(xs) for xs in local],
        late_prediction_stable=all(good(e) for e in late),
        late_structure_stable=all(all(e['local_exact']) and e['sufficient_minimal'] for e in late),
        raw_reads=sum(r['raw_reads']),raw_bypass=sum(d['raw_bypass'] for d in r['diagnostics']),
        group_changes=sum(sum(d['group_changes']) for d in r['diagnostics']),
        partition_changes=sum(sum(d['partition_changes']) for d in r['diagnostics']),
        retrievals=len([v for v in r['reviews'] if v['upper']['action']=='retrieved']),
        incompatible_archive=len([v for v in r['reviews'] if v['upper']['archive_check'] and not v['upper']['archive_check']['compatible']]),recovery=[])
    for low,high in ((256,512),(576,1280)):
        streak=0; confirmation=None
        for e in evaluations:
            if not low<=e['index']<=high: continue
            streak=streak+1 if good(e) else 0
            if streak==2: confirmation=e['index']; break
        m['recovery'].append(confirmation)
    close(r['metrics'],m)


def verify_summary(runs,saved,candidate='R128',confirmation=False):
    branches=('stable','probability','forms','detail','reversed')
    pairs=sorted(set((r['seed'],r['proposal_seed']) for r in runs))
    policies=sorted(set(r['policy'] for r in runs)); windows=('whole','adapt1','adapt2','late')
    lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs}
    groups=[]
    for h in branches:
        for policy in policies:
            ms=[lookup[s,p,h,policy] for s,p in pairs]
            g=dict(branch=h,policy=policy,runs=len(ms))
            for field in ('transfer_valid','final_valid','late_prediction_stable','late_structure_stable'): g[field]=sum(m[field] for m in ms)
            for field in ('structure_errors','raw_reads','raw_bypass','group_changes','partition_changes','retrievals','incompatible_archive'): g[field]=sum(m[field] for m in ms)/len(ms)
            for field in ('observed','latent'): g[field]={k:sum(m[field][k] for m in ms)/len(ms) for k in windows}
            g['recovery_censored']=[len([m for m in ms if m['recovery'][i] is None]) for i in (0,1)]
            groups.append(g)
    close(saved['groups'],groups)
    contrasts=[(candidate,'U128')] if confirmation else [('B128','B64'),('U64','B64'),('U128','B128'),('U128','U64'),('R128','U128'),('H128','R128'),('R128','B64'),('H128','B64'),('H128','U128')]
    paired=[]
    for a,b in contrasts:
        for s,p in pairs:
            for h in branches:
                x=lookup[s,p,h,a];y=lookup[s,p,h,b]
                row=dict(candidate=a,control=b,seed=s,proposal_seed=p,branch=h,
                    observed_cost={k:x['observed'][k]-y['observed'][k] for k in windows},
                    latent_cost={k:x['latent'][k]-y['latent'][k] for k in windows},
                    recovery_delay=[],representation_gain=y['structure_errors']-x['structure_errors'])
                for i,cap in enumerate((592,1344)):
                    tx=cap if x['recovery'][i] is None else x['recovery'][i]
                    ty=cap if y['recovery'][i] is None else y['recovery'][i]
                    row['recovery_delay'].append(tx-ty)
                paired.append(row)
    close(saved['paired'],paired)
    def validity(ps):
        return all(g['transfer_valid']>=8 and g['final_valid']>=8 for g in groups if g['policy'] in ps)
    def guards(p,cs):
        flags=dict(mean_cost=True,recovery=True,worst_pair=True)
        for c in cs:
            for h in branches:
                rows=[r for r in paired if r['candidate']==p and r['control']==c and r['branch']==h]
                assert len(rows)==10
                for field in ('observed_cost','latent_cost'):
                    for k in ('whole','adapt1','adapt2'):
                        if sum(r[field][k] for r in rows)/10>.02: flags['mean_cost']=False
                for i in (0,1):
                    if sum(r['recovery_delay'][i] for r in rows)/10>64: flags['recovery']=False
                if any(r['observed_cost'][k]>.10 for r in rows for k in ('adapt1','adapt2')): flags['worst_pair']=False
        return flags
    representation=[]
    for s,p in pairs:
        ref=sum(lookup[s,p,h,'U128']['structure_errors'] for h in ('forms','detail'))
        test=sum(lookup[s,p,h,candidate]['structure_errors'] for h in ('forms','detail'))
        representation.append(dict(seed=s,proposal_seed=p,control_errors=ref,candidate_errors=test,gain=ref-test))
    close(saved['representation_pairs'],representation)
    total=sum(r['control_errors'] for r in representation); gain=sum(r['gain'] for r in representation)
    close(saved['representation_fraction'],gain/total if total else None)
    flags=dict(representation_reduction=bool(total and gain/total>=.25),
        representation_pairs=len([r for r in representation if r['gain']>0])>=8,
        validity=validity([candidate,'U128']),**guards(candidate,['U128'] if confirmation else ['U128','B64']))
    close(saved['checks'],flags); assert saved['primary_pass']==all(flags.values())
    history=[]; hflags=None
    if not confirmation:
        for s,p in pairs:
            diffs=[lookup[s,p,h,'R128']['observed'][k]-lookup[s,p,h,'H128']['observed'][k] for h in branches[1:] for k in ('adapt1','adapt2')]
            history.append(dict(seed=s,proposal_seed=p,gain=sum(diffs)/8))
        hflags=dict(mean_gain=sum(r['gain'] for r in history)/10>=.02,
            positive_pairs=sum(r['gain']>0 for r in history)>=8,
            validity=validity(['H128','R128','U128','B64']),**guards('H128',['R128','U128','B64']))
    close(saved['history_pairs'],history);close(saved['history_checks'],hflags)
    assert saved['history_pass']==(hflags is not None and all(hflags.values()))
    env=[]
    for s in sorted(set(s for s,p in pairs)):
        for h in branches:
            for policy in policies:
                ms=[lookup[z,p,h,policy] for z,p in pairs if z==s]
                env.append(dict(seed=s,branch=h,policy=policy,
                    observed={k:sum(m['observed'][k] for m in ms)/len(ms) for k in windows},
                    structure_errors=sum(m['structure_errors'] for m in ms)/len(ms)))
    close(saved['environment_means'],env)


def main():
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--confirmation',action='store_true');args=parser.parse_args()
    confirmation=args.confirmation;out=ROOT/('results/explicit-roles-confirmation-v1' if confirmation else 'results/explicit-roles-v1')
    start=time.monotonic()
    def timeout(*_):raise TimeoutError('900-second independent audit limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
        assert data['confirmation']==confirmation and data['hashes']==manifest and data['status']=='completed_pending_audit'
        for name,digest in manifest.items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        policies=('B64','B128','U64','U128','R128','H128');seedbase=1200;candidate='R128'
        if confirmation:
            first=ROOT/'results/explicit-roles-v1';first_data=json.loads((first/'results.json').read_text());first_audit=json.loads((first/'audit.json').read_text())
            assert first_audit['status']=='pass' and first_data['summary']['primary_pass']
            assert first_audit['result_sha256']==hashlib.sha256((first/'results.json').read_bytes()).hexdigest()
            assert manifest==json.loads((first/'manifest.json').read_text())
            candidate='H128' if first_data['summary']['history_pass'] else 'R128';policies=('U128',candidate);seedbase=1300
        assert data['candidate']==candidate
        worlds=json.loads((out/'worlds.json').read_text());branches=('stable','probability','forms','detail','reversed')
        lookup={(w['seed'],w['branch']):w for w in worlds};assert len(worlds)==25 and set(lookup)==set(itertools.product(range(seedbase,seedbase+5),branches))
        for w in worlds:
            assert list(map(len,w['local_main']))==[256,256] and len(w['local_selection'])==4
            assert all(list(map(len,b))==[32,32] for b in w['local_selection'])
            assert len(w['composition'])==256 and len(w['main'])==1280 and list(map(len,w['selection']))==[32]*20
            verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
        n=100 if confirmation else 300
        assert len(runs)==n and set((r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs)==set(itertools.product(range(seedbase,seedbase+5),(seedbase,seedbase+1),branches,policies))
        for i,r in enumerate(runs,1):
            with gzip.open(out/r['checkpoint_file'],'rt') as f:checkpoint=json.load(f)
            verify_run(r,lookup[r['seed'],r['branch']],checkpoint)
            assert r['costs']['feedback_labels']==(6784 if r['policy'] in ('B64','U64') else 5824)
            assert len(checkpoint['history'])==(192 if r['policy']=='H128' else 0)
            if i%25==0:print(f'{i}/{n} independent full trace/checkpoint/metric reconstructions verified',flush=True)
        # Matched acquisition; changed histories are equal up to the first change where specified.
        for seed in range(seedbase,seedbase+5):
            for p in (seedbase,seedbase+1):
                rs=[r for r in runs if r['seed']==seed and r['proposal_seed']==p]
                assert all(r['warmup']==rs[0]['warmup'] and r['initial_upper']==rs[0]['initial_upper'] for r in rs)
            d,rev=lookup[seed,'detail'],lookup[seed,'reversed']
            assert d['main'][:528]==rev['main'][:528] and d['selection'][:8]==rev['selection'][:8]
        verify_summary(runs,data['summary'],candidate,confirmation)
        total=dict(runs=n,allocated_labels=n*6784,generated_labels=25*6784,used_labels=0,candidate_fits=0,scoring_queries=0,
            history_rows=0,history_feature_predictions=0,composite_predictions=n*1280,local_predictions=n*2560,evaluation_predictions=0,oracle_context_queries=0)
        for r in runs:
            c=r['costs'];total['used_labels']+=c['feedback_labels'];total['candidate_fits']+=c['candidate_fits']+c['upper_candidate_fits']
            for k in ('scoring_queries','history_rows','history_feature_predictions'):total[k]+=c[k]
            for e in [r['transfer']]+r['evaluations']+r['endpoints']:
                total['evaluation_predictions']+=e['contexts'];total['oracle_context_queries']+=32*(1+len(e['removal_costs'])+len(e['raw_addition_gains']))
        close(data['totals'],total)
        assert total['used_labels']==(582400 if confirmation else 1843200) and total['evaluation_predictions']==n*728
        assert total['candidate_fits']<=(33200 if confirmation else 99600) and total['scoring_queries']<=(5000000 if confirmation else 15000000)
        assert total['history_rows']<=3000000 and total['oracle_context_queries']<=(368000 if confirmation else 1104000)
        assert data['elapsed_seconds']<900
        fixturepaths=sorted((ROOT/'results/explicit-roles-r0').glob('fixtures-*.json'))
        fixtures=[json.loads(p.read_text()) for p in fixturepaths]
        assert fixtures[-1]['status']=='pass' and sum(f['charged_labels'] for f in fixtures)<=5000
        assert json.loads((ROOT/'results/explicit-roles-r0/compatibility.json').read_text())['status']=='pass'
        result=dict(status='pass',runs=n,independently_replayed_labels=total['used_labels'],elapsed_seconds=time.monotonic()-start,
            primary_pass=data['summary']['primary_pass'],history_pass=data['summary']['history_pass'],
            **{k+'_sha256':hashlib.sha256((out/name).read_bytes()).hexdigest() for k,name in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    except Exception as exc:
        (out/'audit-failure.json').write_text(json.dumps(dict(status='failed',error=repr(exc),elapsed_seconds=time.monotonic()-start),indent=2)+'\n');raise
    finally:signal.alarm(0)

if __name__=='__main__':main()
