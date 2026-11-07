"""037 independent monitor, command, learning, world and outcome reconstruction."""
import copy,gzip,hashlib,itertools,json,math,signal,time,types
from pathlib import Path
from statistics import mean
import audit_preserved_prediction as old
from audit_nested_abstractions import close
from audit_protection_interfaces import canonical
ROOT=Path(__file__).resolve().parents[1]
HISTORIES=old.HISTORIES
POLICIES=('shadow','current','command','evidence')
WINDOWS=dict(old.WINDOWS,rechange=(1537,1600))

def sha(x):return hashlib.sha256(canonical(x).encode()).hexdigest()

class Reference(old.Reference):
    def __init__(self,c,p):
        super().__init__(c,'shadow' if p=='shadow' else 'recall')
        self.steering=dict(policy=p,blocked=False,window=[],commands=[],monitors=[],reviews=[],monitor_queries=0,withdrawals=0)
    def state(self):
        d=super().state();d.update(schema=37,steering=self.steering);return d
    def observe(self,t,row):
        # Archive tables are immutable, so calculate before even the active
        # decay/update; the active probability comes from the inherited replay.
        archived=self.archive_p(row['x'],row['a']) if self.memory['confirmed'] and self.memory['slot'] else None
        self.steering['monitor_queries']+=int(archived is not None)
        ps=super().observe(t,row);e=self.prediction_event;s=self.steering
        e.update(monitor_archive=archived,externally_blocked=s['blocked'])
        if e['source']!='archive':s['window']=[];return ps
        y=row['y'];q=e['active'][2]
        s['window'].append(dict(tick=t,archive_loss=old.exact_loss(archived,y),active_loss=old.exact_loss(q,y)))
        if len(s['window'])==16:
            av=sum(x['archive_loss'] for x in s['window'])/16;cv=sum(x['active_loss'] for x in s['window'])/16
            trigger=av-cv>.02;withdraw=trigger and s['policy']=='evidence'
            event=dict(tick=t,first_tick=s['window'][0]['tick'],n=16,archive_loss=av,active_loss=cv,triggered=trigger,withdrawn=withdraw,before_sha256=sha(self.state()))
            if withdraw:self.memory['route']=False;s['withdrawals']+=1
            s['window']=[];event['route_after']=self.memory['route'];s['monitors'].append(event)
        return ps
    def review(self,t,rows,saved):
        super().review(t,rows,saved);ordinary=self.memory['route'];self.steering['window']=[]
        if self.steering['blocked']:self.memory['route']=False
        self.steering['reviews'].append(dict(tick=t,ordinary_route=ordinary,blocked=self.steering['blocked'],effective_route=self.memory['route']))
    def command(self,blocked,reason,source):
        s=self.steering
        event=dict(tick=self.tick,blocked=blocked,reason=reason,source=source,previous_blocked=s['blocked'],previous_route=self.memory['route'],before_sha256=sha(self.state()))
        s['blocked']=blocked;s['window']=[];self.memory['route']=False;event['route_after']=False;s['commands'].append(event)
        return event


def verify_run(r,w):
    old.previous.old.life.verify_legacy(r['acquisition'],w,r['acquisition_checkpoint'],True)
    ref=Reference(r['acquisition_checkpoint'],r['policy']);pos=0;controls=[];commands=[];restores=[];capture=None;extra=0
    for t,row in enumerate(w['main'],1):
        extra+=sum(len(ref.slow[j]) for j,h in enumerate(ref.half_lives) if h!=1024)
        close(r['predictions'][t-1],ref.observe(t,row));close(r['prediction_events'][t-1],ref.prediction_event);close(r['active_predictions'][t-1],ref.prediction_event['active'])
        assert not (ref.prediction_event['externally_blocked'] and ref.prediction_event['source']=='archive')
        if str(t) in w['selection']:
            ref.review(t,w['selection'][str(t)],r['reviews'][pos])
            if t==384:capture=copy.deepcopy(ref.memory['slot'])
            if t in (512,1024):controls.append(copy.deepcopy(ref.configure([1-w['affected']] if t==512 else [],[2] if t==512 else [],'037 supplied downstream boost' if t==512 else '037 supplied release')))
        if r['policy']=='command' and t in (1552,1664):commands.append(copy.deepcopy(ref.command(t==1552,'037 scheduled recall block' if t==1552 else '037 scheduled block release','supplied experiment schedule')))
        if str(t) in w['selection']:
            close(r['inspections'][pos],ref.inspect());close(r['evaluations'][pos],old.evaluation(ref,w,t));pos+=1
        if t in (448,1544,1552,1664):restores.append(dict(tick=t,sha256=sha(ref.state())))
    assert len(r['predictions'])==len(r['active_predictions'])==len(r['prediction_events'])==len(w['main']) and pos==len(r['reviews'])==len(r['inspections'])==len(r['evaluations'])
    close(r['checkpoint'],ref.state());close(r['capture'],capture);close(r['controls'],controls);close(r['steering_commands'],commands);close(r['restore_checks'],restores);close(r['memory_events'],ref.memory['events']);close(r['costs'],ref.costs)
    assert r['extra_decay_cell_visits']==extra and r['feedback_labels']==r['acquisition']['costs']['feedback_labels']+3*(len(w['main'])+sum(len(xs) for xs in w['selection'].values()))
    if r['policy']=='command':
        assert len(commands)==2 and not ref.steering['blocked']
        assert all(e['source']=='active' for e in r['prediction_events'][1552:1728])
    verify_metrics(r,w)


def verify_metrics(r,w):
    # Independently frozen 036 measurement arithmetic, extended by one fixed window.
    base={k:v for k,v in r['metrics'].items() if k not in ('withdrawals','commands','blocked_uses','monitor_windows')}
    v=dict(r,metrics=base)
    fn=types.FunctionType(old.verify_metrics.__code__,dict(old.verify_metrics.__globals__,WINDOWS=WINDOWS));fn(v,w)
    s=r['checkpoint']['steering'];extra=dict(withdrawals=s['withdrawals'],commands=len(s['commands']),blocked_uses=sum(e['source']=='archive' and e['externally_blocked'] for e in r['prediction_events']),monitor_windows=len(s['monitors']))
    close({k:r['metrics'][k] for k in extra},extra)


def verify_summary(rs,saved):
    keys=sorted({(r['seed'],r['proposal_seed']) for r in rs});table={(r['seed'],r['proposal_seed'],r['history'],r['policy']):r for r in rs};groups=[];paired=[];guards=[];retention=[]
    for h in HISTORIES:
        for p in POLICIES:
            ms=[table[s,q,h,p]['metrics'] for s,q in keys]
            g=dict(history=h,policy=p,confirmed=sum(m['confirmed'] for m in ms),uses=sum(m['uses'] for m in ms),withdrawals=sum(m['withdrawals'] for m in ms),commands=sum(m['commands'] for m in ms),blocked_uses=sum(m['blocked_uses'] for m in ms),final_valid=sum(m['final_valid'] for m in ms),active_final_valid=sum(m['active_final_valid'] for m in ms))
            for typ in ('expected','observed','active_expected'):g[typ]={k:[mean(m[typ][k][j] for m in ms) for j in range(3)] for k in WINDOWS}
            groups.append(g)
        for seed,ps in keys:
            ms={p:table[seed,ps,h,p]['metrics'] for p in POLICIES}
            paired.append(dict(seed=seed,proposal_seed=ps,history=h,rechange_gain=ms['current']['expected']['rechange'][2]-ms['evidence']['expected']['rechange'][2],return_gain=ms['shadow']['expected']['returning'][2]-ms['evidence']['expected']['returning'][2],command_rechange_gain=ms['current']['expected']['rechange'][2]-ms['command']['expected']['rechange'][2],costs={p:{k:[ms['evidence']['expected'][k][j]-ms[p]['expected'][k][j] for j in range(3)] for k in WINDOWS} for p in ('current','shadow')}))
        for control in ('current','shadow'):
            for window in old.WINDOWS:
                for j in range(3):
                    xs=[p['costs'][control][window][j] for p in paired if p['history']==h];m=mean(xs)
                    guards.append(dict(history=h,control=control,window=window,channel=j,mean_cost=m,max_cost=max(xs),passed=m<=.02 and all(x<=.10 for x in xs)))
        if h in ('forms','repeated'):
            for window in ('early_return','returning'):
                xs=[p['costs']['current'][window][2] for p in paired if p['history']==h];m=mean(xs)
                retention.append(dict(history=h,window=window,mean_cost=m,max_cost=max(xs),passed=m<=.01 and all(x<=.05 for x in xs)))
    parity=True
    for h in HISTORIES:
        for s,q in keys:
            base=table[s,q,h,'current']
            for p in POLICIES:
                r=table[s,q,h,p];parity &= r['active_predictions']==base['active_predictions'] and r['reviews']==base['reviews']
                if 'checkpoint' in r:
                    def core(x):
                        d=copy.deepcopy(x['checkpoint'])
                        for k in ('recall','memory','steering'):d.pop(k)
                        for e in d['control_events']:e.pop('before_sha256')
                        return d
                    assert core(r)==core(base)
    returned=[p for p in paired if p['history'] in ('forms','repeated')];rechange=mean(p['rechange_gain'] for p in returned);ret=mean(p['return_gain'] for p in returned)
    gates=dict(rechange_mean=rechange>=.10,rechange_consistency=sum(p['rechange_gain']>1e-12 for p in returned)>=14,each_rechange_improves=all(mean(p['rechange_gain'] for p in returned if p['history']==h)>1e-12 for h in ('forms','repeated')),retained_recall=all(x['passed'] for x in retention),useful_recall_mean=ret>=.01,useful_recall_consistency=sum(p['return_gain']>1e-12 for p in returned)>=14,preservation=all(x['passed'] for x in guards),final_validity=all(g['final_valid']>=8 and g['active_final_valid']>=8 for g in groups if g['policy']=='evidence'),active_parity=bool(parity))
    close(saved,dict(gates=gates,empirical_pass=all(gates.values()),groups=groups,paired=paired,guards=guards,retention_guards=retention,rechange_mean=rechange,rechange_positive=sum(p['rechange_gain']>1e-12 for p in returned),return_mean=ret,return_positive=sum(p['return_gain']>1e-12 for p in returned),command_rechange_mean=mean(p['command_rechange_gain'] for p in returned),environment_means=[dict(seed=s,rechange_gain=mean(p['rechange_gain'] for p in returned if p['seed']==s),return_gain=mean(p['return_gain'] for p in returned if p['seed']==s)) for s in sorted({p['seed'] for p in returned})]))


def verify_totals(rs,ws,saved):
    out=dict(runs=len(rs),generated_labels=0,used_labels=0,candidate_fits=0,scoring_queries=0,raw_bin_visits=0,main_predictions=0,grid_predictions=0,extra_decay_cell_visits=0,memory_diagnostic_queries=0,archive_prediction_queries=0,monitor_queries=0)
    for w in ws:out['generated_labels']+=sum(len(x) for x in w['local_main'])+sum(len(x) for batch in w['local_selection'] for x in batch)+len(w['composition'])+3*(len(w['main'])+sum(len(x) for x in w['selection'].values()))
    for r in rs:
        out['used_labels']+=r['feedback_labels'];out['candidate_fits']+=r['costs']['candidate_fits']+r['acquisition']['costs']['candidate_fits'];out['scoring_queries']+=r['costs']['scoring_queries']+r['acquisition']['costs']['scoring_queries'];out['raw_bin_visits']+=r['costs']['raw_bin_visits'];out['main_predictions']+=3*len(r['predictions']);out['grid_predictions']+=64*len(r['evaluations']);out['extra_decay_cell_visits']+=r['extra_decay_cell_visits'];out['memory_diagnostic_queries']+=r['checkpoint']['memory']['diagnostic_queries'];out['archive_prediction_queries']+=r['metrics']['uses'];out['monitor_queries']+=r['checkpoint']['steering']['monitor_queries']
    close(out,saved);assert out['generated_labels']==307200 and out['used_labels']==2457600 and out['memory_diagnostic_queries']==399360
    for k,v in dict(candidate_fits=450000,scoring_queries=30000000,raw_bin_visits=140000000,grid_predictions=500000,extra_decay_cell_visits=3932160,monitor_queries=491520).items():assert out[k]<=v


def main():
    out=ROOT/'results/recall-withdrawal-v1';start=time.monotonic();examined=0
    def timeout(*_):raise TimeoutError('037 audit 900s ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());m=json.loads((out/'manifest.json').read_text());close(data['hashes'],m)
        for p,d in m.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());ws={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==len(ws)==30 and set(ws)==set(itertools.product(range(2600,2605),HISTORIES))
        for w in worlds:old.verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
        assert len(rs)==240 and {(r['seed'],r['history'],r['proposal_seed'],r['policy']) for r in rs}==set(itertools.product(range(2600,2605),HISTORIES,(2600,2601),POLICIES))
        for examined,r in enumerate(rs,1):
            verify_run(r,ws[r['seed'],r['history']])
            if examined%8==0:print(f'{examined}/240 independently reconstructed',flush=True)
        verify_summary(rs,data['summary']);verify_totals(rs,worlds,data['totals']);assert data['elapsed_seconds']<900
        result=dict(status='pass',runs=240,empirical_pass=data['summary']['empirical_pass'],elapsed_seconds=time.monotonic()-start,**{k+'_sha256':hashlib.sha256((out/n).read_bytes()).hexdigest() for k,n in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
    except BaseException as exc:
        (out/'audit-failed.json').write_text(json.dumps(dict(status='failed',error=repr(exc),examined=examined,elapsed_seconds=time.monotonic()-start),indent=2)+'\n');raise
    finally:signal.alarm(0)
if __name__=='__main__':main()
