# Experiment 011: proposal coverage and corroborated structural revision

Fixed before execution, 2026-10-20. The user authorised continuing the new round
after Experiment 010. This is a new, prospectively specified follow-up informed
by its failures, not a rerun or tuning of its completed benchmark.

## Hypotheses and scope

Experiment 010 exposed missed proposals, unnecessary retained detail, and
discarding a useful pair after a misleading selection batch. Test two changes
in a 2-by-2 factorial design:

| Variant | Proposal generation | Structural acceptance |
| --- | --- | --- |
| iid_single | Independent four-candidate samples per review | Full 32-outcome gain >0.005 |
| deck_single | Shuffled decks, traversed before reshuffling | Full 32-outcome gain >0.005 |
| iid_split | Independent four-candidate samples per review | Both 16-outcome half-batch gains >0.005 |
| deck_split | Shuffled decks, traversed before reshuffling | Both 16-outcome half-batch gains >0.005 |

The two halves are independent draws conditional on the current world, not
evidence from different times or contexts by construction. This is corroboration
within a review, not a statistical confidence guarantee or temporal persistence
test. Half-batches are smaller and noisier individually; agreeing gains may
protect retention while making legitimate simplification harder.

The deck changes search coverage while keeping randomness. The gate changes
selection while keeping its evidence budget. Neither mechanism is learned;
neither is meta-learning, a fold, or a new agent architecture.

## World, pairing, and budget

Reuse the immutable Experiment 010 generator, six-feature representation,
192-main-record rolling window, Beta(1,1) cell estimator, .01-per-cell cost,
1,152 main observations, reviews every 64, and 32 fresh selection outcomes per
review. The reversible branch uses pair / single / pair worlds, each lasting
384 main observations. The persistent branch always uses the pair. Outcome
flip probability remains .10. No change signals or true probabilities reach
the learner.

Use NEW environment seeds 100–104 and NEW proposal seeds 100,101. Generator
seeding remains 20000+environment for permutation, 30000+environment for main,
40000+environment for selection. Learner RNG is Random(50000+proposal_seed).
Each environment/branch/proposal combination runs all four variants with paired
world observations. The same RNG seed does not give identical candidate lists
between deck and iid schemes, whose random operations differ. Diverging
incumbents can also change subsequent eligible sets.

5 environments *2 branches *2 proposal seeds *4 variants =80 runs.
Each uses 1,152 main +576 selection =1,728 outcome presentations:
**138,240 allocated and used outcome-bearing presentations**.
There are 17,280 generated world records in ten paired streams; branches
reuse random draws, and multiple learners reuse those records.
18*80*128 =184,320 base frozen evaluation predictions, plus separately counted
ablation calls; 18*80*4 =5,760 candidate fits. No extra seeds or tuning.

This is a modest increase in total comparisons to isolate two changes, not an
increase in model capacity or per-learner data. Five new environments vary
encoding and sampled evidence, not the task family. Outcomes from Experiment
010 are design evidence, not part of this benchmark's training or evaluation.

## Exact mechanisms

Start with the empty subset. Reuse the pool ordered as empty, six singletons,
then fifteen pairs. Four distinct non-incumbent candidates are fitted on the
main window and ranked by training log loss plus complexity, with tuple
tie-breaking. Only the winner advances to fresh selection.

IID generation matches Experiment 010: rng.sample(eligible_pool,4).

Deck generation starts with an empty queue. When empty, refill with a copy of
all 22 subsets, rng.shuffle it, and increment the deck number. Pop from its
front, discarding the current incumbent and any subset already chosen in this
review, until four candidates have been selected. Preserve the remainder
across reviews and structural changes. Never reset a deck at a world change.
Log the remaining deck and deck number at every review.

Each complete deck visits every subset; some are skipped because they are the
incumbent or already selected at a boundary. It does not guarantee that every
newly relevant candidate is proposed within each six-review world phase.
It also does not guarantee acceptance. A useful model may still be unfitted,
unproposed at the right time, or rejected on noisy evidence.

At selection, predict all 32 outcomes once with both fitted models. Let each
record's predictive gain be incumbent loss minus candidate loss, and let
C=incumbent complexity minus candidate complexity.

* Single gate: mean(all 32 predictive gains)+C >0.005.
* Split gate: mean(first 16 gains)+C >0.005 AND
  mean(last 16 gains)+C >0.005.

Log both half gains even for single-gate variants; this requires no additional
predictor calls or learning evidence. Log the full-batch gain and whether the
split gate vetoed a change that the full batch would accept. Selection never
fits models, enters the observation window, ranks proposals, or changes the
gate's fixed threshold.

## Evaluation and predeclared decision rules

Reuse Experiment 010's frozen enumeration of all 128 context/action pairs,
expected log loss, most-probable-outcome accuracy, exact relevant-subset check,
input-cut ablations, nuisance sensitivity, and evaluation isolation.

For each run, endpoint success requires:

1. Exact relevant subsets at 384,768,1152; accuracy=1 and expected-loss regret
   <=.10 at each endpoint.
2. At 384 and 1152, cutting either relevant input raises expected loss by
   >=.15 nats. No singleton/full-context control is rerun: their role was
   established in 010, and this follow-up isolates search and retention.
3. In the persistent branch, after the first review with the correct pair,
   accuracy=1 and regret<=.10, no subsequent review replaces the correct pair
   with another subset. This counts substitutions as well as cardinality
   reductions. It tests structural preservation, not constant predictive error.

Primary success: `deck_split` passes all applicable conditions in at least 8/10
runs in EACH branch. Report endpoint-only and continuous-preservation results
separately; a final recovery cannot hide a transient discarded relationship.
This is stricter than Experiment 010 and is not a direct success-rate comparison.

Secondary factorial comparisons are descriptive, with no significance claim:

* Coverage: for each pair phase, count whether the correct pair was proposed or
  already current at any review, and the fraction of the 22-subset pool visited
  (proposed or incumbent) across those six reviews. Compare deck versus iid
  under each gate on the paired environments and proposal seeds.
* Retention: count transitions from a correct pair to any wrong subset after
  first successful acquisition in persistent worlds. Compare split versus
  single under each proposal scheme; report reacquisition/recovery endpoints.
* Adaptation cost: report first successful review within each phase, phase and
  first-64-after-change pre-feedback losses, overall main loss, accepted changes,
  gate vetoes, and feature/fitting/search costs. A never-acquired pair cannot
  count as protected, and reduced changes do not by themselves count as benefit.

Evaluate corroboration and coverage independently even if the combined primary
criterion fails. Do not generalise either result to all stochastic learning.

## Verification and stopping

Synthetic tests cover deck traversal and duplicates at shuffle boundaries,
unchanged evidence budgets, a split-gate veto despite positive pooled gain,
acceptance on corroborated gains, selection isolation, preservation metrics,
and frozen evaluation including deck state. No benchmark learner pilots.

Before execution save SHA-256 hashes of this protocol, new implementation,
tests and independent audit, plus reused `bundles.py` and `audit_bundles.py`.
The independent audit must import no learner code, replay all saved streams,
candidate RNG, decks, counts, decisions, evaluations, metrics and costs, and
check hashes and the old Experiment 010 manifest. Refuse overwrite. Disclose
any implementation correction; do not hide a failed run or tune after results.

Run once and stop for findings. No automatic folds, new representation, learned
gate, further sample sizes, extra task families, or meta-learning benchmark.
