# Learning and revising distinctions: evidence and limits

Consolidation, 2026-10-16. These are small, isolated experiments within supplied
representations. They explore whether useful distinctions can be learned and
revised; they do not establish a general-purpose learner or a safety advantage.

## What changes, and what stays constructed

The structural learners change action-conditioned probability estimates and
the grouping of contexts into forms. They can propose a split, merge forms,
and collapse redundant recognition leaves. Selection uses observed outcomes
and a supplied complexity preference. Names are neutral identifiers, not
additional learned semantics.

The perceptual features, action alphabet, representation language, allowed
operations, estimator, window size, review schedule, selection margin, and
complexity penalties are constructed and fixed within each run. **No
meta-learning has been demonstrated:** the experiments do not learn how to
change their learning rules or regulate these hyperparameters.

Fast adaptation and slower retained learning are two supplied functional roles.
They are not learned levels of a category hierarchy. A slower update rate or a
retained snapshot alone does not demonstrate an enduring "I know that" capacity
under interference. Nor does relearning a category establish memory of its
previous incarnation.

## Evidence across experiments

| Question | Observation | Boundary |
| --- | --- | --- |
| Can supplied associations be learned? | Tiny and four-state mapping tasks reached 100% final accuracy. | Slow-only outperformed the tested dual learner on final loss in the reversal task. |
| Can fast learning contribute to slower weights? | Selected transfer improved post-gap loss over parallel fast/slow learning; transfer-only slow weights learned useful predictions. | Slow-only remained better; selection rejected no hybrid candidate, so its necessity was not established. |
| Can useful categories be acquired? | Experiment 006 learned the relevant two-form partition and generalized to withheld combinations in all five seeds. | Single and provisional/retained structural learners had identical final results; the feature language and operations were supplied. |
| Do situated and retained learning robustly complement each other? | Experiment 007 learned a smooth response relationship; using its feedback improved motion prediction. | The predeclared reciprocal-complementarity criterion failed. Learning the curve from raw observations performed almost identically in deployed prediction. |
| Can an acquired distinction be removed selectively? | Experiment 008 acquired two forms, collapsed to one when consequences became equivalent, and kept two in the unchanged world, in all five seeds. | Deterministic, balanced evidence with a fixed recent-data window; rare differences and noisy equivalence were not tested. |
| Can a collapsed distinction be learned again? | Experiment 009 passed acquire → collapse → reacquire in one uninterrupted learner, in all five seeds, with changes between reviews. | The merged learner incurred higher temporary prediction loss when the distinction returned; both variants recovered by the same review. No retrieval or faster-relearning claim. |

The two earlier math studies and the structural studies use different
implementations. They share a research question and variation/selection/retention
framing; these results must not be combined into a claim that one integrated
architecture has demonstrated every capability.

The acquisition and collapse studies do show structural changes within running
learners. In Experiment 008, acquisition followed by removal was one continuous
trajectory, not two separately constructed endpoint models. The disabled-merge
control learned identical responses for its two categories without removing
their structural separation. Prediction equivalence and category collapse are
therefore different measurable outcomes.

## Agreement and external evidence

In Experiment 006, the provisional and retained models agreed at probability
one half before the first useful split. A scheduled structural search still
found a predictive distinction. Internal disagreement can diagnose tension,
but agreement does not establish adequacy and cannot be the only route to
considering new distinctions. External action/outcome evidence supplies the
test of usefulness in these experiments.

Selection examples are separate from fitting examples, but come from the same
constructed process. Held-out combinations test reuse within that process, not
transfer to arbitrary worlds. Five seeds vary presentation order and feature
encoding, not five task families; the feature shuffles cover only two distinct
permutations. Identical final scores can follow mechanically from balanced
sufficient statistics.

## Reversibility completes this bounded stage

The [reversibility experiment](reversibility-v1/findings.md) used an uninterrupted
acquire → collapse → reacquire trajectory, with changes between review points
and no learner modification. All five seeds passed. The learner first acquired
two forms, collapsed to one at review 192, and split again at review 240. At
that point its prediction accuracy was only 50%; full acquisition criteria
were restored at review 288. Structure recovery and predictive recovery are
distinct observations.

The no-merge control recovered by the same review. During the first 48 main
observations after the distinction returned, the merged learner's mean log loss
was 0.594797 versus 0.512499, approximately 16% higher. Simplification helped
confidence in the equivalent-consequences phase but imposed an adaptation cost
on return. Full-run log loss favoured the no-merge control for this schedule.
The final-loss preservation criterion passed; it did not demand equal
transition performance.

This supports **learning and reversibly revising useful distinctions within a
constructed representational language**. It does not establish saved-form
retrieval, faster relearning, or meta-learning. Six synthetic tests and an
independent trace audit passed; the fixed run used 4,480 outcome-bearing
presentations, without tuning or rerunning the benchmark.

## Open questions and stopping boundary

Rare but consequential differences, temporary convergence, noisy equivalence,
retention under interference, autonomous investigation, steerability, learned
hierarchies, and learning-rule adaptation remain open. The failed complementarity
criterion also remains unresolved. None is automatically included in this stage.

The aspiration remains **can learn; can be interpreted; can be steered**. So far
we have evidence of bounded learning and inspectable rules. Readability does not
by itself establish effective steering, and none of these results supports a
claim about consciousness or safer real-world deployment. The registered
reversibility run is complete. This stage now pauses for interpretation and
writing, with no automatic scaling or next experiment.

## Source findings

- [Round 2: retention and consolidation](round2-v1/findings.md)
- [Experiment 006: form acquisition](forms-v1/findings.md)
- [Experiment 007: complementary roles](complementary-roles-v1/findings.md)
- [Experiment 008: selective collapse](collapse-v1/findings.md)
- [Experiment 009: structural reversibility](reversibility-v1/findings.md)
