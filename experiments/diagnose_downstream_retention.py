"""Read-only diagnosis of saved 034 predictors; no learner replay or fitting."""
import gzip, hashlib, itertools, json, math
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]
CONTEXTS=list(itertools.product(range(4),range(4),range(2)))

def main():
    source=ROOT/'results/coordinated-steering-v1'
    manifest=json.loads((source/'manifest.json').read_text())
    for p,d in manifest.items():assert hashlib.sha256((ROOT/p).read_bytes()).hexdigest()==d,p
    worlds={(w['seed'],w['branch']):w for w in json.loads((source/'worlds.json').read_text())}
    with gzip.open(source/'runs.jsonl.gz','rt') as f:rs=[json.loads(line) for line in f]
    records=[]
    for r in rs:
        if r['policy'] not in ('P','D') or r['history']=='stable':continue
        w=worlds[r['seed'],r['history']]
        for e,i in zip(r['evaluations'],r['inspections']):
            if not 512<=e['tick']<=1536:continue
            losses={}
            for label in ('original','changed'):
                forms=[x.copy() for x in w['forms']];q=w['affected']
                if label=='changed':forms[q]=w['alternative'] if r['history']=='forms' else [1-x for x in forms[q]]
                ys=[forms[0][x]^forms[1][y]^a for x,y,a in CONTEXTS]
                losses[label]=mean(-.9*math.log(p[2] if y else 1-p[2])-.1*math.log(1-p[2] if y else p[2]) for p,y in zip(e['predictions'],ys))
            records.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],history=r['history'],policy=r['policy'],tick=e['tick'],loss=losses,mass=i['evidence_mass'],partitions=e['partitions'],spec=e['spec'],local_exact=e['local_exact'],valid=e['valid']))
    groups=[]
    for h in ('forms','repeated'):
        for p in ('P','D'):
            for t in (512,640,768,1024,1088,1152,1280,1536):
                xs=[x for x in records if (x['history'],x['policy'],x['tick'])==(h,p,t)]
                groups.append(dict(history=h,policy=p,tick=t,loss={k:mean(x['loss'][k] for x in xs) for k in ('original','changed')},mass={k:[mean(x['mass'][k][j] for x in xs) for j in range(3)] for k in ('fast','slow')},local_exact=[sum(x['local_exact'][j] for x in xs) for j in range(2)],raw_interfaces=sum(2 in x['spec'] for x in xs),valid=sum(x['valid'] for x in xs)))
    paired=[]
    for h in ('forms','repeated'):
        for seed,ps in sorted({(x['seed'],x['proposal_seed']) for x in records}):
            rows={p:{x['tick']:x for x in records if (x['history'],x['seed'],x['proposal_seed'],x['policy'])==(h,seed,ps,p)} for p in ('P','D')}
            ticks=sorted(rows['P'])
            paired.append(dict(history=h,seed=seed,proposal_seed=ps,first_predictive_divergence=next((t for t in ticks if abs(rows['P'][t]['loss']['original']-rows['D'][t]['loss']['original'])>1e-12),None),partition_different_ticks=[t for t in ticks if rows['P'][t]['partitions']!=rows['D'][t]['partitions']],interface_different_ticks=[t for t in ticks if rows['P'][t]['spec']!=rows['D'][t]['spec']]))
    out=ROOT/'results/downstream-retention-diagnosis';out.mkdir(exist_ok=False)
    result=dict(status='completed',fresh_labels=0,training_presentations=0,stored_prediction_loss_terms=len(records)*32*2,groups=groups,paired=paired,records=records,source_hashes={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (source/'manifest.json',source/'runs.jsonl.gz',source/'worlds.json')})
    (out/'diagnosis.json').write_text(json.dumps(result,indent=2)+'\n')
    for g in groups:
        if g['tick'] in (1024,1088,1280,1536):print(g)
    print('different partitions',sum(bool(x['partition_different_ticks']) for x in paired),'different interfaces',sum(bool(x['interface_different_ticks']) for x in paired))
if __name__=='__main__':main()
