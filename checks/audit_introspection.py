"""032 independent state replay, policy derivation and outcome audit.

No experiment, controller, runtime or new measurement implementation imports.
"""
import copy,gzip,hashlib,itertools,json,math,signal,time
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close,logloss
from audit_protection_interfaces import canonical
import audit_memory_lifecycle as life
from memory_revision_reference import RevisionReference
from memory_control_reference import lp,up
ROOT=Path(__file__).resolve().parents[1]
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))

def control(ref,j):
    before=hashlib.sha256(canonical(ref.state()).encode()).hexdigest();mass=ref.mass()['slow'][j]
    for cell in ref.slow[j]:
        for k in (0,1):cell[k]/=2
    ref.pending[j]=None;ref.revision_pending[j]=None;ref.refresh()
    return dict(operation='weaken_slow',tick=ref.tick,channel=j,review_tick=ref.tick,
        reason='032 diagnostic counterfactual: one slow-evidence weakening',removed_mass=mass/2,
        before_sha256=before,after_sha256=hashlib.sha256(canonical(ref.state()).encode()).hexdigest())

def outer(ref,reviews,event=None):
    return dict(schema=29,memory='combined',tick=ref.tick,active=ref.tick,last_labelled=True,
        review_ticks=ref.selection_ids,last_review=reviews[-1],controls=[] if event is None else [event],engine=ref.state())

def decision(view):
    eligible=[];rank=[]
    for e in view['observed']['last_review']['weakenings']:
        if e['qualifies'] and not e['accepted']:
            eligible.append(e['channel']);rank.append((e['losses'][0]-e['losses'][1],-e['channel']))
    selected=-sorted(rank)[-1][1] if rank else None
    forecasts=[]
    for j in range(3):
        forecasts.append(dict(channel=j,immediate=('change' if j==2 else 'no_change') if j in eligible else 'uncertain',future=('improvement' if j==2 else 'no_effect') if j in eligible else 'uncertain',disagreement_future='improvement' if j in eligible else 'uncertain',own_future='improvement' if j in eligible else 'uncertain'))
    return dict(target_output=2,eligible=eligible,choices=dict(no_op=None,disagreement=selected,aware=2 if 2 in eligible else None,rotated=None if selected is None else (selected+1)%3),forecasts=forecasts)

def verify_record(r,w,measured=True):
    life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=RevisionReference(r['acquisition_checkpoint'],'combined');reviews=[];pos=0
    for t,row in enumerate(w['main'][:r['tick']],1):
        close(r['prefix_predictions'][t-1],ref.observe(t,row))
        if str(t) in w['selection']:
            rev=r['prefix_reviews'][pos];pos+=1;ref.review(t,w['selection'][str(t)],rev);reviews.append(rev)
            eligible=any(e['qualifies'] and not e['accepted'] for e in rev['weakenings'])
            if t<r['tick']:assert not eligible
    assert len(r['prefix_predictions'])==r['tick'] and pos==len(r['prefix_reviews'])
    assert eligible or r['tick']==(16 if w['small'] else 1024)
    assert r['tick']<=(16 if w['small'] else 1024)
    close(r['checkpoint'],outer(ref,reviews))
    observed=dict(memory='combined',tick=ref.tick,active=ref.tick,locals=ref.locals,upper=ref.upper,evidence_mass=ref.mass(),last_review=reviews[-1],controls=[],costs=ref.costs,pending=ref.pending,revision_pending=ref.revision_pending)
    view=dict(observed=observed,inferred=dict(upper_ports=[{0:'absent',1:'group_membership',2:'raw_state'}[s] for s in ref.upper['spec']],upper_consumes_local_confidence=False,review_losses_are_pre_final_migration=True))
    close(r['packet'],view);close(r['decision'],decision(view))
    assert r['decision_sha256']==hashlib.sha256(canonical(dict(packet=r['packet'],decision=r['decision'])).encode()).hexdigest()
    assert set(r['branches'])=={'none','0','1','2'}
    for name,b in r['branches'].items():
        fork=copy.deepcopy(ref);event=None if name=='none' else control(fork,int(name));close(b['control'],event)
        grid=[[lp(fork.locals[0],x),lp(fork.locals[1],y),up(fork.upper,fork.locals,[x,y],a)] for x,y,a in CONTEXTS];close(b['immediate'],grid)
        pos=0
        for t,row in enumerate(w['main'][r['tick']:],r['tick']+1):
            close(b['predictions'][t-r['tick']-1],fork.observe(t,row))
            if str(t) in w['selection']:
                rev=b['reviews'][pos];pos+=1;fork.review(t,w['selection'][str(t)],rev)
        assert len(b['predictions'])==len(w['main'])-r['tick'] and pos==len(b['reviews'])
        close(b['checkpoint'],outer(fork,reviews+b['reviews'],event))
        close(b['evaluation'],life.expected_eval(fork.locals,fork.upper,w,len(w['main'])))
    if measured:verify_metrics(r,w)

def category(g):return 'no_effect' if -.005<=g<=.005 else ('improvement' if g>0 else 'harm')

def verify_metrics(r,w):
    tick=r['tick'];windows={'future':(tick+1,tick+256),'remaining':(tick+1,2048),'returning':(1025,1536),'later':(1537,2048)};branches={}
    for name,b in r['branches'].items():
        values={}
        for key,(lo,hi) in windows.items():
            losses=[[],[],[]];expected=[]
            for t in range(max(tick+1,lo),min(len(w['main']),hi)+1):
                row=w['main'][t-1];ps=b['predictions'][t-tick-1]
                for j,y in enumerate(row['local']+[row['y']]):losses[j].append(logloss(ps[j],y))
                y=life.truth(w,row['x'],row['a'],t);expected.append(.9*logloss(ps[2],y)+.1*logloss(ps[2],1-y))
            values[key]=dict(observed=[sum(xs)/len(xs) for xs in losses],latent=sum(expected)/len(expected))
        e=b['evaluation'];values['valid']=all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10;branches[name]=values
    forecasts=[]
    for j in range(3):
        a=branches[str(j)]['future']['observed'];b=branches['none']['future']['observed'];delta=max(abs(x[2]-y[2]) for x,y in zip(r['branches'][str(j)]['immediate'],r['branches']['none']['immediate']))
        forecasts.append(dict(channel=j,eligible=j in r['decision']['eligible'],gain=b[2]-a[2],own_gain=b[j]-a[j],actual=category(b[2]-a[2]),own_actual=category(b[j]-a[j]),immediate_delta=delta,immediate_actual='no_change' if delta<=1e-12 else 'change'))
    close(r['metrics'],dict(branches=branches,forecasts=forecasts))

def verify_summary(records,saved):
    pairs=[];fs=[];groups=[]
    for r in records:
        choices=r['decision']['choices'];ms=r['metrics']['branches'];get=lambda p:ms['none' if choices[p] is None else str(choices[p])]
        a=get('aware');n=get('no_op');d=get('disagreement');rot=get('rotated')
        pairs.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],history=r['history'],choices=choices,gain_vs_disagreement=d['future']['observed'][2]-a['future']['observed'][2],gain_vs_none=n['future']['observed'][2]-a['future']['observed'][2],gain_vs_rotated=rot['future']['observed'][2]-a['future']['observed'][2],valid=a['valid'],costs={k:dict(observed=[a[k]['observed'][j]-n[k]['observed'][j] for j in range(3)],latent=a[k]['latent']-n[k]['latent']) for k in ('remaining','returning','later')}))
        for f,actual in zip(r['decision']['forecasts'],r['metrics']['forecasts']):
            if actual['eligible']:fs.append(dict(seed=r['seed'],history=r['history'],proposal_seed=r['proposal_seed'],**actual,correct=f['future']==actual['actual'],naive_correct=f['disagreement_future']==actual['actual'],own_correct=f['own_future']==actual['own_actual'],immediate_correct=f['immediate']==actual['immediate_actual']))
    close(saved['paired'],pairs);close(saved['forecasts'],fs)
    for h in ('stable','repeated','forms'):
        rs=[r for r in records if r['history']==h]
        for p in ('no_op','disagreement','aware','rotated'):
            choices=[r['decision']['choices'][p] for r in rs];ms=[r['metrics']['branches']['none' if j is None else str(j)] for r,j in zip(rs,choices)]
            groups.append(dict(history=h,policy=p,actions=sum(j is not None for j in choices),valid=sum(m['valid'] for m in ms),**{k:dict(observed=[mean(m[k]['observed'][j] for m in ms) for j in range(3)],latent=mean(m[k]['latent'] for m in ms)) for k in ('future','remaining','returning','later')}))
    close(saved['groups'],groups);changing=[p for p in pairs if p['history']!='stable'];forecast=[f for f in fs if f['history']!='stable']
    avg=lambda xs:sum(xs)/len(xs) if xs else None
    acc=avg([f['correct'] for f in forecast]);naive=avg([f['naive_correct'] for f in forecast])
    gates=dict(mechanical=all(f['immediate_correct'] for f in fs),forecast_coverage=len(forecast)>=8 and len({f['seed'] for f in forecast})>=3,forecast_accuracy=acc is not None and acc>=.8,forecast_advantage=acc is not None and acc-naive>=.2,steering_gain=mean(p['gain_vs_disagreement'] for p in changing)>=.005,steering_consistency=sum(p['gain_vs_disagreement']>0 for p in changing)>=12,steering_vs_none=mean(p['gain_vs_none'] for p in changing)>=0,preservation=True,final_validity=all(g['valid']>=8 for g in groups if g['policy']=='aware'))
    for h in ('stable','repeated','forms'):
        rs=[p for p in pairs if p['history']==h]
        for k in ('returning','later'):
            for j in range(3):
                costs=[p['costs'][k]['observed'][j] for p in rs]
                if mean(costs)>.02 or max(costs)>.1:gates['preservation']=False
            if mean(p['costs'][k]['latent'] for p in rs)>.02:gates['preservation']=False
    close(saved['gates'],gates);assert saved['primary_pass']==all(gates.values())
    assert saved['forecast_pass']==all(gates[k] for k in ('forecast_coverage','forecast_accuracy','forecast_advantage'))
    assert saved['steering_pass']==all(gates[k] for k in ('steering_gain','steering_consistency','steering_vs_none','preservation','final_validity'))
    close(saved['eligible'],len(fs));close(saved['eligible_changing'],len(forecast));close(saved['forecast_accuracy'],acc);close(saved['naive_accuracy'],naive);close(saved['own_accuracy'],avg([f['own_correct'] for f in forecast]))
    close(saved['environment_means'],[dict(seed=s,gain=mean(p['gain_vs_disagreement'] for p in changing if p['seed']==s)) for s in sorted({p['seed'] for p in changing})])

def verify_totals(records,worlds,saved):
    get={(w['seed'],w['branch']):w for w in worlds};labels=0;fits=scores=visits=preds=oracle=0
    generated=0
    for w in worlds:generated+=sum(len(xs) for xs in w['local_main'])+sum(len(xs) for batch in w['local_selection'] for xs in batch)+len(w['composition'])+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    for r in records:
        w=get[r['seed'],r['history']];t=r['tick'];p=r['checkpoint']['engine']['costs'];ac=r['acquisition']['costs']
        labels+=ac['feedback_labels']+3*t+3*sum(len(xs) for tick,xs in w['selection'].items() if int(tick)<=t)
        labels+=4*3*(len(w['main'])-t+sum(len(xs) for tick,xs in w['selection'].items() if int(tick)>t))
        fits+=ac['candidate_fits']+p['candidate_fits'];scores+=ac['scoring_queries']+p['scoring_queries'];visits+=p['raw_bin_visits'];preds+=3*t
        es=[r['acquisition']['transfer']]
        for b in r['branches'].values():
            c=b['checkpoint']['engine']['costs'];fits+=c['candidate_fits']-p['candidate_fits'];scores+=c['scoring_queries']-p['scoring_queries'];visits+=c['raw_bin_visits']-p['raw_bin_visits'];preds+=3*(len(w['main'])-t);es.append(b['evaluation'])
        oracle+=sum(32*(1+len(e['removal_costs'])+len(e['raw_addition_gains'])) for e in es)
    close(saved,dict(trunks=len(records),continuations=4*len(records),generated_labels=generated,used_labels=labels,candidate_fits=fits,scoring_queries=scores,raw_bin_visits=visits,main_predictions=preds,immediate_predictions=384*len(records),final_grid_predictions=128*len(records),auxiliary_predictions=24*len(records),oracle_context_queries=oracle))
    assert generated==153600
    for k,v in dict(used_labels=1228800,candidate_fits=200000,scoring_queries=15000000,raw_bin_visits=60000000,oracle_context_queries=50000).items():assert saved[k]<=v

def main():
    out=ROOT/'results/introspection-v1';start=time.monotonic()
    def timeout(*_):raise TimeoutError('032 audit 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text());close(data['hashes'],manifest)
        for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds};assert len(ws)==len(worlds)==15
        assert set(ws)==set(itertools.product(range(2100,2105),('stable','repeated','forms')))
        for w in worlds:assert not w['small'];life.verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:records=[json.loads(line) for line in f]
        assert len(records)==30 and {(r['seed'],r['history'],r['proposal_seed']) for r in records}==set(itertools.product(range(2100,2105),('stable','repeated','forms'),(2100,2101)))
        for i,r in enumerate(records,1):
            verify_record(r,ws[r['seed'],r['history']])
            if i%5==0:print(f'{i}/30 trunks and {i*4}/120 branches reconstructed',flush=True)
        verify_summary(records,data['summary']);verify_totals(records,worlds,data['totals']);assert data['elapsed_seconds']<900
        audit=dict(status='pass',trunks=30,continuations=120,primary_pass=data['summary']['primary_pass'],elapsed_seconds=time.monotonic()-start,**{n+'_sha256':hashlib.sha256((out/p).read_bytes()).hexdigest() for n,p in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(audit)
    finally:signal.alarm(0)
if __name__=='__main__':main()
