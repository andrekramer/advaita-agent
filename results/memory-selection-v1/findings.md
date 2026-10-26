# Experiment 022: independent memory admission helps, but remains inconsistent

Completed 2026-10-26. All **80 runs** passed independent reconstruction of
streams, predictions, structural decisions, evidence records and complete
checkpoints. **The primary criterion failed:** independent admission reduced
mean early-return loss by .045996 nats versus ignoring memory, but improved
only 4/10 pairs, requiring eight. Every other prespecified guard passed.
No benchmark was tuned or repeated.

## Separating two effects of memory

Experiment 021 showed that an archive could block a fresh candidate without
being retrieved. The [new protocol](../../experiments/memory_selection_protocol.md)
compared four policies with identical prospective snapshot qualification,
local learning and supplied candidate language:

| Policy | How stored memory can affect a review |
| --- | --- |
| Shadow | Store and score memory, but ignore it in decisions. |
| Veto | Let memory compete in main-buffer ranking; if it wins, suppress ordinary replacement without retrieving it or trying a fallback. |
| Joint | The previous reserve behavior: rank fitted candidates and memory together, then test only the winner on fresh evidence. |
| Separate | Test the best fitted candidate and eligible memory separately, then choose the lower fresh-loss candidate that passes. |

Every policy scored both available challengers; unused scores did not influence
shadow, veto or joint. All used the same acceptance thresholds, reduction rule,
meaning checks and subsequent online refitting. Separate has two selection
opportunities on one fresh batch, not an additional independent confirmation.
Its benefit is assessed on subsequent online predictions.

Five fresh environment seeds with two proposal draws each supplied ten pairs
per history. Detail matters, disappears, then returns either unchanged or
with opposite outcomes. Histories share their first 528 observations. These
are five environment realizations, not ten independent worlds. The fixed
curriculum, 1280-record horizon and 10% noise match 021.

## Prespecified outcome

Early return covers records 529–656; pre-return covers 1–528. Positive loss
reduction means the treatment performed better than its control.

| Detail-return comparison | Mean observed loss reduction | Improved / tied / worse pairs |
| --- | ---: | ---: |
| Veto versus shadow: competition without retrieval | −.007710 | 0 / 9 / 1 |
| Joint versus veto: reinstatement under joint ranking | +.001383 | 1 / 7 / 2 |
| Separate versus shadow: memory with independent admission | +.045996 | 4 / 5 / 1 |
| Separate versus joint: changing the admission rule | +.052323 | 4 / 6 / 0 |

Separate reduced mean detail early loss from .811878 to .765882 versus shadow.
The latent loss reduction was .045506 nats. The mean-benefit threshold of .02
passed, but the required 8/10 improving pairs did not. Over the full return
period, observed loss fell by .010160 nats. Late loss differences were tiny;
this was principally an adaptation benefit.

Separate and shadow had identical pre-return predictions, hence zero pre-return
cost. Separate also avoided joint's .001834 observed pre-return loss cost.
When outcomes reversed, separate increased mean early loss by .013116 nats
versus shadow and .007321 versus joint, both below the .02 allowance. Averages
must not conceal the individual failure described below.

All four policies achieved 10/10 initial transfer, final full validity, stable
late full validity and stable appropriate structure in both histories. Full
validity requires correct local partitions, all 32 modal targets correct and
expected loss regret <=.10. Stable measures require all five reviews from
1024 through 1280. There is no endpoint-validity advantage on this batch and
no justification for erasing failures on earlier worlds.

## Clearer evidence for useful reinstatement

Within each environment/proposal pair, every policy and both histories retained
an identical snapshot, including its parameters and provenance. Four snapshots
per history were confirmed at 192, before simplification began at 241. Six were
confirmed later, at 384 or 448, from buffers containing both earlier detail and
subsequent simplified evidence. All ten therefore contained some earlier
records, but only four were preserved before simplification.

Separate and shadow produced identical online predictions through record 576.
All four positive early-return pairs were the four with early preserved
snapshots. Separate first retrieved them at 576. Its detail branch made eight
retrievals across five runs; joint made five across four runs. Veto and shadow
made none. There were no pre-return retrievals under any policy.

Environment 1101/proposal 1101 illustrates the mechanism. At 576, the incumbent's
fresh loss was .903467. Main-buffer ranking favored a fitted candidate with
fresh loss .850481, exposing the right module's raw state. The earlier archive
had fresh loss .234627 and exposed the left module instead. Joint selected the
fit; separate admitted and retrieved the archive. Their prior states matched.
Separate's early-return gain versus shadow was .148944 nats in this pair.

This is stronger evidence of useful memory access than 021's average gain,
which was confounded with pre-return selection blocking. It includes recovery
of the archive's interface choice. Raw predictors still refit after each main
observation, so the result does not establish durable reuse of the archived
numerical parameters. The policy contrasts measure whole continuing trajectories;
they are not additive causal allocations of each prediction improvement.

## A fresh gate can still accept unhelpful memory

Separate retrieved twice in reversed histories, both at 576. In
1100/proposal 1100, its later, mixed-history snapshot passed fresh selection:
loss .700102 versus .837361 for the incumbent and .767305 for the best fit.
Nevertheless, observed early-return loss was **.131837 nats worse** than shadow.
One other reversed pair improved by .000680 and eight tied, giving the mean
cost .013116. The protocol bounded the mean, not worst-pair harm.

The detail branch also had one small loss increase, .003168 nats, after retrieving
a later snapshot. A fresh batch is evidence, not certainty. Neither the current
capture rule nor the deployment gate reliably distinguishes useful earlier
knowledge from an imperfect intermediate predictor.

## Interpretation and next boundary

On these worlds, competition without retrieval offered no early-return benefit.
Independent admission made useful early snapshots accessible when recent-buffer
ranking would have excluded them. That answers part of the mechanism question,
while the failed consistency criterion and reversed-world setback prevent an
overall reliability claim or promotion to a new default.

The next focused question is capture quality and timing: why did only four
pairs preserve a predictor before simplification, and can preservation improve
without increasing misleading recall? Another separate question is whether
benefit comes mainly from restoring an interface or its fitted parameters.
These remain proposed questions, not additional experiments in this run.
The one-slot archive, task families, feedback, candidate language and thresholds
remain supplied; meta-learning and safety advantages are still untested.

## Verification and artifacts

Six synthetic tests passed on the first attempt, charging 2156 labels against
a 3500-label ceiling. They covered failed and accepted archive competition,
compatibility exclusion, joint/shadow equivalence to previous policies,
checkpoint continuation, frozen qualification, independent replay and metric
thresholds. The benchmark used **542,720** allocated/used label presentations,
24,943 candidate fits and 3,543,552 scoring queries, including 9984 qualification
queries. All resource ceilings passed. The manifest preserves 116 source and
prior-artifact hashes; all earlier experiments remain unchanged. Benchmark time
was 138.60 seconds; independent audit time was 105.76 seconds.

See the [complete report](report.md), [frozen summary](results.json),
[paired contrast summary](contrasts.json), [independent audit](audit.json),
[completion record](completion.json), [manifest](manifest.json),
[worlds](worlds.json), [full traces](runs.jsonl.gz),
[trace-derived diagnostics](diagnostics.json) and [fixture log](tests.txt).
Each trace names its complete checkpoint and checksum. The frozen summary's
pre-audit status is retained; audit and completion records hold the final state.

Reproduction entry points: `python3 experiments/memory_selection.py` refuses
an existing output directory; `python3 checks/audit_memory_selection.py`
reconstructs saved evidence independently. Preserve original artifacts before
any deliberate reproduction.
