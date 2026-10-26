"""Predeclared descriptive metrics; no feedback to the experimental learner."""
import math
from statistics import mean

BRANCHES = ('persistent', 'remap', 'burst')
VARIANTS = ('immediate_opening', 'immediate_reclosure', 'earned_opening', 'earned_reclosure')


def good(e):
    return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10


def forms(w, t):
    f = [x.copy() for x in w['forms']]
    if w['branch'] == 'remap' and t > 128:
        for x in w['representatives'][w['affected']]:
            f[w['affected']][x] ^= 1
    return f


def loss(p, bit):
    return -math.log(p if bit else 1-p)


def latent(p, bit):
    q = .9 if bit else .1
    return -q*math.log(p)-(1-q)*math.log1p(-p)


def metrics(r, w):
    upper, local = [], [[], []]
    observed, local_observed = [], [[], []]
    for t, (p, ps, row) in enumerate(zip(r['predictions'], r['local_predictions'], w['main']), 1):
        f = forms(w, t)
        bits = [f[j][row['x'][j]] for j in range(2)]
        upper.append(latent(p, bits[0] ^ bits[1] ^ row['a']))
        observed.append(loss(p, row['y']))
        for j in range(2):
            local[j].append(latent(ps[j], bits[j]))
            local_observed[j].append(loss(ps[j], row['local'][j]))
    start = {'persistent': 0, 'remap': 128, 'burst': 192}[w['branch']]
    eligible = [v for v in r['reviews'] if v['index'] > start]
    first = next((v['index'] for v in eligible if good(v['evaluation'])), None)
    pair = next(((a['index'], b['index']) for a, b in zip(eligible, eligible[1:])
                 if good(a['evaluation']) and good(b['evaluation'])), (None, None))
    opened, hidden, reclosed, intervals = [], [], [], []
    pending = None
    for v in r['reviews']:
        before, after = v['ordinary']['before']['mode'], v['upper_after']['mode']
        if before == 'coarse' and after != 'coarse':
            opened.append(v['index'])
            pending = v['index']
        if before != 'coarse' and after == 'coarse':
            hidden.append(v['index'])
            if pending is not None:
                intervals.append(dict(opened=pending, hidden=v['index'], latency=v['index']-pending))
                pending = None
        if v.get('reclosure', {}).get('action') == 'reclosed':
            reclosed.append(v['index'])
    if pending is not None:
        intervals.append(dict(opened=pending, hidden=None, latency=None))
    final = r['reviews'][-1]['evaluation']
    result = dict(transfer_valid=good(r['transfer']), final_valid=good(final),
        final_predictive_valid=final['accuracy'] == 1 and final['regret'] <= .10,
        final_local_valid=all(final['local_exact']), coarse_final_valid=good(final) and final['mode'] == 'coarse',
        invalid_affected_checkpoints=sum(not v['evaluation']['local_exact'][w['affected']]
                                        for v in r['reviews'] if v['index'] > 128),
        invalid_local_checkpoints=sum(sum(not x for x in v['evaluation']['local_exact']) for v in r['reviews']),
        first_valid=first, first_confirmed_pair_start=pair[0], confirmation=pair[1],
        confirmation_censored=576 if pair[1] is None else pair[1],
        reopen_reviews=opened, hide_reviews=hidden, reclosure_reviews=reclosed, reclosure_latencies=intervals,
        bypass_wrong_records=sum(m == f"fine{w['affected']}" and not e[w['affected']]
                                 for m, e in zip(r['pre_modes'], r['pre_local_exact'])),
        raw_reads=sum(r['raw_reads']), exposed_records=sum(m != 'coarse' for m in r['pre_modes']))
    for label, window in (('main', slice(None)), ('change', slice(128, None)), ('burst', slice(128, 320))):
        result[f'{label}_observed'] = mean(observed[window])
        result[f'{label}_latent'] = mean(upper[window])
        result[f'{label}_local_observed'] = [mean(x[window]) for x in local_observed]
        result[f'{label}_local_latent'] = [mean(x[window]) for x in local]
        result[f'{label}_affected_latent'] = mean(local[w['affected']][window])
    return result


def summarize(runs):
    groups = []
    for b in BRANCHES:
        for v in VARIANTS:
            rs = [r for r in runs if (r['branch'], r['variant']) == (b, v)]
            g = dict(branch=b, variant=v, runs=len(rs))
            for field in ('transfer_valid', 'final_valid', 'final_predictive_valid', 'final_local_valid', 'coarse_final_valid'):
                g[field] = sum(r['metrics'][field] for r in rs)
            for field in ('main_observed', 'main_latent', 'main_affected_latent', 'change_observed', 'change_latent',
                          'change_affected_latent', 'burst_latent', 'burst_affected_latent', 'confirmation_censored',
                          'raw_reads', 'bypass_wrong_records'):
                g[field] = mean(r['metrics'][field] for r in rs)
            g['invalid_affected_checkpoints'] = sum(r['metrics']['invalid_affected_checkpoints'] for r in rs)
            g['reopenings'] = sum(len(r['metrics']['reopen_reviews']) for r in rs)
            g['reclosures'] = sum(len(r['metrics']['reclosure_reviews']) for r in rs)
            groups.append(g)
    pairs, interactions = [], []
    keys = sorted({(r['seed'], r['proposal_seed'], r['branch']) for r in runs})
    fields = ('main_observed', 'main_latent', 'main_affected_latent', 'change_observed', 'change_latent',
              'change_affected_latent', 'burst_latent', 'burst_affected_latent', 'confirmation_censored',
              'raw_reads', 'invalid_affected_checkpoints')
    for seed, ps, b in keys:
        m = {r['variant']: r['metrics'] for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (seed, ps, b)}
        for axis, settings in (('protection', ('opening', 'reclosure')), ('reclosure', ('immediate', 'earned'))):
            for setting in settings:
                a, c = ((m[f'earned_{setting}'], m[f'immediate_{setting}']) if axis == 'protection'
                        else (m[f'{setting}_reclosure'], m[f'{setting}_opening']))
                pairs.append(dict(seed=seed, proposal_seed=ps, branch=b, axis=axis, setting=setting,
                                  differences={f: a[f]-c[f] for f in fields}))
        interactions.append(dict(seed=seed, proposal_seed=ps, branch=b, differences={
            f: (m['earned_reclosure'][f]-m['earned_opening'][f])-
               (m['immediate_reclosure'][f]-m['immediate_opening'][f])
            for f in ('main_latent', 'raw_reads', 'invalid_affected_checkpoints')}))
    lookup = {(g['branch'], g['variant']): g for g in groups}
    checks = {}
    for setting in ('opening', 'reclosure'):
        diff = lambda b, f: lookup[b, f'earned_{setting}'][f]-lookup[b, f'immediate_{setting}'][f]
        c = lookup['burst', f'immediate_{setting}']['invalid_affected_checkpoints']
        a = lookup['burst', f'earned_{setting}']['invalid_affected_checkpoints']
        checks[setting] = dict(
            endpoint_validity=all(lookup[b, f'{local}_{setting}'][f] >= 8
                for b in BRANCHES for local in ('immediate', 'earned') for f in ('transfer_valid', 'final_valid')),
            persistent_loss=all(diff('persistent', f) <= .02 for f in ('main_observed', 'main_latent', 'main_affected_latent')),
            remap_loss=all(diff('remap', f) <= .05 for f in ('change_observed', 'change_latent', 'change_affected_latent')),
            remap_delay=diff('remap', 'confirmation_censored') <= 64,
            burst_loss=all(diff('burst', f) <= .02 for f in ('burst_latent', 'burst_affected_latent')),
            protection=c > 0 and a <= .75*c and sum(p['differences']['invalid_affected_checkpoints'] < 0 for p in pairs
                if (p['branch'], p['axis'], p['setting']) == ('burst', 'protection', setting)) >= 2)
    gate = {b: all(lookup[b, 'immediate_reclosure'][f] >= 8 for f in ('transfer_valid', 'final_valid')) for b in BRANCHES}
    return dict(groups=groups, paired=pairs, interactions=interactions, checks=checks,
                primary_pass=all(all(c.values()) for c in checks.values()),
                progression_checks=gate, progression_gate=all(gate.values()))
