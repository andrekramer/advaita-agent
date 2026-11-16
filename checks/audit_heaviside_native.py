"""Independent native model/decision and contextual forecast reconstruction.

Uses earlier independent reference implementations, never the native engines or
the Stage2 adapter. Runtime ledger/checkpoint metadata are not independently rebuilt.
"""
import copy
import csv
import gzip
import hashlib
import json
import math
from pathlib import Path
import random
import signal
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'checks'))
from structural_reference import Local, Upper, fit, predict, ports, key
from memory_revision_reference import RevisionReference
from memory_control_reference import local_fit, upper_fit, encode
from audit_nested_abstractions import close

OUT=ROOT/'results/heaviside-native-v1'
HEADS=('vector','scalar','fixed','window','prior_selected')


def tuples(x): return tuple(tuples(v) for v in x) if isinstance(x,list) else x


class Native:
    def __init__(self,core,backbone):
        self.backbone=backbone;self.tick=0
        if backbone!='reference':
            self.ref=RevisionReference(core,backbone);return
        self.nodes=[]
        for seed,d in zip(core['seeds'],core['nodes']):
            n=Local(seed);n.partition=tuple(d['model']['partition']);n.table={int(k):v.copy() for k,v in d['model']['counts'].items()}
            for k in ('buffer','costs','pending','structural','queries','pending_peak'): setattr(n,k,copy.deepcopy(d[k]))
            n.deck=[tuple(p) for p in d['deck']];n.random.setstate(tuples(d['rng']));self.nodes.append(n)
        self.upper=Upper(core['upper_seed'],'delete');self.upper.deploy(core['upper'],core['upper_ports'],core['upper_training_ids'])
        self.upper.rng.setstate(tuples(core['upper_rng']));self.upper.deck=[tuple(p) for p in core['upper_deck']]
        self.upper.pending=copy.deepcopy(core['pending']);self.upper.archive=copy.deepcopy(core['archive'])
        self.buffer=copy.deepcopy(core['buffer']);self.ids=core['buffer_ids'].copy()

    def observe(self,row):
        self.tick+=1
        if self.backbone!='reference':
            rf,rs=2**(-1/64),2**(-1/1024)
            raw=[[[rf*f[k]+rs*s[k] for k in (0,1)] for f,s in zip(ft,st)] for ft,st in zip(self.ref.fast,self.ref.slow)]
            locals_=[local_fit(m['partition'],raw[j]) for j,m in enumerate(self.ref.locals)]
            upper=upper_fit(self.ref.upper['spec'],raw[2],locals_)
            k=encode(upper['spec'],locals_,row['x'],row['a'])
            event=dict(key=k,counts=upper['counts'][k],spec=upper['spec'],groups=[m['groups'] for m in locals_])
            return self.ref.observe(self.tick,row),event
        model=self.upper.model;k=key(model['spec'],self.nodes,row['x'],row['a'])
        local=[n.state() for n in self.nodes]
        event=dict(key=k,counts=model['counts'][k].copy(),spec=model['spec'].copy(),groups=[m['groups'] for m in local])
        ps=[(n.table[n.partition[x]][0]+1)/(n.table[n.partition[x]][1]+2) for n,x in zip(self.nodes,row['x'])]
        ps.append(predict(model,self.nodes,row['x'],row['a']))
        for j,n in enumerate(self.nodes): n.update(dict(x=row['x'][j],y=row['local'][j]))
        self.buffer=(self.buffer+[copy.deepcopy(row)])[-192:];self.ids=(self.ids+[f'main/{self.tick}/upper'])[-192:]
        if 2 in model['spec']: self.upper.deploy(fit(model['spec'],self.buffer,self.nodes),ports(model['spec'],self.nodes),self.ids)
        return ps,event

    def review(self,rows,saved):
        if self.backbone!='reference': self.ref.review(self.tick,rows,saved);return
        for j,n in enumerate(self.nodes): n.review(saved['local'][j],[dict(x=r['x'][j],y=r['local'][j]) for r in rows])
        self.upper.review(saved['upper'],self.buffer,self.ids,self.nodes,rows,f'select/{self.tick}')

    def verify_state(self,d):
        assert d['tick']==self.tick and d['memory']==self.backbone
        state=d['engine']
        if self.backbone!='reference': close(state,self.ref.state());return
        close(state['upper'],self.upper.model);close(state['buffer'],self.buffer);close(state['buffer_ids'],self.ids)
        close(state['pending'],self.upper.pending);close(state['upper_deck'],self.upper.deck)
        close(state['upper_rng'],self.upper.rng.getstate());assert state['archive'] is None
        close(state['upper_ports'],self.upper.ports);close(state['upper_training_ids'],self.upper.ids)
        for n,s in zip(self.nodes,state['nodes']):
            close(s['model'],n.state());close(s['buffer'],n.buffer);close(s['deck'],n.deck)
            close(s['rng'],n.random.getstate());close(s['pending'],n.pending)


class Heads:
    def __init__(self,setup):
        ones,total=setup['initial_counts'];self.success=ones+1.;self.mass=total+2.
        self.scalar=(ones+1)/(total+2);self.scalar_mass=total+2.
        self.fixed=self.scalar;self.raw_success=float(ones);self.raw_total=float(total)
        self.window=setup['acquisition_labels'].copy()

    def predict(self):
        return dict(vector=self.success/self.mass,scalar=self.scalar,fixed=self.fixed,
                    window=(sum(self.window)+1)/(len(self.window)+2),
                    prior_selected=(.9*self.raw_success+1)/(.9*self.raw_total+2))

    def state(self):
        ps=self.predict();answer={}
        for a,p in ps.items():
            mass=self.mass if a=='vector' else self.scalar_mass if a=='scalar' else self.raw_total+2 if a=='prior_selected' else len(self.window)+2 if a=='window' else None
            effective=None if mass is None else .9*mass if a in ('vector','scalar') else .9*(mass-2)+2 if a=='prior_selected' else mass
            answer[a]=dict(p=p,S_stored=mass,S_prediction=effective,theta=math.atan2(1-p,p))
        return answer

    def update(self,y):
        self.success=.9*self.success+y;self.mass=.9*self.mass+1
        self.scalar_mass=.9*self.scalar_mass+1;self.scalar+=(y-self.scalar)/self.scalar_mass
        self.fixed=.9*self.fixed+.1*y
        self.raw_success=.9*self.raw_success+y;self.raw_total=.9*self.raw_total+1
        self.window=(self.window+[y])[-192:]

    def verify(self,saved):
        close([saved['vector']['a'],saved['vector']['a']+saved['vector']['b']],[self.success,self.mass])
        close([saved['scalar']['p'],saved['scalar']['mass']],[self.scalar,self.scalar_mass])
        close(saved['fixed']['p'],self.fixed);close(saved['window']['buffer'],self.window)
        close([saved['prior_selected']['raw_a'],saved['prior_selected']['raw_a']+saved['prior_selected']['raw_b']],
              [self.raw_success,self.raw_total])


def regenerate(seed):
    mirrored=bool(seed%2);flip=lambda ys:[1-y if mirrored else y for y in ys]
    prefixes={};pr={}
    for h,n,base,rb in [('short',10,600000,1000000),('long',1000,700000,1100000)]:
        ys=[1]*(n*4//5)+[0]*(n//5);random.Random(base+seed).shuffle(ys);prefixes[h]=flip(ys)
        r=random.Random(rb+seed);pr[h]={str(t):flip([int(r.random()<.8) for _ in range(32)]) for t in sorted(set(range(64,n+1,64))|{n})}
    r=random.Random(800000+seed);stable=[int(r.random()<.8) for _ in range(512)]
    r=random.Random(900000+seed);reverse=[int(r.random()<.2) for _ in range(512)]
    reviews={}
    for f,b,q in [('stable',1200000,.8),('reversal',1300000,.2)]:
        r=random.Random(b+seed);reviews[f]={str(t):flip([int(r.random()<q) for _ in range(32)]) for t in range(64,513,64)}
    reviews['streak']=copy.deepcopy(reviews['stable'])
    return dict(seed=seed,mirrored=mirrored,prefixes=prefixes,prefix_reviews=pr,
                futures=dict(stable=flip(stable),streak=flip([0]*4+stable[4:]),reversal=flip(reverse)),reviews=reviews)


def measure(ps,ys,f,mirror):
    losses=[(p-y)**2 for p,y in zip(ps,ys)]
    lo,hi={'stable':(0,512),'streak':(4,20),'reversal':(128,256)}[f]
    delay=None
    if f=='reversal':
        delay=next((i for i in range(509) if all(p>.5 if mirror else p<.5 for p in ps[i:i+4])),None)
    return dict(primary=sum(losses[lo:hi])/(hi-lo),whole=sum(losses)/512,early=sum(losses[:64])/64,
                late=sum(losses[256:])/256,forced=sum(losses[:4])/4 if f=='streak' else None,
                recovery_seen=delay,censored=delay is None if f=='reversal' else None,
                recovery_capped=(512 if delay is None else delay) if f=='reversal' else None)


def replay(native,heads,setup,mirror,labels,review_labels,events,reviews,offset=0):
    review_index={e['tick']:e for e in reviews}
    assert len(events)==len(labels)
    for i,(y,event) in enumerate(zip(labels,events),1):
        row=dict(setup['target'],y=1-y if mirror else y)
        expected_heads=heads.predict();expected_state=heads.state()
        ps,capture=native.observe(row);outputs=dict(native=ps[2],**expected_heads)
        if mirror:outputs={a:1-p for a,p in outputs.items()}
        assert event['tick']==native.tick and event['target_matched']
        close(event['native_internal'],ps);close(event['native_row'],capture)
        close(event['outputs'],outputs);close(event['head_state'],expected_state)
        assert event['sources']=={a:'native' if a=='native' else 'context_'+a for a in outputs}
        heads.update(row['y'])
        if str(i) in review_labels:
            e=review_index[native.tick];batch=review_labels[str(i)]
            headps=heads.predict()
            scores={a:sum(((1-p if mirror else p)-z)**2 for z in batch)/len(batch) for a,p in headps.items()}
            close(e['head_review_brier'],scores)
            native.review([dict(setup['target'],y=1-z if mirror else z) for z in batch],e['native'])
    assert len(review_index)==len(review_labels)


def verify_hashes():
    m=json.loads((OUT/'manifest.json').read_text())
    for p,d in {**m['sources'],**m['frozen_dependencies']}.items(): assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    for p,d in json.loads((OUT/'artifact-hashes.json').read_text()).items(): assert hashlib.sha256((OUT/p).read_bytes()).hexdigest()==d,p
    assert hashlib.sha256((OUT/'initial.json').read_bytes()).hexdigest()==m['initial_sha256']


def main():
    dest=OUT/'audit.json';assert not dest.exists();start=time.monotonic();checked=0
    def timeout(*_):raise TimeoutError('Native audit 900-second ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        verify_hashes();setup=json.loads((OUT/'initial.json').read_text())
        with gzip.open(ROOT/'results/recall-withdrawal-v1/runs.jsonl.gz','rt') as f: source=json.loads(next(f))['acquisition_checkpoint']
        source['variant']='delete';close(setup['core'],source)
        assert setup['initial_counts']==[27,32] and len(setup['acquisition_labels'])==32 and sum(setup['acquisition_labels'])==27
        worlds=json.loads((OUT/'worlds.json').read_text());close(worlds,[regenerate(s) for s in range(3000,3040)])
        ws={w['seed']:w for w in worlds};prefixes={}
        with gzip.open(OUT/'prefixes.jsonl.gz','rt') as f:
            for line in f:
                r=json.loads(line);w=ws[r['seed']];h=r['history'];b=r['backbone']
                n=Native(setup['core'],b);heads=Heads(setup)
                replay(n,heads,setup,w['mirrored'],w['prefixes'][h],w['prefix_reviews'][h],r['events'],r['reviews'])
                n.verify_state(r['checkpoint']['native']);heads.verify(r['checkpoint']['heads'])
                prefixes[r['seed'],h,b]=(n,heads)
        assert len(prefixes)==240
        print('All 240 native prefixes independently reconstructed.',flush=True)
        records={}
        with gzip.open(OUT/'runs.jsonl.gz','rt') as f:
            for line in f:
                r=json.loads(line);w=ws[r['seed']];h=r['history'];future=r['future'];b=r['backbone']
                n,heads=copy.deepcopy(prefixes[r['seed'],h,b])
                replay(n,heads,setup,w['mirrored'],w['futures'][future],w['reviews'][future],r['events'],r['reviews'])
                n.verify_state(r['checkpoint']['native']);heads.verify(r['checkpoint']['heads'])
                for arm,ps in r['predictions'].items():
                    close(ps,[e['outputs'][arm] for e in r['events']])
                    close(r['metrics'][arm],measure(ps,w['futures'][future],future,w['mirrored']))
                records[r['seed'],h,future,b]={k:v for k,v in r.items() if k not in ('events','checkpoint')}
                checked+=1
                if checked%120==0:print(f'{checked}/720 native futures reconstructed.',flush=True)
        assert len(records)==720
        result=json.loads((OUT/'results.json').read_text());summary=result['summary'];ds={};samples={}
        definitions={f'vector_vs_{b}':('reference','vector',b,'native') for b in ('reference','relaxed','combined')}
        definitions.update({f'vector_vs_{a}':('reference','vector','reference',a) for a in ('fixed','window','prior_selected')})
        definitions['combined_vs_relaxed']=('combined','native','relaxed','native')
        for name,(cb,ca,bb,ba) in definitions.items():
            for f in ('stable','streak','reversal'):
                by={h:[records[s,h,f,cb]['metrics'][ca]['primary']-records[s,h,f,bb]['metrics'][ba]['primary'] for s in range(3000,3040)] for h in ('short','long')}
                values=[(x+y)/2 for x,y in zip(by['short'],by['long'])]
                close(summary['contrasts'][name][f]['mean'],sum(values)/40)
                close(summary['contrasts'][name][f]['by_history'],{h:sum(xs)/40 for h,xs in by.items()})
                ds[name,f]=values;samples[name,f]=[]
        rng=random.Random(177)
        for _ in range(10000):
            weights=[0]*40
            for _ in range(40):weights[rng.randrange(40)]+=1
            for k,values in ds.items():samples[k].append(sum(n*v for n,v in zip(weights,values))/40)
        for (name,f),xs in samples.items():
            xs.sort()
            for label,q in [('low',.025),('high',.975)]:
                pos=9999*q;i=int(pos);close(summary['contrasts'][name][f][label],xs[i]+(xs[i+1]-xs[i])*(pos-i))
        good=lambda name:all(summary['contrasts'][name][f]['high']<(0 if f=='streak' else .01) for f in ('stable','streak','reversal'))
        assert summary['native_pass']==(good('vector_vs_reference') and good('vector_vs_combined'))
        assert summary['attribution_pass']==good('vector_vs_fixed')
        error=max(abs(p-q) for r in records.values() for p,q in zip(r['predictions']['vector'],r['predictions']['scalar']))
        close(error,summary['scalar_max_error']);assert error<=1e-12
        for s in range(3000,3040):
            for h in ('short','long'):
                for f in ('stable','streak','reversal'):
                    for b in ('relaxed','combined'):
                        for a in HEADS:assert records[s,h,f,b]['predictions'][a]==records[s,h,f,'reference']['predictions'][a]
        weak=[]
        for r in records.values():
            if r['backbone']=='reference':continue
            for rev in r['reviews']:
                for d in rev['native']['weakenings']:
                    if d['accepted']:weak.append(dict(seed=r['seed'],history=r['history'],future=r['future'],backbone=r['backbone'],relative_tick=rev['relative_tick'],channel=d['channel'],removed_mass=d['removed_mass']))
        close(weak,summary['accepted_future_weakenings'])
        with (OUT/'metrics.csv').open() as f:
            rows=list(csv.DictReader(f));assert len(rows)==4320
            for row in rows:
                r=records[int(row['seed']),row['history'],row['future'],row['backbone']]
                for k,value in r['metrics'][row['arm']].items():assert row[k]==('' if value is None else str(value))
        close(result['counts'],dict(prefixes=240,native_futures=720,output_records=4320,checkpoint_roundtrips=1440,
            main_rows=489840,review_rows=249600,main_scalar_presentations=1469520,review_scalar_presentations=748800,
            head_updates=2449200,materialized_composite_labels=154320,distinct_constructed_composite_labels=123760))
        verify_hashes()
        data=dict(status='pass',prefixes=240,native_futures=720,output_records=4320,
                  native_pass=summary['native_pass'],attribution_pass=summary['attribution_pass'],
                  scope='independent forecasts, native review decisions, final learning state and metrics; runtime metadata roundtrips checked by runner',
                  elapsed_seconds=time.monotonic()-start)
    except BaseException as exc:
        data=dict(status='failed',error=repr(exc),checked_futures=checked,elapsed_seconds=time.monotonic()-start);raise
    finally:
        signal.alarm(0)
        with dest.open('x') as f:json.dump(data,f,indent=2);f.write('\n')
    print(json.dumps(data),flush=True)


if __name__=='__main__':main()
