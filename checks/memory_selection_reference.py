"""Independent C2 tables and policy replay; imports no runtime or experiment."""
import copy
import itertools
import json
import random
from statistics import mean
from audit_nested_abstractions import (ReplayNode, PARTS, close, local_table, local_loss,
    local_state, exported, logloss, local_p)
from audit_protection_interfaces import canonical, sha

SPECS = [s for s in itertools.product(range(3), repeat=2) if s != (2, 2)]


def subset(a, b):
    return list(a) != list(b) and all(x <= y for x, y in zip(a, b))


def size(spec):
    return 2*(2**spec[0])*(2**spec[1])


def fit(spec, rows, nodes):
    keys = itertools.product(*[range(2**s) for s in spec if s], range(2))
    table = {'|'.join(map(str, k)): [0, 0] for k in keys}
    for row in rows:
        k = key(spec, nodes, row['x'], row['a'])
        table[k][0] += row['y']; table[k][1] += 1
    return dict(spec=list(spec), counts=table)


def key(spec, nodes, x, a):
    vals = []
    for j, s in enumerate(spec):
        if s == 2: vals.append(x[j])
        if s == 1: vals.append(exported(nodes[j].partition, nodes[j].table)[x[j]])
    return '|'.join(map(str, vals+[a]))


def predict(model, nodes, x, a):
    ones, total = model['counts'][key(model['spec'], nodes, x, a)]
    return (ones+1)/(total+2)


def loss(model, rows, nodes):
    return mean(logloss(predict(model, nodes, r['x'], r['a']), r['y']) for r in rows)


def ports(spec, nodes):
    value = [dict(name='action', domain=[0, 1], meaning=[0, 1])]
    for j, s in enumerate(spec):
        if s:
            value.append(dict(name=f'node{j}.raw' if s == 2 else f'node{j}.group',
                domain=list(range(4 if s == 2 else 2)),
                meaning=list(range(4)) if s == 2 else nodes[j].state()['groups']))
    return value


def fingerprint(value):
    return sha(sorted(value, key=lambda p: p['name']))


def unpack(state):
    return tuple(state['partition']), {int(k): v.copy() for k, v in state['counts'].items()}


from structural_reference import Local


class SelectionUpper:
    def __init__(self, seed, variant, policy):
        self.policy = policy
        self.rng = random.Random(seed)
        self.deck, self.pending, self.archive = [], None, None
        self.variant, self.model, self.ports, self.ids = variant, None, [], []
        self.fits = self.fitrows = self.scoring = 0
        self.peaks = dict(upper_pending=0, archive=0)

    def deploy(self, model, dependencies, ids):
        self.model, self.ports, self.ids = copy.deepcopy(model), copy.deepcopy(dependencies), list(ids)

    def review(self, saved, buffer, ids, nodes, batch, event):
        before = copy.deepcopy(self.model)
        pending_before, archive_before = copy.deepcopy(self.pending), copy.deepcopy(self.archive)
        specifications = []
        while len(specifications) < 4:
            if not self.deck:
                self.deck = SPECS.copy(); self.rng.shuffle(self.deck)
            s = self.deck.pop(0)
            if list(s) != self.model['spec'] and s not in specifications: specifications.append(s)
        specifications += [s for s in SPECS if subset(s, self.model['spec']) and s not in specifications]
        candidates = [fit(s, buffer, nodes) for s in specifications]
        rankings = [loss(m, buffer, nodes) for m in candidates]
        close(saved['candidates'], [dict(state=m, ranking_loss=l) for m, l in zip(candidates, rankings)])
        # Verified saved bits retain the specified tie order under equivalent arithmetic.
        ranks = [c['ranking_loss'] for c in saved['candidates']]
        self.fits += len(candidates); self.fitrows += len(candidates)*len(buffer)
        self.scoring += len(candidates)*len(buffer)
        choices = [(m, ranks[i], 'fit', i) for i, m in enumerate(candidates) if not subset(m['spec'], self.model['spec'])]
        check = None
        if self.archive:
            state = json.loads(self.archive['payload'])
            compatible = self.archive['dependency'] == fingerprint(ports(state['spec'], nodes))
            eligible = compatible and not subset(state['spec'], self.model['spec'])
            check = dict(compatible=compatible, eligible=eligible, ranking_loss=None)
            if eligible:
                rank = loss(state, buffer, nodes); self.scoring += len(buffer)
                check['ranking_loss'] = rank
                close(saved['archive_check'], check)
                choices.append((state, saved['archive_check']['ranking_loss'], 'archive', None))
        key_order = lambda c: (c[1], size(c[0]['spec']), c[0]['spec'].count(2), tuple(c[0]['spec']), c[2] == 'archive')
        fresh_choices = [c for c in choices if c[2] == 'fit']
        fresh = min(fresh_choices, key=key_order) if fresh_choices else None
        archive_choice = next((c for c in choices if c[2] == 'archive'), None)
        ranked = min(choices, key=key_order) if choices else None
        old = loss(self.model, batch, nodes)
        fit_loss = loss(fresh[0], batch, nodes) if fresh else None
        archive_loss = loss(archive_choice[0], batch, nodes) if archive_choice else None
        self.scoring += (1+int(fresh is not None)+int(archive_choice is not None))*len(batch)
        def qualifies(value): return value is not None and old > .55 and old-value > .02
        winner = ranked
        if self.policy == 'shadow': winner = fresh
        if self.policy == 'separate':
            options = []
            if qualifies(fit_loss): options.append((fit_loss, 0, fresh))
            if qualifies(archive_loss): options.append((archive_loss, 1, archive_choice))
            winner = min(options, key=lambda entry: (entry[0], entry[1]))[2] if options else None
        model, _, source, index = winner if winner else (None, None, None, None)
        new = (archive_loss if source == 'archive' else fit_loss) if winner else None
        accepted = qualifies(new) and not (self.policy == 'veto' and source == 'archive')
        selection = dict(policy=self.policy, fit_loss=fit_loss, archive_loss=archive_loss,
            fit_pass=qualifies(fit_loss), archive_pass=qualifies(archive_loss),
            ranked_source=None if ranked is None else ranked[2],
            vetoed=self.policy == 'veto' and source == 'archive' and qualifies(new))
        action, witness, invalidated, captured = 'keep', None, False, None
        if accepted:
            self.deploy(model, ports(model['spec'], nodes), self.archive['record_ids'] if source == 'archive' else ids)
            self.pending, action = None, 'retrieved' if source == 'archive' else 'improved'
        else:
            if self.pending and self.pending['dependency'] != fingerprint(ports(self.pending['model']['spec'], nodes)):
                self.pending, invalidated = None, True
            smaller = [i for i, s in enumerate(specifications) if subset(s, self.model['spec']) and ranks[i] <= .55]
            if self.pending is None and smaller:
                best = min(smaller, key=lambda i: (size(specifications[i]), specifications[i].count(2), ranks[i], specifications[i]))
                dependency = ports(candidates[best]['spec'], nodes)
                self.pending = dict(model=copy.deepcopy(candidates[best]), ports=dependency,
                    dependency=fingerprint(dependency), record_ids=ids.copy(), passes=0)
            if self.pending:
                challenger = self.pending['model']
                value = loss(challenger, batch, nodes)
                self.scoring += len(batch)
                passed = value <= .55 and value-old <= .02
                self.peaks['upper_pending'] = max(self.peaks['upper_pending'], len(challenger['counts']))
                witness = dict(model=copy.deepcopy(challenger), loss=value, passed=passed, prior_passes=self.pending['passes'])
                if not passed: self.pending, action = None, 'reduction_failed'
                elif self.pending['passes'] == 1:
                    snapshot = dict(payload=canonical(self.model), dependency=fingerprint(self.ports),
                                    capture_event=event, record_ids=self.ids.copy())
                    captured = dict(retained=self.variant != 'delete', dependency=snapshot['dependency'],
                                    displaced=copy.deepcopy(self.archive), model=copy.deepcopy(self.model))
                    if self.variant != 'delete':
                        self.archive = snapshot
                        self.peaks['archive'] = max(self.peaks['archive'], len(self.model['counts']))
                    self.deploy(challenger, self.pending['ports'], self.pending['record_ids'])
                    self.pending, action = None, 'reduced'
                else: self.pending['passes'], action = 1, 'awaiting_reduction'
        close(saved, dict(before=before, candidates=[dict(state=m, ranking_loss=l) for m, l in zip(candidates, rankings)],
            winner=None if model is None else dict(source=source, index=index, state=model),
            old_loss=old, new_loss=new, ordinary_accepted=accepted, selection=selection, action=action, witness=witness,
            invalidated=invalidated, captured=captured, archive_check=check, pending_before=pending_before,
            pending_after=self.pending, archive_before=archive_before, archive_after=self.archive,
            after=self.model, deck=self.deck))
