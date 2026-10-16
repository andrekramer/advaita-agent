# Experiment 007: fixed execution protocol

Fixed before execution, 2026-10-15. Implements
[the complementary-roles design](complementary_roles_design.md). One run per
condition and seed, seeds 0–4. No tuning, extra seed search, or follow-on run.
All equations, caps, noise levels, and criteria in the design apply; the details
below resolve its outstanding choices. This protocol takes precedence where a
clarification is needed. No model receives latent state, true gain, noise values,
noise-regime labels, or target information before its prediction.

## World, schedule, and random streams

The world's position is unwrapped and its response field is periodic:

g(x)=0.55+0.25 sin(x)+0.10 cos(2x),
x_next=x+0.2*g(x)*a+epsilon, o=x+eta, r=x_next-x+zeta.

The noise standard deviations are 0.002 for process noise, 0.01/0.12 for the
position sensor, and 0.005/0.04 for the motion sensor. The four regimes are
LL, LH, HL, HH, ordered by position then motion noise. Noise sources are
independent. Position and motion sensor samples are drawn on every transition,
including the first transition of an episode. Initial position is hidden.

For seed s, base=100000+10000*s. Use separate Python random.Random generators:
base+1 for schedule/layout, +2 for actions, +3 for process noise, +4 for position
noise, +5 for motion noise. Pair the entire generated world across conditions.
The layout RNG, in order, shuffles:

1. Main start indices 0–19; x0=2*pi*j/20.
2. Main regimes [LL,LH,HL,HH] repeated five times.
3. Selection start indices 0–3; x0=2*pi*(j+0.25)/4.
4. Selection regimes [LL,LH,HL,HH].
5. Evaluation indices [0,2,5,7,10,12,15,17]; x0=2*pi*(j+0.5)/20.
6. Evaluation regimes [LL,LH,HL,HH] repeated twice.

Execute five main episodes followed by one selection episode, four times, then
eight evaluation episodes. Each episode has 24 transitions; shuffle each of
two action blocks [-1]*6+[+1]*6 independently. Generate observations in episode
order, drawing epsilon, eta, zeta each transition from their respective RNGs.
Fresh evaluation starts do not imply wholly unvisited regions; trajectories
may cross those positions during training.

## Six conditions and chronology

`full`: both paths on. `no_feedback`: state teaching on, predictive feedback off.
`no_teaching`: teaching off, feedback on. `disconnected`: both paths off.
`online`: same observer, local correction and five curve weights, updated online.
`misaligned`: identical to full until evaluation; only the observer's retained
gain query then uses xhat+pi. All six start with theta0=(0.55,0,0,0,0).

For each episode reset x_prior to unavailable and d to zero; preserve theta and
the main-record buffer. On its first transition set xhat=o; otherwise set
xhat=x_prior+0.5*(o-x_prior). Before the target r is supplied:

- z=xhat when teaching is on; z=o when off. Online uses xhat.
- b=clip(theta dot phi(xhat),0.1,1) when feedback is on, except misaligned
  evaluation queries xhat+pi. When feedback is off b=0.55.
- Predict loop motion rhat=0.2*clip(b+d,0.1,1)*a.
- Also predict curve-only motion 0.2*ghat_theta(xhat)*a, without local correction
  or misalignment. This is diagnostic, not substituted for the deployed output.
- During selection, predict incumbent and candidate curve outputs at the same
  pre-outcome z, without local correction. Neither can change the running loop.
- Save the pre-outcome xhat, z, b, theta, d and predictions.

Then reveal r. Set x_prior_next=xhat+rhat using the saved prediction, not r.
Set d_next=clip(0.8*d+0.2*(a*r/0.2-b),-0.4,0.4) using the saved baseline b,
including for online. Thus current r influences local adaptation for later
steps but cannot change its own recorded prediction or context.

Only main records enter the fitting buffer: (z,a,r), maximum 480. Contexts are
never recomputed after learning. Store the same bounded main buffer for online
for accounting, though online does not replay it. Selection episodes adapt the
fast local state in every condition, but never enter the main buffer.

## Retained fitting and selection

phi(x)=(1,sin x,cos x,sin 2x,cos 2x), f=0.2*a*phi(z), lambda=1e-4.
After main episode 5,10,15,20 fit a single candidate before accessing the next
selection episode. Solve

(mean f f^T + lambda I)*theta_raw = mean f*r + lambda*theta0,

then clip each coefficient to [-1,1]. Save the raw solution, matrix, right-hand
side and clipped candidate. Count model calls and records used. Use all and only
the accumulated main observations. There is no hyperparameter search.

Run the entire selection episode under the incumbent. Record paired incumbent
and candidate curve predictions before each r. Let their 24-pair mean squared
errors be E0 and E1. Accept iff E1 <= 0.99*E0 AND E0-E1 > 1e-6.
Promotion happens only after the episode. Local state resets before the next
episode, avoiding a retained gain change combined with an old local correction.

For online there are no batch fits, candidates, or acceptance decisions. After
each main or selection observation, update

theta <- clip(theta - 0.05 * [2*f*(f dot theta-r)
                              +2*lambda*(theta-theta0)]/(1+f dot f), -1,1).

The whole sample gradient, including the ridge term, is normalised. It uses the
unclipped linear fitting objective, matching the batch fitting surrogate, not
the derivative through the clipped deployed predictor. State estimates are
treated as fixed inputs to this update; do not backpropagate through the observer.
The local correction update still uses pre-update b. No continuity compensation
for changing online weights is introduced. Its interaction with d is part of
this fixed baseline, not assumed optimal. Online sees the same 576 feedback
records but learns coefficients from all of them; batch conditions fit on 480
and select using 96. Report this role difference.

## Evaluation and metrics

After the fourth selection episode freeze theta in all conditions, including
online. Retain active causal inference and local d updates within the eight
test episodes. Reset local state each episode; evaluation adds no fitting
records and makes no selection decisions. Check theta and buffer bitwise
unchanged throughout evaluation.

At the end score the retained curve at x_j=2*pi*(j+0.5)/32, j=0..31. These
evaluator-only queries use hidden g solely to calculate error, never to train
or select. At the same points save the initial constant-curve error as context.
Save true and predicted values for plotting without any additional queries.

Calculate position MSE (xhat-x)^2, loop motion MSE (rhat-r)^2, and curve-only
motion MSE on evaluation, by regime and pooled. The latter is measured at xhat
for every condition. Include the first observation of every episode. Also
report position errors per position, per-episode errors, maximum absolute
position error, d, clip counts, candidate decisions, and model computation.
Regime labels and latent values are accessible only to generation and scoring.

For each seed compare full with:

1. `no_feedback`: full position MSE on HL+HH <=90% of the cut condition.
2. `no_teaching`: full 32-point retained-curve MSE <=90% of the cut condition.
3. Both one-path-cut conditions: full HH loop MSE <=90% of EACH cut condition.

Each of these three conditions must hold in at least four of five seeds AND
when comparing the corresponding pooled mean errors. For condition 3 the same
seed must pass both comparisons. Additionally pooled full LL loop MSE must be
<=105% of disconnected LL MSE. All requirements must hold for the declared
complementarity criterion. Report individual counts and the number of seeds
passing all three, without substituting a different criterion afterwards.
Use direct inequalities rather than ratios for decisions, avoiding division
by zero; report ratios only with their denominators.

For each seed and common evaluation loss report
I=L(no_feedback)+L(no_teaching)-L(full)-L(disconnected).
Apply this separately to pooled position, loop, curve-only, and retained-curve
MSE. Positive I is a superadditive loss reduction on that scale, not a required
condition for complementary contributions. Five seeds support descriptive
comparisons, not significance claims.

## Counts, verification and stopping

30 runs * (480 main +96 selection +192 evaluation) = 23,040 transitions and
new motion outcomes, with 23,040 position measurements. The five unique paired
world streams contain 3,840 transitions, each presented to six learners.
There are 960 final retained-curve evaluations and 960 initial-reference curve
evaluations, all evaluator-only. Stored latent states are diagnostics, not
additional learner supervision. Record gain calls, candidate fits, row replay,
parameter updates, selection scores, resets, and clipping separately.

Before running, test the ridge solution on synthetic fixtures, chronology,
both path cuts, local and online updates, candidate isolation, acceptance and
rejection, reset behaviour, and evaluation freezing. No benchmark pilot or
parameter adjustment based on test outcomes. Save this protocol and code hashes,
world streams, full learner traces, candidates, metrics and figures.

Independently audit saved records without importing learner code: regenerate
the world streams, reconstruct the causal updates, verify candidate normal
equations and clipping, validate data separation and path cuts, recompute metrics
and decisions, and check all budgets and hashes. Full and misaligned must have
identical histories before evaluation; no_feedback and disconnected must have
identical deployed trajectories, since neither uses its retained curve there.

Stop on invalid arithmetic, budget violations or failed audits. Correct genuine
implementation bugs transparently; never tune around disappointing outcomes.
No larger models, live actuation, changed-world tests or automatic next round.
