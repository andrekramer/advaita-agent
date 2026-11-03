"""032 post-audit reporting and saved-state-only refit diagnostic.

This diagnostic was added after outcomes. It cannot change frozen gates and
performs no new learning, selection or label generation.
"""
import copy,gzip,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT),str(ROOT/'experiments'),str(ROOT/'checks')]
from advaita.continuing import ContinuingLearner
from introspection import grid
from memory_control_reference import local_fit,upper_fit,lp,up
from audit_nested_abstractions import close

def main():
    out=ROOT/'results/introspection-v1';audit=json.loads((out/'audit.json').read_text());assert audit['status']=='pass'
    with gzip.open(out/'runs.jsonl.gz','rt') as f:records=[json.loads(x) for x in f]
    cases=[]
    for r in records:
        failures=[m for m,f in zip(r['metrics']['forecasts'],r['decision']['forecasts']) if m['eligible'] and m['immediate_actual']!=f['immediate']]
        if not failures:continue
        a=ContinuingLearner.restore(json.dumps(r['checkpoint']));before=grid(a);a.engine.refit();after=grid(a)
        # Independent fit from already-audited evidence, without any intervention.
        st=r['checkpoint']['engine'];raw=[[[f[k]+s[k] for k in (0,1)] for f,s in zip(fast,slow)] for fast,slow in zip(st['fast'],st['slow'])]
        locals_=[local_fit(m['partition'],raw[j]) for j,m in enumerate(st['locals'])];upper=upper_fit(st['upper']['spec'],raw[2],locals_)
        independent=[[lp(locals_[0],x),lp(locals_[1],y),up(upper,locals_,[x,y],act)] for x in range(4) for y in range(4) for act in range(2)]
        close(after,independent)
        for failure in failures:
            j=failure['channel'];immediate=r['branches'][str(j)]['immediate']
            cases.append(dict(seed=r['seed'],history=r['history'],proposal_seed=r['proposal_seed'],tick=r['tick'],channel=j,
                review_actions=[c['action'] for c in r['packet']['observed']['last_review']['channels']],
                upper_spec=st['upper']['spec'],control_delta=failure['immediate_delta'],
                refit_only_delta=max(abs(p[2]-q[2]) for p,q in zip(before,after)),
                control_vs_refit_delta=max(abs(p[2]-q[2]) for p,q in zip(immediate,after)),
                future_composite_gain=failure['gain'],
                future_predictions_identical=all(p[2]==q[2] for p,q in zip(r['branches'][str(j)]['predictions'][:256],r['branches']['none']['predictions'][:256]))))
    assert all(c['control_vs_refit_delta']<=1e-12 and c['future_predictions_identical'] for c in cases)
    report=dict(scope='Post-outcome saved-state diagnostic; no new labels or changed gates',cases=cases,
        independent_refit_verified=True,new_labels=0,new_learning_runs=0,
        report_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/'diagnostics.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
