"""R0: exact B64 compatibility against the 30 saved integrated 019 traces."""
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
import structural_consolidation as old
from advaita.explicit_roles import CompatibilityLearner


def main():
    out=ROOT/'results/explicit-roles-r0';out.mkdir(exist_ok=True)
    path=out/'compatibility.json'
    if path.exists(): raise FileExistsError(path)
    start=time.monotonic();records=[]
    def timeout(*_): raise TimeoutError('900-second saved-replay limit')
    signal.signal(signal.SIGALRM,timeout);signal.alarm(900)
    folder=ROOT/'results/consolidated-recovery-v1'
    for name,digest in json.loads((ROOT/'results/memory-selection-v1/manifest.json').read_text()).items():
        assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    worlds={(w['seed'],w['branch']):w for w in json.loads((folder/'worlds.json').read_text())}
    with gzip.open(folder/'runs.jsonl.gz','rt') as f: saved=[json.loads(line) for line in f if line.strip()]
    selected=[r for r in saved if r['variant']=='integrated'];assert len(selected)==30
    globals_=dict(old.run.__globals__,StructuralLearner=CompatibilityLearner)
    run=types.FunctionType(old.run.__code__,globals_,argdefs=old.run.__defaults__)
    try:
        for i,expected in enumerate(selected,1):
            actual,checkpoint=run(worlds[expected['seed'],expected['branch']],'integrated',expected['proposal_seed'],measure=False)
            expected={k:v for k,v in expected.items() if k not in ('recovery','metrics','checkpoint_file')}
            assert actual==expected,(i,[k for k in actual if actual[k]!=expected.get(k)])
            digest=hashlib.sha256(checkpoint.encode()).hexdigest()
            assert digest==expected['checkpoint_sha256']
            records.append(dict(seed=actual['seed'],branch=actual['branch'],proposal_seed=actual['proposal_seed'],checkpoint_sha256=digest))
            if i%5==0: print(f'{i}/30 complete original traces and checkpoint bytes match',flush=True)
        result=dict(status='pass',runs=30,new_labels=0,replayed_labels=sum(r['costs']['feedback_labels'] for r in selected),records=records)
    except Exception as exc:
        result=dict(status='failed',error=repr(exc),runs=len(records),records=records);raise
    finally:
        signal.alarm(0)
        result.update(elapsed_seconds=time.monotonic()-start,
            tested_sources={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ('advaita/explicit_roles.py','checks/roles_compatibility.py')})
        path.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
