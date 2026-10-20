# Experiment 010: stochastic discovery and revision of minimal bundles

Fixed before benchmark execution, 2026-10-20. First experiment of the new round,
not an extension or rerun of the historical directory `results/round2-v1`.
Run once, report failures, do not tune on benchmark results.

## Question and representation

Can a learner discover a predictive relationship between two supplied binary
distinctions, cease using one when it becomes irrelevant, and reacquire the
relationship under noisy feedback? Does stochastic proposal search help or
hurt relative to deterministic search with the same candidate budget?

A minimal bundle is a selected feature subset K of size two and its joint
action-conditioned Bernoulli table. Size-one and empty subsets are permitted.
This supplies the representation and structural operators; it does not supply
the relevant features or the learned outcome table. Each subset with k features
has 2^(k+1) possible context/action cells. Distinct cells are not claimed to be
distinct learned semantic forms; equal consequences can occur in several cells.

## World and randomness

Six independent uniform binary features x, a uniform binary action a, and an
observed outcome y. In latent coordinates s=x[0], t=x[1]:

* Pair world: y = s XOR t XOR a XOR e.
* Single world: y = s XOR a XOR e.
* e is an independent Bernoulli(0.10) error on every presentation.

For each environment seed 0–4, permute the six feature positions with
Random(20000+seed); observed x[j] is latent x[permutation[j]]. Draw 1,152 main
records with Random(30000+seed), drawing six bits with randrange(2), then the
action, then one random() for e. Generate 18 fresh selection batches of 32
records with Random(40000+seed), using the same draw order.

Two branches use identical inputs, actions, noise draws, and permutations:

| Main indices | Reversible branch | Persistent branch |
| --- | --- | --- |
| 1–384 | Pair | Pair |
| 385–768 | Single | Pair |
| 769–1152 | Pair | Pair |

Selection uses the world at its review index. No change signal, latent feature
index, noiseless target, noise probability, or evaluation result reaches the
learner. Main and selection streams are independent. Actions are externally
randomised; autonomous exploration is not tested. Inputs are iid; this is a
changing interaction task, not temporal dependency discovery. World changes
are fixed and aligned to reviews; random change timing is not tested.

## Learners and update sequence

All estimators keep the latest 192 main records without resets at world changes.
For every cell, q=(ones+1)/(count+2). Predict each main outcome before fitting
that observation; then expire old records and refit the current subset.

Variants:

1. `stochastic`: subsets of size 0, 1, or 2; four candidates uniformly sampled
   without replacement at each review, excluding the current subset.
2. `deterministic`: the same language and four candidates, cycling through the
   ordered pool, skipping the incumbent. The cursor persists across reviews.
3. `singleton`: stochastic proposals restricted to size 0 or 1, four per review.
   This tests the restriction against joint conditioning. It is not a general
   additive, neural, or complementary-processing baseline.
4. `full_context`: fixed subset of all six features (128 possible cells).
   Same estimator and fitting window, no structural search.

The ordered pool is the empty tuple, then singleton tuples in feature order,
then pairs in itertools.combinations order. All structural variants start with
the empty subset. For the two stochastic variants use independent proposal
seeds 0 and 1 via Random(50000+proposal_seed). Proposal RNG is separate from
environment RNG. Deterministic and full-context controls run once per
environment/branch, not twice as if their duplicates were independent.

Review every 64 main records, after updating the incumbent on that record:

1. Fit four candidates using only the current main window.
2. Rank by mean window log loss + 0.01 * possible-cell-count. Break ties by the
   subset tuple. Only the winner advances to selection.
3. Score the winner and incumbent on the new selection batch, adding the same
   complexity costs. Accept if incumbent objective minus candidate objective
   is strictly greater than 0.005. Selection never fits either model, enters
   the buffer, or changes candidate generation.

No candidate is generated using selection outcomes. The full-context learner
has the same allocated evidence but does not use selection outcomes, because
it has no structural decision. Report actual as well as allocated evidence.
A full-context comparison does not match parameter count or fitting work;
its extra sparsity is an explicit tradeoff, not proof that bundles are necessary.

## Selective use and evaluation

At prediction, the table reads only features in K plus the supplied action.
The bounded search buffer retains all six observed features for possible
rediscovery. Count prediction feature reads separately from fitting/search
reads. This is a constructed access mechanism with a learned feature choice,
not a learned interface, a reduction in sensing, or deletion of the raw detail.

After each review, freeze the learner and enumerate all 64 contexts under both
actions. The evaluator alone uses the simulator's true Bernoulli probabilities
to compute expected future log loss, accuracy against the most probable outcome,
and regret relative to the 0.10-noise oracle. No evaluation labels are drawn
or revealed. Evaluation samples no new training outcomes and cannot affect
updates or stopping. All contexts may occur in training: this is distributional
prediction, not a withheld-combination transfer test.

For each selected feature, cut its input to the predictor by averaging its two
possible values with equal weights. Evaluate expected log loss of that averaged
prediction. This is a frozen predictive-input ablation, not an intervention
on the world's causal mechanism. Its loss increase measures use of that feature
in conjunction with the others. Report nuisance-feature invariance from the
enumerated prediction table.

## Predeclared criteria

A stochastic run passes the structural/predictive criterion when all three
phase endpoints (384, 768, 1152) select exactly the relevant pair, single, pair
in the reversible branch, or the relevant pair at all three persistent
endpoints; all endpoints have 100% most-probable-outcome accuracy and expected
log-loss regret <=0.10 nats. An endpoint split is not enough without prediction.

At both pair endpoints 384 and 1152, additionally require:

* Expected log loss at least 0.15 nats lower than the mean of the two paired
  singleton proposal-seed runs.
* Cutting either relevant input raises expected log loss by at least 0.15 nats.

Primary success requires all these conditions in at least 8 of the 10
stochastic runs in EACH branch. Ten runs comprise five environments crossed
with two proposal seeds, not ten independent environments or task families.
Report every run and fractions; no significance or universality claim.

Stochastic versus deterministic search is a secondary, direction-neutral
comparison: report endpoint loss, main pre-feedback loss, discovery/recovery
reviews, and proposal-seed variation. Do not claim randomness helps unless
the comparisons support it; no post-hoc superiority threshold.

Also report phase-wise main loss, first-64-observation transition loss, every
accepted change, conditional-pair recovery, persistent-branch spurious removal,
prediction feature reads, possible-cell counts, all candidate fits/refit rows,
and actual selection use. A smaller subset is not by itself success.

## Budget, verification, provenance, and stopping

5 environments *2 branches *(2 stochastic +2 singleton +1 deterministic
+1 full-context) = 60 runs. Each has 1,152 main and 576 allocated selection
outcomes: **103,680 allocated outcome-bearing presentations**.
There are 17,280 generated world records across ten paired streams; paired
branches reuse random draws and have identical outcomes outside the middle
phase. They are not 17,280 independent draws.
Actual selection use is 50 structural runs *576 =28,800; total used main plus
selection presentations =97,920. Repeated exposure by different learners is
counted in presentation budgets, not as additional independent world evidence.

18 evaluations *60 runs *128 contexts/actions =138,240 base predictions.
Input ablations add a variable, fully counted number of predictor calls.
Four candidates *18 reviews *50 structural runs =3,600 candidate fits.
No hidden pilots, further seeds, parameter searches, or follow-on benchmarks.

Before execution, save source, protocol, plan, tests, and audit SHA-256 hashes.
Synthetic tests cover counting, isolation, selective access, candidate budgets,
and phase/noise generation without running benchmark learners. Independently
reconstruct all saved predictions, candidates, decisions, evaluation, metrics,
RNG streams, budgets, and hashes without importing experiment code. Refuse to
overwrite results. Stop on verification failures and disclose corrections.

Stop after this run and its findings. This experiment does not establish
learned folds, nested Markov models, meta-learning, autonomous exploration,
Kelso phase dynamics, robust complementarity, or any safety advantage.
