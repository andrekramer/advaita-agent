"""Independent Experiment 011 replay; imports only prior independent audit helpers."""
import hashlib
import json
from pathlib import Path
import random
import statistics as st

from audit_bundles import close, check_world, check_evaluation, table, predict, saved_state, nll, cost, SUBSETS

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'results/bundle-retention-v1'
VARIANTS = ('iid_single', 'deck_single', 'iid_split', 'deck_split')
ENDS = (384,768,1152)


def check_run(run, world):
    subset, counts, window, deck = (), {}, [], []
    deck_number = 0
    rng = random.Random(50000 + run['proposal_seed'])
    keys = ('main_prediction_feature_reads', 'count_refits', 'count_refit_rows',
            'refit_feature_reads', 'candidate_fits', 'candidate_fit_rows',
            'candidate_fit_feature_reads', 'candidate_score_feature_reads',
            'selection_outcomes', 'selection_prediction_feature_reads')
    costs = dict.fromkeys(keys, 0)
    losses = []
    assert len(run['main_predictions']) == 1152
    assert len(run['reviews']) == len(run['evaluations']) == 18
    for index, row in enumerate(world['main'], 1):
        p = predict(subset, counts, row['x'], row['a'])
        close(run['main_predictions'][index-1], p)
        losses.append(nll(p,row['y']))
        costs['main_prediction_feature_reads'] += len(subset)
        window = (window+[row])[-192:]
        counts = table(subset,window)
        costs['count_refits'] += 1
        costs['count_refit_rows'] += len(window)
        costs['refit_feature_reads'] += len(window)*len(subset)
        if index % 64:
            continue
        review = run['reviews'][index//64-1]
        assert review['index'] == index and review['cursor'] == 0
        close(review['before'], saved_state(subset,counts))
        if run['variant'].startswith('iid'):
            proposals = rng.sample([s for s in SUBSETS if s != subset],4)
        else:
            proposals = []
            while len(proposals) != 4:
                if len(deck) == 0:
                    deck = SUBSETS.copy()
                    rng.shuffle(deck)
                    deck_number += 1
                item, deck = deck[0], deck[1:]
                if item != subset and item not in proposals:
                    proposals.append(item)
        close(review['deck'],deck)
        assert review['deck_number'] == deck_number
        assert [tuple(c['subset']) for c in review['candidates']] == proposals
        fitted = [table(s,window) for s in proposals]
        for s,c,saved in zip(proposals,fitted,review['candidates']):
            loss = st.mean(nll(predict(s,c,r['x'],r['a']),r['y']) for r in window)
            close(saved,{'subset':list(s),'training_loss':loss,'penalty':cost(s),'objective':loss+cost(s)})
        # Independently verified objectives above; use saved float bits only to
        # resolve exact machine-level ranking ties consistently with the run.
        winner = min(range(4),key=lambda i:(review['candidates'][i]['objective'],proposals[i]))
        assert review['winner'] == winner
        candidate, candidate_counts = proposals[winner],fitted[winner]
        batch = world['selection'][index//64-1]
        before = [nll(predict(subset,counts,r['x'],r['a']),r['y']) for r in batch]
        after = [nll(predict(candidate,candidate_counts,r['x'],r['a']),r['y']) for r in batch]
        advantages = [a-b for a,b in zip(before,after)]
        complexity = cost(subset)-cost(candidate)
        gain = st.mean(advantages)+complexity
        halves = [st.mean(advantages[:16])+complexity,st.mean(advantages[16:])+complexity]
        pooled, split = gain>.005, min(halves)>.005
        accept = split if run['variant'].endswith('split') else pooled
        close(review['decision'],{
            'incumbent_loss':st.mean(before),'candidate_loss':st.mean(after),
            'prediction_gain':st.mean(advantages),'complexity_gain':complexity,'gain':gain,
            'half_gains':halves,'pooled_accept':pooled,'corroborated_accept':split,
            'accepted':accept,'veto':run['variant'].endswith('split') and pooled and not split})
        costs['candidate_fits'] += 4
        costs['candidate_fit_rows'] += 4*len(window)
        reads = len(window)*sum(len(s) for s in proposals)
        costs['candidate_fit_feature_reads'] += reads
        costs['candidate_score_feature_reads'] += reads
        costs['selection_outcomes'] += 32
        costs['selection_prediction_feature_reads'] += 32*(len(subset)+len(candidate))
        if accept:
            subset,counts = candidate,candidate_counts
        close(review['after'],saved_state(subset,counts))
        check_evaluation(run['evaluations'][index//64-1],subset,counts,world,index)
    close(run['costs'],costs)
    evs = run['evaluations']
    endpoints = [e for e in evs if e['index'] in ENDS]
    basic = all(e['exact_structure'] and e['accuracy']==1 and e['regret']<=.1 for e in endpoints)
    cuts = all(min(e['cut_loss_increase'].get(str(d),0) for d in e['relevant'])>=.15
               for e in endpoints if e['index']!=768)
    first = {str(t):next((e['index'] for e in evs if t-384<e['index']<=t and e['exact_structure']
                         and e['accuracy']==1 and e['regret']<=.1),None) for t in ENDS}
    pair = sorted([world['permutation'].index(0),world['permutation'].index(1)])
    acquired = next((e['index'] for e in evs if e['subset']==pair and e['accuracy']==1 and e['regret']<=.1),None)
    departures = [r['index'] for r in run['reviews'] if acquired is not None and r['index']>acquired
                  and r['before']['subset']==pair and r['after']['subset']!=pair]
    preserved = acquired is not None and not departures
    coverage = {}
    for t in (384,1152):
        visited = set()
        for r in run['reviews']:
            if t-384<r['index']<=t:
                visited.add(tuple(r['before']['subset']))
                visited.update(tuple(c['subset']) for c in r['candidates'])
        coverage[str(t)] = {'relevant_seen':tuple(pair) in visited,'visited':len(visited),
                            'fraction':len(visited)/22}
    close(run['metrics'],{
        'phase_main_loss':[st.mean(losses[i:i+384]) for i in (0,384,768)],
        'transition64_loss':[st.mean(losses[i:i+64]) for i in (384,768)],
        'main_loss':st.mean(losses),'first_successful_review':first,'first_successful_pair':acquired,
        'correct_pair_departures':departures,
        'persistent_preservation':preserved if world['branch']=='persistent' else None,
        'endpoint_pass':basic and cuts,'coverage':coverage,
        'accepted_changes':sum(r['decision']['accepted'] for r in run['reviews']),
        'vetoes':sum(r['decision']['veto'] for r in run['reviews']),
        'pass':basic and cuts and (world['branch']!='persistent' or preserved)})


def check_summary(runs, summary):
    groups = []
    for branch in ('reversible','persistent'):
        for variant in VARIANTS:
            rs = [r for r in runs if r['branch']==branch and r['variant']==variant]
            groups.append({
                'branch':branch,'variant':variant,'runs':10,
                'passes':sum(r['metrics']['pass'] for r in rs),
                'endpoint_passes':sum(r['metrics']['endpoint_pass'] for r in rs),
                'persistent_preserved':sum(bool(r['metrics']['persistent_preservation']) for r in rs) if branch=='persistent' else None,
                'departures':sum(len(r['metrics']['correct_pair_departures']) for r in rs) if branch=='persistent' else None,
                'pair_phase_coverage':[sum(r['metrics']['coverage'][str(t)]['relevant_seen'] for r in rs) for t in (384,1152)],
                'mean_visited_fraction':[st.mean(r['metrics']['coverage'][str(t)]['fraction'] for r in rs) for t in (384,1152)],
                'endpoint_loss':[st.mean(next(e['expected_loss'] for e in r['evaluations'] if e['index']==t) for r in rs) for t in ENDS],
                'main_loss':st.mean(r['metrics']['main_loss'] for r in rs),
                'phase_main_loss':[st.mean(r['metrics']['phase_main_loss'][i] for r in rs) for i in range(3)],
                'transition64_loss':[st.mean(r['metrics']['transition64_loss'][i] for r in rs) for i in range(2)],
                'vetoes':sum(r['metrics']['vetoes'] for r in rs)})
    close(summary['groups'],groups)
    assert summary['primary_pass']==all(g['passes']>=8 for g in groups if g['variant']=='deck_split')
    assert len(summary['paired'])==8
    expected_pairs = {(branch,a,b) for branch in ('reversible','persistent') for a,b in (
        ('iid_single','deck_single'),('iid_split','deck_split'),
        ('iid_single','iid_split'),('deck_single','deck_split'))}
    assert {(g['branch'],g['from'],g['to']) for g in summary['paired']}==expected_pairs
    lookup = {(r['seed'],r['proposal_seed'],r['branch'],r['variant']):r for r in runs}
    for group in summary['paired']:
        expected = []
        for seed in range(100,105):
            for ps in (100,101):
                a = lookup[seed,ps,group['branch'],group['from']]['metrics']
                b = lookup[seed,ps,group['branch'],group['to']]['metrics']
                expected.append({'seed':seed,'proposal_seed':ps,'main_loss_delta':b['main_loss']-a['main_loss'],
                                 'pass_delta':int(b['pass'])-int(a['pass'])})
        close(group['pairs'],expected)


def main():
    data = json.loads((OUT/'results.json').read_text())
    manifest = json.loads((OUT/'manifest.json').read_text())
    assert manifest==data['hashes']
    assert set(manifest)=={'experiments/bundle_retention_protocol.md','experiments/bundle_retention.py',
                          'checks/test_bundle_retention.py','checks/audit_bundle_retention.py',
                          'experiments/bundles.py','checks/audit_bundles.py'}
    for source in (manifest,json.loads((ROOT/'results/bundles-v1/manifest.json').read_text())):
        for path,digest in source.items():
            assert hashlib.sha256((ROOT/path).read_bytes()).hexdigest()==digest,path
    worlds = {f"{w['seed']}-{w['branch']}":w for w in data['worlds']}
    assert len(data['worlds'])==10 and set(worlds)=={
        f'{s}-{b}' for s in range(100,105) for b in ('reversible','persistent')}
    for w in worlds.values():
        check_world(w)
    runs = data['runs']
    assert len(runs)==80
    assert {(r['world'],r['variant'],r['proposal_seed']) for r in runs}=={
        (w,v,s) for w in worlds for v in VARIANTS for s in (100,101)}
    for r in runs:
        assert r['world']==f"{r['seed']}-{r['branch']}"
        check_run(r,worlds[r['world']])
    check_summary(runs,data['comparison'])
    costs = {k:sum(r['costs'][k] for r in runs) for k in runs[0]['costs']}
    close(data['totals'],{
        'runs':80,'generated_world_records':17280,'outcome_presentations':138240,
        'base_evaluation_predictions':184320,
        'additional_ablation_predictions':sum(len(e['subset'])*128 for r in runs for e in r['evaluations']),
        'costs':costs})
    assert costs['candidate_fits']==5760 and costs['selection_outcomes']==46080
    close(json.loads((OUT/'metrics.json').read_text()),{
        'comparison':data['comparison'],'totals':data['totals'],
        'runs':[{k:r[k] for k in ('world','variant','proposal_seed','metrics','costs')} for r in runs]})
    print('PASS: 80 traces independently reconstructed; RNG/decks, half-batch gates, '
          'predictions, retention metrics, paired comparisons, costs and both manifests verified.')


if __name__ == '__main__':
    main()
