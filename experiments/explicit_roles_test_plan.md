# Next enquiry: explicit predictive and representational roles

Planning document, 2026-10-27. **Planned; not implemented or run.**
The 019–022 round remains closed. This plan tests the proposed architecture
before choosing a reference for steerability experiments. The current Substack
post describes the existing architecture; a subsequent post will report the
architecture decision and then the steering enquiry.

## Question and hypothesis

Does an explicit division of labour improve learning and revising
generalisations, compared with the current consolidated learner?

Write the prediction as

\[
p(y\mid x,a)=q_\theta(y\mid\phi(x),a).
\]

The situated role changes predictive parameters, theta, within a deployed
representation. The form role changes phi: groupings, exported meanings,
selected relationships and interfaces. Both remain answerable to external
outcomes. This is not a claim about consciousness or meta-learning; the rules
governing both roles remain supplied.

Two hypotheses must be distinguished:

1. Explicit ownership of representation changes improves stability without
   unacceptable delay or predictive cost.
2. The form role benefits from the situated learner's adaptation history,
   beyond the observations and outcomes already available to both.

Giving existing code two names cannot change its behavior. The experiment
must identify the functional changes that implement the proposed roles, and
separate their effects from update frequency and additional computation.

## Operational division of labour

The current local learner refits probabilities within its partition on each
observation. Its exported group IDs are ordered by those probabilities.
Consequently, count updates can change what an exported ID refers to even
without a partition change. Upper consumers can then face changed meanings.
The current upper predictor also refits continuously when it reads raw detail,
but a group-only table can remain fixed between accepted changes.

The explicit-role candidate will have the following contract:

- The situated role updates local and upper predictive tables on main evidence,
  including group-only upper tables. It cannot change partitions, input ports
  or exported group membership.
- The form role owns all representation changes and considers them at declared
  review boundaries. Between accepted changes, exported meanings stay fixed.
- On a grouping revision, align new group IDs with the previous memberships
  by maximum overlap, with a deterministic tie rule. Unchanged membership keeps
  its existing ID; probability ordering does not silently rename it.
- Every proposed representation is evaluated with compatible predictions
  fitted from permitted main evidence. A representation and its predictive
  state are installed together; old counts are never silently reinterpreted.
- Keep the existing lower-then-upper review order. This first comparison does
  not add a joint search over lower and upper structures or a new coordinated
  commit algorithm.

This is one operationalisation of explicit roles: stable representation
contracts plus separate responsibilities. A benefit would support this package,
not every possible two-learner architecture. Each role can operate across the
existing two local modules and upper module; it is not a change to nesting depth.

## Stage R0: contracts and equivalence — proposed record 023

Before new-world generation, produce a short implementation specification and
an independent replay model. First separate code responsibilities while
preserving the original behavior exactly. Require full saved-trace parity with
the 019 integrated reference, including proposals, probabilities, decisions,
exported meanings, costs and checkpoints. This refactor is an engineering gate,
not learning evidence.

Then add the candidate behavior behind explicit switches. Synthetic fixtures
must cover:

- A probability-order crossing with unchanged partition: the original policy
  changes exported meanings, while the explicit-role policy preserves them.
- Accepted partition changes, deterministic ID alignment, and genuinely stale
  upper models or archives; no automatic oracle repair.
- Continuous group-only prediction updates without granting new representations.
- Prediction before feedback, separation of fitting and selection records,
  duplicate evidence rejection and pure evaluation.
- Frozen proposals, bounded histories, pending evidence invalidation and
  checkpoint continuation under every variant.
- Identical behavior when the new history channel is disabled or ignored.

Define the history proposal rule before reserved seeds are generated. Its
inputs may include recent local/composite predictions made before feedback,
observed outcomes, prediction changes, context and representation version.
Use a bounded history attached to the existing 192 main records; no longer
retention window, extra labels or evaluator truth. Evidence of successful
adaptation must be available alongside errors.

Use that history only to prioritise one of the ordinary proposal slots at each
level. Keep the other slots on the existing stochastic schedule and preserve
reserved reduction opportunities. Fit and accept all proposals using the same
predictive evidence and thresholds as the data-only role candidate. This
preserves discovery opportunities when predictors agree. The exact summary,
priority score, tie rules, slot allocation and accounting must be specified
and tested before R1; they must not be chosen from benchmark outcomes.

**Exit:** parity, contracts, resource checks and independent fixture replay
pass. Freeze the complete R1 protocol, implementations, metrics, fixtures,
auditor and prior dependencies. Stop if this gate fails.

## Stage R1: controlled architecture comparison — proposed record 024

Use six variants. Acquisition remains the same for all; policy differences
start after the shared acquisition curriculum.

| Variant | Prediction updates | Structural review | Representation / history policy |
| --- | --- | --- | --- |
| B64: original reference | Existing rules | Every 64 records | Existing behavior |
| B128: timing control | Existing rules | Every 128 | Existing behavior, slower review only |
| U64: uniform-update control | Refit all active predictive tables | Every 64 | Existing representation rules |
| U128: matched control | Refit all active predictive tables | Every 128 | Existing representation rules |
| R128: explicit roles | Same as U128 | Every 128 | Form role owns exported meanings; main observations only |
| H128: roles plus history | Same as R128 | Every 128 | Same ownership; adaptation history prioritises proposals |

The key contrast is **R128 versus U128**. B128 versus B64 measures slower
review under the old policy; U64 versus B64 measures the predictive-update
change; U128 versus U64 checks timing under uniform updates. H128 versus R128
isolates the additional history channel. Report comparisons with B64 too:
beating a deliberately weak matched control would not justify adoption.

Use the same available partitions, upper input specifications, number of fitted
proposals per review, count estimator, main buffers, local feedback, selection
batch size and acceptance thresholds. Keep the original one-slot archive rule
and its capture/retrieval gates across variants. Do not add the 020–022 policy
extensions or tune memory while testing roles. Record archive compatibility
effects caused by changed representation histories.

Provide identical main and allocated selection streams. A 128-record variant
uses the current 32-row selection batch at its review; it does not pool skipped
batches or train on them. Charge allocations and actual use separately. B128
and U128 control for these reduced review opportunities. Proposal budgets are
matched per opportunity, not falsely claimed equal across different schedules.
History summaries add computation, which must be counted explicitly.

### Five histories

Retain two four-state local modules, a binary supplied action and a binary
composite outcome. Use the existing acquisition scale and 1280 main records.
The simulator alone knows the changes.

| History | Purpose |
| --- | --- |
| Stable world with noisy outcomes | Measure needless representational revision and false discoveries. |
| Predictive probabilities change, useful partitions stay fixed | Test adaptation within a representation without requiring a new distinction. Include a local probability-order reversal so exported-meaning ownership is exercised. |
| Local forms collapse and later return | Test simplification, dependency removal and subsequent structural recovery. |
| Raw detail matters, becomes irrelevant, then returns | Test information hiding, reopening and useful memory. |
| Same detail history, but returning outcomes reverse | Measure obsolete-memory costs and adaptation to changed consequences. |

For the last three, retain boundaries after records 240 and 528. For the
probability-only history, place changes at the same boundaries, preserve the
equivalence classes, and explicitly specify local/composite target laws and
probabilities in the frozen protocol. Changes in numerical labels alone must
not be scored as different partitions. Continue independent 10% observation
noise where compatible with the specified target law; state latent probabilities
explicitly rather than accidentally counting the noise twice.

Reserve environment seeds 1200–1204 and proposal seeds 1200,1201. Five histories
× five environments × two proposals × six variants = **300 runs**. Pair layouts,
inputs and noise where the histories permit it; separate RNG streams for each
channel and record their definitions. Do not expose regime markers, reset
states, or supply evaluation results to the learner. Five environments with
two proposals are not ten independent environments or new task families.

### Outcomes and proposed decision gates

Measure prediction, representation and resources separately. Report observed
and latent online loss; withheld-composition transfer; full validity; interface
sufficiency/minimality; structural revisions and exported-meaning changes;
raw reads and bypass of incorrect local forms; capture/retrieval utility;
recovery delay, regression, and computation. Include every acquisition failure.

Evaluate all variants on the same 64-record grid, after any scheduled review,
plus exact regime boundaries. Evaluation must not update the learner. Retain
the existing loss-regret allowance of .10 and exact local partitions up to
renaming. Do not require a unique encoding when multiple representations are
equally sufficient and minimal. Define the task-specific oracle tests before
running, especially in the probability-only history.

Proposed primary gate for R128 versus U128:

1. Reduce inappropriate-representation checkpoints by at least 25% across the
   form-return and detail-return histories, improving at least 8/10 paired
   environment/proposal cases when the two histories are aggregated within
   each pair. Report each history separately as well. A zero-error control
   leaves the benefit unestablished.
2. Transfer and final full validity reach at least 8/10 for R128 and U128 in
   each history. No gain obtained by bypassing a wrong local form counts as
   full representational recovery.
3. Against both U128 and B64, R128's mean observed and latent loss costs are
   at most .02 nats in each whole history and each adaptation window. Use
   records 241–496 and 529–784 as the fixed adaptation windows. Mean confirmed
   full-validity recovery is no more than 64 records later. Confirm recovery
   at the second consecutive valid common-grid evaluation; retain censored
   cases and predeclare their comparison treatment.
4. Disclose worst-pair costs and impose an observed adaptation-window cost
   ceiling of .10 nats for every pair against either control. This addresses
   the individual setback that a mean allowance concealed in 022.

For the representation checkpoint count, use every common-grid evaluation
from 256 through 1280 in both designated histories. Count a checkpoint as
inappropriate if local partitions are wrong or the deployed interface fails
the declared sufficiency/minimality test. Each paired case contains both
histories; do not count them as independent samples. The gate is a practical
decision threshold, not a statistical significance claim.

H128 earns an additional history-benefit claim only if it improves mean
observed adaptation-window loss over R128 by at least .02 nats and improves
at least 8/10 pairs, averaging the two windows and four changing histories
within each pair. Require the same validity, per-history loss, recovery and
worst-pair guards against R128, U128 and B64. Report losses for successful
and unsuccessful revisions; proposal activity is not benefit.

These are proposed gates to resolve during R0, **before any reserved outcome
is inspected**. The executable protocol must settle censoring, ties, exact
latent laws and oracle definitions. Once frozen, no criterion is relaxed and
no extra seeds are added to turn a failure into a pass.

## Stage R2: confirmation and architecture decision — proposed record 025

If the explicit-role primary gate fails, retain the existing reference and
close the comparison with its measured benefits, costs and unresolved cases.
A history-only benefit cannot be relabelled as evidence for role separation.

If R128 passes, confirm on environment seeds 1300–1304 and proposal seeds
1300,1301 without changing code or thresholds. Compare R128 with U128; use
H128 instead only if both the R128 gate and the additional history gate passed.
This selection rule is declared in advance. Five histories × ten pairs × two
variants = **100 confirmation runs**, not an open search for another policy.

The selected candidate must repeat the representation-benefit, validity and
cost gates against U128. Its original B64 comparison remains separately
reported. A failed confirmation leaves adoption unsupported. Successful
confirmation permits a documented choice of the candidate as the reference
for the next steering study, within these task families; it does not establish
universal superiority. Conditional selection does not erase the R1 controls.

## Budget and stopping boundary

These are planning ceilings; final accounting must be verified on fixtures
before R1 freezes. Shared acquisition allocates 1024 labels per run; 1280
joint main records allocate 3840; twenty 32-row joint selection batches
allocate 1920. Total **6784 allocated labels per run**.

| Stage | Runs | Allocated learning-label presentations |
| --- | ---: | ---: |
| R0 | Saved replay and bounded fixtures | At most 5000 new fixture labels across all attempts |
| R1 | 300 | 2,035,200 |
| R2, conditional | 100 | 678,400 |
| Maximum benchmark total | 400 | 2,713,600 |

Cap candidate fits at 99,600 for R1 and 33,200 for R2, based on 32 acquisition
fits plus at most 20 reviews of eight local and seven upper fits per run.
History prioritisation cannot add predictive fits. Proposed scoring ceilings
are 15 million queries for R1 and 5 million for R2; separately count history
summary/proposal arithmetic and freeze its bound during R0. Main buffers remain
192 records per module, with one bounded history over those records and the
existing pending/archive table limits. Freeze evaluation-query ceilings too.
Benchmark and independent audit limits are 900 seconds each per stage.

Use synthetic seed 3990 or hand-built fixtures; preserve every attempt and
charge cumulative fixture use. Persist full worlds, predictions, events,
checkpoint states, costs and source hashes. Independently reconstruct streams,
model arithmetic, meaning changes, selection, metrics and resource accounting
without importing the runtime policy. Audit failure or a resource overrun
leaves the stage incomplete. An empirical failure is a completed result.
No benchmark tuning, automatic scaling or external actuation is included.

## Handoff to steering and writing

Produce an architecture decision record: retain the current learner, adopt
the confirmed explicit-role candidate for bounded research, or state that the
evidence is inconclusive. Include the costs and what actually caused any gain;
do not choose a diagram because it is more appealing.

The next post can explain that decision. Only then specify a steering study:
can a human or AI use the chosen learner's evidence to predict the effect of
a bounded intervention, make it, and verify that intended behavior improves
without unacceptable collateral loss? Compare against an unchanged learner
and simple intervention controls, with pause/restore available.

Steerability is a separate measured claim whichever architecture is retained.
This plan does not execute that study, claim a safety advantage, or reopen
the completed 019–022 round.
