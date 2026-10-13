# Experiment 002: four-state learning and reversal

Protocol fixed before the first experiment run. This is a bounded, offline
extension of Experiment 001, not the cue-gap-action benchmark in maths-v1.md.

## Questions and scope

Can the fast/slow rule learn a mapping involving all four participation states
00 (neither), 10 (first only), 01 (second only), and 11 (both), then relearn after
an unannounced change? How does it compare with single-timescale controls?

The input and output are separate oppositions. Their states are encoded as four
categorical values in the order 00, 10, 01, 11. All four inputs have explicit
one-hot features, including observed 00; missing input is not part of this task.
This is a saturated conditional lookup model, not a test of compositional logic
or generalization. There are three learned output logits per input, with output
00 fixed to zero as the reference. This categorical input encoding extends the
tiny experiment and makes the observed-neither case explicit.

## Model and controls

For input i, p(k|i)=softmax(0, W[i,10], W[i,01], W[i,11]), where W=F+S.
After recording a prediction, the external teacher reveals y. The gradient for
each learned output k is g[j,k]=1[j=i](1[y=k]-p(k|i)). All weights start at zero.
Each training presentation applies simultaneous updates
F'=clip(0.95 F + 0.20 g, -8, 8),
S'=clip(0.999 S + 0.02 g, -8, 8).
Inactive input rows decay too. Fixed input features correspond to fully loaded
traces with no delay; phases and communication gates stay fixed at 1.

Four variants receive identical data within each seed:

- Fast/slow: the preceding rule, inherited unchanged from Experiment 001.
- Fast only: W'=clip(0.95 W + 0.22 g, -16, 16).
- Slow only: W'=clip(0.999 W + 0.22 g, -16, 16).
- Frozen: zero weights throughout.

The single-rate step sizes equal the combined initial step size (0.20+0.02),
and their weight bounds match the combined model's possible effective range.
They are controls for retention timescale, not individually optimized baselines.
The dual model has 24 retained parameters and each single model 12. No tuning,
architecture search, actions, phase learning, structural changes, consolidation,
or real-world connection is enabled. Slow learning remains direct from targets;
this experiment does not test slow learning from fast.

## Data and fixed budget

- Seeds 0 through 4; all results reported.
- For each seed, independently shuffle an initial permutation of the four output
  states. Choose uniformly from the nine permutations that change every input's
  target to obtain the second mapping. The learner receives neither mapping nor
  a phase-change flag; only input followed by target.
- Phase 1: 400 training pairs, exactly 100 per input, shuffled with seed 1000+s.
- Freeze all state for 100 evaluation pairs (25 per input), seed 3000+s.
- Phase 2: change the mapping, then 400 pairs, seed 2000+s, same balance.
- Freeze all state for 100 evaluation pairs, seed 4000+s.
- Teacher mapping randomness uses seed s. Evaluation repeats known input types,
  independently shuffled; these are not unseen-input generalization tests.
- Exactly 20,000 presentations: 16,000 training (including 4,000 frozen-control
  presentations) plus 4,000 evaluation. There are 12,000 weight-update events.
  Read-only evaluation neither updates nor decays weights.

## Criteria and reporting

The primary fast/slow acquisition and adaptation criterion is at least 90%
accuracy and mean natural-log loss strictly below 0.9 in **each** of the two
frozen evaluations, for **each** seed. With four equally represented input
types, the accuracy requirement effectively requires all four mappings correct.
Report control performance against the same thresholds, but frozen-control
failure does not affect the primary outcome. The uniform frozen baseline is
25% accurate with loss log(4). Ties choose the earliest state in the fixed order.

Report phase-wise pre-update loss, evaluation accuracy and loss, and recovery:
the first post-change trial with trailing-40 pre-update accuracy at least 90%,
using only post-change examples. Record null if not reached within 400 trials.
This is an operational threshold, not evidence of permanent recovery. Compare
paired seeds and display every seed, without claiming statistical significance
from five runs. No dual-timescale superiority criterion is assumed in advance.

Check finite normalized probabilities and bounded weights throughout; record
clipping counts. Save all predictions, targets, post-update weights, evaluations,
parameters, mappings and counts. Plot trailing-40 pre-update loss (reset at the
change) and evaluation/recovery comparisons. Smoothing is for display only.
Record failures without adjusting parameters or criteria after seeing results.
