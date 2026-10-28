"""023/024: explicit ownership of predictive updates and representation changes."""
import copy
import itertools
import json
import random
from statistics import mean

from .local import LocalLearner, PARTITIONS
from .models import CountModel, CountTable, LocalModel, RestrictedView, nll, restore_local
from .runtime import NestedLearner, tuple_tree
from .state import Archive, FrozenPredictor, canonical, fingerprint

SPECS = [p for p in itertools.product(range(3), repeat=2) if p != (2, 2)]
COLLAPSED = (0, 0, 0, 0)


def reduces(new, old):
    return tuple(new) != tuple(old) and all(a <= b for a, b in zip(new, old))


def complexity(spec):
    return 2*(1, 2, 4)[spec[0]]*(1, 2, 4)[spec[1]], spec.count(2), tuple(spec)


def aligned(partition, previous):
    labels = sorted(set(partition))
    options = [tuple(mapping[labels.index(p)] for p in partition)
        for mapping in itertools.permutations(range(2), len(labels))]
    return list(min(options, key=lambda g: (-sum(a==b for a,b in zip(g,previous)), g)))


class BoundLocal(LocalModel):
    def __init__(self, model, groups):
        self.partition = model.partition
        self.table = model.table
        self.exported = list(groups)

    def group(self, x): return self.exported[x]

    def state(self):
        result = super().state()
        result['groups'] = list(self.exported)
        return result


def history_score(records, key, channel):
    buckets = {}
    for h in records:
        values = buckets.setdefault(key(h), [0.0,0.0,0])
        values[0] += h['outcomes'][channel]-h['before'][channel]
        values[1] += h['after'][channel]
        values[2] += 1
    return tuple(sum(v[k]*v[k]/v[2] for v in buckets.values())/len(records) for k in (0,1))


class JointModel(CountModel):
    def __init__(self, spec=(1, 1), rows=(), models=()):
        self.spec = tuple(spec)
        self.table = CountTable(['|'.join(map(str, key)) for key in itertools.product(
            *[range((1, 2, 4)[s]) for s in spec if s], range(2))])
        for row in rows:
            self.table.add(self.key(self.view(row['x'], models), row['a']), row['y'])

    def view(self, x, models):
        values = {(j, s): x[j] if s == 2 else models[j].group(x[j])
                  for j, s in enumerate(self.spec) if s}
        return RestrictedView(values, values.keys())

    def key(self, view, action):
        return '|'.join(map(str, [view.read((j, s)) for j, s in enumerate(self.spec) if s]+[action]))

    def predict(self, x, a, models):
        return self.table.probability(self.key(self.view(x, models), a))

    def loss(self, rows, models):
        return mean(nll(self.predict(r['x'], r['a'], models), r['y']) for r in rows)

    def state(self):
        return dict(spec=list(self.spec), counts=copy.deepcopy(self.counts))

    @classmethod
    def restore(cls, state):
        result = cls(state['spec'])
        result.counts = state['counts']
        return result


class RoleLocal(LocalLearner):
    def __init__(self, seed):
        super().__init__(seed)
        self.structural = False
        self.pending = None
        self.queries = 0
        self.pending_peak = 0
        self.stable = False
        self.history = []
        self.history_node = 0
        self.history_enabled = False
        self.history_rows = 0

    def update(self, row):
        previous = self.model.state()['groups']
        super().update(row)
        if self.stable:
            self.model = BoundLocal(self.model, previous)

    def review(self, batch):
        previous = self.model.state()['groups']
        result = self.form_review(batch)
        if self.stable:
            groups = aligned(self.model.partition, previous)
            self.model = BoundLocal(self.model, groups)
            result['after'] = self.model.state()
        return result

    def form_review(self, batch):
        if not self.structural:
            self.queries += 4*min(64, len(self.buffer))+2*len(batch)
            return dict(kind='acquisition', decision=super().review(batch))
        before = self.model.state()
        pending_before = copy.deepcopy(self.pending)
        proposals = [COLLAPSED] if len(self.model.counts) > 1 else []
        while len(proposals) < 4:
            if not self.deck:
                self.deck = PARTITIONS.copy()
                self.rng.shuffle(self.deck)
            p = self.deck.pop(0)
            if p != self.model.partition and p not in proposals and p != COLLAPSED:
                proposals.append(p)
        if self.history_enabled and self.history:
            candidates_for_slot = [p for p in PARTITIONS if p != COLLAPSED
                and p != self.model.partition and p not in proposals[:3]]
            scores = {p: history_score(self.history,
                lambda h, p=p: p[h['x'][self.history_node]], self.history_node) for p in candidates_for_slot}
            self.history_rows += len(candidates_for_slot)*len(self.history)
            proposals[3] = min(candidates_for_slot, key=lambda p: (-scores[p][0], -scores[p][1], p))
        candidates = [LocalModel(p, self.buffer) for p in proposals]
        ranks = [m.loss(self.buffer[-64:]) for m in candidates]
        eligible = [i for i, m in enumerate(candidates) if len(m.counts) >= len(self.model.counts)]
        best = min(eligible, key=lambda i: (ranks[i], len(candidates[i].counts), candidates[i].partition))
        old, new = self.model.loss(batch), candidates[best].loss(batch)
        self.queries += 4*min(64, len(self.buffer))+2*len(batch)
        witness, action = None, 'keep'
        if old-new > .005:
            self.model, self.pending, action = candidates[best], None, 'improved'
        elif len(self.model.counts) > 1:
            if self.pending is None:
                self.pending = dict(model=candidates[proposals.index(COLLAPSED)].state(), passes=0)
            challenger = restore_local(self.pending['model'])
            loss = challenger.loss(batch)
            passed = loss <= .55 and loss-old <= .02
            self.queries += len(batch)
            self.pending_peak = max(self.pending_peak, len(challenger.counts))
            witness = dict(model=challenger.state(), loss=loss, passed=passed, prior_passes=self.pending['passes'])
            if not passed:
                self.pending, action = None, 'reduction_failed'
            elif self.pending['passes'] == 1:
                self.model, self.pending, action = challenger, None, 'collapsed'
            else:
                self.pending['passes'], action = 1, 'awaiting_reduction'
        else:
            self.pending = None
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4*len(self.buffer)
        return dict(kind='structural', before=before, candidates=[dict(state=m.state(), ranking_loss=l)
            for m, l in zip(candidates, ranks)], winner=best, old_loss=old, new_loss=new,
            action=action, witness=witness, pending_before=pending_before, pending_after=copy.deepcopy(self.pending),
            after=self.model.state(), deck=[list(p) for p in self.deck])


class RoleLearner(NestedLearner):
    def __init__(self, seeds, upper_seed, variant='integrated', policy='B64'):
        if policy not in ('B64','B128','U64','U128','R128','H128'):
            raise ValueError('Unsupported roles policy')
        self.policy = policy
        self.history = []
        self.history_costs = dict(feature_predictions=0, proposal_rows=0, records=0)
        if variant not in ('integrated', 'delete', 'raw', 'fixed'):
            raise ValueError('Unsupported structural policy')
        super().__init__(seeds)
        self.nodes = [RoleLocal(s) for s in seeds]
        self.upper_seed, self.variant = upper_seed, variant
        self.upper_rng, self.upper_deck = random.Random(upper_seed), []
        self.pending = None
        self.archive = Archive()
        self.upper_ports, self.upper_training_ids = [], []
        self.scoring = 0
        self.peaks = dict(upper_pending=0, archive=0)

    def dependencies(self, spec=None):
        spec = self.upper.spec if spec is None else spec
        ports = [dict(name='action', domain=[0, 1], meaning=[0, 1])]
        for j, s in enumerate(spec):
            if s:
                ports.append(dict(name=f'node{j}.raw' if s == 2 else f'node{j}.group',
                    domain=list(range(4 if s == 2 else 2)),
                    meaning=list(range(4)) if s == 2 else self.nodes[j].model.state()['groups']))
        return ports

    def deploy(self, model, ports, record_ids):
        self.upper, self.upper_ports = model, copy.deepcopy(ports)
        self.upper_training_ids = list(record_ids)
        self.upper_binding = fingerprint(ports)

    def train_upper(self, record_ids, rows, mode=None):
        if self.upper is not None:
            raise ValueError('Already initialized')
        if len(record_ids) != len(rows):
            raise ValueError('One identity per row')
        self.ledger.add_main(record_ids)
        self.ledger.fit(record_ids, 'upper.initialise')
        model = JointModel((2, 2) if self.variant == 'raw' else (1, 1), rows, self.models())
        self.deploy(model, self.dependencies(model.spec), record_ids)
        self.buffer, self.buffer_ids = copy.deepcopy(rows[-192:]), list(record_ids[-192:])
        for j, n in enumerate(self.nodes):
            n.structural = True
            if self.policy in ('R128', 'H128'):
                n.stable = True
                n.model = BoundLocal(n.model, n.model.state()['groups'])
            n.history_node = j
            n.history_enabled = self.policy == 'H128' 
        self.events.append(dict(operation='upper_initialise', ids=list(record_ids), after=model.state()))

    def predict(self, x, action):
        return self.upper.predict(x, action, self.models()), self.upper.spec.count(2)

    def step(self, identity, row):
        ids = [f'{identity}/local{j}' for j in range(2)] if self.variant != 'raw' else []
        self.ledger.validate_main(ids+[f'{identity}/upper'])
        local_before = [n.model.predict(row['x'][j]) for j,n in enumerate(self.nodes)] if self.policy == 'H128' else None
        p, reads = self.predict(row['x'], row['a'])
        self.costs['main_predictions'] += 1
        self.costs['raw_reads'] += reads
        if self.variant != 'raw':
            for j in range(2):
                self.observe_local(j, ids[j], dict(x=row['x'][j], y=row['local'][j]))
        upper_id = f'{identity}/upper'
        self.ledger.add_main([upper_id])
        self.buffer, self.buffer_ids = (self.buffer+[copy.deepcopy(row)])[-192:], (self.buffer_ids+[upper_id])[-192:]
        if 2 in self.upper.spec or self.policy in ('U64','U128','R128','H128'):
            self.ledger.fit(self.buffer_ids, 'upper.refit')
            self.deploy(JointModel(self.upper.spec, self.buffer, self.models()), self.dependencies(), self.buffer_ids)
            self.costs['upper_refits'] += 1
            self.costs['upper_refit_rows'] += len(self.buffer)
        if self.policy == 'H128':
            after = [n.model.predict(row['x'][j]) for j,n in enumerate(self.nodes)] + [self.predict(row['x'], row['a'])[0]]
            record = dict(id=identity, x=list(row['x']), a=row['a'], before=local_before+[p], after=after,
                outcomes=list(row['local'])+[row['y']], groups=[n.model.state()['groups'] for n in self.nodes])
            self.history = (self.history+[record])[-192:]
            self.history_costs['feature_predictions'] += 5
            self.history_costs['records'] += 1
            for n in self.nodes: n.history = self.history
        self.events.append(dict(operation='main', id=identity, prediction=p, raw_reads=reads))
        return p, reads

    def review(self, batch_id, rows):
        if self.variant == 'raw':
            return dict(local=[], upper=None)
        ids = [f'{batch_id}/{i}' for i in range(len(rows))]
        if self.variant != 'fixed':
            for j in range(2):
                self.ledger.validate_selection([f'{i}/local{j}' for i in ids], f'local{j}.replacement')
        self.ledger.validate_selection([f'{i}/upper' for i in ids], 'upper.replacement')
        local = []
        if self.variant != 'fixed':
            for j in range(2):
                records = [f'{i}/local{j}' for i in ids]
                local.append(self.review_local(j, records, [dict(x=r['x'][j], y=r['local'][j]) for r in rows]))
                self.ledger.select(records, f'local{j}.reduction')
        records = [f'{i}/upper' for i in ids]
        self.ledger.fit(self.buffer_ids, 'upper.proposals')
        self.ledger.select(records, 'upper.replacement')
        self.ledger.select(records, 'upper.reduction')
        upper = self.review_upper(rows, batch_id)
        result = dict(local=local, upper=upper)
        self.events.append(dict(operation='upper_review', ids=records, detail=result,
                                stale_binding=self.upper_binding != fingerprint(self.dependencies())))
        return result

    def review_upper(self, rows, event):
        before, previous_pending, previous_archive = self.upper.state(), copy.deepcopy(self.pending), self.archive.state()
        specs = []
        while len(specs) < 4:
            if not self.upper_deck:
                self.upper_deck = SPECS.copy()
                self.upper_rng.shuffle(self.upper_deck)
            s = self.upper_deck.pop(0)
            if s != self.upper.spec and s not in specs:
                specs.append(s)
        if self.policy == 'H128' and self.history:
            available = [s for s in SPECS if s != self.upper.spec and s not in specs[:3]]
            def hkey(h, spec):
                return tuple(h['x'][j] if v==2 else self.nodes[j].model.group(h['x'][j])
                    for j,v in enumerate(spec) if v)+(h['a'],)
            scores = {s: history_score(self.history, lambda h,s=s: hkey(h,s), 2) for s in available}
            self.history_costs['proposal_rows'] += len(available)*len(self.history)
            specs[3] = min(available, key=lambda s: (-scores[s][0], -scores[s][1], *complexity(s)))
        specs += [s for s in SPECS if reduces(s, self.upper.spec) and s not in specs]
        fitted = [JointModel(s, self.buffer, self.models()) for s in specs]
        ranks = [m.loss(self.buffer, self.models()) for m in fitted]
        self.costs['upper_candidate_fits'] += len(fitted)
        self.costs['upper_candidate_rows'] += len(fitted)*len(self.buffer)
        self.scoring += len(fitted)*len(self.buffer)
        choices = [(m, ranks[i], 'fit', i) for i, m in enumerate(fitted) if not reduces(m.spec, self.upper.spec)]
        archive_check = None
        if self.archive.entry is not None:
            snapshot = self.archive.entry
            state = json.loads(snapshot.payload)
            compatible = snapshot.compatible(self.dependencies(state['spec']))
            eligible = compatible and not reduces(state['spec'], self.upper.spec)
            archive_check = dict(compatible=compatible, eligible=eligible, ranking_loss=None)
            if eligible:
                candidate = JointModel.restore(state)
                rank = candidate.loss(self.buffer, self.models())
                self.scoring += len(self.buffer)
                archive_check['ranking_loss'] = rank
                choices.append((candidate, rank, 'archive', None))
        winner = min(choices, key=lambda c: (c[1], *complexity(c[0].spec), c[2] == 'archive')) if choices else None
        candidate, rank, source, index = winner if winner else (None, None, None, None)
        old = self.upper.loss(rows, self.models())
        new = candidate.loss(rows, self.models()) if candidate is not None else None
        self.scoring += (1+int(candidate is not None))*len(rows)
        accepted = new is not None and old > .55 and old-new > .02
        action, witness, invalidated, captured = 'keep', None, False, None
        if accepted:
            if source == 'archive':
                ports = self.dependencies(candidate.spec)
                construction = self.archive.entry.record_ids
            else:
                ports, construction = self.dependencies(candidate.spec), self.buffer_ids
            self.deploy(candidate, ports, construction)
            self.pending, action = None, 'retrieved' if source == 'archive' else 'improved'
        else:
            if self.pending is not None and self.pending['dependency'] != fingerprint(self.dependencies(self.pending['model']['spec'])):
                self.pending, invalidated = None, True
            reductions = [i for i, s in enumerate(specs) if reduces(s, self.upper.spec) and ranks[i] <= .55]
            if self.pending is None and reductions:
                best = min(reductions, key=lambda i: (complexity(specs[i])[0], complexity(specs[i])[1], ranks[i], specs[i]))
                model = fitted[best]
                ports = self.dependencies(model.spec)
                self.pending = dict(model=model.state(), ports=ports, dependency=fingerprint(ports),
                                    record_ids=self.buffer_ids.copy(), passes=0)
            if self.pending is not None:
                challenger = JointModel.restore(self.pending['model'])
                loss = challenger.loss(rows, self.models())
                self.scoring += len(rows)
                passed = loss <= .55 and loss-old <= .02
                self.peaks['upper_pending'] = max(self.peaks['upper_pending'], len(challenger.counts))
                witness = dict(model=challenger.state(), loss=loss, passed=passed, prior_passes=self.pending['passes'])
                if not passed:
                    self.pending, action = None, 'reduction_failed'
                elif self.pending['passes'] == 1:
                    snapshot = FrozenPredictor.capture(self.upper.state(), self.upper_ports, event, self.upper_training_ids)
                    captured = dict(retained=self.variant != 'delete', dependency=snapshot.dependency,
                                    displaced=self.archive.state(), model=self.upper.state())
                    if self.variant != 'delete':
                        self.archive.capture(snapshot)
                        self.peaks['archive'] = max(self.peaks['archive'], len(self.upper.counts))
                    self.deploy(challenger, self.pending['ports'], self.pending['record_ids'])
                    self.pending, action = None, 'reduced'
                else:
                    self.pending['passes'], action = 1, 'awaiting_reduction'
        return dict(before=before, candidates=[dict(state=m.state(), ranking_loss=l) for m, l in zip(fitted, ranks)],
            winner=None if candidate is None else dict(source=source, index=index, state=candidate.state()), old_loss=old, new_loss=new,
            ordinary_accepted=accepted, action=action, witness=witness, invalidated=invalidated,
            captured=captured, archive_check=archive_check, pending_before=previous_pending,
            pending_after=copy.deepcopy(self.pending), archive_before=previous_archive, archive_after=self.archive.state(),
            after=self.upper.state(), deck=[list(s) for s in self.upper_deck])

    def core_checkpoint(self):
        return canonical(dict(schema=2, seeds=self.seeds, upper_seed=self.upper_seed, variant=self.variant,
            nodes=[dict(model=n.model.state(), buffer=n.buffer, deck=n.deck, rng=n.rng.getstate(), costs=n.costs,
                        pending=n.pending, structural=n.structural, queries=n.queries, pending_peak=n.pending_peak) for n in self.nodes],
            upper=None if self.upper is None else self.upper.state(), upper_ports=self.upper_ports,
            upper_training_ids=self.upper_training_ids, upper_binding=self.upper_binding,
            upper_rng=self.upper_rng.getstate(), upper_deck=self.upper_deck, pending=self.pending,
            archive=self.archive.state(), local_ids=self.local_ids, revisions=self.revisions,
            buffer=self.buffer, buffer_ids=self.buffer_ids, ledger=self.ledger.state(), events=self.events,
            costs=self.costs, scoring=self.scoring, peaks=self.peaks))

    def checkpoint(self):
        return canonical(dict(schema=24, core=json.loads(self.core_checkpoint()), policy=self.policy,
            stable=[n.stable for n in self.nodes], history=self.history, history_costs=self.history_costs,
            local_history_rows=[n.history_rows for n in self.nodes]))

    @classmethod
    def restore(cls, serialized):
        from .structural import StructuralLearner
        saved = json.loads(serialized)
        if saved['schema'] != 24: raise ValueError('Unsupported roles checkpoint')
        core = StructuralLearner.restore(canonical(saved['core']))
        obj = cls(core.seeds, core.upper_seed, core.variant, saved['policy'])
        nodes = obj.nodes
        obj.__dict__.update(core.__dict__)
        obj.nodes = nodes
        for j,(n, original) in enumerate(zip(nodes,core.nodes)):
            n.__dict__.update(original.__dict__)
            n.stable = saved['stable'][j]
            if n.stable: n.model = BoundLocal(n.model, saved['core']['nodes'][j]['model']['groups'])
            n.history_node = j
            n.history_enabled = obj.policy == 'H128'
            n.history_rows = saved['local_history_rows'][j]
        obj.history = copy.deepcopy(saved['history'])
        obj.history_costs = copy.deepcopy(saved['history_costs'])
        for n in obj.nodes: n.history = obj.history
        return obj


class CompatibilityLearner(RoleLearner):
    """B64 exposes the original checkpoint contract for exact 019 replay."""
    def checkpoint(self): return self.core_checkpoint()
