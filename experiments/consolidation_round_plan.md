# Consolidation round: one learner for revisable generalisations

Planning document, 2026-10-21. Status: **planned, not implemented or run**.
Prepared following the user's request to plan consolidation after Experiments
010–015. The Substack draft remains a separate document for the user to edit.

## Aim and claim boundary

Can one continuing learner construct, test and revise generalisations through
distinctions, relationships and interfaces, while preserving a record of the
evidence and costs of each change?

Consolidation has two parts: a shared implementation with explicit contracts,
then new evidence about interactions among its operations. Merely putting the
existing scripts behind one entry point would achieve neither integration nor
generalisability. Conversely, consolidation need not force every operation
into one update equation.

The intended output is a small reusable experimental learner, evaluated within
a supplied representation language. Success would support learning and revising
generalisations in that setting. It would not establish general intelligence,
optimal learning, learned architecture, meta-learning, interpretability for
users, or a safety advantage.

The motivating evidence and failures are collected in the
[010–015 synthesis](../results/relationships-interfaces-synthesis.md).

## Scope: integrate before adding capabilities

Keep the existing small supervised simulation setting: two lower modules,
four raw states per module, one or two forms per module, and one upper
action-conditioned binary predictor. The two-level wiring, local observation
channels and binary action alphabet remain supplied. Actions are scheduled,
not autonomously selected. Independent outcome noise and stochastic proposal
ordering remain present.

Integrate these operations:

| Operation | Existing evidence | Integration question |
| --- | --- | --- |
| Propose and select local forms | 006, 013–015 | Can discovery remain possible when current predictors agree or an incumbent is protected? |
| Use a joint relationship | 010–011 | Can selected dependencies be represented by the same prediction machinery used for forms? |
| Collapse and recreate a distinction | 008–009 | Can a live consumer survive a changing lower representation without treating old IDs as unchanged meanings? |
| Hide detail while retaining a predictor | 012 | Can memory be captured by a declared operation rather than at an oracle phase boundary? |
| Compose local abstractions | 013 | Does useful transfer survive shared machinery and later structural changes? |
| Reopen and reclose an interface | 013–014 | Does the higher level distinguish repaired abstraction from a successful bypass? |
| Protect an established form | 015 | Does protection help the nested system enough to justify its adaptation cost? |

Earned protection remains an experimental option. It does not become the
default because it sounds desirable: 015 failed its lasting-change loss guard.

Defer temporal folds/Markov traces, learned depth, new perceptual primitives,
active exploration, language, symbolic theorem proving, LLM-generated runtime
proposals and meta-learning. Do not add phase dynamics simply to make the
implementation resemble all four influences. Their role remains conceptual;
this round tests no formal unification of Grossberg, Friston, QBism or Kelso.

## A common representation and learning contract

Use a small typed graph with fixed available connections and learned use of
them. Each node owns a predictor, a bounded main-observation buffer, and
explicit policy state. These are shared types, not a claim that all node roles
have identical learning dynamics.

| Object | Required content and responsibility |
| --- | --- |
| Form | Membership map, local predictive counts, exported IDs and revision history. Separate an ID from its meaning. |
| Relationship | Selected input ports and a joint conditional table. Joint proposals must be possible even when neither input helps alone. |
| Interface | Which group or raw ports a consumer may read. Enforce access at the prediction call. |
| Candidate | Proposed operation, fitted or frozen parameters, construction data IDs, dependencies and selection evidence. |
| Retained memory | Frozen predictor, source representation fingerprint and capture event. No updating while hidden. |
| Evidence state | Provisional/established status, pending witnesses, failures and invalidations. It is fallible state under fixed rules. |
| Event | Before/after state, reason, losses, observation IDs, costs and accepted/rejected decision. |

Continue using ordinary predictive log loss and simple conditional probability
tables. Report representational and computational costs separately. Avoid a
new weighted utility combining correctness, simplicity, novelty, goals and
safety. Smaller adequate representations can be selected through an explicitly
declared adequacy rule; that remains a supplied structural preference.

The common loop must make these boundaries explicit:

1. Predict through the deployed interface before the outcome is supplied.
2. Add main observations to bounded buffers and update only the models whose
   declared policy permits updating. Hidden and pending snapshots stay frozen.
3. Construct and rank candidates without fresh selection labels. Scheduled
   proposals continue even when fast/retained responses agree.
4. Review local candidates with local outcomes. Commit accepted local changes
   before preparing the upper review, as in 013–014.
5. Check dependency fingerprints, prepare upper candidates using the current
   exported maps, and review them using composite selection outcomes.
6. Apply explicit replacement, reduction and archive rules. Record the complete
   decision, including no-change decisions and displaced memory.
7. Evaluate with learning frozen and without mutating buffers, RNGs, counters
   or pending evidence. Evaluator knowledge never enters learner decisions.

A local revision can make an upper predictor stale without making it impossible
to execute. Keep that stale predictor observable and test whether it remains
useful; do not automatically give the learner a repaired upper table. Invalidate
pending comparisons made under changed group maps. Archive retrieval requires
a compatible fingerprint of the consumed port domains and exported mappings.
Identical meanings may recur under newer revision numbers; matching revision
numbers alone is not a compatibility test. Incompatible memory must be rejected
or explicitly refitted from permitted observations, never silently relabelled.

Keep record identities separate from current encodings. Re-encoding an old raw
observation under a new form does not create a new observation or independent
selection evidence. Reusing a selection batch across decisions must be recorded.

Information hiding concerns prediction access. Lower nodes and bounded search
buffers still observe raw inputs. Do not report this as reduced sensing,
security isolation, or a demonstrated Markov blanket.

## Stage C0: design and compatibility, reserved record 016

Produce a short architecture specification and a capability-to-code map before
implementing the shared core. Establish explicit policy switches for legacy
behaviour, rather than embedding benchmark names or phase identifiers in the
learner. A simulator supplies observations; an evaluator alone knows truth.

Implement the core in new files, with experiment drivers and independent
auditors separate. Preserve all existing source, protocols, results and hash
manifests. Treat legacy scripts as references, not editable library code.

Compatibility checks should replay saved observations, not acquire new world
evidence. Require parity of predictions, proposals, decisions, archive events
and counted costs for 012–015 under their legacy settings. Earlier form
creation/collapse and joint-only interaction cases need explicit regression
fixtures. State any capability whose parity has not been established; do not
call selective endpoint agreement complete compatibility.

New correctness fixtures cover incompatible archives, returning compatible
meanings, changing group IDs, evidence invalidation, bounded eviction, pure
evaluation, inaccessible raw ports, and round-trip serialisation. A saved
checkpoint restored into a fresh learner must produce the same subsequent
decisions given the same observations and RNG states.

**Exit condition:** parity and invariants pass; the architecture document lists
all supplied assumptions and all intentional departures used by later stages.
Compatibility is an engineering result, not another learning success.

## Stage C1: interacting form protection and interface revision — proposed 017

Question: does protecting a lower form reduce unnecessary upper exposure,
and what does it cost when the lower relationship really changes?

Use the 013 acquisition and composition curriculum, followed by 512 adaptation
records. Preserve the existing local and upper candidate languages. Compare
the full 2×2 combination of local replacement and upper reclosure:

| Variant | Local replacement | Upper interface |
| --- | --- | --- |
| Immediate/opening | Original immediate rule | Failure-triggered reopening |
| Immediate/reclosure | Original immediate rule | Reopening plus 014 reclosure |
| Earned/opening | 015 earned protection | Failure-triggered reopening |
| Earned/reclosure | 015 earned protection | Reopening plus 014 reclosure |

Three paired conditions:

* Persistent local forms and composite relationship.
* Persistent remapping in one lower module; composite outcomes follow the new
  forms while the upper form-level relationship stays unchanged.
* A brief misleading burst in one local observation channel; true local forms
  and the composite relationship stay unchanged. This tests propagation of a
  local error, not just corruption of all feedback channels together.

Use five fresh environments and two proposal seeds, initially reserve 600–604
and 600,601. The full protocol must fix the RNG namespaces and burst timing.
No run may reset, receive a branch signal or use evaluator feedback. The
factorial comparison measures the interaction; do not infer the combined
benefit by adding results from 014 and 015.

Report local validity, upper predictive validity, correct coarse exposure,
unnecessary reopening, time spent bypassing a wrong local form, reclosure
latency, observed and latent loss, and costs. Recovery must distinguish the
first valid checkpoint from its confirmation at a subsequent checkpoint.

Recommended pre-run targets retain the earlier practical standards: at least
8/10 transfer-valid and final-valid runs per relevant condition; persistent
loss cost no greater than .02 nats; remap loss cost no greater than .05 and
recovery no more than one 64-record review later for earned versus immediate
at matched upper policy. A protection-benefit claim additionally requires a
positive control error count, at least a 25% reduction in invalid local
checkpoints in the burst condition, and improvement in at least two seed pairs.
Zero control failures mean benefit is untested, not demonstrated.

The exact windows and conjunction of criteria must be frozen before running.
Acquisition failures stay in all denominators; shared acquisition is not counted
as three independent replications. Report each cell and paired difference,
including the effect of reclosure with and without earned protection.

**Progression gate:** implementation/audit correctness plus the predeclared
immediate/reclosure reference achieving transfer and final validity in at least
8/10 pairs in each condition. An empirical failure of earned protection remains
a reported failure but does not by itself veto C2. C2's policy is selected here
in advance, not chosen as the winner after C1: immediate local replacement with
reclosure. If the reference misses its gate, stop with consolidation incomplete.

## Stage C2: a continuing learner with revisable structure — proposed 018

Question: can forms, dependency selection, interfaces and retained memory
coexist through a sequence of changes, with no phase-specific learner code?

Extend the shared representation with selected upper input subsets, including
joint proposals, and a bounded archive. Permit collapse of a local form and
removal of an upper dependency through a common *smaller-but-adequate*
candidate operation. This is an intentional extension of the legacy rules,
not a claim that a refactor alone produced new behaviour.

Before execution, specify the complete arbitration policy. Recommended default:
ordinary accepted improvements take priority over pending reductions; reductions
require two fresh witnesses with loss <=.55 and disadvantage <=.02 nats; a
dependency change invalidates incompatible pending evidence. Reserve proposal
capacity for reductions so their consideration does not depend on luck. Retain
stochastic proposals for alternative forms and joint dependencies. Record this
change from the original proposal deck. Exact ranking, tie-breaking, candidate
slots and priority across reductions must be frozen in the C2 protocol.

Capture a frozen upper predictor on an accepted reduction in exposure, not at
a simulator phase boundary. Retain at most one upper snapshot, using a fixed
most-recent-capture eviction rule. Check its representation fingerprint before
retrieval and require fresh predictive evidence before deploying it. Record
whether restoration helped compared with rebuilding. No hidden snapshot may
quietly continue learning.

Use the same acquisition curriculum followed by 768 adaptation records, with
three continuous histories:

| History | Sequence | Required distinction in evaluation |
| --- | --- | --- |
| Form and relation return | One module's local effects become equivalent, making its upper dependency unnecessary; the original distinction later returns. | Collapse versus merely equal predictions; relation removal versus retaining an unused dependency; structural versus predictive recovery. |
| Detail returns | Hidden raw detail becomes useful, ceases to matter, then becomes useful again. | Open, hide, retain and retrieve; useful memory versus a fresh refit. |
| Old detail becomes misleading | Same initial opening and hiding, but the returning detailed relationship has reversed outcomes. | Evidence-tested memory rejection versus stale reuse; adaptation cost of retaining memory. |

Default phase lengths are 240,288,240 adaptation records, putting switches
after 240 and 528, between 64-record reviews. The full protocol must define
selection-batch regimes at boundaries and the unchanged acquisition baseline.
The learner receives no switch signals. Histories two and three share all data
until the last phase; paired noise and input streams preserve fair comparisons.

Compare four predeclared variants:

* Integrated learner: immediate local improvement, adequate reductions,
  reopening/reclosure and compatible retained memory.
* Delete hidden predictor: identical structural possibilities, but discard
  the snapshot's fitted parameters; rebuild from the same recent data.
* Always expose raw detail: a raw conditional-table control, with the same
  allocated local observations and curriculum, to measure what abstraction
  costs and contributes. Count unused feedback and unequal computation.
* Fixed local forms: freeze lower structure after acquisition, while allowing
  upper revision. This exposes how much apparent recovery can come from bypass.

All variants use one continuing state per run. Reserve fresh environment seeds
700–704 and proposal seeds 700,701. Do not select favourable acquired forms or
restore oracle checkpoints. Archive access and extra candidate scoring are
explicit costs, not hidden resources.

Recommended primary targets are at least 8/10 complete integrated trajectories
in **each** history, including initial transfer, required structural operations
and final predictive validity. Validity retains modal accuracy 1 and expected
log-loss regret <=.10 in these tiny enumerable worlds. Define exactness up to
irrelevant group renaming, while separately auditing semantic ID alignment.

At declared phase endpoints, require sufficient interfaces with no unnecessary
raw exposure. Confirm that removing a relevant input hurts prediction and that
discarded inputs add no material predictive benefit under the evaluator's known
world. These are diagnostic counterfactuals, not feedback or causal discovery.

For retained memory, carry forward a separate practical target: mean early-return
loss improvement >=.02 nats versus deletion, improvement in at least 8/10 pairs,
and no more than .02 mean loss cost in the reversed-return condition. Fix the
early-return window before execution. Also require lower raw-read use than the
always-open control during the designated hidden phase. Resource savings and
prediction costs must both be reported; do not combine them into an adjustable
score. Freeze all endpoint definitions and any further tolerances before running.

**Exit condition:** independently audited results, including every failure,
against the frozen criteria. A failed criterion is not relaxed to declare the
round complete successfully. The round can end with a useful negative result.

## Budget and execution discipline

These are planning ceilings and proposed designs, not completed protocols.
Before each benchmark, save its final protocol, source, tests, auditor and
dependency hashes. Freeze choices using synthetic correctness fixtures only;
do not inspect reserved benchmark seeds while choosing policies.

| Stage | Proposed runs | Labels per run | Allocated label presentations |
| --- | ---: | ---: | ---: |
| C0 | Saved-trace replay and bounded fixtures | No new benchmark streams | Count replay and fixture work separately |
| C1 / 017 | 3 conditions ×5 environments ×2 search seeds ×4 variants =120 | 768 local acquisition +256 upper training +1,536 adaptation +768 selection =3,328 | 399,360 |
| C2 / 018 | 3 histories ×5 environments ×2 search seeds ×4 variants =120 | 768 local acquisition +256 upper training +2,304 adaptation +1,152 selection =4,480 | 537,600 |
| Total new benchmarks | 240 | | **936,960** |

The counts include local and composite outcomes separately. Generated stream
labels total 49,920 for C1 and 67,200 for C2, including paired duplicated
histories. Record allocated versus actually used labels for every control.
Repeated presentations and two proposal seeds are not independent tasks.

Keep buffers at 192 main records per node, four fitted local proposals per
review, and at most twelve upper fitted proposals per C2 review. C1 retains
three upper fits per review. This caps new benchmark candidate fits at
47,040, assuming the shared acquisition above. Archive proposals add scoring,
not fitting; account for both. A lower pending candidate needs at most two
cells, an upper model at most sixteen (raw control thirty-two), and the single
upper archive at most sixteen. Count every pending table separately; freeze
its maximum count in the stage protocol.

Allow at most 20,000 additional synthetic fixture label presentations. Do not
spend remaining capacity on seed searches. Each full protocol must also set
evaluation/scoring ceilings and a wall-clock stop limit after implementation
timing on fixtures. Hitting a resource limit yields an incomplete result,
not permission to extend the run.

Audit data generation, model arithmetic, proposal decisions, dependency
compatibility, event ordering, metrics, costs and all manifests independently
of learner code. Stop on leakage or an audit discrepancy. Distinguish a source
bug from empirical failure; preserve affected outputs and disclose any correction.
Do not tune failed experiments or overwrite their artifacts.

## What completion would permit next

Produce a shared-core specification, compatibility report, two bounded findings
reports if both stages proceed, and an updated evidence map. State which
capabilities actually coexist in the integrated variant, rather than combining
the strongest result from each control into an imaginary learner.

If consolidation succeeds, a later round can test interpretability and
design-led modification: can a reader infer a form's scope from its evidence,
predict an intervention's consequences, and make a bounded useful change?
The event record and state contracts prepare for those tests; their existence
does not establish interpretation or steering.

Meta-learning remains later: experience would need to improve subsequent
learning on held-out task families against fixed-policy and reset-memory
controls. This round changes evidence state under fixed rules, not those rules
through learned experience. Language or additional logic is not a prerequisite
for the present generalisation tests, and neither is assumed to emerge.

Inspectable structure may help assessment and intervention, but no safety
advantage follows automatically. Keep execution isolated with bounded resources,
auditable state and pause/restore controls. Scaling, live connections and
deployment remain outside this round. The first executable step, once work on
the plan proceeds, is C0 specification and compatibility—not a new benchmark.
