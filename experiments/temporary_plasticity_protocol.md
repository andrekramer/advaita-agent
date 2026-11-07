# 035 — temporary downstream plasticity

2026-11-06. Freeze this protocol, implementation, independent auditor and passing
fixture records before generating reserved outcomes. Implements the
[2026-11-05 plan](downstream_retention_plan.md). Default learner unchanged.

## Prerequisite diagnosis

The [saved-result diagnosis](../results/downstream-retention-diagnosis/findings.md)
finds worse original-map predictions alongside better changed-map predictions in
034 D versus P. Local partitions match across all paired saved reviews; upper
interfaces differ in 18/20 pairs. This warrants a duration test but does not
identify decay as the sole cause. No parameter was selected from that diagnosis.

## Fixed design

Environment seeds 2400–2404; proposal seeds 2400 and 2401. Five histories:
stable, forms, repeated polarity, persistent forms, persistent polarity.
Five policies per history and seed/proposal pair = 250 runs. The two proposal
seeds and paired histories are correlated: show environment means and pair
counts; do not describe them as independent replications.

Worlds reuse the 034 generator. Persistent histories replace the original-return
phase (1025–1536) with the changed mapping, keeping every noise draw and input.
Thus return/persistent pairs match exactly through 1024 and use the same inputs
and noise throughout. Changes occur at 513; original histories return at 1025
and change again at 1537. Horizon 2048, period 64, selection batch 32, independent
10% noise, and the misleading protected-channel burst at 513–640 remain fixed.
No fresh worlds are used for fixtures or threshold tuning.

All policies lock the supplied stable local partition after review 512 and
release it after review 1024. Local evidence half-lives stay 1024. Fast half-lives
stay 64. Ordinary transfer, weakening, structural search and post-review refresh
are inherited without modification. P never boosts. D128, D256 and D512 boost
composite slow decay to half-life 128 after 512, then restore 1024 after reviews
640, 768 and 1024 respectively. No restoration of old evidence occurs.

G boosts after 512 and ends the boost after two consecutive fresh pre-review
composite losses <= .55 nats. Eligibility begins at 576; earliest closure 640.
The deployed predictor is scored before any local or upper review or selection
label fit; the predictor identity and all predicted probabilities are recorded.
A failed witness resets the streak. Selection data subsequently enter ordinary
review; reuse is disclosed. Every arm scores all eight diagnostic batches from
576 through 1024, even after closure. Only G uses the diagnostic for control.

At 1024, one command releases the lock and resets the rate. If G is still open,
record ceiling closure even if a second adequate witness happens on that review.
D512 is also recorded as ceiling closure; its duration is nevertheless fixed.
No reopening. Opening, deadline and protected role are supplied task knowledge,
not learned goals. G never sees clean targets or return dates. The stable control
retains a supplied role even though neither channel changes.

Use a schema-35 controller/learner bundle containing the unchanged schema-34
learner plus policy, opening, ceiling, protected role, streak, last loss, closure
and last review. Round-trip at ticks 576 and 768; continue from the restored
bundle. Diagnostic logs contain batch/model hashes, before/after learner hashes,
predictions, losses, streak and configuration. Independent replay reconstructs
all predictions, fits, review decisions, control commands, snapshots and hashes.

## Outcomes fixed before the run

G is primary; D128/D256 are secondary alternatives. Report all three outputs'
expected and observed log losses. Expected losses use clean targets only in the
evaluator. Windows: active 513–1024, burst 513–640, settled 641–1024, early return
1025–1280, whole return/post-release 1025–1536, later 1537–2048. These do not move
with closure. Record durations, closure reasons, partitions, upper specs, evidence
mass and endpoint validity. Every pair stays in the report.

G full success requires all:

1. Active composite cost versus D512 <= .02 mean and <= .10 each pair in EACH
   changing history. Pooled active gain over P >= .02, positive in >= 28/40 pairs.
2. Early-return composite gain over D512 >= .02 pooled and positive in >= 14/20
   returning pairs; both returning histories have strictly positive mean gain.
3. For all three outputs versus P AND D512: mean costs <= .02 and every pair
   <= .10, separately for every history in whole-return/post-release and later
   windows, and for stable active behavior. Apply the same early-return limits
   versus P in the two returning histories. Persistent windows are post-release,
   not returns.
4. Protected burst correctness >= .95 in each changing history; full endpoint
   validity >= 8/10 in each history. Full validity means correct local partitions
   up to relabeling, modal composite accuracy 1 and expected regret <= .10.
5. Independent correctness, provenance, continuation and budget checks pass.

Positive means > 1e-12. Apply the same bundle descriptively to D128 and D256;
compare G directly with both across all windows. No retrospective primary winner
or adoption claim if a secondary pulse succeeds. These are not exposure-matched
comparisons: do not separate diagnostic information from duration causally.

## Budgets and failure policy

25 generated world histories: 256000 scalar labels, 2560000 training presentations.
Main prediction accounting: 1536000 scalar channel predictions. Review grid:
256000 contexts (each returns three channels). Diagnostic accounting: 64000
composite queries in addition to ordinary scoring (the implementation computes
three scalar channels per query). Extra slow-decay cell visits <= 4096000.
Inherited acquisition evaluation work remains recorded in acquisition records,
separate from main/review-grid/diagnostic counts.

Caps: 400000 candidate fits, 25000000 ordinary scoring queries, 130000000
fit-related raw-bin visits, 300000 review-grid contexts, 900 seconds each for
runner and independent auditor. No adaptive seed expansion. At most eight fixture
attempts with reused 034 worlds and separately counted synthetic presentations.
Each fixture attempt preserves its outcome and source hashes. Fresh generation
requires the latest fixtures to pass on the current exact sources. Hash recursive
034 dependencies and all new study sources/fixtures/diagnosis before generation.
Do not overwrite results; retain partial files and exceptions on failure.

If G passes, propose fresh timing variation confirmation. If a fixed pulse is
as good, prefer the simpler timing explanation. If duration control cannot meet
the adaptation/retention bundle, propose a separate one-slot memory integration
study addressing semantic compatibility and persistence through ordinary refits.
Do not run that conditional study automatically. No general steerability,
meta-learning, consciousness or safety advantage is established by this test.
