"""Post-outcome report and saved-trace diagnostics for study 036; no learning."""
import gzip,hashlib,json,math,sys
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'experiments'),str(ROOT)]
from preserved_prediction import target,HISTORIES


def main():
    out=ROOT/'results/preserved-prediction-v1';data=json.loads((out/'results.json').read_text());audit=json.loads((out/'audit.json').read_text());assert audit['status']=='pass'
    for k,n in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]:assert hashlib.sha256((out/n).read_bytes()).hexdigest()==audit[k+'_sha256']
    with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(line) for line in f]
    ws={(w['seed'],w['branch']):w for w in json.loads((out/'worlds.json').read_text())};s=data['summary'];diagnostics=[]
    for r in rs:
        if r['policy']!='recall' or r['history'] not in ('forms','repeated'):continue
        w=ws[r['seed'],r['history']];uses=[t for t,e in enumerate(r['prediction_events'],1) if 1025<=t<=1536 and e['source']=='archive']
        eligible=[e['tick'] for e in r['memory_events'] if 1025<=e['tick']<=1536 and e['eligible']];costs=[]
        for t in range(1537,2049):
            row=w['main'][t-1];y=target(w,row['x'],row['a'],t)
            loss=lambda p:-.9*math.log(p if y else 1-p)-.1*math.log(1-p if y else p)
            costs.append(loss(r['predictions'][t-1][2])-loss(r['active_predictions'][t-1][2]))
        diagnostics.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],history=r['history'],capture_confirmed=r['metrics']['confirmed'],first_eligible=eligible[0] if eligible else None,first_return_use=uses[0] if uses else None,early_uses=r['metrics']['uses_by_window']['early_return'],route_at_1536=next(e['route_after'] for e in r['memory_events'] if e['tick']==1536),cost_first64=mean(costs[:64]),cost_remainder=mean(costs[64:]),cost_whole_later=mean(costs)))
    desc=dict(status='descriptive_post_outcome',training_presentations=0,fresh_labels=0,late_prediction_pairs_rescored=20*512,records=diagnostics,summary=[dict(history=h,return_uses=sum(d['first_return_use'] is not None for d in diagnostics if d['history']==h),early_use_pairs=sum(d['early_uses']>0 for d in diagnostics if d['history']==h),routed_at_rechange=sum(d['route_at_1536'] for d in diagnostics if d['history']==h),first64_mean_cost=mean(d['cost_first64'] for d in diagnostics if d['history']==h),remaining448_mean_cost=mean(d['cost_remainder'] for d in diagnostics if d['history']==h)) for h in ('forms','repeated')])
    text=['# 036 — preserved prediction helps some returns, but recall remains unreliable','',
          'Completed 2026-11-06. All **180 runs passed independent reconstruction**. The full empirical criterion **'+('passed' if s['empirical_pass'] else 'failed')+'**. No default change or additional experiment.','',
          f"Recall reduced mean early-return expected composite loss by **{s['mean_gain']:.6f} nats**, with **{s['positive']}/20** improving pairs. The requirements were .02 nats and 14/20. Both returning histories improved on average, but the mean benefit and consistency requirements failed. A later reversal cost also exceeded the preservation limits.",'',
          '## What was tested','',
          'All three arms used the same continuing learner and downstream boost. A single predictor was nominated after review 384 and confirmed against two later fresh batches. Discard deleted it; shadow retained/scored it without deployment; recall could use its frozen numerical predictions after an adequate, improving fresh score and matching input meanings. Active learning continued unchanged. The archive could neither block an update nor be overwritten by ordinary refits.','',
          'This is a compositional output alternative, not restoration of the active learner or faster representation learning. Input meaning checks are strict; the stored predictor cannot silently reinterpret current category IDs. Admission lasts until the next review, with compatibility checked on each prediction.','',
          '## Outcomes','', '| Prespecified criterion | Pass |','| --- | --- |']
    text += [f'| {k} | {v} |' for k,v in s['gates'].items()]
    text += ['', '| History | Policy | Active loss | Early return/post-release | Whole return/post-release | Later | Deployed / active final valid |','| --- | --- | ---: | ---: | ---: | ---: | --- |']
    for g in s['groups']:text.append(f"| {g['history']} | {g['policy']} | {g['expected']['active'][2]:.6f} | {g['expected']['early_return'][2]:.6f} | {g['expected']['returning'][2]:.6f} | {g['expected']['later'][2]:.6f} | {g['final_valid']}/10 / {g['active_final_valid']}/10 |")
    text += ['', 'Losses are expected composite log loss; lower is better. Persistent and altered-return windows are not familiar returns. All three output channels and observed loss are retained in results.json.','',
          '## Preservation and actual recall','',
          'Every seed/proposal pair confirmed its snapshot, including all 20 familiar-return pairs. Shadow and discard produced exactly identical online predictions. Across all three arms, active predictions, ordinary reviews and final learning state were identical. The independent audit excludes archive/audit metadata when comparing that learning state. Thus measured differences come from routed predictions rather than selection blocking or extra training.','',
          '| History | Confirmed /10 | Eligible reviews | Admitted reviews | Actual archived main predictions | Blocked mid-interval predictions |','| --- | ---: | ---: | ---: | ---: | ---: |']
    for g in s['groups']:
        if g['policy']=='recall':text.append(f"| {g['history']} | {g['confirmed']} | {g['eligible_reviews']} | {g['admitted_reviews']} | {g['uses']} | {g['blocked']} |")
    text += ['', 'Permanent changes and altered-category returns produced no archive deployment and exactly matched their controls. This reflects exclusion by the supplied compatibility rule in these runs; it does not establish that loss-based admission alone rejects misleading memory. Stable tasks also sometimes used the frozen predictor, with small mean improvements and passing guards.','',
          '## What limited recall: post-outcome trace diagnosis','',
          'Capture did not limit this batch. Every familiar-return run eventually used its archive, but only six began early enough to improve the declared early-return window: four category-return pairs and two polarity-return pairs. These were exactly the six positive pairs. The other 14 tied in that window. Returning input meanings generally became compatible only after substantial active relearning; one polarity pair also waited a further review after first becoming eligible. Changing the primary window afterwards would conceal that delay.','',
          '| History | Pairs with early recall | Routed immediately before rechange | Mean cost, first 64 after rechange | Mean cost, remaining 448 |','| --- | ---: | ---: | ---: | ---: |']
    for g in desc['summary']:text.append(f"| {g['history']} | {g['early_use_pairs']}/10 | {g['routed_at_rechange']}/10 | {g['first64_mean_cost']:.6f} | {g['remaining448_mean_cost']:.6f} |")
    text += ['', 'All ten polarity-return runs authorized the old predictor at review 1536, just before the environment changed again. The predictor remained authorized until the next review; input meanings had not yet triggered mid-interval exclusion. Its additional later loss is confined to that first 64-record interval. Fresh evidence from the preceding regime was insufficient to guarantee usefulness in the next one. The active predictor was already updating during this interval.','',
          'This localizes two different issues: recovering the meanings a stored predictor needs, and revoking a predictor when evidence changes between reviews. It does not show that a larger archive would fix either. The descriptive diagnosis rescored saved predictions only; no new learning, tuning or outcomes were introduced.','',
          '## Failed preservation guard','', '| History | Window | Channel | Mean cost | Worst pair cost |','| --- | --- | ---: | ---: | ---: |']
    text += [f"| {g['history']} | {g['window']} | {g['channel']} | {g['mean_cost']:.6f} | {g['max_cost']:.6f} |" for g in s['guards'] if not g['passed']]
    text += ['', 'The allowed mean cost was .02 and each-pair cost .10. All other prespecified preservation guards passed. Final validity passed, with 8/10 polarity endpoints and 10/10 elsewhere in both active and deployed predictors; this does not erase earlier trajectory costs.','',
          '## Next question, not started','',
          'The smallest follow-up would keep capture and memory capacity fixed while testing withdrawal of recall within a review interval against the present fixed authorization. A separate question is whether a preserved predictor should retain an independently usable encoding of its inputs, rather than wait for the active learner to recreate compatible meanings. That would change what is stored and requires a separate design. Neither intervention is implemented or tested here. No controller or architecture is promoted.','',
          '## Verification and limits','',f"Runner {data['elapsed_seconds']:.1f}s; independent audit {audit['elapsed_seconds']:.1f}s. All caps passed; {len(data['hashes'])} frozen dependency files remain unchanged. The first fixture attempt passed with 194560 reused training presentations and 1632 synthetic scalar presentations; no fresh random fixture labels. The audit reconstructed every world, prediction, review, memory event, immutable snapshot, control, checkpoint, metric and summary, including exact stored-loss arithmetic.",'',
          'The capture schedule, candidate language, stable local role, boost schedule, thresholds, review period and raw symbol meanings are supplied. Worlds and proposal draws are correlated within histories; five environment seeds are not broad task-family generalization. The experiment establishes durable stored-prediction use in some circumstances, not reliable recall, active representation repair, meta-learning or a safety advantage.','',
          'Fresh-run accounting:','']
    text += [f'- {k}: {v}' for k,v in data['totals'].items()]
    text += ['', 'Archive prediction counts exclude separately counted review-grid and diagnostic work. Grid counts are contexts across both active and routed evaluations. Audit replay is separate: 1843200 training presentations, with no newly generated labels. Post-outcome diagnosis compared 10240 saved prediction pairs, also without training.','',
          '[Frozen protocol](../../experiments/preserved_prediction_protocol.md) · [Independent audit](audit.json) · [Full results](results.json) · [Trace diagnosis](descriptive.json) · [Controller documentation](../../docs/preserved-prediction.md)','']
    (out/'descriptive.json').write_text(json.dumps(desc,indent=2)+'\n');(out/'findings.md').write_text('\n'.join(text))
    print(json.dumps(desc['summary'],indent=2))
if __name__=='__main__':main()
