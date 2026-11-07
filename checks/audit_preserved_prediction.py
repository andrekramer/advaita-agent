"""036 independent archive, world, learning and outcome verification."""
import copy,gzip,hashlib,itertools,json,math,signal,time,types
from pathlib import Path
from statistics import mean
from audit_nested_abstractions import close,logloss
from audit_protection_interfaces import canonical
from audit_coordinated_steering import CoordinatedReference
import audit_temporary_plasticity as previous
from memory_control_reference import lp,up
ROOT=Path(__file__).resolve().parents[1]
HISTORIES=('stable','forms','repeated','forms_persistent','repeated_persistent','forms_other')
POLICIES=('discard','shadow','recall')
WINDOWS=dict(active=(513,1024),early_return=(1025,1280),returning=(1025,1536),later=(1537,2048))

def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()
def exact_loss(p,y):return -math.log(p if y else 1-p)
def ports(local,spec):
    out=[dict(name='action',domain=[0,1],meaning='fixed action alphabet')]
    for j in (0,1):
        if spec[j]:out.append(dict(name='local'+str(j),domain=[0,1,2,3] if spec[j]==2 else [0,1],meaning=[0,1,2,3] if spec[j]==2 else list(local[j]['groups'])))
    return out
def binding(local,spec):return sha(sorted(ports(local,spec),key=lambda p:p['name']))

def third(w):
    original=w['forms'][w['affected']];other=w['alternative']
    candidates=[[0,0,1,1],[0,1,0,1],[0,1,1,0]]
    return next(f for f in candidates if f not in (original,[1-x for x in original],other,[1-x for x in other]))

def forms(w,t,observed=False):
    f=previous.forms(dict(w,branch='forms') if w['branch']=='forms_other' else w,t,observed)
    if w['branch']=='forms_other' and 1025<=t<=1536:f[w['affected']]=third(w)
    return f

def truth(w,x,a,t):
    f=forms(w,t,True);return (f[0][x[0]]+f[1][x[1]]+a)%2

def verify_world(w):
    v=copy.deepcopy(w)
    if v['branch']=='forms_other':
        v['branch']='forms';j=v['affected']
        for t,rows in [(t,[r]) for t,r in enumerate(v['main'],1)]+[(int(t),rows) for t,rows in v['selection'].items()]:
            if 1025<=t<=1536:
                for r in rows:
                    delta=(w['forms'][j][r['x'][j]]+third(w)[r['x'][j]])%2
                    r['local'][j]=(r['local'][j]+delta)%2;r['y']=(r['y']+delta)%2
    previous.verify_world(v)


class Reference(CoordinatedReference):
    def __init__(self,c,policy):
        super().__init__(c);self.recall=policy
        self.memory=dict(slot=None,passes=0,confirmed=False,attempt_complete=False,route=False,events=[],prediction_uses=0,blocked_predictions=0,diagnostic_queries=0,archive_prediction_queries=0,acquisition_sha256=sha(c))
    def state(self):
        d=super().state();d.update(schema=36,recall=self.recall,memory=self.memory);return d
    def compatible(self):
        s=self.memory['slot'];return s is not None and s['dependency']==binding(self.locals,s['upper']['spec'])
    def archive_p(self,x,a):
        s=self.memory['slot'];return up(s['upper'],s['locals'],x,a)
    def ps(self,x,a):return [lp(self.locals[j],x[j]) for j in (0,1)]+[up(self.upper,self.locals,x,a)]
    def routed(self,x,a):
        ps=self.ps(x,a)
        if self.recall=='recall' and self.memory['confirmed'] and self.memory['route'] and self.compatible():ps[2]=self.archive_p(x,a)
        return ps
    def observe(self,t,row):
        assert t==self.tick+1;self.tick=t;self.costs['ticks']+=1
        for j,h in enumerate(self.half_lives):
            if h!=1024:
                rate=2**(-1/h+1/1024)
                for cell in self.slow[j]:cell[0]*=rate;cell[1]*=rate
        for bank,rho in ((self.fast,2**(-1/64)),(self.slow,2**(-1/1024))):
            for table in bank:
                for cell in table:cell[0]*=rho;cell[1]*=rho
        self.refresh();active=self.ps(row['x'],row['a']);compatible=self.compatible()
        use=self.recall=='recall' and self.memory['confirmed'] and self.memory['route'] and compatible
        ps=active.copy()
        if use:ps[2]=self.archive_p(row['x'],row['a'])
        self.prediction_event=dict(active=active,source='archive' if use else 'active',compatible=compatible)
        for j,index,y in zip(range(3),row['x']+[8*row['x'][0]+2*row['x'][1]+row['a']],row['local']+[row['y']]):self.fast[j][index][0]+=y;self.fast[j][index][1]+=1
        self.main_ids.append(t);self.costs['observations']+=1;self.refresh()
        self.memory['prediction_uses']+=int(use);self.memory['archive_prediction_queries']+=int(use)
        self.memory['blocked_predictions']+=int(self.recall=='recall' and self.memory['route'] and not compatible)
        return ps
    def review(self,t,rows,saved):
        event=None;s=self.memory['slot']
        if t>=448:
            active=[up(self.upper,self.locals,r['x'],r['a']) for r in rows]
            other=[self.archive_p(r['x'],r['a']) for r in rows] if s else active.copy()
            value=lambda ps:sum(exact_loss(p,r['y']) for p,r in zip(ps,rows))/len(rows)
            event=dict(tick=t,active_predictions=active,archive_predictions=other,active_loss=value(active),archive_loss=value(other),dummy=s is None,compatible_before=self.compatible(),model_sha256=sha(dict(locals=self.locals,upper=self.upper)),slot_sha256=None if s is None else sha(s),batch_sha256=sha(rows),passes_before=self.memory['passes'],route_before=self.memory['route'])
            self.memory['diagnostic_queries']+=2*len(rows)
            if s and t in (448,512):self.memory['passes']=self.memory['passes']+1 if event['compatible_before'] and event['archive_loss']<=.55 else 0
        super().review(t,rows,saved)
        if t==384:self.memory['slot']=dict(upper=copy.deepcopy(self.upper),locals=[dict(groups=list(m['groups'])) for m in self.locals],dependency=binding(self.locals,self.upper['spec']),ports=ports(self.locals,self.upper['spec']),captured_at=t,acquisition_sha256=self.memory['acquisition_sha256'],main_ids=list(self.main_ids),selection_ids=list(self.selection_ids),source_model_sha256=sha(dict(locals=self.locals,upper=self.upper)),evidence_mass=copy.deepcopy(self.mass()))
        if event:
            compatible=self.compatible()
            if t in (448,512) and not compatible:self.memory['passes']=0
            if t==512:
                self.memory['confirmed']=self.memory['passes']==2 and compatible;self.memory['attempt_complete']=True
                if not self.memory['confirmed'] or self.recall=='discard':self.memory['slot']=None
            eligible=t>=576 and self.memory['confirmed'] and self.memory['slot'] is not None and event['compatible_before'] and compatible
            admitted=bool(eligible and event['archive_loss']<=.55 and event['active_loss']-event['archive_loss']>=.02)
            self.memory['route']=admitted and self.recall=='recall'
            event.update(compatible_after=compatible,passes_after=self.memory['passes'],confirmed=self.memory['confirmed'],eligible=bool(eligible),admitted=admitted,route_after=self.memory['route']);self.memory['events'].append(event)

ref_world=types.SimpleNamespace(CONTEXTS=previous.old.life.CONTEXTS,forms=forms,truth=truth)
_evaluation=types.FunctionType(previous.old.evaluation.__code__,dict(previous.old.evaluation.__globals__,life=ref_world))

def evaluation(ref,w,t):
    active=_evaluation(ref,w,t);out=copy.deepcopy(active);ps=[];correct=0;loss=[]
    for x,y,a in ref_world.CONTEXTS:
        pred=ref.routed([x,y],a);ps.append(pred);target=truth(w,[x,y],a,t);correct+=int((pred[2]>=.5)==bool(target));loss.append(.9*logloss(pred[2],target)+.1*logloss(pred[2],1-target))
    use=ref.recall=='recall' and ref.memory['route'] and ref.memory['confirmed'] and ref.compatible()
    out.update(predictions=ps,accuracy=correct/32,regret=sum(loss)/32-(-.9*math.log(.9)-.1*math.log(.1)),spec=copy.deepcopy(ref.memory['slot']['upper']['spec'] if use else ref.upper['spec']),active=active,source='archive' if use else 'active')
    out['valid']=all(out['local_exact']) and correct==32 and out['regret']<=.10
    return out

def verify_run(r,w):
    previous.old.life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=Reference(r['acquisition_checkpoint'],r['policy']);pos=0;controls=[];restores=[];capture=None;extra=0
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(ref.slow[j]) for j,h in enumerate(ref.half_lives) if h!=1024)
        close(r['predictions'][t-1],ref.observe(t,row));close(r['prediction_events'][t-1],ref.prediction_event);close(r['active_predictions'][t-1],ref.prediction_event['active'])
        if str(t) in w['selection']:
            ref.review(t,w['selection'][str(t)],r['reviews'][pos])
            if t==384:capture=copy.deepcopy(ref.memory['slot'])
            if t in (512,1024):controls.append(copy.deepcopy(ref.configure([1-w['affected']] if t==512 else [],[2] if t==512 else [],'036 supplied downstream boost' if t==512 else '036 supplied release')))
            close(r['inspections'][pos],ref.inspect());close(r['evaluations'][pos],evaluation(ref,w,t));pos+=1
        if t in (448,1152):restores.append(dict(tick=t,sha256=sha(ref.state())))
    assert len(r['predictions'])==len(r['active_predictions'])==len(r['prediction_events'])==len(w['main']) and pos==len(r['reviews'])==len(r['inspections'])==len(r['evaluations'])
    close(r['checkpoint'],ref.state());close(r['capture'],capture);close(r['controls'],controls);close(r['restore_checks'],restores);close(r['memory_events'],ref.memory['events']);close(r['costs'],ref.costs)
    assert r['extra_decay_cell_visits']==extra and r['feedback_labels']==r['acquisition']['costs']['feedback_labels']+3*(len(w['main'])+sum(len(x) for x in w['selection'].values()))
    verify_metrics(r,w)


def verify_metrics(r,w):
    vals={'expected':[],'observed':[],'active_expected':[]}
    for t,row in enumerate(w['main'],1):
        f=forms(w,t,True);targets=[f[j][row['x'][j]] for j in (0,1)]+[truth(w,row['x'],row['a'],t)]
        for typ,key in [('expected','predictions'),('active_expected','active_predictions')]:vals[typ].append([.9*logloss(p,y)+.1*logloss(p,1-y) for p,y in zip(r[key][t-1],targets)])
        vals['observed'].append([logloss(p,y) for p,y in zip(r['predictions'][t-1],row['local']+[row['y']])])
    m={typ:{k:[sum(v[j] for v in rows[lo-1:hi])/(hi-lo+1) for j in range(3)] for k,(lo,hi) in WINDOWS.items()} for typ,rows in vals.items()}
    state=r['checkpoint']['memory'];end=r['evaluations'][-1]
    m.update(confirmed=state['confirmed'],retained=state['slot'] is not None,uses=sum(e['source']=='archive' for e in r['prediction_events']),blocked=state['blocked_predictions'],admitted_reviews=sum(e['admitted'] for e in r['memory_events']),eligible_reviews=sum(e['eligible'] for e in r['memory_events']),final_valid=end['valid'],active_final_valid=end['active']['valid'],final_spec=end['spec'],uses_by_window={k:sum(e['source']=='archive' for e in r['prediction_events'][lo-1:hi]) for k,(lo,hi) in WINDOWS.items()})
    close(r['metrics'],m)


def verify_summary(rs,saved):
    keys=sorted({(r['seed'],r['proposal_seed']) for r in rs});table={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r for r in rs}
    groups=[];pairs=[];guards=[]
    for h in HISTORIES:
        for policy in POLICIES:
            ms=[table[s,q,h,policy]['metrics'] for s,q in keys]
            g=dict(history=h,policy=policy,confirmed=sum(m['confirmed'] for m in ms),retained=sum(m['retained'] for m in ms),uses=sum(m['uses'] for m in ms),blocked=sum(m['blocked'] for m in ms),eligible_reviews=sum(m['eligible_reviews'] for m in ms),admitted_reviews=sum(m['admitted_reviews'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),active_final_valid=sum(m['active_final_valid'] for m in ms))
            for typ in ('expected','observed','active_expected'):g[typ]={k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS}
            groups.append(g)
        for seed,ps in keys:
            a=table[seed,ps,h,'recall']['metrics'];b=table[seed,ps,h,'shadow']['metrics']
            pairs.append(dict(seed=seed,proposal_seed=ps,history=h,gain={k:b['expected'][k][2]-a['expected'][k][2] for k in WINDOWS},observed_gain={k:b['observed'][k][2]-a['observed'][k][2] for k in WINDOWS},costs={k:[a['expected'][k][j]-b['expected'][k][j] for j in range(3)] for k in WINDOWS},uses=a['uses'],confirmed=a['confirmed']))
        for k in WINDOWS:
            for j in range(3):
                xs=[p['costs'][k][j] for p in pairs if p['history']==h]
                guards.append(dict(history=h,window=k,channel=j,mean_cost=mean(xs),max_cost=max(xs),passed=mean(xs)<=.02 and all(x<=.10 for x in xs)))
    parity=True
    for h in HISTORIES:
        for s,q in keys:
            base=table[s,q,h,'discard'];shadow=table[s,q,h,'shadow']
            parity &= base['predictions']==shadow['predictions']
            for policy in POLICIES:
                r=table[s,q,h,policy];parity &= r['active_predictions']==base['active_predictions'] and r['reviews']==base['reviews']
                # Stronger than output parity: every retained learning statistic,
                # proposal deck and RNG state also agrees. Audit-only controller
                # before-hashes include the intentionally different memory state.
                def core(x):
                    d=copy.deepcopy(x['checkpoint'])
                    for k in ('recall','memory'):d.pop(k)
                    for event in d['control_events']:event.pop('before_sha256')
                    return d
                if 'checkpoint' in r:close(core(r),core(base))
    returned=[p for p in pairs if p['history'] in ('forms','repeated')];avg=mean(p['gain']['early_return'] for p in returned);positive=sum(p['gain']['early_return']>1e-12 for p in returned)
    gates=dict(mean_recall_gain=avg>=.02,recall_consistency=positive>=14,each_return_improves=all(mean(p['gain']['early_return'] for p in returned if p['history']==h)>1e-12 for h in ('forms','repeated')),preservation=all(g['passed'] for g in guards),final_validity=all(g['final_valid']>=8 and g['active_final_valid']>=8 for g in groups if g['policy']=='recall'),control_parity=bool(parity))
    close(saved,dict(gates=gates,empirical_pass=all(gates.values()),groups=groups,paired=pairs,guards=guards,mean_gain=avg,positive=positive,environment_means=[dict(seed=s,gain=mean(p['gain']['early_return'] for p in returned if p['seed']==s)) for s in sorted({p['seed'] for p in returned})]))


def verify_totals(rs,ws,saved):
    out=dict(runs=len(rs),generated_labels=0,used_labels=0,candidate_fits=0,scoring_queries=0,raw_bin_visits=0,main_predictions=0,grid_predictions=0,extra_decay_cell_visits=0,memory_diagnostic_queries=0,archive_prediction_queries=0)
    for w in ws:out['generated_labels']+=sum(len(x) for x in w['local_main'])+sum(len(x) for b in w['local_selection'] for x in b)+len(w['composition'])+3*(len(w['main'])+sum(len(x) for x in w['selection'].values()))
    for r in rs:
        out['used_labels']+=r['feedback_labels'];out['candidate_fits']+=r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'];out['scoring_queries']+=r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'];out['raw_bin_visits']+=r['costs']['raw_bin_visits'];out['main_predictions']+=3*len(r['predictions']);out['grid_predictions']+=64*len(r['evaluations']);out['extra_decay_cell_visits']+=r['extra_decay_cell_visits'];out['memory_diagnostic_queries']+=r['checkpoint']['memory']['diagnostic_queries'];out['archive_prediction_queries']+=r['metrics']['uses']
    close(out,saved);assert out['generated_labels']==307200 and out['used_labels']==1843200 and out['memory_diagnostic_queries']==299520
    for k,v in dict(candidate_fits=350000,scoring_queries=22000000,raw_bin_visits=110000000,grid_predictions=400000,extra_decay_cell_visits=2949120).items():assert out[k]<=v


def main():
    out=ROOT/'results/preserved-prediction-v1';start=time.monotonic();examined=0
    def timeout(*_):raise TimeoutError('036 audit 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text());close(data['hashes'],manifest)
        for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(ws)==len(worlds)==30 and set(ws)==set(itertools.product(range(2500,2505),HISTORIES))
        for w in worlds:verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
        assert len(rs)==180 and {(r['seed'],r['history'],r['proposal_seed'],r['policy']) for r in rs}==set(itertools.product(range(2500,2505),HISTORIES,(2500,2501),POLICIES))
        for examined,r in enumerate(rs,1):
            verify_run(r,ws[r['seed'],r['history']])
            if examined%6==0:print(f'{examined}/180 independently reconstructed',flush=True)
        verify_summary(rs,data['summary']);verify_totals(rs,worlds,data['totals']);assert data['elapsed_seconds']<900
        result=dict(status='pass',runs=180,empirical_pass=data['summary']['empirical_pass'],elapsed_seconds=time.monotonic()-start,**{k+'_sha256':hashlib.sha256((out/n).read_bytes()).hexdigest() for k,n in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    except BaseException as exc:
        (out/'audit-failed.json').write_text(json.dumps(dict(status='failed',error=repr(exc),examined=examined,elapsed_seconds=time.monotonic()-start),indent=2)+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
