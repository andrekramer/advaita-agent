"""Fixed C2 endpoint, transition and paired-memory criteria."""
import math
from statistics import mean

BRANCHES = ('forms', 'detail', 'reversed')
VARIANTS = ('integrated', 'delete', 'raw', 'fixed')


def valid(e):
    return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10


def desired(w, t):
    spec = [1, 1]
    if w['branch'] == 'forms' and 240 < t <= 528:
        spec[w['affected']] = 0
    elif w['branch'] != 'forms' and (0 < t <= 240 or t > 528):
        spec[w['affected']] = 2
    return spec


def bit(w, row, t):
    f = [x.copy() for x in w['forms']]
    if w['branch'] == 'forms' and 240 < t <= 528:
        f[w['affected']] = [0]*4
    x, a = row['x'], row['a']
    y = f[0][x[0]] ^ f[1][x[1]] ^ a
    if w['branch'] != 'forms' and (0 < t <= 240 or t > 528):
        j = w['affected']
        y ^= int(x[j] != w['representatives'][j][f[j][x[j]]])
        if w['branch'] == 'reversed' and t > 528: y ^= 1
    return y


def metrics(r, w):
    obs, latent = [], []
    for t, (p, row) in enumerate(zip(r['predictions'], w['main']), 1):
        obs.append(-math.log(p if row['y'] else 1-p))
        q = .9 if bit(w, row, t) else .1
        latent.append(-q*math.log(p)-(1-q)*math.log1p(-p))
    j = w['affected']
    collapses, splits, removals, additions, captures, retrieves, mismatches = [], [], [], [], [], [], []
    for v in r['reviews']:
        t = v['index']
        if v['local']:
            local = v['local'][j]
            if local['action'] == 'collapsed': collapses.append(t)
            if len(local['before']['counts']) == 1 and len(local['after']['counts']) == 2: splits.append(t)
        u = v['upper']
        if u is None: continue
        if u['before']['spec'][j] > 0 and u['after']['spec'][j] == 0: removals.append(t)
        if u['before']['spec'][j] < u['after']['spec'][j]: additions.append(t)
        if u['captured'] is not None: captures.append(t)
        if u['action'] == 'retrieved': retrieves.append(t)
        if u['archive_check'] is not None and not u['archive_check']['compatible']: mismatches.append(t)
    endpoints = [valid(e) and e['spec'] == desired(w, e['index']) and e['sufficient_minimal'] for e in r['endpoints']]
    hidden = lambda times: any(240 < t <= 528 for t in times)
    returned = lambda times: any(t > 528 for t in times)
    operations = hidden(collapses) and returned(splits) and hidden(removals) and returned(additions) if w['branch'] == 'forms' else hidden(captures) and returned(additions)
    return dict(transfer_valid=valid(r['transfer']), endpoint_valid=endpoints,
        final_full_valid=valid(r['endpoints'][-1]), final_minimal_valid=endpoints[-1],
        operations=operations, trajectory=valid(r['transfer']) and all(endpoints) and operations,
        collapse_reviews=collapses, recreation_reviews=splits, dependency_removals=removals,
        increases=additions, captures=captures, retrievals=retrieves, incompatible_archive_reviews=mismatches,
        main_observed=mean(obs), main_latent=mean(latent), return_observed=mean(obs[528:656]),
        return_latent=mean(latent[528:656]), hidden_raw_reads=sum(r['raw_reads'][240:528]),
        all_raw_reads=sum(r['raw_reads']))


def summarize(runs):
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            rs = [r for r in runs if (r['branch'], r['variant']) == (b, v)]
            g = dict(branch=b, variant=v, runs=len(rs))
            for f in ('transfer_valid', 'final_full_valid', 'final_minimal_valid', 'operations', 'trajectory'):
                g[f] = sum(r['metrics'][f] for r in rs)
            g['endpoint_passes'] = [sum(r['metrics']['endpoint_valid'][i] for r in rs) for i in range(3)]
            for f in ('main_observed', 'main_latent', 'return_observed', 'return_latent', 'hidden_raw_reads', 'all_raw_reads'):
                g[f] = mean(r['metrics'][f] for r in rs)
            for f in ('captures', 'retrievals', 'incompatible_archive_reviews'):
                g[f] = sum(len(r['metrics'][f]) for r in rs)
            groups.append(g)
    pairs = []
    for s, p, b in sorted({(r['seed'], r['proposal_seed'], r['branch']) for r in runs}):
        ms = {r['variant']: r['metrics'] for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (s, p, b)}
        pairs.append(dict(seed=s, proposal_seed=p, branch=b,
            return_gain=ms['delete']['return_observed']-ms['integrated']['return_observed'],
            latent_return_gain=ms['delete']['return_latent']-ms['integrated']['return_latent'],
            hidden_read_saving=ms['raw']['hidden_raw_reads']-ms['integrated']['hidden_raw_reads']))
    checks = {f'{b}_trajectory': next(g['trajectory'] for g in groups if (g['branch'], g['variant']) == (b, 'integrated')) >= 8 for b in BRANCHES}
    returns = [p for p in pairs if p['branch'] == 'detail']
    reversed_ = [p for p in pairs if p['branch'] == 'reversed']
    checks.update(memory_mean_gain=mean(p['return_gain'] for p in returns) >= .02,
        memory_pairs=sum(p['return_gain'] > 0 for p in returns) >= 8,
        reversed_cost=-mean(p['return_gain'] for p in reversed_) <= .02,
        hidden_read_saving=all(mean(p['hidden_read_saving'] for p in pairs if p['branch'] == b) > 0 for b in BRANCHES))
    return dict(groups=groups, paired=pairs, checks=checks, primary_pass=all(checks.values()))
