# Experiment 019: extended recovery helps, but abstraction can regress

Completed 2026-10-26. All **120 runs** finished and passed independent replay
of streams, learning decisions, predictions, full checkpoints, metrics and
costs. The learner was unchanged. The primary representation criterion failed
in the form-return history; the separate memory-benefit criterion also failed.
No benchmark was tuned or repeated.

## What was tested

Following the [consolidation round](../consolidation-round-synthesis.md), this
separate round tested fresh realizations of the same three small task families.
The final recovery period lasted **752 observations rather than 240**. Five
environment seeds and two proposal seeds gave ten paired runs per condition,
with integrated, deleted-memory, raw-input and fixed-form variants.

The [protocol](../../experiments/consolidated_recovery_protocol.md) and source
hashes were fixed before generating the reserved seeds. All variants received
the same allocated streams; actual label use differs and is recorded. The
first-768 analysis is a distributional replication: generating a longer main
stream changes the selection-stream RNG position relative to generating a
separate short world. This is not a randomized short-versus-long treatment.

## Prediction, forms and interfaces

Stable validity means passing every review at 1024, 1088, 1152, 1216 and 1280.
Prediction requires perfect modal-target accuracy over all 32 contexts and
latent loss regret <=.10. Full validity additionally requires correct local
partitions. Structural validity also requires the appropriate sufficient,
minimal interface and successful transfer. The frozen representation target
was at least 8/10 structurally stable integrated runs in **each** history.

| Integrated learner | Transfer | Stable prediction | Stable full validity | Stable structure |
| --- | ---: | ---: | ---: | ---: |
| Forms disappear and return | 10/10 | 10/10 | 9/10 | **6/10** |
| Raw detail disappears and returns | 10/10 | 10/10 | 9/10 | **9/10** |
| Detailed outcome reverses on return | 10/10 | 10/10 | 9/10 | **9/10** |

The prediction result is encouraging, but representation stability passes only
the two detail histories. These paired histories share their initial experience;
the counts are not independent replications of each other.

For forms, structurally valid endpoints increased from **5/10 at 768** to
**9/10 at 1024**, then fell to **7/10 at 1280**. One run eventually reclosed at
1152 but missed the required earlier stable window. Two others reopened
unnecessary raw ports late in recovery. In environment800/proposal800, a local
replacement at 1280 changed a correct partition into an incorrect one. The
parent retrieved a raw-input model and retained correct output, concealing
the damaged lower form. The same paired local failure occurred in the detail
and reversed histories, where raw access was already required.

More experience allowed some abstraction recovery, but waiting alone did not
reliably preserve it. The trace identifies accepted changes under noisy
evidence; it does not prove which alternative protection policy would avoid
them without adaptation costs.

The original first-768 complete trajectories were **0/10, 4/10, 4/10** for
forms, detail and reversed. The middle simplification endpoint passed in only
2/10, 4/10 and 4/10. Extending the final regime does not repair those earlier
failures or turn the complete lifecycle into a success.

## Retention and its limits

In detail and reversed histories, retained and deleted variants produced
identical prediction sequences in all ten pairs. Return-period gain was zero,
against the required .02 nats and eight improving pairs. No archive was
retrieved in either history; the reversed-return cost guard passed with zero
cost. All four detail snapshots were captured at 448 from records 257–448,
entirely within the no-detail phase. Their paired reversed snapshots had the
same provenance. This reproduces the capture-timing concern without testing
a different capture rule.

There were **four retrieval events in three integrated form-history runs**,
so the archive mechanism did execute beyond capture. Three occurred at the
final review 1280 and had no subsequent online observations within this test.
Only one paired form run had a different online prediction sequence; its
return loss was worse by .003131 nats. Across all ten form pairs the mean
retention gain was -.000313 nats. Retrieval is therefore not itself evidence
of a useful memory benefit. Final post-review evaluations are retained
separately from the pre-update online loss.

## Controls and scope

The fixed-form control achieved stable structures in **8/10, 10/10, 10/10**
runs. It cannot collapse its lower forms in the middle phase, but its upper
model can compensate and it avoids later local revisions. The integrated
learner's full adaptive dynamics are not shown necessary or superior here.

The raw-input control had stable prediction in 6/10, 4/10 and 4/10 runs, and
failed initial withheld-composition transfer in every run. Its representative-
only acquisition curriculum leaves unseen raw cells untrained; this is a
specific benefit of abstraction in this curriculum, not a universal comparison
against raw-input learning. Integrated mean late raw reads were 25.6, 256, 256
versus 512 for raw in each history. Detail's remaining raw access is appropriate;
the desired level of information hiding depends on the task.

These are five small finite simulator worlds, each with two proposal draws.
Local feedback, architecture, candidate partitions, interface language,
thresholds and review schedule are supplied. This tests reliability on these
tasks, not new task-family generalization, meta-learning or safety advantages.

## Verification and artifacts

Three harness tests passed before execution, using fabricated summaries and
saved evidence with **zero new learning labels**. The benchmark used 641,280
label presentations from 814,080 allocated, 23,985 candidate fits and 3,366,144
scoring queries, all within the frozen ceilings. It took 102.21 seconds; the
independent audit took 83.14 seconds. C0–C2 code and artifacts were preserved.

See the [complete report](report.md) for all 120 runs, paired comparisons and
environment aggregates; [audit](audit.json), [manifest](manifest.json),
[summary](results.json), [worlds](worlds.json), [traces](runs.jsonl.gz), and
[trace-derived diagnostics](diagnostics.json) preserve the evidence. Full
checkpoint paths and checksums are recorded in each trace.

The next focused design question is how to preserve a useful form or predictor
before it is overwritten, while permitting genuine change and returning to
abstraction after repair. Any revised protection or memory rule needs a new
protocol and matched controls. This round supplies the unchanged baseline;
it does not imply automatic tuning or further seed searches.

Reproduction entry points are
`python3 experiments/consolidated_recovery.py` (refuses an existing output
directory) and `python3 checks/audit_consolidated_recovery.py` (replays saved
evidence without new learning). Preserve these artifacts before any deliberate
reproduction run.
