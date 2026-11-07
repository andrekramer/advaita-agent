"""035 optional controller; unchanged schema-34 learner with resumable timing state."""
import hashlib
import json
import math
from .coordinated_steering import CoordinatedMemory
from .state import canonical


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


class TemporaryPlasticity:
    def __init__(self, learner, policy, protected, opening=512, ceiling=1024):
        if policy not in ('P', 'D128', 'D256', 'D512', 'G'):
            raise ValueError('Unknown policy')
        self.learner = learner
        self.state = dict(policy=policy, protected=protected, opening=opening,
                          ceiling=ceiling, streak=0, last_loss=None,
                          closed_at=None, closure_reason=None, last_review=None)

    def review(self, t, rows):
        a, s = self.learner, self.state
        if s['last_review'] is not None and t <= s['last_review']:
            raise ValueError('Controller reviews must be fresh')
        if t != a.tick or not rows:
            raise ValueError('Current tick and a nonempty fresh batch required')
        diagnostic = None
        if s['opening'] < t <= s['ceiling']:
            # Freeze and score before any review operation or selection-label fit.
            predictions = [a.predictions(r['x'], r['a'])[2] for r in rows]
            loss = sum(-math.log(p if r['y'] else 1-p) for p,r in zip(predictions,rows))/len(rows)
            diagnostic = dict(tick=t, predictions=predictions, loss=loss,
                model_sha256=digest(dict(locals=a.locals,upper=a.upper)),
                batch_sha256=digest(rows), before_sha256=hashlib.sha256(a.checkpoint().encode()).hexdigest(),
                previous_loss=s['last_loss'], previous_streak=s['streak'])
        result = a.review(t, rows)
        control = None
        reason = None
        if t == s['opening']:
            control = a.configure(lock=[s['protected']], plastic=[] if s['policy']=='P' else [2],
                                  reason='035 supplied opening: protect local form')
        elif s['opening'] < t <= s['ceiling']:
            if s['policy']=='G' and s['closed_at'] is None:
                s['streak'] = s['streak']+1 if diagnostic['loss'] <= .55 else 0
                s['last_loss'] = diagnostic['loss']
                if s['streak'] >= 2:reason='adequate'
            elif s['policy'].startswith('D') and s['closed_at'] is None:
                if t >= s['opening']+int(s['policy'][1:]):reason='fixed'
            if t == s['ceiling']:
                if s['closed_at'] is None and s['policy']!='P':reason='ceiling'
                control = a.configure(lock=[],plastic=[],reason='035 ceiling: release lock and ordinary rates')
            elif reason:
                control = a.configure(lock=[s['protected']],plastic=[],reason='035 close boost: '+reason)
            if reason and s['closed_at'] is None:
                s['closed_at'],s['closure_reason'] = t,reason
        s['last_review'] = t
        if diagnostic is not None:
            diagnostic.update(streak=s['streak'],closed_at=s['closed_at'],closure_reason=s['closure_reason'],
                              half_lives=a.half_lives.copy(),after_sha256=hashlib.sha256(a.checkpoint().encode()).hexdigest())
        return result,control,diagnostic

    def checkpoint(self):
        return canonical(dict(schema=35,learner=json.loads(self.learner.checkpoint()),controller=self.state))

    @classmethod
    def restore(cls, text):
        data=json.loads(text)
        if data['schema']!=35:raise ValueError('Unsupported timing checkpoint')
        s=data['controller'];obj=cls(CoordinatedMemory.restore(canonical(data['learner'])),
                                   s['policy'],s['protected'],s['opening'],s['ceiling'])
        obj.state=s
        return obj
