"""Independent reconstruction: no new runtime, adapter or metrics imports."""
import copy,gzip,hashlib,itertools,json,random,signal,time
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close
from audit_recall_withdrawal import Reference
from audit_selective_steering import verify_world,life
from audit_protection_interfaces import canonical

ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'results/strength-inspection-v1'
ACTIONS=('none','0','1','2');MODES=('existing','raw_banks','direction_strength')
POLICIES=(*MODES,'no_op','disagreement','rotated')


def addr(ref,j,x,a):
    if j<2:return str(ref.locals[j]['partition'][x[j]])
    out=[]
    for k,s in enumerate(ref.upper['spec']):
        if s:out.append(x[k] if s==2 else ref.locals[k]['groups'][x[k]])
    return '|'.join(map(str,out+[a]))


def inspect_reference(ref,recent,target,protected,review):
    tables=[]
    for j,model in enumerate(ref.locals+[ref.upper]):
        table={key:dict(total=list(v),fast=[0.,0.],slow=[0.,0.],recent=[0,0]) for key,v in model['counts'].items()}
        for i in range(len(ref.fast[j])):
            key=addr(ref,j,[i,i] if j<2 else [i//8,(i//2)%4],0 if j<2 else i%2)
            for name in ('fast','slow'):
                for k in range(2):table[key][name][k]+=getattr(ref,name)[j][i][k]
        for row in recent:
            c=table[addr(ref,j,row['x'],row['a'])];c['recent'][0]+=(row['local']+[row['y']])[j];c['recent'][1]+=1
        tables.append(table)
    return dict(models=dict(locals=ref.locals,upper=ref.upper),cells=tables,mass=ref.mass(),
                half_lives=ref.half_lives,recent_n=len(recent),target=target,protected=protected,
                review_losses=[x['losses'] for x in review['weakenings']])


def banks(v,j,c,mode):
    if mode=='existing':
        total=v['mass']['fast'][j]+v['mass']['slow'][j]
        frac=v['mass']['fast'][j]/total if total else .5
        return [x*frac for x in c['total']],[x*(1-frac) for x in c['total']]
    if mode=='direction_strength':
        # Reproduce only rounding introduced by count -> direction -> count.
        return tuple([a/n*n if n else 0.,n] for a,n in (c['fast'],c['slow']))
    return c['fast'],c['slow']


def projections(v,mode):
    result={}
    for action in ACTIONS:
        losses=[]
        for j,table in enumerate(v['cells']):
            value=0.
            for c in table.values():
                f,s=banks(v,j,c,mode);weight=c['recent'][1]/v['recent_n'];q=(c['recent'][0]+1)/(c['recent'][1]+2)
                rf=2**(-1/64);rs=2**(-1/(128 if action==str(j) else v['half_lives'][j]))
                for t in range(1,65):
                    received=weight*rf*(1-rf**(t-1))/(1-rf)
                    n=f[1]*rf**t+s[1]*rs**t+received
                    y=f[0]*rf**t+s[0]*rs**t+q*received
                    p=(y+1)/(n+2)
                    value+=weight*(q*(1-p)**2+(1-q)*p*p)/64
            losses.append(value)
        result[action]=losses
    t=v['target'];p=v['protected'];best='none'
    for action in ACTIONS:
        if result[action][p]-result['none'][p]<=.001 and result[action][t]<result[best][t]-1e-12:best=action
    if result['none'][t]-result[best][t]<=.0005:best='none'
    return dict(choice=best,losses=result,gains={a:result['none'][t]-result[a][t] for a in ACTIONS})


def verify_probes(ref,r):
    assert len(r['probes'])==128
    contexts=list(itertools.product(range(4),range(4),range(2)))
    for i,p in enumerate(r['probes']):
        action=ACTIONS[i//32];x=list(contexts[i%32][:2]);a=contexts[i%32][2]
        labels=[int(v<.5) for v in ref.ps(x,a)]
        assert p['action']==action and p['row']==dict(x=x,a=a,local=labels[:2],y=labels[2])
        b=copy.deepcopy(ref);b.configure([],[] if action=='none' else [int(action)],'Strength inspection: bounded selected-channel plasticity')
        actual=dict(before=b.observe(641,p['row']),after=b.ps(x,a));close(p['actual'],actual)
        for mode in (*MODES,'prediction_only'):
            predicted=dict(before=[],after=[])
            for j in range(3):
                c=r['packet']['cells'][j][addr(ref,j,x,a)]
                if mode=='prediction_only':
                    values=[(c['total'][0]+1)/(c['total'][1]+2)]*2
                else:
                    f,s=banks(r['packet'],j,c,mode);rf=2**(-1/64);rs=2**(-1/(128 if action==str(j) else ref.half_lives[j]))
                    mass=f[1]*rf+s[1]*rs;y=f[0]*rf+s[0]*rs
                    values=[(y+1)/(mass+2),(y+labels[j]+1)/(mass+3)]
                for name,v in zip(('before','after'),values):predicted[name].append(v)
            close(p['forecasts'][mode],predicted)


def reconstruct(r,w):
    life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=Reference(r['acquisition_checkpoint'],'shadow');idx=0
    assert len(r['prefix_predictions'])==640 and len(r['prefix_reviews'])==10
    for t,row in enumerate(w['main'][:640],1):
        close(r['prefix_predictions'][t-1],ref.observe(t,row))
        if str(t) in w['selection']:
            ref.review(t,w['selection'][str(t)],r['prefix_reviews'][idx]);idx+=1
    close(ref.state(),r['checkpoint']['engine'])
    expected=inspect_reference(ref,w['main'][576:640],w['affected'] if r['proposal_seed']==3100 else 2,1-w['affected'],r['prefix_reviews'][-1])
    close(r['packet'],expected)
    ds={m:projections(expected,m) for m in MODES}
    target=expected['target'];slow,fast=expected['review_losses'][target][:2];chosen=ds['raw_banks']['choice']
    ds.update(no_op=dict(choice='none'),disagreement=dict(choice=str(target) if fast<=.55 and slow-fast>.05 else 'none'),rotated=dict(choice='none' if chosen=='none' else str((int(chosen)+1)%3)))
    close(r['decisions'],ds)
    assert hashlib.sha256(canonical(dict(packet=r['packet'],decisions=r['decisions'])).encode()).hexdigest()==r['decision_sha256']
    verify_probes(ref,r)
    assert set(r['branches'])==set(ACTIONS) and r['restore_checks']==8
    for action,b in r['branches'].items():
        clone=copy.deepcopy(ref)
        event=clone.configure([],[] if action=='none' else [int(action)],'Strength inspection: bounded selected-channel plasticity')
        close(event,b['commands'][0]['native']);idx=0
        assert len(b['predictions'])==512 and len(b['reviews'])==8 and len(b['commands'])==2
        for t,row in enumerate(w['main'][640:1152],641):
            close(b['predictions'][t-641],clone.observe(t,row))
            if str(t) in w['selection']:
                clone.review(t,w['selection'][str(t)],b['reviews'][idx]);idx+=1
                if t==896:close(clone.configure([],[],'Strength inspection: scheduled release'),b['commands'][1]['native'])
        close(b['checkpoint']['engine'],clone.state());assert clone.half_lives==[1024]*3


def classification(x):return 'improvement' if x>.001 else 'harm' if x<-.001 else 'negligible'


def metrics(r,w):
    windows={'early':(0,64),'active':(0,256),'released':(256,384),'returning':(384,512)}
    losses={}
    for action,b in r['branches'].items():
        losses[action]={}
        for name,(start,end) in windows.items():
            losses[action][name]=[sum((b['predictions'][k][j]-(w['main'][640+k]['local']+[w['main'][640+k]['y']])[j])**2 for k in range(start,end))/(end-start) for j in range(3)]
    t=r['packet']['target'];pr=r['packet']['protected'];future={};policies={}
    for mode in MODES:
        effects=[]
        for action in ('0','1','2'):
            a=losses['none']['early'][t]-losses[action]['early'][t];p=r['decisions'][mode]['gains'][action]
            effects.append(dict(action=action,actual=a,predicted=p,error=abs(a-p),correct=classification(a)==classification(p),nonnegligible=abs(a)>.001))
        future[mode]=dict(effects=effects,mae=mean(e['error'] for e in effects),accuracy=mean(e['correct'] for e in effects))
    best=min(v['active'][t] for v in losses.values())
    for mode in POLICIES:
        action=r['decisions'][mode]['choice'];gain=losses['none']['active'][t]-losses[action]['active'][t]
        policies[mode]=dict(choice=action,losses=losses[action],target=losses[action]['active'][t],gain=gain,acted=action!='none',unnecessary=action!='none' and gain<=.001,missed=action=='none' and losses['none']['active'][t]-best>.001,regret=losses[action]['active'][t]-best)
    errors={mode:mean(abs(p['actual'][when][j]-p['forecasts'][mode][when][j]) for p in r['probes'] for when in ('before','after') for j in range(3)) for mode in ('prediction_only',*MODES)}
    result=dict(branches=losses,probe_errors=errors,future=future,policies=policies,target=t,protected=pr)
    close(result,r['metrics']);return result


def verify_summary(rs,s):
    seeds=sorted({r['seed'] for r in rs});rng=random.Random(417)
    samples=[[rng.randrange(len(seeds)) for _ in seeds] for _ in range(5000)]
    def ci(fn):
        xs=[mean(fn(r) for r in rs if r['seed']==seed) for seed in seeds]
        vals=sorted(sum(xs[i] for i in sample)/len(sample) for sample in samples)
        def quantile(p):
            pos=(len(vals)-1)*p;lo=int(pos);return vals[lo]*(1-pos+lo)+vals[min(lo+1,len(vals)-1)]*(pos-lo)
        return dict(mean=mean(xs),low=quantile(.025),high=quantile(.975),positive=sum(x>1e-12 for x in xs),n=len(xs))
    f=ci(lambda r:r['metrics']['future']['raw_banks']['mae']-r['metrics']['future']['existing']['mae'])
    gs={p:ci(lambda r,p=p:r['metrics']['policies'][p]['target']-r['metrics']['policies']['raw_banks']['target']) for p in ('existing','no_op','disagreement','rotated')}
    close(s['future_error_difference'],f);close(s['steering_gains'],gs)
    guards=[];groups=[]
    for h in ('stable','forms','repeated'):
        subset=[r for r in rs if r['history']==h]
        for win in ('active','released','returning'):
            for j in range(3):
                use=[r for r in subset if win!='active' or h=='stable' or r['metrics']['protected']==j]
                if not use:continue
                values=[r['metrics']['policies']['raw_banks']['losses'][win][j]-r['metrics']['policies']['no_op']['losses'][win][j] for r in use]
                guards.append(dict(history=h,window=win,channel=j,mean=mean(values),maximum=max(values),passed=mean(values)<=.01 and max(values)<=.05))
        for task in ('local','composite'):
            subset2=[r for r in subset if (r['metrics']['target']==2)==(task=='composite')]
            for p in POLICIES:
                values=[r['metrics']['policies'][p] for r in subset2]
                groups.append(dict(history=h,task=task,policy=p,n=len(values),loss=mean(x['target'] for x in values),gain=mean(x['gain'] for x in values),actions=sum(x['acted'] for x in values),unnecessary=sum(x['unnecessary'] for x in values),missed=sum(x['missed'] for x in values),regret=mean(x['regret'] for x in values)))
    close(s['guards'],guards);close(s['groups'],groups)
    es=[e for r in rs for e in r['metrics']['future']['raw_banks']['effects']]
    accuracy=mean(e['correct'] for e in es);coverage=sum(e['nonnegligible'] for e in es)
    maxima={m:max(abs(p['actual'][w][j]-p['forecasts'][m][w][j]) for r in rs for p in r['probes'] for w in ('before','after') for j in range(3)) for m in ('raw_banks','direction_strength')}
    gates=dict(mechanical=max(maxima.values())<=1e-10,information_forecast=f['high']<0,effect_direction=coverage>=24 and accuracy>=.75,steering_mean=gs['existing']['mean']>=.001 and gs['existing']['low']>0,steering_consistency=gs['existing']['positive']>=8,versus_no_op=gs['no_op']['low']>=-.001,preservation=all(g['passed'] for g in guards))
    close(s['gates'],gates);close(s['mechanical_maxima'],maxima)
    close(s['probe_mean_errors'],{m:mean(r['metrics']['probe_errors'][m] for r in rs) for m in ('prediction_only',*MODES)})
    assert s['information_pass']==(gates['information_forecast'] and gates['effect_direction'])
    assert s['steering_pass']==all(gates[k] for k in ('steering_mean','steering_consistency','versus_no_op','preservation'))
    assert s['presentation_tested'] is False and s['nonnegligible_effects']==coverage
    close(s['future_accuracy'],accuracy)


def main():
    assert not (OUT/'audit.json').exists();start=time.monotonic();status='failed';error=None;count=0
    def timeout(*_):raise TimeoutError('Strength inspection auditor900s cap')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        manifest=json.loads((OUT/'manifest.json').read_text())
        for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        for p,d in json.loads((OUT/'artifact-hashes.json').read_text()).items():assert hashlib.sha256((OUT/p).read_bytes()).hexdigest()==d,p
        ws=json.loads((OUT/'worlds.json').read_text());assert len(ws)==36
        assert {(w['seed'],w['branch']) for w in ws}==set(itertools.product(range(3100,3112),('stable','forms','repeated')))
        for w in ws:verify_world(w)
        worlds={(w['seed'],w['branch']):w for w in ws};rs=[]
        with gzip.open(OUT/'runs.jsonl.gz','rt') as f:
            for line in f:
                r=json.loads(line);w=worlds[r['seed'],r['history']]
                reconstruct(r,w);metrics(r,w);rs.append(r);count+=1
                if count%6==0:print(f'Audit: {count}/72 cases',flush=True)
        assert len(rs)==72 and {(r['seed'],r['history'],r['proposal_seed']) for r in rs}==set(itertools.product(range(3100,3112),('stable','forms','repeated'),(3100,3101)))
        data=json.loads((OUT/'results.json').read_text());verify_summary(rs,data['summary'])
        acquisition=sum(r['acquisition']['costs']['feedback_labels'] for r in rs)
        total=dict(environments=12,worlds=36,trunks=72,continuations=288,generated_scalar_labels=36*10240,acquisition_label_presentations=acquisition,prefix_label_presentations=72*3*960,future_label_presentations=288*3*768,training_label_presentations=acquisition+72*3*960+288*3*768,controller_reused_scalar_labels=72*192,synthetic_probe_scalar_labels=72*384,probe_clones=9216,restores=576)
        close(data['totals'],total);assert data['elapsed_seconds']<900;status='pass'
    except BaseException as exc:error=repr(exc);raise
    finally:
        signal.alarm(0)
        (OUT/'audit.json').write_text(json.dumps(dict(status=status,error=error,cases=count,elapsed_seconds=time.monotonic()-start,scope='independent worlds, acquisition, native learning, probes, packets, decisions and metrics; wrapper metadata roundtrips checked by runner'),indent=2)+'\n')


if __name__=='__main__':main()
