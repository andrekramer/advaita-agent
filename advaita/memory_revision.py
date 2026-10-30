"""027: separate admission of fast evidence from weakening slow evidence."""
import copy
import json
from .memory_control import MemoryLearner
from .state import canonical

MODES=('fast','selective','relaxed','weaken','combined','uniform')


class RevisionLearner(MemoryLearner):
    def __init__(self,core,mode):
        if mode not in MODES:raise ValueError(mode)
        super().__init__(core,'fast' if mode=='fast' else 'selective')
        self.mode=mode;self.revision_pending=[None]*3
        self.costs.update(weakening_tests=0,weakenings=0,removed_mass=0.)

    def weaken(self,j,rows):
        rep=self.locals[j]['partition'] if j<2 else self.upper['spec']
        binding=dict(representation=rep.copy(),meanings=None if j<2 else
            [self.locals[k]['groups'].copy() if s==1 else None for k,s in enumerate(rep)])
        half=[[v/2 for v in cell] for cell in self.slow[j]]
        proposed=[[f[k]+s[k] for k in (0,1)] for f,s in zip(self.fast[j],half)]
        models=[self.fit(j,rep,raw) for raw in (self.slow[j],self.fast[j],self.combined(j),proposed)]
        losses=[self.loss(j,m,rows) for m in models]
        mass=sum(v[1] for v in self.slow[j]);previous=copy.deepcopy(self.revision_pending[j])
        qualifies=mass>0 and losses[1]<=.55 and losses[0]-losses[1]>.05 and losses[2]-losses[3]>.02
        corroborated=qualifies and previous is not None and previous['tick']==self.tick-64 and previous['binding']==binding
        accepted=mass>0 and (self.mode=='uniform' or (self.mode in ('weaken','combined') and corroborated))
        self.revision_pending[j]=dict(tick=self.tick,binding=binding) if qualifies and not accepted else None
        structural_before=copy.deepcopy(self.pending[j])
        self.costs['weakening_tests']+=1
        if accepted:
            self.slow[j]=half;self.pending[j]=None;self.refit()
            self.costs['weakenings']+=1;self.costs['removed_mass']+=mass/2
        return dict(channel=j,binding=binding,losses=losses,qualifies=qualifies,corroborated=corroborated,
            accepted=accepted,removed_mass=mass/2 if accepted else 0.,before_mass=mass,
            after_mass=sum(v[1] for v in self.slow[j]),pending_before=previous,pending_after=copy.deepcopy(self.revision_pending[j]),
            structural_pending_before=structural_before,structural_pending_after=copy.deepcopy(self.pending[j]))

    def migrate(self,j,rows):
        if self.mode not in ('relaxed','combined','uniform'):return super().migrate(j,rows)
        rep=self.locals[j]['partition'] if j<2 else self.upper['spec']
        fm=sum(v[1] for v in self.fast[j]);sm=sum(v[1] for v in self.slow[j])
        fraction=min(.25,max(0.,512-sm)/fm) if fm else 0.
        raw=[[s[k]+fraction*f[k] for k in (0,1)] for f,s in zip(self.fast[j],self.slow[j])]
        old=self.loss(j,self.fit(j,rep,self.slow[j]),rows);new=self.loss(j,self.fit(j,rep,raw),rows)
        self.costs['memory_scores']+=2*len(rows);gate=old-new>.005;accepted=fraction>0 and gate
        self.costs['proposals']+=int(fraction>0)
        if accepted:
            for f,s in zip(self.fast[j],self.slow[j]):
                for k in (0,1):c=fraction*f[k];f[k]-=c;s[k]+=c
            self.costs['transfers']+=1;self.costs['transferred_mass']+=fraction*fm
        return dict(channel=j,fraction=fraction,old_loss=old,new_loss=new,gate=gate,accepted=accepted,
            moved_mass=fraction*fm if accepted else 0.,before_mass=[fm,sm],after_mass=[sum(v[1] for v in self.fast[j]),sum(v[1] for v in self.slow[j])])

    def review(self,t,rows):
        if t!=self.tick or t in self.selection_ids or t not in self.main_ids:raise ValueError('Review needs a unique current labelled tick')
        self.selection_ids.append(t)
        channels=[self.review_channel(j,rows) for j in range(3)]
        weakenings=[self.weaken(j,rows) for j in range(3)]
        migrations=[self.migrate(j,rows) for j in range(3)]
        return dict(index=t,channels=channels,weakenings=weakenings,migrations=migrations,mass=self.mass())

    def checkpoint(self):
        d=json.loads(super().checkpoint());d.update(schema=27,mode=self.mode,revision_pending=self.revision_pending)
        return canonical(d)

    @classmethod
    def restore(cls,serialized):
        d=json.loads(serialized)
        if d['schema']!=27:raise ValueError('Unsupported revision schema')
        mode=d.pop('mode');pending=d.pop('revision_pending');d['schema']=26
        obj=super().restore(canonical(d));obj.mode=mode;obj.revision_pending=pending
        return obj
