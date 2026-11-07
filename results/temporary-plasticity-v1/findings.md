# 035 — temporary downstream plasticity

Completed 2026-11-06. All **250 runs independently reconstructed**. The primary full empirical criterion **failed**. The original default is unchanged.

## Primary outcome

G active expected composite gain over protection-only P: **0.075449 nats**, positive in **40/40** changing pairs. Early-return gain over long-boost D512: **-0.023147 nats**, positive in **2/20** returning pairs.

| Prespecified criterion | Pass |
| --- | --- |
| adaptation_preserved | True |
| active_gain | True |
| active_consistency | True |
| early_gain | False |
| early_consistency | False |
| each_return_improves | False |
| preservation | False |
| protection | True |
| final_validity | True |

## Expected composite loss and endpoint validity

Each row averages ten paired runs. Lower loss is better. Early-return is a post-release window for persistent tasks and a control window for stable tasks. Validity is a final snapshot, not a measure of recovery speed.

| History | Policy | Active | Early return/post-release | Whole return/post-release | Later | Final valid | Mean boost ticks |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable | P | 0.333774 | 0.340035 | 0.336567 | 0.330930 | 10/10 | 0.0 |
| stable | D128 | 0.335996 | 0.341345 | 0.337647 | 0.331460 | 10/10 | 128.0 |
| stable | D256 | 0.337708 | 0.342512 | 0.338571 | 0.331716 | 10/10 | 256.0 |
| stable | D512 | 0.339390 | 0.346759 | 0.341411 | 0.332060 | 10/10 | 512.0 |
| stable | G | 0.335996 | 0.341345 | 0.337647 | 0.331460 | 10/10 | 128.0 |
| forms | P | 0.602472 | 0.587046 | 0.489132 | 0.503457 | 10/10 | 0.0 |
| forms | D128 | 0.576974 | 0.601040 | 0.499714 | 0.503005 | 10/10 | 128.0 |
| forms | D256 | 0.564388 | 0.604689 | 0.502823 | 0.501008 | 10/10 | 256.0 |
| forms | D512 | 0.561608 | 0.596422 | 0.491225 | 0.504822 | 10/10 | 512.0 |
| forms | G | 0.562561 | 0.605862 | 0.500319 | 0.502550 | 10/10 | 345.6 |
| repeated | P | 0.818851 | 0.670176 | 0.543385 | 0.636594 | 9/10 | 0.0 |
| repeated | D128 | 0.743996 | 0.743821 | 0.589809 | 0.614476 | 10/10 | 128.0 |
| repeated | D256 | 0.715822 | 0.797254 | 0.633662 | 0.600317 | 10/10 | 256.0 |
| repeated | D512 | 0.707450 | 0.772068 | 0.601588 | 0.615158 | 10/10 | 512.0 |
| repeated | G | 0.707863 | 0.808922 | 0.637113 | 0.600927 | 10/10 | 390.4 |
| forms_persistent | P | 0.602472 | 0.367542 | 0.360176 | 0.341074 | 10/10 | 0.0 |
| forms_persistent | D128 | 0.576974 | 0.360081 | 0.354852 | 0.342558 | 10/10 | 128.0 |
| forms_persistent | D256 | 0.564388 | 0.354035 | 0.349809 | 0.340341 | 10/10 | 256.0 |
| forms_persistent | D512 | 0.561608 | 0.347008 | 0.343672 | 0.336976 | 10/10 | 512.0 |
| forms_persistent | G | 0.562561 | 0.349727 | 0.346276 | 0.338580 | 10/10 | 345.6 |
| repeated_persistent | P | 0.818851 | 0.412740 | 0.386602 | 0.342274 | 10/10 | 0.0 |
| repeated_persistent | D128 | 0.743996 | 0.370239 | 0.360800 | 0.339622 | 10/10 | 128.0 |
| repeated_persistent | D256 | 0.715822 | 0.361865 | 0.355823 | 0.339123 | 10/10 | 256.0 |
| repeated_persistent | D512 | 0.707450 | 0.346863 | 0.343858 | 0.334394 | 10/10 | 512.0 |
| repeated_persistent | G | 0.707863 | 0.350017 | 0.346545 | 0.335520 | 10/10 | 390.4 |

## Closure and fixed-pulse comparisons

| History | G closures (tick: count) |
| --- | --- |
| stable | 640: 10 |
| forms | 768: 3, 832: 2, 896: 3, 960: 2 |
| repeated | 832: 1, 896: 7, 960: 2 |
| forms_persistent | 768: 3, 832: 2, 896: 3, 960: 2 |
| repeated_persistent | 832: 1, 896: 7, 960: 2 |

Closure at 1024 is recorded as the supplied ceiling, even if the last batch also meets the adequacy condition. Opening at 512, the ceiling, and the protected role are supplied. This is a fixed evidence-responsive rule, not learned control.

| Secondary pulse | Full bundle | Active gain over P | Early-return gain over D512 |
| --- | --- | ---: | ---: |
| D128 | False | 0.050177 (40/40 positive) | 0.011814 (14/20 positive) |
| D256 | False | 0.070557 (40/40 positive) | -0.016727 (3/20 positive) |

| History | G compared with | Active gain | Early-return gain | Later gain |
| --- | --- | ---: | ---: | ---: |
| stable | D128 | 0.000000 | 0.000000 | 0.000000 |
| stable | D256 | 0.001712 | 0.001166 | 0.000256 |
| forms | D128 | 0.014413 | -0.004822 | 0.000456 |
| forms | D256 | 0.001827 | -0.001173 | -0.001541 |
| repeated | D128 | 0.036133 | -0.065101 | 0.013549 |
| repeated | D256 | 0.007959 | -0.011668 | -0.000610 |
| forms_persistent | D128 | 0.014413 | 0.010354 | 0.003978 |
| forms_persistent | D256 | 0.001827 | 0.004308 | 0.001761 |
| repeated_persistent | D128 | 0.036133 | 0.020222 | 0.004103 |
| repeated_persistent | D256 | 0.007959 | 0.011848 | 0.003603 |

Positive here means lower loss for G. These comparisons are not exposure-matched. A secondary pulse cannot become a retrospective primary success.

## Guard failures

| Kind | History | Comparator | Window | Channel | Mean cost | Worst pair cost |
| --- | --- | --- | --- | ---: | ---: | ---: |
| Preservation | repeated | P | returning | 2 | 0.093728 | 0.160052 |
| Preservation | repeated | P | early_return | 2 | 0.138747 | 0.231368 |
| Preservation | repeated | D512 | returning | 2 | 0.035525 | 0.069415 |

## Interpretation and next decision

The evidence-based closure retained the active adaptation benefit but did not improve return. The shortest pulse improved pooled early return modestly, below the declared .02-nat threshold, and exceeded the allowed adaptation cost in both reversal histories. No tested duration policy passed the full bundle. Do not promote the controller or tune its threshold on these outcomes.

Restoring a slower decay rate does not restore earlier knowledge. It can also make recently acquired evidence more persistent. That is a candidate explanation for slower recovery here, not an isolated causal finding. In a post-outcome descriptive check of saved tick-1024 predictors, G had more composite slow evidence than D512 and slightly better original-map predictions, yet subsequently recovered more slowly. An endpoint snapshot therefore does not determine the recovery trajectory. Upper search and migration remain possible contributors.

| Returning history | Policy | Original-map loss at 1024 | Composite slow mass | Raw interfaces |
| --- | --- | ---: | ---: | ---: |
| forms | P | 0.872822 | 111.809 | 3/10 |
| forms | D128 | 0.911049 | 117.692 | 1/10 |
| forms | D512 | 0.987257 | 60.700 | 2/10 |
| forms | G | 0.960550 | 96.033 | 2/10 |
| repeated | P | 1.104661 | 84.707 | 9/10 |
| repeated | D128 | 1.335638 | 78.569 | 7/10 |
| repeated | D512 | 1.612148 | 56.006 | 0/10 |
| repeated | G | 1.566173 | 79.574 | 0/10 |

This descriptive check only rescores saved predictions; it adds no training or fresh labels and did not select a controller. Next, prepare the separate one-slot preserved-predictor study contemplated by the plan: matched no-archive/shadow/use conditions, semantic compatibility, fresh evidence admission and defined persistence through refits. That study is not implemented or launched here.


## Integrity and scope

Runner 162.8s; independent auditor 129.5s. All resource caps passed. 1518 frozen dependency files remain unchanged.

The frozen auditor first stopped at run 115 on a checkpoint hash: its log1p arithmetic differed from the runtime log arithmetic by at most 1.11e-16 nats. The failed attempt is preserved. A separate serialization supplement uses the runtime operation only for the controller loss being serialized; it leaves all learning, world and outcome logic intact. No adequacy decision changes across 2000 batches (nearest threshold margin 0.000993888). The supplement then independently replays all 250 runs. No learner, frozen source, world or experiment result was changed. This is a disclosed post-outcome auditor correction.

The auditor independently rebuilt worlds, controller decisions, every prediction/review, intermediate snapshot, final evidence state, checkpoint hashes, costs and outcome gates. Returning and persistent histories match through the intervention window. Results include all acquisitions and all pairs. No thresholds or durations were tuned after outcomes.

The 40 changing active-window records include 20 distinct return/persistent paired trajectories, duplicated before those histories diverge at 1025. Five environment seeds and two proposal seeds are correlated within histories; counts are descriptive, not independent statistical evidence. The misleading burst, supplied role, fixed opening/deadline, small discrete world family and one adequacy threshold limit the claim. No autonomous opening, archive integration, meta-learning or safety advantage was tested.

The first fixture attempt passed: 112640 reused-world training presentations, 6912 synthetic scalar presentations, no fresh random labels. The preceding diagnosis only rescored stored predictors. Fresh-run accounting:

- runs: 250
- generated_labels: 256000
- used_labels: 2560000
- candidate_fits: 251773
- scoring_queries: 8710592
- raw_bin_visits: 44872816
- main_predictions: 1536000
- grid_predictions: 256000
- extra_decay_cell_visits: 1945600
- controller_queries: 64000

Audit replay accounting is separate from training: the failed attempt examined 115 runs (1177600 replayed training presentations), and the full corrected audit examined 250 (2560000). The supplement also rescored 2000 saved diagnostic batches (64000 predictions), with no learning or new labels. The failed auditor did not persist exact elapsed time; its 900-second alarm did not fire.

Controller queries are additional to ordinary scoring; each composite query computes three scalar channels. Grid counts are contexts, each with three channels. Inherited acquisition evaluation is logged separately.

[Frozen protocol](../../experiments/temporary_plasticity_protocol.md) · [Independent audit](audit.json) · [Results and all guards](results.json) · [Prior diagnosis](../downstream-retention-diagnosis/findings.md)
