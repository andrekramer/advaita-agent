"""033 independent world, selective-control, state and outcome reconstruction."""
import copy,gzip,hashlib,itertools,json,math,signal,time
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close,logloss
from audit_protection_interfaces import canonical
import audit_memory_lifecycle as life
from memory_revision_reference import RevisionReference
from memory_control_reference import lp,up,local_fit,upper_fit
ROOT=Path(__file__).resolve().parents[1]
HISTORIES=('stable','forms','repeated');POLICIES=('legacy','refreshed','lock_only','plastic_only','selective','swapped')
WINDOWS={'active':(513,1024),'burst':(513,640),'settled':(641,1024),'returning':(1025,1536),'later':(1537,2048)}

class SteeringReference(RevisionReference):
    def __init__(self,c):
        super().__init__(c,'combined');self.locked={};self.half_lives=[1024]*3;self.control_events=[]
    def state(self):
        s=super().state();s.update(schema=33,locked=self.locked,half_lives=self.half_lives,control_events=self.control_events);return s
    def observe(self,t,row):
        assert t==self.tick+1
        for j,h in enumerate(self.half_lives):
            if h!=1024:
                rate=2**(-1/h+1/1024)
                for cell in self.slow[j]:cell[0]*=rate;cell[1]*=rate
        return super().observe(t,row)
    def review_channel(self,j,rows,saved):
        if str(j) in self.locked:
            assert self.locals[j]['partition']==self.locked[str(j)] and self.pending[j] is None
            close(saved,dict(action='locked',channel=j,partition=self.locked[str(j)]))
        else:super().review_channel(j,rows,saved)
    def review(self,t,rows,saved):
        super().review(t,rows,saved);self.refresh();close(saved['post_review'],dict(locals=self.locals,upper=self.upper))
    def configure(self,lock,plastic,reason):
        before=hashlib.sha256(canonical(self.state()).encode()).hexdigest();prior=dict(locked=copy.deepcopy(self.locked),half_lives=list(self.half_lives))
        for j in set(int(x) for x in self.locked)|set(lock):self.pending[j]=None
        self.locked={str(j):list(self.locals[j]['partition']) for j in lock};self.half_lives=[128 if j in plastic else 1024 for j in range(3)]
        e=dict(tick=self.tick,reason=reason,before_sha256=before,previous=prior,locked=copy.deepcopy(self.locked),half_lives=list(self.half_lives));self.control_events.append(e);return e
    def inspect(self):
        return dict(tick=self.tick,locals=self.locals,upper=self.upper,evidence_mass=self.mass(),locked=self.locked,half_lives=self.half_lives,pending=self.pending,revision_pending=self.revision_pending,controls=self.control_events)

def verify_world(w):
    original=copy.deepcopy(w);p=1-w['affected'];n=w['phase_length']
    assert original.pop('instruction')==dict(protected=p,flexible=1-p)
    mask=[0,1,0,1];changed=[(a+b)%2 for a,b in zip(w['forms'][p],mask)]
    if all(x==changed[0] for x in changed):mask=[0,0,1,1]
    if w['branch']!='stable':
        batches=[(t,[row]) for t,row in enumerate(original['main'],1)]+[(int(t),rows) for t,rows in original['selection'].items()]
        for t,rows in batches:
            if n<t<=n+n//4:
                for row in rows:
                    d=mask[row['x'][p]];row['local'][p]=(row['local'][p]+d)%2;row['y']=(row['y']+d)%2
    life.verify_world(original)

def evaluation(ref,w,t):
    predictions=[];losses=[];correct=0;forms=life.forms(w,t,True)
    for x,y,a in life.CONTEXTS:
        ps=[lp(ref.locals[0],x),lp(ref.locals[1],y),up(ref.upper,ref.locals,[x,y],a)];predictions.append(ps);target=life.truth(w,[x,y],a,t)
        losses.append(.9*logloss(ps[2],target)+.1*logloss(ps[2],1-target));correct+=int((ps[2]>=.5)==bool(target))
    exact=[]
    for j in (0,1):
        part=ref.locals[j]['partition'];truth=forms[j]
        exact.append(all((part[x]==part[y])==(truth[x]==truth[y]) for x in range(4) for y in range(4)))
    regret=sum(losses)/32-(-.9*math.log(.9)-.1*math.log(.1))
    return dict(tick=t,predictions=predictions,partitions=[m['partition'] for m in ref.locals],spec=ref.upper['spec'],local_exact=exact,accuracy=correct/32,regret=regret,valid=all(exact) and correct==32 and regret<=.10)

def verify_run(r,w,measured=True):
    life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    legacy=r['policy']=='legacy';ref=RevisionReference(r['acquisition_checkpoint'],'combined') if legacy else SteeringReference(r['acquisition_checkpoint'])
    pos=0;controls=[];n=w['phase_length'];p=w['instruction']['protected'];q=1-p
    for t,row in enumerate(w['main'],1):
        close(r['predictions'][t-1],ref.observe(t,row))
        if str(t) in w['selection']:
            review=r['reviews'][pos];ref.review(t,w['selection'][str(t)],review)
            if r['policy'] not in ('legacy','refreshed') and t in (n,2*n):
                lock=([p] if r['policy'] in ('lock_only','selective') else [q] if r['policy']=='swapped' else []) if t==n else []
                plastic=([q] if r['policy'] in ('plastic_only','selective') else [p] if r['policy']=='swapped' else []) if t==n else []
                reason='Supplied task instruction: protect one form and adapt the other' if t==n else 'Scheduled release: restore ordinary structural and memory learning'
                controls.append(copy.deepcopy(ref.configure(lock,plastic,reason)))
            if not legacy:
                close(r['inspections'][pos],ref.inspect())
                # Independent evidence-to-model consistency, separate from saved review.
                local=[local_fit(m['partition'],ref.total(j)) for j,m in enumerate(ref.locals)]
                upper=upper_fit(ref.upper['spec'],ref.total(2),local);close(ref.locals,local);close(ref.upper,upper)
            close(r['evaluations'][pos],evaluation(ref,w,t));pos+=1
        if t==3*n//2:
            close(r['restore_check'],dict(tick=t,sha256=hashlib.sha256(canonical(ref.state()).encode()).hexdigest()))
    assert len(r['predictions'])==len(w['main']) and pos==len(r['reviews'])==len(r['evaluations'])
    assert len(r['inspections'])==(0 if legacy else pos)
    close(r['checkpoint'],ref.state());close(r['controls'],controls);close(r['costs'],ref.costs)
    assert r['feedback_labels']==r['acquisition']['costs']['feedback_labels']+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    if not legacy:assert not ref.locked and ref.half_lives==[1024]*3
    if measured:verify_metrics(r,w)

def verify_metrics(r,w):
    data={'observed':[],'expected':[]}
    for t,row in enumerate(w['main'],1):
        ps=r['predictions'][t-1];f=life.forms(w,t,True);truth=[f[j][row['x'][j]] for j in range(2)]+[life.truth(w,row['x'],row['a'],t)]
        data['observed'].append([logloss(p,y) for p,y in zip(ps,row['local']+[row['y']])]);data['expected'].append([.9*logloss(p,y)+.1*logloss(p,1-y) for p,y in zip(ps,truth)])
    ms={}
    for typ,rows in data.items():
        ms[typ]={}
        for k,(lo,hi) in WINDOWS.items():ms[typ][k]=[sum(row[j] for row in rows[lo-1:hi])/(hi-lo+1) for j in range(3)]
    p=1-w['affected'];burst=[e for e in r['evaluations'] if 513<=e['tick']<=640];active=[e for e in r['evaluations'] if 513<=e['tick']<=1024];end=r['evaluations'][-1]
    ms.update(protected=p,flexible=1-p,burst_correct=sum(e['local_exact'][p] for e in burst)/len(burst),active_local_correct=[sum(e['local_exact'][j] for e in active)/len(active) for j in range(2)],final_valid=end['valid'],final_local_exact=end['local_exact'],final_spec=end['spec']);close(r['metrics'],ms)

def verify_summary(rs,saved):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in rs});d={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r['metrics'] for r in rs};groups=[];paired=[]
    for h in HISTORIES:
        for policy in POLICIES:
            ms=[d[s,q,h,policy] for s,q in pairs]
            groups.append(dict(history=h,policy=policy,burst_correct=mean(m['burst_correct'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),**{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed')}))
        for s,q in pairs:
            a=d[s,q,h,'selective'];b=d[s,q,h,'refreshed'];lock=d[s,q,h,'lock_only'];j=a['flexible']
            paired.append(dict(seed=s,proposal_seed=q,history=h,plastic_gain=lock['expected']['active'][j]-a['expected']['active'][j],composite_gain=b['expected']['active'][2]-a['expected']['active'][2],costs={k:[a['expected'][k][i]-b['expected'][k][i] for i in range(3)] for k in WINDOWS}))
    close(saved['groups'],groups);close(saved['paired'],paired);changing=[p for p in paired if p['history']!='stable']
    get={(g['history'],g['policy']):g for g in groups}
    gates=dict(protection=all(get[h,'selective']['burst_correct']>=.95 and get[h,'selective']['burst_correct']>=get[h,'refreshed']['burst_correct'] for h in ('forms','repeated')),plastic_gain=mean(p['plastic_gain'] for p in changing)>=.01,plastic_consistency=sum(p['plastic_gain']>0 for p in changing)>=14,composite_gain=mean(p['composite_gain'] for p in changing)>=.005,composite_consistency=sum(p['composite_gain']>0 for p in changing)>=12,preservation=True,final_validity=all(get[h,'selective']['final_valid']>=8 for h in HISTORIES))
    for h in HISTORIES:
        for k in ['returning','later']+(['active'] if h=='stable' else []):
            for j in range(3):
                costs=[p['costs'][k][j] for p in paired if p['history']==h]
                if sum(costs)/len(costs)>.02 or any(c>.1 for c in costs):gates['preservation']=False
    close(saved['gates'],gates);assert saved['empirical_pass']==all(gates.values())
    close(saved['environment_means'],[dict(seed=s,plastic_gain=mean(p['plastic_gain'] for p in changing if p['seed']==s),composite_gain=mean(p['composite_gain'] for p in changing if p['seed']==s)) for s in sorted({p['seed'] for p in changing})])

def verify_parity(rs):
    lookup={(r['seed'],r['history'],r['proposal_seed'],r['policy']):r for r in rs};maximum=0
    for key,r in lookup.items():
        if key[3]!='refreshed':continue
        old=lookup[(*key[:3],'legacy')]
        maximum=max(maximum,max(abs(a-b) for ps,qs in zip(r['predictions'],old['predictions']) for a,b in zip(ps,qs)))
        for fresh,prior in zip(r['reviews'],old['reviews']):close({k:v for k,v in fresh.items() if k!='post_review'},prior)
        expected=copy.deepcopy(old['costs']);expected['active_fits']+=3*len(r['reviews']);expected['raw_bin_visits']+=40*len(r['reviews']);close(r['costs'],expected)
    assert maximum<=1e-12
    return dict(status='pass',paired_runs=sum(r['policy']=='refreshed' for r in rs),maximum_prediction_delta=maximum)

def verify_totals(rs,ws,saved):
    out=dict(runs=len(rs),generated_labels=0,used_labels=0,candidate_fits=0,scoring_queries=0,raw_bin_visits=0,main_predictions=0,grid_predictions=0)
    for w in ws:out['generated_labels']+=sum(len(xs) for xs in w['local_main'])+sum(len(xs) for batch in w['local_selection'] for xs in batch)+len(w['composition'])+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    for r in rs:
        out['used_labels']+=r['feedback_labels'];out['candidate_fits']+=r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'];out['scoring_queries']+=r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'];out['raw_bin_visits']+=r['costs']['raw_bin_visits'];out['main_predictions']+=3*len(r['predictions']);out['grid_predictions']+=32*len(r['evaluations'])
    close(saved,out);assert out['generated_labels']==153600 and out['used_labels']==1843200
    for k,v in dict(candidate_fits=300000,scoring_queries=20000000,raw_bin_visits=100000000,grid_predictions=250000).items():assert out[k]<=v

def main():
    out=ROOT/'results/selective-steering-v1';start=time.monotonic()
    def timeout(*_):raise TimeoutError('033 audit 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());m=json.loads((out/'manifest.json').read_text());close(data['hashes'],m)
        for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(ws)==len(worlds)==15 and set(ws)==set(itertools.product(range(2200,2205),HISTORIES))
        for w in worlds:assert not w['small'];verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
        assert len(rs)==180 and {(r['seed'],r['history'],r['proposal_seed'],r['policy']) for r in rs}==set(itertools.product(range(2200,2205),HISTORIES,(2200,2201),POLICIES))
        for i,r in enumerate(rs,1):
            verify_run(r,ws[r['seed'],r['history']])
            if i%12==0:print(f'{i}/180 independently reconstructed',flush=True)
        parity=verify_parity(rs);verify_summary(rs,data['summary']);verify_totals(rs,worlds,data['totals']);assert data['elapsed_seconds']<=900
        result=dict(status='pass',runs=180,parity=parity,empirical_pass=data['summary']['empirical_pass'],elapsed_seconds=time.monotonic()-start,**{n+'_sha256':hashlib.sha256((out/p).read_bytes()).hexdigest() for n,p in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    finally:signal.alarm(0)
if __name__=='__main__':main()
