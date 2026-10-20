# Experiment 012: hide detail, delete it, or keep it exposed

Fixed before execution, 2026-10-20, following the user's instruction to proceed
after Experiment 011. This is a restricted information-hiding experiment,
not another tuning run of 010 or 011 and not a test of meta-learning.

## Question and limitations specified in advance

Can a learner expose a smaller predictive interface while preserving a
previously learned detailed predictor, and later recover useful detail without
being misled when the old relationship becomes wrong?

Here an interface is a selected subset of input coordinates and a Bernoulli
prediction table. It aggregates joint input configurations into equivalence
classes determined by the visible coordinates. The external prediction call
receives only these coordinates, enforced by an access-restricting view.
An optional detailed snapshot is private to the learner's review mechanism.
It is not consulted by ordinary predictions while hidden.

Raw observations of all six features are still sensed and stored in the
192-record search buffer. This experiment tests restricted prediction access
and retained predictor memory, not sensing savings, a Markov trace, information
theoretic sufficiency, or hidden temporal trajectories. The allowed
aggregation operations and snapshot time are constructed. Feature identities,
probabilities, and subsequent hide/reopen decisions are learned or selected.

## World, controls, and shared acquisition

Reuse the 010 generator and estimator with fresh environment seeds 200–204
and proposal seeds 200,201. Six iid binary features, random binary actions,
10% independent outcome flips, 1,152 main records, 18 reviews every 64,
32 independent selection records per review.

Three paired branches, using the same permutation/input/action/noise draws:

| Main indices | return | novel | persistent |
| --- | --- | --- | --- |
| 1–384 | s XOR t XOR a | s XOR t XOR a | s XOR t XOR a |
| 385–768 | s XOR a | s XOR a | s XOR t XOR a |
| 769–1152 | s XOR t XOR a | 1 XOR s XOR t XOR a | s XOR t XOR a |

Use the unchanged 010 `generate(seed,"reversible")` for return and novel,
and `generate(seed,"persistent")` for persistent. For novel, flip the generated
y after main index 768 and in selection batches whose review is >768.
No true mapping, branch, latent-feature identity, change indicator, or
evaluator result reaches a learner. The common acquisition-stage boundary at
384 is supplied by design; it is aligned with the first possible world change.
Discovery of when to form a durable memory is therefore not tested.

All variants first run unchanged 011 `deck_single` for main indices 1–384 and
six selection reviews. At 384 record its selected subset K and fitted table
as a prototype. This is learned from noisy data, not an oracle model. Freeze
K as the allowed detailed interface for the rest of this experiment; only
subsets of K can subsequently be exposed. Do not discard failed acquisition
runs or replace their K with the true pair.

Compare:

* `retain`: hide detail when supported, keeping the acquisition prototype
  frozen for possible retrieval.
* `delete`: identical access and proposal mechanisms, but erase that prototype
  on the first accepted change to a proper subset of K. Keep K's identity so
  that rebuilding has the same structural possibilities as retain. Thus the
  deletion ablates fitted predictive detail, not the entire feature language.
* `open`: always expose K after acquisition and keep fitting it to the same
  rolling main window. No post-acquisition structural decisions.

All variants retain raw observations for at most 192 main steps. By the end
of the 384-step middle phase, the original acquisition observations have
expired. A saved prototype therefore carries predictive information unavailable
in that recent-data window, at an explicit extra memory cost.

## Prediction, fitting, and reversible interface selection

Ordinary prediction receives a view that permits only the visible coordinates;
attempts to access other coordinates raise an error. Log actual main prediction
coordinate reads. The interface object contains the exposed prediction table,
not the private archive.

While the current source is `fresh`, refit that interface on the rolling window
after each main observation using the unchanged Beta(1,1) estimator. A retrieved
`prototype` remains frozen while deployed; main records still enter the buffer,
and reviews may replace it with a fresh estimate. Do not silently overwrite
the retrieved memory on the first subsequent update or double-count old data
as new observations. Report frozen deployment duration.

At each of the twelve post-acquisition reviews:

1. For retain/delete, fit fresh tables for every subset of K except the
   incumbent when it is already a fresh table. If a prototype is deployed,
   include a fresh K as a possible replacement.
2. If a prototype exists and the current interface is a proper subset of K,
   also consider the frozen prototype as a retrieval candidate.
3. Rank candidates using only the latest 64 main records: mean log loss plus
   .01 times the possible table-cell count, 2^(visible_dimensions+1).
   Fresh candidates still fit all 192 available main records. Rank ties by
   (subset tuple, source string), where `"fresh"` precedes `"prototype"`.
4. Advance only the winner to the new 32-outcome selection batch. Accept when
   incumbent objective minus candidate objective exceeds .005, using the
   original pooled-evidence rule. Selection never fits a model.

For a learned pair there are at most four candidates per review. The prototype
uses an extra candidate slot when available; the delete control may have one
fewer candidate. Report this as a cost, not a perfectly capacity-matched
comparison. Rebuilding can propose K at every review, so it is not delayed
by the shuffled global search that limited earlier experiments.

The open control receives the same allocated selection batches but ignores
post-acquisition selection outcomes. It has the same fitting window and
observations, not an identical compute or effective-feedback budget.

## Evaluation and fixed criteria

Evaluate immediately after every review, before any future data. Enumerate all
64 contexts under both actions. The evaluator alone uses true noisy outcome
probabilities to calculate expected log loss, regret against the noise oracle,
most-probable-outcome accuracy, exact relevant subset, and relevant-input cut
effects. Check that evaluation changes neither visible state, private prototype,
buffer, search RNG, nor costs. It cannot affect a decision or stopping.

For retain, define a complete trajectory:

* At 384, K is exactly the true pair, accuracy=1, regret<=.10.
* In return/novel, at 768 the interface is exactly the relevant singleton,
  accuracy=1, regret<=.10, and the original learned prototype is still retained.
  A real accepted hide operation must have occurred.
* At 1152, the interface is the true pair, accuracy=1, regret<=.10, and cutting
  either relevant input raises expected loss by >=.15 nats.
* In persistent, the pair remains exposed at every post-acquisition review,
  and endpoint prediction checks at 768 and 1152 pass. This is continuous
  structural exposure, not a guarantee of constant predictive performance.

Primary success requires ALL of:

1. At least 8/10 retain trajectories pass in EACH of the three branches.
2. In return, retain has lower mean pre-feedback loss than paired delete over
   main observations 769–960 in at least 8/10 runs, with mean improvement
   (delete minus retain) >=.02 nats across all ten, including acquisition
   failures. Report retrieval use; a speed claim needs the paired comparison.
3. In novel, mean retain-minus-delete loss over 769–960 is <=.02 nats.
4. In persistent, mean retain-minus-open main loss over 385–1152 is <=.02 nats.

These are fixed practical margins, not statistical significance or formal
noninferiority claims. All runs and acquisition failures remain in results.
Five environments crossed with two search seeds do not make ten independent
task families. Any conditional-on-acquisition result must also show its
denominator and cannot replace the unconditional primary criterion.

Report all variants' phase and transition losses; hide, reopen, retrieval and
prototype-deletion reviews; interface dimensions; frozen deployment duration;
feature accesses; candidate fits/scores; memory cells; and every accepted or
rejected proposal. Distinguish a structural reopening from predictive recovery.
Report stale-prototype proposals and acceptance in novel even if later corrected.

## Budget, provenance, and stopping

5 environments *3 branches *2 proposal seeds *3 variants =90 runs.
Each has 1,152 main +576 allocated selection outcomes:
**155,520 allocated outcome-bearing presentations**.
Actual use is at most 103,680 main +17,280 shared-acquisition selection exposures
+23,040 retain/delete post-acquisition selection exposures =144,000. If
acquisition leaves an empty K, it has no proper subset or alternative candidate;
post-acquisition selection is unused. Count actual use explicitly.
There are 25,920 generated records across 15 paired streams; repeated learner
exposures and paired branches are not independent world evidence.
18*90*128 =207,360 base evaluation predictions plus counted ablation calls.
Candidate fitting ceiling is 2,160 acquisition fits +2,880 later fits =5,040.
Maximum raw buffer 192; detailed subset at most two coordinates; prototype
at most eight [ones,count] cells. Report visible and archived cells separately.

Before execution save protocol/new source/test/audit hashes and the reused
010/011 implementation and independent audit helpers. Verify both previous
manifests unchanged. Refuse overwrite. Synthetic fixtures test prediction
access, hidden retention versus deletion, no hidden-model update, frozen
retrieval, evidence isolation, stale-memory rejection, and evaluator purity.
Independently replay streams, shared warmup, candidate construction/ranking,
memory transitions, predictions, selections, metrics, budgets, and hashes.

Run once; report failure without tuning. Disclose implementation corrections.
Stop after findings. No automatic temporal folds, rare-case extensions,
new capacity, learned retention policies, or meta-learning experiments.
