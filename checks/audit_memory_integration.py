"""029 independent artifact/coverage audit, not a second learning replication."""
import gzip,hashlib,itertools,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'results/memory-integration-v1';source=ROOT/'results/memory-confirmation-v1'
    manifest=json.loads((out/'manifest.json').read_text())
    for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    data=json.loads((out/'compatibility.json').read_text());assert data['status']=='pass' and data['runs']==350 and data['new_labels']==0
    with gzip.open(source/'runs.jsonl.gz','rt') as f:old=[json.loads(line) for line in f]
    key=lambda r:(r['seed'],r['proposal_seed'],r['branch'],r['policy'])
    records={key(r):r for r in data['records']};assert len(records)==350 and set(records)=={key(r) for r in old}
    for r in old:
        row=records[key(r)];assert row['checkpoint_sha256']==r['checkpoint_sha256']
        with gzip.open(source/r['checkpoint_file'],'rb') as f:assert hashlib.sha256(f.read()).hexdigest()==row['checkpoint_sha256']
        assert row['predictions']==1280 and row['reviews']==(20 if r['branch'] in ('stable','burst') else 12)
        assert row['feedback_labels']==r['costs']['feedback_labels']
    assert data['replayed_labels']==1890560 and data['elapsed_seconds']<900
    assert json.loads((out/'fixtures.json').read_text())['status']=='pass'
    result=dict(status='pass',runs=350,new_labels=0,replayed_labels=1890560,compatibility_sha256=hashlib.sha256((out/'compatibility.json').read_bytes()).hexdigest())
    (out/'audit.json').write_text(json.dumps(result,indent=2)+'\n');print(result)
if __name__=='__main__':main()
