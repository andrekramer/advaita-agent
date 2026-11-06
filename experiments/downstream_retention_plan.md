# Next round: downstream adaptation without avoidable retention costs

Planned 2026-11-05. **Planning only: no new experiment or implementation has
started.** Recommended next study: 035, temporary downstream plasticity. A separate
preserved-memory study is conditional, not part of the initial run. This document
is a design proposal; implementation, passing fixtures and the final protocol
must be frozen before reserved outcomes are generated.

## Question and reason for the sequence

**Can we keep the adaptation benefit of downstream plasticity while reducing its
cost when earlier knowledge becomes useful again?**

[034](../results/coordinated-steering-v1/findings.md) found that downstream
plasticity, with protection held fixed, improved active composite loss by .096068
nats over protection alone in all 20 changing pairs. Adding local plasticity did
not improve that primary outcome: 16 ties, four small losses. The full criterion
failed through the incremental comparison and preservation costs. In reversal,
downstream-only return loss was .590336 versus .511768 for protection alone,
despite eventual recovery. This suggests testing exposure duration before adding
another learner, more simultaneous plasticity or a larger memory architecture.

We must distinguish three possibilities:

1. Plasticity stays open longer than necessary.
2. Faster revision genuinely sacrifices older useful evidence; stopping later
   cannot reconstruct what has already been lost.
3. Slow recovery involves interface/structural decisions as well as retention.

Timing is the smallest controlled change that can address the first possibility.
A failure would not prove the second, and a successful timing rule would not
establish general memory management or meta-learning.

## Step 0 — inspect the existing evidence

Before implementing 035, use saved 034 models and review traces to compare D with
P at the end of the boost and through return. Score the stored predictors on the
original and changed target mappings, with truth restricted to the evaluator.
Compare exported local partitions, upper interface choices, predictive errors
and reported fast/slow masses. Record when divergence first appears.

This is descriptive diagnosis, not a new causal experiment. Low evidence mass
alone does not show useful knowledge was lost. Models can recover eventually
while incurring large early-return costs. If intermediate raw evidence is needed,
reconstruct it from the saved stream and charge that as saved-data replay, not
fresh outcomes. No parameter search or selection of a favored seed is allowed.

Deliver a short mechanism note that separates observed behavior from hypotheses.
If it exposes a correctness problem rather than a timing question, resolve and
validate that issue before proceeding; do not run a benchmark through a known
confound. Do not silently repair frozen 034 sources or results.

## Step 1 — compare temporary downstream plasticity

Keep the 033/034 representation, coherent post-review snapshot, memory transfer,
automatic weakening, structural search and fast half-life unchanged. Protect the
same supplied stable local distinction from review 512 to review 1024 in every
condition. Both local slow stores keep their ordinary 1024-tick half-life.
Only the composite slow-memory boost duration varies:

| Policy | Composite slow half-life | When the boost ends |
| --- | --- | --- |
| P: protection only | 1024 throughout | No boost |
| D128: short boost | 128 while active | After review 640 |
| D256: medium boost | 128 while active | After review 768 |
| D512: long boost | 128 while active | After review 1024; reproduces 034 D |
| G: evidence-based closure | 128 while active | Two adequate fresh reviews, with review 1024 as a hard ceiling |

All boosts begin after review 512, an explicit supplied steering command. Ending
a boost restores composite half-life 1024; it does not restore lost evidence,
reset learning, undo search history or release the protected partition early.
All partition locks release after review 1024. No policy reopens plasticity later
in the run. Automatic opening/reopening is a separate future question.

### Proposed closure rule for G

Use the existing adequacy threshold of .55 nats, without tuning it on new outcomes:

- At each review from 576 onwards, freeze the currently deployed composite
  predictor **before any selection labels are used or local/upper review changes
  are made**. Score that predictor on the fresh 32-row selection batch.
- Two consecutive eligible reviews with observed mean loss <= .55 end the boost
  after the second review. A failed review resets the streak. Earliest closure 640.
- The normal learning review still proceeds. Closure changes the rate for
  subsequent observations only. Historical review losses must not be mislabeled
  as losses of a newly fitted post-review model.
- At 1024, release the lock and end any remaining boost in one configuration
  command. A still-open boost is recorded as ceiling closure, not adaptive success.
- Log prediction identity, batch identity, both losses, streak, closure reason,
  duration, configuration and checkpoint hashes. Checkpoint restoration must
  retain the streak and whether the one permitted closure has occurred.

Score the same diagnostics in all arms, but let them affect only G. The same
selection batch also supports ordinary review; disclose that reuse. Evaluate
benefit on subsequent main observations, not on the batch that chose closure.
The controller sees no clean target, task phase marker, return date or future data.
Its 512 opening command and 1024 ceiling remain supplied timing information.

This is a fixed evidence-responsive rule. It is not learned hyperparameter
selection, an internally discovered goal, or a claim to identify true causes.
Adequacy can be misleading; stable/no-change controls remain necessary.

## Worlds and comparisons

Use five fresh environment seeds, proposed 2400–2404, with proposal seeds 2400/2401;
recheck reservation before freezing. Do not generate them during planning.
Five policies × five histories × ten seed/proposal pairs = 250 runs:

1. Stable/no change.
2. Category remapping, then return, then another remap: the 034 schedule.
3. Polarity reversal, then return, then another reversal: the 034 schedule.
4. The same category change at 513, persisting through 2048.
5. The same polarity reversal at 513, persisting through 2048.

Retain the 034 misleading burst on the protected channel for changing histories
and the same 10% independent label noise. Pair returning and persistent histories
through 1024 with identical inputs and noise draws; only later clean mappings
change. Keep the horizon 2048 and reviews every 64. Persistent histories prevent a
short boost from being judged useful solely because the task happens to return.
The stable condition measures unnecessary adaptation. These remain five layouts
of a constructed family, not new-family generalization.

The supplied channel-role mapping must be reported explicitly. Do not drop bad
acquisitions, delayed/no closures or inconvenient seed/proposal pairs. The two
proposal seeds and shared histories are correlated; report environment means.

## Outcomes and proposed success criteria

G is the primary candidate **before** outcomes; do not choose whichever duration
wins afterwards. D128/D256 are prespecified simpler alternatives and sensitivity
controls. Freeze exact comparisons, windows, thresholds and budgets after the
engineering checks and before any fresh run.

Measure expected and observed loss for all three outputs, form correctness,
upper interface/raw-port use, slow/fast mass, actual boost duration, closure
frequency and reason, full validity, and resource cost. Expected losses use clean
truth only in evaluation. Snapshot consistency and model identity remain audited.

Primary windows are fixed for every run, not aligned retrospectively to closure:
active 513–1024; early return 1025–1280; whole return 1025–1536; later 1537–2048.
Also report burst 513–640 and settled 641–1024. Duration-aligned plots are secondary.

Proposed full gate for G:

1. **Retained adaptation:** in EACH of the four changing histories, active expected
   composite loss is no more than .02 nats worse on average than D512, and no
   individual pair is more than .10 worse. Pooled active gain over P is at least
   .02 nats and positive in at least 28/40 changing pairs.
2. **Useful return:** versus D512, pooled early-return expected composite gain is
   at least .02 nats and positive in at least 14/20 returning pairs. Each returning
   history must have positive mean gain; pooling cannot conceal a mean loss.
3. **Preservation:** versus P and D512, all three expected-output mean costs are
   <= .02 and individual costs <= .10, separately by history in whole-return/post-
   release and later windows. Apply the same limits to stable active behavior.
   Bound early-return costs against P by the same limits. In persistent histories
   the 1025–1536 interval is a post-release window, not a return.
4. **Representations and endpoint:** protected-form burst correctness >= .95 in
   each changing history; G final full validity >= 8/10 in each history. Full
   validity retains correct local partitions, modal composite accuracy 1 and
   expected composite regret <= .10.
5. **Correct execution:** all commands, release behavior, fresh evidence use,
   prediction-before-selection ordering, coherent snapshots, copied inspection,
   budgets and checkpoint continuation pass independent verification.

Positive paired gains mean > 1e-12. Keep observed-loss comparisons beside expected
ones, particularly during the deliberately misleading burst. Report every guard
failure. Passing endpoint validity cannot erase poor recovery trajectories.

Apply the same outcome bundle descriptively to the two fixed pulses, with clear
secondary status. Compare G directly with both. If a fixed pulse is as good, do
not claim evidence-based closure adds value. A pulse selected from these outcomes
would need a separately frozen fresh confirmation before an adoption claim.
These comparisons are not exposure-matched, so a result cannot isolate the value
of the diagnostic information independently of its effect on duration.

## Engineering and resource boundaries

Extend the optional experimental path, not frozen classes or the default. Before
fresh outcomes, validate D512/P compatibility on saved/reused data, closure at
both boundaries, reset after a failed witness, ceiling/no-closure behavior,
exactly-once configuration, active checkpoint restoration and release. Include
synthetic cases where adequate recent prediction is misleading. The independent
auditor must reconstruct the controller as well as the learning arithmetic.

Proposed allocation: 25 worlds, 250 runs, 256000 generated scalar labels and 2560000
training presentations if the existing acquisition/review sizes are retained.
Keep main/evaluation/diagnostic queries separate; equal diagnostic scoring costs
across arms do not mean identical learning computation. Allow at most 8 fixture
attempts using reused fixtures plus explicitly counted synthetic steps. No new
random fixture outcomes or adaptive fresh-seed expansion.

Provisional caps for the final protocol: 400000 candidate fits, 25m scoring queries,
130m fit-related raw-bin visits, 300000 grid predictions, and 900s each for runner
and auditor. Count additional selective decay and controller queries explicitly;
verify formulas before freezing. Hash all new sources, fixture records and
recursive 034 dependencies. Save partial failures and do not overwrite results.

## Decision after 035; no automatic follow-up

| Finding | Interpretation and proposed next step |
| --- | --- |
| G preserves adaptation and improves return, with guards passing | Confirm on fresh timing/duration variations; do not yet claim autonomous steering. |
| A fixed pulse performs as well as G | Prefer the simpler timing explanation; evidence-based closure has not earned its complexity. |
| Only a secondary pulse passes | Treat it as a candidate for fresh confirmation, not a retrospective primary success. |
| Shorter boosts lose adaptation, or none adequately preserves return | Investigate protected recovery memory after distinguishing remaining structural effects. |
| A correctness or accounting check fails | Repair and audit the engineering separately; preserve any already generated outcomes. |

### Conditional later study: one preserved downstream predictor

If timing alone proves insufficient, prepare a separate proposal for preserving
one pre-intervention composite predictor while an active predictor adapts.
Do not merge this into 035: it would change memory capacity, capture, compatibility
and admission as well as timing.

Build on [021](../results/prospective-memory-v1/findings.md) and
[022](../results/memory-selection-v1/findings.md), which found useful but
inconsistent recall. Memory could influence selection without being retrieved,
and ordinary refitting could erase restored numerical parameters. A new weighted-
memory integration must address those issues explicitly.

A later design should compare no archive, a shadow archive and evidence-qualified
use with matched capture/scoring work; keep at most one confirmed snapshot and
record its evidence and semantic dependencies. A frozen predictor must not
silently bind old category IDs to new meanings. Restoration or separate deployment
must have defined persistence under subsequent refits. Test compatible return,
incompatible/changed return and permanent change. Admission must use fresh
observed evidence; an oracle recall condition, if included, is diagnostic only.
No design is selected or implemented here, and this conditional step requires
its own protocol and decision before running.

The original default remains unchanged throughout. The intended claim is a
bounded improvement in controlled adaptation and retention, not consciousness,
general agency, general steerability, meta-learning or a safety advantage.
