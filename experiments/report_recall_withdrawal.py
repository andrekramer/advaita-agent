"""037 post-audit report and inspection excerpts; does not train or select."""
import gzip,hashlib,json
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]

def main():
    out=ROOT/'results/recall-withdrawal-v1';d=json.loads((out/'results.json').read_text());a=json.loads((out/'audit.json').read_text());assert a['status']=='pass'
    for k,n in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]:assert hashlib.sha256((out/n).read_bytes()).hexdigest()==a[k+'_sha256']
    with gzip.open(out/'runs.jsonl.gz','rt') as f:rs=[json.loads(line) for line in f]
    s=d['summary'];lookup={(r['seed'],r['history'],r['proposal_seed'],r['policy']):r for r in rs}
    diagnostics=[]
    for r in rs:
        if r['policy'] not in ('evidence','command'):continue
        state=r['checkpoint']['steering'];events=state['monitors']
        diagnostics.append(dict(seed=r['seed'],history=r['history'],proposal_seed=r['proposal_seed'],policy=r['policy'],withdrawal_ticks=[x['tick'] for x in events if x['withdrawn']],withdrawal_windows=[dict(first=x['first_tick'],last=x['tick'],archive_loss=x['archive_loss'],active_loss=x['active_loss']) for x in events if x['withdrawn']],commands=state['commands'],uses_by_window=r['metrics']['uses_by_window'],blocked_uses=r['metrics']['blocked_uses']))
    opportunity=[]
    for p in s['paired']:
        if p['history'] not in ('forms','repeated'):continue
        k=(p['seed'],p['history'],p['proposal_seed']);current=lookup[*k,'current'];evidence=lookup[*k,'evidence']
        opportunity.append(dict(seed=p['seed'],history=p['history'],proposal_seed=p['proposal_seed'],gain=p['rechange_gain'],current_rechange_uses=current['metrics']['uses_by_window']['rechange'],evidence_rechange_uses=evidence['metrics']['uses_by_window']['rechange'],withdrawal_ticks=[e['tick'] for e in evidence['checkpoint']['steering']['monitors'] if e['withdrawn'] and 1537<=e['tick']<=1600]))
    command=[r for r in rs if r['policy']=='command'];release_fidelity=all(len(r['steering_commands'])==2 and not r['checkpoint']['steering']['blocked'] and all(e['source']=='active' for e in r['prediction_events'][1552:1728]) for r in command)
    desc=dict(status='descriptive_post_audit',fresh_labels=0,training_presentations=0,command_runs=len(command),command_events=sum(len(r['steering_commands']) for r in command),blocked_archive_predictions=sum(r['metrics']['blocked_uses'] for r in command),block_and_release_fidelity=release_fidelity,records=diagnostics,posthoc_opportunity=opportunity)
    text=['# 037 — withdrawing recall and releasing explicit control','',
          'Completed 2026-11-06. All **240 runs independently reconstructed**. The evidence-withdrawal full empirical criterion **'+('passed' if s['empirical_pass'] else 'failed')+'**. The first steering round ends with this study; no further experiment is started. The original default is unchanged.','',
          '## Primary comparison','',
          f"Compared with current recall, evidence-triggered withdrawal improved immediate-rechange expected composite loss by **{s['rechange_mean']:.6f} nats**, positive in **{s['rechange_positive']}/20** familiar-return pairs. The target was .10 nats and 14/20. Whole-return gain over shadow was **{s['return_mean']:.6f} nats**, positive in **{s['return_positive']}/20** pairs; its target was .01 and 14/20.",'',
          '| Prespecified criterion | Pass |','| --- | --- |']
    text += [f'| {k} | {v} |' for k,v in s['gates'].items()]
    text += ['', 'These comparisons test withdrawal while preserving useful recall. They do not replace the failed early-recall criterion in 036. A benefit against current recall can coexist with a cost against never deploying memory.','',
          '## Predictions and validity','', '| History | Policy | Early return | Whole return/post-release | First 64 after rechange | Later | Final deployed / active valid | Withdrawals |','| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |']
    for g in s['groups']:text.append(f"| {g['history']} | {g['policy']} | {g['expected']['early_return'][2]:.6f} | {g['expected']['returning'][2]:.6f} | {g['expected']['rechange'][2]:.6f} | {g['expected']['later'][2]:.6f} | {g['final_valid']}/10 / {g['active_final_valid']}/10 | {g['withdrawals']} |")
    text += ['', 'Lower loss is better. All three channels, observed losses and active-only loss are in results.json. Stable, persistent and altered-return histories use the same fixed windows, without implying that they underwent a familiar return or rechange.','',
          '## Explicit block and release','',f"All **{len(command)} command runs** executed the block after 1552 and release after 1664: **{desc['command_events']} commands**, **{desc['blocked_archive_predictions']} blocked archive predictions**, block/release fidelity **{release_fidelity}**. Active learning continued identically. Release did not revive the old authorization: output remained active through 1728, with any later recall requiring a fresh review.",'',
          f"The supplied command improved mean immediate-rechange composite loss by **{s['command_rechange_mean']:.6f} nats** versus current recall across the two returning histories. Its schedule deliberately follows the constructed change; this is a supplied instruction and timing advantage, not autonomous change detection. Command-arm costs and usefulness are separate from the primary evidence-controller verdict.",'',
          '## What the controller actually did','',
          'All arms scored immutable archived probabilities before the main labels entered learning. Only the evidence arm could withdraw after a 16-observation window with mean archive loss more than .02 above active loss. Withdrawal affected subsequent predictions; it did not rewrite the 16th prediction. Ordinary fresh reviews could authorize recall again. Windows reset at review, incompatibility, non-recall, missing labels and explicit commands.','',
          'Exact active predictions, ordinary reviews and final active-learning states matched across policies, excluding intentional controller and audit metadata. Frozen capture, stored meanings and parameters were unchanged. Thus intervention differences are in authorization and output routing, not extra training or a veto on active learning.','',
          '| History | Current archive predictions | Evidence archive predictions | Evidence withdrawals | First-64 evidence cost vs shadow |','| --- | ---: | ---: | ---: | ---: |']
    for h in ('stable','forms','repeated','forms_persistent','repeated_persistent','forms_other'):
        g={x['policy']:x for x in s['groups'] if x['history']==h}
        text.append(f"| {h} | {g['current']['uses']} | {g['evidence']['uses']} | {g['evidence']['withdrawals']} | {g['evidence']['expected']['rechange'][2]-g['shadow']['expected']['rechange'][2]:.6f} |")
    text += ['', '## Consistency and intervention opportunity: descriptive check', '',
             f"The immediate-rechange comparison has {sum(p['gain']>1e-12 for p in opportunity)} gains, {sum(abs(p['gain'])<=1e-12 for p in opportunity)} ties and {sum(p['gain'] < -1e-12 for p in opportunity)} losses. Current recall supplied at least one prediction in this window in {sum(p['current_rechange_uses']>0 for p in opportunity)}/20 pairs.", '',
             '| History | Seed / proposal | Current recalled predictions | Evidence recalled predictions | Withdrawal ticks | Gain |',
             '| --- | --- | ---: | ---: | --- | ---: |']
    for p in opportunity:text.append(f"| {p['history']} | {p['seed']} / {p['proposal_seed']} | {p['current_rechange_uses']} | {p['evidence_rechange_uses']} | {p['withdrawal_ticks']} | {p['gain']:.6f} |")
    text += ['', 'This is a post-outcome explanation of the fixed result, not a replacement denominator. The prespecified consistency requirement remains failed. Where no recall was active, there was no stale authorization to withdraw in this window. The comparison still includes those pairs. The scheduled command and evidence controller produced the same immediate-rechange gains on this batch; fixed phase/review alignment limits extrapolation to other timings.', '',
             'The evidence monitor also withdrew recall in stable tasks. Those withdrawals need not diagnose an environmental change: they compare recent prediction losses and can respond to noise or calibration differences. The preservation guards, rather than an assumed perfect detector, assess their cost.']
    text += ['', '## Failed guards','', '| Guard | History | Comparator | Window | Channel | Mean cost | Worst cost |','| --- | --- | --- | --- | ---: | ---: | ---: |']
    failures=0
    for guard in s['retention_guards']:
        if not guard['passed']:failures+=1;text.append(f"| Retain useful recall | {guard['history']} | current | {guard['window']} | 2 | {guard['mean_cost']:.6f} | {guard['max_cost']:.6f} |")
    for guard in s['guards']:
        if not guard['passed']:failures+=1;text.append(f"| Preservation | {guard['history']} | {guard['control']} | {guard['window']} | {guard['channel']} | {guard['mean_cost']:.6f} | {guard['max_cost']:.6f} |")
    if not failures:text.append('| None | | | | | | |')
    text += ['', 'Useful-recall allowances are .01 mean/.05 individual versus current; general preservation allowances are .02/.10 against both current and shadow. Immediate-rechange absolute costs are shown separately above, not bounded by the longer-window preservation criterion. Endpoint success cannot erase trajectory costs.','',
          '## Integrity and scope','',f"Runner {d['elapsed_seconds']:.1f}s; independent auditor {a['elapsed_seconds']:.1f}s. All caps passed; {len(d['hashes'])} frozen dependencies unchanged. Four fixture groups passed on the first attempt: 266240 reused training presentations and 255 synthetic scalar presentations, with no fresh random labels. The audit reconstructed streams, every prediction/review, archive qualification, monitor losses and decisions, external commands, checkpoint hashes, outcome measurements and final learning-state parity.",'',
          'Five environment seeds, two proposal draws and shared histories remain correlated. Capture timing, language of distinctions, role assignment, review cadence, thresholds and explicit command timing are supplied. This is a small controller comparison, not meta-learning, general reliable steering, human comprehension testing or a safety guarantee. The round synthesis records the result alongside earlier positive and negative findings without combining their different variants into one claimed superior learner.','',
          'Fresh-run accounting:','']
    text += [f'- {k}: {v}' for k,v in d['totals'].items()]
    text += ['', 'Main archive predictions, monitoring queries, review-memory scoring and evaluation grids are counted separately. Audit replay adds 2457600 reused training presentations, no new labels. Inspection excerpts are derived from existing traces without new learning.','',
          '[Frozen protocol](../../experiments/recall_withdrawal_protocol.md) · [Independent audit](audit.json) · [Results and all pairs](results.json) · [Command/monitor excerpts](descriptive.json) · [First-round synthesis](../steering-round-one-synthesis.md)','']
    (out/'descriptive.json').write_text(json.dumps(desc,indent=2)+'\n');(out/'findings.md').write_text('\n'.join(text))
    print(json.dumps(dict(gates=s['gates'],rechange_gain=s['rechange_mean'],rechange_positive=s['rechange_positive'],return_gain=s['return_mean'],return_positive=s['return_positive'],command_fidelity=release_fidelity),indent=2))
if __name__=='__main__':main()
