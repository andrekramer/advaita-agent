# 037 — recall withdrawal and explicit permission

2026-11-06. Final study in the [first steering round](steering_round_one_plan.md).
Freeze this protocol, implementation, independent auditor and passing fixtures
before generating outcomes. End with a round synthesis and goals review; do not
continue experimentation automatically. Original default and frozen sources stay
unchanged. No archive enlargement, new input encoding or changed learning rule.

## Design

Five fresh environment seeds 2600–2604; proposal seeds 2600 and 2601. Use the six
036 histories unchanged: stable, familiar category return, familiar polarity
return, persistent category change, persistent polarity change, and a different
category return. Four policies × six histories × ten seed/proposal pairs = 240
runs. Horizon 2048, reviews every 64, 32 fresh selection rows, independent 10%
label noise. Related histories and proposal draws are correlated, not independent
replications. Show environment means and all pairs, including missing memories.

All arms inherit 036 capture at 384, confirmation at 448/512, strict input-meaning
checks and separate immutable output routing. Stable local locking and composite
slow-memory half-life 128 run after 512 through after 1024; other rates stay
unchanged. No archive veto, replay training or evidence/parameter injection.

| Arm | Recall control |
| --- | --- |
| shadow | Retain and score memory but never deploy it. |
| current | Original 036 review-interval authorization. |
| command | Original authorization with a supplied block after tick 1552 and release after tick 1664. |
| evidence | Original authorization with the 16-observation withdrawal rule below. |

## Explicit command semantics

`set_recall_block(blocked, reason, source)` is accepted only after a completed
labelled observation at the current tick; at most one command per tick. Reject
non-boolean states, empty reasons/sources and duplicate commands without mutation.
Log prior permission/route, reason, source, tick and pre-command checkpoint hash.
Both block and release clear current authorization and partial monitoring evidence.
A block overrides all later ordinary review admissions until explicitly released.
Release permits a FUTURE fresh review to authorize recall; it does not revive
stale authorization or reuse the just-completed review's permission.

For the command arm, block after observation 1552, release after review 1664.
At review ticks, ordinary review and any fixed learning-rate instruction precede
this recall command. Outputs 1553–1728 therefore use the active model; earliest
possible newly authorized recall is 1729. The same commands occur in every
history. This schedule was chosen relative to the constructed rechange at 1537:
its timing is supplied task knowledge, not autonomous change detection.

## Evidence-triggered withdrawal

On EVERY main prediction with a confirmed available slot, all arms calculate the
archived probability as a matched diagnostic in addition to the active prediction.
Both probabilities are fixed before the current label enters learning. Following
the labelled observation, accumulate observed archive and active log losses ONLY
when that observation actually used recall and was compatible.

Use non-overlapping windows of 16 consecutive recalled observations. When a full
window's mean archive loss minus mean active loss is strictly greater than .02
nats, the evidence arm withdraws authorization for subsequent predictions. The
current prediction remains as made. Windows reset after every full check,
every ordinary review, either external command, an incompatible/non-recalled
prediction or missing label. No evidence is reused across windows. A partial
window never triggers withdrawal. Monitor scores in other arms are logged but
cannot revoke recall. No clean targets, phase markers, future labels or return
schedule enter this rule.

An ordinary later fresh review can authorize recall again using the unchanged
036 admission criterion. No additional cooldown or adaptive threshold is added.
The external block takes precedence if present. The monitor changes only output
authorization; every active learning operation and label presentation remains
unchanged. There is no learned control policy.

Schema 37 checkpoints contain the active learner, immutable slot, permission,
partial window, commands and monitoring history. Round-trip at 448, 1544, 1552,
1664: qualification, possible partial monitoring, possible withdrawal/block,
and command release. Inspection must return detached data. Serialized loss uses
-log(p) or -log(1-p) identically in the independent reference for exact hashes.

## Measurements and primary criteria

Evidence versus current is the primary empirical comparison. Command execution
and its supplied-timing effects are reported separately, not pooled as evidence
of an autonomous controller. Shadow measures the cost of using memory at all.

Report observed and expected loss on all three outputs, active expected loss,
actual archived predictions, monitor windows, withdrawals, command fidelity,
active/deployed validity, timing and resource costs. Clean targets are evaluator-
only. Windows: active 513–1024; early return 1025–1280; whole return/post-release
1025–1536; later 1537–2048; immediate rechange 1537–1600. This last window isolates
the 64-observation failure in 036. Report its absolute costs versus shadow too;
improvement versus current does not imply zero transient cost.

Full empirical success for evidence requires ALL:

1. Pooled immediate-rechange expected composite gain over current >= .10 nats,
   positive (>1e-12) in >= 14/20 familiar-return pairs, with positive mean gain in
   each returning history.
2. Retain useful recall: in EACH familiar-return history, early-return and whole-
   return composite cost versus current <= .01 mean and <= .05 in every pair.
3. Whole-return gain over shadow >= .01 pooled and positive in >= 14/20 pairs.
   This tests retained use, not merely disabling memory. It does not revise 036's
   failed early-return criterion or claim that delayed recall has been solved.
4. For EACH history, ALL outputs, active/early-return/whole-return/later windows:
   mean cost versus current AND shadow <= .02 and every-pair cost <= .10.
   Immediate rechange has the separate benefit criterion and reported absolute
   costs; its short-horizon costs must not be hidden by later averages.
5. Final active and deployed full validity >= 8/10 per history. Full validity
   requires correct local partitions, 32/32 correct modal composite predictions
   and expected regret <= .10.
6. Exact active-prediction/ordinary-review/final-learning-state parity, control
   execution, provenance, continuation, independent arithmetic and budgets pass.

No primary success is inferred from command-arm gains alone. No omitted pairs,
post-outcome parameter tuning, seed expansion or retrospective primary windows.

## Resources and completion

30 histories generated, 307200 scalar labels, 2457600 training presentations.
Active main predictions: 1474560 scalar channels. Active/deployed review grids:
491520 contexts, each returning three channels. Archive main calls and additional
monitor calls counted separately; monitor ceiling 491520 (at most one per main
record), expected 368640 if every snapshot confirms. Review memory diagnostics:
399360 composite scores, separate from ordinary scoring. Extra selective-decay
cell visits 3932160. Monitoring adds at most 16 pairs of losses as decision state;
its immutable audit history is not a replay training buffer.

Caps: 450000 candidate fits; 30000000 ordinary scoring queries; 140000000 fit-
related raw-bin visits; 500000 review-grid contexts; 900 seconds each for runner
and independent auditor. At most eight fixture attempts using released 2500 data
and explicitly counted synthetic labels. No reserved-seed fixture outcomes.

Freeze recursive 036 dependencies and all new study sources/fixtures. Preserve
partial outcomes and exceptions. Resolve correctness failures separately, with
no silent editing of frozen sources/results. After the audit, publish findings
and a round synthesis distinguishing execution, utility, limitations and which
optional implementation supplies each control. Stop experiments for user review
of next goals, whether the empirical gate passes or fails.
