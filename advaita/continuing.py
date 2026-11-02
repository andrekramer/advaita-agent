"""Optional memory integration around frozen learning engines.

No world, latent target, experiment schedule or evaluation code belongs here.
The default remains the original integrated StructuralLearner.
"""
import copy
import hashlib
import json

from .memory_revision import RevisionLearner, MODES
from .structural import StructuralLearner
from .state import canonical


class ContinuingLearner:
    def __init__(self, acquired, memory='reference'):
        if not isinstance(acquired, StructuralLearner) or acquired.upper is None:
            raise ValueError('An acquired StructuralLearner is required')
        if memory not in ('reference', *MODES):
            raise ValueError('Unknown memory variant')
        core = StructuralLearner.restore(acquired.checkpoint())
        self.memory = memory
        self.engine = core if memory == 'reference' else RevisionLearner(core, memory)
        self.tick = self.active = 0
        self.review_ticks = []
        self.last_review = None
        self.controls = []

    @staticmethod
    def _row(row):
        if not isinstance(row, dict) or not {'x', 'a', 'local', 'y'} <= row.keys():
            raise ValueError('A row needs x, a, local and y')
        if not isinstance(row['x'], (list, tuple)) or len(row['x']) != 2:
            raise ValueError('Two raw states required')
        if any(type(x) is not int or not 0 <= x < 4 for x in row['x']):
            raise ValueError('Raw states must be integers 0..3')
        if not isinstance(row['local'], (list, tuple)) or len(row['local']) != 2:
            raise ValueError('Two local outcomes required')
        if any(type(x) is not int or x not in (0, 1) for x in [row['a'], row['y'], *row['local']]):
            raise ValueError('Action and outcomes must be binary integers')

    def observe(self, tick, row):
        if type(tick) is not int or tick != self.tick + 1:
            raise ValueError('Ticks must be consecutive and unique')
        if row is not None:
            self._row(row)
        if self.memory == 'reference':
            result = None
            if row is not None:
                result = [n.model.predict(row['x'][j]) for j, n in enumerate(self.engine.nodes)]
                p, _ = self.engine.step(f'main/{self.active+1}', copy.deepcopy(row))
                result.append(p)
        else:
            result = self.engine.observe(tick, copy.deepcopy(row))
        self.tick = tick
        self.active += int(row is not None)
        self.last_labelled = row is not None
        return result

    def review(self, tick, rows):
        if tick != self.tick or not getattr(self, 'last_labelled', False) or tick in self.review_ticks:
            raise ValueError('Review requires a unique current labelled tick')
        if not isinstance(rows, (list, tuple)) or not rows:
            raise ValueError('Review requires a nonempty batch')
        for row in rows:
            self._row(row)
        result = self.engine.review(f'select/{self.active}' if self.memory == 'reference' else tick, copy.deepcopy(rows))
        self.review_ticks.append(tick)
        self.last_review = copy.deepcopy(result)
        return copy.deepcopy(result)

    def inspect(self):
        if self.memory == 'reference':
            local = [n.model.state() for n in self.engine.nodes]
            upper = self.engine.upper.state()
            mass = None
        else:
            local, upper, mass = self.engine.locals, self.engine.upper, self.engine.mass()
        return copy.deepcopy(dict(memory=self.memory, tick=self.tick, active=self.active,
            locals=local, upper=upper, evidence_mass=mass, last_review=self.last_review,
            controls=self.controls, costs=self.engine.costs))

    def weaken_slow(self, channel, *, review_tick, reason):
        """Explicit one-shot channel intervention, not an autonomous policy.

        Requires the current fresh review; at most one intervention per channel
        per review. Halves only slow evidence and invalidates pending decisions
        for that channel. The caller supplies a human-readable rationale.
        """
        if self.memory == 'reference':
            raise ValueError('The reference variant has no weighted slow store')
        if type(channel) is not int or channel not in range(3):
            raise ValueError('Channel must be 0, 1 or 2')
        if review_tick != self.tick or not self.review_ticks or self.review_ticks[-1] != review_tick:
            raise ValueError('Control requires the current completed review')
        if not isinstance(reason, str) or not reason.strip():
            raise ValueError('An explicit rationale is required')
        if any(e['tick'] == self.tick and e['channel'] == channel for e in self.controls):
            raise ValueError('This channel has already been controlled at this review')
        before = self.learning_checkpoint()
        mass = self.engine.mass()['slow'][channel]
        self.engine.slow[channel] = [[x/2 for x in cell] for cell in self.engine.slow[channel]]
        self.engine.pending[channel] = None
        self.engine.revision_pending[channel] = None
        self.engine.refit()
        event = dict(operation='weaken_slow', tick=self.tick, channel=channel,
            review_tick=review_tick, reason=reason, removed_mass=mass/2,
            before_sha256=hashlib.sha256(before.encode()).hexdigest(),
            after_sha256=hashlib.sha256(self.learning_checkpoint().encode()).hexdigest())
        self.controls.append(event)
        return copy.deepcopy(event)

    def learning_checkpoint(self):
        """Native engine bytes, for compatibility checks and independent audit."""
        return self.engine.checkpoint()

    def checkpoint(self):
        return canonical(dict(schema=29, memory=self.memory, tick=self.tick, active=self.active,
            last_labelled=getattr(self, 'last_labelled', False), review_ticks=self.review_ticks,
            last_review=self.last_review, controls=self.controls, engine=json.loads(self.learning_checkpoint())))

    @classmethod
    def restore(cls, serialized):
        value = json.loads(serialized)
        if value.pop('schema') != 29:
            raise ValueError('Unsupported continuing checkpoint')
        obj = object.__new__(cls)
        engine = value.pop('engine')
        obj.__dict__.update(value)
        if obj.memory not in ('reference', *MODES):
            raise ValueError('Unknown memory variant')
        obj.engine = (StructuralLearner if obj.memory == 'reference' else RevisionLearner).restore(canonical(engine))
        if obj.memory != 'reference' and (obj.engine.mode != obj.memory or obj.engine.tick != obj.tick):
            raise ValueError('Inconsistent engine identity or clock')
        return obj
