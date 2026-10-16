"""Experiment 008: selective collapse, using immutable Experiment 006 primitives."""
import argparse
import copy
import hashlib
import json
import random
import statistics
from pathlib import Path

from forms import CONTEXTS, FormModel, group_for, loss, neighbours

ROOT = Path(__file__).resolve().parents[1]
BRANCHES = ('changed', 'unchanged')
VARIANTS = ('merge_enabled', 'merge_disabled')
WINDOW = 48


def form_count(model):
    return len(model.counts)


def penalty(model):
    return .01 * form_count(model) + .005 * len(model.structure)


def mean_loss(model, rows):
    return statistics.mean(loss(model.predict(r['x'], r['a']), r['y']) for r in rows)


class Learner:
    def __init__(self, allow_merge):
        self.allow_merge = allow_merge
        self.model = FormModel()
        self.buffer = []
        self.seen = 0
        self.costs = {'count_refits': 0, 'count_refit_rows': 0,
                      'candidate_fits': 0, 'candidate_fit_rows': 0,
                      'selection_outcomes': 0}

    def state(self):
        return {'model': self.model.state(), 'seen': self.seen,
                'window_size': len(self.buffer),
                'window_start': max(1, self.seen-WINDOW+1)}

    def predict(self, x, a):
        return self.model.predict(x, a)

    def update(self, x, a, y):
        self.seen += 1
        self.buffer.append({'x': list(x), 'a': a, 'y': y})
        if len(self.buffer) > WINDOW:
            self.buffer.pop(0)
        self.model = FormModel.fit(self.model.structure, self.buffer)
        self.costs['count_refits'] += 1
        self.costs['count_refit_rows'] += len(self.buffer)

    def prepare(self):
        allowed = [s for s in neighbours(self.model.structure)
                   if self.allow_merge or len({k for _, k in s}) >= form_count(self.model)]
        models = [FormModel.fit(s, self.buffer) for s in allowed]
        scores = [m.objective(self.buffer) for m in models]
        best = min(range(len(models)), key=lambda i: (scores[i], models[i].structure))
        self.costs['candidate_fits'] += len(models)
        self.costs['candidate_fit_rows'] += len(models)*len(self.buffer)
        return models[best], {'winner': best, 'candidates': [
            {'state': m.state(), 'training_objective': score,
             'training_loss': mean_loss(m, self.buffer), 'penalty': penalty(m),
             'advanced': i == best}
            for i, (m, score) in enumerate(zip(models, scores))]}

    def select(self, candidate, rows):
        before = [self.model.predict(r['x'], r['a']) for r in rows]
        after = [candidate.predict(r['x'], r['a']) for r in rows]
        incumbent_loss = statistics.mean(loss(p, r['y']) for p, r in zip(before, rows))
        candidate_loss = statistics.mean(loss(p, r['y']) for p, r in zip(after, rows))
        prediction_gain = incumbent_loss-candidate_loss
        complexity_gain = penalty(self.model)-penalty(candidate)
        gain = prediction_gain+complexity_gain
        accepted = gain > .001
        merge = accepted and form_count(candidate) < form_count(self.model)
        if accepted:
            self.model = candidate
        self.costs['selection_outcomes'] += len(rows)
        return {'incumbent_predictions': before, 'candidate_predictions': after,
                'incumbent_loss': incumbent_loss, 'candidate_loss': candidate_loss,
                'prediction_gain': prediction_gain, 'complexity_gain': complexity_gain,
                'gain': gain, 'accepted': accepted, 'merge': merge}


def stream(seed, branch):
    permutation = [0, 1, 2]
    random.Random(seed).shuffle(permutation)
    support = [(raw, a) for raw in CONTEXTS if raw not in ((0,0,0),(1,1,1)) for a in (0,1)]
    tr, vr = random.Random(8000+seed), random.Random(9000+seed)
    training, selection = [], []
    for block in range(16):
        rows = support.copy(); tr.shuffle(rows)
        for raw, a in rows:
            training.append({'x': [raw[j] for j in permutation], 'a': a,
                             'y': a if branch == 'changed' and block >= 8 else raw[0]^a})
    for boundary in (48,96,144,192):
        rows = support.copy(); vr.shuffle(rows)
        selection.append([{'x': [raw[j] for j in permutation], 'a': a,
                           'y': a if branch == 'changed' and boundary > 96 else raw[0]^a}
                          for raw,a in rows])
    return permutation, training, selection


def evaluate(learner, relevant, collapsed_world):
    snapshot = copy.deepcopy(learner.state())
    old_buffer = copy.deepcopy(learner.buffer)
    table = [{'x':list(x),'a':a,'p':learner.predict(x,a)} for x in CONTEXTS for a in (0,1)]
    held = [{**r,'y':r['a'] if collapsed_world else r['x'][relevant]^r['a']}
            for r in table if tuple(r['x']) in ((0,0,0),(1,1,1))]
    assignments = [group_for(learner.model.structure,x) for x in CONTEXTS]
    p = {(tuple(r['x']),r['a']):r['p'] for r in table}
    effects = [[],[],[]]
    for x in CONTEXTS:
        for d in range(3):
            other = list(x); other[d] ^= 1
            effects[d].extend(abs(p[x,a]-p[tuple(other),a]) for a in (0,1))
    metrics = {'accuracy':sum((r['p']>.5)==r['y'] for r in held)/4,
               'loss':statistics.mean(loss(r['p'],r['y']) for r in held),
               'forms':form_count(learner.model),'leaves':len(learner.model.structure),
               'partition_matches_relevant_bit':all(
                   (assignments[i]==assignments[j])==(x[relevant]==y[relevant])
                   for i,x in enumerate(CONTEXTS) for j,y in enumerate(CONTEXTS) if i<j),
               'context_effect':max(max(v) for v in effects),
               'nuisance_effect':max(max(effects[d]) for d in range(3) if d!=relevant),
               'relevant_effect':min(effects[relevant]),
               'action_effect':min(abs(p[x,0]-p[x,1]) for x in CONTEXTS)}
    assert learner.state()==snapshot and learner.buffer==old_buffer
    return {'table':table,'withheld':held,'assignments':assignments,'metrics':metrics,
            'before':snapshot,'after':learner.state()}


def acquisition_pass(metrics):
    return (metrics['forms']==metrics['leaves']==2 and metrics['partition_matches_relevant_bit']
            and metrics['accuracy']==1 and metrics['loss']<.25
            and metrics['nuisance_effect']<=1e-12 and metrics['relevant_effect']>=.5)


def run(seed, branch, variant):
    perm, training, selection = stream(seed,branch)
    learner = Learner(variant=='merge_enabled')
    events, checkpoints = [], []
    for i,row in enumerate(training,1):
        event = {'kind':'train','index':i,'row':row,'before':learner.state(),
                 'p':learner.predict(row['x'],row['a'])}
        learner.update(**row); event['after']=learner.state(); events.append(event)
        if i%48==0:
            event={'kind':'review','index':i,'before':learner.state()}
            candidate, prepared=learner.prepare()
            event.update(prepared)
            batch=selection[i//48-1]
            event['selection']=batch
            event['decision']=learner.select(candidate,batch)
            event['after']=learner.state(); events.append(event)
        if i in (96,192):
            checkpoints.append({'index':i,**evaluate(learner,perm.index(0),branch=='changed' and i>96)})
    reviews=[e for e in events if e['kind']=='review']
    merges=[e['index'] for e in reviews if e['decision']['merge']]
    final=checkpoints[-1]['metrics']; initial=checkpoints[0]['metrics']
    first=next((i for i in merges if i>96),None)
    stable=bool(first) and all(len(e['after']['model']['counts'])==1 for e in reviews if e['index']>=first)
    checks={'acquisition':acquisition_pass(initial), 'prediction':final['accuracy']==1 and final['loss']<.25}
    if branch=='changed' and variant=='merge_enabled':
        checks.update(actual_collapse=first is not None and stable and final['forms']==final['leaves']==1,
                      useful_invariance=final['context_effect']<=1e-12 and final['action_effect']>=.5)
    elif branch=='changed':
        checks['retains_structure']=final['forms']==final['leaves']==2
    else:
        correct_reviews=all(
            len(e['after']['model']['counts'])==len(e['after']['model']['structure'])==2
            and all((group_for(tuple((tuple(c),k) for c,k in e['after']['model']['structure']),x)
                      ==group_for(tuple((tuple(c),k) for c,k in e['after']['model']['structure']),y))
                    ==(x[perm.index(0)]==y[perm.index(0)]) for x in CONTEXTS for y in CONTEXTS)
            for e in reviews if e['index']>96)
        checks['preservation']=acquisition_pass(final) and not merges and correct_reviews
    metrics={'acquisition':initial,'final':final,'checks':checks,'own_pass':all(checks.values()),
             'first_merge':first,'merge_delay':first-96 if first else None,
             'merges':merges,'review_forms':[[e['index'],len(e['after']['model']['counts'])] for e in reviews],
             'training_loss':statistics.mean(loss(e['p'],e['row']['y']) for e in events if e['kind']=='train')}
    return {'seed':seed,'branch':branch,'variant':variant,'permutation':perm,
            'events':events,'checkpoints':checkpoints,'metrics':metrics,
            'final_buffer':learner.buffer,'costs':learner.costs}


def compare(runs):
    pairs=[]
    for seed in range(5):
        by={(r['branch'],r['variant']):r for r in runs if r['seed']==seed}
        enabled=by['changed','merge_enabled']['metrics']['final']['loss']
        disabled=by['changed','merge_disabled']['metrics']['final']['loss']
        preserved=enabled<=disabled+.01
        pairs.append({'seed':seed,'enabled_changed_loss':enabled,'disabled_changed_loss':disabled,
                      'prediction_preserved':preserved,
                      'all_conditions_pass':preserved and all(r['metrics']['own_pass'] for r in by.values())})
    return {'per_seed':pairs,'passed_seeds':sum(r['all_conditions_pass'] for r in pairs),
            'overall_pass':all(r['all_conditions_pass'] for r in pairs)}


def hashes():
    paths=('experiments/collapse_protocol.md','experiments/collapse.py','experiments/forms.py',
           'checks/test_collapse.py','checks/audit_collapse.py')
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}


def report(runs,comparison):
    lines=['# Experiment 008 results','',
           f"Declared criterion: **{comparison['overall_pass']}**, {comparison['passed_seeds']}/5 seeds.",'',
           '| World | Learner | Seed | Acquired forms | Final forms | Accuracy | Log loss | Merge delay |',
           '| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for r in runs:
        m=r['metrics']; f=m['final']
        lines.append(f"| {r['branch']} | {r['variant']} | {r['seed']} | {m['acquisition']['forms']} | "
                     f"{f['forms']} | {f['accuracy']:.0%} | {f['loss']:.6f} | {m['merge_delay'] if m['merge_delay'] else '—'} |")
    lines+=['','## Review histories','','Forms after each review; first phase ends at trial 96.','',
            '| World | Learner | Seed | Trial 48 | Trial 96 | Trial 144 | Trial 192 |',
            '| --- | --- | ---: | ---: | ---: | ---: | ---: |']
    for r in runs:
        lines.append(f"| {r['branch']} | {r['variant']} | {r['seed']} | "+
                     ' | '.join(str(n) for _,n in r['metrics']['review_forms'])+' |')
    lines+=['','## Accepted merges','','| Seed | Trial | Predictive loss gain | Complexity gain | Total selection gain |',
            '| --- | ---: | ---: | ---: | ---: |']
    for r in runs:
        for e in r['events']:
            if e['kind']=='review' and e['decision']['merge']:
                d=e['decision']
                lines.append(f"| {r['seed']} | {e['index']} | {d['prediction_gain']:.6f} | {d['complexity_gain']:.6f} | {d['gain']:.6f} |")
    lines+=['','## Evidence and computation','','| World | Learner | Candidate fits, all seeds | Candidate fit rows | Count refit rows |',
            '| --- | --- | ---: | ---: | ---: |']
    for branch in BRANCHES:
        for variant in VARIANTS:
            rs=[r for r in runs if (r['branch'],r['variant'])==(branch,variant)]
            lines.append(f'| {branch} | {variant} | '+' | '.join(str(sum(r['costs'][k] for r in rs))
                         for k in ('candidate_fits','candidate_fit_rows','count_refit_rows'))+' |')
    lines+=['','4,960 outcome-bearing presentations; 480 additional unlabelled checkpoint predictions.',
            'All runs used the same 48-main-observation rolling window from their start.',
            'Full traces and criteria are saved in results.json; see findings.md for interpretation.','']
    return '\n'.join(lines)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=ROOT/'results/collapse-v1')
    args=parser.parse_args(); args.output.mkdir(parents=True,exist_ok=False)
    provenance=hashes()
    runs=[run(seed,branch,variant) for seed in range(5) for branch in BRANCHES for variant in VARIANTS]
    comparison=compare(runs); assert provenance==hashes()
    payload={'hashes':provenance,'runs':runs,'comparison':comparison,
             'outcome_presentations':4960,'unlabelled_predictions':480}
    (args.output/'results.json').write_text(json.dumps(payload,separators=(',',':'))+'\n')
    (args.output/'metrics.json').write_text(json.dumps({'runs':[{k:r[k] for k in
        ('seed','branch','variant','permutation','metrics','costs')} for r in runs],
        'comparison':comparison},indent=2)+'\n')
    (args.output/'report.md').write_text(report(runs,comparison))
    print(f'Saved 20 runs, 4,960 outcome-bearing presentations to {args.output}')
    print(json.dumps(comparison))


if __name__=='__main__': main()
