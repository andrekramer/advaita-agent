# 036 — preserved prediction helps some returns, but recall remains unreliable

Completed 2026-11-06. All **180 runs passed independent reconstruction**. The full empirical criterion **failed**. No default change or additional experiment.

Recall reduced mean early-return expected composite loss by **0.011777 nats**, with **6/20** improving pairs. The requirements were .02 nats and 14/20. Both returning histories improved on average, but the mean benefit and consistency requirements failed. A later reversal cost also exceeded the preservation limits.

## What was tested

All three arms used the same continuing learner and downstream boost. A single predictor was nominated after review 384 and confirmed against two later fresh batches. Discard deleted it; shadow retained/scored it without deployment; recall could use its frozen numerical predictions after an adequate, improving fresh score and matching input meanings. Active learning continued unchanged. The archive could neither block an update nor be overwritten by ordinary refits.

This is a compositional output alternative, not restoration of the active learner or faster representation learning. Input meaning checks are strict; the stored predictor cannot silently reinterpret current category IDs. Admission lasts until the next review, with compatibility checked on each prediction.

## Outcomes

| Prespecified criterion | Pass |
| --- | --- |
| mean_recall_gain | False |
| recall_consistency | False |
| each_return_improves | True |
| preservation | False |
| final_validity | True |
| control_parity | True |

| History | Policy | Active loss | Early return/post-release | Whole return/post-release | Later | Deployed / active final valid |
| --- | --- | ---: | ---: | ---: | ---: | --- |
| stable | discard | 0.338625 | 0.338374 | 0.336005 | 0.340145 | 10/10 / 10/10 |
| stable | shadow | 0.338625 | 0.338374 | 0.336005 | 0.340145 | 10/10 / 10/10 |
| stable | recall | 0.336872 | 0.337988 | 0.334941 | 0.339791 | 10/10 / 10/10 |
| forms | discard | 0.572207 | 0.581848 | 0.477702 | 0.509067 | 10/10 / 10/10 |
| forms | shadow | 0.572207 | 0.581848 | 0.477702 | 0.509067 | 10/10 / 10/10 |
| forms | recall | 0.572207 | 0.565881 | 0.454227 | 0.527681 | 10/10 / 10/10 |
| repeated | discard | 0.704403 | 0.752156 | 0.584077 | 0.648654 | 8/10 / 8/10 |
| repeated | shadow | 0.704403 | 0.752156 | 0.584077 | 0.648654 | 8/10 / 8/10 |
| repeated | recall | 0.704403 | 0.744568 | 0.546452 | 0.748473 | 8/10 / 8/10 |
| forms_persistent | discard | 0.572207 | 0.347878 | 0.342593 | 0.337941 | 10/10 / 10/10 |
| forms_persistent | shadow | 0.572207 | 0.347878 | 0.342593 | 0.337941 | 10/10 / 10/10 |
| forms_persistent | recall | 0.572207 | 0.347878 | 0.342593 | 0.337941 | 10/10 / 10/10 |
| repeated_persistent | discard | 0.704403 | 0.350776 | 0.344355 | 0.338607 | 10/10 / 10/10 |
| repeated_persistent | shadow | 0.704403 | 0.350776 | 0.344355 | 0.338607 | 10/10 / 10/10 |
| repeated_persistent | recall | 0.704403 | 0.350776 | 0.344355 | 0.338607 | 10/10 / 10/10 |
| forms_other | discard | 0.572207 | 0.594446 | 0.484285 | 0.503329 | 10/10 / 10/10 |
| forms_other | shadow | 0.572207 | 0.594446 | 0.484285 | 0.503329 | 10/10 / 10/10 |
| forms_other | recall | 0.572207 | 0.594446 | 0.484285 | 0.503329 | 10/10 / 10/10 |

Losses are expected composite log loss; lower is better. Persistent and altered-return windows are not familiar returns. All three output channels and observed loss are retained in results.json.

## Preservation and actual recall

Every seed/proposal pair confirmed its snapshot, including all 20 familiar-return pairs. Shadow and discard produced exactly identical online predictions. Across all three arms, active predictions, ordinary reviews and final learning state were identical. The independent audit excludes archive/audit metadata when comparing that learning state. Thus measured differences come from routed predictions rather than selection blocking or extra training.

| History | Confirmed /10 | Eligible reviews | Admitted reviews | Actual archived main predictions | Blocked mid-interval predictions |
| --- | ---: | ---: | ---: | ---: | ---: |
| stable | 10 | 233 | 47 | 3008 | 0 |
| forms | 10 | 54 | 42 | 2688 | 0 |
| repeated | 10 | 49 | 43 | 2752 | 0 |
| forms_persistent | 10 | 0 | 0 | 0 | 0 |
| repeated_persistent | 10 | 0 | 0 | 0 | 0 |
| forms_other | 10 | 0 | 0 | 0 | 0 |

Permanent changes and altered-category returns produced no archive deployment and exactly matched their controls. This reflects exclusion by the supplied compatibility rule in these runs; it does not establish that loss-based admission alone rejects misleading memory. Stable tasks also sometimes used the frozen predictor, with small mean improvements and passing guards.

## What limited recall: post-outcome trace diagnosis

Capture did not limit this batch. Every familiar-return run eventually used its archive, but only six began early enough to improve the declared early-return window: four category-return pairs and two polarity-return pairs. These were exactly the six positive pairs. The other 14 tied in that window. Returning input meanings generally became compatible only after substantial active relearning; one polarity pair also waited a further review after first becoming eligible. Changing the primary window afterwards would conceal that delay.

| History | Pairs with early recall | Routed immediately before rechange | Mean cost, first 64 after rechange | Mean cost, remaining 448 |
| --- | ---: | ---: | ---: | ---: |
| forms | 4/10 | 6/10 | 0.148912 | 0.000000 |
| repeated | 2/10 | 10/10 | 0.798554 | 0.000000 |

All ten polarity-return runs authorized the old predictor at review 1536, just before the environment changed again. The predictor remained authorized until the next review; input meanings had not yet triggered mid-interval exclusion. Its additional later loss is confined to that first 64-record interval. Fresh evidence from the preceding regime was insufficient to guarantee usefulness in the next one. The active predictor was already updating during this interval.

This localizes two different issues: recovering the meanings a stored predictor needs, and revoking a predictor when evidence changes between reviews. It does not show that a larger archive would fix either. The descriptive diagnosis rescored saved predictions only; no new learning, tuning or outcomes were introduced.

## Failed preservation guard

| History | Window | Channel | Mean cost | Worst pair cost |
| --- | --- | ---: | ---: | ---: |
| repeated | later | 2 | 0.099819 | 0.111961 |

The allowed mean cost was .02 and each-pair cost .10. All other prespecified preservation guards passed. Final validity passed, with 8/10 polarity endpoints and 10/10 elsewhere in both active and deployed predictors; this does not erase earlier trajectory costs.

## Next question, not started

The smallest follow-up would keep capture and memory capacity fixed while testing withdrawal of recall within a review interval against the present fixed authorization. A separate question is whether a preserved predictor should retain an independently usable encoding of its inputs, rather than wait for the active learner to recreate compatible meanings. That would change what is stored and requires a separate design. Neither intervention is implemented or tested here. No controller or architecture is promoted.

## Verification and limits

Runner 125.6s; independent audit 112.0s. All caps passed; 1537 frozen dependency files remain unchanged. The first fixture attempt passed with 194560 reused training presentations and 1632 synthetic scalar presentations; no fresh random fixture labels. The audit reconstructed every world, prediction, review, memory event, immutable snapshot, control, checkpoint, metric and summary, including exact stored-loss arithmetic.

The capture schedule, candidate language, stable local role, boost schedule, thresholds, review period and raw symbol meanings are supplied. Worlds and proposal draws are correlated within histories; five environment seeds are not broad task-family generalization. The experiment establishes durable stored-prediction use in some circumstances, not reliable recall, active representation repair, meta-learning or a safety advantage.

Fresh-run accounting:

- runs: 180
- generated_labels: 307200
- used_labels: 1843200
- candidate_fits: 181242
- scoring_queries: 6269280
- raw_bin_visits: 32306544
- main_predictions: 1105920
- grid_predictions: 368640
- extra_decay_cell_visits: 2949120
- memory_diagnostic_queries: 299520
- archive_prediction_queries: 8448

Archive prediction counts exclude separately counted review-grid and diagnostic work. Grid counts are contexts across both active and routed evaluations. Audit replay is separate: 1843200 training presentations, with no newly generated labels. Post-outcome diagnosis compared 10240 saved prediction pairs, also without training.

[Frozen protocol](../../experiments/preserved_prediction_protocol.md) · [Independent audit](audit.json) · [Full results](results.json) · [Trace diagnosis](descriptive.json) · [Controller documentation](../../docs/preserved-prediction.md)
