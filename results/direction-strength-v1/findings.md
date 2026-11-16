# Direction and strength as a steering architecture

**Decision, 13 November 2026. Carry forward the per-cell inspection interface and pursue meaning-bound cell steering. Defer the architecture pivot.** The budgeted candidate met the scripted interpretation criterion and every preservation limit. Two other predeclared requirements failed, one at acquisition and one during steering. [Protocol](../../experiments/direction_strength_protocol.md) · [Measured outcomes](summary.json)

Eight fresh environment seeds supplied stable, misleading-burst, lasting-reversal, polarity-return and form-return histories. Each of two proposal seeds received both a local and a composite instruction. This produced 160 cases and 640 cloned continuations. Each intervention arm used the same decision, past evidence and future observations. Stable and burst histories share most outcomes. The lasting and polarity-return histories are identical through the active interval and diverge on return. All intervals resample the eight environment means.

## Can the candidate learn?

With commands off, the prototype exactly reproduced the consolidated learner's forecasts, review decisions and native checkpoints on every paired trunk and continuation. During the active interval of the three changed histories, continued learning reduced mean Brier loss by 0.27033 against the frozen acquired predictions, averaged across all three outputs. Every environment exhibited a local split that improved prediction on later stable observations relative to pooling its evidence.

Seven of eight environments also reached the required 87.5% upper accuracy on held-out input combinations in at least one acquisition. Environment 3204 reached at most 66.7% across its two proposal seeds. This failure preceded the intervention. Recovery is another limitation. At the last evaluation after a polarity return, budgeted branches averaged 76.8% upper modal accuracy across the 32 contexts and none recovered both true local partitions. Passing a relative preservation limit can coexist with poor absolute recovery in both the controlled and abstaining learners.

## Can a script interpret the update?

The direction/strength view identified the outcomes of 122 of 148 material command effects as improvement or harm in the correct direction. The proportional allocation of channel-wide bank totals gave 82 of 148 on the same decisions. Across all 480 effects the richer script correctly classified 404, with a mean absolute Brier-effect error of 0.000778 against 0.001159 for the proportional approximation. Equivalent raw counts reproduced the named forecasts within the declared tolerance.

At the decision point cloned one-step probes checked both possible labels. Over those probes and all live debit checks the maximum numerical discrepancy was 1.4 × 10⁻¹⁴. The scoring audit reconciled 14,070 debit events to the ordinary decay, observed before/after slow masses and remaining allowance. The comparison evaluates a supplied script under a fixed control vocabulary.

## Can a supplied instruction steer learning?

Gains below are reductions in mean target-channel Brier loss over the 256 active ticks against abstention. This scores all target-channel observations, including those outside the selected cell. The cost column is the largest case-level increase in any monitored protected, stable or post-release output. The paired intervals are 95% environment bootstrap intervals.

| Scope of plasticity | Mean target gain [interval] | Gain on originally selected members | Largest monitored case cost | Preservation |
| --- | ---: | ---: | ---: | --- |
| Whole channel | 0.008408 [0.006026, 0.010609] | 0.008961 | 0.079234 | Two limits exceeded |
| One cell, uncapped | 0.001204 [0.001013, 0.001409] | 0.004515 | 0.008573 | All limits met |
| One cell, 25% budget | 0.000940 [0.000786, 0.001079] | 0.004000 | 0.005498 | All limits met |

Addressing one distinction reduced both benefit and collateral cost. Adding the budget reduced mean target gain a further 0.000264 [0.000160, 0.000371]. For the budgeted candidate the predeclared target was 0.001 mean improvement. Its point estimate missed, despite a positive lower interval bound. The uncapped cell arm cleared that numerical floor and preserved the monitored outputs in this comparison. It was a planned comparator. A promotion decision for that arm would require its own confirmation.

The controller acted in 74 of 160 cases, including 21 of 32 misleading-burst cases and none of the stable cases. All 74 budgets exhausted after exactly 63 ticks. The first scheduled review was 64 ticks after opening. Before that review, the selected slow store receives no migration and its decay is multiplicative. With a budget proportional to initial mass, the cumulative extra debit as a fraction of initial mass is the same across starting masses. The fixed budget therefore behaved like a common duration here, with a partial debit on its final tick. A 63-tick duration control is needed to attribute a distinct benefit to strength budgeting. Of the uncapped cell commands, 57 closed on a change of meaning and 17 reached expiry.

The next decision can focus on whether a meaning-bound cell command with no mass cap reproduces its benefit and preservation on fresh worlds. Include a matched-duration arm if testing the mass cap again. Keep the failed transfer case as a separate learning issue.

## Reproduction and verification

The prototype exposes a bank's direction and retained strength at a semantic cell address. It applies extra decay only to contributing raw bins, closes on exhaustion, release, expiry or changed meaning, and restores an in-flight command from checkpoint. The trial uses shadow recall and fixed binary poles. [Prototype](../../advaita/direction_strength.py)

Run the contract fixtures with `python3 checks/test_direction_strength.py`. Reproduce the simulation in a fresh output directory using `python3 experiments/direction_strength_trial.py --output /tmp/advaita-direction-strength-replay` with a previously unused path. The saved audit independently rescored 327,680 observations and checked spending, bootstrap contrasts and the three decisions. It relies on the trial's native parity checks and cloned probes for runtime behaviour. [Source manifest](manifest.json) · [Per-case predictions and events](cases.jsonl.gz) · [Audit](audit.json)
