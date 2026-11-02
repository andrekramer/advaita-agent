"""031 independent scripted-control and full learning replay."""
import copy,gzip,hashlib,itertools,json,math,signal,time
from pathlib import Path
from audit_nested_abstractions import close,logloss
from audit_protection_interfaces import canonical
import audit_memory_lifecycle as life
from memory_revision_reference import RevisionReference
ROOT=Path(__file__).resolve().parents[1]
WINDOWS={'whole':(1,2048),'early':(513,576),'benefit':(577,1024),'returning':(1025,1536),'later':(1537,2048)}
POLICIES=('unsteered','targeted','rotated');BRANCHES=('stable','repeated')

def selection(review):
    candidates=[]
    for e in review['weakenings']:
        if e['qualifies'] and not e['accepted']:candidates.append((e['losses'][0]-e['losses'][1],-e['channel']))
    return -max(candidates)[1] if candidates else None

def intervention(ref,t,j):
    before=hashlib.sha256(canonical(ref.state()).encode()).hexdigest();mass=sum(v[1] for v in ref.slow[j])
    for cell in ref.slow[j]:cell[0]*=.5;cell[1]*=.5
    ref.pending[j]=None;ref.revision_pending[j]=None;ref.refresh()
    return dict(operation='weaken_slow',tick=t,channel=j,review_tick=t,reason='Scripted review diagnostic: weaken selected slow evidence once',removed_mass=mass*.5,
        before_sha256=before,after_sha256=hashlib.sha256(canonical(ref.state()).encode()).hexdigest())

def verify_run(r,w,c,measure=True):
    life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=RevisionReference(r['acquisition_checkpoint'],'combined');close(r['transfer'],life.expected_eval(ref.locals,ref.upper,w,0,True))
    trigger=event=None;pos=0
    for t,row in enumerate(w['main'],1):
        close(r['predictions'][t-1],ref.observe(t,row))
        if str(t) in w['selection']:
            review=r['reviews'][pos];ref.review(t,w['selection'][str(t)],review);pos+=1
            if trigger is None and t<=1024:
                j=selection(review)
                if j is not None:
                    trigger=dict(tick=t,channel=j)
                    if r['policy']!='unsteered':event=intervention(ref,t,j if r['policy']=='targeted' else (j+1)%3)
        if t%w['period']==0:close(r['evaluations'][t//w['period']-1],life.expected_eval(ref.locals,ref.upper,w,t))
    close(r['trigger'],trigger);close(r['control'],event);close(c,ref.state())
    assert hashlib.sha256(canonical(c).encode()).hexdigest()==r['checkpoint_sha256']
    close(r['runtime_checkpoint'],dict(schema=29,memory='combined',tick=len(w['main']),active=len(w['main']),last_labelled=True,
        review_ticks=[int(t) for t in w['selection']],last_review=r['reviews'][-1],controls=[] if event is None else [event],engine=c))
    costs=ref.costs.copy();costs['feedback_labels']=r['acquisition']['costs']['feedback_labels']+3*len(w['main'])+3*sum(map(len,w['selection'].values()));close(r['costs'],costs)
    if measure:verify_metrics(r,w)

def verify_metrics(r,w):
    values={'observed':[],'latent':[],'unaffected':[]};j=1-w['affected']
    for t,row in enumerate(w['main'],1):
        ps=r['predictions'][t-1];y=life.truth(w,row['x'],row['a'],t)
        values['observed'].append((t,logloss(ps[2],row['y'])));values['latent'].append((t,.9*logloss(ps[2],y)+.1*logloss(ps[2],1-y)))
        values['unaffected'].append((t,logloss(ps[j],row['local'][j])))
    out={}
    for n,seq in values.items():
        out[n]={}
        for k,(lo,hi) in WINDOWS.items():
            xs=[v for t,v in seq if lo<=t<=hi];out[n][k]=sum(xs)/len(xs)
    e=r['evaluations'][-1];out.update(final_valid=all(e['local_exact']) and e['accuracy']==1 and e['regret']<=.10,trigger=r['trigger'],controlled=r['control'] is not None)
    close(r['metrics'],out)

def verify_summary(runs,saved):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});assert len(pairs)==10
    get={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r['metrics'] for r in runs};groups=[]
    for h,p in itertools.product(BRANCHES,POLICIES):
        ms=[get[s,q,h,p] for s,q in pairs];g=dict(branch=h,policy=p,final_valid=sum(m['final_valid'] for m in ms),triggers=sum(m['trigger'] is not None for m in ms),controls=sum(m['controlled'] for m in ms))
        for n in ('observed','latent','unaffected'):g[n]={k:sum(m[n][k] for m in ms)/10 for k in WINDOWS}
        groups.append(g)
    close(saved['groups'],groups);paired=[]
    for c in ('unsteered','rotated'):
        for s,q in pairs:
            for h in BRANCHES:
                a,b=get[s,q,h,'targeted'],get[s,q,h,c];r=dict(seed=s,proposal_seed=q,branch=h,control=c)
                for n in ('observed','latent','unaffected'):r[n+'_cost']={k:a[n][k]-b[n][k] for k in WINDOWS}
                paired.append(r)
    close(saved['paired'],paired)
    gains=[dict(seed=s,proposal_seed=q,gain=get[s,q,'repeated','unsteered']['observed']['benefit']-get[s,q,'repeated','targeted']['observed']['benefit']) for s,q in pairs]
    specific=[get[s,q,'repeated','rotated']['observed']['benefit']-get[s,q,'repeated','targeted']['observed']['benefit'] for s,q in pairs]
    close(saved['gains'],gains);close(saved['specificity_gains'],specific)
    gates=dict(benefit=sum(r['gain'] for r in gains)/10>=.01,benefit_pairs=sum(r['gain']>0 for r in gains)>=8,
        specificity=sum(specific)/10>=.01,specificity_pairs=sum(v>0 for v in specific)>=8,
        final_validity=all(sum(get[s,q,h,'targeted']['final_valid'] for s,q in pairs)>=8 for h in BRANCHES),
        cost_mean=True,cost_worst=True,unaffected_mean=True,unaffected_worst=True)
    for h,k in [('stable','whole'),('repeated','early'),('repeated','returning'),('repeated','later')]:
        for n in ('observed','latent'):
            xs=[get[s,q,h,'targeted'][n][k]-get[s,q,h,'unsteered'][n][k] for s,q in pairs]
            if sum(xs)/10>.02:gates['cost_mean']=False
            if n=='observed' and max(xs)>.10:gates['cost_worst']=False
    for h in BRANCHES:
        xs=[get[s,q,h,'targeted']['unaffected']['whole']-get[s,q,h,'unsteered']['unaffected']['whole'] for s,q in pairs]
        if sum(xs)/10>.02:gates['unaffected_mean']=False
        if max(xs)>.10:gates['unaffected_worst']=False
    close(saved['gates'],gates);assert saved['primary_pass']==all(gates.values())
    close(saved['environment_means'],[dict(seed=s,gain=sum(r['gain'] for r in gains if r['seed']==s)/2) for s in sorted({s for s,q in pairs})])

def totals(runs,worlds):
    # No imported experiment budget arithmetic.
    out=dict(runs=len(runs),generated_labels=0,used_labels=0,candidate_fits=0,scoring_queries=0,raw_bin_visits=0,main_predictions=0,evaluation_predictions=0,auxiliary_predictions=0,oracle_context_queries=0)
    for w in worlds:out['generated_labels']+=sum(len(x) for x in w['local_main'])+sum(len(x) for b in w['local_selection'] for x in b)+len(w['composition'])+3*len(w['main'])+3*sum(len(x) for x in w['selection'].values())
    for r in runs:
        c=r['costs'];a=r['acquisition']['costs'];out['used_labels']+=c['feedback_labels'];out['candidate_fits']+=c['candidate_fits']+a['candidate_fits'];out['scoring_queries']+=c['scoring_queries']+a['scoring_queries'];out['raw_bin_visits']+=c['raw_bin_visits'];out['main_predictions']+=3*len(r['predictions']);out['auxiliary_predictions']+=24
        for e in [r['transfer']]+r['evaluations']:out['evaluation_predictions']+=e['contexts']
        for e in [r['transfer'],r['acquisition']['transfer']]+r['evaluations']:out['oracle_context_queries']+=32*(1+len(e['removal_costs'])+len(e['raw_addition_gains']))
    return out

def main():
    out=ROOT/'results/memory-steering-v1';start=time.monotonic()
    def timeout(*_):raise TimeoutError('900 second steering audit ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text());assert data['hashes']==manifest
        for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==10 and set(ws)==set(itertools.product(range(2000,2005),BRANCHES))
        for w in worlds:assert not w['small'];life.verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
        assert len(runs)==60 and {(r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs}==set(itertools.product(range(2000,2005),(2000,2001),BRANCHES,POLICIES))
        for i,r in enumerate(runs,1):
            with gzip.open(out/r['checkpoint_file'],'rt') as f:c=json.load(f)
            verify_run(r,ws[r['seed'],r['branch']],c)
            if i%10==0:print(f'{i}/60 independently reconstructed',flush=True)
        verify_summary(runs,data['summary']);total=totals(runs,worlds);close(total,data['totals'])
        for k,v in dict(generated_labels=102400,used_labels=614400,main_predictions=368640,evaluation_predictions=62880,auxiliary_predictions=1440).items():assert total[k]==v
        for k,v in dict(candidate_fits=150000,scoring_queries=10000000,raw_bin_visits=40000000,oracle_context_queries=330000).items():assert total[k]<=v
        assert data['elapsed_seconds']<900
        result=dict(status='pass',runs=60,primary_pass=data['summary']['primary_pass'],elapsed_seconds=time.monotonic()-start,
            **{n+'_sha256':hashlib.sha256((out/f).read_bytes()).hexdigest() for n,f in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    finally:signal.alarm(0)
if __name__=='__main__':main()
