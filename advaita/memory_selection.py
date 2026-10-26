"""022: separate archive competition from predictor reinstatement."""
import copy
import json

from .state import FrozenPredictor, canonical
from .structural import JointModel, StructuralLearner, SPECS, reduces, complexity
from .state import fingerprint


class MemorySelection(StructuralLearner):
    def __init__(self, seeds, upper_seed, selection_policy='separate'):
        if selection_policy not in ('shadow', 'veto', 'joint', 'separate'):
            raise ValueError('Unsupported selection policy')
        self.selection_policy = selection_policy
        memory_mode = 'reserve'
        if memory_mode not in ('reserve', 'discard'):
            raise ValueError('Unsupported prospective-memory policy')
        super().__init__(seeds, upper_seed, 'integrated')
        self.memory_mode = memory_mode
        self.reservation = dict(pending=None, completed=False)
        self.memory_costs = dict(nominations=0, failures=0, invalidations=0,
            confirmations=0, qualification_queries=0, pending_cells_peak=0)

    def review_upper(self, rows, event):
        self.ledger.select([f'{event}/{i}/upper' for i in range(len(rows))], 'upper.memory_qualification')
        before = copy.deepcopy(self.reservation)
        action, witness, promoted = 'locked', None, None
        if not self.reservation['completed']:
            action = 'idle'
            pending = self.reservation['pending']
            if pending is None and 2 in self.upper.spec:
                snapshot = FrozenPredictor.capture(self.upper.state(), self.upper_ports, event, self.upper_training_ids)
                # A current predictor can still be bound to outdated local meanings.
                if snapshot.compatible(self.dependencies(self.upper.spec)):
                    pending = dict(snapshot=snapshot.state(), passes=0)
                    self.reservation['pending'] = pending
                    self.memory_costs['nominations'] += 1
                    self.memory_costs['pending_cells_peak'] = max(
                        self.memory_costs['pending_cells_peak'], len(self.upper.counts))
            if pending is not None:
                snapshot = FrozenPredictor.from_state(pending['snapshot'])
                state = json.loads(snapshot.payload)
                if not snapshot.compatible(self.dependencies(state['spec'])):
                    self.reservation['pending'] = None
                    self.memory_costs['invalidations'] += 1
                    action = 'invalidated'
                else:
                    value = JointModel.restore(state).loss(rows, self.models())
                    self.scoring += len(rows)
                    self.memory_costs['qualification_queries'] += len(rows)
                    passed = value <= .55
                    witness = dict(snapshot=snapshot.state(), loss=value, passed=passed,
                        prior_passes=pending['passes'])
                    if not passed:
                        self.reservation['pending'] = None
                        self.memory_costs['failures'] += 1
                        action = 'failed'
                    elif pending['passes'] == 0:
                        pending['passes'] = 1
                        action = 'awaiting_confirmation'
                    else:
                        promoted = FrozenPredictor.from_state(dict(pending['snapshot'], capture_event=event))
                        self.reservation.update(pending=None, completed=True)
                        self.memory_costs['confirmations'] += 1
                        action = 'reserved' if self.memory_mode == 'reserve' else 'discarded'
        # Suppress reduction-triggered replacement of the reserved slot.
        # A newly confirmed snapshot becomes available only AFTER this review,
        # so its confirmation labels cannot also deploy it.
        self.variant = 'delete'
        try:
            ordinary = self.ordinary_review(rows, event)
        finally:
            self.variant = 'integrated'
        if promoted is not None and self.memory_mode == 'reserve':
            self.archive.capture(promoted)
            self.peaks['archive'] = max(self.peaks['archive'], len(json.loads(promoted.payload)['counts']))
        return dict(qualification=dict(before=before, after=copy.deepcopy(self.reservation),
            action=action, witness=witness, confirmed=None if promoted is None else promoted.state()),
            ordinary=ordinary, archive_final=self.archive.state())

    def ordinary_review(self, rows, event):
        before, previous_pending, previous_archive = self.upper.state(), copy.deepcopy(self.pending), self.archive.state()
        specs = []
        while len(specs) < 4:
            if not self.upper_deck:
                self.upper_deck = SPECS.copy()
                self.upper_rng.shuffle(self.upper_deck)
            s = self.upper_deck.pop(0)
            if s != self.upper.spec and s not in specs:
                specs.append(s)
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
        ordering = lambda c: (c[1], *complexity(c[0].spec), c[2] == 'archive')
        fits = [c for c in choices if c[2] == 'fit']
        fresh = min(fits, key=ordering) if fits else None
        archived = next((c for c in choices if c[2] == 'archive'), None)
        ranked = min(choices, key=ordering) if choices else None
        old = self.upper.loss(rows, self.models())
        fit_loss = fresh[0].loss(rows, self.models()) if fresh else None
        archive_loss = archived[0].loss(rows, self.models()) if archived else None
        self.scoring += (1+int(fresh is not None)+int(archived is not None))*len(rows)
        passes = lambda value: value is not None and old > .55 and old-value > .02
        winner = ranked
        if self.selection_policy == 'shadow':
            winner = fresh
        elif self.selection_policy == 'separate':
            # The same fresh batch selects between at most two independently
            # admitted challengers. Online outcomes measure its generalization.
            admitted = [(fit_loss, 0, fresh)] if passes(fit_loss) else []
            if passes(archive_loss): admitted.append((archive_loss, 1, archived))
            winner = min(admitted, key=lambda c: (c[0], c[1]))[2] if admitted else None
        candidate, rank, source, index = winner if winner else (None, None, None, None)
        new = (archive_loss if source == 'archive' else fit_loss) if winner else None
        accepted = passes(new) and not (self.selection_policy == 'veto' and source == 'archive')
        selection = dict(policy=self.selection_policy, fit_loss=fit_loss, archive_loss=archive_loss,
            fit_pass=passes(fit_loss), archive_pass=passes(archive_loss),
            ranked_source=None if ranked is None else ranked[2],
            vetoed=self.selection_policy == 'veto' and source == 'archive' and passes(new))
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
            ordinary_accepted=accepted, selection=selection, action=action, witness=witness, invalidated=invalidated,
            captured=captured, archive_check=archive_check, pending_before=previous_pending,
            pending_after=copy.deepcopy(self.pending), archive_before=previous_archive, archive_after=self.archive.state(),
            after=self.upper.state(), deck=[list(s) for s in self.upper_deck])

    def checkpoint(self):
        return canonical(dict(schema=22, selection_policy=self.selection_policy, core=json.loads(super().checkpoint()), memory_mode=self.memory_mode,
            reservation=copy.deepcopy(self.reservation), memory_costs=copy.deepcopy(self.memory_costs)))

    @classmethod
    def restore(cls, serialized):
        saved = json.loads(serialized)
        if saved['schema'] != 22:
            raise ValueError('Unsupported prospective-memory checkpoint')
        core = StructuralLearner.restore(canonical(saved['core']))
        result = cls(core.seeds, core.upper_seed, saved['selection_policy'])
        result.__dict__.update(core.__dict__)
        result.reservation = copy.deepcopy(saved['reservation'])
        result.memory_costs = copy.deepcopy(saved['memory_costs'])
        return result
