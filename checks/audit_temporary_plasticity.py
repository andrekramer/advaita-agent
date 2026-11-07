"""035 independent world/controller/state/measurement reconstruction.

Does not import study-035 learner, runner or metrics.
"""
import copy,gzip,hashlib,itertools,json,math,signal,time,types
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close,logloss
from audit_protection_interfaces import canonical
from audit_coordinated_steering import CoordinatedReference
import audit_selective_steering as old
from memory_control_reference import lp,up,local_fit,upper_fit
ROOT=Path(__file__).resolve().parents[1]
HISTORIES=('stable','forms','repeated','forms_persistent','repeated_persistent')
POLICIES=('P','D128','D256','D512','G')
WINDOWS={'active':(513,1024),'burst':(513,640),'settled':(641,1024),'early_return':(1025,1280),'returning':(1025,1536),'later':(1537,2048)}

def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()

def forms(w,t,observed=False):
    f=copy.deepcopy(w['forms']);h=w['branch'];j=w['affected'];phase=(max(t,1)-1)//512
    changed=(t>512) if h.endswith('_persistent') else bool(phase%2)
    if changed and h.startswith('forms'):f[j]=list(w['alternative'])
    if changed and observed and h.startswith('repeated'):f[j]=[1-v for v in f[j]]
    return f

def truth(w,x,a,t):
    f=forms(w,t,True);return (f[0][x[0]]+f[1][x[1]]+a)%2

ref_life=types.SimpleNamespace(CONTEXTS=old.life.CONTEXTS,forms=forms,truth=truth)
evaluation=types.FunctionType(old.evaluation.__code__,dict(old.evaluation.__globals__,life=ref_life))

def verify_world(w):
    original=copy.deepcopy(w)
    if w['branch'].endswith('_persistent'):
        original['branch']=w['branch'].split('_')[0]
        # Only the original-return phase differs; preserve every old noise bit.
        for t,rows in [(t,[r]) for t,r in enumerate(original['main'],1)]+[(int(t),rows) for t,rows in original['selection'].items()]:
            if 1025<=t<=1536:
                q=w['affected'];original_form=w['forms'][q]
                changed=w['alternative'] if w['branch'].startswith('forms') else [1-v for v in original_form]
                for row in rows:
                    difference=(original_form[row['x'][q]]+changed[row['x'][q]])%2
                    row['local'][q]=(row['local'][q]+difference)%2
                    row['y']=(row['y']+difference)%2
    old.verify_world(original)


def verify_run(r,w,measured=True):
    old.life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=CoordinatedReference(r['acquisition_checkpoint']);p=1-w['affected'];policy=r['policy'];pos=0;controls=[];diagnostics=[];restores=[];extra=0
    s=dict(policy=policy,protected=p,opening=512,ceiling=1024,streak=0,last_loss=None,closed_at=None,closure_reason=None,last_review=None)
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(ref.slow[j]) for j,h in enumerate(ref.half_lives) if h==128)
        close(r['predictions'][t-1],ref.observe(t,row))
        if str(t) in w['selection']:
            batch=w['selection'][str(t)];d=None
            if 512<t<=1024:
                ps=[up(ref.upper,ref.locals,x['x'],x['a']) for x in batch]
                loss=sum(logloss(pred,x['y']) for pred,x in zip(ps,batch))/len(batch)
                d=dict(tick=t,predictions=ps,loss=loss,model_sha256=sha(dict(locals=ref.locals,upper=ref.upper)),batch_sha256=sha(batch),before_sha256=sha(ref.state()),previous_loss=s['last_loss'],previous_streak=s['streak'])
            ref.review(t,batch,r['reviews'][pos]);reason=None;event=None
            if t==512:event=ref.configure([p],[] if policy=='P' else [2],'035 supplied opening: protect local form')
            elif 512<t<=1024:
                if s['closed_at'] is None and policy=='G':
                    s['streak']=s['streak']+1 if d['loss']<=.55 else 0;s['last_loss']=d['loss']
                    if s['streak']==2:reason='adequate'
                if s['closed_at'] is None and policy in ('D128','D256','D512') and t>=dict(D128=640,D256=768,D512=1024)[policy]:reason='fixed'
                if t==1024:
                    if s['closed_at'] is None and policy!='P':reason='ceiling'
                    event=ref.configure([],[],'035 ceiling: release lock and ordinary rates')
                elif reason:event=ref.configure([p],[],'035 close boost: '+reason)
                if reason and s['closed_at'] is None:s['closed_at']=t;s['closure_reason']=reason
            s['last_review']=t
            if event:controls.append(copy.deepcopy(event))
            if d:
                d.update(streak=s['streak'],closed_at=s['closed_at'],closure_reason=s['closure_reason'],half_lives=list(ref.half_lives),after_sha256=sha(ref.state()));diagnostics.append(d)
            close(r['inspections'][pos],ref.inspect());close(r['evaluations'][pos],evaluation(ref,w,t))
            local=[local_fit(m['partition'],ref.total(j)) for j,m in enumerate(ref.locals)];close(local,ref.locals);close(upper_fit(ref.upper['spec'],ref.total(2),local),ref.upper);pos+=1
        if t in (576,768):restores.append(dict(tick=t,sha256=sha(dict(schema=35,learner=ref.state(),controller=s))))
    assert len(r['predictions'])==len(w['main']) and pos==len(r['reviews'])==len(r['inspections'])==len(r['evaluations'])
    close(r['checkpoint'],dict(schema=35,learner=ref.state(),controller=s));close(r['costs'],ref.costs);close(r['controls'],controls);close(r['diagnostics'],diagnostics);close(r['restore_checks'],restores)
    assert r['extra_decay_cell_visits']==extra and r['controller_queries']==sum(len(d['predictions']) for d in diagnostics)
    assert r['feedback_labels']==r['acquisition']['costs']['feedback_labels']+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    assert not ref.locked and ref.half_lives==[1024]*3
    if measured:verify_metrics(r,w)


def verify_metrics(r,w):
    values={'observed':[],'expected':[]}
    for t,(row,ps) in enumerate(zip(w['main'],r['predictions']),1):
        f=forms(w,t,True);ys=[f[j][row['x'][j]] for j in (0,1)]+[truth(w,row['x'],row['a'],t)]
        values['observed'].append([logloss(p,y) for p,y in zip(ps,row['local']+[row['y']])])
        values['expected'].append([.9*logloss(p,y)+.1*logloss(p,1-y) for p,y in zip(ps,ys)])
    m={kind:{k:[sum(x[j] for x in vals[lo-1:hi])/(hi-lo+1) for j in range(3)] for k,(lo,hi) in WINDOWS.items()} for kind,vals in values.items()}
    p=1-w['affected'];es=[e for e in r['evaluations'] if 513<=e['tick']<=640];last=r['evaluations'][-1];s=r['checkpoint']['controller']
    m.update(protected=p,burst_correct=sum(e['local_exact'][p] for e in es)/len(es),final_valid=last['valid'],final_local_exact=last['local_exact'],final_spec=last['spec'],closed_at=s['closed_at'],closure_reason=s['closure_reason'],duration=(s['closed_at']-512) if s['closed_at'] is not None else 0)
    close(r['metrics'],m)


def verify_candidate(rs,policy,saved):
    keys=sorted({(r['seed'],r['proposal_seed']) for r in rs});table={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r['metrics'] for r in rs}
    paired=[];guards=[];adaptation=[]
    for h in HISTORIES:
        def cost(control,window,j):return [table[s,q,h,policy]['expected'][window][j]-table[s,q,h,control]['expected'][window][j] for s,q in keys]
        for s,q in keys:
            target=table[s,q,h,policy];paired.append(dict(seed=s,proposal_seed=q,history=h,active_gain_P=table[s,q,h,'P']['expected']['active'][2]-target['expected']['active'][2],early_gain_D512=table[s,q,h,'D512']['expected']['early_return'][2]-target['expected']['early_return'][2]))
        for control in ('P','D512'):
            windows=['returning','later']
            if h=='stable':windows.append('active')
            if control=='P' and h in ('forms','repeated'):windows.append('early_return')
            for window in windows:
                for j in range(3):
                    xs=cost(control,window,j);avg=sum(xs)/len(xs)
                    guards.append(dict(history=h,control=control,window=window,channel=j,mean_cost=avg,max_cost=max(xs),passed=avg<=.02 and all(x<=.10 for x in xs)))
        if h!='stable':
            xs=cost('D512','active',2);avg=sum(xs)/len(xs);adaptation.append(dict(history=h,mean_cost=avg,max_cost=max(xs),passed=avg<=.02 and all(x<=.10 for x in xs)))
    changed=[p for p in paired if p['history']!='stable'];returned=[p for p in paired if p['history'] in ('forms','repeated')]
    active=mean(p['active_gain_P'] for p in changed);early=mean(p['early_gain_D512'] for p in returned)
    gates=dict(adaptation_preserved=all(x['passed'] for x in adaptation),active_gain=active>=.02,active_consistency=sum(p['active_gain_P']>1e-12 for p in changed)>=28,early_gain=early>=.02,early_consistency=sum(p['early_gain_D512']>1e-12 for p in returned)>=14,each_return_improves=all(mean(p['early_gain_D512'] for p in returned if p['history']==h)>1e-12 for h in ('forms','repeated')),preservation=all(x['passed'] for x in guards),protection=all(mean(table[s,q,h,policy]['burst_correct'] for s,q in keys)>=.95 for h in HISTORIES[1:]),final_validity=all(sum(table[s,q,h,policy]['final_valid'] for s,q in keys)>=8 for h in HISTORIES))
    expected=dict(policy=policy,gates=gates,empirical_pass=all(gates.values()),adaptation_guards=adaptation,preservation_guards=guards,paired=paired,active_mean_gain=active,active_positive=sum(p['active_gain_P']>1e-12 for p in changed),early_mean_gain=early,early_positive=sum(p['early_gain_D512']>1e-12 for p in returned),environment_means=[dict(seed=s,active_gain=mean(p['active_gain_P'] for p in changed if p['seed']==s),early_gain=mean(p['early_gain_D512'] for p in returned if p['seed']==s)) for s in sorted({p['seed'] for p in changed})])
    close(saved,expected)


def verify_summary(rs,s):
    verify_candidate(rs,'G',s['primary'])
    for p in ('D128','D256'):verify_candidate(rs,p,s['secondary'][p])
    groups=[]
    for h,p in itertools.product(HISTORIES,POLICIES):
        ms=[r['metrics'] for r in rs if r['history']==h and r['policy']==p]
        g=dict(history=h,policy=p,burst_correct=mean(m['burst_correct'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),final_raw_interface=sum(any(x==2 for x in m['final_spec']) for m in ms),mean_duration=mean(m['duration'] for m in ms),closure_counts={('null' if reason is None else reason):sum(m['closure_reason']==reason for m in ms) for reason in (None,'fixed','adequate','ceiling')})
        for typ in ('expected','observed'):g[typ]={k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS}
        groups.append(g)
    # JSON serializes None dictionary keys as the string 'null'.
    close(json.loads(canonical(s['groups'])),json.loads(canonical(groups)))
    direct=[];lookup={(g['history'],g['policy']):g for g in groups}
    for h,p in itertools.product(HISTORIES,('D128','D256')):
        direct.append(dict(history=h,control=p,gain={k:lookup[h,p]['expected'][k][2]-lookup[h,'G']['expected'][k][2] for k in WINDOWS}))
    close(s['G_vs_fixed'],direct)


def verify_totals(rs,ws,saved):
    out=dict(runs=len(rs),generated_labels=0,used_labels=0,candidate_fits=0,scoring_queries=0,raw_bin_visits=0,main_predictions=0,grid_predictions=0,extra_decay_cell_visits=0,controller_queries=0)
    for w in ws:out['generated_labels']+=sum(len(xs) for xs in w['local_main'])+sum(len(xs) for batch in w['local_selection'] for xs in batch)+len(w['composition'])+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    for r in rs:
        out['used_labels']+=r['feedback_labels'];out['candidate_fits']+=r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'];out['scoring_queries']+=r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'];out['raw_bin_visits']+=r['costs']['raw_bin_visits'];out['main_predictions']+=3*len(r['predictions']);out['grid_predictions']+=32*len(r['evaluations'])
        for k in ('extra_decay_cell_visits','controller_queries'):out[k]+=r[k]
    close(saved,out);assert out['generated_labels']==256000 and out['used_labels']==2560000 and out['controller_queries']==64000
    for k,v in dict(candidate_fits=400000,scoring_queries=25000000,raw_bin_visits=130000000,grid_predictions=300000).items():assert out[k]<=v


def main():
    out=ROOT/'results/temporary-plasticity-v1';start=time.monotonic()
    def timeout(*_):raise TimeoutError('035 audit 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());m=json.loads((out/'manifest.json').read_text());close(data['hashes'],m)
        for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(ws)==len(worlds)==25 and set(ws)==set(itertools.product(range(2400,2405),HISTORIES))
        for w in worlds:assert not w['small'];verify_world(w)
        for seed in range(2400,2405):
            for h in ('forms','repeated'):
                a,b=ws[seed,h],ws[seed,h+'_persistent'];assert a['main'][:1024]==b['main'][:1024]
                assert all(a['selection'][str(t)]==b['selection'][str(t)] for t in range(64,1025,64))
        with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
        assert len(rs)==250 and {(r['seed'],r['history'],r['proposal_seed'],r['policy']) for r in rs}==set(itertools.product(range(2400,2405),HISTORIES,(2400,2401),POLICIES))
        for i,r in enumerate(rs,1):
            verify_run(r,ws[r['seed'],r['history']])
            if i%10==0:print(f'{i}/250 independently reconstructed',flush=True)
        verify_summary(rs,data['summary']);verify_totals(rs,worlds,data['totals']);assert data['elapsed_seconds']<900
        result=dict(status='pass',runs=250,empirical_pass=data['summary']['primary']['empirical_pass'],elapsed_seconds=time.monotonic()-start,**{n+'_sha256':hashlib.sha256((out/p).read_bytes()).hexdigest() for n,p in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    finally:signal.alarm(0)
if __name__=='__main__':main()
