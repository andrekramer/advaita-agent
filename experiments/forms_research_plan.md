# Learning forms: proposed next experimental direction

Status: research direction, 2026-10-15. The acquisition stage is now specified
in a [fixed protocol](forms_protocol.md) and completed in the
[first form-learning experiment](../results/forms-v1/findings.md). The proposal
below records the motivating design; the protocol fixes its implementation
choices. A [collapse point test](../results/collapse-v1/findings.md) and an
[acquire–collapse–reacquire test](../results/reversibility-v1/findings.md) are also
complete; retention under interference, broader revision, and exploration remain
proposals. See the [research consolidation](../results/research-synthesis.md) for
the claim boundary: reversible structural learning, with no demonstrated
meta-learning or learned hierarchy.

The follow-on experiment focuses on
[complementary situated and retained roles](complementary_roles_design.md):
whether better recognition helps learn an action-consequence relationship and
whether that retained relationship improves recognition in turn. This tests
directional contributions within one learner, rather than treating the value of
a second copy of the same predictor as the sole question. It uses a smooth world
without supplied category boundaries. It is now
[implemented and completed](../results/complementary-roles-v1/findings.md).
The response relationship was learned, but the declared criterion for robust
reciprocal complementarity failed. A separate, smaller collapse experiment then
tested removal of an acquired distinction after a change in consequences; it
did not extend or rerun the complementary-role experiment.

## Question and operational meaning

Can a learner discover a useful organisation of experience, recognise it in new
instances, retain it, and revise or collapse it when consequences change?

The completed association experiments provide a baseline, not evidence of form
discovery. Their input categories and output distinctions were supplied. The
new task should withhold category identities and teach through observed action
consequences. Keep the world and computation small; broaden what can be learned.

Here a **form** is a reusable grouping of contexts with sufficiently similar
predicted consequences under the available actions. Its implementation includes
a recognition rule, action-conditioned predictions, supporting evidence, and a
record of revision. This is a deliberately limited operational definition, not
a definition of every kind of form or meaning.

For this proposal, name identifies the learned structure; form organises
recognition and prediction; action exposes consequences that can support or
challenge it. Assign neutral identifiers such as `form-1` automatically. Human
or AI descriptions can be added after evaluation and must be checked against
the recognition rule and predictions. Naming does not count as learning.

This correspondence develops the project's Vedanta-inspired framing; it does
not purport to formalise Vedanta or establish a claim about consciousness.

## First experiment: discover action-equivalent forms

Use an isolated simulator with three observable binary features
\(x=(s,t,c)\), two actions \(a\in\{0,1\}\), and an observed binary outcome
\(y\). The evaluator knows the simulator's rule:

\[
y=s\mathbin{\mathrm{XOR}}a.
\]

Only the harness knows this equation. The learner receives three neutrally named
feature positions, the action, and the subsequent outcome. It receives no form
label, relevant-feature index, target number of forms, or hidden simulator state.
For every pair, predict before revealing the outcome. Randomly permute feature
positions per seed, with the same permutation for all compared learners.

The two action-response profiles are `(0,1)` and `(1,0)`. Features t and c do not
affect consequences in this world. The meaningful grouping therefore ignores
them. Neither the grouping nor its recognition rule is provided to the learner.
However, the perceptual features, actions, outcome alphabet, and candidate-rule
language are constructed by us. Success would demonstrate discovery within this
small supplied language, not discovery of the perceptual primitives themselves.

Withhold contexts `(0,0,0)` and `(1,1,1)` from all training, structural proposal,
selection, and diagnostic probes. Train on the other six feature combinations,
covering both actions equally. Evaluate the withheld contexts under both actions
only after learning is frozen. Both feature values occur during training; the
novelty is their combination. Correct prediction must come from reuse of a rule,
rather than a learned entry for either withheld context.

Initially choose actions by a balanced external schedule. This establishes
coverage of both interventions without giving the learner an exploration policy.
Because the simulator sets actions and produces their consequences, the task
can test action-conditioned predictions. It does not test discovering causality
from confounded observations or autonomous action selection.

### Minimal representation to specify

Start with one provisional form. Permit a small decision-rule representation
whose tests use the three supplied feature positions. A split changes a context
recognition rule; a merge allows contexts to share an outcome predictor again.
Allow at most eight recognition leaves and four distinct response forms.
Several leaves may refer to the same form. Record leaf count and form count
separately: multiple recognition paths need not imply different consequences.

Each form predicts \(p(y\mid a,\text{form})\). All contexts must have a defined
assignment and prediction, including contexts absent from the training stream.
Do not initialise separate forms using the simulator's latent rule. The
allowable operations are supplied by design; which operations are retained must
depend on experience.

Before execution specify outcome smoothing, rule enumeration and tie-breaking,
how sufficient statistics move on splits and merges, proposal frequency, and
the treatment of insufficient evidence. Enumerating all eight complete context
rules is an available upper bound on recognition complexity, not a requirement
to create them. Do not let a proposed split fabricate outcome observations for
its children.

### Fast/slow hypothesis

The retained model N supplies the currently established recognition rules and
response predictions. A provisional model A can propose revised rules and
responses, using new experience and a bounded record of past observations.
Compare their predictions on the same admissible context/action pairs:

\[
D=\frac{1}{|U|}\sum_{(x,a)\in U}
\frac12\sum_y|p_A(y\mid x,a)-p_N(y\mid x,a)|.
\]

This extends the existing response differential to models whose internal
partitions may differ. Persistent disagreement can trigger a proposal review;
external prediction performance must select it. Include an outcome-error trigger
or a bounded scheduled proposal opportunity: identical but wrong models have
zero disagreement and still need a route to discovering a distinction.

An illustrative selection objective is

\[
J(M;V)=\frac{1}{|V|}\sum_{(x,a,y)\in V}-\log p_M(y\mid x,a)
+\lambda_f K(M)+\lambda_r L(M),
\]

where K counts response forms and L counts recognition leaves. The complexity
terms discourage distinctions that add no predictive value. Fix their weights
and a minimum selection improvement before running; report predictive loss and
both complexity measures separately. V is reserved observed feedback, never
the withheld-combination evaluation set. A selection batch must not also fit
or generate the candidate being judged on that batch. Repeated candidate
search can overfit selection evidence; bound candidates and use fresh batches.

Retention here means accepting a reusable organisation, not merely lowering a
learning rate. A can teach N by proposing such an organisation. This is a new
structural extension: the old F-to-S weight-transfer equations assume fixed
features and cannot simply be applied to a split or merge. Do not claim that
structural promotion conserves immediate predictions. Specify state transfer,
diagnostic resets, and prediction changes explicitly.

### Controls and evidence

Compare four learners with paired streams and equal allocated feedback:

1. A context/action lookup table, which can memorise observed combinations but
   has no rule for generalising to an unseen combination.
2. A single adaptive structural learner with the same rule language, candidate
   operations, selection evidence, and resource caps, without provisional and
   retained models. Match total proposal/evidence budgets, not just per-model
   budgets. This is the essential control for whether two timescales help.
3. The provisional/retained structural learner described above.
4. A fixed, feature-based predictor using all three features and their action
   interactions. It can generalise without explicit category creation and tests
   whether categories add anything to prediction or inspectability here.

The simulator's true two-form grouping is an evaluator-only reference. It is
not a source of training labels, candidate rules, or semantic names.

Report withheld-combination log loss and accuracy; pre-update training loss;
the learned recognition rules and action-response tables; number of forms and
leaves; and every accepted/rejected structural proposal. Check whether changing
t or c changes predictions unnecessarily, and whether changing s changes the
predicted action-response profile. Perform those evaluator checks only after
freezing learning. Check partition agreement independent of arbitrary form IDs.

Do not call successful prediction alone form discovery. A positive finding needs
both transfer to withheld combinations and an explicit reusable grouping aligned
with action consequences. If the single structural learner also succeeds, that
supports the form-learning task while leaving any IVSR advantage unestablished.
If the fixed predictor succeeds equally, report that category creation was not
necessary for predictive success. Slow-memory retention requires a subsequent
test; it is not established by grouping alone.

Proposed first-run ceiling: five seeds, four learners, 192 training pairs and
48 reserved selection pairs per learner, plus the four withheld evaluation
pairs: **4,880 allocated outcome-bearing presentations**. Training comprises 16
balanced passes over the 12 admissible context/action pairs; selection comprises
four separate balanced batches. Fix when proposals are fitted and tested, and
how controls access the reserved evidence, before execution. Any extra labelled
diagnostics must fit a revised declared budget. Log unlabelled prediction probes,
candidate counts, storage, and actual feedback use separately. No tuning after
seeing these five benchmark runs.

## Subsequent questions, each requiring its own bounded protocol

1. **Retain and reopen a form.** Introduce distractor learning, then revisit the
   original rule through fresh instances. Separately alter one subgroup's action
   consequences so an old grouping becomes inadequate. Compare retrieval,
   adaptation, and interference against the single structural learner. Include
   matched transient corruption and persistent change conditions; neither
   confidence nor a slow update rate establishes justified recognition.
2. **Merge and collapse.** Change the simulator so a previously relevant feature
   ceases to distinguish consequences. Test whether the learner reduces its
   representation without losing useful prediction. A temporarily rare group
   must not be treated as equivalent merely because evidence is missing.
   The first deterministic, balanced instance is now
   [completed](../results/collapse-v1/findings.md): appropriate collapse and
   preservation both passed. A subsequent uninterrupted
   [reacquisition test](../results/reversibility-v1/findings.md) also passed,
   with a temporary prediction cost relative to keeping the distinction.
   Rare-case and noisy-equivalence tests remain open.
3. **Choose when to investigate.** Introduce a bounded choice between actions
   that achieve an immediate objective and actions that discriminate candidate
   forms. Specify objective, action costs, and an exploration budget. Measure
   what was learned and the cost of learning it. Compare adaptive choice with
   balanced and random schedules. A mode called explore/exploit is a policy
   mechanism; it is not yet an oscillator phase or evidence of phase dynamics.

Keep these separate so a failure can be attributed. The first experiment does
not claim autonomous exploration, causal discovery, broad abstraction, effective
steering, or an advantage for dual timescales. Later steering tests can freeze or
edit a learned recognition rule and measure predicted effects and collateral
changes; readable names alone do not establish steerability.

## Acquisition completion and stopping boundary

The bounded structural learner, single-model control, acquisition protocol, and
feedback-separation audit are complete. Both structural learners passed the
acquisition criteria in all five seeds, with identical final predictions. The
experiment supports the small form-learning task without establishing a need
for two timescales. The complementary-roles follow-on is now complete; the
first selective-collapse and reacquisition tests also passed. Reacquisition
does not establish saved-form memory, and neither test establishes meta-learning.
Retention under interference, broader revision, and exploration remain untested.
This stage pauses for interpretation and writing. Keep all actions within the
synthetic simulator; do not increase model size or add an LLM to solve the task
on the learner's behalf. There is no automatic progression to later stages.
