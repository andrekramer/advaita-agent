"""033 experimental controls around the frozen combined memory learner.

Locks hold local partitions, not probabilities or group label ordering. Plasticity
changes only the selected slow evidence half-life. This is not the default API.
"""
import copy
import hashlib
import json
from .memory_revision import RevisionLearner
from .state import canonical


class SteerableMemory(RevisionLearner):
    def __init__(self, core):
        super().__init__(core, 'combined')
        self.locked = {}
        self.half_lives = [1024, 1024, 1024]
        self.control_events = []

    def configure(self, *, lock, plastic, reason):
        if not self.selection_ids or self.selection_ids[-1] != self.tick:
            raise ValueError('Configure only after a current completed review')
        if any(e['tick'] == self.tick for e in self.control_events):
            raise ValueError('One configuration per review')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('A reason is required')
        if not isinstance(lock, (list, tuple)) or not isinstance(plastic, (list, tuple)):
            raise ValueError('Channel lists required')
        if any(type(j) is not int or j not in (0, 1) for j in [*lock, *plastic]):
            raise ValueError('Only local channels 0 and 1 are configurable')
        if len(set(lock)) != len(lock) or len(set(plastic)) != len(plastic) or set(lock) & set(plastic):
            raise ValueError('Distinct, disjoint channels required')
        before = hashlib.sha256(self.checkpoint().encode()).hexdigest()
        previous = dict(locked=copy.deepcopy(self.locked), half_lives=self.half_lives.copy())
        for j in set(map(int, self.locked)) | set(lock):
            self.pending[j] = None
        self.locked = {str(j): self.locals[j]['partition'].copy() for j in lock}
        self.half_lives = [128 if j in plastic else 1024 for j in range(3)]
        event = dict(tick=self.tick, reason=reason, before_sha256=before, previous=previous,
                     locked=copy.deepcopy(self.locked), half_lives=self.half_lives.copy())
        self.control_events.append(event)
        return copy.deepcopy(event)

    def observe(self, t, row):
        if type(t) is not int or t != self.tick + 1:
            raise ValueError('Ticks must be consecutive and unique')
        # The inherited update supplies the original 1024-tick slow decay.
        for j, half_life in enumerate(self.half_lives):
            if half_life != 1024:
                extra = 2 ** (-1 / half_life + 1 / 1024)
                for cell in self.slow[j]:
                    for k in (0, 1):
                        cell[k] *= extra
        return super().observe(t, row)

    def review_channel(self, j, rows):
        if str(j) not in self.locked:
            return super().review_channel(j, rows)
        assert self.locals[j]['partition'] == self.locked[str(j)]
        assert self.pending[j] is None
        return dict(action='locked', channel=j, partition=self.locked[str(j)].copy())

    def review(self, t, rows):
        result = super().review(t, rows)
        # Snapshot consistency only: preserve all within-review decisions.
        self.refit()
        result['post_review'] = dict(locals=copy.deepcopy(self.locals), upper=copy.deepcopy(self.upper))
        return result

    def inspect(self):
        return copy.deepcopy(dict(tick=self.tick, locals=self.locals, upper=self.upper,
            evidence_mass=self.mass(), locked=self.locked, half_lives=self.half_lives,
            pending=self.pending, revision_pending=self.revision_pending, controls=self.control_events))

    def checkpoint(self):
        state = json.loads(super().checkpoint())
        state.update(schema=33, locked=self.locked, half_lives=self.half_lives, control_events=self.control_events)
        return canonical(state)

    @classmethod
    def restore(cls, serialized):
        state = json.loads(serialized)
        if state['schema'] != 33:
            raise ValueError('Unsupported steering checkpoint')
        config = {k: state.pop(k) for k in ('locked', 'half_lives', 'control_events')}
        state['schema'] = 27
        obj = RevisionLearner.restore(canonical(state))
        obj.__class__ = cls
        obj.__dict__.update(config)
        return obj
