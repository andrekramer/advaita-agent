"""021: reserve the first corroborated detailed predictor before it is lost."""
import copy
import json

from .state import FrozenPredictor, canonical
from .structural import JointModel, StructuralLearner


class ProspectiveMemory(StructuralLearner):
    def __init__(self, seeds, upper_seed, memory_mode='reserve'):
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
            ordinary = super().review_upper(rows, event)
        finally:
            self.variant = 'integrated'
        if promoted is not None and self.memory_mode == 'reserve':
            self.archive.capture(promoted)
            self.peaks['archive'] = max(self.peaks['archive'], len(json.loads(promoted.payload)['counts']))
        return dict(qualification=dict(before=before, after=copy.deepcopy(self.reservation),
            action=action, witness=witness, confirmed=None if promoted is None else promoted.state()),
            ordinary=ordinary, archive_final=self.archive.state())

    def checkpoint(self):
        return canonical(dict(schema=21, core=json.loads(super().checkpoint()), memory_mode=self.memory_mode,
            reservation=copy.deepcopy(self.reservation), memory_costs=copy.deepcopy(self.memory_costs)))

    @classmethod
    def restore(cls, serialized):
        saved = json.loads(serialized)
        if saved['schema'] != 21:
            raise ValueError('Unsupported prospective-memory checkpoint')
        core = StructuralLearner.restore(canonical(saved['core']))
        result = cls(core.seeds, core.upper_seed, saved['memory_mode'])
        result.__dict__.update(core.__dict__)
        result.reservation = copy.deepcopy(saved['reservation'])
        result.memory_costs = copy.deepcopy(saved['memory_costs'])
        return result
