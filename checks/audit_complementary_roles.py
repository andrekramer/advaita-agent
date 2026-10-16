"""Independent saved-record audit for experiment 007. No learner imports."""
import copy
import hashlib
import json
import math
from pathlib import Path
import random
import statistics

ROOT=Path(__file__).resolve().parents[1]
NAMES=('full','no_feedback','no_teaching','disconnected','online','misaligned')
REGIMES=('LL','LH','HL','HH')
T0=[.55,0.,0.,0.,0.]


def close(a,b):
    if isinstance(a,dict):
        assert a.keys()==b.keys(),(a.keys(),b.keys())
        for key in a: close(a[key],b[key])
    elif isinstance(a,(list,tuple)):
        assert len(a)==len(b)
        for x,y in zip(a,b): close(x,y)
    elif isinstance(a,float) or isinstance(b,float):
        assert math.isfinite(a) and math.isfinite(b)
        assert abs(a-b)<=1e-11+1e-10*abs(a),(a,b)
    else:
        assert a==b,(a,b)


def features(x): return [1.,math.sin(x),math.cos(x),math.sin(2*x),math.cos(2*x)]
def product(a,b): return sum(x*y for x,y in zip(a,b))
def bound(x,lo,hi): return max(lo,min(hi,x))
def response(theta,x): return bound(product(theta,features(x)),.1,1.)
def truth(x): return .55+.25*math.sin(x)+.1*math.cos(2*x)


def verify_world(seed,episodes):
    base=100000+10000*seed
    rng=random.Random(base+1)
    main=list(range(20)); rng.shuffle(main)
    regimes=list(REGIMES)*5; rng.shuffle(regimes)
    selected=list(range(4)); rng.shuffle(selected)
    sr=list(REGIMES); rng.shuffle(sr)
    tested=[0,2,5,7,10,12,15,17]; rng.shuffle(tested)
    tr=list(REGIMES)*2; rng.shuffle(tr)
    schedule=[]
    for i in range(20):
        schedule.append(('main',i,2*math.pi*main[i]/20,regimes[i]))
        if i%5==4:
            j=i//5; schedule.append(('selection',j,2*math.pi*(selected[j]+.25)/4,sr[j]))
    schedule += [('evaluation',i,2*math.pi*(tested[i]+.5)/20,tr[i]) for i in range(8)]
    ar,pr,orr,rr=[random.Random(base+i) for i in (2,3,4,5)]
    assert len(episodes)==32
    for ep,(stage,index,x0,regime) in zip(episodes,schedule):
        close([ep['stage'],ep['index'],ep['x0'],ep['regime']],[stage,index,x0,regime])
        acts=[]
        for _ in range(2):
            block=[-1]*6+[1]*6; ar.shuffle(block); acts+=block
        assert len(ep['records'])==24
        x=x0
        for t,row in enumerate(ep['records']):
            eps=pr.gauss(0,.002)
            eta=orr.gauss(0,.01 if regime[0]=='L' else .12)
            zeta=rr.gauss(0,.005 if regime[1]=='L' else .04)
            nx=x+.2*truth(x)*acts[t]+eps
            close(row,{'t':t,'x':x,'next_x':nx,'o':x+eta,'a':acts[t],'r':nx-x+zeta,
                       'epsilon':eps,'eta':eta,'zeta':zeta})
            x=nx


def verify_fit(proposal,buffer):
    n=len(buffer)
    matrix=[[1e-4 if i==j else 0. for j in range(5)] for i in range(5)]
    rhs=[1e-4*v for v in T0]
    for z,a,r in buffer:
        f=[.2*a*v for v in features(z)]
        for i in range(5):
            rhs[i]+=f[i]*r/n
            for j in range(5): matrix[i][j]+=f[i]*f[j]/n
    close(proposal['matrix'],matrix); close(proposal['rhs'],rhs)
    assert proposal['records']==n
    for row,target in zip(matrix,rhs): close(product(row,proposal['raw']),target)
    close(proposal['theta'],[bound(v,-1.,1.) for v in proposal['raw']])


def metric(pairs):
    return {'position_mse':statistics.mean((p['xhat']-r['x'])**2 for p,r in pairs),
            'loop_mse':statistics.mean((p['loop_prediction']-r['r'])**2 for p,r in pairs),
            'curve_motion_mse':statistics.mean((p['curve_prediction']-r['r'])**2 for p,r in pairs),
            'max_position_error':max(abs(p['xhat']-r['x']) for p,r in pairs)}


def verify_run(run,episodes):
    name=run['variant']; teaching=name not in ('no_teaching','disconnected')
    feedback=name not in ('no_feedback','disconnected')
    theta=T0.copy(); buffer=[]; test_theta=None; test_buffer=None
    costs={k:0 for k in run['costs']}
    all_pairs={r:[] for r in REGIMES}; accepted=0
    assert len(run['episodes'])==len(episodes)
    def cg(weights,x):
        raw=product(weights,features(x))
        costs['gain_calls']+=1; costs['gain_clips']+=int(raw<.1 or raw>1.)
        return bound(raw,.1,1.)
    for log,ep in zip(run['episodes'],episodes):
        close([log['stage'],log['index']],[ep['stage'],ep['index']])
        stage=ep['stage']; test=stage=='evaluation'; prop=log['proposal']
        if test and test_theta is None:
            test_theta=theta.copy(); test_buffer=copy.deepcopy(buffer)
        if stage=='selection' and name!='online':
            verify_fit(prop,buffer)
            costs['fits']+=1; costs['fit_rows']+=len(buffer)
            costs['coefficient_clips']+=sum(abs(w)>1. for w in prop['raw'])
        else: assert prop is None
        prior=None; d=0.; costs['resets']+=1
        state=lambda:{'theta':theta.copy(),'prior':prior,'d':d,'buffer_size':len(buffer)}
        close(log['before'],state()); pairs=[]; inc=[]; cand=[]
        assert len(log['events'])==24
        for event,row in zip(log['events'],ep['records']):
            close(event['before'],state())
            o,a,r=row['o'],row['a'],row['r']
            xhat=o if prior is None else prior+.5*(o-prior)
            z=xhat if teaching else o
            query=xhat+(math.pi if test and name=='misaligned' else 0.)
            b=cg(theta,query) if feedback else .55
            costs['loop_gain_clips']+=int(b+d<.1 or b+d>1.)
            prediction={'xhat':xhat,'z':z,'b':b,'loop_prediction':.2*bound(b+d,.1,1.)*a,
                        'curve_prediction':.2*cg(theta,xhat)*a}
            if prop is not None:
                prediction['selection_incumbent']=.2*cg(theta,z)*a
                prediction['selection_candidate']=.2*cg(prop['theta'],z)*a
                costs['selection_scores']+=2
                inc.append((prediction['selection_incumbent']-r)**2)
                cand.append((prediction['selection_candidate']-r)**2)
            close(event['prediction'],prediction)
            pairs.append((prediction,row))
            prior=xhat+prediction['loop_prediction']
            raw_d=.8*d+.2*(a*r/.2-b)
            costs['local_clips']+=int(abs(raw_d)>.4)
            d=bound(raw_d,-.4,.4); costs['local_updates']+=1
            if stage=='main': buffer.append([z,a,r])
            if name=='online' and not test:
                f=[.2*a*v for v in features(z)]
                grad=[2*f[i]*(product(f,theta)-r)+2e-4*(w-T0[i]) for i,w in enumerate(theta)]
                updated=[w-.05*grad[i]/(1+product(f,f)) for i,w in enumerate(theta)]
                costs['coefficient_clips']+=sum(abs(w)>1. for w in updated)
                theta=[bound(w,-1.,1.) for w in updated]
                costs['online_updates']+=1
            close(event['after'],state())
            if test:
                close(theta,test_theta); close(buffer,test_buffer)
        close(log['metrics'],metric(pairs))
        if test: all_pairs[ep['regime']]+=pairs
        if prop is not None:
            e0,e1=statistics.mean(inc),statistics.mean(cand)
            ok=e1<=.99*e0 and e0-e1>1e-6
            close(log['decision'],{'incumbent_mse':e0,'candidate_mse':e1,'gain':e0-e1,'accepted':ok})
            if ok: theta=prop['theta'].copy(); accepted+=1
        else: assert log['decision'] is None
        close(log['after'],state())
    close(run['theta'],theta); close(run['final_buffer'],buffer); assert len(buffer)==480
    close(run['costs'],costs)
    grid=[]
    for i in range(32):
        x=2*math.pi*(i+.5)/32
        grid.append({'x':x,'truth':truth(x),'prediction':response(theta,x),'initial':response(T0,x)})
    close(run['grid'],grid)
    strata={key:metric(pairs) for key,pairs in all_pairs.items()}
    metrics=metric([pair for pairs in all_pairs.values() for pair in pairs])
    metrics.update({'by_regime':strata,
                    'noisy_position_mse':(strata['HL']['position_mse']+strata['HH']['position_mse'])/2,
                    'gain_mse':statistics.mean((g['truth']-g['prediction'])**2 for g in grid),
                    'initial_gain_mse':statistics.mean((g['truth']-g['initial'])**2 for g in grid),
                    'accepted':accepted})
    close(run['metrics'],metrics)
    return metrics


def verify_comparisons(runs,comparison):
    means={}
    for name in NAMES:
        ms=[r['metrics'] for r in runs if r['variant']==name]
        means[name]={k:statistics.mean(m[k] for m in ms) for k in
                     ('position_mse','loop_mse','curve_motion_mse','gain_mse','noisy_position_mse')}
        for regime in ('LL','HH'):
            means[name][regime+'_loop_mse']=statistics.mean(m['by_regime'][regime]['loop_mse'] for m in ms)
    close(comparison['means'],means)
    counts={'feedback':0,'teaching':0,'joint':0}; all_count=0
    for seed,row in enumerate(comparison['per_seed']):
        assert row['seed']==seed
        m={r['variant']:r['metrics'] for r in runs if r['seed']==seed}
        f,nf,nt,dc=[m[k] for k in ('full','no_feedback','no_teaching','disconnected')]
        checks={'feedback':f['noisy_position_mse']<=.9*nf['noisy_position_mse'],
                'teaching':f['gain_mse']<=.9*nt['gain_mse'],
                'joint':all(f['by_regime']['HH']['loop_mse']<=.9*c['by_regime']['HH']['loop_mse'] for c in (nf,nt))}
        assert checks==row['criteria']; assert all(checks.values())==row['all_three']
        all_count+=all(checks.values())
        for key in counts: counts[key]+=checks[key]
        close(row['interaction'],{key:nf[key]+nt[key]-f[key]-dc[key] for key in
                                 ('position_mse','loop_mse','curve_motion_mse','gain_mse')})
    f,nf,nt,dc=[means[k] for k in ('full','no_feedback','no_teaching','disconnected')]
    pooled={'feedback':f['noisy_position_mse']<=.9*nf['noisy_position_mse'],
            'teaching':f['gain_mse']<=.9*nt['gain_mse'],
            'joint':f['HH_loop_mse']<=.9*nf['HH_loop_mse'] and f['HH_loop_mse']<=.9*nt['HH_loop_mse'],
            'clean_guard':f['LL_loop_mse']<=1.05*dc['LL_loop_mse']}
    assert comparison['pooled']==pooled and comparison['pass_counts']==counts
    assert comparison['all_three_count']==all_count
    assert comparison['complementarity_pass']==(all(pooled.values()) and all(v>=4 for v in counts.values()))


def main():
    data=json.loads((ROOT/'results/complementary-roles-v1/results.json').read_text())
    for name,digest in data['hashes'].items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    assert [w['seed'] for w in data['worlds']]==list(range(5))
    for w in data['worlds']: verify_world(w['seed'],w['episodes'])
    assert [(r['seed'],r['variant']) for r in data['runs']]==[(s,n) for s in range(5) for n in NAMES]
    for run in data['runs']: verify_run(run,data['worlds'][run['seed']]['episodes'])
    verify_comparisons(data['runs'],data['comparisons'])
    for seed in range(5):
        by={r['variant']:r for r in data['runs'] if r['seed']==seed}
        assert by['full']['episodes'][:24]==by['misaligned']['episodes'][:24]
        assert by['full']['theta']==by['misaligned']['theta']
        for ep1,ep2 in zip(by['no_feedback']['episodes'],by['disconnected']['episodes']):
            for first,second in zip(ep1['events'],ep2['events']):
                for k in ('xhat','b','loop_prediction'):
                    assert first['prediction'][k]==second['prediction'][k]
    assert data['transitions']==data['position_measurements']==30*32*24==23040
    assert data['final_curve_queries']==data['reference_curve_queries']==30*32==960
    assert sum(len(w['episodes'])*24 for w in data['worlds'])==3840
    print('PASS: 30 runs / 23,040 transitions; independent world regeneration, causal updates,')
    print('path cuts, ridge fits, feedback isolation, selection, frozen retention, costs, metrics,')
    print('criteria, paired controls, presentation budgets, and source/protocol hashes verified.')


if __name__=='__main__': main()
