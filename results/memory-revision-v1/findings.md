# 027 — Admission and revision of slow memory

Completed 2026-10-30. **350 runs passed independent replay audit.** The primary
criterion **failed**; the separate selectivity-benefit criterion
**passed**. No policy is promoted to the reference architecture.

## What was tested

026 showed that slow evidence can retain useful predictions, but its admission
gate could also reject gradual repair of a wrong slow model. This experiment
separates admitting new evidence from reducing the influence of old evidence.
The [protocol](../../experiments/memory_revision_protocol.md) was frozen before
the reserved outcomes. Five fresh environment seeds each have two proposal
replicates; these are ten paired runs, not ten independent environments.

**The primary window was poorly timed.** It measured pre-update predictions
at 769–896, but two fresh post-change reviews are first available at 832 and
896. An accepted weakening at 896 can first affect prediction 897. The saved
traces confirm identical combined/relaxed predictions throughout the primary
window in all reversal and remap runs. No selective weakening occurred
before the gap. Thus the zero early gain cannot assess the later intervention.
This protocol design error was discovered after outcomes; the primary failure
is preserved, without changing its window, thresholds or reserved seeds.

The separately predeclared late window and final-validity measurements show
useful later effects. Those remain secondary evidence, not a repaired primary
success. In reversal, final validity rose from 5/10 under relaxed admission
to 8/10 with selective weakening added. The original admission gate plus
weakening rose from 2/10 to 8/10. Neither change eliminates structural failures.

| Policy | Admission | Extra weakening |
| --- | --- | --- |
| baseline | Original window/archive learner | Original behavior |
| fast | No migration to slow store | None |
| selective | Improved and already adequate slow candidate | None |
| relaxed | Improved slow candidate | None |
| weaken | Improved and adequate | Two supporting reviews |
| combined | Improved | Two supporting reviews |
| uniform | Improved | Half the slow evidence each labelled review |

All weighted variants preserve the same structural operators and fast/slow
half-lives of 64/1024 ticks. Fast and slow store raw sufficient statistics
supporting forms. They are not two autonomous learners of a category language.

## Memory rule

For one channel, compare predictors fitted to S, F, F+S and F+S/2 on the
current 32 fresh selection labels, using actual learned forms/interfaces.
Qualifying evidence requires fast loss<=.55, slow-minus-fast loss>.05,
and combined-minus-weakened loss>.02. Two reviews 64 ticks apart must
qualify under the same representation and used interface meanings.
Then S is halved and active predictions refit; F is unchanged.
The candidate is recomputed at each review. This is repeated evidence for
weakening, not a frozen-hypothesis confirmation or learned controller.

Migration then moves up to .25F into S under the policy admission rule.
Migration conserves F+S; weakening deliberately reduces it. Evidence
mass, decisions and removed mass remain inspectable in the saved traces.
Selection labels are never added as training counts. The same batch also
supports structural and migration decisions; these are not independent
confirmations within a review. Subsequent pre-update predictions test utility.

## All policies and histories

Loss is mean composite observed log loss in nats; lower is better.
Early windows are 769–896, burst 257–320, and post-burst recovery 321–448.
The burst is a brief genuine outcome reversal, not corrupted labels for an
unchanged latent task. Gap histories have no observations at 257–768.

| Policy | Stable whole | Brief reversal | Post-burst | Familiar early | Reversal early | Remap early |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0.339571 | 1.768669 | 0.641454 | 0.351792 | 1.274691 | 0.853139 |
| fast | 0.350224 | 1.106608 | 0.650890 | 0.422769 | 0.427503 | 0.669533 |
| selective | 0.338488 | 1.304690 | 0.619744 | 0.360005 | 0.860965 | 0.712968 |
| relaxed | 0.338488 | 1.304690 | 0.620275 | 0.358818 | 0.877732 | 0.716191 |
| weaken | 0.338488 | 1.304690 | 0.619744 | 0.360005 | 0.860965 | 0.712968 |
| combined | 0.338488 | 1.304690 | 0.620275 | 0.358818 | 0.877732 | 0.716191 |
| uniform | 0.354357 | 1.152818 | 0.653586 | 0.377847 | 0.646826 | 0.669977 |

Full validity means correct local partitions, all composite modal predictions
correct and expected regret<=.10. It is more demanding than modal accuracy.

| Policy | Stable final | Burst final | Return final | Reversal final | Remap final | Return gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 10/10 | 10/10 | 8/10 | 8/10 | 8/10 | 10/10 |
| fast | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 |
| selective | 10/10 | 10/10 | 8/10 | 2/10 | 7/10 | 10/10 |
| relaxed | 10/10 | 10/10 | 8/10 | 5/10 | 8/10 | 10/10 |
| weaken | 10/10 | 10/10 | 8/10 | 8/10 | 8/10 | 10/10 |
| combined | 10/10 | 10/10 | 8/10 | 8/10 | 8/10 | 10/10 |
| uniform | 10/10 | 10/10 | 8/10 | 8/10 | 8/10 | 8/10 |

Late observed-loss improvements (1153–1280) isolate adding the weakening
rule under each admission policy. These are secondary comparisons.

| Candidate minus control intervention | History | Mean gain | Positive pairs |
| --- | --- | ---: | ---: |
| weaken versus selective | reversal | 0.148482 | 10/10 |
| weaken versus selective | remap | 0.035174 | 10/10 |
| combined versus relaxed | reversal | 0.076204 | 10/10 |
| combined versus relaxed | remap | 0.017282 | 10/10 |

Selective weakening made no changes in stable, brief-reversal or familiar-return
histories. It therefore preserved its admission-matched control exactly in
those histories. The combined policy retained full validity through the
familiar gap in 10/10 runs, versus 0/10 for fast-only. At the final horizon
familiar-return validity was 8/10: retaining evidence did not prevent every
later structural error. All combined preservation guards passed.

The two final invalid combined runs in each gap history are the two proposal
replicates of environment 1704. They began with correct forms, but ended with
one incorrect local partition and a raw upper port [2,1]. Their composite
modal predictions were nevertheless all correct. This is a continuing
representation failure concealed by an accurate raw bypass, not an excluded
acquisition failure.

Uniform weakening adapted earlier and had lower reversal loss, while its
familiar-gap validity was 8/10 and retention-oriented mean loss was worse.
Fast-only reached 10/10 final validity in every history but lost confidence
through the blank gap. These controls expose a retention/adaptation tradeoff;
they do not establish universal superiority of the richer policy.

## Paired tests and guards

| Predeclared primary condition | Result |
| --- | --- |
| revision gain | fail |
| revision pairs | fail |
| final validity | pass |
| gap validity | pass |
| preservation mean | pass |
| preservation worst | pass |
| gap cost | pass |
| revision mean cost | pass |
| revision worst | pass |
| recovery censoring | pass |

Combined's declared early-revision gain over relaxed admission alone was **0.000000 nats**,
positive in **0/10 pairs** (equal reversal/remap weight).
Its separate retention-oriented gain over uniform weakening was **0.022737 nats**,
positive in **10/10 pairs** (stable whole, familiar early and post-burst).

The following costs are combined minus control; positive means worse.
Each cell reports mean observed / mean expected cost, then worst observed pair.

| Control | Window | Mean observed / expected | Worst observed |
| --- | --- | ---: | ---: |
| selective | stable whole | +0.000000 / +0.000000 | +0.000000 |
| selective | return early | -0.001187 / -0.001526 | +0.000000 |
| selective | burst burst | +0.000000 / +0.000000 | +0.000000 |
| selective | burst recovery | +0.000531 / +0.000468 | +0.008747 |
| selective | reversal early | +0.016768 / +0.017700 | +0.096218 |
| selective | remap early | +0.003224 / +0.004538 | +0.027291 |
| relaxed | stable whole | +0.000000 / +0.000000 | +0.000000 |
| relaxed | return early | +0.000000 / +0.000000 | +0.000000 |
| relaxed | burst burst | +0.000000 / +0.000000 | +0.000000 |
| relaxed | burst recovery | +0.000000 / +0.000000 | +0.000000 |
| relaxed | reversal early | +0.000000 / +0.000000 | +0.000000 |
| relaxed | remap early | +0.000000 / +0.000000 | +0.000000 |

## Recovery and mechanism checks

Recovery is the second consecutive full-valid evaluation from 832 onward.
Non-recoveries are censored at the 1280-tick horizon, not assigned an observed
recovery time. The following counts are runs that did not confirm recovery.

| Policy | Reversal censored | Remap censored | Accepted weakenings, reversal / remap |
| --- | ---: | ---: | ---: |
| baseline | 0/10 | 0/10 | 0 / 0 |
| fast | 0/10 | 0/10 | 0 / 0 |
| selective | 8/10 | 3/10 | 0 / 0 |
| relaxed | 8/10 | 0/10 | 0 / 0 |
| weaken | 3/10 | 0/10 | 39 / 16 |
| combined | 2/10 | 0/10 | 31 / 16 |
| uniform | 0/10 | 0/10 | 329 / 329 |

Detailed per-phase/channel decisions and final prediction/representation
diagnostics are in [diagnostics.json](diagnostics.json). These descriptive
checks were computed after the audit and do not replace the frozen gates.
The uniform policy forgets more often, not an equal amount; its comparison
does not isolate selectivity at matched removed mass.

## Scope and interpretation

This is a bounded test of hand-designed memory control over existing
representations. It does not establish meta-learning, human steerability,
new perceptual primitives, autonomous agency, a safety advantage or general
superiority. Correct partitions do not guarantee calibrated predictions.
Raw evidence remains stored beyond coarse prediction interfaces. There is
no new task family, arbitrary nesting or autonomous category vocabulary.
No variant was selected for promotion after looking at its results.

A defensible next confirmation would register a primary benefit window after
the earliest possible weakening (from 897 onward), while keeping the first 128
return observations as an adaptation-cost guard. It should use fresh seeds
and retain admission-only and fast-forgetting controls. That confirmation
has not been run. The present evidence supports testing selective revision
further; it does not close the question of a robust memory controller.

## Verification and resources

All 350 worlds/run combinations, every pre-update prediction and review,
weakening/migration decision, full final checkpoint, evaluation, per-run
measurement, paired summary and resource count passed independent replay.
The reference implementation reuses frozen independent026 components and
separately implements the new decisions; it imports no new runtime policy.
Arithmetic checks and deliberately tampered traces passed before the run.
Controls reproduced026 behavior in the fixtures. All prior frozen files
and the new source freeze remained unchanged. No benchmark restart or tuning.

Fixtures used 2264 label presentations of the 5000 allowance. Benchmark time: 119.813s; independent audit: 103.312s (900s ceilings).

| Resource | Count |
| --- | ---: |
| legacy auxiliary predictions | 12,000 |
| reused grid predictions | 7,680 |
| runs | 350 |
| generated labels | 135,040 |
| used labels | 1,890,560 |
| candidate fits | 165,265 |
| active fits | 2,035,107 |
| probe fits | 1,800 |
| raw bin visits | 29,206,088 |
| scoring queries | 7,079,744 |
| main predictions | 1,021,440 |
| evaluation predictions | 232,400 |
| slow probe predictions | 24,000 |
| oracle context queries | 1,197,824 |

The grid allocation includes 7680 reused baseline gap predictions.
Actual grid plus legacy auxiliary computations total 236720; slow probes
add 24000. Candidate fits and score counts include the extra counterfactual
weakening proposals even for non-weakening weighted controls. Each has two
40-bin evidence stores, bounded active/pending models and separate audit logs.

Artifacts: [results and paired data](results.json), [audit](audit.json),
[source manifest](manifest.json), [worlds](worlds.json),
[full compressed traces](runs.jsonl.gz), [fixture evidence](../memory-revision-fixtures/attempt-01.json).

Commands (the benchmark refuses to overwrite existing outputs):

```sh
python3 checks/test_memory_revision.py
python3 experiments/memory_revision.py
python3 checks/audit_memory_revision.py
python3 experiments/report_memory_revision.py
```
