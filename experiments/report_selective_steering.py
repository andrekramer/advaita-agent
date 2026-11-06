"""033 descriptive tables from audited saved runs; no new learning or criteria."""
import gzip,hashlib,json
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'results/selective-steering-v1';audit=json.loads((out/'audit.json').read_text());assert audit['status']=='pass'
    with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
    groups=[]
    for history in ('stable','forms','repeated'):
        for policy in ('legacy','refreshed','lock_only','plastic_only','selective','swapped'):
            group=[r for r in rs if r['history']==history and r['policy']==policy]
            local={role:mean(r['metrics']['expected']['active'][r['metrics'][role]] for r in group) for role in ('protected','flexible')}
            correctness={role:mean(r['metrics']['active_local_correct'][r['metrics'][role]] for r in group) for role in ('protected','flexible')}
            endpoints={}
            for t in (512,640,1024,1536,2048):
                ev=[next(e for e in r['evaluations'] if e['tick']==t) for r in group]
                endpoints[t]=dict(full_valid=sum(e['valid'] for e in ev),**{role:sum(e['local_exact'][r['metrics'][role]] for r,e in zip(group,ev)) for role in ('protected','flexible')})
            groups.append(dict(history=history,policy=policy,active_local_loss=local,active_form_correctness=correctness,endpoints=endpoints))
    summary=json.loads((out/'results.json').read_text())['summary'];violations=[]
    for h in ('stable','forms','repeated'):
        for window in ('returning','later')+(('active',) if h=='stable' else ()):
            for j in range(3):
                ps=[p for p in summary['paired'] if p['history']==h];xs=[p['costs'][window][j] for p in ps]
                if mean(xs)>.02 or max(xs)>.10:violations.append(dict(history=h,window=window,channel=j,mean_cost=mean(xs),maximum_cost=max(xs),individual_failures=[dict(seed=p['seed'],proposal_seed=p['proposal_seed'],cost=x) for p,x in zip(ps,xs) if x>.10]))
    result=dict(scope='Descriptive summaries of audited033 traces; not new success criteria',groups=groups,guard_violations=violations,new_learning_runs=0,
        extra_slow_decay_cell_visits=90*512*4,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),audited_runs_sha256=audit['runs_sha256'])
    (out/'descriptive.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Saved role-specific losses, release endpoints, failed guards and additional decay work.')
if __name__=='__main__':main()
