# Review: direction, retained strength and prediction revision

2026-11-13. Side quest based on [the supplied handoff](../advaita-heaviside.md).
Reviewed against commit `51415c6480ef7d73fdd896e0ad34be6fbe5f4a92`.

**Recommendation: test it, in two stages.** The mathematical mechanism is sound
and the proposed controls are useful. It can test whether an evidence-dependent
gain improves a particular prediction trade-off. It cannot distinguish an
advantage of vector coordinates from the exactly equivalent scalar rule, and
the current learner already retains evidence strength. A fair native comparison
needs explicit decisions about update timing, priors and structural reviews.

Six deterministic feasibility checks passed on the first attempt. No development
or confirmation seeds have been generated or inspected. This review leaves the
handoff, current architecture and frozen experiment artifacts unchanged.

## What the mathematics establishes

For positive total mass, the vector update and scalar update are exactly the same:

\[
S_{t+1}=\rho S_t+1,\qquad
p_{t+1}-p_t=\frac{y_t-p_t}{\rho S_t+1}.
\]

The useful decomposition is **prediction direction plus retained strength**.
At fixed odds and outcome, greater retained mass produces a smaller revision.
Strength is an extra state variable compared with a direction-only predictor,
but it is not an extra variable compared with an ordinary two-count predictor.

The exact angular equation in the handoff is correct for the stated nonnegative
evidence vectors. The large-radius approximation makes the sine dependence
visible. The fixed-target substitution also follows directly:

\[
\frac{d}{dt}\tan(\delta/2)
=\tfrac12\sec^2(\delta/2)(-k\sin\delta)
=-k\tan(\delta/2).
\]

This continuous coordinate identity does not equate all discrete rotor, instar
and native learning rules. Their update schedules, priors and retained state
still matter. The labels in the handoff are mathematical interpretations here;
this review does not establish historical attribution or validate the complete
R-rule dynamics.

For fixed discount, mass evolves independently of the observed outcome values:

\[
S_t=\rho^t S_0+\frac{1-\rho^t}{1-\rho}
\quad(\rho<1).
\]

Consequently, this is a history-dependent gain schedule, not a learned judgement
of evidence quality. At stationary mass it is exactly constant gain. In these
experiments, call S retained evidence mass or update inertia; treating it as a
calibrated uncertainty estimate would require further assumptions about the data
and its dependence. The scalar twin and matched fixed-gain controls are essential.

## Relationship to the current learner

The existing [count table](../advaita/models.py) stores successes n1 and total
observations n, predicting `(n1 + 1)/(n + 2)`. Its equivalent evidence vector is
`(n1 + 1, n - n1 + 1)`, including the two fixed unit priors. It already distinguishes
identical odds supported by different counts. Substituting native counts into
the handoff's short/long deterministic example produces exactly 6/11 and
501/1001 after an A outcome, with the symmetric B results.

The [weighted learner](../advaita/memory_control.py) retains fast and slow evidence
separately. Their sum determines a current table, but their allocation determines
future decay. Two states with the same odds and total mass can respond differently
because one holds its evidence in fast memory and the other in slow memory. The
feasibility checks demonstrate this counterexample. One `(p,S)` pair therefore
does not encode the complete current fast/slow system.

This makes the proposed comparison worthwhile as a possible simplification or
alternative retention rule. It does not introduce retained strength into a
learner that previously lacked it. The question becomes: **does this simpler,
explicit mass-dependent update improve the chosen prediction trade-off relative
to our existing retention and revision policies?**

## Comparison issues to resolve before confirmation

| Issue | Consequence | Recommended treatment |
| --- | --- | --- |
| Reference update timing | A coarse `StructuralLearner.step` stores a new upper observation without refitting its upper table. Raw-port tables refit on each step; coarse tables change through review decisions. | Keep the literal native arm, but also include a clearly labelled per-observation rolling-window count control. Do not attribute a win over an unreviewed coarse table to missing strength. |
| Selective weakening timing | Native corroboration requires qualifying reviews 64 ticks apart. Starting without a qualifying pending decision, reviews at future observations 64 and 128 cannot make weakening affect the declared 1–64 reversal window. | Keep the 128-event micro-test separate. Use a longer native comparison with a post-intervention window and the original review semantics. |
| Fixed versus decaying priors | Native unit priors remain fixed when evidence decays. The handoff discounts both initial tally components, including its initial `(1,1)`. | Report both conventions and add a fixed-prior discounted-count control. The supplied scalar twin must still reproduce the supplied vector exactly. |
| Prediction clock | Weighted native `observe` decays/refits before predicting, then incorporates the label. A diagnostic prediction just before that call can differ. | Score the probability returned by the native observation entry point; expose equivalent pre-label timing in adapters. Log diagnostic queries separately. |
| Frozen category versus native review | A native review can revise forms and interfaces as well as weaken or migrate evidence. Local locks hold partitions, not group-label ordering; there is no supported upper-partition lock. | Treat a fixed-row adapter as a restricted numerical test. Preserve the full published mechanism in a separate native study; do not silently suppress its structural steps. |
| Review evidence budget | Native reviews use selection rows in addition to ordinary observations. | Declare that budget and its use for every arm before comparing outcomes. A candidate must not receive extra uncounted evidence or be described as equally trained when the budgets differ. |
| Initial support and retained support | Long prefixes can be truncated by the native 192-row window or discounted toward a finite mass. Their final odds need not match. | Keep A's imposed equal-odds states separate from B's prefix replay, and log actual retained support and odds. |

The native timing issue was verified through ordinary `ContinuingLearner.observe`
calls on a deliberately constructed common category fixture. After one B outcome,
the coarse reference stayed at .75, while the diagnostic raw-port configuration
changed from .75 to 9/13. That is a routing/update distinction, not an observed
predictive-performance result. Changing to a raw port must not be presented as
the unchanged reference configuration.

## Recommended experimental sequence

**Stage 0 — completed feasibility.** The supplied acceptance checks passed at the
declared tolerance. Native counts reproduced the support-sensitive revision;
additional probes established the prior, clock and two-bank distinctions above.
[Recorded checks and source hashes](../results/heaviside-feasibility-v1/attempt-01.json)
are reproducible with:

```sh
python3 checks/test_heaviside_feasibility.py
```

**Stage 1 — isolated prediction study.** Implement the vector, exact scalar twin,
direction-only rotor, selected fixed gain, vector-matched fixed gain and full
retention diagnostic. Add the native-style fixed-prior discounted-count control
and a 192-observation rolling-window control that refits on every observation.
Keep all controls labelled by their actual implementation.

Retain the handoff's imposed A states and shuffled B prefixes, paired futures,
label mirroring, Brier windows, censoring rule and finite development search.
The imposed long A state is an intentional intervention, not a state necessarily
reachable under the selected discount's equilibrium. Report A and B separately.
At this stage, B is a fixed-row numerical comparison, not yet a full agent result.

Select parameters using the declared B development objective only; use the A
suite for mechanism diagnostics rather than another opportunity to select a
favourable configuration. Keep development seeds 0–31 and confirmation seeds
1000–1199 disjoint. The vector's selected discount determines the scalar twin and
matched-gain arm. Choose the separate fixed-gain and rotor parameters on the same
development objective, with the handoff's tie order. Do not tune the native settings.

Materialise each future once per seed and share it across arms and support levels.
Mirror the labels, probabilities and initial states consistently. Score each
forecast before its outcome is incorporated. Show the forced streak separately;
label its deterministic outcome intervention distinctly from the resumed .8
generating process. Record recovery in observations already seen, censoring when
four qualifying predictions cannot be observed before the horizon.

Retain paired seed-bootstrap reporting and the strict post-streak improvement /
.01 stable-and-reversal tolerance as proposed. Report support levels separately
alongside the pooled result so a long-support failure is visible. Passing the
comparison against both a competent rolling-window control and the selected
fixed-gain arm would support a useful retention/gain policy in these tasks.
Vector/scalar equality remains a correctness check, never a performance claim.

**Stage 2 — native integration comparison.** After the fixed-row adapters pass
their contracts, freeze a separate protocol comparing the candidate with the
unchanged native reference and the published combined-memory policy. Reuse the
current continuing/controlled entry points, keep recall disabled, record actual
row identities and meanings, and verify that each recorded row prediction reaches
the emitted output. Preserve native reviews and account for all selection data.

Allow at least two qualifying reviews and a nonempty scored interval after the
second. A 256-event future with a separately declared post-review measure is a
reasonable starting design; its precise scoring window and budgets must be fixed
before generating confirmation data. Keep the original early window as a cost
diagnostic. Longer horizons do not guarantee that weakening will qualify.

If strict fixed mappings require bypassing native structural decisions, call that
an adapter ablation and report full-task native results separately, as the handoff
already allows. Do not relabel the adapter as the published algorithm. Any Stage 2
confirmation must use fresh seeds if Stage 1 results influenced its design; reserve
a separate range rather than reuse 1000–1199 as fresh confirmation twice.

## Claims and stopping point

We can already claim mathematical consistency and demonstrated history
sensitivity, including in the existing count tables. We cannot yet claim predictive
improvement. A successful next study could justify a simpler downstream update or
a better retention trade-off. It would not establish superiority of geometric
coordinates, the necessity of the full R-rule, general steerability or meta-learning.

The population-decoding idea should remain a later study. Explicit counters
verifying their own update law cannot establish that a neural population encodes
the same quantity. No network experiment, development sweep or fresh confirmation
has been started as part of this review.
