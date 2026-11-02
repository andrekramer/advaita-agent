"""Post-audit 030 report."""
import hashlib,json
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'results/memory-lifecycle-v1'
d=json.loads((out/'results.json').read_text());a=json.loads((out/'audit.json').read_text());assert a['status']=='pass' and a['result_sha256']==hashlib.sha256((out/'results.json').read_bytes()).hexdigest()
s=d['summary'];gain=mean(r['gain'] for r in s['revision_pairs']);rare=mean(s['rare_gains'])
lines=['# 030 — Repeated changes, returning forms and rare distinctions','',
'Completed 2026-11-02. **All 120 runs independently audited; the full primary criterion failed.**',
f'The combined policy improved settled prediction loss over admission alone by **{gain:.6f} nats**, positive in {sum(r["gain"]>0 for r in s["revision_pairs"])}/10 paired runs.',
f'Rare-group expected loss improved over fast-only by **{rare:.6f} nats**, positive in {sum(v>0 for v in s["rare_gains"])}/10 pairs.','',
'These benefits did not remove the stability/adaptation tradeoff. Final full validity',
'was only 4/10 after repeated reversals and 7/10 in the rare-category history.',
'Early costs against admission alone exceeded the .02-nat limit in both changing',
'histories. The optional variant is therefore not promoted to the default.','',
'## Fixed comparison','',
'Three 2048-tick histories use four 512-tick phases: repeated polarity reversal;',
'alternating original/alternative categories; and an unchanged category that',
'becomes rare during the middle two phases (2/32 rather than 16/32 contexts).',
'Fresh selection has the same imbalance. Balanced evaluation remains separate.',
'All policies see the same observations; the learner sees no history label or',
'latent truth. Five fresh environment seeds each have two proposal replicates.',
'These ten pairs are not ten independent environments. No parameter tuning.','',
'The [protocol](../../experiments/memory_lifecycle_protocol.md) fixes all windows',
'and criteria. Settled loss includes returns to earlier knowledge as well as',
'changes; early loss covers the first 128 observations after each transition.',
'The weighted variants execute through the new common runtime; the baseline',
'uses its frozen implementation, whose common-runtime equivalence passed 029.','',
'| History | Policy | Settled observed loss | Early observed loss | Full-valid endpoints at 512 / 1024 / 1536 / 2048 |',
'| --- | --- | ---: | ---: | --- |']
for g in s['groups']:lines.append(f"| {g['branch']} | {g['policy']} | {g['observed']['settled']:.6f} | {g['observed']['early']:.6f} | {' / '.join(str(x)+'/10' for x in g['endpoint_valid'])} |")
lines += ['', 'Full validity requires correct local partitions, all modal composite',
'predictions correct and expected regret<=.10. Every acquisition failure and',
'later failure remains in the denominator.','',
'## Rare knowledge','', '| Policy | Rare-context expected loss at 1536 | Full validity at 1536 | Final full validity |','| --- | ---: | ---: | ---: |']
for g in s['groups']:
 if g['branch']=='rare':lines.append(f"| {g['policy']} | {g['rare_loss']:.6f} | {g['endpoint_valid'][2]}/10 | {g['final_valid']}/10 |")
lines += ['', 'The rare probe weights the 16 rare contexts equally, so common inputs cannot',
'hide loss of the less frequent distinction. Combined and admission-only have',
'identical rare-history performance here. This is evidence for retention in the',
'slow store, not an extra rare-knowledge benefit from weakening. Despite the gain',
'over fast-only, rare-context loss remains substantial and full validity is',
'incomplete. The original baseline finishes the rare history at 10/10.','',
'## Gates and adaptation costs','', '| Gate | Result |','| --- | --- |']
lines += [f"| {k.replace('_',' ')} | {'pass' if v else 'fail'} |" for k,v in s['gates'].items()]
for h in ('repeated','forms'):
 rs=[r for r in s['paired'] if r['control']=='relaxed' and r['branch']==h]
 lines += ['',f"In {h}, combined's early observed cost against admission alone was {mean(r['observed_cost']['early'] for r in rs):+.6f} nats; expected cost was {mean(r['latent_cost']['early'] for r in rs):+.6f}."]
lines += ['', 'Thus repeated reuse/revision of memory is harder than the one-change',
'confirmation in 028. Better later predictions do not imply faster adjustment',
'or consistently sound representations. The next bounded steering test examines',
'one diagnosed contradiction without changing these failed results.','',
'## Verification and scope','',
'Every world, prediction, review, native checkpoint, outer runtime checkpoint,',
'metric, paired decision and resource total passed independent reconstruction.',
'All 350 earlier traces had already passed exact integration compatibility.',
'Fixtures used 1792 label presentations out of 2000. New benchmark presentations:',
'1,228,800 across 120 runs; generated labels: 153,600. No restart or tuning.',
f'Benchmark {d["elapsed_seconds"]:.3f}s; audit {a["elapsed_seconds"]:.3f}s, each below 900s.',
'All declared fit/query/resource ceilings passed. Full counts and per-environment',
'means are in [results](results.json); [audit](audit.json), [manifest](manifest.json),',
'[worlds](worlds.json), [traces](runs.jsonl.gz) and [fixtures](../memory-lifecycle-fixtures/attempt-01.json) preserve the evidence.','',
'These are supplied finite contexts, local feedback and fixed memory rules.',
'The experiment demonstrates neither meta-learning, user interpretability,',
'universal learning superiority nor a safety advantage.','']
(out/'findings.md').write_text('\n'.join(lines))
(out/'completion.json').write_text(json.dumps(dict(experiment='030',date='2026-11-02',status='complete_audited',runs=120,primary_pass=s['primary_pass'],promoted=False,report_code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()),indent=2)+'\n')
