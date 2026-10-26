"""021 independent prospective-memory and full core reconstruction."""
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

from audit_nested_abstractions import close, CONTEXTS, H, logloss, local_p
from audit_protection_interfaces import canonical, sha
from audit_structural_consolidation import truth, label, same_partition, verify_world
from structural_reference import Local, Upper, fit, predict, ports, fingerprint, loss

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/prospective-memory-v1'
BRANCHES=('detail','reversed')
POLICIES=('legacy','reserve','discard')


class MemoryUpper(Upper):
    def __init__(self,seed,mode):
        super().__init__(seed,'integrated')
        self.mode=mode
        self.reservation=dict(pending=None,completed=False)
        self.memory_costs=dict(nominations=0,failures=0,invalidations=0,confirmations=0,qualification_queries=0,pending_cells_peak=0)

    def review(self,saved,buffer,ids,nodes,batch,event):
        before=copy.deepcopy(self.reservation)
        action,witness,promoted='locked',None,None
        if not self.reservation['completed']:
            action='idle'; pending=self.reservation['pending']
            if pending is None and 2 in self.model['spec']:
                snapshot=dict(payload=canonical(self.model),dependency=fingerprint(self.ports),capture_event=event,record_ids=self.ids.copy())
                if snapshot['dependency']==fingerprint(ports(self.model['spec'],nodes)):
                    pending=dict(snapshot=snapshot,passes=0)
                    self.reservation['pending']=pending
                    self.memory_costs['nominations']+=1
                    self.memory_costs['pending_cells_peak']=max(self.memory_costs['pending_cells_peak'],len(self.model['counts']))
            if pending is not None:
                snapshot=pending['snapshot']; model=json.loads(snapshot['payload'])
                if snapshot['dependency']!=fingerprint(ports(model['spec'],nodes)):
                    self.reservation['pending']=None
                    self.memory_costs['invalidations']+=1
                    action='invalidated'
                else:
                    value=loss(model,batch,nodes)
                    self.scoring+=len(batch); self.memory_costs['qualification_queries']+=len(batch)
                    passed=value<=.55
                    witness=dict(snapshot=copy.deepcopy(snapshot),loss=value,passed=passed,prior_passes=pending['passes'])
                    if not passed:
                        self.reservation['pending']=None; self.memory_costs['failures']+=1; action='failed'
                    elif pending['passes']==0:
                        pending['passes']=1; action='awaiting_confirmation'
                    else:
                        promoted=copy.deepcopy(snapshot); promoted['capture_event']=event
                        self.reservation=dict(pending=None,completed=True)
                        self.memory_costs['confirmations']+=1
                        action='reserved' if self.mode=='reserve' else 'discarded'
        self.variant='delete'
        super().review(saved['ordinary'],buffer,ids,nodes,batch,event)
        self.variant='integrated'
        if promoted is not None and self.mode=='reserve':
            self.archive=copy.deepcopy(promoted)
            self.peaks['archive']=max(self.peaks['archive'],len(json.loads(promoted['payload'])['counts']))
        close(saved,dict(qualification=dict(before=before,after=self.reservation,action=action,witness=witness,confirmed=promoted),
            ordinary=saved['ordinary'],archive_final=self.archive))


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
    upper = Upper(95000+r['proposal_seed'], variant) if r['policy']=='legacy' else MemoryUpper(95000+r['proposal_seed'], r['policy'])
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
                if r['policy'] != 'legacy': use(records, 'upper.memory_qualification', 'selection')
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
    assert r['reservation'] == (None if r['policy']=='legacy' else upper.reservation)
    assert r['memory_costs'] == (None if r['policy']=='legacy' else upper.memory_costs)
    if r['policy'] != 'legacy':
        assert upper.memory_costs['pending_cells_peak'] <= 16
        expected = dict(schema=21, core=expected, memory_mode=r['policy'], reservation=upper.reservation, memory_costs=upper.memory_costs)
    close(checkpoint, expected)
    assert sha(checkpoint) == r['checkpoint_sha256']
    assert costs['local_pending_peak'] <= 1 and costs['upper_pending'] <= 8 and costs['archive'] <= 16
    if measure: verify_metrics(r, w)


def good(e):
    return all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10


def verify_metrics(r,w):
    observed,latent=[],[]
    for t,row in enumerate(w['main'],1):
        p=r['predictions'][t-1]; y=label(w,row['x'],row['a'],t)
        observed.append(logloss(p,row['y']))
        latent.append(.9*logloss(p,y)+.1*logloss(p,1-y))
    tail=[v['evaluation'] for v in r['reviews'] if v['index'] in (1024,1088,1152,1216,1280)]
    assert len(tail)==5
    spec=[1,1]; spec[w['affected']]=2
    captures,retrievals,incompatible=[],[],[]
    for v in r['reviews']:
        u=v['upper']; old=u['ordinary'] if 'ordinary' in u else u
        if old['action']=='retrieved': retrievals.append(v['index'])
        if old['archive_check'] is not None and old['archive_check']['compatible'] is False: incompatible.append(v['index'])
        snapshot,nominated,retained=None,None,True
        if r['policy']=='legacy':
            if old['captured'] is not None: snapshot=old['archive_after']
        else:
            q=u['qualification']
            if q['confirmed'] is not None:
                snapshot=q['confirmed']; nominated=q['witness']['snapshot']['capture_event']; retained=r['policy']=='reserve'
        if snapshot is not None:
            ids=snapshot['record_ids']; times=sorted(int(i.split('/')[1]) for i in ids if i.startswith('main/'))
            captures.append(dict(index=v['index'],nominated=nominated,retained=retained,
                main_first=times[0] if times else None,main_last=times[-1] if times else None,construction_labels=len(ids),
                contains_pre_simplification=bool(times and times[0]<=240) or any(i.startswith('composition/') for i in ids)))
    expected=dict(transfer_valid=good(r['transfer']),final_full=good(tail[-1]),stable_full=all(good(e) for e in tail),
        stable_structure=good(r['transfer']) and all(good(e) and e['spec']==spec and e['sufficient_minimal'] for e in tail),
        raw_reads=sum(r['raw_reads']),captures=captures,retrievals=retrievals,incompatible=incompatible)
    for name,start,stop in [('pre',0,528),('early',528,656),('returned',528,1280),('late',1024,1280)]:
        expected[name+'_observed']=mean(observed[start:stop]); expected[name+'_latent']=mean(latent[start:stop])
    close(r['metrics'],expected)


def verify_summary(runs,saved):
    groups=[]
    for b,p in itertools.product(BRANCHES,POLICIES):
        rs=[r for r in runs if r['branch']==b and r['policy']==p]; ms=[r['metrics'] for r in rs]
        assert len(rs)==10
        g=dict(branch=b,policy=p,runs=10)
        for k in ('transfer_valid','final_full','stable_full','stable_structure'): g[k]=sum(m[k] for m in ms)
        for k in ['raw_reads']+[n+'_'+kind for n in ('pre','early','returned','late') for kind in ('observed','latent')]: g[k]=mean(m[k] for m in ms)
        for k in ('captures','retrievals','incompatible'): g[k]=sum(len(m[k]) for m in ms)
        g['pre_simplification_captures']=sum(c['contains_pre_simplification'] for m in ms for c in m['captures'])
        g['early_confirmations']=sum(any(c['index']<=240 for c in m['captures']) for m in ms)
        g['qualification_queries']=sum(r['memory_costs']['qualification_queries'] for r in rs if r['memory_costs'] is not None)
        groups.append(g)
    pairs=[]
    for s,ps,b in sorted(set((r['seed'],r['proposal_seed'],r['branch']) for r in runs)):
        rs={r['policy']:r for r in runs if (r['seed'],r['proposal_seed'],r['branch'])==(s,ps,b)}
        for control in ('discard','legacy'):
            a,c=rs['reserve']['metrics'],rs[control]['metrics']
            item=dict(seed=s,proposal_seed=ps,branch=b,control=control,
                identical_predictions=rs['reserve']['predictions']==rs[control]['predictions'])
            for name in ('pre','early','returned','late'):
                for kind in ('observed','latent'): item[name+'_'+kind+'_gain']=c[name+'_'+kind]-a[name+'_'+kind]
            pairs.append(item)
    checks={}
    for b in BRANCHES: checks[b+'_final']=all(g['final_full']>=8 for g in groups if g['branch']==b)
    for c in ('discard','legacy'):
        ds=[p for p in pairs if p['branch']=='detail' and p['control']==c]
        rev=[p for p in pairs if p['branch']=='reversed' and p['control']==c]
        checks[c+'_early_gain']=mean(p['early_observed_gain'] for p in ds)>=.02
        checks[c+'_improving_pairs']=sum(p['early_observed_gain']>0 for p in ds)>=8
        checks[c+'_reversed_cost']=mean(p['early_observed_gain'] for p in rev)>=-.02
        for b in BRANCHES:
            for kind in ('observed','latent'):
                checks[c+'_'+b+'_pre_'+kind]=mean(p['pre_'+kind+'_gain'] for p in pairs if p['branch']==b and p['control']==c)>=-.02
    env=[]
    for s,b,c in sorted(set((p['seed'],p['branch'],p['control']) for p in pairs)):
        ps=[p for p in pairs if (p['seed'],p['branch'],p['control'])==(s,b,c)]
        env.append(dict(seed=s,branch=b,control=c,proposals=len(ps),early_gain=mean(p['early_observed_gain'] for p in ps),early_latent_gain=mean(p['early_latent_gain'] for p in ps)))
    close(saved,dict(groups=groups,paired=pairs,environments=env,checks=checks,primary_pass=all(checks.values())))


def main():
    started=time.monotonic()
    def timeout(*_): raise TimeoutError('600-second 021 audit limit')
    signal.signal(signal.SIGALRM,timeout); signal.alarm(600)
    try:
        manifest=json.loads((OUT/'manifest.json').read_text())
        for name,digest in manifest.items(): assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
        data=json.loads((OUT/'results.json').read_text())
        assert data['hashes']==manifest and data['status']=='completed_pending_audit'
        worlds=json.loads((OUT/'worlds.json').read_text()); lookup={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==10 and set(lookup)==set(itertools.product(range(1000,1005),BRANCHES))
        for w in worlds:
            assert list(map(len,w['local_main']))==[256]*2 and len(w['local_selection'])==4
            assert all(list(map(len,b))==[32]*2 for b in w['local_selection'])
            assert len(w['composition'])==256 and len(w['main'])==1280 and list(map(len,w['selection']))==[32]*20
            verify_world(w)
        with gzip.open(OUT/'runs.jsonl.gz','rt') as f: runs=[json.loads(line) for line in f]
        assert len(runs)==60 and {(r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs}==set(itertools.product(range(1000,1005),(1000,1001),BRANCHES,POLICIES))
        for i,r in enumerate(runs,1):
            with gzip.open(OUT/r['checkpoint_file'],'rt') as f: checkpoint=json.load(f)
            verify_run(r,lookup[r['seed'],r['branch']],checkpoint)
            assert r['costs']['feedback_labels']==6784
            if i%12==0: print(f'{i}/60 memory policies, full traces and checkpoints verified',flush=True)
        for s in range(1000,1005):
            d,rev=lookup[s,'detail'],lookup[s,'reversed']
            assert d['main'][:528]==rev['main'][:528] and d['selection'][:8]==rev['selection'][:8]
            for ps in (1000,1001):
                rs=[r for r in runs if (r['seed'],r['proposal_seed'])==(s,ps)]
                assert all(r['warmup']==rs[0]['warmup'] for r in rs)
        verify_summary(runs,data['summary'])
        es=[e for r in runs for e in [r['transfer'],*r['endpoints'],*(v['evaluation'] for v in r['reviews'])]]
        totals=dict(runs=60,allocated_labels=407040,generated_labels=67840,
            used_labels=sum(r['costs']['feedback_labels'] for r in runs),
            candidate_fits=sum(r['costs']['candidate_fits']+r['costs']['upper_candidate_fits'] for r in runs),
            scoring_queries=sum(r['costs']['scoring_queries'] for r in runs),composite_predictions=76800,local_predictions=153600,
            evaluation_predictions=sum(e['contexts'] for e in es),
            oracle_context_queries=32*sum(1+len(e['removal_costs'])+len(e['raw_addition_gains']) for e in es),
            qualification_queries=sum(r['memory_costs']['qualification_queries'] for r in runs if r['memory_costs'] is not None))
        close(data['totals'],totals)
        assert totals['used_labels']==407040 and totals['candidate_fits']<=19920 and totals['scoring_queries']<=3000000
        assert totals['evaluation_predictions']==45600 and totals['oracle_context_queries']<=230400
        assert data['elapsed_seconds']<600
        fixture=json.loads((ROOT/'results/prospective-memory-fixtures.json').read_text())
        assert fixture['status']=='pass' and fixture['charged_labels']<=2500
        result=dict(status='pass',runs=60,independently_replayed_labels=407040,elapsed_seconds=time.monotonic()-started,
            artifact_sha256={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('results.json','runs.jsonl.gz','worlds.json')})
        (OUT/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
        print('PASS: all 60 memory runs independently reconstructed and verified.')
    except Exception as exc:
        (OUT/'audit-incomplete.json').write_text(json.dumps(dict(error=repr(exc),elapsed_seconds=time.monotonic()-started),indent=2)+'\n')
        raise
    finally: signal.alarm(0)


if __name__=='__main__': main()
