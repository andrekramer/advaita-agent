# Strength inspection and bounded steering

Completed2026-11-13. Mechanical contract: **True**;
information/forecast criterion: **True**;
steering criterion: **False**. Presentation comprehension was
**not tested**. Native reconstruction passed for72 acquired trunks and288 command
continuations, across12 environment seeds, three histories and two proposal seeds.

## What this tests

The unchanged consolidated learner uses combined memory and shadow recall.
At tick640 a supplied controller chooses no intervention or temporary plasticity
for one channel. All four possibilities are replayed on identical future data;
controls release at896 and evaluation ends1152. Target/protected outputs are
supplied task instructions. Forms, reviews, automatic weakening and migration
continue normally. No goals or control policy were learned.

The ordinary inspection supplies row totals and channel-wide bank masses. The
existing-view controller approximates each row's bank allocation proportionally.
An additional read-only adapter supplies actual row-specific fast/slow counts.
The named description represents those same counts as bank direction and retained
strength. Raw and named descriptions produced identical commands and numerically
equivalent forecasts. This verifies an encoding; it does not show that a reader
understands the named version better. The extra bank information, rather than
geometry, is the substantive information intervention.

All evaluators are supplied scripts. The64-step control model uses recent empirical
rates and fixed representations, omitting future structural reviews and memory
decisions. It is a plug-in approximation, not an exact expected future loss.
Recent64 observations are reused training data, not an independent validation set.

## Mechanical effect forecasts

All32 input contexts and all4 commands were probed from each decision state on
isolated clones, using a supplied contrary outcome. Mean absolute probability
error, pooling emitted pre-label and diagnostic post-label predictions:

| Inspection | Mean absolute error |
| --- | ---: |
| prediction_only | 0.00950587192 |
| existing | 0.00019929475 |
| raw_banks | 4.21242661e-17 |
| direction_strength | 4.26934722e-17 |

Maximum errors with row-bank information: raw 3.33e-16,
named 3.33e-16, against tolerance1e-10.
These conditional predictions account for decay and fixed priors; they do not
predict which outcome will arrive or establish calibrated uncertainty.

## Forecasting future control effects

Bank-minus-existing mean absolute error in64-observation target Brier effects:
**-0.000171 [-0.000212, -0.000128]** (negative favors bank information).
Bank effect-direction accuracy was **96.8%**, with
31/216 actual command effects exceeding .001 in magnitude.
All commands count, including actions the controller declined to take. Small/no
effects can inflate aggregate direction accuracy; coverage is separately required.

Intervals use5000 paired environment-cluster bootstrap samples. Outcomes within
an environment are averaged before resampling;72 states and288 branches are not
independent environment samples. Twelve environments give limited precision.

## Selecting controls

Positive differences below mean that bank-informed selection reduced target
Brier loss over the256-observation active window, relative to the named control.

| Control | Mean improvement [95% interval] | Positive environment means |
| --- | ---: | ---: |
| existing | +0.002126 [+0.001027, +0.003517] | 9/12 |
| no_op | +0.010560 [+0.008927, +0.012208] | 12/12 |
| disagreement | +0.008529 [+0.006094, +0.010805] | 11/12 |
| rotated | +0.010560 [+0.008927, +0.012208] | 12/12 |

Descriptive breakdowns; raw/named outcomes are identical. Unnecessary means an
action yielded no more than .001 actual target improvement; missed means abstaining
when one of the four tested commands would have improved by more than .001.
These classifications use hindsight only for evaluation, never for selection.

| History | Task | Policy | Gain vs no-op | Actions | Unnecessary | Missed |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| stable | local | existing | +0.000000 | 0/12 | 0 | 1 |
| stable | local | raw_banks | +0.000000 | 0/12 | 0 | 1 |
| stable | local | disagreement | +0.000000 | 0/12 | 0 | 1 |
| stable | composite | existing | -0.000063 | 1/12 | 1 | 0 |
| stable | composite | raw_banks | -0.000497 | 5/12 | 5 | 0 |
| stable | composite | disagreement | +0.000000 | 0/12 | 0 | 0 |
| forms | local | existing | +0.001300 | 5/12 | 1 | 7 |
| forms | local | raw_banks | +0.001300 | 5/12 | 1 | 7 |
| forms | local | disagreement | +0.001300 | 5/12 | 1 | 7 |
| forms | composite | existing | +0.001698 | 2/12 | 0 | 10 |
| forms | composite | raw_banks | +0.011680 | 11/12 | 0 | 1 |
| forms | composite | disagreement | +0.005457 | 5/12 | 0 | 7 |
| repeated | local | existing | +0.029185 | 11/12 | 0 | 1 |
| repeated | local | raw_banks | +0.029185 | 11/12 | 0 | 1 |
| repeated | local | disagreement | +0.000724 | 1/12 | 0 | 11 |
| repeated | composite | existing | +0.018485 | 5/12 | 0 | 7 |
| repeated | composite | raw_banks | +0.021690 | 6/12 | 0 | 6 |
| repeated | composite | disagreement | +0.004702 | 1/12 | 0 | 11 |

Target type is paired with proposal seed, so differences between local/composite
strata are descriptive, not a causal comparison of target types.

Failed preservation guards (mean cost>.01 or any case cost>.05 vs no-op):

| History | Window | Output | Mean cost | Maximum case cost |
| --- | --- | ---: | ---: | ---: |
| forms | returning | 2 | +0.010261 | +0.061120 |
| repeated | returning | 1 | +0.006707 | +0.069547 |
| repeated | returning | 2 | +0.012211 | +0.081746 |

## Frozen criteria

- mechanical: **True**
- information_forecast: **True**
- effect_direction: **True**
- steering_mean: **True**
- steering_consistency: **True**
- versus_no_op: **True**
- preservation: **False**

Exact contracts and information/steering usefulness are separate claims. No
failed criterion is repaired through new thresholds or a post-outcome rerun.
The [protocol](../../experiments/strength_inspection_protocol.md) specifies all
windows, instructions, baselines and limits.

## Verification, budgets and reader tasks

Three preflight fixture tests checked hidden allocation, empty banks, fixed priors,
clock alignment, equivalent encodings, read-only inspection and release/restore.
An independent implementation reconstructed worlds, acquisition, native forecasts,
reviews, final learning state, inspection quantities, commands and metrics.
The controller's iterative projection was checked with a closed-form recurrence.
Wrapper ledger metadata receives runtime round-trip checks, not a separately
implemented schema38 validator. There were9216 isolated
synthetic probe clones and576 trajectory checkpoint round trips.

Generated scalar labels: 368,640, including
materialized world futures beyond the evaluation horizon. Training label
presentations across reused acquisitions and branches:
944,640. Controller recent-data reuse:
13,824 scalar labels; synthetic
probe labels:27,648. These counts
are not independent evidence. Runner:87.25s;
audit:42.33s.

[Twelve blinded reader tasks](reader-tasks/README.md) are prepared but unscored.
They compare equivalent raw/named information, not unequal evidence access.
The assignment is a pilot task pack, not a completed randomized reader study;
future confirmation requires a fixed evaluator and fresh tasks.

The architecture/defaults and prior Heaviside failures remain unchanged. This is
not evidence of human/LLM comprehension, generally reliable steering, safety or
meta-learning. No further benchmark starts automatically.

Artifacts: [summary](results.json), [independent audit](audit.json),
[traces](runs.jsonl.gz), [worlds](worlds.json), [source manifest](manifest.json).
