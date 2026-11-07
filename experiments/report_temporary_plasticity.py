"""Report study 035 only after independent audit; no training or selection."""
import gzip,hashlib,itertools,json,math
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'results/temporary-plasticity-v1';a=json.loads((out/'audit.json').read_text());d=json.loads((out/'results.json').read_text());assert a['status']=='pass'
    supplement=json.loads((out/'audit-serialization-supplement.json').read_text());assert supplement['status']=='pass'
    for key,name in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]:assert hashlib.sha256((out/name).read_bytes()).hexdigest()==a[key+'_sha256']
    with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(line) for line in f]
    s=d['summary'];g=s['primary'];groups=s['groups']
    worlds={(w['seed'],w['branch']):w for w in json.loads((out/'worlds.json').read_text())}
    contexts=list(itertools.product(range(4),range(4),range(2)));snapshots=[]
    for h in ('forms','repeated'):
        for policy in ('P','D128','D512','G'):
            xs=[];masses=[];raw=0
            for r in rs:
                if (r['history'],r['policy'])!=(h,policy):continue
                w=worlds[r['seed'],h];e=next(e for e in r['evaluations'] if e['tick']==1024);i=next(i for i in r['inspections'] if i['tick']==1024)
                targets=[w['forms'][0][x]^w['forms'][1][y]^a for x,y,a in contexts]
                xs.append(mean(-.9*math.log(ps[2] if y else 1-ps[2])-.1*math.log(1-ps[2] if y else ps[2]) for ps,y in zip(e['predictions'],targets)))
                masses.append(i['evidence_mass']['slow'][2]);raw+=2 in e['spec']
            snapshots.append(dict(history=h,policy=policy,original_map_loss=mean(xs),composite_slow_mass=mean(masses),raw_interfaces=raw))
    desc=dict(closure_ticks={h:{str(t):sum(r['metrics']['closed_at']==t for r in rs if r['history']==h and r['policy']=='G') for t in range(640,1025,64)} for h in ('stable','forms','repeated','forms_persistent','repeated_persistent')},guard_failures=[x for x in g['preservation_guards'] if not x['passed']],adaptation_failures=[x for x in g['adaptation_guards'] if not x['passed']])
    desc['posthoc_1024_snapshots']=snapshots
    desc['posthoc_stored_prediction_loss_terms']=80*32
    text=['# 035 — temporary downstream plasticity','', 'Completed 2026-11-06. All **250 runs independently reconstructed**. The primary full empirical criterion **'+('passed' if g['empirical_pass'] else 'failed')+'**. The original default is unchanged.','',
          '## Primary outcome','',f"G active expected composite gain over protection-only P: **{g['active_mean_gain']:.6f} nats**, positive in **{g['active_positive']}/40** changing pairs. Early-return gain over long-boost D512: **{g['early_mean_gain']:.6f} nats**, positive in **{g['early_positive']}/20** returning pairs.",'',
          '| Prespecified criterion | Pass |','| --- | --- |']
    text += [f'| {k} | {v} |' for k,v in g['gates'].items()]
    text += ['', '## Expected composite loss and endpoint validity','', 'Each row averages ten paired runs. Lower loss is better. Early-return is a post-release window for persistent tasks and a control window for stable tasks. Validity is a final snapshot, not a measure of recovery speed.','', '| History | Policy | Active | Early return/post-release | Whole return/post-release | Later | Final valid | Mean boost ticks |','| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for x in groups:text.append(f"| {x['history']} | {x['policy']} | {x['expected']['active'][2]:.6f} | {x['expected']['early_return'][2]:.6f} | {x['expected']['returning'][2]:.6f} | {x['expected']['later'][2]:.6f} | {x['final_valid']}/10 | {x['mean_duration']:.1f} |")
    text += ['', '## Closure and fixed-pulse comparisons','', '| History | G closures (tick: count) |','| --- | --- |']
    for h,ticks in desc['closure_ticks'].items():text.append('| '+h+' | '+', '.join(f'{t}: {n}' for t,n in ticks.items() if n)+' |')
    text+=['','Closure at 1024 is recorded as the supplied ceiling, even if the last batch also meets the adequacy condition. Opening at 512, the ceiling, and the protected role are supplied. This is a fixed evidence-responsive rule, not learned control.','','| Secondary pulse | Full bundle | Active gain over P | Early-return gain over D512 |','| --- | --- | ---: | ---: |']
    for p,x in s['secondary'].items():text.append(f"| {p} | {x['empirical_pass']} | {x['active_mean_gain']:.6f} ({x['active_positive']}/40 positive) | {x['early_mean_gain']:.6f} ({x['early_positive']}/20 positive) |")
    text += ['','| History | G compared with | Active gain | Early-return gain | Later gain |','| --- | --- | ---: | ---: | ---: |']
    for x in s['G_vs_fixed']:text.append(f"| {x['history']} | {x['control']} | {x['gain']['active']:.6f} | {x['gain']['early_return']:.6f} | {x['gain']['later']:.6f} |")
    text += ['', 'Positive here means lower loss for G. These comparisons are not exposure-matched. A secondary pulse cannot become a retrospective primary success.','', '## Guard failures','', '| Kind | History | Comparator | Window | Channel | Mean cost | Worst pair cost |','| --- | --- | --- | --- | ---: | ---: | ---: |']
    for x in desc['adaptation_failures']:text.append(f"| Adaptation | {x['history']} | D512 | active | 2 | {x['mean_cost']:.6f} | {x['max_cost']:.6f} |")
    for x in desc['guard_failures']:text.append(f"| Preservation | {x['history']} | {x['control']} | {x['window']} | {x['channel']} | {x['mean_cost']:.6f} | {x['max_cost']:.6f} |")
    if not desc['adaptation_failures'] and not desc['guard_failures']:text.append('| None | | | | | | |')
    text += ['', '## Interpretation and next decision', '',
             'The evidence-based closure retained the active adaptation benefit but did not improve return. The shortest pulse improved pooled early return modestly, below the declared .02-nat threshold, and exceeded the allowed adaptation cost in both reversal histories. No tested duration policy passed the full bundle. Do not promote the controller or tune its threshold on these outcomes.', '',
             'Restoring a slower decay rate does not restore earlier knowledge. It can also make recently acquired evidence more persistent. That is a candidate explanation for slower recovery here, not an isolated causal finding. In a post-outcome descriptive check of saved tick-1024 predictors, G had more composite slow evidence than D512 and slightly better original-map predictions, yet subsequently recovered more slowly. An endpoint snapshot therefore does not determine the recovery trajectory. Upper search and migration remain possible contributors.', '',
             '| Returning history | Policy | Original-map loss at 1024 | Composite slow mass | Raw interfaces |',
             '| --- | --- | ---: | ---: | ---: |']
    for x in snapshots:text.append(f"| {x['history']} | {x['policy']} | {x['original_map_loss']:.6f} | {x['composite_slow_mass']:.3f} | {x['raw_interfaces']}/10 |")
    text += ['', 'This descriptive check only rescores saved predictions; it adds no training or fresh labels and did not select a controller. Next, prepare the separate one-slot preserved-predictor study contemplated by the plan: matched no-archive/shadow/use conditions, semantic compatibility, fresh evidence admission and defined persistence through refits. That study is not implemented or launched here.', '']
    text += ['', '## Integrity and scope','',f"Runner {d['elapsed_seconds']:.1f}s; independent auditor {a['elapsed_seconds']:.1f}s. All resource caps passed. {len(d['hashes'])} frozen dependency files remain unchanged.",'',
             f"The frozen auditor first stopped at run 115 on a checkpoint hash: its log1p arithmetic differed from the runtime log arithmetic by at most {supplement['maximum_loss_difference']:.3g} nats. The failed attempt is preserved. A separate serialization supplement uses the runtime operation only for the controller loss being serialized; it leaves all learning, world and outcome logic intact. No adequacy decision changes across {supplement['diagnostic_batches']} batches (nearest threshold margin {supplement['minimum_threshold_margin']:.6g}). The supplement then independently replays all 250 runs. No learner, frozen source, world or experiment result was changed. This is a disclosed post-outcome auditor correction.", '',
             'The auditor independently rebuilt worlds, controller decisions, every prediction/review, intermediate snapshot, final evidence state, checkpoint hashes, costs and outcome gates. Returning and persistent histories match through the intervention window. Results include all acquisitions and all pairs. No thresholds or durations were tuned after outcomes.','',
             'The 40 changing active-window records include 20 distinct return/persistent paired trajectories, duplicated before those histories diverge at 1025. Five environment seeds and two proposal seeds are correlated within histories; counts are descriptive, not independent statistical evidence. The misleading burst, supplied role, fixed opening/deadline, small discrete world family and one adequacy threshold limit the claim. No autonomous opening, archive integration, meta-learning or safety advantage was tested.','',
             'The first fixture attempt passed: 112640 reused-world training presentations, 6912 synthetic scalar presentations, no fresh random labels. The preceding diagnosis only rescored stored predictors. Fresh-run accounting:','']
    text += ['- '+k+': '+str(v) for k,v in d['totals'].items()]
    text += ['','Audit replay accounting is separate from training: the failed attempt examined 115 runs (1177600 replayed training presentations), and the full corrected audit examined 250 (2560000). The supplement also rescored 2000 saved diagnostic batches (64000 predictions), with no learning or new labels. The failed auditor did not persist exact elapsed time; its 900-second alarm did not fire.', '', 'Controller queries are additional to ordinary scoring; each composite query computes three scalar channels. Grid counts are contexts, each with three channels. Inherited acquisition evaluation is logged separately.','','[Frozen protocol](../../experiments/temporary_plasticity_protocol.md) · [Independent audit](audit.json) · [Results and all guards](results.json) · [Prior diagnosis](../downstream-retention-diagnosis/findings.md)','']
    (out/'descriptive.json').write_text(json.dumps(desc,indent=2)+'\n');(out/'findings.md').write_text('\n'.join(text))
    print(json.dumps(dict(gates=g['gates'],active_gain=g['active_mean_gain'],early_gain=g['early_mean_gain'],closure_ticks=desc['closure_ticks']),indent=2))
if __name__=='__main__':main()
