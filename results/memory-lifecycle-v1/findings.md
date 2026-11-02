# 030 — Repeated changes, returning forms and rare distinctions

Completed 2026-11-02. **All 120 runs independently audited; the full primary criterion failed.**
The combined policy improved settled prediction loss over admission alone by **0.043923 nats**, positive in 10/10 paired runs.
Rare-group expected loss improved over fast-only by **0.180382 nats**, positive in 10/10 pairs.

These benefits did not remove the stability/adaptation tradeoff. Final full validity
was only 4/10 after repeated reversals and 7/10 in the rare-category history.
Early costs against admission alone exceeded the .02-nat limit in both changing
histories. The optional variant is therefore not promoted to the default.

## Fixed comparison

Three 2048-tick histories use four 512-tick phases: repeated polarity reversal;
alternating original/alternative categories; and an unchanged category that
becomes rare during the middle two phases (2/32 rather than 16/32 contexts).
Fresh selection has the same imbalance. Balanced evaluation remains separate.
All policies see the same observations; the learner sees no history label or
latent truth. Five fresh environment seeds each have two proposal replicates.
These ten pairs are not ten independent environments. No parameter tuning.

The [protocol](../../experiments/memory_lifecycle_protocol.md) fixes all windows
and criteria. Settled loss includes returns to earlier knowledge as well as
changes; early loss covers the first 128 observations after each transition.
The weighted variants execute through the new common runtime; the baseline
uses its frozen implementation, whose common-runtime equivalence passed 029.

| History | Policy | Settled observed loss | Early observed loss | Full-valid endpoints at 512 / 1024 / 1536 / 2048 |
| --- | --- | ---: | ---: | --- |
| repeated | baseline | 0.353720 | 1.287621 | 9/10 / 10/10 / 8/10 / 9/10 |
| repeated | fast | 0.372483 | 0.852155 | 9/10 / 10/10 / 9/10 / 9/10 |
| repeated | relaxed | 0.608100 | 0.900529 | 9/10 / 0/10 / 2/10 / 0/10 |
| repeated | combined | 0.548749 | 0.955583 | 9/10 / 5/10 / 10/10 / 4/10 |
| forms | baseline | 0.354370 | 0.799916 | 9/10 / 10/10 / 8/10 / 9/10 |
| forms | fast | 0.360878 | 0.718004 | 9/10 / 10/10 / 10/10 / 9/10 |
| forms | relaxed | 0.449642 | 0.719916 | 9/10 / 9/10 / 10/10 / 7/10 |
| forms | combined | 0.421148 | 0.750212 | 9/10 / 10/10 / 10/10 / 9/10 |
| rare | baseline | 0.337363 | 0.380953 | 10/10 / 5/10 / 5/10 / 10/10 |
| rare | fast | 0.354898 | 0.395990 | 9/10 / 2/10 / 3/10 / 8/10 |
| rare | relaxed | 0.335083 | 0.377222 | 10/10 / 8/10 / 6/10 / 7/10 |
| rare | combined | 0.335083 | 0.377222 | 10/10 / 8/10 / 6/10 / 7/10 |

Full validity requires correct local partitions, all modal composite
predictions correct and expected regret<=.10. Every acquisition failure and
later failure remains in the denominator.

## Rare knowledge

| Policy | Rare-context expected loss at 1536 | Full validity at 1536 | Final full validity |
| --- | ---: | ---: | ---: |
| baseline | 0.749680 | 5/10 | 10/10 |
| fast | 0.805601 | 3/10 | 8/10 |
| relaxed | 0.625219 | 6/10 | 7/10 |
| combined | 0.625219 | 6/10 | 7/10 |

The rare probe weights the 16 rare contexts equally, so common inputs cannot
hide loss of the less frequent distinction. Combined and admission-only have
identical rare-history performance here. This is evidence for retention in the
slow store, not an extra rare-knowledge benefit from weakening. Despite the gain
over fast-only, rare-context loss remains substantial and full validity is
incomplete. The original baseline finishes the rare history at 10/10.

## Gates and adaptation costs

| Gate | Result |
| --- | --- |
| revision gain | pass |
| revision pairs | pass |
| final validity | fail |
| rare gain | pass |
| rare pairs | pass |
| preservation mean | pass |
| preservation worst | pass |
| revision mean | fail |
| revision worst | pass |

In repeated, combined's early observed cost against admission alone was +0.055054 nats; expected cost was +0.054559.

In forms, combined's early observed cost against admission alone was +0.030296 nats; expected cost was +0.029443.

Thus repeated reuse/revision of memory is harder than the one-change
confirmation in 028. Better later predictions do not imply faster adjustment
or consistently sound representations. The next bounded steering test examines
one diagnosed contradiction without changing these failed results.

## Verification and scope

Every world, prediction, review, native checkpoint, outer runtime checkpoint,
metric, paired decision and resource total passed independent reconstruction.
All 350 earlier traces had already passed exact integration compatibility.
Fixtures used 1792 label presentations out of 2000. New benchmark presentations:
1,228,800 across 120 runs; generated labels: 153,600. No restart or tuning.
Benchmark 105.774s; audit 81.519s, each below 900s.
All declared fit/query/resource ceilings passed. Full counts and per-environment
means are in [results](results.json); [audit](audit.json), [manifest](manifest.json),
[worlds](worlds.json), [traces](runs.jsonl.gz) and [fixtures](../memory-lifecycle-fixtures/attempt-01.json) preserve the evidence.

These are supplied finite contexts, local feedback and fixed memory rules.
The experiment demonstrates neither meta-learning, user interpretability,
universal learning superiority nor a safety advantage.
