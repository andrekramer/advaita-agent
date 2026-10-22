"""Partition search and optional retention, preserving 013/015 decisions."""
import copy
import itertools as it
import random
from .models import LocalModel, restore_local as restore
from .policies import Retention
PARTITIONS = [(0,)+bits for bits in it.product((0, 1), repeat=3)]

class LocalLearner:
    def __init__(self, seed):
        self.model = LocalModel()
        self.buffer, self.deck = [], []
        self.rng = random.Random(seed)
        self.costs = {'candidate_fits': 0, 'candidate_fit_rows': 0,
                      'refits': 0, 'refit_rows': 0}

    def update(self, row):
        self.buffer = (self.buffer+[row])[-192:]
        self.model = LocalModel(self.model.partition, self.buffer)
        self.costs['refits'] += 1
        self.costs['refit_rows'] += len(self.buffer)

    def review(self, selection):
        before = self.model.state()
        proposals = []
        while len(proposals) < 4:
            if not self.deck:
                self.deck = PARTITIONS.copy()
                self.rng.shuffle(self.deck)
            p = self.deck.pop(0)
            if p != self.model.partition and p not in proposals:
                proposals.append(p)
        models = [LocalModel(p, self.buffer) for p in proposals]
        losses = [m.loss(self.buffer[-64:]) for m in models]
        best = min(range(4), key=lambda i: (
            losses[i], len(models[i].counts), models[i].partition))
        old_loss, new_loss = self.model.loss(selection), models[best].loss(selection)
        gain = old_loss-new_loss
        if gain > .005:
            self.model = models[best]
        self.costs['candidate_fits'] += 4
        self.costs['candidate_fit_rows'] += 4*len(self.buffer)
        return {'before': before, 'candidates': [
            {'state': m.state(), 'ranking_loss': loss} for m, loss in zip(models, losses)],
            'winner': best, 'old_loss': old_loss, 'new_loss': new_loss,
            'gain': gain, 'accepted': gain > .005,
            'after': self.model.state(), 'deck': [list(p) for p in self.deck]}


class ProtectedLearner(LocalLearner):
    def __init__(self, seed, variant):
        super().__init__(seed)
        self.policy = Retention(variant)

    def review(self, batch):
        # Reuse the frozen 013 search exactly; replace only its acceptance step.
        ordinary = super().review(batch)
        incumbent = restore(ordinary['before'])
        candidate = restore(ordinary['candidates'][ordinary['winner']]['state'])
        self.model, policy = self.policy.decide(
            incumbent, candidate, ordinary['old_loss'], ordinary['new_loss'], batch)
        return {'ordinary': ordinary, 'policy': policy, 'after': self.model.state()}
