# 028 — Fresh confirmation of selective memory revision

**350 runs independently audited. The full primary criterion passed.**
Adding selective weakening to relaxed admission improved the declared mean prediction loss by **0.033904 nats**,
with strictly positive gains in **10/10 paired runs** and **5/5 environment means**.

The primary comparison equally weights lasting prediction reversal and local
category remapping. A gain is control loss minus candidate loss. It is a
bounded comparison with admission alone, not a claim of beating every
simpler learner or of generalized intelligence. No architecture is promoted.

## Why repeat the experiment?

027 found later improvements, but its primary window ended before the
two-review weakening rule could affect a prediction. That failed result
remains unchanged. This confirmation registered a new primary window,
**897–1280 inclusive**, before generating fresh seeds 1800–1804 with proposal
seeds 1800/1801. The whole 384-tick period is included for every run, even
if weakening occurs late or never. Early return 769–896 remains a cost guard.
The later 1153–1280 window remains secondary. There was no outcome-driven
window alignment, policy tuning, sample extension or benchmark restart.

The learner, generator, seven policies, acquisition and horizon are the
frozen 027 implementations. Only orchestration and measurement changed.
Two supporting reviews still authorize halving a channel of slow evidence.
Fast evidence is unchanged by weakening; subsequent migration is mass
conserving. The [protocol](../../experiments/memory_confirmation_protocol.md)
specifies the complete criteria. Five environment seeds with two proposal
replicates are not ten independent environment samples.

## Primary comparison

| History | Admission only | Admission + weakening | Observed gain | Expected gain | Positive observed pairs |
| --- | ---: | ---: | ---: | ---: | ---: |
| reversal | 0.512803 | 0.458171 | 0.054632 | 0.054181 | 10/10 |
| remap | 0.401294 | 0.388119 | 0.013176 | 0.012705 | 6/10 |

Observed loss uses noisy outcomes. Expected loss uses the simulator’s
Bernoulli target only for evaluation, never for learning decisions.
Both are composite predictive log loss in nats; lower is better.

The improvement is strongest in lasting reversal: all ten pairs improved.
For category remapping, six pairs improved and four tied. The pooled gain
is positive in all ten pairs and all five environment means; one environment
mean is below .02, which is the pooled threshold, not a per-environment
threshold. The result supports a repeatable benefit within these tasks.

| Environment | Mean primary gain across its two proposal replicates |
| --- | ---: |
| 1800 | 0.035449 |
| 1801 | 0.030856 |
| 1802 | 0.057461 |
| 1803 | 0.016847 |
| 1804 | 0.028906 |

## Full criterion, including costs

| Condition | Result |
| --- | --- |
| revision gain | pass |
| revision pairs | pass |
| final validity | pass |
| gap validity | pass |
| preservation mean | pass |
| preservation worst | pass |
| gap cost | pass |
| revision mean cost | pass |
| revision worst | pass |
| post mean cost | pass |
| post worst | pass |
| recovery censoring | pass |

All predeclared primary conditions passed.
The primary gain threshold is .02 nats and at least 8/10 positive pairs.
Preservation and early-cost means must not exceed .02, or .10 in an
individual observed pair. The new primary window has the same per-history
cost limits so a pooled benefit cannot conceal excessive harm to one history.
Final full validity must reach 8/10 in every history, with familiar-gap
validity at least 8/10 and no increased number of censored recoveries.

## All policies

Baseline is the original hard-window/archive learner. Fast is the weighted
learner without slow migration. Selective is the old adequate-and-improved
admission gate; relaxed requires improvement alone. Weaken adds selective
weakening to the old gate, and combined adds it to relaxed admission.
Uniform halves slow evidence every labelled review with relaxed admission.
Uniform is not matched in removed mass.

| Policy | Stable whole | Familiar early | Brief reversal | Post-burst | Reversal primary | Remap primary |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0.328625 | 0.344847 | 1.573029 | 0.576593 | 0.354658 | 0.340003 |
| fast | 0.333102 | 0.410337 | 1.077845 | 0.550910 | 0.348376 | 0.352162 |
| selective | 0.320871 | 0.344790 | 1.263703 | 0.527997 | 0.578047 | 0.424692 |
| relaxed | 0.320875 | 0.342844 | 1.264975 | 0.534413 | 0.512803 | 0.401294 |
| weaken | 0.320871 | 0.344790 | 1.263703 | 0.527997 | 0.480550 | 0.399804 |
| combined | 0.320875 | 0.342844 | 1.264975 | 0.534413 | 0.458171 | 0.388119 |
| uniform | 0.336812 | 0.361315 | 1.121627 | 0.575083 | 0.348322 | 0.365652 |

Adaptation trajectories: early 769–896, primary 897–1280, late 1153–1280.
The late window is contained within the primary window.

| Policy | Reversal early | Reversal primary | Reversal late | Remap early | Remap primary | Remap late |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 1.225158 | 0.354658 | 0.335733 | 0.803815 | 0.340003 | 0.332504 |
| fast | 0.417505 | 0.348376 | 0.333900 | 0.579863 | 0.352162 | 0.338768 |
| selective | 0.878329 | 0.578047 | 0.541405 | 0.708110 | 0.424692 | 0.388210 |
| relaxed | 0.886471 | 0.512803 | 0.443879 | 0.712045 | 0.401294 | 0.363827 |
| weaken | 0.878329 | 0.480550 | 0.394416 | 0.708110 | 0.399804 | 0.359232 |
| combined | 0.886471 | 0.458171 | 0.374255 | 0.712045 | 0.388119 | 0.351022 |
| uniform | 0.620702 | 0.348322 | 0.336374 | 0.613653 | 0.365652 | 0.356617 |

The brief reversal changes the true target for 64 observations, then restores
it. It is not just label corruption. Gap histories have no observations
at ticks 257–768. All policies receive the same history within each pair.

| Policy | Stable final | Burst final | Return final | Reversal final | Remap final | Familiar gap |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 9/10 |
| fast | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 0/10 |
| selective | 10/10 | 10/10 | 10/10 | 0/10 | 8/10 | 9/10 |
| relaxed | 10/10 | 10/10 | 10/10 | 3/10 | 10/10 | 9/10 |
| weaken | 10/10 | 10/10 | 10/10 | 10/10 | 8/10 | 9/10 |
| combined | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 9/10 |
| uniform | 10/10 | 10/10 | 10/10 | 10/10 | 10/10 | 8/10 |

Full validity requires correct local partitions, all composite modal
predictions correct and expected regret<=.10. Accurate output can hide a
damaged local representation when an upper raw-input port bypasses it.

For lasting reversal, adding weakening to relaxed admission raised final
full validity from 3/10 to 10/10. Combined reached 10/10 final validity in
every history. It made no weakening changes during stable, brief-reversal
or familiar-return histories. Familiar-gap validity was 9/10 versus 0/10
for fast-only. The one failed gap run already had an incorrect local form
before the gap; it recovered later. This endpoint success does not establish
error-free representations throughout learning.

| Policy | Reversal censored recovery | Remap censored recovery | Accepted weakenings across all histories |
| --- | ---: | ---: | ---: |
| baseline | 0/10 | 0/10 | 0 |
| fast | 0/10 | 0/10 | 0 |
| selective | 10/10 | 2/10 | 0 |
| relaxed | 8/10 | 0/10 | 0 |
| weaken | 2/10 | 2/10 | 56 |
| combined | 0/10 | 0/10 | 41 |
| uniform | 0/10 | 0/10 | 2130 |

Recovery requires two consecutive full-valid evaluations from tick 832.
Censored means it was not confirmed by tick 1280; no recovery time is
invented for those runs. Endpoint validity and sustained recovery differ.

## Secondary comparisons

| Candidate | Control | Reversal primary gain | Remap primary gain |
| --- | --- | ---: | ---: |
| weaken | selective | 0.097497 | 0.024888 |
| combined | selective | 0.119876 | 0.036574 |
| relaxed | selective | 0.065244 | 0.023398 |
| combined | uniform | -0.109849 | -0.022466 |
| combined | fast | -0.109796 | -0.035956 |
| combined | baseline | -0.103514 | -0.048116 |

The separate selectivity-benefit criterion passed: combined’s mean retention-oriented gain over uniform was 0.025026 nats,
positive in 10/10 pairs. This equally weights stable whole, familiar early return and post-burst recovery.

Fast-only, uniform weakening and the original baseline had lower loss than
combined in the primary adaptation window. The confirmed benefit is over
keeping the same slow memory without selective weakening. Retaining slow
evidence still carries an adaptation cost; selective control improves that
tradeoff without dominating the simpler alternatives.

## Boundaries of the result

This is fixed memory control over a supplied finite representation language.
It does not learn the control rule. Raw sufficient statistics remain stored
beyond coarse prediction interfaces. The tests are new instances of the same
constructed families, not open-ended tasks. General superiority, autonomous
agency, meta-learning, human steerability and a safety advantage are not
established. A positive memory result does not by itself repair remaining
representation errors. No policy is automatically promoted.

## Audit and resources

Four pre-run fixture tests checked exact window endpoints, primary versus
early/late selection, failure of individual cost guards, and replay of one
saved 027 trace with unchanged runtime/generator identities. They used zero
new learning labels; the saved-trace replay rechecked 6784 label presentations.
All 25 worlds and 350 fresh traces, decisions, predictions, checkpoints, old/new
metrics, paired summaries and budgets passed independent reconstruction.
The auditor imports no runtime or experiment policy implementation.

Benchmark: 129.638s. Independent audit: 106.354s. Each ceiling: 900s.

| Resource | Count |
| --- | ---: |
| legacy auxiliary predictions | 12,000 |
| reused grid predictions | 7,680 |
| runs | 350 |
| generated labels | 135,040 |
| used labels | 1,890,560 |
| candidate fits | 164,986 |
| active fits | 2,035,101 |
| probe fits | 1,800 |
| raw bin visits | 29,197,496 |
| scoring queries | 7,060,928 |
| main predictions | 1,021,440 |
| evaluation predictions | 232,400 |
| slow probe predictions | 24,000 |
| oracle context queries | 1,203,104 |

The primary window reuses saved predictions; it generates no additional
labels, fits or oracle queries. Grid allocation includes 7680 reused baseline
gap predictions. Actual grid plus legacy auxiliary computations: 236720;
slow-only probes add 24000. Prior artifacts and frozen sources are preserved.

Artifacts: [results and paired measurements](results.json), [audit](audit.json),
[source manifest](manifest.json), [worlds](worlds.json), [full traces](runs.jsonl.gz),
[post-audit diagnostics](diagnostics.json), [fixtures](../memory-confirmation-fixtures/attempt-01.json).

```sh
python3 checks/test_memory_confirmation.py
python3 experiments/memory_confirmation.py
python3 checks/audit_memory_confirmation.py
python3 experiments/report_memory_confirmation.py
```

The benchmark refuses to overwrite an existing output directory.
