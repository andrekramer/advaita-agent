"""Projection search and retained detail, preserving 010–012 decisions.

Legacy modes retain their original complexity cost and acquisition policy.
These are reusable policies, not imports or dispatch to experiment scripts.
"""
import copy
import itertools
import random
import statistics
import statistics as st
from .models import ProjectionModel as Model, VisibleInput, nll
N = 6
WINDOW = 192
POOL = [()] + [(i,) for i in range(N)] + list(itertools.combinations(range(N), 2))
VARIANTS = ('iid_single', 'deck_single', 'iid_split', 'deck_split')

def penalty(subset):
    return .01 * 2**(len(subset)+1)

class ProjectionLearner:
    def __init__(self, variant, proposal_seed=None):
        self.variant = variant
        self.model = Model(range(N) if variant == 'full_context' else ())
        self.buffer = []
        self.rng = random.Random(50000 + (proposal_seed or 0))
        self.cursor = 0
        self.costs = dict.fromkeys((
            'main_prediction_feature_reads', 'count_refits', 'count_refit_rows',
            'refit_feature_reads', 'candidate_fits', 'candidate_fit_rows',
            'candidate_fit_feature_reads', 'candidate_score_feature_reads',
            'selection_outcomes', 'selection_prediction_feature_reads',
        ), 0)

    def predict(self, x, action):
        self.costs['main_prediction_feature_reads'] += len(self.model.subset)
        return self.model.predict(x, action)

    def update(self, row):
        self.buffer = (self.buffer + [row])[-WINDOW:]
        self.model = Model(self.model.subset, self.buffer)
        self.costs['count_refits'] += 1
        self.costs['count_refit_rows'] += len(self.buffer)
        self.costs['refit_feature_reads'] += len(self.buffer) * len(self.model.subset)

    def prepare(self):
        pool = POOL[:N + 1] if self.variant == 'singleton' else POOL
        if self.variant == 'deterministic':
            candidates = []
            while len(candidates) < 4:
                subset = pool[self.cursor % len(pool)]
                self.cursor += 1
                if subset != self.model.subset:
                    candidates.append(subset)
        else:
            candidates = self.rng.sample([s for s in pool if s != self.model.subset], 4)
        fitted = [Model(s, self.buffer) for s in candidates]
        summaries = [{'subset': list(m.subset), 'training_loss': m.mean_loss(self.buffer),
                      'penalty': penalty(m.subset)} for m in fitted]
        for s in summaries:
            s['objective'] = s['training_loss'] + s['penalty']
        winner = min(range(4), key=lambda i: (summaries[i]['objective'], fitted[i].subset))
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4 * len(self.buffer)
        reads = len(self.buffer) * sum(len(s) for s in candidates)
        self.costs['candidate_fit_feature_reads'] += reads
        self.costs['candidate_score_feature_reads'] += reads
        return fitted[winner], {'candidates': summaries, 'winner': winner, 'cursor': self.cursor}

    def select(self, candidate, rows):
        current_loss, new_loss = self.model.mean_loss(rows), candidate.mean_loss(rows)
        prediction_gain = current_loss - new_loss
        complexity_gain = penalty(self.model.subset) - penalty(candidate.subset)
        accepted = prediction_gain + complexity_gain > .005
        self.costs['selection_outcomes'] += len(rows)
        self.costs['selection_prediction_feature_reads'] += (
            len(rows) * (len(self.model.subset) + len(candidate.subset)))
        if accepted:
            self.model = candidate
        return {'incumbent_loss': current_loss, 'candidate_loss': new_loss,
                'prediction_gain': prediction_gain, 'complexity_gain': complexity_gain,
                'gain': prediction_gain + complexity_gain, 'accepted': accepted}


class AcquisitionLearner(ProjectionLearner):
    def __init__(self, variant, proposal_seed):
        assert variant in VARIANTS
        super().__init__(variant, proposal_seed)
        self.deck = []
        self.deck_number = 0

    def prepare(self):
        if self.variant.startswith('iid'):
            candidate, details = super().prepare()
        else:
            subsets = []
            while len(subsets) < 4:
                if not self.deck:
                    self.deck = list(POOL)
                    self.rng.shuffle(self.deck)
                    self.deck_number += 1
                subset = self.deck.pop(0)
                if subset != self.model.subset and subset not in subsets:
                    subsets.append(subset)
            models = [Model(s, self.buffer) for s in subsets]
            candidates = [{'subset': list(m.subset), 'training_loss': m.mean_loss(self.buffer),
                           'penalty': penalty(m.subset)} for m in models]
            for c in candidates:
                c['objective'] = c['training_loss'] + c['penalty']
            winner = min(range(4), key=lambda i: (candidates[i]['objective'], models[i].subset))
            candidate = models[winner]
            details = {'candidates': candidates, 'winner': winner, 'cursor': self.cursor}
            self.costs['candidate_fits'] += 4
            self.costs['candidate_fit_rows'] += 4 * len(self.buffer)
            reads = sum(len(s) for s in subsets) * len(self.buffer)
            self.costs['candidate_fit_feature_reads'] += reads
            self.costs['candidate_score_feature_reads'] += reads
        details.update(deck=[list(s) for s in self.deck], deck_number=self.deck_number)
        return candidate, details

    def select(self, candidate, rows):
        assert len(rows) == 32
        old_losses = [nll(self.model.predict(r['x'], r['a']), r['y']) for r in rows]
        new_losses = [nll(candidate.predict(r['x'], r['a']), r['y']) for r in rows]
        predictive = [a - b for a, b in zip(old_losses, new_losses)]
        complexity = penalty(self.model.subset) - penalty(candidate.subset)
        gain = st.mean(predictive) + complexity
        halves = [st.mean(predictive[i:i+16]) + complexity for i in (0, 16)]
        pooled = gain > .005
        corroborated = all(g > .005 for g in halves)
        accepted = corroborated if self.variant.endswith('split') else pooled
        self.costs['selection_outcomes'] += 32
        self.costs['selection_prediction_feature_reads'] += 32 * (len(self.model.subset) + len(candidate.subset))
        if accepted:
            self.model = candidate
        return {'incumbent_loss': st.mean(old_losses), 'candidate_loss': st.mean(new_losses),
                'prediction_gain': st.mean(predictive), 'complexity_gain': complexity,
                'gain': gain, 'half_gains': halves, 'pooled_accept': pooled,
                'corroborated_accept': corroborated, 'accepted': accepted,
                'veto': self.variant.endswith('split') and pooled and not corroborated}


class Boundary:
    def __init__(self, model):
        self.model = copy.deepcopy(model)

    def predict(self, x, action):
        view = VisibleInput(x, self.model.subset)
        p = self.model.predict(view, action)
        return p, view.reads


class MemoryLearner:
    def __init__(self, variant, model, buffer, costs):
        self.variant = variant
        self.parent = tuple(model.subset)
        self.boundary = Boundary(model)
        self.source = 'fresh'
        self.prototype = copy.deepcopy(model) if variant != 'open' else None
        self.buffer = copy.deepcopy(buffer)
        self.costs = copy.deepcopy(costs)
        self.costs.update(prototype_candidate_scores=0, prototype_selection_predictions=0,
                          main_prototype_steps=0)

    @property
    def model(self):
        return self.boundary.model

    def state(self):
        return {'parent': list(self.parent), 'model': self.model.state(), 'source': self.source,
                'prototype': None if self.prototype is None else self.prototype.state()}

    def predict(self, x, action):
        p, reads = self.boundary.predict(x, action)
        self.costs['main_prediction_feature_reads'] += reads
        self.costs['main_prototype_steps'] += self.source == 'prototype'
        return p

    def update(self, row):
        self.buffer = (self.buffer+[row])[-192:]
        if self.source == 'fresh':
            self.boundary = Boundary(Model(self.model.subset, self.buffer))
            self.costs['count_refits'] += 1
            self.costs['count_refit_rows'] += len(self.buffer)
            self.costs['refit_feature_reads'] += len(self.model.subset)*len(self.buffer)

    def prepare(self):
        models = []
        for k in range(len(self.parent)+1):
            for subset in itertools.combinations(self.parent, k):
                if self.source == 'fresh' and subset == self.model.subset:
                    continue
                models.append(('fresh', Model(subset, self.buffer)))
        if self.prototype is not None and len(self.model.subset) < len(self.parent):
            models.append(('prototype', copy.deepcopy(self.prototype)))
        ranked = []
        for source, model in models:
            loss = model.mean_loss(self.buffer[-64:])
            ranked.append({'source': source, 'state': model.state(), 'training_loss': loss,
                           'penalty': penalty(model.subset), 'objective': loss+penalty(model.subset)})
            if source == 'fresh':
                self.costs['candidate_fits'] += 1
                self.costs['candidate_fit_rows'] += len(self.buffer)
                self.costs['candidate_fit_feature_reads'] += len(model.subset)*len(self.buffer)
            else:
                self.costs['prototype_candidate_scores'] += 1
            self.costs['candidate_score_feature_reads'] += len(model.subset)*len(self.buffer[-64:])
        winner = min(range(len(models)), key=lambda i: (
            ranked[i]['objective'], models[i][1].subset, models[i][0])) if models else None
        return (models[winner] if winner is not None else None), {'candidates': ranked, 'winner': winner}

    def select(self, candidate, rows):
        # Empty K can yield no candidate; the batch is still allocated, but unused.
        if candidate is None:
            return None
        source, model = candidate
        old_loss, new_loss = self.model.mean_loss(rows), model.mean_loss(rows)
        complexity = penalty(self.model.subset)-penalty(model.subset)
        gain = old_loss-new_loss+complexity
        accepted = gain > .005
        self.costs['selection_outcomes'] += len(rows)
        self.costs['selection_prediction_feature_reads'] += len(rows)*(len(self.model.subset)+len(model.subset))
        self.costs['prototype_selection_predictions'] += len(rows)*(source == 'prototype')
        if accepted:
            if self.variant == 'delete' and len(model.subset) < len(self.parent):
                self.prototype = None
            self.boundary = Boundary(model)
            self.source = source
        return {'incumbent_loss': old_loss, 'candidate_loss': new_loss,
                'prediction_gain': old_loss-new_loss,
                'complexity_gain': complexity, 'gain': gain, 'accepted': accepted}
