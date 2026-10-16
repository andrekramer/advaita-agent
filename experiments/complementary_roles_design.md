# Experiment 007 design: situated recognition and retained relationships

Status: design implemented and tested, 2026-10-15. The
[fixed execution protocol](complementary_roles_protocol.md) resolves the choices
recorded below. [Results and independent verification](../results/complementary-roles-v1/findings.md)
are complete: learning the smooth relationship succeeded, but the declared
reciprocal-complementarity criterion failed. The design below is preserved as
the proposal preceding that run; proposed settings are not claims of validation.

## The question changes

Can two interacting processes compensate for each other's limitations?

Experiment 006 compared two arrangements learning the same grouping. Here the
roles differ. A situated process estimates what is happening here and now. A
retained process learns reusable action-consequence relationships. They encounter
one world, and each can improve the conditions under which the other works.

This is closer to the idea of complementary computing in Grossberg's
[The Complementary Brain](https://sites.bu.edu/steveg/files/2016/06/Gro2000TICS.pdf):
specialised processes have complementary limitations, and their interactions
can overcome those limitations. Our allocation of what/where to a fast role
and how/why to a slower role is a proposed engineering arrangement. It is not
Grossberg's demonstrated fast/slow division, a reproduction of ART, or a claim
about anatomical streams. His examples include distinct What and Where streams;
we are deliberately using different operational roles.

The unit under investigation is the interacting learner. Single-process and
disconnected controls help explain its behaviour, but outperforming a flat
learner is not the definition of complementarity. A flat learner could implement
similar interactions internally. Conversely, merely outperforming either weak
component in isolation would not establish that reciprocal interaction helped.

## One small world with no category boundaries

A probe moves along a continuous one-dimensional track. The response to an
action varies smoothly with position. There are no supplied classes such as
sticky/slippery, no region IDs, and no hidden switch between types.

Let x_t be position, a_t in {-1,+1} a scheduled action, and h=0.2. The simulator is

\[
g(x)=0.55+0.25\sin x+0.10\cos(2x),
\qquad
x_{t+1}=x_t+h\,g(x_t)a_t+\epsilon_t.
\]

Here epsilon is independent Gaussian process noise with standard deviation
0.002. Position is unwrapped: the track has no wrap discontinuity or boundary;
only the response field is periodic. The response gain remains positive.

The learner receives two fallible measurements:

\[
o_t=x_t+\eta_t,\qquad
r_t=(x_{t+1}-x_t)+\zeta_t.
\]

The first is a position sensor, available before action. The second is a motion
sensor, available only after action. Both are observable measurements, not
latent-state labels. Use independent zero-mean Gaussian noise: position standard
deviation 0.01 or 0.12, and motion standard deviation 0.005 or 0.04. Noise regimes
are known to the evaluator but not supplied as learner labels.

Only the harness knows x, g, and process noise. All learners receive the same
o, a, and r streams. Actions are externally scheduled so differences in learning
do not produce different evidence. Autonomous exploration and navigation toward
a goal remain later questions.

This world has a designed state space and dynamics. "No category boundaries"
means the experiment does not install categorical ground truth for the learner
to recover. It does not mean the simulator is free of assumptions or variables.

## Complementary roles and a minimal implementation

### Situated process: what is happening, and where?

The fast role keeps a current position estimate xhat and a temporary local
gain correction d. Its prediction combines a retained expectation with that
correction; current sensory evidence can correct its position estimate.

A deliberately simple candidate observer is

\[
\widehat x_t=x^-_t+\alpha(o_t-x^-_t),\qquad \alpha=0.5,
\]

\[
\widehat r_t=h\,\operatorname{clip}(b_t+d_t,0.1,1.0)a_t,
\qquad x^-_{t+1}=\widehat x_t+\widehat r_t.
\]

When predictive feedback is connected, b_t=ghat_theta(xhat_t). When that path
is cut, b_t=0.55, the same initial neutral gain for every learner. Initialise
xhat_0=o_0 and d_0=0 at each episode. These are observable initialisation and a
neutral prior, not true position or the simulator's gain field.

After receiving r_t, update the local correction:

\[
d_{t+1}=\operatorname{clip}\left(
0.8d_t+0.2\left(\frac{a_t r_t}{h}-b_t\right),-0.4,0.4\right).
\]

This is actual fast adaptation of a temporary response parameter, separate from
the inference of current position. It can follow local changes but has no map
for recognising a relationship on a later visit. It resets between episodes.
Both processes still receive observable feedback; neither owns exclusive
access to a sensor or action channel.

### Retained process: how does action produce an effect here?

The slow role retains a smooth response relationship across episodes:

\[
\widehat g_\theta(x)=\operatorname{clip}\bigl(\theta^\top\phi(x),0.1,1.0\bigr),
\quad \phi(x)=(1,\sin x,\cos x,\sin2x,\cos2x).
\]

Initialise theta=(0.55,0,0,0,0). The basis is supplied; coefficients and the
response curve are learned. This is the operational form in this first test:
a relationship reusable across positions and episodes. No category count is
rewarded, and a continuous relationship is an acceptable outcome.

When state teaching is connected, store each pre-outcome estimate xhat_t with
its action and subsequently observed r_t. When cut, store raw o_t instead.
Thus both conditions use the same sensors, action records, and number of
examples. They differ in whether the fast process improves the context in which
the slow process learns. Never revise a stored context using its own target r_t
or a later observation: otherwise a candidate could partly explain data that
were already used to construct its supposed input.

Use at most 480 main training records. At a review, propose a regularised
least-squares coefficient fit on their saved contexts z_t:

\[
\theta_* = \arg\min_\theta
\frac1{|B|}\sum_{t\in B}
\bigl[r_t-h a_t\theta^\top\phi(z_t)\bigr]^2
+10^{-4}\|\theta-\theta_0\|_2^2.
\]

The fit has a unique solution because of the ridge term. Clip coefficients to
[-1,1] afterwards and evaluate the actual clipped-gain predictor, not its
unclipped fitting surrogate. Propose once after every five main episodes. No
target from the subsequent selection episode fits this candidate.

On that selection episode, the current deployed loop runs unchanged. For each
pre-outcome context z_t, record both incumbent and candidate motion predictions
before revealing r_t. Accept only if the candidate's mean squared prediction
error is at least 1% below the incumbent's, with absolute improvement >1e-6.
The contextual inputs to this comparison are identical and recorded before
feedback. This tests the retained response relationship conditionally; the
separate evaluation episodes test the entire coupled loop.

Promote only between episodes, when the fast state and local correction reset.
There is then no silent mid-episode double counting of a new retained gain and
an old local correction. The next episode uses the new retained relationship.
No fitted curve is assumed correct merely because it was selected.

"Why" has a restricted operational meaning here: predicting action effects
conditional on circumstances. This is not an account of purpose, nor discovery
of arbitrary causal structure from observational correlations. Controlled action
pulses are supplied by the harness; learner-directed interventions come later.

## What travels in each direction

**Fast to slow, state teaching:** experience is associated with an estimated
current context, rather than an unprocessed noisy position reading. The
hypothesis is that this improves the reusable response curve.

**Slow to fast, predictive feedback:** a learned response expectation helps
carry the current position estimate between uncertain observations. The
hypothesis is that this improves situated tracking.

Both connections can also be harmful. A mistaken expectation can pull perception
away from evidence; a mistaken state estimate can teach an incorrect relationship.
The desired result is not greater agreement between the processes. It is better
prediction of observable consequences and more accurate state estimation against
evaluator-only ground truth.

Review opportunities are scheduled even when the processes agree. Experiment
006 showed why: agreement can coexist with a missing distinction. Do not use
the old fast/slow response distance as a mandatory gate for this experiment.
The two roles have different outputs; compare them only through a shared
prediction of motion, never by subtracting a position from a gain function.

## Interventions that test complementarity

Train four matched conditions from scratch, using a two-by-two intervention:

| State teaching | Predictive feedback | Meaning |
| --- | --- | --- |
| On | On | Complete proposed loop |
| On | Off | Situated estimates still teach the curve; learned curve does not guide the observer |
| Off | On | Curve is learned from raw contexts; it still guides the observer |
| Off | Off | Both selected paths cut; both processes and sensor streams remain present |

These are cuts to specified paths, not removal of all communication. In
particular, the local residual uses its baseline gain when feedback is enabled.
The top-down-off condition still has a constant-gain prediction and a fast local
correction; it is not forced to stop predicting or tracking. All conditions keep
the same curve capacity, fitting records, review schedule and selection budget.

Two additional controls make the interpretation less dependent on our chosen
partition:

- **Joint online learner:** the same observer, five curve coefficients, local
  correction, observations and record cap, but curve weights update continuously
  from pre-outcome state estimates using a fixed normalised gradient step.
  Use step 0.05 on the same regularised squared-error objective, dividing the
  sample gradient by 1+||h a phi||^2 and clipping coefficients to [-1,1]. It
  learns directly from selection observations as well, like earlier baseline
  comparisons. Record that difference in feedback use. This is a conventional
  comparison, not an oracle or a claim to exhaust possible single learners.
- **Misaligned-feedback control:** train the complete loop normally, but during
  final evaluation query its retained curve at xhat+pi in the observer only.
  Keep sensory evidence, local adaptation, parameters, and number of messages
  the same. The intervention tests the meaning of feedback, not simply the
  presence of another channel. It is deliberately incorrect feedback; failure
  here alone cannot establish complementarity. It does not alter training or
  selection and must not contaminate the primary factorial comparison.

The four primary conditions test the directional contributions. The online
control asks whether a simpler scheduling/retention arrangement can achieve
similar behaviour. An equal result would not erase demonstrated directional
contributions, but would limit claims for the proposed architectural division.

## Measurements and candidate decision rules

Use fresh final episodes with retained parameters frozen. Fast state estimation
and local adaptation remain active and causal within each episode; reset both
between episodes. No evaluation observation enters retained fitting or selection.
This is frozen retained knowledge, not a frozen whole system.

Cross two position-noise levels with two motion-noise levels. The high-position-
noise condition challenges recognition; the high-motion-noise condition
challenges learning and local adaptation. Train with all four regimes, without
regime labels; evaluate the four strata separately and together.

Measure:

1. Position mean squared error, scored against hidden simulator x only by the
   evaluator. It never supplies a training gradient or acceptance decision.
2. Pre-outcome motion prediction error against the observed r, for the complete
   loop and the retained curve alone. Report the two predictions separately.
3. Retained-curve error against g at 32 fixed evaluator-only positions, including
   between training start locations. This tests the learned relationship, not
   whether the designer's preferred categories appeared. Also plot both curves.
4. Accepted/rejected proposals, local corrections, clipping, computation, and
   errors by position and sensor regime. Include failures and feedback-induced
   drift, not only averaged improvements.

Proposed complementarity criterion, to fix before running:

- In noisy-position evaluation episodes, the complete loop reduces position
  error by at least 10% relative to the no-predictive-feedback condition.
- Its retained-curve error is at least 10% below the no-state-teaching condition.
- In episodes where both sensors are noisy, its motion prediction error is at
  least 10% below each one-path-cut condition.
- Each directional condition holds in at least four of five paired seeds and
  in the pooled mean. On clean-sensor episodes, its mean motion error is no more
  than 5% above the both-paths-cut condition. Report every seed regardless.

These thresholds are engineering criteria, not statistical significance tests.
If effects are smaller or mixed, report partial evidence or failure. Do not
substitute good performance against the misaligned control for a missing
directional result. Break down retention-fit error and deployed prediction error
so a local correction cannot conceal a poor retained relationship.

For a common loss L, also report the factorial interaction

\[
I=L_{10}+L_{01}-L_{11}-L_{00},
\]

where the subscripts denote the two enabled paths. Positive I means the joint
loss reduction exceeds the sum of the separate reductions on that scale.
Report it descriptively; complementary contributions need not be superadditive.
Do not make success depend on a particular architecture winning every metric.

## Scope, allocation, and implementation checks

Proposed fixed budget: five seeds, six conditions, and per condition 20 main
episodes, four interleaved selection episodes, and eight final evaluation
episodes, each with 24 transitions. Total: 5*6*32*24 = **23,040 transitions**.
This is a new declared budget, not a continuation inside Experiment 006's cap.
Every transition has one scheduled action and one newly revealed motion outcome;
position measurements, evaluator-only states, curve queries, and computational
replays must be counted separately. Curve checks add no learner feedback.

Main episodes contain five examples of each of the four sensor regimes; each
selection block of five main episodes is followed by one selection episode.
The four selection episodes cover all sensor regimes once. Final evaluation has
two episodes per regime. Stratify initial positions over one period; interleave
evaluation starts between training start points. This provides fresh starts,
not strictly withheld geographical regions: trajectories may cross them.

Within each episode, shuffle two consecutive balanced blocks of 12 actions
(six positive and six negative per block). Pair action sequences, initial
positions, process noise, and observations across all conditions within seed.
Noise-stream seeds, regime order, selection ordering, exact start grids, and
the joint baseline's treatment of the ridge gradient must be fixed in the
execution protocol before any benchmark observations are generated.

Before execution verify chronology, the local adaptation update, observer
initialisation, identical evidence across conditions, the ridge solution,
selection isolation, no hidden-state access, independent episode resets, and
unchanged retained parameters during final evaluation. Audit both path cuts so
neither silently receives its excluded signal. Candidate fitting must use saved
causal context estimates, not retrospectively recomputed estimates with later
knowledge. Keep an independent replay audit of full traces and source hashes.

This first design tests complementarity in learning and using a smooth form.
It deliberately does not add changing environments, learned category boundaries,
phase oscillations, active exploration, or higher-order rule evolution at once.
If the interaction works, a separate experiment can make the field change and
ask whether a useful form can be reopened or replaced. If it fails, inspect the
directional results before expanding the architecture or changing the task.

All actions remain inside the simulator. No execution, scaling, or automatic
follow-on run is implied by this design document.
