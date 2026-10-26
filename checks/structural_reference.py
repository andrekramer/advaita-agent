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


class Local(ReplayNode):
    def __init__(self, seed):
        super().__init__(seed)
        self.structural, self.pending, self.queries, self.pending_peak, self.revision = False, None, 0, 0, 0

    def update(self, row):
        before = self.state()['groups']
        super().update(row)
        self.revision += before != self.state()['groups']

    def review(self, saved, batch):
        before = self.state()
        if not self.structural:
            assert saved['kind'] == 'acquisition'
            self.queries += 4*min(64, len(self.buffer))+2*len(batch)
            super().review(saved['decision'], batch)
            self.revision += before['groups'] != self.state()['groups']
            return
        pending_before = copy.deepcopy(self.pending)
        collapse = (0, 0, 0, 0)
        proposals = [collapse] if len(self.table) > 1 else []
        while len(proposals) != 4:
            if not self.deck:
                self.deck = PARTS.copy(); self.random.shuffle(self.deck)
            p = self.deck.pop(0)
            if p != self.partition and p != collapse and p not in proposals: proposals.append(p)
        tables = [local_table(p, self.buffer) for p in proposals]
        ranks = [local_loss(p, c, self.buffer[-64:]) for p, c in zip(proposals, tables)]
        candidates = [dict(state=local_state(p, c), ranking_loss=l) for p, c, l in zip(proposals, tables, ranks)]
        close(saved['candidates'], candidates)
        best = min([i for i, c in enumerate(tables) if len(c) >= len(self.table)],
                   key=lambda i: (saved['candidates'][i]['ranking_loss'], len(tables[i]), proposals[i]))
        old, new = local_loss(self.partition, self.table, batch), local_loss(proposals[best], tables[best], batch)
        self.queries += 4*min(64, len(self.buffer))+2*len(batch)
        witness, action = None, 'keep'
        if old-new > .005:
            self.partition, self.table = proposals[best], tables[best]
            self.pending, action = None, 'improved'
        elif len(self.table) > 1:
            if self.pending is None:
                i = proposals.index(collapse)
                self.pending = dict(model=local_state(proposals[i], tables[i]), passes=0)
            p, c = unpack(self.pending['model'])
            value = local_loss(p, c, batch)
            passed = value <= .55 and value-old <= .02
            witness = dict(model=copy.deepcopy(self.pending['model']), loss=value, passed=passed,
                           prior_passes=self.pending['passes'])
            self.queries += len(batch); self.pending_peak = max(self.pending_peak, len(c))
            if not passed: self.pending, action = None, 'reduction_failed'
            elif self.pending['passes'] == 1:
                self.partition, self.table, self.pending, action = p, c, None, 'collapsed'
            else: self.pending['passes'], action = 1, 'awaiting_reduction'
        else: self.pending = None
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4*len(self.buffer)
        close(saved, dict(kind='structural', before=before, candidates=candidates, winner=best,
            old_loss=old, new_loss=new, action=action, witness=witness, pending_before=pending_before,
            pending_after=self.pending, after=self.state(), deck=self.deck))
        self.revision += before['groups'] != self.state()['groups']


class Upper:
    def __init__(self, seed, variant):
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
        winner = min(choices, key=lambda c: (c[1], size(c[0]['spec']), c[0]['spec'].count(2), tuple(c[0]['spec']), c[2] == 'archive')) if choices else None
        model, _, source, index = winner if winner else (None, None, None, None)
        old = loss(self.model, batch, nodes)
        new = loss(model, batch, nodes) if model is not None else None
        self.scoring += (1+int(model is not None))*len(batch)
        accepted = new is not None and old > .55 and old-new > .02
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
            old_loss=old, new_loss=new, ordinary_accepted=accepted, action=action, witness=witness,
            invalidated=invalidated, captured=captured, archive_check=check, pending_before=pending_before,
            pending_after=self.pending, archive_before=archive_before, archive_after=self.archive,
            after=self.model, deck=self.deck))
