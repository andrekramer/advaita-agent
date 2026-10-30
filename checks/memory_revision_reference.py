"""Independent 027 decisions; uses only the frozen independent 026 arithmetic."""
import copy
from memory_control_reference import Reference
from audit_nested_abstractions import close


class RevisionReference(Reference):
    def __init__(self,checkpoint,mode):
        super().__init__(checkpoint,'fast' if mode=='fast' else 'selective')
        self.mode=mode;self.revision_pending=[None,None,None]
        self.costs.update(weakening_tests=0,weakenings=0,removed_mass=0.)

    def state(self):
        result=super().state();result.update(schema=27,mode=self.mode,revision_pending=self.revision_pending)
        return result

    def revision(self,j,rows,saved):
        shape=list(self.locals[j]['partition'] if j<2 else self.upper['spec'])
        names=None if j<2 else [list(self.locals[k]['groups']) if shape[k]==1 else None for k in (0,1)]
        binding={'representation':shape,'meanings':names}
        weakened=copy.deepcopy(self.slow[j])
        for cell in weakened:
            cell[0]*=.5;cell[1]*=.5
        proposal=[[f[0]+s[0],f[1]+s[1]] for f,s in zip(self.fast[j],weakened)]
        models=[self.fit(j,shape,e) for e in [self.slow[j],self.fast[j],self.total(j),proposal]]
        values=[self.fresh_loss(j,m,rows) for m in models]
        mass=sum(c[1] for c in self.slow[j]);prior=copy.deepcopy(self.revision_pending[j])
        passed=mass>0 and values[1]<=.55 and values[0]-values[1]>.05 and values[2]-values[3]>.02
        repeated=passed and prior is not None and self.tick-prior['tick']==64 and prior['binding']==binding
        accept=mass>0 and (self.mode=='uniform' or (self.mode in ['weaken','combined'] and repeated))
        self.revision_pending[j]={'tick':self.tick,'binding':binding} if passed and not accept else None
        old_pending=copy.deepcopy(self.pending[j]);self.costs['weakening_tests']+=1
        if accept:
            self.slow[j]=weakened;self.pending[j]=None;self.refresh()
            self.costs['weakenings']+=1;self.costs['removed_mass']+=mass*.5
        close(saved,dict(channel=j,binding=binding,losses=values,qualifies=passed,corroborated=repeated,accepted=accept,
            removed_mass=mass*.5 if accept else 0.,before_mass=mass,after_mass=sum(c[1] for c in self.slow[j]),
            pending_before=prior,pending_after=self.revision_pending[j],structural_pending_before=old_pending,structural_pending_after=self.pending[j]))

    def transfer(self,j,rows,saved):
        if self.mode not in ['relaxed','combined','uniform']:return super().transfer(j,rows,saved)
        fmass=sum(c[1] for c in self.fast[j]);smass=sum(c[1] for c in self.slow[j])
        rate=min(.25,max(0.,512-smass)/fmass) if fmass else 0.
        shape=self.locals[j]['partition'] if j<2 else self.upper['spec']
        candidate=[[s[0]+rate*f[0],s[1]+rate*f[1]] for s,f in zip(self.slow[j],self.fast[j])]
        a=self.fit(j,shape,self.slow[j]);b=self.fit(j,shape,candidate)
        old=self.fresh_loss(j,a,rows);new=self.fresh_loss(j,b,rows)
        gate=old-new>.005;accept=rate>0 and gate;self.costs['memory_scores']+=2*len(rows)
        self.costs['proposals']+=int(rate>0);total=self.total(j)
        if accept:
            for i in range(len(self.fast[j])):
                for k in (0,1):
                    moved=rate*self.fast[j][i][k]
                    self.fast[j][i][k]-=moved;self.slow[j][i][k]+=moved
            self.costs['transfers']+=1;self.costs['transferred_mass']+=rate*fmass
        close(total,self.total(j));assert sum(c[1] for c in self.slow[j])<=512+1e-8
        close(saved,dict(channel=j,fraction=rate,old_loss=old,new_loss=new,gate=gate,accepted=accept,moved_mass=rate*fmass if accept else 0.,
            before_mass=[fmass,smass],after_mass=[sum(c[1] for c in self.fast[j]),sum(c[1] for c in self.slow[j])]))

    def review(self,t,rows,saved):
        assert t==self.tick and t in self.main_ids and t not in self.selection_ids
        self.selection_ids.append(t);assert saved['index']==t
        for j in range(3):self.review_channel(j,rows,saved['channels'][j])
        for j in range(3):self.revision(j,rows,saved['weakenings'][j])
        for j in range(3):self.transfer(j,rows,saved['migrations'][j])
        close(saved['mass'],self.mass())
