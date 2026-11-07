# 037 — withdrawing recall and releasing explicit control

Completed 2026-11-06. All **240 runs independently reconstructed**. The evidence-withdrawal full empirical criterion **failed**. The first steering round ends with this study; no further experiment is started. The original default is unchanged.

## Primary comparison

Compared with current recall, evidence-triggered withdrawal improved immediate-rechange expected composite loss by **0.246703 nats**, positive in **10/20** familiar-return pairs. The target was .10 nats and 14/20. Whole-return gain over shadow was **0.021621 nats**, positive in **20/20** pairs; its target was .01 and 14/20.

| Prespecified criterion | Pass |
| --- | --- |
| rechange_mean | True |
| rechange_consistency | False |
| each_rechange_improves | True |
| retained_recall | True |
| useful_recall_mean | True |
| useful_recall_consistency | True |
| preservation | True |
| final_validity | True |
| active_parity | True |

These comparisons test withdrawal while preserving useful recall. They do not replace the failed early-recall criterion in 036. A benefit against current recall can coexist with a cost against never deploying memory.

## Predictions and validity

| History | Policy | Early return | Whole return/post-release | First 64 after rechange | Later | Final deployed / active valid | Withdrawals |
| --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| stable | shadow | 0.351355 | 0.352657 | 0.334066 | 0.332773 | 9/10 / 9/10 | 0 |
| stable | current | 0.348528 | 0.350882 | 0.333202 | 0.332695 | 9/10 / 9/10 | 0 |
| stable | command | 0.348528 | 0.350882 | 0.333915 | 0.332652 | 9/10 / 9/10 | 0 |
| stable | evidence | 0.349036 | 0.351303 | 0.333527 | 0.332685 | 9/10 / 9/10 | 25 |
| forms | shadow | 0.588389 | 0.481389 | 0.901295 | 0.492761 | 9/10 / 9/10 | 0 |
| forms | current | 0.582356 | 0.465734 | 0.982325 | 0.502890 | 9/10 / 9/10 | 0 |
| forms | command | 0.582356 | 0.465734 | 0.919729 | 0.495065 | 9/10 / 9/10 | 0 |
| forms | evidence | 0.582356 | 0.469524 | 0.919729 | 0.495065 | 9/10 / 9/10 | 20 |
| repeated | shadow | 0.764389 | 0.591165 | 1.142564 | 0.636865 | 9/10 / 9/10 | 0 |
| repeated | current | 0.756827 | 0.552539 | 1.668668 | 0.702628 | 9/10 / 9/10 | 0 |
| repeated | command | 0.756827 | 0.552539 | 1.237858 | 0.648777 | 9/10 / 9/10 | 0 |
| repeated | evidence | 0.756827 | 0.559787 | 1.237858 | 0.648777 | 9/10 / 9/10 | 20 |
| forms_persistent | shadow | 0.346764 | 0.342079 | 0.333960 | 0.339571 | 9/10 / 9/10 | 0 |
| forms_persistent | current | 0.346764 | 0.342079 | 0.333960 | 0.339571 | 9/10 / 9/10 | 0 |
| forms_persistent | command | 0.346764 | 0.342079 | 0.333960 | 0.339571 | 9/10 / 9/10 | 0 |
| forms_persistent | evidence | 0.346764 | 0.342079 | 0.333960 | 0.339571 | 9/10 / 9/10 | 0 |
| repeated_persistent | shadow | 0.348961 | 0.343499 | 0.335068 | 0.339856 | 9/10 / 9/10 | 0 |
| repeated_persistent | current | 0.348961 | 0.343499 | 0.335068 | 0.339856 | 9/10 / 9/10 | 0 |
| repeated_persistent | command | 0.348961 | 0.343499 | 0.335068 | 0.339856 | 9/10 / 9/10 | 0 |
| repeated_persistent | evidence | 0.348961 | 0.343499 | 0.335068 | 0.339856 | 9/10 / 9/10 | 0 |
| forms_other | shadow | 0.612544 | 0.495304 | 0.901774 | 0.483222 | 9/10 / 9/10 | 0 |
| forms_other | current | 0.612544 | 0.495304 | 0.901774 | 0.483222 | 9/10 / 9/10 | 0 |
| forms_other | command | 0.612544 | 0.495304 | 0.901774 | 0.483222 | 9/10 / 9/10 | 0 |
| forms_other | evidence | 0.612544 | 0.495304 | 0.901774 | 0.483222 | 9/10 / 9/10 | 0 |

Lower loss is better. All three channels, observed losses and active-only loss are in results.json. Stable, persistent and altered-return histories use the same fixed windows, without implying that they underwent a familiar return or rechange.

## Explicit block and release

All **60 command runs** executed the block after 1552 and release after 1664: **120 commands**, **0 blocked archive predictions**, block/release fidelity **True**. Active learning continued identically. Release did not revive the old authorization: output remained active through 1728, with any later recall requiring a fresh review.

The supplied command improved mean immediate-rechange composite loss by **0.246703 nats** versus current recall across the two returning histories. Its schedule deliberately follows the constructed change; this is a supplied instruction and timing advantage, not autonomous change detection. Command-arm costs and usefulness are separate from the primary evidence-controller verdict.

## What the controller actually did

All arms scored immutable archived probabilities before the main labels entered learning. Only the evidence arm could withdraw after a 16-observation window with mean archive loss more than .02 above active loss. Withdrawal affected subsequent predictions; it did not rewrite the 16th prediction. Ordinary fresh reviews could authorize recall again. Windows reset at review, incompatibility, non-recall, missing labels and explicit commands.

Exact active predictions, ordinary reviews and final active-learning states matched across policies, excluding intentional controller and audit metadata. Frozen capture, stored meanings and parameters were unchanged. Thus intervention differences are in authorization and output routing, not extra training or a veto on active learning.

| History | Current archive predictions | Evidence archive predictions | Evidence withdrawals | First-64 evidence cost vs shadow |
| --- | ---: | ---: | ---: | ---: |
| stable | 2432 | 1824 | 25 | -0.000539 |
| forms | 2304 | 1616 | 20 | 0.018434 |
| repeated | 2752 | 1984 | 20 | 0.095295 |
| forms_persistent | 0 | 0 | 0 | 0.000000 |
| repeated_persistent | 0 | 0 | 0 | 0.000000 |
| forms_other | 0 | 0 | 0 | 0.000000 |

## Consistency and intervention opportunity: descriptive check

The immediate-rechange comparison has 10 gains, 10 ties and 0 losses. Current recall supplied at least one prediction in this window in 10/20 pairs.

| History | Seed / proposal | Current recalled predictions | Evidence recalled predictions | Withdrawal ticks | Gain |
| --- | --- | ---: | ---: | --- | ---: |
| forms | 2600 / 2600 | 0 | 0 | [] | 0.000000 |
| forms | 2600 / 2601 | 64 | 16 | [1552] | 0.186545 |
| forms | 2601 / 2600 | 0 | 0 | [] | 0.000000 |
| forms | 2601 / 2601 | 0 | 0 | [] | 0.000000 |
| forms | 2602 / 2600 | 0 | 0 | [] | 0.000000 |
| forms | 2602 / 2601 | 0 | 0 | [] | 0.000000 |
| forms | 2603 / 2600 | 0 | 0 | [] | 0.000000 |
| forms | 2603 / 2601 | 0 | 0 | [] | 0.000000 |
| forms | 2604 / 2600 | 64 | 16 | [1552] | 0.219872 |
| forms | 2604 / 2601 | 64 | 16 | [1552] | 0.219548 |
| repeated | 2600 / 2600 | 64 | 16 | [1552] | 0.616174 |
| repeated | 2600 / 2601 | 64 | 16 | [1552] | 0.651577 |
| repeated | 2601 / 2600 | 0 | 0 | [] | 0.000000 |
| repeated | 2601 / 2601 | 0 | 0 | [] | 0.000000 |
| repeated | 2602 / 2600 | 64 | 16 | [1552] | 0.639866 |
| repeated | 2602 / 2601 | 0 | 0 | [] | 0.000000 |
| repeated | 2603 / 2600 | 64 | 16 | [1552] | 0.555476 |
| repeated | 2603 / 2601 | 64 | 16 | [1552] | 0.554169 |
| repeated | 2604 / 2600 | 64 | 16 | [1552] | 0.629080 |
| repeated | 2604 / 2601 | 64 | 16 | [1552] | 0.661753 |

This is a post-outcome explanation of the fixed result, not a replacement denominator. The prespecified consistency requirement remains failed. Where no recall was active, there was no stale authorization to withdraw in this window. The comparison still includes those pairs. The scheduled command and evidence controller produced the same immediate-rechange gains on this batch; fixed phase/review alignment limits extrapolation to other timings.

The evidence monitor also withdrew recall in stable tasks. Those withdrawals need not diagnose an environmental change: they compare recent prediction losses and can respond to noise or calibration differences. The preservation guards, rather than an assumed perfect detector, assess their cost.

## Failed guards

| Guard | History | Comparator | Window | Channel | Mean cost | Worst cost |
| --- | --- | --- | --- | ---: | ---: | ---: |
| None | | | | | | |

Useful-recall allowances are .01 mean/.05 individual versus current; general preservation allowances are .02/.10 against both current and shadow. Immediate-rechange absolute costs are shown separately above, not bounded by the longer-window preservation criterion. Endpoint success cannot erase trajectory costs.

## Integrity and scope

Runner 202.8s; independent auditor 147.5s. All caps passed; 1553 frozen dependencies unchanged. Four fixture groups passed on the first attempt: 266240 reused training presentations and 255 synthetic scalar presentations, with no fresh random labels. The audit reconstructed streams, every prediction/review, archive qualification, monitor losses and decisions, external commands, checkpoint hashes, outcome measurements and final learning-state parity.

Five environment seeds, two proposal draws and shared histories remain correlated. Capture timing, language of distinctions, role assignment, review cadence, thresholds and explicit command timing are supplied. This is a small controller comparison, not meta-learning, general reliable steering, human comprehension testing or a safety guarantee. The round synthesis records the result alongside earlier positive and negative findings without combining their different variants into one claimed superior learner.

Fresh-run accounting:

- runs: 240
- generated_labels: 307200
- used_labels: 2457600
- candidate_fits: 241588
- scoring_queries: 8362240
- raw_bin_visits: 43076416
- main_predictions: 1474560
- grid_predictions: 491520
- extra_decay_cell_visits: 3932160
- memory_diagnostic_queries: 399360
- archive_prediction_queries: 19440
- monitor_queries: 368640

Main archive predictions, monitoring queries, review-memory scoring and evaluation grids are counted separately. Audit replay adds 2457600 reused training presentations, no new labels. Inspection excerpts are derived from existing traces without new learning.

[Frozen protocol](../../experiments/recall_withdrawal_protocol.md) · [Independent audit](audit.json) · [Results and all pairs](results.json) · [Command/monitor excerpts](descriptive.json) · [First-round synthesis](../steering-round-one-synthesis.md)
