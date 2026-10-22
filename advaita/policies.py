"""Fixed decision policies extracted from 013–015; trace-compatible rules.

Only model storage is shared/refactored. No benchmark or evaluator imports.
"""
import copy
import statistics as st
from .models import Upper, restore_upper, restore_local as restore
MODES = ('coarse', 'fine0', 'fine1')

def upper_review(upper, buffer, models, selection):
    # Construction and ranking complete before composite selection labels are read.
    candidates = [Upper(mode, buffer, models) for mode in MODES]
    losses = [m.loss(buffer, models) for m in candidates]
    best = min(range(3), key=lambda i: (losses[i], i))
    old_loss = upper.loss(selection, models)
    new_loss = candidates[best].loss(selection, models)
    accepted = old_loss > .55 and old_loss-new_loss > .02
    details = {'before': upper.state(), 'candidates': [
        {'state': m.state(), 'ranking_loss': loss} for m, loss in zip(candidates, losses)],
        'winner': best, 'old_loss': old_loss, 'new_loss': new_loss,
        'gain': old_loss-new_loss, 'failure_gate': old_loss > .55, 'accepted': accepted}
    result = candidates[best] if accepted else upper
    details['after'] = result.state()
    return result, details


class Reclosure:
    def __init__(self):
        self.pending = None
        self.costs = {'challenger_predictions': 0, 'challenger_starts': 0,
                      'group_invalidations': 0, 'failed_witnesses': 0,
                      'accepted_reclosures': 0, 'max_pending_cells': 0}

    def state(self):
        return copy.deepcopy(self.pending)

    def review(self, incumbent, prepared_coarse, models, selection, ordinary):
        before = self.state()
        groups = [m.state()['groups'] for m in models]
        detail = {'before': before, 'invalidated': False, 'witness': None}
        if ordinary['accepted']:
            self.pending = None
            detail['action'] = 'ordinary_replacement'
        elif incumbent.mode == 'coarse':
            self.pending = None
            detail['action'] = 'already_coarse'
        else:
            if self.pending is not None and self.pending['groups'] != groups:
                self.pending = None
                detail['invalidated'] = True
                self.costs['group_invalidations'] += 1
            if self.pending is None:
                self.pending = {'model': copy.deepcopy(prepared_coarse), 'groups': groups, 'passes': 0}
                self.costs['challenger_starts'] += 1
            challenger = restore_upper(self.pending['model'])
            self.costs['max_pending_cells'] = max(self.costs['max_pending_cells'], len(challenger.counts))
            loss = challenger.loss(selection, models)
            passed = loss <= .55 and loss-ordinary['old_loss'] <= .02
            self.costs['challenger_predictions'] += len(selection)
            detail['witness'] = {'model': challenger.state(), 'groups': groups,
                                 'loss': loss, 'fine_loss': ordinary['old_loss'],
                                 'passed': passed, 'prior_passes': self.pending['passes']}
            if not passed:
                self.pending = None
                self.costs['failed_witnesses'] += 1
                detail['action'] = 'witness_failed'
            else:
                self.pending['passes'] += 1
                if self.pending['passes'] == 2:
                    incumbent = challenger
                    self.pending = None
                    self.costs['accepted_reclosures'] += 1
                    detail['action'] = 'reclosed'
                else:
                    detail['action'] = 'awaiting_witness'
        detail['after'] = self.state()
        return incumbent, detail


class Retention:
    def __init__(self, variant):
        self.variant = variant
        self.established = False
        self.adequate = 0
        self.pending = None
        self.costs = dict(pending_predictions=0, pending_starts=0, pending_failures=0,
                          confirmed_replacements=0, immediate_replacements=0,
                          establishments=0, max_pending_cells=0)

    def state(self):
        return copy.deepcopy(dict(established=self.established,
                                  adequate=self.adequate, pending=self.pending))

    def decide(self, incumbent, challenger, old_loss, new_loss, batch):
        before = self.state()
        accepted, action, pending_loss = False, 'keep', None
        result = incumbent
        if self.pending is not None:
            frozen = restore(self.pending)
            pending_loss = frozen.loss(batch)
            self.costs['pending_predictions'] += len(batch)
            if old_loss-pending_loss > .005:
                result, accepted, action = frozen, True, 'confirmed'
                self.costs['confirmed_replacements'] += 1
            else:
                action = 'pending_failed'
                self.costs['pending_failures'] += 1
            self.pending = None
        elif old_loss-new_loss > .005:
            protected = self.variant == 'uniform' or (
                self.variant == 'earned' and self.established)
            if protected:
                self.pending = challenger.state()
                action = 'pending_started'
                self.costs['pending_starts'] += 1
                self.costs['max_pending_cells'] = max(
                    self.costs['max_pending_cells'], len(challenger.counts))
            else:
                result, accepted, action = challenger, True, 'immediate'
                self.costs['immediate_replacements'] += 1
        if accepted:
            self.established, self.adequate = False, 0
        else:
            self.adequate = min(2, self.adequate+1) if old_loss <= .55 else 0
            if self.adequate == 2 and not self.established:
                self.established = True
                self.costs['establishments'] += 1
        return result, dict(before=before, after=self.state(), action=action,
                            accepted=accepted, pending_loss=pending_loss)
