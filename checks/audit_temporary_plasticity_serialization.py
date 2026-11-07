"""035 audit supplement: reproduce serialized controller loss exactly.

Frozen auditor uses -log1p(-p) while the frozen controller serializes -log(1-p).
They agree numerically but can differ by one ulp, changing a checkpoint hash.
Only the controller replay's loss operation changes here. Learning arithmetic,
worlds, outcome measurements, thresholds, guards and original sources are intact.
"""
import gzip,hashlib,json,math,time,types
from pathlib import Path
import audit_temporary_plasticity as frozen
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/temporary-plasticity-v1'


def serialized_loss(p,y):
    return -math.log(p if y else 1-p)


replay=types.FunctionType(frozen.verify_run.__code__,dict(frozen.verify_run.__globals__,logloss=serialized_loss),argdefs=frozen.verify_run.__defaults__)
main_replay=types.FunctionType(frozen.main.__code__,dict(frozen.main.__globals__,verify_run=replay))


def main():
    assert not (OUT/'audit.json').exists()
    start=time.monotonic();before={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in ('results.json','worlds.json','runs.jsonl.gz','manifest.json')}
    worlds={(w['seed'],w['branch']):w for w in json.loads((OUT/'worlds.json').read_text())}
    maximum=0.;minimum_margin=math.inf;count=0;changed=0
    with gzip.open(OUT/'runs.jsonl.gz','rt') as f:
        for line in f:
            r=json.loads(line);w=worlds[r['seed'],r['history']]
            for d in r['diagnostics']:
                rows=w['selection'][str(d['tick'])]
                exact=sum(serialized_loss(p,row['y']) for p,row in zip(d['predictions'],rows))/len(rows)
                stable=sum(frozen.logloss(p,row['y']) for p,row in zip(d['predictions'],rows))/len(rows)
                assert exact==d['loss'];maximum=max(maximum,abs(exact-stable));minimum_margin=min(minimum_margin,abs(exact-.55));changed+=int((exact<=.55)!=(stable<=.55));count+=1
    assert changed==0 and maximum<1e-12
    supplement=dict(status='arithmetic_checked_pending_full_replay',reason='Serialized log versus log1p rounding; no learning or empirical changes',maximum_loss_difference=maximum,minimum_threshold_margin=minimum_margin,diagnostic_batches=count,changed_adequacy_decisions=changed,output_hashes=before,supplement_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (OUT/'audit-serialization-supplement.json').write_text(json.dumps(supplement,indent=2)+'\n')
    print(json.dumps(supplement,indent=2),flush=True)
    try:
        main_replay()
        assert before=={name:hashlib.sha256((OUT/name).read_bytes()).hexdigest() for name in before}
        supplement.update(status='pass',elapsed_seconds=time.monotonic()-start,full_replay_runs=250)
    except BaseException as exc:
        supplement.update(status='failed',error=repr(exc),elapsed_seconds=time.monotonic()-start)
        raise
    finally:(OUT/'audit-serialization-supplement.json').write_text(json.dumps(supplement,indent=2)+'\n')
if __name__=='__main__':main()
