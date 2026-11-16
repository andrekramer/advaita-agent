# Heaviside side quest, Stage 1 — fixed-row prediction comparison

Frozen design before development, 2026-11-13. This is an isolated numerical
prediction study following [the review](heaviside_review.md), not a native-agent
benchmark or an architecture change. No structural search, selective weakening,
archive recall, additional selection labels or latent change indicators enter
these predictors. Row and emitted output are the same isolated binary readout.

## Arms and timing

All probabilities are logged before revealing the outcome, followed by one
update. Diagnostic reads have no side effects. Each prefix event also updates
exactly once. Discount occurs once per observation, never on inspection.

- `vector`: c' = rho*c + (y,1-y), including discount of initial unit tallies.
- `scalar`: exact (p,S) twin at the selected vector rho.
- `full`: vector with rho=1, diagnostic only.
- `fixed`: p' = p+g(y-p), development-selected g.
- `matched`: same rule with g=1-selected vector rho.
- `rotor`: theta' = theta+eta*sqrt(p(1-p))*sin(phi-theta), with
  p=cos(theta)/(cos(theta)+sin(theta)), phi=0 for y=1 else pi/2.
- `prior_matched`: discounted *raw* success/failure counts with fixed unit priors,
  at vector-selected rho. Forecast (rho*u+1)/(rho*(u+v)+2), then update raw counts.
- `prior_selected`: same fixed-prior rule with independently selected rho.
- `window`: last 192 observations, fixed unit priors, refit each observation.

The last three arms run only in suite B. They are explicitly numerical controls,
not the original structural or combined-memory learner. Their prior and update
timing follow the native count semantics identified in the review. A window
cannot represent the imposed 1000-observation support in A. The A mechanism test
uses the first six arms without imposing an artificial prior/window history.

For vector and scalar, uniform pre-label decay leaves the forecast unchanged.
For fixed priors it can change the forecast; the formula above accounts for this
without making repeated prediction calls mutate state. Trace fields distinguish
stored mass from effective mass at prediction and post-label probability.

## Worlds and initialization

Use Python random.Random with independent seed streams: prefix RNG seeds
100000+seed (short), 200000+seed (long); stable 300000+seed; reversal400000+seed.
Short prefix is a shuffled eight ones/two zeros; long prefix800/200. Generate
128 stable outcomes at probability .8 and 128 reversal outcomes at .2. Streak
copies stable but replaces its first four outcomes with zero. Share each future
across both histories and every arm. Odd seeds mirror initial probabilities,
all prefix/future labels and targets. Record the mirroring flag.

Suite A: impose vector/scalar/full tallies (8,2) or (800,200), mirrored as needed;
fixed/matched/rotor begin at the same .8 or .2 forecast. Prefix labels are not used.
Suite B: vector/scalar/full begin with (1,1); fixed/matched/rotor at .5; fixed-prior
arms have zero raw counts; window is empty. Replay the shared prefix, then clone
the resulting state for each future. Record actual initial odds and mass; no
equal-odds inference is made from B. Fixed-gain/rotor have no retained mass field.

## Development and freeze

Development seeds0–31 only, suite B only. Rho candidates [.90,.97,.99] for vector
and separately fixed-prior; g [.01,.03,.10]; eta [.02,.06,.20]. Select each family
by equal-weighted mean Brier loss across seeds, histories and three windows:
stable1–128, post-streak5–20, reversal1–64 (one-based inclusive). Ties use listed
order. Freeze selections and source/world hashes before creating confirmation
worlds. No other grid, threshold search, extra seeds or tuning after confirmation.
Scalar and matched gain inherit the vector's selected rho. Full/window are fixed.

Fresh confirmation seeds1000–1199; A has6 arms and B9. There are18,000
seed×suite×history×future×arm runs. No hidden development use of A or confirmation.
All source and frozen038 dependencies are checked before/after running.

## Metrics and decisions

For each run report primary-window and whole-future Brier loss, mean forecast,
mean generating probability, mean squared deviation from that probability,
first update, and retained mass/odds at the start. Streak's forced four losses
are separate. Its first four generating probabilities are the deterministic
intervention (0, or1 when mirrored); resumed probabilities revert to .8/.2.

Reversal recovery is the first pre-outcome forecast strictly on the new side of
.5 beginning four consecutive qualifying forecasts. Report observations already
seen (index0 for the first forecast). Unobserved recovery is censored; cap delay
at128 only for the capped-mean statistic, also report the censored fraction.

Primary inference uses **B only**. For each future, average candidate-minus-control
primary Brier differences equally across the two histories within each seed.
Use10,000 paired seed-bootstrap resamples with random.Random(77), drawing200
indices via randrange per resample. Share draws across all contrasts; 95%
percentile endpoints use linear interpolation at .025/.975. Preserve branches
within a seed. Report descriptive differences separately by history; A is
mechanism evidence and receives no primary significance claim.

Compare vector with window, selected fixed gain, matched gain, rotor, both
fixed-prior controls and full retention. The declared Stage1 trade-off gate
requires **both** window and selected-fixed comparisons to have an upper bound
<0 for post-streak loss and <+.01 for stable and reversal loss. Individual
contrasts and other controls remain visible even if the gate fails. Scalar/vector
forecasts must agree within absolute1e-12 on every step; any violation is an
implementation failure, not a finding. Improvement over a native agent is not
tested here. Prior-control results constrain any interpretation about strength.

## Verification, outputs and stopping

Before execution, deterministic tests cover equivalence, constant-gain limit,
symmetry, forecast read-only behaviour, window eviction, metric endpoints,
recovery censoring and decision-gate fixtures. An independent checker uses its
own prediction recurrences to reconstruct all development scores, selections,
confirmation forecasts, metrics and bootstrap summaries from materialized worlds.
It also reconstructs the seeded worlds and verifies source/artifact hashes.

Save manifest, development worlds/scores/selections, confirmation worlds, all
forecast trajectories, one metrics row per run, comparison intervals, a few
paired event traces with p/S/theta/delta-p, and mean-forecast plots. Plots undo
label mirroring before averaging. Preserve failures and do not overwrite outputs.
Runner and checker each have a900-second ceiling. Confirmation uses2,304,000
future forecasts; prefix presentations are also counted. Report generated labels
separately from repeated use across arms. Stop after the report; Stage2 native
integration requires its own timing/evidence-budget protocol and fresh seeds.
