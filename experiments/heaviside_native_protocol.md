# Heaviside Stage 2 — native continuing learners and a contextual output adapter

Frozen design, 2026-11-13, before generating the new worlds. Follow-up to
[Stage 1](../results/heaviside-prediction-v1/findings.md). No parameter tuning.

## Scope and hypotheses

Test the final emitted binary forecast for one supplied familiar input context,
while ordinary native representation, evidence and review operations continue.
This is a contextual output intervention, not a replacement of the whole learning
architecture. Native forms may change; the adapter address remains the supplied
raw context (0,0,action0). This additional addressing rule is explicit. There is
no claim of learned context selection, category transfer or broader competence.

Native backbones use `ContinuingLearner`: reference with the existing `delete`
variant to disable archive capture/recall, `relaxed` admission, and `combined`
admission plus selective weakening. Preserve their published algorithms, fixed
thresholds and native review ordering, including the original weighted runtime's
post-review inspection limitation. Score the probability actually returned by
observe; never substitute a separately refitted diagnostic. No plasticity boost,
extra lock, control command or reset of pending evidence is introduced.

Each native trajectory supplies six output alternatives: native, vector, scalar
twin, fixed gain, rolling-window and fixed-prior discounted counts. The five
adapter predictors are the frozen Stage1 implementations, rho=.9, g=.1, window192.
They override only the target's final composite probability. Local outputs and
all native learning are identical across these counterfactual output alternatives.
Exogenous observations/actions do not depend on output, allowing one physical
native replay to evaluate all six. Outside the supplied context the adapter
returns native output and does not update its target counts.

## Initial state and label semantics

Use the first saved037 acquisition checkpoint (seed2600, stable, proposal2600)
and its acquisition composition rows, verified against the parent artifacts.
The target input is (0,0,0), whose native group row is initially `1|0|0`, counts
27 successes/32 observations, p=28/34. All native engines clone the same acquired
state. Weighted engines initialize from their ordinary retained buffers; record
actual odds/masses rather than assert equal native starting strengths.

Vector/scalar start with (28,6); fixed starts at28/34; fixed-prior starts with
raw(27,5); window receives the32 acquisition composition outcomes belonging to
that initial row in original order. These are preexisting evidence, not fresh
labels. The different subsequent discounts remain the tested policies.

Odd seeds exchange external outcome names by a bijective input/output adapter:
native and contextual predictors receive the unmirrored y, and their emitted
composite probabilities are flipped back for external scoring. Local labels are
unchanged. This preserves exact mirrored initial forecasts without rewriting the
historical checkpoint or giving a predictor a change marker. The fixed raw context
and its two local labels come from the acquired local group meanings.

## Fresh worlds, reviews and evidence budgets

Forty independent outcome seeds3000–3039; one fixed acquired/proposal state.
Inference is over these40 outcome histories, not over learned architectures.
No development seeds. Short/long prefixes contain shuffled8/2 and800/200 outcomes.
Use RNG seeds600000+seed and700000+seed for prefix order. Stable future512 draws
uses800000+seed at .8; reversal uses900000+seed at .2. Streak shares stable after
forcing its first four labels to0. Mirror externally on odd seeds. Futures are
shared across both histories and all backbones/readouts.

Prefix reviews occur after every64 observations and at the end (10 or1000);
no duplicate review at a boundary. Selection batches contain32 independently
drawn target-context outcomes at .8, using RNG1000000+seed (short) and1100000+seed
(long). Future reviews occur after future observations64,128,...,512, regardless
of prefix length. Stable/streak share review batches at .8 using1200000+seed;
reversal batches use1300000+seed at .2. Every future clones the post-prefix state,
including native pending decisions. A boundary is a scoring branch, not a reset.

All alternatives are allocated the same main and review observations. Native
engines use main rows for fitting and review rows for their existing selection,
weakening and migration decisions. Adapter heads fit each main y once; they score
the review batch read-only and never fit or select on its outcomes. This is equal
available evidence, not identical evidence use. Native engines additionally use
the two supplied deterministic local labels. Log these differences and costs.

The runner executes240 prefixes and720 native futures; these yield4,320 output
run records. Main-row updates total489,840 across native backbones (121,200 prefix,
368,640 future); review rows total249,600 (65,280 prefix,184,320 future). Each row
contains three scalar labels. Adapter computation repeats five numerical updates
per target main row without creating new evidence. There are154,320 materialized
composite-label positions across40 worlds, counting duplicated stable/streak
storage; there are123,760 distinct constructed positions including the forced
outcomes. Publish actual generator and
reuse counts and verify them rather than treating presentations as independent.

## Primary and diagnostic metrics

Pre-outcome Brier loss. Primary windows: stable1–512, post-streak5–20,
reversal129–256. The latter follows two new review opportunities; it does not
guarantee qualifying weakening. Record each accepted weakening and its timing,
especially composite-channel changes. Preserve reversal1–64 as an early diagnostic,
and whole/later257–512 losses, forced-four losses and recovery censoring at512.
Recovery starts four consecutive predictions strictly on the new side of .5,
reported in observations already seen. Log row counts, native input meanings,
actual output sources, head strengths and checkpoint continuity.

Compute vector-minus-native differences, averaged equally across histories
within each seed, separately for reference, relaxed and combined. Also compare
vector with fixed/window/fixed-prior heads; these shared heads must give identical
outputs across backbones. Bootstrap10,000 paired seed samples using RNG177,
40 randrange draws per sample, shared across contrasts; linear-interpolated95%
percentile intervals. Show history-specific descriptive effects.

Native improvement requires post-streak upper bounds<0 and stable/late-reversal
upper bounds<+.01 against **both reference and combined**. Attribution to the
mass-dependent update additionally requires the same criterion versus fixed gain.
No gate is changed after outcomes. Report combined-minus-relaxed to identify
whether selective weakening actually helps in these worlds. Scalar/vector maximum
forecast difference must be<=1e-12, otherwise implementation failure.

## Verification and stop

Deterministic preflight checks: adapter output routing and off-target fallback;
exact active-state parity with a plain native learner; prefix cloning and midway
checkpoint continuation; observation/review separation and no hidden head updates;
pre-label count reconstruction; metric boundaries and rejection of a failing gate.
No confirmation seeds are used in fixtures.

An auditor reconstructs native forecasts/reviews/final learning state using the
existing independent structural and memory references, and independently computes
adapter forecasts, metrics and bootstrap intervals. Checkpoints/metadata receive
exact runtime round-trip checks; independent model-state checks use1e-9 tolerance
consistent with existing reference auditors. Explicitly distinguish these scopes.

Freeze source, parent and initial-state hashes. Save complete forecasts, native
reviews, prefix and final checkpoints, per-output metrics, effect intervals and
plots. Preserve failed attempts; no overwrite or empirical restart. Runner and
auditor each have a900-second ceiling. Stop after reporting; no architecture
promotion, new tuning grid or follow-up benchmark is automatic.
