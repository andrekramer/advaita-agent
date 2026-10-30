# 027 — Revising slow evidence

Specified 2026-10-30 before generating reserved outcomes. This follows 026's
blocked improving transfers. All earlier sources and results remain frozen.
The original consolidated learner remains the reference architecture.

## Question and intervention

Does evidence-gated weakening help beyond simply relaxing admission? Keep 026's
finite raw bins, F/S half-lives (64/1024), acquisition, structural operators,
selection batches, capacity512 and .25F mass-conserving migration unchanged.
Use seven policies: original `baseline`; `fast` (no migration); `selective`
(026 gate); `relaxed` (migration requires improvement>.005, without loss<=.55);
`weaken` (026 admission plus selective weakening); `combined` (relaxed admission
plus selective weakening); `uniform` (relaxed admission plus unconditional
halving of slow evidence at every labelled review).

Uniform is a simple faster-forgetting control, not matched in removed mass.
The 2x2 selective/relaxed/weaken/combined comparison separates admission from
revision. Neither the architecture nor its parameters learn this control rule.

After each structural review, before migration, consider channels0,1,2 in
order. Under the current partition/interface and actual current local meanings,
fit four counterfactual predictors from S, F, F+S and F+.5S. All weighted policies
score these same four proposals on the existing32 selection rows per channel.
No selection label enters either evidence store. A qualifying contradiction is:

* fast-only loss<=.55;
* slow-only loss minus fast-only loss>.05;
* combined loss minus proposed weakened-combined loss>.02;
* slow mass is positive.

Selective weakening needs qualifying evidence at two consecutive reviews
exactly64 clock ticks apart with the same partition (local), or same interface
and used local group meanings (upper). The candidate is recomputed at each
review; this is repeated support for a direction of change, not two tests of a
frozen predictor. A failed or changed witness replaces/clears the pending
witness. After acceptance it clears. No weakening happens during a blank gap.

Accepted weakening sets S'=S/2, F'=F, logs the removed evidence mass, clears that
channel's old pending structural reduction and refits all active predictions
from F+S. Local weakening can change group names; later upper tests use those
actual meanings. Ordinary upper pending-meaning checks remain in force.
The subsequent migration uses the resulting evidence and names. This reduces
confidence in old observations; it does not erase raw bins, collapse a form,
retrieve episodic memories or learn a new memory policy. Audit logs retain the
history. Half removal is a fixed bounded proposal, not an optimized rate.

Selection batches are shared across structure, weakening and migration. Two
consecutive batches supply fresh observations, but decisions within a batch
are not independent confirmations. Main pre-update outcomes measure utility.

## Paired worlds and measurements

Reuse the corrected frozen026 generator on fresh environment seeds1700–1704,
proposal seeds1700/1701: five histories x ten pairs x seven policies =350 runs.
Histories: stable; brief true reversal at257–320; a blank gap257–768 followed by
familiar return, permanent prediction reversal, or local partition remapping.
Same acquisition, ten-percent noise and1280-tick horizon as026. Runtime receives
only present observations/elapsed ticks, never history labels or latent truth.
No exclusion of acquisition failures. Five independent environments with two
proposal replicates are not ten independent environment samples.

Keep026 measurements: prequential observed and expected loss, structural and
full validity, unseen-combination transfer, gap probes, early769–896 and
late1153–1280, burst257–320, recovery321–448, whole-stream loss. Full validity
requires correct local partitions, all composite modal predictions correct
and expected regret<=.10. Recovery requires two consecutive valid evaluations
from832 through1280; missing recovery is censored, never treated as observed.
Also record every weakening test, witness, decision, mass removed, migrations,
fit/scoring cost and final checkpoints. Report every policy, all paired costs
and environment means. No retrospectively selected winning variant.

## Predeclared primary decision

Primary candidate is `combined`; admission-only control is `relaxed`.
All gates must pass:

1. Mean observed early-revision gain (equally averaging reversal and remap per
   pair) >=.02, positive in at least8/10 pairs.
2. Final full validity >=8/10 for EACH of five histories; gap full validity on
   familiar return >=8/10.
3. Against BOTH selective and relaxed: mean observed AND expected cost <=.02
   for stable whole, familiar-return early, burst interval and burst recovery;
   every individual observed cost in these cases <=.10. End-of-gap familiar
   expected-loss cost <=.02 on average.
4. Against relaxed: mean observed AND expected early cost <=.02 separately for
   reversal and remap; every individual observed early cost <=.10. In each
   history reversal/remap, candidate's censored count cannot exceed control's.

Secondary contrasts: weaken-selective, combined-selective, relaxed-selective,
combined-uniform, combined-fast and combined-baseline. Report predictive costs
without automatic superiority claims. A separate selectivity-benefit gate
requires combined's mean gain over uniform >=.01 averaged over stable whole,
familiar-return early and burst recovery, positive in>=8/10 pairs. It is not
part of the primary gate. No automatic promotion or confirmation run.
Failure of any primary gate completes this round with a qualified/null result.

## Freeze, budget and audit

Fixtures use seed5990, at most5000 label presentations across preserved attempts;
synthetic state arithmetic and replay consume no new training labels. Reserved
seeds remain unopened until fixtures pass and source manifest is written.
Fixture allocations are charged before execution, including failed attempts.
Ceilings:350 runs; generated labels135040; used labels1890560;
candidate fits350000; scoring queries20000000; raw-bin visits100000000;
oracle context queries1300000. Same baseline-inclusive evaluation allocation
as026:1021440 main-channel predictions;232400 grid/transfer predictions;
24000 slow-only probes;12000 legacy auxiliary predictions;7680 reused gap
predictions. Benchmark and independent audit each<=900 seconds. Fixed two
40-bin stores, plus bounded pending witnesses and active tables; logs separate.

Freeze new code, this protocol, tests and passing fixture evidence, together
with026's manifest and artifacts. Reuse frozen generator/evaluator and independent
026 replay for unchanged components through explicit function adapters. New
revision arithmetic and decisions must be independently reconstructed without
importing the new runtime/experiment. Verify every world, prediction, decision,
checkpoint, metric, paired summary and budget. Preserve partial outputs on
engineering failure; no outcome-driven threshold, seed or horizon changes.
