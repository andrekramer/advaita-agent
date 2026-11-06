"""034 descriptive saved-result tables; no new trials or success criteria."""
import gzip,hashlib,json
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'results/coordinated-steering-v1';audit=json.loads((out/'audit.json').read_text());assert audit['status']=='pass'
    with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(x) for x in f]
    summary=json.loads((out/'results.json').read_text())['summary'];groups=[]
    for history in ('stable','forms','repeated'):
        for policy in ('U','P','L','D','C'):
            group=[r for r in rs if r['history']==history and r['policy']==policy]
            groups.append(dict(history=history,policy=policy,
                active_local_loss={role:mean(r['metrics']['expected']['active'][r['metrics'][role]] for r in group) for role in ('protected','flexible')},
                full_valid_endpoints={t:sum(next(e for e in r['evaluations'] if e['tick']==t)['valid'] for r in group) for t in (512,640,1024,1536,2048)}))
    contrasts=[]
    for h in ('forms','repeated','pooled_changing'):
        paired=[r for r in summary['paired'] if r['history']!='stable' and (h=='pooled_changing' or r['history']==h)]
        for name in paired[0]['gains']:
            xs=[r['gains'][name] for r in paired]
            contrasts.append(dict(history=h,comparison=name,expected_gain=mean(xs),observed_gain=mean(r['observed_gains'][name] for r in paired),positive=sum(x>1e-12 for x in xs),negative=sum(x < -1e-12 for x in xs),ties=sum(abs(x)<=1e-12 for x in xs)))
    result=dict(scope='Descriptive extraction from audited034 results; no new criteria',groups=groups,contrasts=contrasts,failed_guards=[g for g in summary['guards'] if not g['passed']],new_learning_runs=0,
        report_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),audited_runs_sha256=audit['runs_sha256'])
    (out/'descriptive.json').write_text(json.dumps(result,indent=2)+'\n');print('Descriptive contrasts, endpoint and role-specific tables saved.')
if __name__=='__main__':main()
