"""Experiment 012: restricted prediction interfaces with retained or deleted detail."""
import argparse
import copy
import hashlib
import itertools
import json
from pathlib import Path
import statistics as st

from bundles import Model, generate as base_generate, nll, expected_loss, penalty, ORACLE, XS
from bundle_retention import Learner as Acquisition

ROOT = Path(__file__).resolve().parents[1]
VARIANTS = ('retain', 'delete', 'open')
BRANCHES = ('return', 'novel', 'persistent')
ENDS = (384, 768, 1152)
FILES = ('experiments/interfaces_protocol.md', 'experiments/interfaces.py',
         'checks/test_interfaces.py', 'checks/audit_interfaces.py',
         'experiments/bundles.py', 'experiments/bundle_retention.py',
         'checks/audit_bundles.py')


def hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in FILES}


def old_hashes_unchanged():
    for folder in ('bundles-v1', 'bundle-retention-v1'):
        manifest = json.loads((ROOT/'results'/folder/'manifest.json').read_text())
        if any(hashlib.sha256((ROOT/p).read_bytes()).hexdigest() != h for p,h in manifest.items()):
            return False
    return True


def generate(seed, branch):
    world = base_generate(seed, 'persistent' if branch == 'persistent' else 'reversible')
    world['branch'] = branch
    if branch == 'novel':
        for row in world['main'][768:]:
            row['y'] ^= 1
        for batch in world['selection'][12:]:
            for row in batch:
                row['y'] ^= 1
    return world


class VisibleInput:
    """A predictive client can access only the interface's named coordinates."""
    def __init__(self, raw, allowed):
        self._raw = raw
        self.allowed = frozenset(allowed)
        self.reads = 0

    def __getitem__(self, key):
        if key not in self.allowed:
            raise PermissionError(f'Coordinate {key} is hidden')
        self.reads += 1
        return self._raw[key]


class Boundary:
    def __init__(self, model):
        self.model = copy.deepcopy(model)

    def predict(self, x, action):
        view = VisibleInput(x, self.model.subset)
        p = self.model.predict(view, action)
        return p, view.reads


class Learner:
    def __init__(self, variant, model, buffer, costs):
        self.variant = variant
        self.parent = tuple(model.subset)
        self.boundary = Boundary(model)
        self.source = 'fresh'
        self.prototype = copy.deepcopy(model) if variant != 'open' else None
        self.buffer = copy.deepcopy(buffer)
        self.costs = copy.deepcopy(costs)
        self.costs.update(prototype_candidate_scores=0, prototype_selection_predictions=0,
                          main_prototype_steps=0)

    @property
    def model(self):
        return self.boundary.model

    def state(self):
        return {'parent': list(self.parent), 'model': self.model.state(), 'source': self.source,
                'prototype': None if self.prototype is None else self.prototype.state()}

    def predict(self, x, action):
        p, reads = self.boundary.predict(x, action)
        self.costs['main_prediction_feature_reads'] += reads
        self.costs['main_prototype_steps'] += self.source == 'prototype'
        return p

    def update(self, row):
        self.buffer = (self.buffer+[row])[-192:]
        if self.source == 'fresh':
            self.boundary = Boundary(Model(self.model.subset, self.buffer))
            self.costs['count_refits'] += 1
            self.costs['count_refit_rows'] += len(self.buffer)
            self.costs['refit_feature_reads'] += len(self.model.subset)*len(self.buffer)

    def prepare(self):
        models = []
        for k in range(len(self.parent)+1):
            for subset in itertools.combinations(self.parent, k):
                if self.source == 'fresh' and subset == self.model.subset:
                    continue
                models.append(('fresh', Model(subset, self.buffer)))
        if self.prototype is not None and len(self.model.subset) < len(self.parent):
            models.append(('prototype', copy.deepcopy(self.prototype)))
        ranked = []
        for source, model in models:
            loss = model.mean_loss(self.buffer[-64:])
            ranked.append({'source': source, 'state': model.state(), 'training_loss': loss,
                           'penalty': penalty(model.subset), 'objective': loss+penalty(model.subset)})
            if source == 'fresh':
                self.costs['candidate_fits'] += 1
                self.costs['candidate_fit_rows'] += len(self.buffer)
                self.costs['candidate_fit_feature_reads'] += len(model.subset)*len(self.buffer)
            else:
                self.costs['prototype_candidate_scores'] += 1
            self.costs['candidate_score_feature_reads'] += len(model.subset)*len(self.buffer[-64:])
        winner = min(range(len(models)), key=lambda i: (
            ranked[i]['objective'], models[i][1].subset, models[i][0])) if models else None
        return (models[winner] if winner is not None else None), {'candidates': ranked, 'winner': winner}

    def select(self, candidate, rows):
        # Empty K can yield no candidate; the batch is still allocated, but unused.
        if candidate is None:
            return None
        source, model = candidate
        old_loss, new_loss = self.model.mean_loss(rows), model.mean_loss(rows)
        complexity = penalty(self.model.subset)-penalty(model.subset)
        gain = old_loss-new_loss+complexity
        accepted = gain > .005
        self.costs['selection_outcomes'] += len(rows)
        self.costs['selection_prediction_feature_reads'] += len(rows)*(len(self.model.subset)+len(model.subset))
        self.costs['prototype_selection_predictions'] += len(rows)*(source == 'prototype')
        if accepted:
            if self.variant == 'delete' and len(model.subset) < len(self.parent):
                self.prototype = None
            self.boundary = Boundary(model)
            self.source = source
        return {'incumbent_loss': old_loss, 'candidate_loss': new_loss,
                'prediction_gain': old_loss-new_loss,
                'complexity_gain': complexity, 'gain': gain, 'accepted': accepted}


def evaluate(model, world, index, source, prototype):
    relevant = [world['permutation'].index(0)]
    if world['branch'] == 'persistent' or not 384 < index <= 768:
        relevant.append(world['permutation'].index(1))
    relevant.sort()
    invert = world['branch'] == 'novel' and index > 768
    before = model.state()
    predictions, losses, cuts = [], [], {str(d): [] for d in model.subset}
    correct = 0
    for x in XS:
        for a in (0,1):
            target = (a+sum(x[d] for d in relevant)+int(invert)) % 2
            q = .9 if target else .1
            p = model.predict(VisibleInput(x, model.subset), a)
            predictions.append(p)
            losses.append(expected_loss(p,q))
            correct += (p > .5) == bool(target)
            for d in model.subset:
                other = list(x)
                other[d] ^= 1
                cut = (p+model.predict(VisibleInput(other, model.subset), a))/2
                cuts[str(d)].append(expected_loss(cut,q))
    loss = st.mean(losses)
    assert model.state() == before
    return {'index': index, 'subset': list(model.subset), 'source': source, 'relevant': relevant,
            'predictions': predictions, 'expected_loss': loss, 'regret': loss-ORACLE,
            'accuracy': correct/128, 'exact_structure': list(model.subset) == relevant,
            'cut_loss_increase': {d:st.mean(ls)-loss for d,ls in cuts.items()},
            'visible_cells': len(model.counts), 'archive_cells': 0 if prototype is None else len(prototype.counts),
            'base_predictions':128, 'additional_ablation_predictions':128*len(model.subset)}


def metrics(r, world):
    evs = {e['index']:e for e in r['evaluations']}
    valid = lambda e: e['exact_structure'] and e['accuracy'] == 1 and e['regret'] <= .10
    acquisition = valid(evs[384])
    hide, reopen, retrieve, delete = [], [], [], []
    parent = r['parent']
    for review in r['reviews'][6:]:
        before, after = review['before'], review['after']
        if len(before['model']['subset']) == len(parent) and len(after['model']['subset']) < len(parent):
            hide.append(review['index'])
        if len(before['model']['subset']) < len(parent) and len(after['model']['subset']) == len(parent):
            reopen.append(review['index'])
        if review.get('decision') and review['decision']['accepted']:
            if after['source'] == 'prototype':
                retrieve.append(review['index'])
            if before['prototype'] is not None and after['prototype'] is None:
                delete.append(review['index'])
    final = valid(evs[1152]) and all(evs[1152]['cut_loss_increase'].get(str(d),0) >= .15 for d in evs[1152]['relevant'])
    if world['branch'] == 'persistent':
        middle = valid(evs[768]) and all(e['subset'] == evs[384]['relevant'] for e in r['evaluations'][6:])
    else:
        middle = valid(evs[768]) and any(384 < i <= 768 for i in hide)
        if r['variant'] == 'retain':
            middle = middle and evs[768]['archive_cells'] > 0
    losses = [nll(p,row['y']) for p,row in zip(r['main_predictions'],world['main'])]
    recovery = next((e['index'] for e in r['evaluations'] if e['index'] > 768 and valid(e)), None)
    return {'acquisition_pass': acquisition, 'middle_pass': middle, 'final_pass': final,
            'trajectory_pass': acquisition and middle and final,
            'hide_reviews':hide, 'reopen_reviews':reopen, 'retrieval_reviews':retrieve,
            'deletion_reviews':delete, 'predictive_recovery':recovery,
            'phase_main_loss':[st.mean(losses[i:i+384]) for i in (0,384,768)],
            'return192_loss':st.mean(losses[768:960]),
            'post_acquisition_loss':st.mean(losses[384:]),
            'main_loss':st.mean(losses),
            'mean_post_prediction_features':sum(r['feature_reads'][384:])/768,
            'max_total_model_cells':max(e['visible_cells']+e['archive_cells'] for e in r['evaluations']),
            'stale_retrievals':sum(i>768 for i in retrieve) if world['branch']=='novel' else 0}


def run(world, variant, proposal_seed):
    warm = Acquisition('deck_single', proposal_seed)
    learner = None
    result = {'world':f"{world['seed']}-{world['branch']}", 'seed':world['seed'],
              'branch':world['branch'], 'variant':variant, 'proposal_seed':proposal_seed,
              'main_predictions':[], 'feature_reads':[], 'reviews':[], 'evaluations':[]}
    for index,row in enumerate(world['main'],1):
        if index <= 384:
            view = VisibleInput(row['x'],warm.model.subset)
            result['main_predictions'].append(warm.predict(view,row['a']))
            result['feature_reads'].append(view.reads)
            warm.update(row)
            if index % 64 == 0:
                review = {'index':index,'before':warm.model.state()}
                candidate, details = warm.prepare()
                review.update(details)
                review['decision'] = warm.select(candidate,world['selection'][index//64-1])
                review['after'] = warm.model.state()
                result['reviews'].append(review)
                snapshot = copy.deepcopy((warm.model.state(),warm.buffer,warm.costs,warm.deck,warm.rng.getstate()))
                result['evaluations'].append(evaluate(warm.model,world,index,'fresh',None))
                assert snapshot == (warm.model.state(),warm.buffer,warm.costs,warm.deck,warm.rng.getstate())
            if index == 384:
                learner = Learner(variant,warm.model,warm.buffer,warm.costs)
                result['parent'] = list(learner.parent)
                result['interface_initial_state'] = learner.state()
        else:
            before_reads = learner.costs['main_prediction_feature_reads']
            result['main_predictions'].append(learner.predict(row['x'],row['a']))
            result['feature_reads'].append(learner.costs['main_prediction_feature_reads']-before_reads)
            learner.update(row)
            if index % 64 == 0:
                review = {'index':index,'before':learner.state()}
                if variant != 'open':
                    candidate,details = learner.prepare()
                    review.update(details)
                    review['decision'] = learner.select(candidate,world['selection'][index//64-1])
                review['after'] = learner.state()
                result['reviews'].append(review)
                snapshot = copy.deepcopy((learner.state(),learner.buffer,learner.costs))
                result['evaluations'].append(evaluate(learner.model,world,index,learner.source,learner.prototype))
                assert snapshot == (learner.state(),learner.buffer,learner.costs)
    result['costs'] = learner.costs
    result['metrics'] = metrics(result,world)
    return result


def compare(runs):
    groups = []
    for branch in BRANCHES:
        for variant in VARIANTS:
            rs = [r for r in runs if r['branch']==branch and r['variant']==variant]
            groups.append({
                'branch':branch,'variant':variant,'runs':len(rs),
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
                rs = {r['variant']:r for r in runs if (r['branch'],r['seed'],r['proposal_seed'])==(branch,seed,ps)}
                paired.append({'branch':branch,'seed':seed,'proposal_seed':ps,
                               'delete_minus_retain_return192':rs['delete']['metrics']['return192_loss']-rs['retain']['metrics']['return192_loss'],
                               'retain_minus_open_post':rs['retain']['metrics']['post_acquisition_loss']-rs['open']['metrics']['post_acquisition_loss']})
    returning = [r for r in paired if r['branch']=='return']
    checks = {
        'trajectories':all(g['trajectory_passes']>=8 for g in groups if g['variant']=='retain'),
        'return_improved_count':sum(r['delete_minus_retain_return192']>0 for r in returning)>=8,
        'return_mean_gain':st.mean(r['delete_minus_retain_return192'] for r in returning)>=.02,
        'novel_cost_guard':-st.mean(r['delete_minus_retain_return192'] for r in paired if r['branch']=='novel')<=.02,
        'persistent_cost_guard':st.mean(r['retain_minus_open_post'] for r in paired if r['branch']=='persistent')<=.02}
    return {'groups':groups,'paired':paired,'checks':checks,'primary_pass':all(checks.values())}


def report(runs, summary, totals):
    lines = ['# Experiment 012: hiding versus deleting predictive detail','',
             f"Primary criterion: **{'PASS' if summary['primary_pass'] else 'FAIL'}**.",'',
             '| Branch | Variant | Acquisition /10 | Trajectory /10 | Endpoint losses | Return-192 loss | Prediction features | Retrievals |',
             '| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |']
    for g in summary['groups']:
        lines.append(f"| {g['branch']} | {g['variant']} | {g['acquisition_passes']} | {g['trajectory_passes']} | "+
                     ' / '.join(f'{v:.6f}' for v in g['endpoint_losses'])+
                     f" | {g['return192_loss']:.6f} | {g['post_prediction_features']:.4f} | {g['retrievals']} |")
    lines += ['','Open is not expected to pass the reduced-interface criterion in return/novel.',
              'Counts include failed acquisition; accuracy is against the most probable noisy-world outcome.',
              '', '## Per-run transitions', '',
              '| World | Variant | Proposal seed | Parent | Hide | Reopen | Retrieve | Delete | Recovery | Pass |',
              '| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |']
    for r in runs:
        m = r['metrics']
        lines.append(f"| {r['world']} | {r['variant']} | {r['proposal_seed']} | {r['parent']} | "+
                     ' | '.join(str(m[k]) for k in ('hide_reviews','reopen_reviews','retrieval_reviews','deletion_reviews','predictive_recovery','trajectory_pass'))+' |')
    lines += ['','## Primary checks','','```json',json.dumps(summary['checks'],indent=2),'```',
              '', '## Resources','','```json',json.dumps(totals,indent=2),'```','']
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/interfaces-v1')
    args = parser.parse_args()
    assert old_hashes_unchanged()
    args.output.mkdir(parents=True,exist_ok=False)
    provenance = hashes()
    (args.output/'manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
    worlds = [generate(s,b) for s in range(200,205) for b in BRANCHES]
    runs = [run(w,v,ps) for w in worlds for ps in (200,201) for v in VARIANTS]
    summary = compare(runs)
    totals = {
        'runs':90,'generated_world_records':25920,'allocated_outcome_presentations':155520,
        'used_outcome_presentations':103680+sum(r['costs']['selection_outcomes'] for r in runs),
        'base_evaluation_predictions':207360,
        'additional_ablation_predictions':sum(e['additional_ablation_predictions'] for r in runs for e in r['evaluations']),
        'costs':{k:sum(r['costs'][k] for r in runs) for k in runs[0]['costs']}}
    assert hashes()==provenance and old_hashes_unchanged()
    payload = {'hashes':provenance,'worlds':worlds,'runs':runs,'comparison':summary,'totals':totals}
    (args.output/'results.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
    (args.output/'metrics.json').write_text(json.dumps({
        'comparison':summary,'totals':totals,
        'runs':[{k:r[k] for k in ('world','variant','proposal_seed','parent','metrics','costs')} for r in runs]},indent=2)+'\n')
    (args.output/'report.md').write_text(report(runs,summary,totals))
    print(json.dumps({'checks':summary['checks'],'primary_pass':summary['primary_pass'],
                      'groups':summary['groups'],'totals':totals},indent=2))


if __name__ == '__main__':
    main()
