"""A continuing nested learner; observations in, predictions and events out.

No simulator, branch, truth, stage schedule or evaluation logic lives here.
Acquisition is orchestrated by callers through the same local update/review APIs.
"""
import copy
import json

from .local import LocalLearner, ProtectedLearner
from .models import Upper, restore_local, restore_upper, view_for
from .policies import Reclosure, upper_review
from .state import EvidenceLedger, canonical, fingerprint


def tuple_tree(value):
    return tuple(tuple_tree(v) for v in value) if isinstance(value, list) else value


class NestedLearner:
    def __init__(self, seeds, local_policy='immediate', reclose=True):
        if len(seeds) != 2 or local_policy not in ('immediate', 'earned', 'uniform'):
            raise ValueError('Two local seeds and a supported local policy are required')
        self.seeds = list(seeds)
        self.local_policy, self.reclose = local_policy, reclose
        self.nodes = [LocalLearner(s) if local_policy == 'immediate'
                      else ProtectedLearner(s, local_policy) for s in seeds]
        self.local_ids = [[], []]
        self.revisions = [0, 0]
        self.upper, self.upper_binding = None, None
        self.buffer, self.buffer_ids = [], []
        self.reclosure = Reclosure()
        self.ledger = EvidenceLedger()
        self.events = []
        self.costs = dict(main_predictions=0, raw_reads=0, upper_refits=0,
                          upper_refit_rows=0, upper_candidate_fits=0, upper_candidate_rows=0)

    def models(self):
        return [n.model for n in self.nodes]

    def dependencies(self, mode=None):
        mode = mode or self.upper.mode
        ports = []
        for j, model in enumerate(self.models()):
            raw = mode in ('flat', f'fine{j}')
            ports.append(dict(name=f'node{j}.raw' if raw else f'node{j}.group',
                              domain=list(range(4 if raw else 2)),
                              meaning=list(range(4)) if raw else model.state()['groups']))
        ports.append(dict(name='action', domain=[0, 1], meaning=[0, 1]))
        return ports

    def _revision(self, j, before):
        if self.nodes[j].model.state()['groups'] != before:
            self.revisions[j] += 1

    def observe_local(self, j, record_id, row):
        self.ledger.add_main([record_id])
        before = self.nodes[j].model.state()['groups']
        self.nodes[j].update(copy.deepcopy(row))
        self.local_ids[j] = (self.local_ids[j]+[record_id])[-192:]
        self.ledger.fit(self.local_ids[j], f'local{j}.refit')
        self._revision(j, before)

    def review_local(self, j, record_ids, rows):
        if len(record_ids) != len(rows):
            raise ValueError('One identity per labelled observation is required')
        self.ledger.validate_selection(record_ids, f'local{j}.replacement')
        self.ledger.fit(self.local_ids[j], f'local{j}.proposals')
        self.ledger.select(record_ids, f'local{j}.replacement')
        if hasattr(self.nodes[j], 'policy'):
            self.ledger.select(record_ids, f'local{j}.retention')
        before = self.nodes[j].model.state()['groups']
        result = self.nodes[j].review(rows)
        self._revision(j, before)
        self.events.append(dict(operation='local_review', node=j, ids=list(record_ids), detail=result))
        return result

    def train_upper(self, record_ids, rows, mode='coarse'):
        if self.upper is not None:
            raise ValueError('Upper initialisation must occur exactly once')
        if len(record_ids) != len(rows):
            raise ValueError('One identity per labelled observation is required')
        self.ledger.add_main(record_ids)
        self.ledger.fit(record_ids, 'upper.initialise')
        self.upper = Upper(mode, rows, self.models())
        self.upper_binding = fingerprint(self.dependencies())
        self.buffer = copy.deepcopy(rows[-192:])
        self.buffer_ids = list(record_ids[-192:])
        self.events.append(dict(operation='upper_initialise', ids=list(record_ids), after=self.upper.state()))

    def predict(self, x, action):
        if self.upper is None:
            raise ValueError('Upper predictor is not initialised')
        view = view_for(x, self.models(), self.upper.mode)
        return self.upper.predict(view, action), view.raw_reads

    def step(self, record_id, row):
        # Validate all identities before prediction/learning mutates any state.
        ids = [f'{record_id}/local{j}' for j in range(2)]+[f'{record_id}/upper']
        self.ledger.validate_main(ids)
        p, reads = self.predict(row['x'], row['a'])
        self.costs['main_predictions'] += 1
        self.costs['raw_reads'] += reads
        for j in range(2):
            self.observe_local(j, ids[j], dict(x=row['x'][j], y=row['local'][j]))
        self.ledger.add_main([ids[2]])
        self.buffer = (self.buffer+[copy.deepcopy(row)])[-192:]
        self.buffer_ids = (self.buffer_ids+[ids[2]])[-192:]
        if self.upper.mode != 'coarse':
            self.ledger.fit(self.buffer_ids, 'upper.refit')
            self.upper = Upper(self.upper.mode, self.buffer, self.models())
            self.upper_binding = fingerprint(self.dependencies())
            self.costs['upper_refits'] += 1
            self.costs['upper_refit_rows'] += len(self.buffer)
        self.events.append(dict(operation='main', id=record_id, prediction=p, raw_reads=reads))
        return p, reads

    def review(self, batch_id, rows):
        ids = [f'{batch_id}/{i}' for i in range(len(rows))]
        for j in range(2):
            self.ledger.validate_selection([f'{i}/local{j}' for i in ids], f'local{j}.replacement')
        self.ledger.validate_selection([f'{i}/upper' for i in ids], 'upper.replacement')
        local = [self.review_local(j, [f'{i}/local{j}' for i in ids],
                 [dict(x=r['x'][j], y=r['local'][j]) for r in rows]) for j in range(2)]
        upper_ids = [f'{i}/upper' for i in ids]
        self.ledger.fit(self.buffer_ids, 'upper.proposals')
        self.ledger.select(upper_ids, 'upper.replacement')
        self.upper, ordinary = upper_review(self.upper, self.buffer, self.models(), rows)
        self.costs['upper_candidate_fits'] += 3
        self.costs['upper_candidate_rows'] += 3*len(self.buffer)
        if ordinary['accepted']:
            self.upper_binding = fingerprint(self.dependencies())
        detail = dict(local=local, ordinary=ordinary)
        if self.reclose:
            # The same composite batch is intentionally reused, not new evidence.
            self.ledger.select(upper_ids, 'upper.reclosure')
            self.upper, detail['reclosure'] = self.reclosure.review(
                self.upper, ordinary['candidates'][0]['state'], self.models(), rows, ordinary)
            if detail['reclosure']['action'] == 'reclosed':
                self.upper_binding = fingerprint(self.dependencies())
        detail['upper_after'] = self.upper.state()
        self.events.append(dict(operation='upper_review', ids=upper_ids, detail=detail,
                                stale_binding=self.upper_binding != fingerprint(self.dependencies())))
        return detail

    def checkpoint(self):
        nodes = []
        for node in self.nodes:
            state = dict(model=node.model.state(), buffer=node.buffer, deck=node.deck,
                         rng=node.rng.getstate(), costs=node.costs)
            if hasattr(node, 'policy'):
                state['policy'] = node.policy.state()
                state['policy_costs'] = node.policy.costs
            nodes.append(state)
        return canonical(dict(schema=1, seeds=self.seeds, local_policy=self.local_policy,
            reclose=self.reclose, nodes=nodes, local_ids=self.local_ids, revisions=self.revisions,
            upper=None if self.upper is None else self.upper.state(), upper_binding=self.upper_binding,
            buffer=self.buffer, buffer_ids=self.buffer_ids, pending=self.reclosure.state(),
            reclosure_costs=self.reclosure.costs, ledger=self.ledger.state(),
            events=self.events, costs=self.costs))

    @classmethod
    def restore(cls, serialized):
        state = json.loads(serialized)
        if state['schema'] != 1:
            raise ValueError('Unsupported checkpoint schema')
        result = cls(state['seeds'], state['local_policy'], state['reclose'])
        for node, saved in zip(result.nodes, state['nodes']):
            node.model = restore_local(saved['model'])
            node.buffer = saved['buffer']
            node.deck = [tuple(p) for p in saved['deck']]
            node.rng.setstate(tuple_tree(saved['rng']))
            node.costs = saved['costs']
            if hasattr(node, 'policy'):
                p = saved['policy']
                node.policy.established, node.policy.adequate, node.policy.pending = p['established'], p['adequate'], p['pending']
                node.policy.costs = saved['policy_costs']
        result.upper = None if state['upper'] is None else restore_upper(state['upper'])
        for key in ('local_ids', 'revisions', 'upper_binding', 'buffer', 'buffer_ids', 'events', 'costs'):
            setattr(result, key, state[key])
        result.reclosure.pending = state['pending']
        result.reclosure.costs = state['reclosure_costs']
        result.ledger = EvidenceLedger.from_state(state['ledger'])
        return result
