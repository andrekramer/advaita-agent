"""038: optional common interface over the frozen schema-37 learner.

Composition only: no new learning or admission rules. See docs/controlled-learner.md.
"""
import copy
import hashlib
import json

from .continuing import ContinuingLearner
from .preserved_prediction import ports
from .recall_withdrawal import RecallWithdrawal
from .state import canonical
from .structural import StructuralLearner


class ControlledLearner:
    """Combined memory with explicit controls; recall is shadowed by default.

    `predict` and `inspect` are read-only. `observe` scores before adding its
    label, after elapsed-time decay. Callers supply independent review evidence.
    """

    SCHEMA = 38
    POLICIES = ('shadow', 'current', 'command', 'evidence')

    def __init__(self, acquired, *, recall_policy='shadow'):
        if not isinstance(acquired, StructuralLearner) or acquired.upper is None:
            raise ValueError('An acquired StructuralLearner is required')
        if recall_policy not in self.POLICIES:
            raise ValueError('Unknown recall policy')
        core = StructuralLearner.restore(acquired.checkpoint())
        self._engine = RecallWithdrawal(core, recall_policy)
        self._last_prediction = None
        self._last_review = None
        self._commands = []

    @property
    def tick(self):
        return self._engine.tick

    @property
    def recall_policy(self):
        return self._engine.steering['policy']

    @staticmethod
    def _identity(reason, source):
        if any(not isinstance(s, str) or not s.strip() for s in (reason, source)):
            raise ValueError('Nonempty reason and source required')

    def _labelled(self):
        return bool(self._engine.main_ids and self._engine.main_ids[-1] == self.tick)

    def _source(self):
        e = self._engine
        return ('archive' if e.recall == 'recall' and e.memory['confirmed']
                and e.memory['route'] and e.compatible() and not e.steering['blocked']
                else 'active')

    def predict(self, x, action):
        """Current-state diagnostic, without decay, training or query counters."""
        ContinuingLearner._row(dict(x=x, a=action, local=[0, 0], y=0))
        return dict(tick=self.tick,
                    active=self._engine.active_predictions(x, action),
                    deployed=self._engine.predictions(x, action),
                    source=self._source())

    def observe(self, tick, row):
        if type(tick) is not int or tick != self.tick + 1:
            raise ValueError('Ticks must be consecutive integers')
        if row is not None:
            ContinuingLearner._row(row)
        result = self._engine.observe(tick, copy.deepcopy(row))
        self._last_prediction = (None if row is None else dict(
            tick=tick, deployed=copy.deepcopy(result),
            **copy.deepcopy(self._engine._prediction_event)))
        return copy.deepcopy(result)

    def review(self, tick, rows):
        if (type(tick) is not int or tick != self.tick or not self._labelled()
                or tick in self._engine.selection_ids):
            raise ValueError('Review requires a unique current labelled tick')
        if not isinstance(rows, (list, tuple)) or not rows:
            raise ValueError('Nonempty review batch required')
        for row in rows:
            ContinuingLearner._row(row)
        result = self._engine.review(tick, copy.deepcopy(rows))
        self._last_review = copy.deepcopy(result)
        return copy.deepcopy(result)

    def _record(self, operation, reason, source, before, native):
        event = dict(operation=operation, tick=self.tick, reason=reason,
                     source=source, before_sha256=before,
                     after_sha256=self._digest(), native=copy.deepcopy(native))
        self._commands.append(event)
        return copy.deepcopy(event)

    def _digest(self):
        return hashlib.sha256(self.native_checkpoint().encode()).hexdigest()

    def configure(self, *, lock, plastic, reason, source):
        """Replace all local locks and plastic channels at a completed review.

        Empty lists release all such controls. Release does not restore evidence.
        Native validation rejects invalid requests before changing state.
        """
        self._identity(reason, source)
        before = self._digest()
        native = self._engine.configure(lock=lock, plastic=plastic, reason=reason)
        return self._record('configure', reason, source, before, native)

    def set_recall_block(self, blocked, *, reason, source):
        """Change permission for future predictions; release requires readmission."""
        self._identity(reason, source)
        before = self._digest()
        native = self._engine.set_recall_block(blocked, reason=reason, source=source)
        return self._record('recall_block', reason, source, before, native)

    def inspect(self):
        """One detached snapshot of learning, memory, controls and provenance."""
        e = self._engine
        return copy.deepcopy(dict(
            schema=self.SCHEMA, tick=self.tick, recall_policy=self.recall_policy,
            learning=e.inspect(),
            dependencies=dict(active=ports(e.locals, e.upper['spec']),
                              archived=None if e.memory['slot'] is None
                              else e.memory['slot']['ports']),
            memory=e.memory, recall=e.inspect_steering(),
            current_output_source=self._source(),
            last_prediction=self._last_prediction, last_review=self._last_review,
            commands=self._commands, costs=e.costs,
            schedule=dict(capture=384, confirmation=[448, 512], admission_from=576,
                          weakening_review_spacing=64),
            boundaries=dict(labelled=self._labelled(),
                            reviewed=self.tick in e.selection_ids)))

    def native_checkpoint(self):
        """Exact schema-37 bytes for replay; excludes wrapper-only metadata."""
        return self._engine.checkpoint()

    def checkpoint(self):
        return canonical(dict(schema=self.SCHEMA,
                              engine=json.loads(self.native_checkpoint()),
                              last_prediction=self._last_prediction,
                              last_review=self._last_review, commands=self._commands))

    @classmethod
    def restore(cls, serialized):
        """Restore our own trusted checkpoint; not an untrusted-file verifier."""
        value = json.loads(serialized)
        if value.get('schema') != cls.SCHEMA:
            raise ValueError('Unsupported controlled-learner checkpoint')
        engine = RecallWithdrawal.restore(canonical(value['engine']))
        if (engine.steering['policy'] not in cls.POLICIES or engine.mode != 'combined'
                or engine.recall != ('shadow' if engine.steering['policy'] == 'shadow' else 'recall')):
            raise ValueError('Inconsistent controlled-learner configuration')
        obj = object.__new__(cls)
        obj._engine = engine
        obj._last_prediction = value['last_prediction']
        obj._last_review = value['last_review']
        obj._commands = value['commands']
        return obj
