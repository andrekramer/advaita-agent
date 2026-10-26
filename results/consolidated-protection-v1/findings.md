# Experiment 020: corroboration protects forms, but slows genuine change

Completed 2026-10-26. All **60 runs** passed independent reconstruction of
streams, predictions, decisions, evidence records and full checkpoints.
**The combined criterion failed:** corroboration substantially reduced errors
under noise and misleading evidence, but exceeded the declared joint-prediction
loss and recovery-delay limits after lasting change. No benchmark was tuned
or repeated.

## Fixed intervention and comparisons

The [protocol](../../experiments/consolidated_protection_protocol.md) compared
the unchanged consolidated learner with one new local acceptance rule.
Discovery remained immediate. After upper initialization, two unchanged,
adequate reviews established protection. An ordinary replacement of a protected
form became a frozen provisional challenger, requiring a second fresh witness.
The incumbent's counts kept updating. A failed witness discarded the challenger
without falling through to a different replacement that review. Accepted
replacement reset protection. Existing two-witness collapse and all upper
interface, dependency and memory rules remained unchanged.

Five fresh environment seeds, each with two proposal seeds, gave ten paired
runs in each of three histories: persistent structure with 10% label noise,
a temporary misleading local-label burst, and a lasting local remap affecting
the composite outcome. All received the same acquisition curriculum followed
by 1280 observations and 20 reviews. All acquisition failures remained in
denominators. These are five environment realizations, not ten independent
worlds; the histories also share pre-change experience.

## Stability benefits

| Affected-form error checkpoints | Baseline | Corroborated | Reduction | Improved pairs |
| --- | ---: | ---: | ---: | ---: |
| Persistent, reviews 192–1280 | 9/180 | 1/180 | 88.9% | 4/10 |
| Burst, reviews 192–512 | 23/60 | 4/60 | 82.6% | 8/10 |

Both passed the frozen benefit requirement: at least 25% fewer errors and
improvement in at least two pairs. This did not conceal damage to the other
module: corresponding both-node errors fell from 19 to 1 and from 26 to 4.
Stable late full validity rose from 7/10 to 10/10 in both histories. Persistent
loss costs were slightly negative; burst latent composite loss fell by .115874
nats and affected-local latent loss by .118466 over records 129–320.

Protection was not immediate or infallible. Eight of ten affected forms had
earned protection by review128. The remaining harmful replacements in protected
runs occurred at that review in environment902, before those forms had earned
protection, in both proposal draws. The paired histories share this event.
No incorrect establishment was recorded. Four pending challengers remained
unresolved at the end across persistent/burst runs; their states are retained.

## Genuine-change costs

For the lasting remap, evaluate loss over records 129–512 and confirmed
recovery at the second consecutive fully valid post-change review.

| Remap measure | Protected minus baseline | Allowed cost | Result |
| --- | ---: | ---: | --- |
| Observed composite loss | +.063845 nats | <=.05 | Fail |
| Latent composite loss | +.065902 nats | <=.05 | Fail |
| Affected-local latent loss | +.039909 nats | <=.05 | Pass |
| Mean confirmed-recovery delay | +89.6 records | <=64 | Fail |

Mean confirmation time moved from 288 to 377.6. Eight pairs were delayed by
128 records and two improved by 64; no recovery was censored. Every policy
achieved 10/10 acquisition transfer in every history, and all final full-validity
gates passed. Protection achieved 10/10 stable late full validity in remap,
versus 8/10 for baseline. Those later successes do not erase the early cost.

A saved trace illustrates why the delay can exceed the extra local witness.
In environment900/proposal900, baseline adopted the remapped lower form at192
and confirmed full recovery at256. Protection held a challenger at192 while
the upper learner changed its interface. At256 it accepted the correct lower
form and achieved correct modal predictions, but loss regret was still .200817,
above .10. Full-valid reviews at320 and384 confirmed recovery at384. This
illustrates coupled local/interface adaptation; it does not establish that a
particular alternative upper policy would remove the delay.

## What remains unresolved

Stable appropriate structures passed in **6/10 persistent, 6/10 burst and 4/10
remap** protected runs, versus 3/10, 3/10 and 4/10 for baseline. Correct local
forms and predictions still do not guarantee return to group-only interfaces.
Mean raw reads decreased in persistent/burst but increased in remap, from 249.6
to 371.2. Local protection addresses part of the regression problem; it does not
solve information hiding throughout the system.

The protected learner retrieved no archives. Archive events were recorded,
but this experiment did not isolate memory benefit and did not redesign capture.
The upper learning and memory rules were held fixed to isolate local protection.

The result is consistent with the earlier [C1 protection trade-off](../protection-interfaces-v1/findings.md),
now tested inside the structural learner. It provides a concrete stability
benefit and a measured adaptation cost, not a reason to promote this policy as
an overall improvement. Any next intervention should be separately specified:
preserving a useful prior predictor or coordinating provisional local changes
with the upper interface are distinct hypotheses, not demonstrated solutions.
Meta-learning, new-family generalization and safety advantages remain untested.

## Verification and artifacts

Five synthetic checks passed before reserved-world generation, charging
1615 labels against a 2000-label fixture ceiling. They covered earned protection,
frozen pending models, confirmation failure, checkpoint restoration, duplicate
evidence rejection, independent metric arithmetic and zero-error baselines.

The benchmark used **407,040** allocated/used label presentations, 18,078
candidate fits and 2,408,960 scoring queries, including 1280 extra confirmation
queries. All resource ceilings passed. Benchmark time was 47.47 seconds and
independent audit time 39.07 seconds. Ninety-one source/prior-artifact hashes
preserve the unchanged baseline and all earlier records.

The [complete report](report.md) includes every run, paired comparison and
environment aggregate. See [summary](results.json), [audit](audit.json),
[manifest](manifest.json), [worlds](worlds.json), [full traces](runs.jsonl.gz)
and [trace-derived diagnostics](diagnostics.json). Each trace names its full
checkpoint and checksum; protected checkpoints also include the provisional
models, protection states and costs.

Reproduction entry points: `python3 experiments/consolidated_protection.py`
refuses an existing output directory; `python3 checks/audit_consolidated_protection.py`
replays saved evidence without new learning. Preserve original artifacts before
any deliberate reproduction. No next experiment was run automatically.
