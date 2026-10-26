"""020 independent arithmetic, policy, provenance and checkpoint reconstruction."""
import copy
import gzip
import hashlib
import itertools
import json
import math
from pathlib import Path
import signal
from statistics import mean
import time

from audit_nested_abstractions import close, CONTEXTS, H, logloss, local_p, local_loss
from audit_protection_interfaces import canonical, sha, truth, verify_world
from audit_structural_consolidation import same_partition
from structural_reference import Local as CoreLocal, Upper, fit, predict, ports, fingerprint, unpack

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/consolidated-protection-v1'
BRANCHES = ('persistent', 'burst', 'remap')
POLICIES = ('baseline', 'corroborated')


def label(w, x, a, t):
    f = truth(w, t)
    return (f[0][x[0]]+f[1][x[1]]+a) % 2


class ProtectedReference(CoreLocal):
    def __init__(self, seed):
        super().__init__(seed)
        self.protection = dict(established=False, adequate=0, pending=None)
        self.protection_costs = dict(starts=0, confirmations=0, failures=0,
            establishments=0, confirmation_queries=0, pending_cells_peak=0)

    def review(self, saved, batch):
        if not self.structural:
            return super().review(saved, batch)
        before, original, revision = copy.deepcopy(self.protection), self.state(), self.revision
        ordinary = saved['ordinary']
        super().review(ordinary, batch)
        action, witness = ordinary['action'], None
        if before['pending'] is not None:
            challenger = before['pending']
            value = local_loss(*unpack(challenger), batch)
            passed = ordinary['old_loss']-value > .005
            witness = dict(model=challenger, loss=value, passed=passed)
            self.queries += len(batch)
            self.protection_costs['confirmation_queries'] += len(batch)
            self.partition, self.table = unpack(challenger if passed else original)
            self.pending = None
            self.protection['pending'] = None
            action = 'confirmed' if passed else 'confirmation_failed'
            self.protection_costs['confirmations' if passed else 'failures'] += 1
        elif before['established'] and ordinary['action'] == 'improved':
            self.protection['pending'] = copy.deepcopy(ordinary['after'])
            self.partition, self.table = unpack(original)
            self.pending = None
            action = 'awaiting_confirmation'
            self.protection_costs['starts'] += 1
            self.protection_costs['pending_cells_peak'] = max(self.protection_costs['pending_cells_peak'], len(ordinary['after']['counts']))
        accepted = action in ('improved', 'collapsed', 'confirmed')
        if accepted:
            self.protection = dict(established=False, adequate=0, pending=None)
        else:
            self.protection['adequate'] = min(2, before['adequate']+1) if ordinary['old_loss'] <= .55 else 0
            if self.protection['adequate'] == 2 and not self.protection['established']:
                self.protection['established'] = True
                self.protection_costs['establishments'] += 1
        close(saved, dict(ordinary=ordinary, protection=dict(before=before, after=self.protection,
            action=action, accepted=accepted, witness=witness), after=self.state()))
        self.revision = revision + (original['groups'] != self.state()['groups'])


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
    protected = r["policy"] == "corroborated"
    nodes = [ProtectedReference(s) if protected else CoreLocal(s) for s in seeds]
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
        if protected and nodes[j].structural:
            use(records, f'local{j}.corroboration', 'selection')
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
        assert r['pre_specs'][t-1] == upper.model['spec']
        assert r['pre_local_exact'][t-1] == [same_partition(n.partition, f) for n,f in zip(nodes, truth(w,t))]
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
        if t in (128, 192, 320, 512, 1280):
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
    assert r['protection'] == [n.protection if protected else None for n in nodes]
    assert r['protection_costs'] == [n.protection_costs if protected else None for n in nodes]
    if protected:
        expected = dict(schema=20, core=expected, protection=[n.protection for n in nodes],
            protection_costs=[n.protection_costs for n in nodes])
        assert all(n.protection_costs['pending_cells_peak'] <= 2 for n in nodes)
    close(checkpoint, expected)
    assert sha(checkpoint) == r['checkpoint_sha256']
    assert costs['local_pending_peak'] <= 1 and costs['upper_pending'] <= 8 and costs['archive'] <= 16
    if measure: verify_metrics(r, w)


def good(e):
    return all(e['local_exact']) and e['accuracy'] == 1 and e['regret'] <= .10


def verify_metrics(r, w):
    reviews = r['reviews']; j = w['affected']
    selected = [v for v in reviews if v['index'] >= 192 and (w['branch'] != 'burst' or v['index'] <= 512)]
    tail = [v for v in reviews if v['index'] in (1024,1088,1152,1216,1280)]
    assert len(tail) == 5
    recovery = None
    for a,b in zip(reviews, reviews[1:]):
        if a['index'] > 128 and good(a['evaluation']) and good(b['evaluation']):
            recovery = b['index']; break
    observed, latent, local = [], [], []
    for t,row in enumerate(w['main'],1):
        p = r['predictions'][t-1]; lp = r['local_predictions'][t-1][j]
        y = label(w,row['x'],row['a'],t); ly = truth(w,t)[j][row['x'][j]]
        observed.append(logloss(p,row['y']))
        latent.append(.9*logloss(p,y)+.1*logloss(p,1-y))
        local.append(.9*logloss(lp,ly)+.1*logloss(lp,1-ly))
    replacements, harmful, wrong = [], [], []
    for v in reviews:
        forms = truth(w,v['index'])
        for k,node in enumerate(v['local']):
            if 'protection' in node:
                action = node['protection']['action']; before = node['ordinary']['before']
                p = node['protection']
                if not p['before']['established'] and p['after']['established'] and not same_partition(node['after']['partition'],forms[k]):
                    wrong.append([v['index'],k])
            else: action, before = node['action'], node['before']
            if action in ('improved','collapsed','confirmed'):
                replacements.append([v['index'],k])
                if same_partition(before['partition'],forms[k]) and not same_partition(node['after']['partition'],forms[k]):
                    harmful.append([v['index'],k])
    start,stop = (0,1280) if w['branch']=='persistent' else ((128,320) if w['branch']=='burst' else (128,512))
    expected = dict(transfer_valid=good(r['transfer']),final_full=good(reviews[-1]['evaluation']),
        stable_predictive=all(v['evaluation']['accuracy']==1 and v['evaluation']['regret']<=.10 for v in tail),
        stable_full=all(good(v['evaluation']) for v in tail),
        stable_structure=good(r['transfer']) and all(good(v['evaluation']) and v['evaluation']['spec']==[1,1] and v['evaluation']['sufficient_minimal'] for v in tail),
        affected_errors=sum(not v['evaluation']['local_exact'][j] for v in selected),
        both_node_errors=sum(2-sum(v['evaluation']['local_exact']) for v in selected),
        late_node_errors=sum(2-sum(v['evaluation']['local_exact']) for v in tail),
        confirmed_recovery=recovery,recovery_for_comparison=1344 if recovery is None else recovery,
        composite_observed=mean(observed[start:stop]),composite_latent=mean(latent[start:stop]),
        affected_latent=mean(local[start:stop]),late_composite_latent=mean(latent[1024:]),
        raw_reads=sum(r['raw_reads']),wrong_form_bypass=sum(any(r['pre_specs'][i][k]==2 and not r['pre_local_exact'][i][k] for k in (0,1)) for i in range(len(w['main']))),
        replacements=replacements,harmful=harmful,wrong_establishments=wrong,
        captures=sum(v['upper']['captured'] is not None for v in reviews),
        retrievals=sum(v['upper']['action']=='retrieved' for v in reviews))
    close(r['metrics'],expected)


def verify_summary(runs,saved):
    groups=[]
    count=('transfer_valid','final_full','stable_predictive','stable_full','stable_structure',
        'affected_errors','both_node_errors','late_node_errors','captures','retrievals')
    avg=('recovery_for_comparison','composite_observed','composite_latent','affected_latent',
        'late_composite_latent','raw_reads','wrong_form_bypass')
    for b,p in itertools.product(BRANCHES,POLICIES):
        ms=[r['metrics'] for r in runs if r['branch']==b and r['policy']==p]
        assert len(ms)==10
        g=dict(branch=b,policy=p,runs=10)
        for k in count: g[k]=sum(m[k] for m in ms)
        for k in avg: g[k]=mean(m[k] for m in ms)
        for k in ('replacements','harmful','wrong_establishments'): g[k]=sum(map(lambda m:len(m[k]),ms))
        groups.append(g)
    pairs=[]
    for s,ps,b in sorted(set((r['seed'],r['proposal_seed'],r['branch']) for r in runs)):
        both={r['policy']:r['metrics'] for r in runs if (r['seed'],r['proposal_seed'],r['branch'])==(s,ps,b)}
        a,c=both['baseline'],both['corroborated']
        p=dict(seed=s,proposal_seed=ps,branch=b,error_reduction=a['affected_errors']-c['affected_errors'],
            recovery_delay=c['recovery_for_comparison']-a['recovery_for_comparison'])
        for k in ('composite_observed','composite_latent','affected_latent'): p[k+'_cost']=c[k]-a[k]
        pairs.append(p)
    checks={}
    for b in BRANCHES:
        groups_b=[g for g in groups if g['branch']==b]; pairs_b=[p for p in pairs if p['branch']==b]
        checks[b+'_acquisition_final']=all(g['transfer_valid']>=8 and g['final_full']>=8 for g in groups_b)
        fields=['composite_latent','affected_latent']
        if b!='burst': fields.insert(0,'composite_observed')
        for k in fields: checks[b+'_'+k]=mean(p[k+'_cost'] for p in pairs_b) <= (.05 if b=='remap' else .02)
        if b=='remap': checks['remap_recovery_delay']=mean(p['recovery_delay'] for p in pairs_b)<=64
        else:
            a,c=groups_b
            assert a['policy']=='baseline' and c['policy']=='corroborated'
            checks[b+'_error_benefit']=a['affected_errors']>0 and 4*c['affected_errors']<=3*a['affected_errors'] and sum(p['error_reduction']>0 for p in pairs_b)>=2
    env=[]
    for s,b in sorted(set((p['seed'],p['branch']) for p in pairs)):
        ps=[p for p in pairs if (p['seed'],p['branch'])==(s,b)]
        env.append(dict(seed=s,branch=b,proposals=len(ps),**{k:mean(p[k] for p in ps) for k in ('error_reduction','recovery_delay','composite_observed_cost','composite_latent_cost','affected_latent_cost')}))
    close(saved,dict(groups=groups,paired=pairs,environments=env,checks=checks,primary_pass=all(checks.values())))


def main():
    started=time.monotonic()
    def timeout(*_): raise TimeoutError('600-second 020 audit limit')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(600)
    try:
        manifest=json.loads((OUT/'manifest.json').read_text())
        for name,digest in manifest.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        data=json.loads((OUT/'results.json').read_text())
        assert data['hashes']==manifest and data['status']=='completed_pending_audit'
        worlds=json.loads((OUT/'worlds.json').read_text())
        lookup={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==15 and set(lookup)==set(itertools.product(range(900,905),BRANCHES))
        for w in worlds:
            assert list(map(len,w['local_main']))==[256]*2 and len(w['local_selection'])==4
            assert all(list(map(len,b))==[32]*2 for b in w['local_selection'])
            assert len(w['composition'])==256 and len(w['main'])==1280 and list(map(len,w['selection']))==[32]*20
            verify_world(w)
        with gzip.open(OUT/'runs.jsonl.gz','rt') as f: runs=[json.loads(line) for line in f]
        assert len(runs)==60 and {(r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs}==set(itertools.product(range(900,905),(900,901),BRANCHES,POLICIES))
        for i,r in enumerate(runs,1):
            with gzip.open(OUT/r['checkpoint_file'],'rt') as f: checkpoint=json.load(f)
            verify_run(r,lookup[r['seed'],r['branch']],checkpoint)
            assert r['costs']['feedback_labels']==6784
            if i%12==0: print(f'{i}/60 policies, traces and full checkpoints verified',flush=True)
        for s in range(900,905):
            ws=[lookup[s,b] for b in BRANCHES]
            assert all(w['main'][:128]==ws[0]['main'][:128] for w in ws)
            for ps in (900,901):
                rs=[r for r in runs if (r['seed'],r['proposal_seed'])==(s,ps)]
                assert all(r['warmup']==rs[0]['warmup'] for r in rs)
        verify_summary(runs,data['summary'])
        es=[e for r in runs for e in [r['transfer'],*r['endpoints'],*(v['evaluation'] for v in r['reviews'])]]
        totals=dict(runs=60,allocated_labels=407040,generated_labels=101760,
            used_labels=sum(r['costs']['feedback_labels'] for r in runs),
            candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
            scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),composite_predictions=76800,
            local_predictions=153600,evaluation_predictions=sum(e['contexts'] for e in es),
            oracle_context_queries=32*sum(1+len(e['removal_costs'])+len(e['raw_addition_gains']) for e in es),
            confirmation_queries=sum(c['confirmation_queries'] for r in runs for c in r['protection_costs'] if c is not None))
        close(data['totals'],totals)
        assert totals['used_labels']==407040 and totals['candidate_fits']<=19920 and totals['scoring_queries']<=3000000
        assert totals['evaluation_predictions']==49440 and totals['oracle_context_queries']<=249600
        assert data['elapsed_seconds']<600
        fixture=json.loads((ROOT/'results/consolidated-protection-fixtures.json').read_text())
        assert fixture['status']=='pass' and fixture['charged_labels']<=2000
        result=dict(status='pass',runs=60,independently_replayed_labels=407040,elapsed_seconds=time.monotonic()-started,
            artifact_sha256={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('results.json','runs.jsonl.gz','worlds.json')})
        (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASS: all 60 runs independently reconstructed, including corroboration and full checkpoints.')
    except Exception as exc:
        (OUT/'audit-incomplete.json').write_text(json.dumps(dict(error=repr(exc),elapsed_seconds=time.monotonic()-started),indent=2)+'\n')
        raise
    finally: signal.alarm(0)


if __name__=='__main__': main()
