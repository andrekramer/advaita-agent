"""020 frozen error, loss and adaptation criteria."""
import math
from statistics import mean

BRANCHES = ('persistent', 'burst', 'remap')
POLICIES = ('baseline', 'corroborated')


def truth(w, t):
    f = [a.copy() for a in w['forms']]
    if w['branch'] == 'remap' and t > 128:
        for x in w['representatives'][w['affected']]: f[w['affected']][x] ^= 1
    return f


def same(a, b):
    return all((a[i] == a[j]) == (b[i] == b[j]) for i in range(4) for j in range(4))


def full(e):
    return e['accuracy'] == 1 and e['regret'] <= .10 and all(e['local_exact'])


def expected(p, y):
    q = .9 if y else .1
    return -q*math.log(p)-(1-q)*math.log1p(-p)


def metrics(r, w):
    j = w['affected']
    observed, latent, local = [], [], []
    for t, (p, row, lp) in enumerate(zip(r['predictions'], w['main'], r['local_predictions']), 1):
        f = truth(w, t); y = f[0][row['x'][0]] ^ f[1][row['x'][1]] ^ row['a']
        observed.append(-math.log(p if row['y'] else 1-p))
        latent.append(expected(p, y)); local.append(expected(lp[j], f[j][row['x'][j]]))
    reviews = r['reviews']
    selected = [v for v in reviews if v['index'] >= 192 and (w['branch'] != 'burst' or v['index'] <= 512)]
    tail = [v for v in reviews if v['index'] >= 1024]
    confirmed = next((b['index'] for a, b in zip(reviews, reviews[1:])
        if a['index'] > 128 and full(a['evaluation']) and full(b['evaluation'])), None)
    replacements, harmful, wrong_establishments = [], [], []
    for v in reviews:
        f = truth(w, v['index'])
        for k, node in enumerate(v['local']):
            ordinary = node.get('ordinary', node)
            action = node['protection']['action'] if 'protection' in node else node['action']
            if action in ('improved', 'collapsed', 'confirmed'):
                replacements.append([v['index'], k])
                if same(ordinary['before']['partition'], f[k]) and not same(node['after']['partition'], f[k]):
                    harmful.append([v['index'], k])
            if 'protection' in node:
                p = node['protection']
                if not p['before']['established'] and p['after']['established'] and not same(node['after']['partition'], f[k]):
                    wrong_establishments.append([v['index'], k])
    start, stop = {'persistent': (0, 1280), 'burst': (128, 320), 'remap': (128, 512)}[w['branch']]
    return dict(transfer_valid=full(r['transfer']), final_full=full(reviews[-1]['evaluation']),
        stable_predictive=all(v['evaluation']['accuracy'] == 1 and v['evaluation']['regret'] <= .10 for v in tail),
        stable_full=all(full(v['evaluation']) for v in tail),
        stable_structure=full(r['transfer']) and all(full(v['evaluation']) and v['evaluation']['spec'] == [1, 1]
            and v['evaluation']['sufficient_minimal'] for v in tail),
        affected_errors=sum(not v['evaluation']['local_exact'][j] for v in selected),
        both_node_errors=sum(sum(not x for x in v['evaluation']['local_exact']) for v in selected),
        late_node_errors=sum(sum(not x for x in v['evaluation']['local_exact']) for v in tail),
        confirmed_recovery=confirmed, recovery_for_comparison=confirmed if confirmed is not None else 1344,
        composite_observed=mean(observed[start:stop]), composite_latent=mean(latent[start:stop]),
        affected_latent=mean(local[start:stop]), late_composite_latent=mean(latent[1024:]),
        raw_reads=sum(r['raw_reads']), wrong_form_bypass=sum(any(s == 2 and not ok for s, ok in zip(spec, exact))
            for spec, exact in zip(r['pre_specs'], r['pre_local_exact'])),
        replacements=replacements, harmful=harmful, wrong_establishments=wrong_establishments,
        captures=sum(v['upper']['captured'] is not None for v in reviews),
        retrievals=sum(v['upper']['action'] == 'retrieved' for v in reviews))


def summarize(runs):
    groups=[]
    counts=('transfer_valid','final_full','stable_predictive','stable_full','stable_structure',
        'affected_errors','both_node_errors','late_node_errors','captures','retrievals')
    avgs=('recovery_for_comparison','composite_observed','composite_latent','affected_latent',
        'late_composite_latent','raw_reads','wrong_form_bypass')
    for b in BRANCHES:
        for p in POLICIES:
            ms=[r['metrics'] for r in runs if (r['branch'],r['policy']) == (b,p)]
            assert len(ms)==10
            groups.append(dict(branch=b,policy=p,runs=10,**{k:sum(m[k] for m in ms) for k in counts},
                **{k:mean(m[k] for m in ms) for k in avgs},
                **{k:sum(len(m[k]) for m in ms) for k in ('replacements','harmful','wrong_establishments')}))
    pairs=[]
    for s,ps,b in sorted({(r['seed'],r['proposal_seed'],r['branch']) for r in runs}):
        ms={r['policy']:r['metrics'] for r in runs if (r['seed'],r['proposal_seed'],r['branch'])==(s,ps,b)}
        a,c=ms['baseline'],ms['corroborated']
        pairs.append(dict(seed=s,proposal_seed=ps,branch=b,error_reduction=a['affected_errors']-c['affected_errors'],
            recovery_delay=c['recovery_for_comparison']-a['recovery_for_comparison'],
            **{k+'_cost':c[k]-a[k] for k in ('composite_observed','composite_latent','affected_latent')}))
    checks={}
    for b in BRANCHES:
        gs={g['policy']:g for g in groups if g['branch']==b}
        ps=[p for p in pairs if p['branch']==b]
        checks[b+'_acquisition_final']=all(g['transfer_valid']>=8 and g['final_full']>=8 for g in gs.values())
        fields=('composite_latent','affected_latent') if b=='burst' else ('composite_observed','composite_latent','affected_latent')
        for k in fields: checks[b+'_'+k]=mean(p[k+'_cost'] for p in ps) <= (.05 if b=='remap' else .02)
        if b in ('persistent','burst'):
            a,c=gs['baseline']['affected_errors'],gs['corroborated']['affected_errors']
            checks[b+'_error_benefit']=a>0 and c<=.75*a and sum(p['error_reduction']>0 for p in ps)>=2
        else: checks['remap_recovery_delay']=mean(p['recovery_delay'] for p in ps)<=64
    environments=[]
    for s,b in sorted({(p['seed'],p['branch']) for p in pairs}):
        ps=[p for p in pairs if (p['seed'],p['branch'])==(s,b)]
        environments.append(dict(seed=s,branch=b,proposals=len(ps),
            **{k:mean(p[k] for p in ps) for k in ('error_reduction','recovery_delay','composite_observed_cost','composite_latent_cost','affected_latent_cost')}))
    return dict(groups=groups,paired=pairs,environments=environments,checks=checks,primary_pass=all(checks.values()))
