"""020: corroborate revisions of established local forms in the structural core."""
import copy
import json

from .models import restore_local
from .state import canonical
from .structural import ReducingLocal, StructuralLearner


class CorroboratedLocal(ReducingLocal):
    def __init__(self, seed):
        super().__init__(seed)
        self.protection = dict(established=False, adequate=0, pending=None)
        self.protection_costs = dict(starts=0, confirmations=0, failures=0,
            establishments=0, confirmation_queries=0, pending_cells_peak=0)

    def review(self, batch):
        if not self.structural:
            return super().review(batch)
        before = copy.deepcopy(self.protection)
        incumbent = self.model.state()
        ordinary = super().review(batch)
        action, witness = ordinary['action'], None
        if before['pending'] is not None:
            # Keep search/RNG and its costs paired, but resolve the frozen
            # challenger before considering any replacement from this review.
            challenger = restore_local(before['pending'])
            value = challenger.loss(batch)
            passed = ordinary['old_loss']-value > .005
            witness = dict(model=challenger.state(), loss=value, passed=passed)
            self.queries += len(batch)
            self.protection_costs['confirmation_queries'] += len(batch)
            self.model = challenger if passed else restore_local(incumbent)
            self.pending = None
            self.protection['pending'] = None
            action = 'confirmed' if passed else 'confirmation_failed'
            self.protection_costs['confirmations' if passed else 'failures'] += 1
        elif before['established'] and ordinary['action'] == 'improved':
            self.protection['pending'] = copy.deepcopy(ordinary['after'])
            self.model, self.pending = restore_local(incumbent), None
            action = 'awaiting_confirmation'
            self.protection_costs['starts'] += 1
            self.protection_costs['pending_cells_peak'] = max(
                self.protection_costs['pending_cells_peak'], len(ordinary['after']['counts']))
        accepted = action in ('improved', 'collapsed', 'confirmed')
        if accepted:
            self.protection.update(established=False, adequate=0, pending=None)
        else:
            self.protection['adequate'] = min(2, before['adequate']+1) if ordinary['old_loss'] <= .55 else 0
            if self.protection['adequate'] == 2 and not self.protection['established']:
                self.protection['established'] = True
                self.protection_costs['establishments'] += 1
        return dict(ordinary=ordinary, protection=dict(before=before, after=copy.deepcopy(self.protection),
            action=action, accepted=accepted, witness=witness), after=self.model.state())


class CorroboratedLearner(StructuralLearner):
    def __init__(self, seeds, upper_seed):
        super().__init__(seeds, upper_seed, 'integrated')
        self.nodes = [CorroboratedLocal(s) for s in seeds]

    def review_local(self, j, record_ids, rows):
        result = super().review_local(j, record_ids, rows)
        if self.nodes[j].structural:
            self.ledger.select(record_ids, f'local{j}.corroboration')
        return result

    def checkpoint(self):
        return canonical(dict(schema=20, core=json.loads(super().checkpoint()),
            protection=[copy.deepcopy(n.protection) for n in self.nodes],
            protection_costs=[copy.deepcopy(n.protection_costs) for n in self.nodes]))

    @classmethod
    def restore(cls, serialized):
        saved = json.loads(serialized)
        if saved['schema'] != 20:
            raise ValueError('Unsupported corroboration checkpoint')
        core = StructuralLearner.restore(canonical(saved['core']))
        obj = cls(core.seeds, core.upper_seed)
        obj.__dict__.update(core.__dict__)
        nodes = []
        for j, old in enumerate(core.nodes):
            node = CorroboratedLocal(core.seeds[j])
            node.__dict__.update(old.__dict__)
            node.protection = copy.deepcopy(saved['protection'][j])
            node.protection_costs = copy.deepcopy(saved['protection_costs'][j])
            nodes.append(node)
        obj.nodes = nodes
        return obj
