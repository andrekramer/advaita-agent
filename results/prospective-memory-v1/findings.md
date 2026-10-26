# Experiment 021: earlier preservation, but inconsistent memory benefit

Completed 2026-10-26. All **60 runs** passed independent reconstruction of
streams, predictions, decisions, evidence records and full checkpoints.
**The primary criterion failed:** prospective preservation reduced mean
early-return loss, but improved only 3/10 pairs, requiring 8/10. The saved
traces also reveal a selection interaction: an available archive can change
learning even when it is not retrieved. No benchmark was tuned or repeated.

## What changed

Earlier integrated experiments captured predictors when accepting structural
reduction, sometimes after adaptation had erased the earlier relationship.
This [protocol](../../experiments/prospective_memory_protocol.md) instead
nominates a detailed predictor while it is active, freezes it, and requires
adequate loss on two consecutive fresh selection batches. The first confirmed
snapshot occupies one archive slot for the rest of the run. Existing meaning
checks, candidate ranking and fresh deployment gates remain unchanged.

This is a capture-and-preservation intervention, not timing alone. Compare
`reserve` with `legacy` capture at reduction and `discard`, which performs the
same prospective qualification work but destroys its confirmed snapshot.
Local learning uses the original consolidated rule, without experiment 020's
additional protection.

Five fresh environment seeds, each with two proposal draws, supplied ten pairs
per history. Detail matters, disappears, and then returns either unchanged
(`detail`) or with opposite outcomes (`reversed`). Each learner receives the
same acquisition curriculum and 1280 joint records with 10% label noise.
The histories share evidence through record 528. These are five environment
realizations, not ten independent worlds or independent initial histories.

## Benefit and costs

Legacy and discard produced identical complete online prediction sequences in
every pair, so the following comparisons apply to both controls.

| Measure | Reserve relative to control | Frozen requirement | Result |
| --- | ---: | ---: | --- |
| Detail early-return observed loss reduction | .028616 nats | >=.02 | Pass |
| Detail pairs with strictly lower early loss | 3/10 | >=8/10 | Fail |
| Reversed early-return observed loss cost | −.020949 nats | <=.02 | Pass |
| Pre-return observed loss cost, each history | +.008981 nats | <=.02 | Pass |
| Pre-return latent loss cost, each history | +.011076 nats | <=.02 | Pass |
| Final full validity, every policy/history | 10/10 | >=8/10 | Pass |

Early return means records 529–656; pre-return means 1–528. Detail early loss
fell from .724525 to .695909. Three pairs improved, six tied and one became
slightly worse. Latent early loss improved by .028491 nats. Reversed early
loss also improved, although no archive was retrieved after its return.
The corresponding mean benefit over the whole detail-return period was
.004871 nats; late loss was identical across policies.

Every policy achieved 10/10 initial transfer, final full validity, stable late
full validity and stable appropriate structure in both histories. Full validity
requires correct local partitions, all 32 modal targets correct and expected
loss regret at most .10. Stable measures require every review from 1024 to
1280. This batch therefore shows no endpoint advantage for memory and does
not erase representation failures on earlier, different worlds.

## Preservation worked earlier in seven pairs

Reserve confirmed one snapshot in every run. In each history, seven were
confirmed at review 192, before simplification began at 241. Eight contained
some pre-simplification evidence; the eighth mixed earlier and later evidence
and was confirmed only at 448. Containing old records is not itself proof of
an accurate old representation. Legacy made three captures per history, none
containing pre-simplification evidence. Discard qualified the same number of
snapshots as reserve but retained none.

Reserve retrieved six times in detail: twice at 256, three times at 640 and
once at 1280, with no subsequent online prediction inside this run for that
last retrieval. In reversed it retrieved only twice, both at 256. Legacy
retrieved nothing. Four incompatible archive checks occurred per reserve
history. Preserving parameters does not guarantee compatible or useful recall.

## An archive also changes selection

Read-only inspection of the saved traces identified the first upper-decision
divergence in seven pairs per history, at review 256. Before those decisions,
local states, upper states and fitted candidates matched. The first online
prediction differences followed at record 257, well before return at 529.

In five pairs, the archive won ranking on recent main evidence but failed the
fresh improvement gate. Reserve kept the incumbent. Without the archive,
discard selected a freshly fitted candidate that passed. The unchanged rule
tests only the ranking winner; it does not fall back to the fitted candidate
when an archive fails. For example, environment 1000/proposal 1000 had fresh
loss .922473 for the incumbent, .944357 for the archive and .716894 for the
fitted candidate. Archive availability prevented that fitted update.

In the other two pairs, the archive was retrieved at 256 even though the fitted
alternative had lower fresh loss: main-evidence ranking had already chosen
the archive. All three positive early-return detail pairs belong to the first
group. The same three reversed pairs improved despite no post-return retrieval.
Thus the experiment measures the effect of making memory available to the
existing selection rule; it does not isolate recovery by reinstating old
knowledge. Archive competition can introduce additional inertia, with both
pre-return cost and later benefit. These diagnostics suggest a mechanism;
they do not replace a separately specified causal ablation.

## Scope and next question

Prospective preservation partly addresses lost information, but reliable
beneficial recall remains unestablished. One permanent slot can preserve the
wrong snapshot, miss an early opportunity or become incompatible. The task
families, candidate language, architecture, thresholds and feedback are still
supplied. This is no evidence of meta-learning or a safety advantage.

The next focused question is whether memory retrieval and fresh adaptation
should receive separate selection opportunities. A future controlled test
could isolate archive competition from actual reinstatement while measuring
pre-return and reversal costs. That would require its own protocol; no such
intervention was run here, and reserve is not promoted as the new baseline.

## Verification and artifacts

Six synthetic checks passed before reserved-world generation, charging
854 labels against a 2500-label ceiling. They cover frozen qualification,
failure and semantic invalidation, delayed deployment eligibility, preservation
against overwrite, discard equivalence, checkpoints and independent metrics.
The benchmark used **407,040** allocated/used label presentations, 18,718
candidate fits and 2,534,112 scoring queries, including 4864 qualification
queries. All resource ceilings passed. Benchmark time was 99.60 seconds and
independent audit time 77.72 seconds. The manifest preserves 103 hashes of
source and prior artifacts.

See the [complete numerical report](report.md), [frozen summary](results.json),
[independent audit](audit.json), [completion record](completion.json),
[manifest](manifest.json), [worlds](worlds.json), [full traces](runs.jsonl.gz),
[trace-derived diagnostics](diagnostics.json) and [fixture log](tests.txt).
Each trace names its complete checkpoint and checksum. The frozen summary's
pre-audit status remains unchanged; the separate audit and completion records
record the final state.

Reproduction entry points: `python3 experiments/prospective_memory.py` refuses
an existing output directory; `python3 checks/audit_prospective_memory.py`
reconstructs saved evidence independently. Preserve original artifacts before
any deliberate reproduction.
