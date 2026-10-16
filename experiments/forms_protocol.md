# Experiment 006: acquisition of action-conditioned forms

Fixed before benchmark execution, 2026-10-15. Implements the acquisition stage
of [the research plan](forms_research_plan.md). Five seeds 0–4, one run per
condition, no tuning after results. Later retention/revision/exploration stages
are outside this run.

## Environment and evidence

The simulator has x=(s,t,c), action a in {0,1}, outcome y=s XOR a. Per seed,
random.Random(seed) shuffles the feature positions; this encoding is identical
for all learners. Only the harness knows the relevant feature. Learners receive
three numbered feature positions, chosen action, and then outcome. They receive
no category IDs or target category count. Features and hypothesis language are
supplied, so this tests discovery of a grouping within that language.

Withhold 000 and 111 entirely from training, proposal fitting, selection, and
learning diagnostics. The other six contexts times two actions give 12 pairs.
Use 16 independently shuffled balanced passes (192 training pairs), generated
with Random(1000+seed). After every 48 training pairs supply a fresh shuffled
balanced selection batch of 12, generated with Random(2000+seed). Selection
has the same deterministic outcome process as training; it is separate feedback,
not an independent source of truth about the rule. Actions are scheduled by the
harness, not chosen by the learner.

No label is read before its prediction. Structural candidates are completely
fitted/ranked before accessing their selection batch. Selection outcomes never
enter the structural training buffer or future sufficient statistics. Baselines
use selection pairs for ordinary sequential learning. All learners have 240
allocated and accessed feedback pairs, but use them in different ways; report
this distinction. All final evaluation is frozen and occurs once per run.

## Representation and mathematical updates

A recognition leaf is a length-three cube in {*,0,1}^3. Leaves partition the
eight possible contexts. Each leaf refers to one form. Multiple leaves may
refer to a shared form. Canonically order cubes lexicographically (* before 0
before 1) and assign form IDs in order of first occurrence. IDs identify the
current model version; record the full old-to-new structure rather than assuming
ID identity survives a change. Start with one all-wildcard leaf and one form.
Maximum eight leaves and four forms. All contexts have exactly one matching leaf.

For each form k and action a keep success count r_ka and total count n_ka.
Predict p(y=1|x,a)=(r_ka+1)/(n_ka+2), where k is recognised from x. Thus an
unobserved form/action combination predicts 1/2. Counts are observations, not
confidences or ontological commitments. A stream update increments n by one
and r by y. No forgetting is used in this stationary acquisition test.

Keep at most the 192 main training records. At each boundary enumerate the
incumbent structure and every legal one-operation neighbour:

- Split any leaf on one of its wildcard feature positions. Its two children
  receive fresh separate form IDs; other leaves retain their groupings.
- Merge any pair of forms. All their leaves share one response predictor.
  Repeatedly collapse sibling cubes that differ in exactly one fixed bit and
  refer to the same form, choosing the lexicographically first legal pair.

Discard over-cap candidates and duplicate canonical structures. A hard maximum
of 31 unique candidates applies per boundary (incumbent, at most 24 split
proposals, at most six merge proposals); stop on a violation. Refit counts for
every candidate using only the main training buffer. Never divide parent counts
arbitrarily or create outcomes for unobserved children. Score each candidate by

J(M;B) = mean binary log loss on B + 0.01 K(M) + 0.005 L(M).

K is number of forms, L number of leaves; logs are natural. Choose the smallest
J, with canonical-structure order breaking exact ties. Record every candidate
and score. Only the winner is tested on the next selection batch; others are
logged as not advanced, not as externally rejected. Select the winner over the
current deployed model only when J(current;V)-J(candidate;V)>0.001. Score all
12 selection pairs before changing any structural state. The complexity penalty
is a designed preference, and its value is fixed here, not inferred from data.

## Four learners

1. **lookup:** per-exact-context/action Beta(1,1) counts. Unseen contexts remain
   at 1/2. Update on all main and selection feedback.
2. **single_structure:** one deployed structural model. Main training updates
   its counts immediately. At boundaries perform the candidate procedure above;
   replace the deployed model on acceptance, otherwise keep the updated incumbent.
3. **retained_structure:** a retained deployed model N, plus provisional A with
   the same structure. Main training updates A only; N supplies the reported
   predictions and remains fixed until selection accepts a candidate. Generate
   the same candidate pool from the current structure, fit on the same buffer,
   and use the same selection rule as single_structure. If accepted, replace N
   with the winning model. After every boundary set A to the current structure
   refitted on all main feedback, including after rejection. Log A predictions
   as a separate diagnostic; do not substitute their accuracy for N's results.
4. **fixed_features:** logistic prediction with eight fixed features
   [1,b,u0,u1,u2,b*u0,b*u1,b*u2], b=2a-1 and ui=2xi-1.
   Initialise all weights at zero. After each main or selection pair apply
   w <- clip(w+0.1*(y-p)*features,-8,8). Log clipping. These interactions can
   express the simulator's rule but contain no learned category operation.

Both structural variants have one search per boundary, identical candidate
language, fitting buffer and evidence allocation. Actual candidate counts may
diverge with learned structures and must be reported. The retained model has an
extra parameter snapshot and provisional predictions; storage and these extra
computations are costs, not hidden free capacity. No feature semantics or
simulator equation enter learner classes.

For retained_structure, before each search compute
D=mean_U |p_A(1|x,a)-p_N(1|x,a)| on the 12 admissible pairs; update
Dbar=0.75 Dbar+0.25 D, initially zero. Record signed gaps. Reviews are scheduled
every 48 pairs regardless of D, so identical wrong models can initiate a split.
This run does **not** test the necessity of a differential trigger. It tests a
provisional/retained structural mechanism, not the previous F/S additive-weight
equations. Structural promotion need not conserve predictions. Record its
maximum change on the admissible contexts; report it without treating it as an
error. Both time scales use externally checked evidence; slower here means less
frequent accepted replacement, not a claim of abstraction by definition.

## Evaluation, criteria, and budget

After all four boundaries, snapshot each learner. Predict both actions on all
eight contexts with no mutation. Reveal outcomes only for the four withheld
context/action pairs, once. The other 12 predictions are unlabelled diagnostics.
For structural models report the complete final partition and probability table.

For each structural learner, the acquisition criterion requires **all** of:

- 100% accuracy on the four withheld pairs (ties predict 0), mean loss <0.25.
- Exactly two forms and two recognition leaves.
- Exact evaluator-only partition agreement with the simulator's relevant bit,
  checked on all 28 pairs of contexts independently of form IDs.
- Maximum change in predicted probability when either nuisance bit is flipped
  <=1e-12; minimum change when the relevant bit is flipped >=0.5, for each action.

Latent partition labels are evaluator-only diagnostics from the known world
design, never learner feedback. Report all outcomes, not just the pass indicator.
Report every seed, main pre-update loss, candidate counts, decisions, feedback
use, and final loss/accuracy for all four learners. Five seeds are descriptive;
passing is not evidence of statistical superiority. A dual-timescale advantage
has no assumed pass criterion in this acquisition test. If both structural
learners pass, form discovery is supported but the need for retention is not.
If fixed_features succeeds, explicit forms are not necessary for prediction.

Exactly 5*4*(192+48+4)=4,880 outcome-bearing presentations; 240 additional
unlabelled final diagnostics. Retained A/N comparisons add 5*4*12=240 paired
unlabelled probes (480 model predictions), plus logged A predictions during
main training. Candidate scoring reuses stored main labels; selection scores
reuse the single allocated selection batch for incumbent and winning candidate.
Record computation separately from newly presented evidence. No other seeds,
parameter search, or automatic follow-on experiment. Unit fixtures use separate
synthetic examples, not the benchmark stream or withheld outcome performance.

## Verification and provenance

Before running, test representation coverage/caps, split/merge accounting,
feedback isolation, predictive updates, and immutable evaluation. Save protocol
and source hashes, encoded streams, pre-update predictions, state snapshots,
candidate scores/counts, selection predictions/decisions, and all final metrics.
Independently audit saved records, including update arithmetic, candidate counts
from training data, selection decisions, frozen final evaluation, budgets, and
source hashes. Stop on numerical, budget, or separation failures. Corrections
to implementation bugs must be disclosed; do not change this protocol based on
benchmark outcomes. All actions remain inside the synthetic simulator.
