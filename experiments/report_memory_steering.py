"""Post-audit 031 report and explicitly secondary channel diagnostics."""
import gzip,hashlib,json,math
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results/memory-steering-v1'
d=json.loads((out/'results.json').read_text());a=json.loads((out/'audit.json').read_text());assert a['status']=='pass'
for n,f in [('result','results.json'),('runs','runs.jsonl.gz'),('worlds','worlds.json')]:assert a[n+'_sha256']==hashlib.sha256((out/f).read_bytes()).hexdigest()
s=d['summary']
with gzip.open(out/'runs.jsonl.gz','rt') as f:runs=[json.loads(line) for line in f]
worlds={(w['seed'],w['branch']):w for w in json.loads((out/'worlds.json').read_text())};lookup={(r['seed'],r['proposal_seed'],r['branch'],r['policy']):r for r in runs}
diagnostics=[]
for r in runs:
 if r['policy']!='targeted' or r['control'] is None:continue
 b=lookup[r['seed'],r['proposal_seed'],r['branch'],'unsteered'];w=worlds[r['seed'],r['branch']];j=r['control']['channel']
 def value(run,k):
  losses=[]
  for t,row in enumerate(w['main'],1):
   if 577<=t<=1024:
    p=run['predictions'][t-1][k];y=row['local'][k] if k<2 else row['y'];losses.append(-math.log(p if y else 1-p))
  return mean(losses)
 diagnostics.append(dict(seed=r['seed'],proposal_seed=r['proposal_seed'],channel=j,tick=r['trigger']['tick'],affected=w['affected'],
  selected_channel_gain=value(b,j)-value(r,j),composite_gain=value(b,2)-value(r,2),
  identical_composite_window=[p[2] for p in b['predictions'][576:1024]]==[p[2] for p in r['predictions'][576:1024]]))
(out/'diagnostics.json').write_text(json.dumps(dict(post_audit=True,rows=diagnostics),indent=2)+'\n')
lines=['# 031 — Bounded external memory steering','',
'Completed 2026-11-02. **All 60 runs independently audited; the primary steering criterion failed.**',
f'Targeted control improved mean composite loss over no intervention by **{mean(r["gain"] for r in s["gains"]):.6f} nats**, positive in **{sum(r["gain"]>0 for r in s["gains"])}/10 changing-history pairs**.',
'This missed the declared .01-nat and 8/10 thresholds. Stable histories triggered',
'no controls, and all declared collateral-cost guards passed. Final validity in',
'the changing history remained below the 8/10 requirement.','',
'## What was steered','',
'All runs used the same combined learner. A scripted external controller inspected',
'current review diagnostics and selected the first qualifying, not-yet-automatically',
'accepted weakening proposal, ranked by slow-minus-fast loss. It acted at most once',
'per run, up to tick1024. No latent truth entered that choice. No new labels were',
'provided by the intervention. Halving applied to the whole slow channel after',
'the completed review, including any evidence just migrated there.','',
'No-control runs logged the same proposed trigger. Targeted runs halved that',
'channel; rotated controls halved the next channel modulo3. Rotated is a',
'specificity control, not necessarily an irrelevant channel. Each event recorded',
'the review identity, rationale, removed mass and before/after engine hashes.',
'This tests a scripted controller and the API, not human or LLM interpretability.','',
'Five fresh environments each had two proposal replicates; the ten pairs are',
'not ten independent environments. All five draws happened to change node0.',
'No extra seeds were drawn to change that coverage limitation. The fixed primary',
'window577–1024 was not aligned to actual intervention times (640–832 here).',
'The [protocol](../../experiments/memory_steering_protocol.md) preserves the full design.','',
'| History | Policy | Triggers | Interventions | Primary observed loss | Return loss | Later loss | Final full validity |',
'| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |']
for g in s['groups']:lines.append(f"| {g['branch']} | {g['policy']} | {g['triggers']} | {g['controls']} | {g['observed']['benefit']:.6f} | {g['observed']['returning']:.6f} | {g['observed']['later']:.6f} | {g['final_valid']}/10 |")
lines += ['', 'Final validity requires correct partitions, all modal composite predictions',
'correct and expected regret<=.10. Returned knowledge and later reversals remain',
'part of evaluation even though only one early control is allowed.','', '| Gate | Result |','| --- | --- |']
lines += [f"| {k.replace('_',' ')} | {'pass' if v else 'fail'} |" for k,v in s['gates'].items()]
lines += ['',f"Mean gain over rotated control was {mean(s['specificity_gains']):.6f} nats, positive in {sum(v>0 for v in s['specificity_gains'])}/10 pairs: the mean specificity gate passed, but consistency failed.",'',
'## A useful distinction in the diagnostics','',
'Post-audit examination separates improvement in a selected local prediction from',
'improvement in the composite output. These diagnostics were not primary criteria',
'and do not overturn the failed test.','',
'| Seed / proposal | Selected channel | Tick | Selected-channel gain | Composite gain | Composite probabilities unchanged in primary window |',
'| --- | ---: | ---: | ---: | ---: | --- |']
for x in diagnostics:lines.append(f"| {x['seed']} / {x['proposal_seed']} | {x['channel']} | {x['tick']} | {x['selected_channel_gain']:.6f} | {x['composite_gain']:.6f} | {x['identical_composite_window']} |")
lines += ['', 'Four interventions selected composite channel2; all four improved the measured',
'composite outcome. Six selected local channel0; all six improved that local',
'prediction, while composite probabilities were unchanged in the primary window.',
'The upper predictor consumes category membership, not local confidence. Improving',
'local probability estimates need not alter its prediction. This exposes a',
'limitation of ranking intervention targets by local surprise without measuring',
'their relevance to the intended output. It is not a post-hoc success claim.','',
'The next steering question is therefore more specific: can a controller identify',
'which representation or evidence change will affect the intended outcome? A',
'future test would need a preregistered target and downstream-effect checks.',
'No new controller, additional interventions or follow-up seeds were tried here.','',
'## Verification and scope','',
'All worlds, pre-update predictions, automatic decisions, explicit interventions,',
'event hashes, native/outer checkpoints, metrics, paired gates and budgets passed',
'independent reconstruction. The audit imports no runtime or experiment policy.',
'Fixtures used672 label presentations of a1000 allowance. Benchmark generated',
'102400 labels and presented614400 across60 runs. All resource ceilings passed.',
f'Benchmark {d["elapsed_seconds"]:.3f}s; audit {a["elapsed_seconds"]:.3f}s, each below900s.',
'No restart, tuning, default promotion or claim of general steerability.','',
'Artifacts: [results](results.json), [audit](audit.json), [manifest](manifest.json),',
'[worlds](worlds.json), [traces](runs.jsonl.gz), [secondary diagnostics](diagnostics.json),',
'[fixtures](../memory-steering-fixtures/attempt-01.json).','']
(out/'findings.md').write_text('\n'.join(lines))
(out/'completion.json').write_text(json.dumps(dict(experiment='031',date='2026-11-02',status='complete_audited',runs=60,primary_pass=s['primary_pass'],promoted=False,report_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
