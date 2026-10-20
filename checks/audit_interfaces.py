"""Independent replay of Experiment 012, using only independent arithmetic helpers."""
import copy
import hashlib
import itertools
import json
import math
from pathlib import Path
import random
import statistics as st

from audit_bundles import close, table, predict, saved_state, nll, cost, SUBSETS, CONTEXTS, H

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/interfaces-v1'
BRANCHES = ('return','novel','persistent')
VARIANTS = ('retain','delete','open')
ENDS = (384,768,1152)
BASE_COSTS = ('main_prediction_feature_reads','count_refits','count_refit_rows',
              'refit_feature_reads','candidate_fits','candidate_fit_rows',
              'candidate_fit_feature_reads','candidate_score_feature_reads',
              'selection_outcomes','selection_prediction_feature_reads')


def world_check(w):
    perm = list(range(6))
    random.Random(20000+w['seed']).shuffle(perm)
    assert w['permutation']==perm
    def row(rng,t):
        raw = [rng.randrange(2) for _ in range(6)]
        a = rng.randrange(2)
        e = rng.random()<.1
        y = raw[0]+a+int(e)
        if w['branch']=='persistent' or not 384<t<=768:
            y += raw[1]
        if w['branch']=='novel' and t>768:
            y += 1
        return {'x':[raw[i] for i in perm],'a':a,'y':y%2}
    rng = random.Random(30000+w['seed'])
    assert w['main']==[row(rng,t) for t in range(1,1153)]
    rng = random.Random(40000+w['seed'])
    assert w['selection']==[[row(rng,t) for _ in range(32)] for t in range(64,1153,64)]


def score(subset,counts,rows):
    return st.mean(nll(predict(subset,counts,r['x'],r['a']),r['y']) for r in rows)


def check_evaluation(ev,subset,counts,w,t,source,archive):
    relevant = [w['permutation'].index(0)]
    if w['branch']=='persistent' or not 384<t<=768:
        relevant += [w['permutation'].index(1)]
    relevant.sort()
    ps,losses,cuts = [],[],{str(d):[] for d in subset}
    correct = 0
    for x in CONTEXTS:
        for a in (0,1):
            target = (a+sum(x[d] for d in relevant)+int(w['branch']=='novel' and t>768))%2
            q = .9 if target else .1
            p = predict(subset,counts,x,a)
            ps.append(p)
            losses.append(-q*math.log(p)-(1-q)*math.log1p(-p))
            correct += (p>.5)==bool(target)
            for d in subset:
                other = list(x)
                other[d] = 1-other[d]
                value = (p+predict(subset,counts,other,a))/2
                cuts[str(d)].append(-q*math.log(value)-(1-q)*math.log1p(-value))
    loss = st.mean(losses)
    close(ev,{'index':t,'subset':list(subset),'source':source,'relevant':relevant,
              'predictions':ps,'expected_loss':loss,'regret':loss-H,'accuracy':correct/128,
              'exact_structure':list(subset)==relevant,
              'cut_loss_increase':{d:st.mean(ls)-loss for d,ls in cuts.items()},
              'visible_cells':2**(len(subset)+1),
              'archive_cells':0 if archive is None else 2**(len(archive[0])+1),
              'base_predictions':128,'additional_ablation_predictions':128*len(subset)})


def verify_run(r,w):
    subset,counts,buffer,deck = (),{},[],[]
    deck_number = 0
    rng = random.Random(50000+r['proposal_seed'])
    source,archive,parent = 'fresh',None,None
    costs = dict.fromkeys(BASE_COSTS,0)
    losses = []
    assert len(r['reviews'])==len(r['evaluations'])==18
    assert len(r['main_predictions'])==len(r['feature_reads'])==1152
    def state():
        return {'parent':list(parent),'model':saved_state(subset,counts),'source':source,
                'prototype':None if archive is None else saved_state(*archive)}
    for t,row in enumerate(w['main'],1):
        p = predict(subset,counts,row['x'],row['a'])
        close(r['main_predictions'][t-1],p)
        assert r['feature_reads'][t-1]==len(subset)
        costs['main_prediction_feature_reads'] += len(subset)
        if t>384:
            costs['main_prototype_steps'] += source=='prototype'
        losses.append(nll(p,row['y']))
        buffer = (buffer+[row])[-192:]
        if source=='fresh':
            counts = table(subset,buffer)
            costs['count_refits'] += 1
            costs['count_refit_rows'] += len(buffer)
            costs['refit_feature_reads'] += len(buffer)*len(subset)
        if t%64:
            continue
        review = r['reviews'][t//64-1]
        assert review['index']==t
        if t<=384:
            close(review['before'],saved_state(subset,counts))
            proposed = []
            while len(proposed)<4:
                if not deck:
                    deck = SUBSETS.copy()
                    rng.shuffle(deck)
                    deck_number += 1
                item = deck.pop(0)
                if item!=subset and item not in proposed:
                    proposed.append(item)
            close(review['deck'],deck)
            assert review['deck_number']==deck_number and review['cursor']==0
            assert [tuple(c['subset']) for c in review['candidates']]==proposed
            fitted = [table(s,buffer) for s in proposed]
            for s,c,saved in zip(proposed,fitted,review['candidates']):
                value = score(s,c,buffer)
                close(saved,{'subset':list(s),'training_loss':value,'penalty':cost(s),'objective':value+cost(s)})
            winner = min(range(4),key=lambda i:(review['candidates'][i]['objective'],proposed[i]))
            assert review['winner']==winner
            candidate,cs = proposed[winner],fitted[winner]
            batch = w['selection'][t//64-1]
            old = [nll(predict(subset,counts,x['x'],x['a']),x['y']) for x in batch]
            new = [nll(predict(candidate,cs,x['x'],x['a']),x['y']) for x in batch]
            delta = [a-b for a,b in zip(old,new)]
            complexity = cost(subset)-cost(candidate)
            gain = st.mean(delta)+complexity
            halves = [st.mean(delta[i:i+16])+complexity for i in (0,16)]
            close(review['decision'],{
                'incumbent_loss':st.mean(old),'candidate_loss':st.mean(new),
                'prediction_gain':st.mean(delta),'complexity_gain':complexity,'gain':gain,
                'half_gains':halves,'pooled_accept':gain>.005,
                'corroborated_accept':min(halves)>.005,'accepted':gain>.005,'veto':False})
            costs['candidate_fits'] += 4
            costs['candidate_fit_rows'] += 4*len(buffer)
            reads = len(buffer)*sum(len(s) for s in proposed)
            costs['candidate_fit_feature_reads'] += reads
            costs['candidate_score_feature_reads'] += reads
            costs['selection_outcomes'] += 32
            costs['selection_prediction_feature_reads'] += 32*(len(subset)+len(candidate))
            if gain>.005:
                subset,counts = candidate,cs
            close(review['after'],saved_state(subset,counts))
            check_evaluation(r['evaluations'][t//64-1],subset,counts,w,t,'fresh',None)
            if t==384:
                parent = subset
                archive = None if r['variant']=='open' else (parent,copy.deepcopy(counts))
                assert r['parent']==list(parent)
                close(r['interface_initial_state'],state())
                costs.update(prototype_candidate_scores=0,prototype_selection_predictions=0,main_prototype_steps=0)
        else:
            close(review['before'],state())
            if r['variant']!='open':
                models = []
                for n in range(len(parent)+1):
                    for s in itertools.combinations(parent,n):
                        if not(source=='fresh' and s==subset):
                            models.append(('fresh',s,table(s,buffer)))
                if archive is not None and len(subset)<len(parent):
                    models.append(('prototype',archive[0],copy.deepcopy(archive[1])))
                assert len(review['candidates'])==len(models)<=4
                for (kind,s,c),saved in zip(models,review['candidates']):
                    value = score(s,c,buffer[-64:])
                    close(saved,{'source':kind,'state':saved_state(s,c),'training_loss':value,
                                 'penalty':cost(s),'objective':value+cost(s)})
                    if kind=='fresh':
                        costs['candidate_fits'] += 1
                        costs['candidate_fit_rows'] += len(buffer)
                        costs['candidate_fit_feature_reads'] += len(buffer)*len(s)
                    else:
                        costs['prototype_candidate_scores'] += 1
                    costs['candidate_score_feature_reads'] += len(buffer[-64:])*len(s)
                winner = min(range(len(models)),key=lambda i:(
                    review['candidates'][i]['objective'],models[i][1],models[i][0])) if models else None
                assert review['winner']==winner
                if winner is None:
                    assert review['decision'] is None
                else:
                    kind,s,c = models[winner]
                    batch = w['selection'][t//64-1]
                    old_loss,new_loss = score(subset,counts,batch),score(s,c,batch)
                    complexity = cost(subset)-cost(s)
                    gain = old_loss-new_loss+complexity
                    close(review['decision'],{'incumbent_loss':old_loss,'candidate_loss':new_loss,
                                             'prediction_gain':old_loss-new_loss,'complexity_gain':complexity,
                                             'gain':gain,'accepted':gain>.005})
                    costs['selection_outcomes'] += 32
                    costs['selection_prediction_feature_reads'] += 32*(len(subset)+len(s))
                    costs['prototype_selection_predictions'] += 32*(kind=='prototype')
                    if gain>.005:
                        if r['variant']=='delete' and len(s)<len(parent):
                            archive = None
                        subset,counts,source = s,c,kind
            else:
                assert set(review)=={'index','before','after'}
            close(review['after'],state())
            check_evaluation(r['evaluations'][t//64-1],subset,counts,w,t,source,archive)
    close(r['costs'],costs)
    evs = {e['index']:e for e in r['evaluations']}
    valid = lambda e:e['exact_structure'] and e['accuracy']==1 and e['regret']<=.1
    hide,reopen,retrieve,deleted = [],[],[],[]
    for review in r['reviews'][6:]:
        a,b = review['before'],review['after']
        if len(a['model']['subset'])==len(parent) and len(b['model']['subset'])<len(parent):
            hide.append(review['index'])
        if len(a['model']['subset'])<len(parent) and len(b['model']['subset'])==len(parent):
            reopen.append(review['index'])
        if review.get('decision') and review['decision']['accepted']:
            if b['source']=='prototype':
                retrieve.append(review['index'])
            if a['prototype'] is not None and b['prototype'] is None:
                deleted.append(review['index'])
    final = valid(evs[1152]) and all(evs[1152]['cut_loss_increase'].get(str(d),0)>=.15 for d in evs[1152]['relevant'])
    if w['branch']=='persistent':
        middle = valid(evs[768]) and all(e['subset']==evs[384]['relevant'] for e in r['evaluations'][6:])
    else:
        middle = valid(evs[768]) and any(384<i<=768 for i in hide)
        if r['variant']=='retain':
            middle = middle and evs[768]['archive_cells']>0
    close(r['metrics'],{
        'acquisition_pass':valid(evs[384]),'middle_pass':middle,'final_pass':final,
        'trajectory_pass':valid(evs[384]) and middle and final,
        'hide_reviews':hide,'reopen_reviews':reopen,'retrieval_reviews':retrieve,'deletion_reviews':deleted,
        'predictive_recovery':next((e['index'] for e in r['evaluations'] if e['index']>768 and valid(e)),None),
        'phase_main_loss':[st.mean(losses[i:i+384]) for i in (0,384,768)],
        'return192_loss':st.mean(losses[768:960]),'post_acquisition_loss':st.mean(losses[384:]),
        'main_loss':st.mean(losses),'mean_post_prediction_features':sum(r['feature_reads'][384:])/768,
        'max_total_model_cells':max(e['visible_cells']+e['archive_cells'] for e in r['evaluations']),
        'stale_retrievals':sum(i>768 for i in retrieve) if w['branch']=='novel' else 0})


def verify_summary(runs,summary):
    groups = []
    for branch in BRANCHES:
        for variant in VARIANTS:
            rs = [r for r in runs if r['branch']==branch and r['variant']==variant]
            groups.append({
                'branch':branch,'variant':variant,'runs':10,
                'acquisition_passes':sum(r['metrics']['acquisition_pass'] for r in rs),
                'trajectory_passes':sum(r['metrics']['trajectory_pass'] for r in rs),
                'endpoint_losses':[st.mean(next(e['expected_loss'] for e in r['evaluations'] if e['index']==t) for r in rs) for t in ENDS],
                'phase_main_loss':[st.mean(r['metrics']['phase_main_loss'][i] for r in rs) for i in range(3)],
                'return192_loss':st.mean(r['metrics']['return192_loss'] for r in rs),
                'post_acquisition_loss':st.mean(r['metrics']['post_acquisition_loss'] for r in rs),
                'post_prediction_features':st.mean(r['metrics']['mean_post_prediction_features'] for r in rs),
                'retrievals':sum(len(r['metrics']['retrieval_reviews']) for r in rs),
                'prototype_main_steps':sum(r['costs']['main_prototype_steps'] for r in rs),
                'stale_retrievals':sum(r['metrics']['stale_retrievals'] for r in rs)})
    paired = []
    for branch in BRANCHES:
        for seed in range(200,205):
            for ps in (200,201):
                data = {r['variant']:r['metrics'] for r in runs if (
                    r['branch'],r['seed'],r['proposal_seed'])==(branch,seed,ps)}
                paired.append({'branch':branch,'seed':seed,'proposal_seed':ps,
                               'delete_minus_retain_return192':data['delete']['return192_loss']-data['retain']['return192_loss'],
                               'retain_minus_open_post':data['retain']['post_acquisition_loss']-data['open']['post_acquisition_loss']})
    gains = [r['delete_minus_retain_return192'] for r in paired if r['branch']=='return']
    checks = {
        'trajectories':all(g['trajectory_passes']>=8 for g in groups if g['variant']=='retain'),
        'return_improved_count':sum(v>0 for v in gains)>=8,
        'return_mean_gain':st.mean(gains)>=.02,
        'novel_cost_guard':-st.mean(r['delete_minus_retain_return192'] for r in paired if r['branch']=='novel')<=.02,
        'persistent_cost_guard':st.mean(r['retain_minus_open_post'] for r in paired if r['branch']=='persistent')<=.02}
    close(summary,{'groups':groups,'paired':paired,'checks':checks,'primary_pass':all(checks.values())})


def main():
    data = json.loads((OUT/'results.json').read_text())
    manifest = json.loads((OUT/'manifest.json').read_text())
    assert manifest==data['hashes']
    assert set(manifest)=={'experiments/interfaces_protocol.md','experiments/interfaces.py',
                          'checks/test_interfaces.py','checks/audit_interfaces.py',
                          'experiments/bundles.py','experiments/bundle_retention.py','checks/audit_bundles.py'}
    for m in [manifest]+[json.loads((ROOT/'results'/f/'manifest.json').read_text())
                         for f in ('bundles-v1','bundle-retention-v1')]:
        for name,digest in m.items():
            assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    worlds = {f"{w['seed']}-{w['branch']}":w for w in data['worlds']}
    assert len(worlds)==len(data['worlds'])==15
    assert set(worlds)=={f'{s}-{b}' for s in range(200,205) for b in BRANCHES}
    for w in worlds.values():
        world_check(w)
    runs = data['runs']
    assert len(runs)==90
    assert {(r['world'],r['variant'],r['proposal_seed']) for r in runs}=={
        (w,v,s) for w in worlds for v in VARIANTS for s in (200,201)}
    for r in runs:
        assert r['world']==f"{r['seed']}-{r['branch']}"
        verify_run(r,worlds[r['world']])
    # Shared acquisition must be identical across variants AND all branches.
    for seed in range(200,205):
        for ps in (200,201):
            rs = [r for r in runs if r['seed']==seed and r['proposal_seed']==ps]
            for r in rs[1:]:
                assert r['main_predictions'][:384]==rs[0]['main_predictions'][:384]
                assert r['reviews'][:6]==rs[0]['reviews'][:6]
    verify_summary(runs,data['comparison'])
    costs = {k:sum(r['costs'][k] for r in runs) for k in runs[0]['costs']}
    assert costs['candidate_fits']<=5040 and costs['selection_outcomes']<=40320
    close(data['totals'],{
        'runs':90,'generated_world_records':25920,'allocated_outcome_presentations':155520,
        'used_outcome_presentations':103680+costs['selection_outcomes'],
        'base_evaluation_predictions':207360,
        'additional_ablation_predictions':sum(e['additional_ablation_predictions'] for r in runs for e in r['evaluations']),
        'costs':costs})
    close(json.loads((OUT/'metrics.json').read_text()),{
        'comparison':data['comparison'],'totals':data['totals'],
        'runs':[{k:r[k] for k in ('world','variant','proposal_seed','parent','metrics','costs')} for r in runs]})
    print('PASS: 90 traces independently replayed, including shared acquisition, '
          'hidden/deleted snapshots, frozen retrieval, interfaces, selection, metrics, costs and three manifests.')


if __name__=='__main__':
    main()
