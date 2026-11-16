# Strength inspection and bounded steering — frozen protocol

2026-11-13. Follow-up to the two Heaviside comparisons. This round tests whether
prediction-specific fast/slow evidence helps forecast and select existing
controls. It does not test a new learning rule or geometric superiority.

## Separate the claims

1. Mechanical interpretability: can an external, read-only description forecast
   a next observation's effect, including elapsed-time decay and fixed priors?
2. Information usefulness: do per-prediction bank counts improve a supplied
   controller over ordinary inspection (row totals plus channel-wide bank mass)?
3. Presentation comprehension: do humans or a fixed AI evaluator perform better
   with direction/strength language than equivalent counts? **Not measured by
   scripted parity.** Export blinded tasks, with answers in a separate file.
   A later reader study needs its own evaluator and assignment protocol.

## Fixed learner and controls

Use schema-38 ControlledLearner, combined memory, shadow recall. Native learning,
coherent reviews, automatic weakening and migrations remain unchanged. Available
commands: no intervention or slow half-life 1024→128 in exactly one channel 0/1/2.
No locks, new one-shot weakening command, probability edits or new retention rule.
Apply immediately after review640; release after review896. Continue to1152.
Release restores rates, not forgotten evidence. Observe/review timing is unchanged.

Twelve fresh environment seeds3100–3111, three existing supplied task histories
(stable, repeated polarity change, changed forms), two acquisition/proposal seeds
3100 and3101. Use the frozen selective_steering.generate including its transient
protected-channel corruption513–640. The twelve seeds are the inference clusters;
histories/proposals/branches sharing a seed are not independent samples.
For proposal3100 target the affected local output; for3101 target the composite.
The other local channel is the supplied protected output. Controllers receive
these instructions, not the simulator's forms, branch, seed or future data.
The deterministic pairing confounds target type with proposal seed; report target
strata descriptively and do not infer a causal difference between target types.

Acquisition is freshly learned for each case. Process the first640 main rows and
reviews64 apart. Freeze a decision at640 regardless of apparent opportunity.
All four command continuations use the same remaining observations/review labels.
There are72 acquired trunks and288 continuations of512 observations. No tuning.

## Inspection conditions and evaluator

All views have current partitions/interface addresses, current prediction tables,
channel-wide fast/slow masses, supplied instruction, half-lives, and the preceding
64 ordinary observations aggregated into current prediction cells. Recent data
are reused training evidence, not an independent validation set. Review diagnostic
losses are available to the simple disagreement control. No future labels enter.

- `existing`: native row successes/total plus channel-wide fast/slow totals.
  For forecasting only, allocate each row proportionally to the channel totals;
  this is an explicit approximation, not information exposed by the learner.
- `raw_banks`: additionally expose row-specific fast/slow successes and totals
  through a read-only checkpoint adapter. This is new inspection information.
- `direction_strength`: exactly the same information as raw_banks, encoded as
  each bank's success fraction and retained mass. Empty mass has null direction.
- `prediction_only`: persistence forecast for the mechanical probe; a diagnostic
  lower-information baseline, not a competent alternative model of the dynamics.

The scripted evaluator is supplied mathematics, not an LLM, a human, or learned
introspection. Raw_banks and direction_strength must give equivalent forecasts
and control choices. This is a correctness control, not presentation superiority.
No unverified uncertainty/confidence interpretation is attached to retained mass.

At fixed representations, forecast a next observation by decaying fast evidence
by2^(-1/64), slow by2^(-1/h), keeping each row's unit success/failure priors fixed,
then adding the incoming label once to fast evidence. Test all32 contexts under
each of the4 commands. Labels for these synthetic probes oppose each current
channel prediction. Both pre-label emitted and post-label diagnostic forecasts
are checked on separate clones; probes never train the experimental trajectories.
Group labels may reorder, but membership and grouped raw evidence remain the same
between reviews. Forecasts are conditional on the specified input/label and do
not claim to infer which outcome will occur.

For future control effects use a frozen-representation, 64-step mean-evidence
approximation. Each cell's visit rate is its frequency in the last64 observations;
its outcome rate is (recent successes+1)/(recent count+2). On each projected step,
decay both banks, score expected Brier under that estimated rate, then add expected
visit mass/outcomes to fast memory. Do not simulate structural reviews/migration or
future random paths. This plug-in approximation can fail even with exact state.
The controller forecasts all4 commands, chooses minimum projected target loss
with protected-output increase<=.001, and acts only for predicted gain>.0005.
Ties within1e-12 prefer no-op, then channel order. The same function and thresholds
apply to existing/raw/named views. All decisions are saved and hashed before any
future branch is executed.

Controls: always no-op; disagreement (plasticity in the instructed target only
if the current review's fast loss<=.55 and slow-minus-fast loss>.05); rotated
control (rotate the raw-bank chosen channel, or abstain if it abstains). No control
receives the actual future or may choose intervention timing from outcomes.

## Outcomes and criteria

Mechanical: raw/named maximum probability error<=1e-10 against actual native clone
probes; forecast equivalence<=1e-12, identical commands, unchanged inspection state
and exact checkpoint round trips. Compare per-case mean probe error with existing
and persistence descriptions. These are contract tests, not empirical advantages.

Future forecasting: for each non-noop command estimate its64-observation target
Brier gain over no-op. Score mean absolute effect error and direction (improves
if gain>.001, harms if<-.001, otherwise negligible). Primary information benefit
requires bank-minus-existing effect-error bootstrap upper bound<0. Report accuracy
and non-negligible-effect coverage; require at least24 such cases for an effect
direction claim and bank accuracy>=.75. Report all cases, not only chosen commands.

Steering: actual observed target Brier over641–896 (256 active observations).
Primary bank-vs-existing improvement: mean gain>=.001, paired bootstrap lower>0,
positive environment means in at least8/12 environments. Also require bank-vs-noop
gain lower>=-.001 and no-op preservation guards: mean cost<=.01 and individual
case cost<=.05 for every output in897–1024 (released, world still changed) and
1025–1152 (return), protected output641–896, and every output during stable641–896.
Report disagreement/rotated comparisons, action rates, unnecessary actions
(chosen command gain<=.001), missed opportunities, and regret to the best of four
actually tested commands. The latter is an evaluator-only hindsight diagnostic.
No future-aware choice enters learning. These are supplied task objectives, not
new endogenous values or goals in the learner.

Use5000 paired cluster bootstrap samples with RNG417,12 seed draws per sample,
95% linear-interpolated percentile intervals. Average histories/proposals within
environment first. No threshold or parameter changes after outcomes. Display
stable/forms/repeated and target-type breakdowns as descriptive results.

## Verification, accounting and stop

Before fresh data: deterministic fixtures for detached views, exact counts↔named
round trips (including empty banks), contradictory bank allocation, fixed priors,
clock alignment, command equivalence, restore/release and independent reference.
Preserve numbered attempts. Freeze source/parent hashes before confirmation.
Independent audit reconstructs worlds, acquisition, native predictions, reviews,
learning state, packet quantities, commands and measurements. Use earlier independent
reference implementations; do not claim independent verification of wrapper ledger
metadata beyond exact runtime round trips. Verify synthetic clone probes separately.
Record allocated/generated labels, reused controller data, branch presentations,
probe labels, forecast arithmetic and runtime. Both runner/auditor capped at900s.
All three outputs' labels count. World generator materializes2048 main rows although
only1–1152 are used here; distinguish generated evidence from used evidence.

Stop after audit/report and export of reader tasks. Preserve failed results. No
architecture promotion, human comprehension, general steerability, safety or
meta-learning claim follows automatically. Reader tasks remain unscored until a
separately fixed evaluator submits answers.
