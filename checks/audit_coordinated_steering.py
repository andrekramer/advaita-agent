"""034 independent replay. No new runtime, runner or metrics imports."""
import copy,gzip,hashlib,itertools,json,signal,time
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close
from audit_protection_interfaces import canonical
import audit_selective_steering as old
from memory_control_reference import local_fit,upper_fit
ROOT=Path(__file__).resolve().parents[1]
HISTORIES=('stable','forms','repeated');POLICIES=('U','P','L','D','C')
WINDOWS=old.WINDOWS

class CoordinatedReference(old.SteeringReference):
    def state(self):
        state=super().state();state['schema']=34;return state


def verify_run(r,w,measured=True):
    old.life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=CoordinatedReference(r['acquisition_checkpoint']);n=w['phase_length'];p=1-w['affected'];q=1-p;pos=0;events=[];extra=0
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(ref.slow[j]) for j,h in enumerate(ref.half_lives) if h!=1024)
        close(r['predictions'][t-1],ref.observe(t,row))
        if str(t) in w['selection']:
            ref.review(t,w['selection'][str(t)],r['reviews'][pos])
            if r['policy']!='U' and t in (n,2*n):
                lock=[];plastic=[]
                if t==n:
                    lock=[p]
                    if r['policy'] in ('L','C'):plastic+=[q]
                    if r['policy'] in ('D','C'):plastic+=[2]
                reason='034 supplied instruction: protected local form with factorial plasticity' if t==n else '034 release: restore ordinary learning in all channels'
                events.append(copy.deepcopy(ref.configure(lock,plastic,reason)))
            close(r['inspections'][pos],ref.inspect());close(r['evaluations'][pos],old.evaluation(ref,w,t))
            local=[local_fit(m['partition'],ref.total(j)) for j,m in enumerate(ref.locals)];upper=upper_fit(ref.upper['spec'],ref.total(2),local);close(local,ref.locals);close(upper,ref.upper);pos+=1
        if t==3*n//2:close(r['restore_check'],dict(tick=t,sha256=hashlib.sha256(canonical(ref.state()).encode()).hexdigest()))
    assert len(r['predictions'])==len(w['main']) and pos==len(r['reviews'])==len(r['inspections'])==len(r['evaluations'])
    close(r['checkpoint'],ref.state());close(r['costs'],ref.costs);close(r['controls'],events);assert r['extra_decay_cell_visits']==extra
    assert not ref.locked and ref.half_lives==[1024]*3
    assert r['feedback_labels']==r['acquisition']['costs']['feedback_labels']+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    if measured:old.verify_metrics(r,w)


def verify_summary(rs,saved):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in rs});lookup={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r['metrics'] for r in rs};groups=[];paired=[]
    comparisons=[('C_vs_D','D','C'),('C_vs_L','L','C'),('C_vs_U','U','C'),('D_vs_P','P','D'),('L_vs_P','P','L'),('C_vs_P','P','C')]
    for h in HISTORIES:
        for policy in POLICIES:
            ms=[lookup[s,q,h,policy] for s,q in pairs]
            groups.append(dict(history=h,policy=policy,burst_correct=mean(m['burst_correct'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),final_local_correct=[sum(m['final_local_exact'][j] for m in ms) for j in (0,1)],final_raw_interface=sum(any(v==2 for v in m['final_spec']) for m in ms),**{typ:{k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS} for typ in ('expected','observed')}))
        for s,q in pairs:
            ms={p:lookup[s,q,h,p] for p in POLICIES};gains={key:ms[a]['expected']['active'][2]-ms[b]['expected']['active'][2] for key,a,b in comparisons};obs={key:ms[a]['observed']['active'][2]-ms[b]['observed']['active'][2] for key,a,b in comparisons}
            interaction=(ms['D']['expected']['active'][2]-ms['C']['expected']['active'][2])-(ms['P']['expected']['active'][2]-ms['L']['expected']['active'][2])
            paired.append(dict(seed=s,proposal_seed=q,history=h,gains=gains,observed_gains=obs,interaction=interaction,costs={p:{k:[ms['C']['expected'][k][j]-ms[p]['expected'][k][j] for j in range(3)] for k in WINDOWS} for p in ('U','D')}))
    close(saved['groups'],groups);close(saved['paired'],paired)
    changed=[p for p in paired if p['history']!='stable'];gd={(g['history'],g['policy']):g for g in groups}
    gates={'protection':all(gd[h,p]['burst_correct']>=.95 for h in ('forms','repeated') for p in ('P','L','D','C'))}
    for name in ('C_vs_D','C_vs_L','C_vs_U'):
        xs=[p['gains'][name] for p in changed];gates[name+'_mean']=sum(xs)/len(xs)>=.005;gates[name+'_consistency']=sum(x>1e-12 for x in xs)>=12
    guards=[]
    for h in HISTORIES:
        for control in ('U','D'):
            for window in ['returning','later']+(['active'] if h=='stable' else []):
                for j in range(3):
                    xs=[p['costs'][control][window][j] for p in paired if p['history']==h];m=sum(xs)/len(xs)
                    guards.append(dict(history=h,control=control,window=window,channel=j,mean_cost=m,max_cost=max(xs),passed=m<=.02 and all(x<=.10 for x in xs)))
            if h!='stable':
                xs=[p['costs'][control]['active'][2] for p in paired if p['history']==h];m=sum(xs)/len(xs);guards.append(dict(history=h,control=control,window='active',channel=2,mean_cost=m,max_cost=max(xs),passed=m<=.02))
    close(saved['guards'],guards);gates['preservation']=all(g['passed'] for g in guards);gates['final_validity']=all(gd[h,'C']['final_valid']>=8 for h in HISTORIES)
    close(saved['gates'],gates);assert saved['empirical_pass']==all(gates.values());assert saved['incremental_pass']==(gates['C_vs_D_mean'] and gates['C_vs_D_consistency'])
    xs=[p['interaction'] for p in changed];interaction=sum(xs)/len(xs);positive=sum(x>1e-12 for x in xs)
    close(saved['interaction_mean'],interaction);assert saved['interaction_positive']==positive;assert saved['interaction_pass']==(interaction>=.005 and positive>=12)
    close(saved['environment_means'],[dict(seed=s,**{key:mean(p['gains'][key] for p in changed if p['seed']==s) for key,a,b in comparisons},interaction=mean(p['interaction'] for p in changed if p['seed']==s)) for s in sorted({p['seed'] for p in changed})])


def verify_totals(rs,ws,saved):
    out=dict(runs=len(rs),generated_labels=0,used_labels=0,candidate_fits=0,scoring_queries=0,raw_bin_visits=0,main_predictions=0,grid_predictions=0,extra_decay_cell_visits=0)
    for w in ws:out['generated_labels']+=sum(len(xs) for xs in w['local_main'])+sum(len(xs) for batch in w['local_selection'] for xs in batch)+len(w['composition'])+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    for r in rs:
        out['used_labels']+=r['feedback_labels'];out['candidate_fits']+=r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'];out['scoring_queries']+=r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'];out['raw_bin_visits']+=r['costs']['raw_bin_visits'];out['main_predictions']+=3*len(r['predictions']);out['grid_predictions']+=32*len(r['evaluations']);out['extra_decay_cell_visits']+=r['extra_decay_cell_visits']
    close(saved,out);assert out['generated_labels']==153600 and out['used_labels']==1536000 and out['extra_decay_cell_visits']==1105920
    for k,v in dict(candidate_fits=250000,scoring_queries=18000000,raw_bin_visits=90000000,grid_predictions=200000).items():assert out[k]<=v


def main():
    out=ROOT/'results/coordinated-steering-v1';start=time.monotonic()
    def timeout(*_):raise TimeoutError('034 audit900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());m=json.loads((out/'manifest.json').read_text());close(data['hashes'],m)
        for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(ws)==len(worlds)==15 and set(ws)==set(itertools.product(range(2300,2305),HISTORIES))
        for w in worlds:assert not w['small'];old.verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
        assert len(rs)==150 and {(r['seed'],r['history'],r['proposal_seed'],r['policy']) for r in rs}==set(itertools.product(range(2300,2305),HISTORIES,(2300,2301),POLICIES))
        for i,r in enumerate(rs,1):
            verify_run(r,ws[r['seed'],r['history']])
            if i%10==0:print(f'{i}/150 independently reconstructed',flush=True)
        verify_summary(rs,data['summary']);verify_totals(rs,worlds,data['totals']);assert data['elapsed_seconds']<900
        result=dict(status='pass',runs=150,empirical_pass=data['summary']['empirical_pass'],incremental_pass=data['summary']['incremental_pass'],elapsed_seconds=time.monotonic()-start,**{n+'_sha256':hashlib.sha256((out/p).read_bytes()).hexdigest() for n,p in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    finally:signal.alarm(0)
if __name__=='__main__':main()
