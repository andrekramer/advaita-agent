"""028 post-audit report; does not affect learning or predeclared decisions."""
import gzip
import hashlib
import json
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'results/memory-confirmation-v1'


def main():
    data=json.loads((OUT/'results.json').read_text());audit=json.loads((OUT/'audit.json').read_text())
    assert audit['status']=='pass'
    for key,file in [('result','results.json'),('runs','runs.jsonl.gz')]:
        assert audit[key+'_sha256']==hashlib.sha256((OUT/file).read_bytes()).hexdigest()
    with gzip.open(OUT/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
    s=data['summary'];groups={(g['branch'],g['policy']):g for g in s['groups']}
    policies=['baseline','fast','selective','relaxed','weaken','combined','uniform']
    gain=mean(r['gain'] for r in s['revision_pairs']);positive=sum(r['gain']>0 for r in s['revision_pairs'])
    env=[dict(seed=seed,primary_gain=mean(r['gain'] for r in s['revision_pairs'] if r['seed']==seed)) for seed in sorted({r['seed'] for r in runs})]
    diagnostics=[]
    for h in ['stable','burst','return','reversal','remap']:
        for p in policies:
            rs=[r for r in runs if r['branch']==h and r['policy']==p]
            finals=[r['evaluations'][-1] for r in rs]
            diagnostics.append(dict(branch=h,policy=p,final_correct_forms=sum(all(e['local_exact']) for e in finals),
                final_perfect_modal=sum(e['accuracy']==1 for e in finals),mean_final_regret=mean(e['regret'] for e in finals),
                weakenings=sum(r['costs'].get('weakenings',0) for r in rs),
                failures=[dict(seed=r['seed'],proposal_seed=r['proposal_seed'],initial_full_valid=r['metrics']['transfer_valid'],
                    final=r['evaluations'][-1]) for r in rs if not r['metrics']['final_valid']],
                first_weakening=[dict(seed=r['seed'],proposal_seed=r['proposal_seed'],tick=next((v['index'] for v in r['reviews'] if any(e['accepted'] for e in v.get('weakenings',[]))),None)) for r in rs]))
    (OUT/'diagnostics.json').write_text(json.dumps(dict(post_audit=True,environment_gains=env,groups=diagnostics),indent=2)+'\n')
    lines=['# 028 — Fresh confirmation of selective memory revision','',
        f"**350 runs independently audited. The full primary criterion {'passed' if s['primary_pass'] else 'failed'}.**",
        f"Adding selective weakening to relaxed admission improved the declared mean prediction loss by **{gain:.6f} nats**,",
        f"with strictly positive gains in **{positive}/10 paired runs** and **{sum(e['primary_gain']>0 for e in env)}/5 environment means**.", '',
        'The primary comparison equally weights lasting prediction reversal and local',
        'category remapping. A gain is control loss minus candidate loss. It is a',
        'bounded comparison with admission alone, not a claim of beating every',
        'simpler learner or of generalized intelligence. No architecture is promoted.','',
        '## Why repeat the experiment?','',
        '027 found later improvements, but its primary window ended before the',
        'two-review weakening rule could affect a prediction. That failed result',
        'remains unchanged. This confirmation registered a new primary window,',
        '**897–1280 inclusive**, before generating fresh seeds 1800–1804 with proposal',
        'seeds 1800/1801. The whole 384-tick period is included for every run, even',
        'if weakening occurs late or never. Early return 769–896 remains a cost guard.',
        'The later 1153–1280 window remains secondary. There was no outcome-driven',
        'window alignment, policy tuning, sample extension or benchmark restart.','',
        'The learner, generator, seven policies, acquisition and horizon are the',
        'frozen 027 implementations. Only orchestration and measurement changed.',
        'Two supporting reviews still authorize halving a channel of slow evidence.',
        'Fast evidence is unchanged by weakening; subsequent migration is mass',
        'conserving. The [protocol](../../experiments/memory_confirmation_protocol.md)',
        'specifies the complete criteria. Five environment seeds with two proposal',
        'replicates are not ten independent environment samples.','',
        '## Primary comparison','',
        '| History | Admission only | Admission + weakening | Observed gain | Expected gain | Positive observed pairs |',
        '| --- | ---: | ---: | ---: | ---: | ---: |']
    for h in ['reversal','remap']:
        rows=[r for r in s['paired'] if r['candidate']=='combined' and r['control']=='relaxed' and r['branch']==h]
        lines.append(f"| {h} | {groups[h,'relaxed']['observed']['post']:.6f} | {groups[h,'combined']['observed']['post']:.6f} | {-mean(r['observed_cost']['post'] for r in rows):.6f} | {-mean(r['latent_cost']['post'] for r in rows):.6f} | {sum(r['observed_cost']['post']<0 for r in rows)}/10 |")
    lines += ['', 'Observed loss uses noisy outcomes. Expected loss uses the simulator’s',
        'Bernoulli target only for evaluation, never for learning decisions.',
        'Both are composite predictive log loss in nats; lower is better.','',
        'The improvement is strongest in lasting reversal: all ten pairs improved.',
        'For category remapping, six pairs improved and four tied. The pooled gain',
        'is positive in all ten pairs and all five environment means; one environment',
        'mean is below .02, which is the pooled threshold, not a per-environment',
        'threshold. The result supports a repeatable benefit within these tasks.','',
        '| Environment | Mean primary gain across its two proposal replicates |',
        '| --- | ---: |']
    lines += [f"| {e['seed']} | {e['primary_gain']:.6f} |" for e in env]
    lines += ['', '## Full criterion, including costs','', '| Condition | Result |','| --- | --- |']
    lines += [f"| {key.replace('_',' ')} | {'pass' if value else 'fail'} |" for key,value in s['gates'].items()]
    failed=[k.replace('_',' ') for k,v in s['gates'].items() if not v]
    lines += ['', ('All predeclared primary conditions passed.' if not failed else 'Failed conditions: '+', '.join(failed)+'.'),
        'The primary gain threshold is .02 nats and at least 8/10 positive pairs.',
        'Preservation and early-cost means must not exceed .02, or .10 in an',
        'individual observed pair. The new primary window has the same per-history',
        'cost limits so a pooled benefit cannot conceal excessive harm to one history.',
        'Final full validity must reach 8/10 in every history, with familiar-gap',
        'validity at least 8/10 and no increased number of censored recoveries.','',
        '## All policies','',
        'Baseline is the original hard-window/archive learner. Fast is the weighted',
        'learner without slow migration. Selective is the old adequate-and-improved',
        'admission gate; relaxed requires improvement alone. Weaken adds selective',
        'weakening to the old gate, and combined adds it to relaxed admission.',
        'Uniform halves slow evidence every labelled review with relaxed admission.',
        'Uniform is not matched in removed mass.','',
        '| Policy | Stable whole | Familiar early | Brief reversal | Post-burst | Reversal primary | Remap primary |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in policies:
        values=[groups[h,p]['observed'][k] for h,k in [('stable','whole'),('return','early'),('burst','burst'),('burst','recovery'),('reversal','post'),('remap','post')]]
        lines.append('| '+p+' | '+' | '.join(f'{v:.6f}' for v in values)+' |')
    lines += ['', 'Adaptation trajectories: early 769–896, primary 897–1280, late 1153–1280.',
        'The late window is contained within the primary window.','',
        '| Policy | Reversal early | Reversal primary | Reversal late | Remap early | Remap primary | Remap late |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in policies:
        values=[groups[h,p]['observed'][k] for h in ['reversal','remap'] for k in ['early','post','late']]
        lines.append('| '+p+' | '+' | '.join(f'{v:.6f}' for v in values)+' |')
    lines += ['', 'The brief reversal changes the true target for 64 observations, then restores',
        'it. It is not just label corruption. Gap histories have no observations',
        'at ticks 257–768. All policies receive the same history within each pair.','',
        '| Policy | Stable final | Burst final | Return final | Reversal final | Remap final | Familiar gap |',
        '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for p in policies:
        counts=[groups[h,p]['final_valid'] for h in ['stable','burst','return','reversal','remap']]+[groups['return',p]['gap_valid']]
        lines.append('| '+p+' | '+' | '.join(f'{v}/10' for v in counts)+' |')
    lines += ['', 'Full validity requires correct local partitions, all composite modal',
        'predictions correct and expected regret<=.10. Accurate output can hide a',
        'damaged local representation when an upper raw-input port bypasses it.','',
        'For lasting reversal, adding weakening to relaxed admission raised final',
        'full validity from 3/10 to 10/10. Combined reached 10/10 final validity in',
        'every history. It made no weakening changes during stable, brief-reversal',
        'or familiar-return histories. Familiar-gap validity was 9/10 versus 0/10',
        'for fast-only. The one failed gap run already had an incorrect local form',
        'before the gap; it recovered later. This endpoint success does not establish',
        'error-free representations throughout learning.','',
        '| Policy | Reversal censored recovery | Remap censored recovery | Accepted weakenings across all histories |',
        '| --- | ---: | ---: | ---: |']
    for p in policies:
        lines.append(f"| {p} | {groups['reversal',p]['recovery_censored']}/10 | {groups['remap',p]['recovery_censored']}/10 | {sum(g['weakenings'] for g in s['groups'] if g['policy']==p)} |")
    lines += ['', 'Recovery requires two consecutive full-valid evaluations from tick 832.',
        'Censored means it was not confirmed by tick 1280; no recovery time is',
        'invented for those runs. Endpoint validity and sustained recovery differ.','',
        '## Secondary comparisons','',
        '| Candidate | Control | Reversal primary gain | Remap primary gain |',
        '| --- | --- | ---: | ---: |']
    contrasts=[('weaken','selective'),('combined','selective'),('relaxed','selective'),('combined','uniform'),('combined','fast'),('combined','baseline')]
    for a,b in contrasts:
        vals=[-mean(r['observed_cost']['post'] for r in s['paired'] if r['candidate']==a and r['control']==b and r['branch']==h) for h in ['reversal','remap']]
        lines.append(f'| {a} | {b} | {vals[0]:.6f} | {vals[1]:.6f} |')
    sel=s['selection_pairs']
    lines += ['', f"The separate selectivity-benefit criterion {'passed' if s['selectivity_pass'] else 'failed'}: combined’s mean retention-oriented gain over uniform was {mean(r['gain'] for r in sel):.6f} nats,",
        f"positive in {sum(r['gain']>0 for r in sel)}/10 pairs. This equally weights stable whole, familiar early return and post-burst recovery.",'',
        'Fast-only, uniform weakening and the original baseline had lower loss than',
        'combined in the primary adaptation window. The confirmed benefit is over',
        'keeping the same slow memory without selective weakening. Retaining slow',
        'evidence still carries an adaptation cost; selective control improves that',
        'tradeoff without dominating the simpler alternatives.','',
        '## Boundaries of the result','',
        'This is fixed memory control over a supplied finite representation language.',
        'It does not learn the control rule. Raw sufficient statistics remain stored',
        'beyond coarse prediction interfaces. The tests are new instances of the same',
        'constructed families, not open-ended tasks. General superiority, autonomous',
        'agency, meta-learning, human steerability and a safety advantage are not',
        'established. A positive memory result does not by itself repair remaining',
        'representation errors. No policy is automatically promoted.','',
        '## Audit and resources','',
        'Four pre-run fixture tests checked exact window endpoints, primary versus',
        'early/late selection, failure of individual cost guards, and replay of one',
        'saved 027 trace with unchanged runtime/generator identities. They used zero',
        'new learning labels; the saved-trace replay rechecked 6784 label presentations.',
        'All 25 worlds and 350 fresh traces, decisions, predictions, checkpoints, old/new',
        'metrics, paired summaries and budgets passed independent reconstruction.',
        'The auditor imports no runtime or experiment policy implementation.','',
        f"Benchmark: {data['elapsed_seconds']:.3f}s. Independent audit: {audit['elapsed_seconds']:.3f}s. Each ceiling: 900s.",'',
        '| Resource | Count |','| --- | ---: |']
    lines += [f"| {key.replace('_',' ')} | {value:,} |" for key,value in data['totals'].items()]
    lines += ['', 'The primary window reuses saved predictions; it generates no additional',
        'labels, fits or oracle queries. Grid allocation includes 7680 reused baseline',
        'gap predictions. Actual grid plus legacy auxiliary computations: 236720;',
        'slow-only probes add 24000. Prior artifacts and frozen sources are preserved.','',
        'Artifacts: [results and paired measurements](results.json), [audit](audit.json),',
        '[source manifest](manifest.json), [worlds](worlds.json), [full traces](runs.jsonl.gz),',
        '[post-audit diagnostics](diagnostics.json), [fixtures](../memory-confirmation-fixtures/attempt-01.json).','',
        '```sh','python3 checks/test_memory_confirmation.py','python3 experiments/memory_confirmation.py',
        'python3 checks/audit_memory_confirmation.py','python3 experiments/report_memory_confirmation.py','```','',
        'The benchmark refuses to overwrite an existing output directory.','']
    (OUT/'findings.md').write_text('\n'.join(lines))
    completion=dict(experiment='028',date='2026-10-30',status='complete_audited',runs=350,primary_pass=s['primary_pass'],selectivity_pass=s['selectivity_pass'],
        primary_mean_gain=gain,primary_positive_pairs=positive,primary_positive_environments=sum(e['primary_gain']>0 for e in env),
        learner_changed=False,baseline_promoted=False,benchmark_restart=False,
        report_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        **{k+'_sha256':hashlib.sha256((OUT/file).read_bytes()).hexdigest() for k,file in [('manifest','manifest.json'),('audit','audit.json'),('findings','findings.md')]})
    (OUT/'completion.json').write_text(json.dumps(completion,indent=2)+'\n')

if __name__=='__main__':main()
