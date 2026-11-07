"""036: one corroborated immutable downstream predictor, optionally routed.

The active schema-34 learning operations never consult this archive. Recall is
an output path, not an evidence injection or a veto on structural learning.
"""
import copy
import hashlib
import json
import math
from .coordinated_steering import CoordinatedMemory
from .memory_control import upper_p
from .state import canonical, fingerprint


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def ports(locals_,spec):
    return [dict(name='action',domain=[0,1],meaning='fixed action alphabet')]+[
        dict(name=f'local{j}',domain=list(range(4)) if mode==2 else [0,1],
             meaning=list(range(4)) if mode==2 else locals_[j]['groups'].copy())
        for j,mode in enumerate(spec) if mode]


class PreservedPrediction(CoordinatedMemory):
    def __init__(self,core,recall):
        if recall not in ('discard','shadow','recall'):raise ValueError('Unknown archive policy')
        super().__init__(core)
        self.recall=recall
        self.memory=dict(slot=None,passes=0,confirmed=False,attempt_complete=False,
                         route=False,events=[],prediction_uses=0,blocked_predictions=0,
                         diagnostic_queries=0,archive_prediction_queries=0,
                         acquisition_sha256=hashlib.sha256(core.checkpoint().encode()).hexdigest())
        self._in_observe=False
        self._prediction_event=None

    def compatible(self):
        slot=self.memory['slot']
        return slot is not None and slot['dependency']==fingerprint(ports(self.locals,slot['upper']['spec']))

    def archive_p(self,x,a):
        slot=self.memory['slot']
        if slot is None:raise ValueError('No stored predictor')
        return upper_p(slot['upper'],slot['locals'],x,a)

    def active_predictions(self,x,a):
        return super().predictions(x,a)

    def predictions(self,x,a):
        active=self.active_predictions(x,a);ps=active.copy()
        compatible=self.compatible()
        use=self.recall=='recall' and self.memory['confirmed'] and self.memory['route'] and compatible
        if use:ps[2]=self.archive_p(x,a)
        if self._in_observe:
            self._prediction_event=dict(active=active,source='archive' if use else 'active',compatible=compatible)
        return ps

    def observe(self,t,row):
        self._in_observe=True
        try:result=super().observe(t,row)
        finally:self._in_observe=False
        if row is not None:
            used=self._prediction_event['source']=='archive'
            self.memory['prediction_uses']+=int(used)
            self.memory['archive_prediction_queries']+=int(used)
            self.memory['blocked_predictions']+=int(self.recall=='recall' and self.memory['route'] and not self._prediction_event['compatible'])
        return result

    def review(self,t,rows):
        if t!=self.tick or t in self.selection_ids or not rows:raise ValueError('Fresh current review required')
        slot=self.memory['slot'];event=None
        if t>=448:
            active=[self.active_predictions(r['x'],r['a'])[2] for r in rows]
            # Discard keeps no past predictor: a second active score is its
            # explicit query-count-matched dummy, never a hidden archive.
            archived=[self.archive_p(r['x'],r['a']) for r in rows] if slot else [upper_p(self.upper,self.locals,r['x'],r['a']) for r in rows]
            loss=lambda ps:sum(-math.log(p if r['y'] else 1-p) for p,r in zip(ps,rows))/len(rows)
            event=dict(tick=t,active_predictions=active,archive_predictions=archived,
                       active_loss=loss(active),archive_loss=loss(archived),dummy=slot is None,
                       compatible_before=self.compatible(),model_sha256=digest(dict(locals=self.locals,upper=self.upper)),
                       slot_sha256=None if slot is None else digest(slot),batch_sha256=digest(rows),
                       passes_before=self.memory['passes'],route_before=self.memory['route'])
            self.memory['diagnostic_queries']+=2*len(rows)
            if slot and t in (448,512):
                self.memory['passes']=self.memory['passes']+1 if event['compatible_before'] and event['archive_loss']<=.55 else 0
        result=super().review(t,rows)
        if t==384:
            self.memory['slot']=dict(upper=copy.deepcopy(self.upper),locals=[dict(groups=m['groups'].copy()) for m in self.locals],
                dependency=fingerprint(ports(self.locals,self.upper['spec'])),ports=ports(self.locals,self.upper['spec']),
                captured_at=t,acquisition_sha256=self.memory['acquisition_sha256'],main_ids=self.main_ids.copy(),selection_ids=self.selection_ids.copy(),
                source_model_sha256=digest(dict(locals=self.locals,upper=self.upper)),evidence_mass=copy.deepcopy(self.mass()))
        if event:
            compatible=self.compatible()
            if t in (448,512) and not compatible:self.memory['passes']=0
            if t==512:
                self.memory['confirmed']=self.memory['passes']==2 and compatible
                self.memory['attempt_complete']=True
                # Failed and discarded candidates leave no model in memory.
                if not self.memory['confirmed'] or self.recall=='discard':self.memory['slot']=None
            # No admission on the confirmation batch. Reauthorization is for
            # one interval; compatibility is also checked on every prediction.
            eligible=t>=576 and self.memory['confirmed'] and self.memory['slot'] is not None and event['compatible_before'] and compatible
            admitted=bool(eligible and event['archive_loss']<=.55 and event['active_loss']-event['archive_loss']>=.02)
            self.memory['route']=admitted and self.recall=='recall'
            event.update(compatible_after=compatible,passes_after=self.memory['passes'],confirmed=self.memory['confirmed'],eligible=bool(eligible),admitted=admitted,route_after=self.memory['route'])
            self.memory['events'].append(event)
        return result

    def checkpoint(self):
        d=json.loads(super().checkpoint());d.update(schema=36,recall=self.recall,memory=self.memory)
        return canonical(d)

    @classmethod
    def restore(cls,text):
        d=json.loads(text)
        if d['schema']!=36:raise ValueError('Unsupported preserved-prediction checkpoint')
        recall=d.pop('recall');memory=d.pop('memory');d['schema']=34
        obj=CoordinatedMemory.restore(canonical(d));obj.__class__=cls
        obj.recall=recall;obj.memory=memory;obj._in_observe=False;obj._prediction_event=None
        return obj
