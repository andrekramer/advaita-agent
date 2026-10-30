"""Post-audit descriptive report; never used to select or tune the experiment."""
import gzip
import hashlib
import json
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/memory-revision-v1'


def main():
    data=json.loads((OUT/'results.json').read_text());audit=json.loads((OUT/'audit.json').read_text())
    assert audit['status']=='pass' and audit['result_sha256']==hashlib.sha256((OUT/'results.json').read_bytes()).hexdigest()
    assert audit['runs_sha256']==hashlib.sha256((OUT/'runs.jsonl.gz').read_bytes()).hexdigest()
    with gzip.open(OUT/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
    summary=data['summary'];groups={(g['branch'],g['policy']):g for g in summary['groups']}
    policies=['baseline','fast','selective','relaxed','weaken','combined','uniform']
    phases={'before':(1,256),'brief':(257,320),'after_brief':(321,448),'after_gap':(769,1280)}
    diagnostics=[]
    for h in ['stable','burst','return','reversal','remap']:
        for p in policies:
            rs=[r for r in runs if r['branch']==h and r['policy']==p];final=[r['evaluations'][-1] for r in rs]
            events=[(v['index'],e) for r in rs for v in r['reviews'] for e in v.get('weakenings',[])]
            diagnostics.append(dict(branch=h,policy=p,final_correct_forms=sum(all(e['local_exact']) for e in final),
                final_perfect_modal=sum(e['accuracy']==1 for e in final),final_mean_regret=mean(e['regret'] for e in final),
                by_phase={name:dict(tests=sum(lo<=t<=hi for t,e in events),qualified=sum(e['qualifies'] for t,e in events if lo<=t<=hi),
                    accepted=sum(e['accepted'] for t,e in events if lo<=t<=hi),removed_mass=sum(e['removed_mass'] for t,e in events if lo<=t<=hi),
                    channel_accepts=[sum(e['accepted'] and e['channel']==j for t,e in events if lo<=t<=hi) for j in range(3)]) for name,(lo,hi) in phases.items()}))
    lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r for r in runs}
    timing=[]
    for r in runs:
        if r['policy'] not in ('combined','weaken'):continue
        control='relaxed' if r['policy']=='combined' else 'selective'
        c=lookup[r['seed'],r['proposal_seed'],r['branch'],control]
        timing.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],branch=r['branch'],policy=r['policy'],
            first_weakening=next((v['index'] for v in r['reviews'] if any(e['accepted'] for e in v['weakenings'])),None),
            identical_predictions_through_896=r['predictions'][:896]==c['predictions'][:896]))
    (OUT/'diagnostics.json').write_text(json.dumps(dict(post_audit=True,groups=diagnostics,timing=timing),indent=2)+'\n')
    lines=['# 027 — Admission and revision of slow memory','',
        'Completed 2026-10-30. **350 runs passed independent replay audit.** The primary',
        f"criterion **{'passed' if summary['primary_pass'] else 'failed'}**; the separate selectivity-benefit criterion",
        f"**{'passed' if summary['selectivity_pass'] else 'failed'}**. No policy is promoted to the reference architecture.",'',
        '## What was tested','',
        '026 showed that slow evidence can retain useful predictions, but its admission',
        'gate could also reject gradual repair of a wrong slow model. This experiment',
        'separates admitting new evidence from reducing the influence of old evidence.',
        'The [protocol](../../experiments/memory_revision_protocol.md) was frozen before',
        'the reserved outcomes. Five fresh environment seeds each have two proposal',
        'replicates; these are ten paired runs, not ten independent environments.','',
        '**The primary window was poorly timed.** It measured pre-update predictions',
        'at 769–896, but two fresh post-change reviews are first available at 832 and',
        '896. An accepted weakening at 896 can first affect prediction 897. The saved',
        'traces confirm identical combined/relaxed predictions throughout the primary',
        'window in all reversal and remap runs. No selective weakening occurred',
        'before the gap. Thus the zero early gain cannot assess the later intervention.',
        'This protocol design error was discovered after outcomes; the primary failure',
        'is preserved, without changing its window, thresholds or reserved seeds.','',
        'The separately predeclared late window and final-validity measurements show',
        'useful later effects. Those remain secondary evidence, not a repaired primary',
        'success. In reversal, final validity rose from 5/10 under relaxed admission',
        'to 8/10 with selective weakening added. The original admission gate plus',
        'weakening rose from 2/10 to 8/10. Neither change eliminates structural failures.','',
        '| Policy | Admission | Extra weakening |',
        '| --- | --- | --- |',
        '| baseline | Original window/archive learner | Original behavior |',
        '| fast | No migration to slow store | None |',
        '| selective | Improved and already adequate slow candidate | None |',
        '| relaxed | Improved slow candidate | None |',
        '| weaken | Improved and adequate | Two supporting reviews |',
        '| combined | Improved | Two supporting reviews |',
        '| uniform | Improved | Half the slow evidence each labelled review |','',
        'All weighted variants preserve the same structural operators and fast/slow',
        'half-lives of 64/1024 ticks. Fast and slow store raw sufficient statistics',
        'supporting forms. They are not two autonomous learners of a category language.','',
        '## Memory rule','',
        'For one channel, compare predictors fitted to S, F, F+S and F+S/2 on the',
        'current 32 fresh selection labels, using actual learned forms/interfaces.',
        'Qualifying evidence requires fast loss<=.55, slow-minus-fast loss>.05,',
        'and combined-minus-weakened loss>.02. Two reviews 64 ticks apart must',
        'qualify under the same representation and used interface meanings.',
        'Then S is halved and active predictions refit; F is unchanged.',
        'The candidate is recomputed at each review. This is repeated evidence for',
        'weakening, not a frozen-hypothesis confirmation or learned controller.','',
        'Migration then moves up to .25F into S under the policy admission rule.',
        'Migration conserves F+S; weakening deliberately reduces it. Evidence',
        'mass, decisions and removed mass remain inspectable in the saved traces.',
        'Selection labels are never added as training counts. The same batch also',
        'supports structural and migration decisions; these are not independent',
        'confirmations within a review. Subsequent pre-update predictions test utility.','',
        '## All policies and histories','',
        'Loss is mean composite observed log loss in nats; lower is better.',
        'Early windows are 769–896, burst 257–320, and post-burst recovery 321–448.',
        'The burst is a brief genuine outcome reversal, not corrupted labels for an',
        'unchanged latent task. Gap histories have no observations at 257–768.','',
        '| Policy | Stable whole | Brief reversal | Post-burst | Familiar early | Reversal early | Remap early |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in policies:
        values=[groups[h,p]['observed'][k] for h,k in [('stable','whole'),('burst','burst'),('burst','recovery'),('return','early'),('reversal','early'),('remap','early')]]
        lines.append('| '+p+' | '+' | '.join(f'{v:.6f}' for v in values)+' |')
    lines += ['', 'Full validity means correct local partitions, all composite modal predictions',
        'correct and expected regret<=.10. It is more demanding than modal accuracy.','',
        '| Policy | Stable final | Burst final | Return final | Reversal final | Remap final | Return gap |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in policies:
        counts=[groups[h,p]['final_valid'] for h in ['stable','burst','return','reversal','remap']]+[groups['return',p]['gap_valid']]
        lines.append('| '+p+' | '+' | '.join(f'{v}/10' for v in counts)+' |')
    lines += ['', 'Late observed-loss improvements (1153–1280) isolate adding the weakening',
        'rule under each admission policy. These are secondary comparisons.','',
        '| Candidate minus control intervention | History | Mean gain | Positive pairs |',
        '| --- | --- | ---: | ---: |']
    for a,b in [('weaken','selective'),('combined','relaxed')]:
        for h in ['reversal','remap']:
            values=[-r['observed_cost']['late'] for r in summary['paired'] if r['candidate']==a and r['control']==b and r['branch']==h]
            lines.append(f"| {a} versus {b} | {h} | {mean(values):.6f} | {sum(v>0 for v in values)}/10 |")
    lines += ['', 'Selective weakening made no changes in stable, brief-reversal or familiar-return',
        'histories. It therefore preserved its admission-matched control exactly in',
        'those histories. The combined policy retained full validity through the',
        'familiar gap in 10/10 runs, versus 0/10 for fast-only. At the final horizon',
        'familiar-return validity was 8/10: retaining evidence did not prevent every',
        'later structural error. All combined preservation guards passed.','',
        'The two final invalid combined runs in each gap history are the two proposal',
        'replicates of environment 1704. They began with correct forms, but ended with',
        'one incorrect local partition and a raw upper port [2,1]. Their composite',
        'modal predictions were nevertheless all correct. This is a continuing',
        'representation failure concealed by an accurate raw bypass, not an excluded',
        'acquisition failure.','',
        'Uniform weakening adapted earlier and had lower reversal loss, while its',
        'familiar-gap validity was 8/10 and retention-oriented mean loss was worse.',
        'Fast-only reached 10/10 final validity in every history but lost confidence',
        'through the blank gap. These controls expose a retention/adaptation tradeoff;',
        'they do not establish universal superiority of the richer policy.']
    lines += ['', '## Paired tests and guards','',
        '| Predeclared primary condition | Result |','| --- | --- |']
    lines += [f"| {k.replace('_',' ')} | {'pass' if v else 'fail'} |" for k,v in summary['gates'].items()]
    rev=summary['revision_pairs'];sel=summary['selection_pairs']
    lines += ['', f"Combined's declared early-revision gain over relaxed admission alone was **{mean(x['gain'] for x in rev):.6f} nats**,",
        f"positive in **{sum(x['gain']>0 for x in rev)}/10 pairs** (equal reversal/remap weight).",
        f"Its separate retention-oriented gain over uniform weakening was **{mean(x['gain'] for x in sel):.6f} nats**,",
        f"positive in **{sum(x['gain']>0 for x in sel)}/10 pairs** (stable whole, familiar early and post-burst).",'',
        'The following costs are combined minus control; positive means worse.',
        'Each cell reports mean observed / mean expected cost, then worst observed pair.','',
        '| Control | Window | Mean observed / expected | Worst observed |',
        '| --- | --- | ---: | ---: |']
    for c in ['selective','relaxed']:
        for h,k in [('stable','whole'),('return','early'),('burst','burst'),('burst','recovery'),('reversal','early'),('remap','early')]:
            ps=[r for r in summary['paired'] if r['candidate']=='combined' and r['control']==c and r['branch']==h]
            lines.append(f"| {c} | {h} {k} | {mean(r['observed_cost'][k] for r in ps):+.6f} / {mean(r['latent_cost'][k] for r in ps):+.6f} | {max(r['observed_cost'][k] for r in ps):+.6f} |")
    lines += ['', '## Recovery and mechanism checks','',
        'Recovery is the second consecutive full-valid evaluation from 832 onward.',
        'Non-recoveries are censored at the 1280-tick horizon, not assigned an observed',
        'recovery time. The following counts are runs that did not confirm recovery.','',
        '| Policy | Reversal censored | Remap censored | Accepted weakenings, reversal / remap |',
        '| --- | ---: | ---: | ---: |']
    for p in policies:
        lines.append(f"| {p} | {groups['reversal',p]['recovery_censored']}/10 | {groups['remap',p]['recovery_censored']}/10 | {groups['reversal',p]['weakenings']} / {groups['remap',p]['weakenings']} |")
    lines += ['', 'Detailed per-phase/channel decisions and final prediction/representation',
        'diagnostics are in [diagnostics.json](diagnostics.json). These descriptive',
        'checks were computed after the audit and do not replace the frozen gates.',
        'The uniform policy forgets more often, not an equal amount; its comparison',
        'does not isolate selectivity at matched removed mass.', '',
        '## Scope and interpretation','',
        'This is a bounded test of hand-designed memory control over existing',
        'representations. It does not establish meta-learning, human steerability,',
        'new perceptual primitives, autonomous agency, a safety advantage or general',
        'superiority. Correct partitions do not guarantee calibrated predictions.',
        'Raw evidence remains stored beyond coarse prediction interfaces. There is',
        'no new task family, arbitrary nesting or autonomous category vocabulary.',
        'No variant was selected for promotion after looking at its results.','',
        'A defensible next confirmation would register a primary benefit window after',
        'the earliest possible weakening (from 897 onward), while keeping the first 128',
        'return observations as an adaptation-cost guard. It should use fresh seeds',
        'and retain admission-only and fast-forgetting controls. That confirmation',
        'has not been run. The present evidence supports testing selective revision',
        'further; it does not close the question of a robust memory controller.','',
        '## Verification and resources','',
        'All 350 worlds/run combinations, every pre-update prediction and review,',
        'weakening/migration decision, full final checkpoint, evaluation, per-run',
        'measurement, paired summary and resource count passed independent replay.',
        'The reference implementation reuses frozen independent026 components and',
        'separately implements the new decisions; it imports no new runtime policy.',
        'Arithmetic checks and deliberately tampered traces passed before the run.',
        'Controls reproduced026 behavior in the fixtures. All prior frozen files',
        'and the new source freeze remained unchanged. No benchmark restart or tuning.','',
        f"Fixtures used 2264 label presentations of the 5000 allowance. Benchmark time: {data['elapsed_seconds']:.3f}s; independent audit: {audit['elapsed_seconds']:.3f}s (900s ceilings).",'',
        '| Resource | Count |','| --- | ---: |']
    for k,v in data['totals'].items():lines.append(f"| {k.replace('_',' ')} | {v:,} |")
    lines += ['', 'The grid allocation includes 7680 reused baseline gap predictions.',
        'Actual grid plus legacy auxiliary computations total 236720; slow probes',
        'add 24000. Candidate fits and score counts include the extra counterfactual',
        'weakening proposals even for non-weakening weighted controls. Each has two',
        '40-bin evidence stores, bounded active/pending models and separate audit logs.', '',
        'Artifacts: [results and paired data](results.json), [audit](audit.json),',
        '[source manifest](manifest.json), [worlds](worlds.json),',
        '[full compressed traces](runs.jsonl.gz), [fixture evidence](../memory-revision-fixtures/attempt-01.json).', '',
        'Commands (the benchmark refuses to overwrite existing outputs):','',
        '```sh','python3 checks/test_memory_revision.py','python3 experiments/memory_revision.py',
        'python3 checks/audit_memory_revision.py','python3 experiments/report_memory_revision.py','```','']
    (OUT/'findings.md').write_text('\n'.join(lines))
    completion=dict(experiment='027',date='2026-10-30',status='complete_audited',runs=350,
        primary_pass=summary['primary_pass'],selectivity_pass=summary['selectivity_pass'],baseline_modified=False,
        fixture_labels=2264,used_labels=data['totals']['used_labels'],benchmark_restart=False,
        primary_window_precedes_first_possible_effect=True,
        report_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        **{name+'_sha256':hashlib.sha256((OUT/(name+'.json' if name!='findings' else 'findings.md')).read_bytes()).hexdigest() for name in ['manifest','audit','findings']})
    (OUT/'completion.json').write_text(json.dumps(completion,indent=2)+'\n')

if __name__=='__main__':main()
