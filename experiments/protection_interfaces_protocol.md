# Experiment 017 / C1: local protection and interface revision

Frozen design prepared 2026-10-23, before inspecting seeds 600–604. This is
Stage C1 of the consolidation plan. C0's core and historical records stay
unchanged. No tuning or additional seeds follow an empirical failure.

## Question and supplied structure

Does earned protection of a lower form prevent error propagation to a nested
consumer, and what does it cost when a lower relationship genuinely changes?
Compare immediate/opening, immediate/reclosure, earned/opening and
earned/reclosure. Use the unchanged `advaita.runtime.NestedLearner` and its
013–015 policies. Two four-state lower modules export binary groups to an
XOR-with-action upper table. Wiring, action schedule, partition language,
review schedule, thresholds and noise model are supplied. This is not
meta-learning, causal discovery, or a test of the necessity of full R-rule
or phase dynamics.

## Streams and pairing

Environment seeds 600–604; proposal seeds 600,601. Layout RNG 81000+seed,
input-order RNG 82000+seed, outcome-noise RNG 83000+seed. Local proposal RNGs
84000+2*proposal_seed+j. Every branch uses identical random draws and input
orders. No branch, time index, truth or evaluation enters the learner.

For each module, shuffle four raw states; the first two have latent effect 0,
the last two effect 1. Choose the first state of each pair as a composition
representative. Choose the affected module with the layout RNG. Its alternative
form flips membership of those two representatives, retaining two groups.
All outcomes have independent 10% bit-flip noise.

Acquisition matches 013: 256 balanced raw observations per module, four reviews
with 32 fresh local labels each, then 256 composite labels drawn from the eight
representative/action combinations. Fit the coarse upper table once. Evaluate
transfer on the other 24 combinations, without learning. Do not discard failed
acquisitions or restore selected checkpoints.

Adapt for 512 main records, balanced in shuffled blocks of all 32 contexts.
Review every 64 records using a fresh balanced block of 32 contexts. Each main
and selection record has two local outcomes and one composite outcome.

* Persistent: original local forms and composite XOR throughout.
* Remap: after adaptation record 128, the affected module uses its alternative
  form permanently. Composite outcomes follow that new form; XOR is unchanged.
* Burst: records 129–192, inclusive, use the alternative form only for the
  affected local observation channel. Composite outcomes and latent local forms
  stay unchanged. Selection batches use the condition at their review index,
  so the batch at 192 is corrupted and the batch at 256 is clean.

No buffers or policy state reset at changes. All acquisition draws are paired
across branches. These duplicated histories and the two proposal seeds are not
independent environment replications. Generate main data before selection data,
with local noise draws preceding the composite draw in each joint row.

## Unchanged decisions and observability

Buffers hold 192 main records. Local proposals fit four non-incumbent partitions
from shuffled decks of the eight binary partitions, rank by loss on the last
64 main records (ties: fewer groups, then partition), and need fresh gain >.005.
Earned protection latches after two unchanged adequate reviews (loss <=.55).
A protected challenger stays frozen and needs gain >.005 on the next fresh
batch; failure discards it without accepting another challenger that review.
Counts can still update while a form is protected.

Upper reviews fit coarse/fine0/fine1 on the current buffer after local reviews;
rank by main loss, ties in that order. Ordinary replacement needs incumbent
selection loss >.55 and gain >.02. Reclosure requires a frozen coarse challenger
adequate on two consecutive batches: loss <=.55 and disadvantage <=.02.
Changed group maps invalidate its evidence; ordinary replacement takes priority.
Fine upper tables refit after each main update; coarse tables stay frozen.

Save all proposals, losses, decisions, main predictions, local predictions,
exposures, checkpoint evaluations, final state and policy costs. Record ledger
counts and reuse. Save hashes of the complete checkpoint and ledger, plus the
ledger and final checkpoint in compressed per-run files. Evaluation predicts
through exported states only and receives no write access to the learner.
Prediction access restrictions are API contracts, not security isolation.

## Metrics and frozen criteria

Predictive validity: all 32 modal composite outcomes correct and expected
Bernoulli(.9/.1) log-loss regret <=.10 nats. Transfer uses the 24 unseen contexts.
Full validity additionally requires both exported local membership maps to match
the latent forms, including their effect-based labels. Coarse validity also
requires the coarse interface. Numeric label agreement alone is insufficient.

Report observed and latent expected main loss separately for the composite and
each local channel. Report upper and local validity, invalid affected-local
checkpoints, coarse validity, reopening/hiding/reclosure events, raw reads,
per-record bypass of a wrong affected form, and opening-to-hiding latencies.
A bypass means fine exposure of the affected module while its exported map is
wrong, whether or not that bypass predicts successfully. All fine exposure is
structurally unnecessary in these worlds; it can still be a useful temporary
bypass. Latencies without a later hide remain censored (`null`).

Invalid local checkpoints for the protection comparison are affected-module
errors at reviews 192,256,320,384,448,512 in the burst condition. Recovery starts
after 128 in remap, after 192 in burst, and after 0 in persistent. Report the
first fully valid review and the first pair of consecutive fully valid reviews,
including the second review's confirmation time. An unconfirmed run receives
576 solely for the prespecified mean delay comparison; retain null in traces.

For each matched upper policy, an earned-protection success requires:

1. At least 8/10 transfer-valid and final-fully-valid runs in every condition,
   for both immediate and earned variants.
2. Persistent mean composite observed loss cost <=.02 nats, and mean composite
   and affected-local latent loss costs <=.02 each (all 512 records).
3. Remap mean composite observed loss cost <=.05 nats, and composite and
   affected-local latent loss costs <=.05 each (records 129–512). Mean confirmed
   recovery delay <=64 records, using the declared censor value.
4. Burst mean composite and affected-local latent loss costs <=.02 each
   (records 129–320), plus a positive immediate-control affected-local error
   count, at least 25% reduction of that count, and strict improvement in at
   least two of the ten seed pairs. Zero control errors leave benefit untested.

Primary success is the conjunction for both upper policies. Report every
component and cell, including failure. Also report paired effects of reclosure
under each local policy, and the factorial difference of those effects for
composite latent loss, raw reads and invalid local checkpoints. Do not infer
synergy from separate favourable main effects. These are descriptive paired
results, not population significance tests.

**C2 progression gate:** correct implementation and independent audit, plus
immediate/reclosure transfer and final full validity >=8/10 in each condition.
This gate does not require primary earned-protection success or coarse final
validity; report coarse validity separately. C2's reference remains immediate
local replacement with reclosure, chosen before these results. If the gate
fails, stop with consolidation incomplete. No repair benchmark is added.

## Budget, freezing and audit

Exactly 120 runs: 3 conditions ×5 environments ×2 proposal seeds ×4 variants.
3,328 used/allocated label presentations each; total 399,360. Generated labels
49,920 including paired duplicated histories. Main predictions: 61,440 composite
and 122,880 local. Evaluation queries: 33,600 composite (24 transfer +8×32 per
run). Local form checks inspect membership maps and introduce no labels.

Candidate fits: 11,520 local +2,880 upper =14,400. At most 1,700,000 candidate
ranking/selection/challenger probability queries (local 12×[4×64+2×32+32]×2,
upper 8×[3×192+2×32+32], per run). Refits are counted separately: 1,536 local
per run and at most 512 upper. Pending predictive tables: at most two local
(two cells each) plus one upper (eight cells), 12 cells in total; no archive.
Audit metadata is not a predictive buffer and is separately retained on disk.

C0 charged 18,880 synthetic labels against the round ceiling of 20,000. New
fixtures are capped at 336: three tiny generated worlds (48 labels each), plus
four 48-label executions, conservatively counting generation as well as use.
Use only synthetic seed 990; run the fixture suite once before freezing.
Audit replays consume saved evidence and are counted separately. No benchmark
seed is inspected during development. Set a 600-second wall-clock limit for
the benchmark (including persistence) and a separate 600-second audit limit;
record fixture timing to check feasibility before execution. A resource limit
or correctness failure leaves an incomplete record, never extra budget.

Before generation, freeze this protocol, driver, tests, auditor, reporting
module and all runtime/auditor dependencies in the manifest. The independent
checker imports no learner or experiment code, reconstructs streams and
arithmetic, checks policy ordering, predictions, checkpoints, provenance,
metrics and costs, and verifies every historical manifest. Historical floating
arithmetic may differ by <=1e-10; tie order is checked with saved ranking bits
only after independently verifying those losses. Preserve outputs and disclose
any code correction; never tune criteria after seeing results.
