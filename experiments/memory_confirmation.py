"""028 fresh confirmation: measurement and orchestration only."""
import gzip
import hashlib
import json
from pathlib import Path
import signal
import sys
import time
import types
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'experiments')]
from advaita.memory_revision import RevisionLearner
from advaita.state import canonical
import memory_control_v2 as previous
from memory_confirmation_metrics import POLICIES,summarize,metrics
BRANCHES=previous.BRANCHES
generate=previous.generate
run=types.FunctionType(previous.run.__code__,dict(previous.run.__globals__,MemoryLearner=RevisionLearner,metrics=metrics),argdefs=previous.run.__defaults__)
FILES=('experiments/memory_confirmation.py','experiments/memory_confirmation_protocol.md',
 'experiments/memory_confirmation_metrics.py','checks/audit_memory_confirmation.py','checks/test_memory_confirmation.py',
 'experiments/report_memory_revision.py')
LIMITS=dict(candidate_fits=350000,scoring_queries=20000000,raw_bin_visits=100000000,oracle_context_queries=1300000)


def hashes():
    parent=ROOT/'results/memory-revision-v1'
    frozen=json.loads((parent/'manifest.json').read_text())
    for p,d in frozen.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    files=set(frozen)|set(FILES)
    files.update(str(p.relative_to(ROOT)) for p in parent.rglob('*') if p.is_file())
    files.update(str(p.relative_to(ROOT)) for p in (ROOT/'results/memory-confirmation-fixtures').glob('attempt-*.json'))
    return {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sorted(files)}


def main():
    fixtures=[json.loads(p.read_text()) for p in sorted((ROOT/'results/memory-confirmation-fixtures').glob('attempt-*.json'))]
    assert fixtures and fixtures[-1]['status']=='pass' and sum(x['new_learning_labels'] for x in fixtures)==0
    for p,d in fixtures[-1]['sources'].items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    out=ROOT/'results/memory-confirmation-v1';out.mkdir(exist_ok=False);(out/'checkpoints').mkdir()
    provenance=hashes();(out/'manifest.json').write_text(json.dumps(provenance,indent=2)+'\n')
    started=time.monotonic();worlds=[];runs=[]
    def timeout(*_):raise TimeoutError('900-second confirmation benchmark ceiling')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    try:
        for seed in range(1800,1805):
            for branch in BRANCHES:
                w=generate(seed,branch);worlds.append(w);(out/'worlds.json').write_text(json.dumps(worlds)+'\n')
                for ps in (1800,1801):
                    for policy in POLICIES:
                        r,c=run(w,policy,ps);path=f'checkpoints/{seed}-{branch}-{ps}-{policy}.json.gz'
                        with gzip.open(out/path,'wt') as f:f.write(c)
                        r['checkpoint_file']=path;runs.append(r)
                        with gzip.open(out/'runs.jsonl.gz','at') as f:f.write(canonical(r)+'\n')
                print(f'{seed} {branch}: {len(runs)}/350 saved',flush=True)
        assert hashes()==provenance;total=previous.totals(runs,worlds)
        for k,v in LIMITS.items():assert total[k]<=v,(k,total[k])
        assert total['runs']==350 and total['generated_labels']==135040 and total['used_labels']==1890560
        result=dict(status='completed_pending_audit',summary=summarize(runs),totals=total,hashes=provenance,elapsed_seconds=time.monotonic()-started)
        (out/'results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['summary']['gates'],indent=2))
    except BaseException as exc:
        (out/'incomplete.json').write_text(json.dumps(dict(error=repr(exc),completed_runs=len(runs),elapsed_seconds=time.monotonic()-started),indent=2)+'\n');raise
    finally:signal.alarm(0)

if __name__=='__main__':main()
