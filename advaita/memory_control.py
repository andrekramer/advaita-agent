"""026: bounded fast/slow evidence, structural revision and selective migration.

No simulator truths or task boundaries enter this learner. Raw sufficient
statistics deliberately retain information beyond the active coarse interface.
"""
import copy
import itertools
import json
import math
import random
from statistics import mean
from .state import canonical

PARTS=[(0,)+p for p in itertools.product((0,1),repeat=3)]
SPECS=[s for s in itertools.product(range(3),repeat=2) if s!=(2,2)]
POLICIES=('fast','slow','always','selective','permanent','activity')
RF=2**(-1/64); RS=2**(-1/1024)


def nll(p,y):return -math.log(p if y else 1-p)
def cells(s):return 2*(2**s[0])*(2**s[1])
def smaller(a,b):return tuple(a)!=tuple(b) and all(x<=y for x,y in zip(a,b))
def prob(v):return (v[0]+1)/(v[1]+2)
def local_p(m,x):return prob(m['counts'][str(m['partition'][x])])
def key(spec,locals_,x,a):return '|'.join(map(str,[x[j] if s==2 else locals_[j]['groups'][x[j]] for j,s in enumerate(spec) if s]+[a]))
def upper_p(m,locals_,x,a):return prob(m['counts'][key(m['spec'],locals_,x,a)])


def fit_local(part,raw):
    counts={str(g):[0.,0.] for g in sorted(set(part))}
    for x,v in enumerate(raw):
        for k in (0,1):counts[str(part[x])][k]+=v[k]
    order=sorted(counts,key=lambda g:(prob(counts[g]),int(g)))
    return dict(partition=list(part),counts=counts,groups=[order.index(str(g)) for g in part])


def fit_upper(spec,raw,locals_):
    counts={'|'.join(map(str,k)):[0.,0.] for k in itertools.product(*[range(2**s) for s in spec if s],range(2))}
    for i,v in enumerate(raw):
        x=[i//8,(i//2)%4];a=i%2;k=key(spec,locals_,x,a)
        for z in (0,1):counts[k][z]+=v[z]
    return dict(spec=list(spec),counts=counts)


def weighted_loss(ps,raw):
    mass=sum(v[1] for v in raw)
    return sum(v[0]*nll(p,1)+(v[1]-v[0])*nll(p,0) for p,v in zip(ps,raw))/mass if mass else math.log(2)


class MemoryLearner:
    def __init__(self,core,policy):
        if policy not in POLICIES:raise ValueError(policy)
        self.policy=policy;self.tick=0
        self.fast=[[[0.,0.] for _ in range(n)] for n in (4,4,32)]
        self.slow=copy.deepcopy(self.fast)
        for j,n in enumerate(core.nodes):
            for r in n.buffer:self.add(j,r['x'],r['y'])
        for r in core.buffer:self.add(2,(r['x'][0]*4+r['x'][1])*2+r['a'],r['y'])
        self.locals=[n.model.state() for n in core.nodes];self.upper=core.upper.state()
        self.decks=[[tuple(p) for p in n.deck] for n in core.nodes]+[list(core.upper_deck)]
        self.rngs=[random.Random() for _ in range(3)]
        for rng,n in zip(self.rngs,core.nodes):rng.setstate(n.rng.getstate())
        self.rngs[2].setstate(core.upper_rng.getstate())
        self.pending=[None,None,None]
        self.main_ids=[];self.selection_ids=[]
        self.costs=dict(candidate_fits=0,active_fits=0,probe_fits=0,raw_bin_visits=0,scoring_queries=0,
            memory_scores=0,transfers=0,proposals=0,transferred_mass=0.,observations=0,ticks=0)
        self.refit()

    def add(self,j,i,y):self.fast[j][i][0]+=y;self.fast[j][i][1]+=1
    def combined(self,j):return [[a[k]+b[k] for k in (0,1)] for a,b in zip(self.fast[j],self.slow[j])]
    def fit(self,j,representation,raw,kind='candidate'):
        self.costs[kind+'_fits']+=1;self.costs['raw_bin_visits']+=len(raw)
        return fit_local(representation,raw) if j<2 else fit_upper(representation,raw,self.locals)
    def refit(self):
        self.locals=[self.fit(j,m['partition'],self.combined(j),'active') for j,m in enumerate(self.locals)]
        self.upper=self.fit(2,self.upper['spec'],self.combined(2),'active')
    def predictions(self,x,a):return [local_p(m,x[j]) for j,m in enumerate(self.locals)]+[upper_p(self.upper,self.locals,x,a)]
    def mass(self):return dict(fast=[sum(v[1] for v in t) for t in self.fast],slow=[sum(v[1] for v in t) for t in self.slow])
    def observe(self,t,row):
        if t!=self.tick+1:raise ValueError('Ticks must be consecutive and unique')
        self.tick=t;self.costs['ticks']+=1
        rf=RS if self.policy=='slow' else RF;rs=1. if self.policy=='permanent' else RS
        if row is not None or self.policy!='activity':
            for bank,rho in ((self.fast,rf),(self.slow,rs)):
                for table in bank:
                    for v in table:
                        for k in (0,1):v[k]*=rho
        self.refit()
        if row is None:return None
        ps=self.predictions(row['x'],row['a'])
        for j in (0,1):self.add(j,row['x'][j],row['local'][j])
        self.add(2,(row['x'][0]*4+row['x'][1])*2+row['a'],row['y'])
        self.main_ids.append(t);self.costs['observations']+=1;self.refit()
        return ps
    def draw(self,j,current):
        choices=PARTS if j<2 else SPECS
        proposals=[(0,0,0,0)] if j<2 and len(set(current))>1 else []
        while len(proposals)<4:
            if not self.decks[j]:self.decks[j]=choices.copy();self.rngs[j].shuffle(self.decks[j])
            p=self.decks[j].pop(0)
            if p!=tuple(current) and p not in proposals and (j==2 or p!=(0,0,0,0)):proposals.append(p)
        if j==2:proposals += [s for s in SPECS if smaller(s,current) and s not in proposals]
        return proposals
    def ps(self,j,m,rows):
        return [local_p(m,r['x'][j]) for r in rows] if j<2 else [upper_p(m,self.locals,r['x'],r['a']) for r in rows]
    def loss(self,j,m,rows):
        self.costs['scoring_queries']+=len(rows)
        return mean(nll(p,r['local'][j] if j<2 else r['y']) for p,r in zip(self.ps(j,m,rows),rows))
    def rank(self,j,m,raw):
        ps=[local_p(m,x) for x in range(4)] if j<2 else [upper_p(m,self.locals,[i//8,(i//2)%4],i%2) for i in range(32)]
        self.costs['scoring_queries']+=len(raw)
        return weighted_loss(ps,raw)
    def review_channel(self,j,rows):
        before=copy.deepcopy(self.locals[j] if j<2 else self.upper)
        rep=before['partition'] if j<2 else before['spec'];raw=self.combined(j)
        props=self.draw(j,rep);models=[self.fit(j,p,raw) for p in props];ranks=[self.rank(j,m,raw) for m in models]
        eligible=[i for i,p in enumerate(props) if (len(set(p))>=len(set(rep)) if j<2 else not smaller(p,rep))]
        winner=min(eligible,key=lambda i:(ranks[i],len(set(props[i])),props[i])) if j<2 else min(eligible,key=lambda i:(ranks[i],cells(props[i]),props[i].count(2),props[i])) if eligible else None
        old=self.loss(j,before,rows);new=self.loss(j,models[winner],rows) if winner is not None else None
        pending_before=copy.deepcopy(self.pending[j]);witness=None;action='keep';invalidated=False
        accepted=new is not None and (old-new>.005 if j<2 else old>.55 and old-new>.02)
        chosen=before
        if accepted:chosen=models[winner];self.pending[j]=None;action='improved'
        else:
            if j==2 and self.pending[j] is not None:
                # Meaning checks include only group ports actually used by the pending model.
                spec=self.pending[j]['model']['spec']
                binding=[self.locals[k]['groups'] if s==1 else None for k,s in enumerate(spec)]
                if binding!=self.pending[j]['binding']:self.pending[j]=None;invalidated=True
            candidates=([props.index((0,0,0,0))] if len(set(rep))>1 else []) if j<2 else [i for i,p in enumerate(props) if smaller(p,rep) and ranks[i]<=.55]
            if self.pending[j] is None and candidates:
                best=candidates[0] if j<2 else min(candidates,key=lambda i:(cells(props[i]),props[i].count(2),ranks[i],props[i]))
                m=models[best]
                self.pending[j]=dict(model=copy.deepcopy(m),passes=0,binding=None if j<2 else [self.locals[k]['groups'] if v==1 else None for k,v in enumerate(m['spec'])])
            if self.pending[j] is not None:
                p=self.pending[j];value=self.loss(j,p['model'],rows);passed=value<=.55 and value-old<=.02
                witness=dict(loss=value,passed=passed,prior_passes=p['passes'])
                if not passed:self.pending[j]=None;action='reduction_failed'
                elif p['passes']==1:chosen=p['model'];self.pending[j]=None;action='collapsed' if j<2 else 'reduced'
                else:p['passes']=1;action='awaiting_reduction'
        if j<2:self.locals[j]=copy.deepcopy(chosen)
        else:self.upper=copy.deepcopy(chosen)
        return dict(before=before,proposals=[list(p) for p in props],candidates=models,ranks=ranks,winner=winner,
            old_loss=old,new_loss=new,action=action,witness=witness,invalidated=invalidated,
            pending_before=pending_before,pending_after=copy.deepcopy(self.pending[j]),after=copy.deepcopy(chosen))
    def migrate(self,j,rows):
        rep=self.locals[j]['partition'] if j<2 else self.upper['spec']
        fmass=sum(v[1] for v in self.fast[j]);smass=sum(v[1] for v in self.slow[j])
        fraction=min(.25,max(0.,512-smass)/fmass) if fmass else 0.
        proposed=[[s[k]+fraction*f[k] for k in (0,1)] for f,s in zip(self.fast[j],self.slow[j])]
        old_model=self.fit(j,rep,self.slow[j]);new_model=self.fit(j,rep,proposed)
        old=self.loss(j,old_model,rows);new=self.loss(j,new_model,rows)
        self.costs['memory_scores']+=2*len(rows)
        gate=new<=.55 and old-new>.005
        eligible=self.policy in ('always','selective','permanent','activity')
        accepted=eligible and fraction>0 and (self.policy=='always' or gate)
        self.costs['proposals']+=int(eligible and fraction>0)
        if accepted:
            for f,s in zip(self.fast[j],self.slow[j]):
                for k in (0,1):c=fraction*f[k];f[k]-=c;s[k]+=c
            self.costs['transfers']+=1;self.costs['transferred_mass']+=fraction*fmass
        # No refit: sum conservation keeps deployed models unchanged immediately.
        return dict(channel=j,fraction=fraction,old_loss=old,new_loss=new,gate=gate,accepted=accepted,
            moved_mass=fraction*fmass if accepted else 0.,before_mass=[fmass,smass],after_mass=[sum(v[1] for v in self.fast[j]),sum(v[1] for v in self.slow[j])])
    def review(self,t,rows):
        if t!=self.tick or t in self.selection_ids or t not in self.main_ids:raise ValueError('Review needs a unique current labelled tick')
        self.selection_ids.append(t)
        channels=[self.review_channel(j,rows) for j in range(3)]
        migrations=[self.migrate(j,rows) for j in range(3)]
        return dict(index=t,channels=channels,migrations=migrations,mass=self.mass())
    def checkpoint(self):
        return canonical(dict(schema=26,policy=self.policy,tick=self.tick,fast=self.fast,slow=self.slow,
            locals=self.locals,upper=self.upper,decks=self.decks,rngs=[r.getstate() for r in self.rngs],
            pending=self.pending,main_ids=self.main_ids,selection_ids=self.selection_ids,costs=self.costs))
    @classmethod
    def restore(cls,serialized):
        from .runtime import tuple_tree
        d=json.loads(serialized)
        if d.pop('schema')!=26:raise ValueError('Unsupported memory schema')
        states=d.pop('rngs');obj=object.__new__(cls);obj.__dict__.update(d)
        obj.decks=[[tuple(p) for p in deck] for deck in obj.decks]
        obj.rngs=[random.Random() for _ in states]
        for rng,state in zip(obj.rngs,states):rng.setstate(tuple_tree(state))
        return obj
