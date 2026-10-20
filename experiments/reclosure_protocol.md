# Experiment 014: returning to a nested abstraction

Fixed before execution, 2026-10-20. Follow-up to the user's request to round out
capabilities after 013. Test one added operation: re-hide detail after evidence
supports a smaller interface, without waiting for the current predictor to fail.
Run once on fresh seeds; stop after the findings and a capability consolidation.

## Scope

Use the unchanged 013 local partition learners, observation channels, supplied
two-level wiring, conditional tables, proposal search and upper failure/reopening
rule. Compare that rule against adding corroborated reclosure. Do not change
local acceptance, add depth, add goals/preferences, or claim meta-learning.

The previous experiment demonstrated transfer and selective reopening but
could bypass a temporary local error permanently. This experiment tests return
to abstraction separately from the ability to open it. It does not learn the
reclosure rule, its thresholds, or a general evidence-accumulation policy.

## Worlds and matched controls

Environment seeds 400–404, learner seeds 400,401. Same 013 acquisition:
256 main local records per module, four 32-record selection batches per module,
then 256 composite training records using representatives. The two lower
groupings and higher predictor are learned; local-effect supervision, canonical
group naming and representative training curriculum are supplied.

Generate 768 adaptation main records and twelve fresh selection batches of 32.
Each record has two local labels and one composite label. Balance raw pairs
and action in shuffled blocks of 32, with independent 10% flips per label.
RNG construction continues the 013 scheme with fresh seed values: layout
61000+environment, inputs 62000+environment, noise 63000+environment. Generate
all 768 main records before the selection batches. Learner RNGs are
64000+2*learner_seed+module. Branches share layout, inputs and noise draws.

Four branches:

* `persistent`: unchanged local and composite relationships.
* `remap`: throughout adaptation, invert the forms of the two representative
  states in the affected lower module. Composite outcomes follow the new forms.
* `breach`: local forms stay unchanged; composite outcomes additionally depend
  on whether the affected module's raw state is an alternative realization.
* `transient`: breach through main record 384 and its selection review; revert
  to the original composite relationship from main record 385 onward. Local
  effects never change.

The learner receives no phase/branch identifier or switch signal. All variants
continue their bounded buffers and state without a reset at 384.

Compare two variants:

* `failure_only`: exactly the 013 upper failure/reopening rule.
* `reclose`: the same rule plus the operation below.

Both learn local groups identically, receive the same outcomes, fit the same
three upper candidates per review and retain the same 192-record buffers.
The extra operation costs additional candidate scoring and up to eight pending
table cells; do not describe it as perfectly compute/memory matched.

## Reclosure operation

At every review, first perform local selection. Then prepare the normal three
upper candidates (coarse, fine0, fine1) from the recent main buffer. Run the
unchanged failure rule: current loss >.55 nats and winner improvement >.02 on
fresh composite selection. That operation has priority.

For `reclose`:

1. If the ordinary failure rule accepts a replacement, clear any pending
   reclosure evidence and use that replacement.
2. If the incumbent is coarse, keep no pending challenger.
3. Otherwise, maintain one frozen coarse challenger and the pair of exported
   lower group maps under which it was constructed. If either group map has
   changed since its last witness, invalidate it. Start a new challenger from
   the already-prepared fresh coarse candidate when none remains.
4. Score this frozen challenger on the current fresh composite selection batch.
   A witness passes when challenger mean log loss <=.55 and challenger loss
   minus current fine loss <=.02 nats. These are practical adequacy margins,
   not a statistical noninferiority test.
5. Require two consecutive passing review batches for the same frozen table
   under unchanged exported group maps. Then deploy that table as the coarse
   predictor and clear pending evidence. Any failed witness clears the candidate.

Candidate fitting never uses selection observations. No first-batch refit is
allowed between witnesses. The same current selection batch serves the existing
failure decision and the additional comparison; report this adaptive use of
evidence rather than claiming entirely independent policy selection. Successive
batches have independent noise. No additional outcomes are acquired.

A deployed coarse table stays frozen between accepted reviews; deployed fine
tables continue the unchanged 013 refitting rule. Main predictions never consult
the pending challenger. No archive of previous fine predictors is added.

This prefers the smaller supplied interface once it is adequately predictive.
It is a constructed structural preference with explicit tolerance, not the
absence of design assumptions. There is no weighted complexity reward or new
goal catalogue. The two-witness requirement is not assumed to improve reliability:
the controls and negative branch test its consequences.

## Fixed evaluation and criteria

Evaluate transfer on the same 24 withheld composition/action contexts before
adaptation, and all 32 contexts after each adaptation review. Only the evaluator
sees true probabilities, affected module and phase. Check evaluator purity,
including pending evidence and learner RNGs.

Validity means exact exported local forms, modal-outcome accuracy 1, and
expected log-loss regret <=.10 above the 10% noise oracle. All acquisition
failures remain in denominators.

Primary success requires all of:

1. At least 8/10 transfer-valid runs for each variant (count once per seed pair,
   not four times for shared branches).
2. At least 8/10 final-valid, coarse `reclose` runs in each of persistent and
   remap. Persistent mean pre-feedback loss must be <=.02 nats above failure_only.
3. At least 8/10 final-valid `reclose` runs exposing the affected module in
   breach. Mean pre-feedback loss must be <=.02 nats above failure_only.
4. At least 8/10 `reclose` transient trajectories have a valid, affected fine
   interface at 384; a valid coarse interface at 768; and an actual accepted
   two-witness reclosure after 384.
5. In transient, `reclose` has strictly fewer parent raw-state accesses over
   main records 513–768 in at least 8/10 pairs, and their overall mean is at
   most 75% of failure_only's positive mean. Over records 385–768, its mean
   prediction loss must be <=.02 nats above failure_only.

Five environments crossed with two search seeds are not ten independent tasks.
These margins are fixed practical targets, not significance claims. Report
all reclosures, reopenings, pending invalidations, premature hiding in breach,
predictive recovery separately from structural change, and intermediate failures.
A primary pass does not mean every interface decision was correct.

## Budgets and reproducibility

5 environments *2 learner seeds *4 branches *2 variants =80 runs.
Per run 768 local acquisition labels +256 composite training +2,304 adaptation
main +1,152 adaptation selection =4,480 used and allocated label presentations.
Total **358,400**. The 20 generated branch streams contain 89,600 labels,
including repeated paired acquisition. Repeated presentations are not new
independent evidence.

32,640 evaluation predictions (80*(24+12*32)). Exactly 10,240 local candidate
fits and 2,880 upper candidate fits; a pending challenger reuses a prepared
coarse table and adds no fitting. At most 15,360 extra challenger-selection
predictions. Each local buffer and the composite buffer contain at most 192
main records; the extra pending table contains at most eight cells.

Hash the new protocol, implementation, tests, auditor and reused 013 source/
independent arithmetic helpers before the run. Verify all manifests from
010–013 unchanged. Refuse overwrite. Test consecutive witnesses, no refitting,
reset on failed evidence or changed groups, failure-rule priority, preservation
of relevant detail, access restrictions and feedback/evaluation isolation.
Independently replay worlds, original decisions, new evidence state, outputs,
metrics, costs and all hashes. No rerun or tuning after results.
