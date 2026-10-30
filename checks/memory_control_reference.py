"""Independent 026 arithmetic/policy replay; no runtime or experiment imports."""
import copy
import itertools
import math
import random
from statistics import mean
from audit_nested_abstractions import close,logloss

PARTITIONS=[(0,)+bits for bits in itertools.product((0,1),repeat=3)]
SPECIFICATIONS=[x for x in itertools.product((0,1,2),repeat=2) if x!=(2,2)]

def probability(c):return (1+c[0])/(2+c[1])
def lp(model,x):return probability(model['counts'][str(model['partition'][x])])
def encode(spec,local,x,a):
    code=[]
    for j,s in enumerate(spec):
        if s==1:code.append(local[j]['groups'][x[j]])
        elif s==2:code.append(x[j])
    code.append(a);return '|'.join(str(v) for v in code)
def up(model,local,x,a):return probability(model['counts'][encode(model['spec'],local,x,a)])
def reduced(s,current):return list(s)!=list(current) and all(a<=b for a,b in zip(s,current))
def size(s):return 2**(1+s[0]+s[1])

def local_fit(partition,evidence):
    counts={str(k):[0.,0.] for k in sorted(set(partition))}
    for state in range(4):
        cell=counts[str(partition[state])];cell[0]+=evidence[state][0];cell[1]+=evidence[state][1]
    order=sorted(counts,key=lambda k:(probability(counts[k]),int(k)))
    return dict(partition=list(partition),counts=counts,groups=[order.index(str(partition[x])) for x in range(4)])

def upper_fit(spec,evidence,local):
    counts={'|'.join(str(v) for v in k):[0.,0.] for k in itertools.product(*[range(2**s) for s in spec if s],range(2))}
    for left in range(4):
        for right in range(4):
            for action in range(2):
                src=evidence[8*left+2*right+action];dst=counts[encode(spec,local,[left,right],action)]
                dst[0]+=src[0];dst[1]+=src[1]
    return dict(spec=list(spec),counts=counts)


class Reference:
    def __init__(self,checkpoint,policy):
        self.policy=policy;self.tick=0
        self.fast=[[[0.,0.] for _ in range(n)] for n in [4,4,32]];self.slow=copy.deepcopy(self.fast)
        for j,node in enumerate(checkpoint['nodes']):
            for row in node['buffer']:
                v=self.fast[j][row['x']];v[0]+=row['y'];v[1]+=1
        for row in checkpoint['buffer']:
            v=self.fast[2][8*row['x'][0]+2*row['x'][1]+row['a']];v[0]+=row['y'];v[1]+=1
        self.locals=[copy.deepcopy(n['model']) for n in checkpoint['nodes']];self.upper=copy.deepcopy(checkpoint['upper'])
        self.decks=[[tuple(p) for p in n['deck']] for n in checkpoint['nodes']]+[[tuple(s) for s in checkpoint['upper_deck']]]
        def tuples(x):return tuple(tuples(v) for v in x) if isinstance(x,(tuple,list)) else x
        self.rngs=[random.Random() for _ in range(3)]
        for j,n in enumerate(checkpoint['nodes']):self.rngs[j].setstate(tuples(n['rng']))
        self.rngs[2].setstate(tuples(checkpoint['upper_rng']))
        self.pending=[None,None,None];self.main_ids=[];self.selection_ids=[]
        self.costs=dict(candidate_fits=0,active_fits=0,probe_fits=0,raw_bin_visits=0,scoring_queries=0,memory_scores=0,transfers=0,proposals=0,transferred_mass=0.,observations=0,ticks=0)
        self.refresh()
    def total(self,j):return [[self.fast[j][x][k]+self.slow[j][x][k] for k in (0,1)] for x in range(len(self.fast[j]))]
    def fit(self,j,shape,raw,kind='candidate'):
        self.costs[kind+'_fits']+=1;self.costs['raw_bin_visits']+=len(raw)
        return local_fit(shape,raw) if j<2 else upper_fit(shape,raw,self.locals)
    def refresh(self):
        for j in (0,1):self.locals[j]=self.fit(j,self.locals[j]['partition'],self.total(j),'active')
        self.upper=self.fit(2,self.upper['spec'],self.total(2),'active')
    def state(self):
        return dict(schema=26,policy=self.policy,tick=self.tick,fast=self.fast,slow=self.slow,locals=self.locals,upper=self.upper,decks=self.decks,
            rngs=[g.getstate() for g in self.rngs],pending=self.pending,main_ids=self.main_ids,selection_ids=self.selection_ids,costs=self.costs)
    def mass(self):return {name:[sum(v[1] for v in bank[j]) for j in range(3)] for name,bank in [('fast',self.fast),('slow',self.slow)]}
    def observe(self,t,row):
        assert t==self.tick+1;self.tick=t;self.costs['ticks']+=1
        rates=[2**(-1/(1024 if self.policy=='slow' else 64)),1. if self.policy=='permanent' else 2**(-1/1024)]
        if self.policy!='activity' or row is not None:
            for bank,rho in zip((self.fast,self.slow),rates):
                for table in bank:
                    for cell in table:cell[0]*=rho;cell[1]*=rho
        self.refresh()
        if row is None:return None
        ps=[lp(self.locals[j],row['x'][j]) for j in (0,1)]+[up(self.upper,self.locals,row['x'],row['a'])]
        indices=row['x']+[8*row['x'][0]+2*row['x'][1]+row['a']];ys=row['local']+[row['y']]
        for j,(index,y) in enumerate(zip(indices,ys)):self.fast[j][index][0]+=y;self.fast[j][index][1]+=1
        self.main_ids.append(t);self.costs['observations']+=1;self.refresh();return ps
    def candidates(self,j,shape):
        out=[(0,0,0,0)] if j<2 and len(set(shape))>1 else []
        while len(out)<4:
            if not self.decks[j]:
                self.decks[j]=(PARTITIONS if j<2 else SPECIFICATIONS).copy();self.rngs[j].shuffle(self.decks[j])
            p=self.decks[j].pop(0)
            if list(p)==list(shape) or p in out or (j<2 and p==(0,0,0,0)):continue
            out.append(p)
        if j==2:
            for p in SPECIFICATIONS:
                if reduced(p,shape) and p not in out:out.append(p)
        return out
    def fresh_loss(self,j,model,rows):
        self.costs['scoring_queries']+=len(rows)
        return mean(logloss(lp(model,r['x'][j]) if j<2 else up(model,self.locals,r['x'],r['a']),r['local'][j] if j<2 else r['y']) for r in rows)
    def ranking(self,j,model,raw):
        numerator=[]
        for i,v in enumerate(raw):
            p=lp(model,i) if j<2 else up(model,self.locals,[i//8,i//2%4],i%2)
            numerator.append(v[0]*logloss(p,1)+(v[1]-v[0])*logloss(p,0))
        self.costs['scoring_queries']+=len(raw);mass=sum(v[1] for v in raw)
        return sum(numerator)/mass if mass else math.log(2)
    def review_channel(self,j,rows,saved):
        old_model=copy.deepcopy(self.locals[j] if j<2 else self.upper);shape=old_model['partition' if j<2 else 'spec'];raw=self.total(j)
        proposals=self.candidates(j,shape);models=[self.fit(j,p,raw) for p in proposals];ranks=[self.ranking(j,m,raw) for m in models]
        close(saved['ranks'],ranks)
        # Use verified saved bits only to preserve deterministic exact-tie ranking.
        order=saved['ranks'];eligible=[i for i,p in enumerate(proposals) if len(set(p))>=len(set(shape))] if j<2 else [i for i,p in enumerate(proposals) if not reduced(p,shape)]
        best=min(eligible,key=lambda i:(order[i],len(set(proposals[i])),proposals[i])) if j<2 else min(eligible,key=lambda i:(order[i],size(proposals[i]),proposals[i].count(2),proposals[i])) if eligible else None
        old=self.fresh_loss(j,old_model,rows);new=None if best is None else self.fresh_loss(j,models[best],rows)
        previous=copy.deepcopy(self.pending[j]);witness=None;invalidated=False;action='keep';chosen=old_model
        if new is not None and ((old-new>.005) if j<2 else (old>.55 and old-new>.02)):
            chosen=models[best];self.pending[j]=None;action='improved'
        else:
            if j==2 and self.pending[j] is not None:
                binding=[self.locals[k]['groups'] if s==1 else None for k,s in enumerate(self.pending[j]['model']['spec'])]
                if binding!=self.pending[j]['binding']:self.pending[j]=None;invalidated=True
            opts=([proposals.index((0,0,0,0))] if len(set(shape))>1 else []) if j<2 else [i for i,p in enumerate(proposals) if reduced(p,shape) and order[i]<=.55]
            if self.pending[j] is None and opts:
                i=opts[0] if j<2 else min(opts,key=lambda k:(size(proposals[k]),proposals[k].count(2),order[k],proposals[k]))
                m=models[i];self.pending[j]=dict(model=copy.deepcopy(m),passes=0,binding=None if j<2 else [self.locals[k]['groups'] if s==1 else None for k,s in enumerate(m['spec'])])
            if self.pending[j] is not None:
                entry=self.pending[j];value=self.fresh_loss(j,entry['model'],rows);passed=value<=.55 and value-old<=.02
                witness=dict(loss=value,passed=passed,prior_passes=entry['passes'])
                if not passed:self.pending[j]=None;action='reduction_failed'
                elif entry['passes']==1:chosen=entry['model'];self.pending[j]=None;action='collapsed' if j<2 else 'reduced'
                else:entry['passes']=1;action='awaiting_reduction'
        if j<2:self.locals[j]=copy.deepcopy(chosen)
        else:self.upper=copy.deepcopy(chosen)
        expected=dict(before=old_model,proposals=[list(p) for p in proposals],candidates=models,ranks=ranks,winner=best,old_loss=old,new_loss=new,
            action=action,witness=witness,invalidated=invalidated,pending_before=previous,pending_after=self.pending[j],after=chosen)
        close(saved,expected)
    def transfer(self,j,rows,saved):
        fast=sum(v[1] for v in self.fast[j]);slow=sum(v[1] for v in self.slow[j])
        fraction=min(.25,max(0.,512-slow)/fast) if fast else 0.
        raw=[[s[k]+fraction*f[k] for k in (0,1)] for f,s in zip(self.fast[j],self.slow[j])]
        shape=self.locals[j]['partition'] if j<2 else self.upper['spec']
        incumbent=self.fit(j,shape,self.slow[j]);candidate=self.fit(j,shape,raw)
        old=self.fresh_loss(j,incumbent,rows);new=self.fresh_loss(j,candidate,rows);self.costs['memory_scores']+=2*len(rows)
        gate=new<=.55 and old-new>.005;eligible=self.policy not in ('fast','slow')
        accepted=eligible and fraction>0 and (self.policy=='always' or gate);self.costs['proposals']+=int(eligible and fraction>0)
        before=self.total(j)
        if accepted:
            for f,s in zip(self.fast[j],self.slow[j]):
                for k in (0,1):transfer=fraction*f[k];f[k]-=transfer;s[k]+=transfer
            self.costs['transfers']+=1;self.costs['transferred_mass']+=fraction*fast
        close(before,self.total(j))
        assert sum(v[1] for v in self.slow[j])<=512+1e-8
        close(saved,dict(channel=j,fraction=fraction,old_loss=old,new_loss=new,gate=gate,accepted=accepted,
            moved_mass=fraction*fast if accepted else 0.,before_mass=[fast,slow],after_mass=[sum(v[1] for v in self.fast[j]),sum(v[1] for v in self.slow[j])]))
    def review(self,t,rows,saved):
        assert t==self.tick and t in self.main_ids and t not in self.selection_ids;self.selection_ids.append(t)
        assert saved['index']==t
        for j in range(3):self.review_channel(j,rows,saved['channels'][j])
        for j in range(3):self.transfer(j,rows,saved['migrations'][j])
        close(saved['mass'],self.mass())
