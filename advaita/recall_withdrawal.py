"""037: explicit recall permission and bounded evidence-triggered withdrawal."""
import copy
import hashlib
import json
import math
from .preserved_prediction import PreservedPrediction
from .state import canonical


class RecallWithdrawal(PreservedPrediction):
    def __init__(self,core,steering_policy):
        if steering_policy not in ('shadow','current','command','evidence'):
            raise ValueError('Unknown steering policy')
        super().__init__(core,'shadow' if steering_policy=='shadow' else 'recall')
        self.steering=dict(policy=steering_policy,blocked=False,window=[],commands=[],
                           monitors=[],reviews=[],monitor_queries=0,withdrawals=0)

    def predictions(self,x,a):
        result=super().predictions(x,a)
        if self._in_observe:
            value=self.archive_p(x,a) if self.memory['confirmed'] and self.memory['slot'] else None
            self._prediction_event['monitor_archive']=value
            self._prediction_event['externally_blocked']=self.steering['blocked']
            self.steering['monitor_queries']+=int(value is not None)
        return result

    def observe(self,t,row):
        result=super().observe(t,row)
        s=self.steering
        if row is None or self._prediction_event['source']!='archive':
            s['window']=[]
            return result
        # Both probabilities were produced before this label was added by the
        # inherited learner. Withdrawal changes only subsequent predictions.
        e=self._prediction_event;p=e['monitor_archive'];q=e['active'][2];y=row['y']
        s['window'].append(dict(tick=t,archive_loss=-math.log(p if y else 1-p),active_loss=-math.log(q if y else 1-q)))
        if len(s['window'])==16:
            archive=sum(x['archive_loss'] for x in s['window'])/16
            active=sum(x['active_loss'] for x in s['window'])/16
            triggered=archive-active>.02
            withdraw=triggered and s['policy']=='evidence'
            event=dict(tick=t,first_tick=s['window'][0]['tick'],n=16,archive_loss=archive,
                       active_loss=active,triggered=triggered,withdrawn=withdraw,
                       before_sha256=hashlib.sha256(self.checkpoint().encode()).hexdigest())
            if withdraw:self.memory['route']=False;s['withdrawals']+=1
            s['window']=[];event['route_after']=self.memory['route'];s['monitors'].append(event)
        return result

    def review(self,t,rows):
        result=super().review(t,rows);s=self.steering
        ordinary=self.memory['route'];s['window']=[]
        if s['blocked']:self.memory['route']=False
        s['reviews'].append(dict(tick=t,ordinary_route=ordinary,blocked=s['blocked'],effective_route=self.memory['route']))
        return result

    def set_recall_block(self,blocked,*,reason,source):
        if type(blocked) is not bool:raise ValueError('Boolean block state required')
        if not isinstance(reason,str) or not reason.strip() or not isinstance(source,str) or not source.strip():
            raise ValueError('Reason and source required')
        if not self.main_ids or self.main_ids[-1]!=self.tick:raise ValueError('Command requires a current completed labelled observation')
        if any(e['tick']==self.tick for e in self.steering['commands']):raise ValueError('One recall command per tick')
        event=dict(tick=self.tick,blocked=blocked,reason=reason,source=source,
                   previous_blocked=self.steering['blocked'],previous_route=self.memory['route'],
                   before_sha256=hashlib.sha256(self.checkpoint().encode()).hexdigest())
        self.steering['blocked']=blocked;self.steering['window']=[];self.memory['route']=False
        event['route_after']=False;self.steering['commands'].append(event)
        return copy.deepcopy(event)

    def inspect_steering(self):
        return copy.deepcopy(dict(tick=self.tick,steering=self.steering,authorized=self.memory['route'],
                                  compatible=self.compatible(),confirmed=self.memory['confirmed']))

    def checkpoint(self):
        state=json.loads(super().checkpoint());state.update(schema=37,steering=self.steering)
        return canonical(state)

    @classmethod
    def restore(cls,text):
        state=json.loads(text)
        if state['schema']!=37:raise ValueError('Unsupported recall-withdrawal checkpoint')
        steering=state.pop('steering');state['schema']=36
        obj=PreservedPrediction.restore(canonical(state));obj.__class__=cls;obj.steering=steering
        return obj
