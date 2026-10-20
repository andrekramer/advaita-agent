# Relationships, abstractions and interfaces: capability consolidation

Consolidation, 2026-10-20, after Experiments 010–015. This is the round following
the [earlier form-learning synthesis](research-synthesis.md), not the older
directory named `round2-v1`.

The round now contains bounded demonstrations of learning joint relationships,
retaining hidden predictive detail, transferring through learned abstractions,
composing two interface levels, reopening relevant detail, hiding it again,
and protecting an established local form.
**The capability range has expanded; general reliability has not been
established.** Five of the six experiments failed their combined primary
criteria. Their successful components and failure cases are both part of the
evidence.

## Capability map

| Capability | Evidence | What it does not establish |
| --- | --- | --- |
| Learn and revise categories | Earlier 006, 008 and 009 acquired, collapsed and reacquired useful groups in supplied languages. | Discovery of arbitrary perceptual primitives or a general ontology. |
| Learn a joint relationship | 010 selected a useful feature pair whose members were insufficient alone. Deterministic search passed endpoint checks; stochastic reliability failed. | A general relational or causal learner; superiority of random search. |
| Organize stochastic variation | 011's shuffled deck improved initial candidate coverage. | Guaranteed discovery or better retention; corroborated selection sometimes blocked useful discoveries. |
| Hide detail without forgetting its predictor | 012 passed: retained detail reduced early return loss by 12.1% versus deletion, improving 9/10 pairs. | Free memory, automatic snapshot timing or a benefit when the old relationship becomes wrong. |
| Learn a reusable abstraction | 013 transferred local effect groupings to unseen upper compositions in 10/10 pairs. 014's fresh sample passed only 7/10 at the initial transfer checkpoint. | Reliable acquisition across seeds or transfer to arbitrary new task families. |
| Compose abstractions through nested interfaces | 013 recovered from changed lower membership with the higher table frozen in 9/10 runs. | Discovery of the wiring, number of levels or appropriate consolidation schedule. |
| Reopen a consequential hidden distinction | 013 selected the affected module in all ten breach runs; nine met final exactness and prediction criteria. 014 preserved needed exposure in all ten persistent-breach pairs. | Reliable attribution of every error to the appropriate level. |
| Return from detail to abstraction | 014 ended coarse and valid in 10/10 remap runs and completed a temporary-breach return in 7/10, reducing late parent raw reads by 40% on average. | Reliable reclosure timing; the overall criterion failed, including the required 8/10 temporary returns. |
| Protect an established form | 015's earned protection prevented harmful replacements during a brief misleading burst in 10/10 runs, without delaying initial acquisition. | Cheap adaptation to lasting change: recovery was one review later and the loss allowance failed. No nested integration or learned protection rule. |

The studies use related but different implementations. They must not be
presented as one general architecture that has demonstrated every capability
together. Experiments 013 and 014 do exercise local grouping and upper interface
revision within continuous nested learners, but their architecture is supplied.

## Four distinctions sharpened by this round

**Prediction and representation are different outcomes.** A system can predict
correctly while keeping unnecessary detail. It can also restore prediction by
bypassing a faulty abstraction without repairing that abstraction. Both occurred
in the nested experiments.

**Hiding and deleting are different operations.** Restricting what a prediction
interface exposes can coexist with retaining useful learned content. Experiment
012 measured a retrieval benefit against deleting that content. Its benefit
depended on the relationship returning; a genuinely new relationship still
needed learning.

**Opening and closing need separately tested evidence.** A failure-triggered
rule can discover that detail is needed without ever reconsidering that decision
once its predictions become adequate. Experiment 014 added a separate
adequacy-based route back to abstraction. It helped, but repeated evidence also
delayed some useful reclosures.

**Discovery and protection can use different evidence rules.** Experiment 015
allowed immediate provisional discovery, then required corroboration to replace
a form after it earned support. This preserved acquisition speed and resisted
a temporary misleading burst, but delayed adaptation to persistent change.
The adequacy flag is fallible evidence, not a declaration that a category is true.

These findings concern what an interface makes available and what the learner
keeps, not only the number of categories. They are compatible with treating
distinctions as revisable ways of organizing experience rather than fixed
entities that the system should multiply.

## Simple learning criteria, substantial representational choices

Experiments 010–012 used predictive log loss plus a fixed complexity penalty.
Experiment 013 used prediction loss and a failure gate. Experiment 014 added
reclosure when a smaller interface was adequately predictive on successive
batches, using explicit tolerances. Experiment 015 used evidence to change the
incumbent's protection state under a fixed rule, without adding another
prediction objective.

The latter experiments do not require a catalogue of desired outcomes or an
elaborate utility function. They still contain design choices: which outcomes
are observed, which representations can be proposed, what counts as adequate
evidence, how much memory is available and when review occurs. A preference
for smaller adequate interfaces is itself a structural bias, even when it is
not expressed as a weighted complexity term.

The work so far supports investigating a relatively simple local learning
process acting on richer, revisable representations. It does not establish
that useful organization follows from arbitrary oppositions or randomness
alone. Useful candidates must be reachable, and external consequences must
select among them.

## What changes through learning

Depending on the experiment, the learner changes probabilities, selected
features, group membership, exposed interfaces, which prepared predictor
is deployed or retained, and an incumbent's establishment state. These changes
are visible in recorded decision traces.

The following remain constructed:

* Input primitives, action alphabets and local feedback channels.
* Candidate languages, available structural operations, capacities and wiring.
* The two-level depth and semantic alignment of exported group IDs in 013–014.
* Acquisition curriculum, buffers, proposal budgets, review schedules,
  acceptance margins, reclosure rules and the establishment/protection rule.
* Snapshot timing in 012 and the rules for keeping upper tables fixed in
  013–014.

A fixed two-witness rule introduces persistence of evidence; it does not
establish a learned policy for consolidation. Neither additional layers nor
slower updates are sufficient evidence of meta-learning.

## Remaining limits

Initial acquisition and retention under noise remain vulnerable. Fresh seeds
in 014 exposed local failures that had not prevented initial transfer in 013.
Noisy or incomplete evidence can lead to poor categories, temporary bypasses,
unnecessary exposure or delayed simplification.
The isolated follow-up 015 found a protection benefit under structured temporary
corruption, but it did not reproduce initial acquisition failures, and persistent
change incurred excessive loss under its fixed allowance.

The experiments use tiny, balanced synthetic worlds with independent outcome
noise and supplied feedback channels; 015 additionally tested a brief structured
corruption burst aligned to a review interval. Rare consequential differences,
unbalanced exposure, delayed feedback, partial observability and novel task
families remain largely untested. Grouping by observed effects is not, by
itself, identification of causes.

The work does not yet demonstrate:

* General folds, return-trace interfaces or hidden temporal dynamics.
* Learned architecture or depth.
* Autonomous action selection and exploration.
* Broadly effective steering or a safety advantage.
* Necessity of the full R-rule/IVSR dynamics or reciprocal complementarity.
* Experience improving subsequent learning on held-out task families.

That last item is the eventual meta-learning question. It could involve learned
memory, initialization or revision policies even with a fixed outer update
rule; changing hyperparameters is neither necessary nor sufficient. This round
establishes candidate operations on which such learning could act, rather than
claiming that learning-to-learn has already occurred.

## Current stopping point

The rounded-out contribution is a **small experimental account of revisable
distinctions and interfaces**, with explicit controls and inspectable failures.
The completed runs justify describing those capabilities and limitations.
They do not justify scaling or silently replacing failed criteria with weaker
ones. Following the initial 010–014 consolidation, the user authorized the
bounded 015 follow-up. That follow-up is now complete; no further benchmark
or meta-learning run is included here.

Source findings:
[010](bundles-v1/findings.md),
[011](bundle-retention-v1/findings.md),
[012](interfaces-v1/findings.md),
[013](nested-abstractions-v1/findings.md),
[014](reclosure-v1/findings.md),
[015](form-retention-v1/findings.md).
