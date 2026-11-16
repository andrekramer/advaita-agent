# Direction, strength and steering one learned distinction

**Research decision, 13 November 2026. Adopt the direction/strength view and the uncapped, meaning-bound cell command as the working architecture for the next bounded research round.** “Uncapped” refers to evidence mass. The command still closes when the selected distinction changes meaning or the scheduled 256 ticks elapse. A script supplies the instruction and selects a cell from its past observations. [Implementation](../../advaita/direction_strength.py) · [Frozen confirmation protocol](../../experiments/cell_duration_protocol.md)

## Confirmation of the three project aims

| Aim | Result on fresh environments |
| --- | --- |
| Can learn | With commands off, native forecasts, reviews and learning checkpoints matched the consolidated learner exactly. Across the three changed histories, continued learning improved Brier loss by 0.26607 against a frozen acquired predictor. All 12 environments produced a useful local split and met the 87.5% upper transfer criterion in at least one of two acquisitions. |
| Can interpret | On the three replicated control contrasts, the script correctly classified 581 of 720 short-term effects. Among 222 material effects, it got 187 directions right using the selected cells' fast/slow evidence and 105 using proportional allocation from channel totals. Mean absolute effect error fell from 0.001070 to 0.000892. Named directions and strengths reproduced raw-count forecasts within 1e-12. |
| Can steer | The uncapped cell command improved active target Brier by 0.001636 [0.001223, 0.002135] over abstention, above the 0.001 floor. The controller acted on 130 of 240 instructions. All mean and individual preservation checks passed. Its worst monitored case cost was 0.01512 against the 0.05 limit. |

The inference units are 12 new environments. Two proposal draws, five histories and both local and composite instructions yield 240 cases and 1,200 paired continuations. Intervals use 5,000 paired bootstrap samples of environment means. The lasting and returning polarity shifts share their observations during the active window. Earlier acquisition failures still matter when interpreting the 12/12 transfer result on this set. [First trial](../direction-strength-v1/findings.md)

## What a cell command bought

| Extra plasticity | Target Brier gain over abstention [95% interval] | Worst monitored cost | Failed preservation checks |
| --- | ---: | ---: | ---: |
| Whole channel | 0.007838 [0.006771, 0.008860] | 0.068268 | 2 |
| Selected cell, up to 256 ticks | 0.001636 [0.001223, 0.002135] | 0.015124 | 0 |
| Selected cell, 25% mass budget | 0.001267 [0.000882, 0.001742] | 0.015060 | 0 |
| Selected cell, 63 ticks | 0.001277 [0.000892, 0.001752] | 0.015089 | 0 |

Of the 130 uncapped commands, 104 closed on a change of meaning and 26 reached scheduled expiry. The effect varied with the history. The controller acted on 39 of 48 misleading bursts, where mean target gain was −0.000253. The lasting and returning polarity shifts each gained 0.004063 during intervention. At the end of polarity return, only 22.9% of uncapped cases recovered both true local partitions and upper modal accuracy averaged 69.7%. The preservation checks measure additional harm relative to abstaining. Structural recovery remains a separate problem.

## The matched-duration comparison

Every budget exhausted and every matched command expired on tick 703, after 63 observations. In each of the 130 exposed cases the two arms made identical predictions through tick 702. The budget took 16.0024% of the duration arm's final extra debit. The first review opportunity was tick 704. The fraction follows from multiplicative slow decay with a budget proportional to starting mass during an interval without migration.

The fixed-duration arm gained 0.0000101 more active target Brier than the budgeted arm [0.0000089, 0.0000113]. The whole interval lies inside the predeclared ±0.0001 practical equivalence margin. The largest absolute release or return difference for any case/output was 0.0000604 against a 0.005 limit. The budget and timer therefore met both equivalence checks on this schedule. The maximum individual probability difference across their trajectories was 0.000640. A schedule with migration during the budget window could yield a different result.

## Verification and reproduction

The runner checked command-off native parity, checkpoint restoration, equivalent encodings, and one-step outcomes on cloned learners. The largest one-step or debit discrepancy was 1.38 × 10⁻¹⁴. The separate scoring audit recomputed Brier outcomes on 614,400 observations, checked timing and reconciled 33,596 debit events. Native runtime parity and clone probes are runner checks. All evaluations were scripted. [Numerical results](summary.json) · [Audit](audit.json) · [Predictions and command events](cases.jsonl.gz) · [Source hashes](manifest.json)

Reproduce in an unused directory with `python3 experiments/cell_duration_confirmation.py --output /tmp/advaita-cell-duration-replay` and then `python3 checks/audit_cell_duration.py --output /tmp/advaita-cell-duration-replay`.
