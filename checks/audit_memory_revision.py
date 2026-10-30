"""027 independent replay, summary and resource verification; no policy imports."""
import gzip
import hashlib
import itertools
import json
from pathlib import Path
import signal
import time
import types
from audit_nested_abstractions import close
import audit_memory_control_v2 as prior
from memory_revision_reference import RevisionReference
ROOT=Path(__file__).resolve().parents[1]
POLICIES=('baseline','fast','selective','relaxed','weaken','combined','uniform')
BRANCHES=prior.BRANCHES
verify_run=types.FunctionType(prior.verify_run.__code__,dict(prior.verify_run.__globals__,Reference=RevisionReference,POLICIES=POLICIES),argdefs=prior.verify_run.__defaults__)


def verify_summary(runs,saved):
    pairs=sorted({(r['seed'],r['proposal_seed']) for r in runs});assert len(pairs)==10
    lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r for r in runs}
    def get(s,q,h,p):return lookup[s,q,h,p]['metrics']
    assert len(saved['groups'])==35
    for g,(h,p) in zip(saved['groups'],itertools.product(BRANCHES,POLICIES)):
        rows=[lookup[s,q,h,p] for s,q in pairs];ms=[r['metrics'] for r in rows]
        expected=dict(branch=h,policy=p,runs=10)
        for key in ['transfer_valid','final_valid','gap_valid','final_structure']:expected[key]=sum(m[key] for m in ms)
        for key in ['gap_loss','structure_errors','transfers','transferred_mass']:expected[key]=sum(m[key] for m in ms)/10
        for name in ['observed','latent']:
            expected[name]={}
            for window in prior.WINDOWS:
                vals=[m[name][window] for m in ms if m[name][window] is not None]
                expected[name][window]=sum(vals)/len(vals) if vals else None
        expected.update(recovery_censored=sum(m['recovery'] is None for m in ms),recoveries=[m['recovery'] for m in ms],
            weakenings=sum(r['costs'].get('weakenings',0) for r in rows),removed_mass=sum(r['costs'].get('removed_mass',0) for r in rows))
        close(g,expected)
    contrasts=[('combined','relaxed'),('weaken','selective'),('combined','selective'),('relaxed','selective'),('combined','uniform'),('combined','fast'),('combined','baseline')]
    expected_pairs=[]
    for a,b in contrasts:
        for s,q in pairs:
            for h in BRANCHES:
                x,y=get(s,q,h,a),get(s,q,h,b)
                row=dict(candidate=a,control=b,seed=s,proposal_seed=q,branch=h,gap_cost=x['gap_loss']-y['gap_loss'])
                for name in ['observed','latent']:row[name+'_cost']={k:None if x[name][k] is None else x[name][k]-y[name][k] for k in prior.WINDOWS}
                expected_pairs.append(row)
    close(saved['paired'],expected_pairs)
    revision=[];selection=[]
    for s,q in pairs:
        revision.append(dict(seed=s,proposal_seed=q,gain=sum(get(s,q,h,'relaxed')['observed']['early']-get(s,q,h,'combined')['observed']['early'] for h in ['reversal','remap'])/2))
        selection.append(dict(seed=s,proposal_seed=q,gain=sum(get(s,q,h,'uniform')['observed'][k]-get(s,q,h,'combined')['observed'][k] for h,k in [('stable','whole'),('return','early'),('burst','recovery')])/3))
    close(saved['revision_pairs'],revision);close(saved['selection_pairs'],selection)
    flags=dict(revision_gain=sum(r['gain'] for r in revision)/10>=.02,revision_pairs=sum(r['gain']>0 for r in revision)>=8,
        final_validity=all(sum(get(s,q,h,'combined')['final_valid'] for s,q in pairs)>=8 for h in BRANCHES),
        gap_validity=sum(get(s,q,'return','combined')['gap_valid'] for s,q in pairs)>=8,
        preservation_mean=True,preservation_worst=True,gap_cost=True,revision_mean_cost=True,revision_worst=True,recovery_censoring=True)
    for control in ['selective','relaxed']:
        for history,window in [('stable','whole'),('return','early'),('burst','burst'),('burst','recovery')]:
            for measure in ['observed','latent']:
                costs=[get(s,q,history,'combined')[measure][window]-get(s,q,history,control)[measure][window] for s,q in pairs]
                if sum(costs)/10>.02:flags['preservation_mean']=False
                if measure=='observed' and max(costs)>.10:flags['preservation_worst']=False
        if sum(get(s,q,'return','combined')['gap_loss']-get(s,q,'return',control)['gap_loss'] for s,q in pairs)/10>.02:flags['gap_cost']=False
    for history in ['reversal','remap']:
        for measure in ['observed','latent']:
            costs=[get(s,q,history,'combined')[measure]['early']-get(s,q,history,'relaxed')[measure]['early'] for s,q in pairs]
            if sum(costs)/10>.02:flags['revision_mean_cost']=False
            if measure=='observed' and max(costs)>.10:flags['revision_worst']=False
        if sum(get(s,q,history,'combined')['recovery'] is None for s,q in pairs)>sum(get(s,q,history,'relaxed')['recovery'] is None for s,q in pairs):flags['recovery_censoring']=False
    close(saved['gates'],flags);assert saved['primary_pass']==all(flags.values())
    selection_flags=dict(mean_gain=sum(r['gain'] for r in selection)/10>=.01,positive_pairs=sum(r['gain']>0 for r in selection)>=8)
    close(saved['selectivity_gates'],selection_flags);assert saved['selectivity_pass']==all(selection_flags.values())
    env=[]
    for seed in sorted({s for s,q in pairs}):
        for h in BRANCHES:
            for p in POLICIES:
                ms=[get(s,q,h,p) for s,q in pairs if s==seed]
                env.append(dict(seed=seed,branch=h,policy=p,whole_loss=sum(m['observed']['whole'] for m in ms)/len(ms),early_loss=sum(m['observed']['early'] for m in ms)/len(ms)))
    close(saved['environment_means'],env)


def totals(runs,worlds):
    total=dict(runs=len(runs),generated_labels=0,used_labels=0,candidate_fits=0,active_fits=0,probe_fits=0,raw_bin_visits=0,
        scoring_queries=0,main_predictions=0,evaluation_predictions=0,slow_probe_predictions=0,oracle_context_queries=0,legacy_auxiliary_predictions=0,reused_grid_predictions=0)
    for w in worlds:
        total['generated_labels']+=sum(len(x) for x in w['local_main'])+sum(len(x) for b in w['local_selection'] for x in b)+len(w['composition'])
        total['generated_labels']+=3*(sum(x is not None for x in w['main'])+sum(len(x) for x in w['selection'].values()))
    lookup={(w['seed'],w['branch']):w for w in worlds}
    for r in runs:
        c=r['costs'];total['used_labels']+=c['feedback_labels']
        if r['policy']=='baseline':
            total['candidate_fits']+=c['candidate_fits']+c['upper_candidate_fits'];total['scoring_queries']+=c['scoring_queries']
            extra=r['legacy']['endpoints'];total['reused_grid_predictions']+=32*sum(x is None for x in lookup[r['seed'],r['branch']]['main'][63::64])
        else:
            ac=r['acquisition']['costs'];total['candidate_fits']+=c['candidate_fits']+ac['candidate_fits'];total['scoring_queries']+=c['scoring_queries']+ac['scoring_queries']
            for k in ['active_fits','probe_fits','raw_bin_visits']:total[k]+=c[k]
            total['slow_probe_predictions']+=40*len(r['snapshots']);extra=[r['acquisition']['transfer']]
        total['legacy_auxiliary_predictions']+=sum(e['contexts'] for e in extra)
        total['main_predictions']+=3*sum(p is not None for p in r['predictions'])
        total['evaluation_predictions']+=sum(e['contexts'] for e in [r['transfer']]+r['evaluations'])
        for e in [r['transfer']]+r['evaluations']+extra:total['oracle_context_queries']+=32*(1+len(e['removal_costs'])+len(e['raw_addition_gains']))
    return total


def main():
    out=ROOT/'results/memory-revision-v1';started=time.monotonic()
    def timeout(*_):raise TimeoutError('900-second revision audit ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        data=json.loads((out/'results.json').read_text());manifest=json.loads((out/'manifest.json').read_text())
        assert data['status']=='completed_pending_audit' and data['hashes']==manifest
        for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
        worlds=json.loads((out/'worlds.json').read_text());lookup={(w['seed'],w['branch']):w for w in worlds}
        assert len(worlds)==25 and set(lookup)==set(itertools.product(range(1700,1705),BRANCHES))
        for w in worlds:assert not w['small'];prior.verify_world(w)
        with gzip.open(out/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
        assert len(runs)==350 and {(r['seed'],r['proposal_seed'],r['branch'],r['policy']) for r in runs}==set(itertools.product(range(1700,1705),(1700,1701),BRANCHES,POLICIES))
        for i,r in enumerate(runs,1):
            with gzip.open(out/r['checkpoint_file'],'rt') as f:c=json.load(f)
            verify_run(r,lookup[r['seed'],r['branch']],c)
            if i%25==0:print(f'{i}/350 independently reconstructed',flush=True)
        verify_summary(runs,data['summary']);total=totals(runs,worlds);close(total,data['totals'])
        for k,v in dict(runs=350,generated_labels=135040,used_labels=1890560,main_predictions=1021440,evaluation_predictions=232400,
                        slow_probe_predictions=24000,legacy_auxiliary_predictions=12000,reused_grid_predictions=7680).items():assert total[k]==v,(k,total[k])
        for k,v in dict(candidate_fits=350000,scoring_queries=20000000,raw_bin_visits=100000000,oracle_context_queries=1300000).items():assert total[k]<=v
        fixtures=[json.loads(p.read_text()) for p in sorted((ROOT/'results/memory-revision-fixtures').glob('attempt-*.json'))]
        assert fixtures[-1]['status']=='pass' and sum(x['charged_labels'] for x in fixtures)<=5000 and data['elapsed_seconds']<900
        result=dict(status='pass',runs=350,independently_replayed_labels=total['used_labels'],primary_pass=data['summary']['primary_pass'],
            selectivity_pass=data['summary']['selectivity_pass'],elapsed_seconds=time.monotonic()-started,
            **{name+'_sha256':hashlib.sha256((out/file).read_bytes()).hexdigest() for name,file in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]})
        (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
    finally:signal.alarm(0)

if __name__=='__main__':main()
