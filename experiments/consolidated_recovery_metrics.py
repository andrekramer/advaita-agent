"""019: separate prediction, representation stability and memory criteria."""
import copy
import math
from statistics import mean

from structural_consolidation_metrics import bit, desired, metrics as old_metrics, valid

BRANCHES = ('forms', 'detail', 'reversed')
VARIANTS = ('integrated', 'delete', 'raw', 'fixed')
TAIL = (1024, 1088, 1152, 1216, 1280)


def reference_slice(r, w):
    short = dict(r, predictions=r['predictions'][:768], raw_reads=r['raw_reads'][:768],
                 reviews=[v for v in r['reviews'] if v['index'] <= 768])
    return short, dict(w, main=w['main'][:768])


def score(r, w):
    short, short_world = reference_slice(r, w)
    reference = old_metrics(short, short_world)
    checks = []
    for v in r['reviews']:
        e = v['evaluation']
        checks.append(dict(index=v['index'], predictive=e['accuracy'] == 1 and e['regret'] <= .10,
            full=valid(e), structural=valid(e) and e['sufficient_minimal'] and e['spec'] == desired(w, e['index'])))
    tail = [c for c in checks if c['index'] in TAIL]
    assert len(tail) == 5
    obs, latent = [], []
    for t, (p, row) in enumerate(zip(r['predictions'], w['main']), 1):
        obs.append(-math.log(p if row['y'] else 1-p))
        q = .9 if bit(w, row, t) else .1
        latent.append(-q*math.log(p)-(1-q)*math.log1p(-p))
    captures, retrievals = [], []
    for v in r['reviews']:
        u = v['upper']
        if u is None:
            continue
        if u['action'] == 'retrieved':
            retrievals.append(v['index'])
        if u['captured'] is not None and u['archive_after'] is not None:
            ids = u['archive_after']['record_ids']
            indices = [int(i.split('/')[1]) for i in ids if i.startswith('main/')]
            captures.append(dict(index=v['index'], main_first=min(indices) if indices else None,
                main_last=max(indices) if indices else None, construction_labels=len(ids),
                contains_pre_simplification=any(i <= 240 for i in indices) or any(i.startswith('composition/') for i in ids)))
    result = dict(reference_768=reference, checkpoints=[c for c in checks if c['index'] in (768, 1024, 1280)],
        stable_predictive=all(c['predictive'] for c in tail), stable_full=all(c['full'] for c in tail),
        stable_structural=reference['transfer_valid'] and all(c['structural'] for c in tail),
        late_raw_reads=sum(r['raw_reads'][1024:1280]), captures=captures, retrievals=retrievals)
    for name, start, stop in [('return', 528, 1280), ('late', 1024, 1280)]:
        result[name+'_observed'] = mean(obs[start:stop])
        result[name+'_latent'] = mean(latent[start:stop])
    return result


def summarize(runs):
    groups = []
    for branch in BRANCHES:
        for variant in VARIANTS:
            ms = [r['recovery'] for r in runs if (r['branch'], r['variant']) == (branch, variant)]
            assert len(ms) == 10
            g = dict(branch=branch, variant=variant, runs=len(ms))
            for k in ('stable_predictive', 'stable_full', 'stable_structural'):
                g[k] = sum(m[k] for m in ms)
            g['transfer_valid'] = sum(m['reference_768']['transfer_valid'] for m in ms)
            g['trajectory_768'] = sum(m['reference_768']['trajectory'] for m in ms)
            g['checkpoints'] = [dict(index=t, **{k: sum(m['checkpoints'][i][k] for m in ms)
                for k in ('predictive', 'full', 'structural')}) for i, t in enumerate((768, 1024, 1280))]
            for k in ('return_observed', 'return_latent', 'late_observed', 'late_latent', 'late_raw_reads'):
                g[k] = mean(m[k] for m in ms)
            for k in ('captures', 'retrievals'):
                g[k] = sum(len(m[k]) for m in ms)
            groups.append(g)
    pairs = []
    for seed, ps, branch in sorted({(r['seed'], r['proposal_seed'], r['branch']) for r in runs}):
        rs = {r['variant']: r for r in runs if (r['seed'], r['proposal_seed'], r['branch']) == (seed, ps, branch)}
        a, d = rs['integrated']['recovery'], rs['delete']['recovery']
        p = dict(seed=seed, proposal_seed=ps, branch=branch,
            identical_predictions=rs['integrated']['predictions'] == rs['delete']['predictions'],
            early_return_gain=d['reference_768']['return_observed']-a['reference_768']['return_observed'],
            late_read_saving=rs['raw']['recovery']['late_raw_reads']-a['late_raw_reads'])
        for k in ('return_observed', 'return_latent', 'late_observed', 'late_latent'):
            p[k+'_gain'] = d[k]-a[k]
        pairs.append(p)
    environments = []
    for seed, branch in sorted({(p['seed'], p['branch']) for p in pairs}):
        ps = [p for p in pairs if (p['seed'], p['branch']) == (seed, branch)]
        ms = [r['recovery'] for r in runs if (r['seed'], r['branch'], r['variant']) == (seed, branch, 'integrated')]
        environments.append(dict(seed=seed, branch=branch, proposals=len(ps),
            return_gain=mean(p['return_observed_gain'] for p in ps), stable_structural=sum(m['stable_structural'] for m in ms)))
    representation = {b: next(g['stable_structural'] for g in groups if (g['branch'], g['variant']) == (b, 'integrated')) >= 8 for b in BRANCHES}
    detail = [p for p in pairs if p['branch'] == 'detail']
    reverse = [p for p in pairs if p['branch'] == 'reversed']
    memory = dict(mean_gain=mean(p['return_observed_gain'] for p in detail) >= .02,
        improving_pairs=sum(p['return_observed_gain'] > 0 for p in detail) >= 8,
        reversed_cost=-mean(p['return_observed_gain'] for p in reverse) <= .02)
    return dict(groups=groups, paired=pairs, environments=environments,
        representation_checks=representation, representation_pass=all(representation.values()),
        memory_checks=memory, memory_pass=all(memory.values()))
