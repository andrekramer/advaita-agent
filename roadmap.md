# Future roadmap: evolving distinctions and relations

This extends and clarifies the research brief in [initial-spec](initial-spec).
The aim is to explore differences that matter by changing, creating, and
collapsing distinctions. A first model may use a fixed set of distinctions and
allowed connections, with dipoles as one candidate representation. Later models
may change those distinctions, their relations, and the rules governing change.
The mechanisms below are research proposals, not yet settled equations.

Construction and change are open to deliberate design and chance-driven
evolution. Humans, LLMs, other AI agents, evolutionary processes, or combinations
of these may construct an initial system and propose later changes. An explicit
aim may be to simulate or emulate an existing system. Development proceeds in
monitored, evaluated, and controlled steps within an isolated experimental
environment. Connecting the experimental system to the real world is not
recommended; the default scope is simulation without live external actuation.

## Aspiration and immediate mathematical focus

The aspiration is a system that **can learn, can be interpreted, and can be
steered**. It combines autonomous learning with construction and revision by
AI agents and humans. Evaluate these three aims separately: improvement from
experience; explanations of states, relations, and updates that can be checked
against behavior; and deliberate interventions that have testable effects.
None is established merely by naming internal structures or supplying controls.

The immediate research focus is the space of opposites and the mathematics of
the fast/slow learning rule. Non-dualism provides the overarching philosophy;
opposites provide a concrete mathematical space to investigate. Their study
does not require every later distinction to be dual or make the creation of
additional opposites an objective.

Before structural evolution, define the states and relations in this space and
derive how current activity, lingering traces, and retained relations influence
one another across timescales. Specify what changes quickly, what changes
slowly, what persists, and how consequences alter those changes. Distinguish
fast inference or settling from fast learning: a transient activity change
alone does not demonstrate retention. Fast and slow describe relative rates;
the formulation need not be restricted to exactly two timescales.

The first tiny experiments should test this learning rule on a fixed structure,
make its updates inspectable, and test the effects of a controlled intervention
in a relation or learning parameter. Record which behavior was learned and
which was supplied through construction. Changing, creating, and collapsing
distinctions remain later investigations built on this mathematical basis.

## Four influences for consolidation

Four influences help frame the next enquiry. They contribute different questions
and concepts; they are not a single established theory or a derivation of the
current implementation.

| Influence | Contribution to the enquiry |
| --- | --- |
| [Grossberg: complementary processing](https://sites.bu.edu/steveg/files/2016/06/Gro2000TICS.pdf) | Differently organised processes can compensate for one another's computational limitations. Ask what each learning role contributes and whether their interaction is useful; two copies operating at different rates do not establish complementarity. |
| [Friston: Markov blankets, free energy, and active inference](https://arxiv.org/abs/2201.06387) | Examine how an agent's internal organisation relates to its environment through sensory and active states, and how inference and action interact. A proposed boundary needs an explicit statistical and dynamical account. |
| [QBism: expectations, action, and experience](https://arxiv.org/abs/2512.14122) | Treat expectations as belonging to an agent and examine how the consequences of its actions prompt revision. This is an epistemic influence; the project does not thereby implement quantum probability or the Born rule. |
| [Kelso: coordination dynamics](https://ccs.fau.edu/hbblab/pdfs/2022_Kelso_Journal_of_Physics_Complexity.pdf) | Study forms as stable or temporarily sustained relationships among changing components, including loss of stability, transitions, and metastability. Distinguish movement among existing patterns from learning that changes the available repertoire. |

Kelso adds a language for how complementary processes coordinate while retaining
different tendencies. His [account of learning and metastability](https://ccs.fau.edu/hbblab/pdfs/ordered/2012_Kelso_Phil.Trans.R.Soc.B.pdf)
is relevant to the emergence, persistence, and revision of forms. The R-rule
already supplies paired contributions and phase-dependent weighting; any precise
correspondence with Haken–Kelso–Bunz dynamics would require defining the phase
variable and deriving its evolution and stability. No such correspondence is
established by the shared use of sine and cosine.

These four influences sit within the project's broader non-dual philosophy and
its interests in probabilistic causality and learned representations. They guide
consolidation before folds or meta-learning; they add no empirical claims to the
completed experiments.

## Research scope and safety

Experiments are small scale and carefully limited in scope. All AI risks and
safety concerns apply to this method and to any resulting system, including
systems constructed by humans or AI agents and systems developed through
evolution. Explicit logic, labels, inspectable structures, and modification
controls are design aims; they do not establish safety or effective control.
Whether these properties make a system safer or more controllable remains an
empirical question, and the answer may be negative or depend on the conditions.

The decision to scale or apply the method or a resulting system must not be
taken lightly. Either step requires a separate, deliberate assessment of risks,
safety evidence, limitations, intended use, and the proposed change in scope.
Successful small experiments do not establish safety at larger scales or in
other settings. This roadmap does not authorize scaling, deployment, or
connection to real-world operational systems.

Each experiment must state its limits on system size, computation, duration,
structural change, and permitted interactions before execution. Evaluation must
include failures and loss of control as well as useful performance. Reaching an
experimental limit calls for stopping or review rather than automatic expansion.

## Design aim: differences that matter within a non-dual philosophy

Non-dualism is the overarching philosophy of advaita-agent and the reason for
its name. Distinctions serve the exploration of differences that matter; they
are revisable representations, not commitments to fundamentally separate or
opposed entities. Creating additional opposites or dualities is not an objective.
A useful change may create a distinction, alter its meaning or relations, or
collapse it when the separation no longer serves the inquiry.

Begin with distinctions that are partly known, specified, or constrained, while
allowing their meanings, relations, and organization to develop. A distinction
need not take the form of a pair of opposites. The fixed structure of a first
model is an experimental starting point. The broader aim is an evolving system
whose structure remains accessible to evaluation and controlled modification
by humans and AI agents.

The motivating description is a sort of LLM with logic and labelling built in.
This states an architectural ambition; whether it uses an LLM internally, is
constructed by one, or develops a different architecture remains open. Explicit
logic should participate in inference, constraints, and permitted changes, with
its effects visible in the system's behavior. It need not assume that opposing
tendencies are Boolean negations or that only one can participate at a time.

"Name, form, and action," drawn by the project from Vedanta, provides a design
inspiration. For this engineering proposal, a name identifies a distinction;
a form is a reusable organisation recognised across variations in experience;
and action exposes consequences that can support or challenge that organisation.
Its implementation needs explicit states, relations, constraints, and recognition
rules. This is a proposed design correspondence, not a claim to formalize
Vedanta. Labels should be linked to operational definitions and testable behavior;
a readable label alone does not establish understanding or interpretability.
New distinctions may carry provisional labels while their roles are investigated.

Following the fixed-structure experiments, the
[next proposed enquiry](experiments/forms_research_plan.md) tests learning such
forms from action consequences. Slower retention should be evaluated for what it
makes recognisable and reusable, rather than equated with form extraction by
definition. The initial task separates form discovery from later retention,
revision, collapse, and exploration tests, and compares two timescales with a
single structural learner using the same representational possibilities.

Record which properties are fixed for an experiment, which are provisional
assumptions, and which are open to learning, design, or evolution. Structural
changes should preserve identities and lineage where appropriate, and record
when a label or meaning changes. Revising an experimental constraint requires an
explicit evaluation step. The aim is to keep evolved systems open to inspection
and intervention as well as measuring whether their performance improves.

## 1. Create and remove relations

Treat every represented distinction as potentially related to every other. For
clarity and efficiency, explicitly maintain only a selected set of relations.
A creation rule introduces a relation; a removal rule removes a relation whose
estimated relevance falls below a threshold.

Potential connectivity need not require storing or evaluating every pair on
every update. Candidate relations could be proposed from experience, unresolved
prediction errors, shared consequences, or chance. The proposal mechanism must
allow previously absent or removed relations to be discovered again.

Relevance needs an operational definition tied to the agent's concerns: for
example, contribution to prediction, coordination, or action relative to its
cost. Coupling magnitude or frequency of activity alone need not establish
relevance. Rarely used relations may still matter in particular conditions.
Possible mechanisms to investigate include a trial period for new relations,
evidence accumulated over time, and different creation and removal thresholds
to avoid repeated switching near a boundary.

## 2. Change or create distinctions that capture relevant differences

Introduce rules to change an existing distinction or create a new one when the
current representation misses a difference that matters. Changing a distinction
may revise its boundary, meaning, context, or relations. Creating one need not
introduce an opposite or a complementary pair.

The earlier proposal to split an opposition into three or four dimensions is one
possible experiment. Neither the number of dimensions nor a dual form is a
general requirement. Any new dimensions need explicitly defined states and
meaning. Whether a prior distinction is replaced or retained as a coarser
summary remains an open design choice.

A split must specify how current activity, uncertainty, memory traces, retained
relations, and input/action mappings transfer to the new representation. It
must also identify what information can distinguish the new dimensions; adding
dimensions alone supplies no new evidence. Proposals may be driven by persistent
mismatch, differing consequences within an existing category, or chance.

## 3. Merge or collapse distinctions

Introduce rules to merge distinctions whose separate treatment adds insufficient
value, and to collapse or remove distinctions that remain unproductive. Merging
combines distinctions into a shared representation; collapse reduces the
available distinctions without necessarily identifying a replacement dimension.

These operations need explicit mappings for activity, uncertainty, memories,
relations, and the agent–environment interface. Evaluate both the resources
saved and the useful distinctions lost. Correlated activity alone is not a
sufficient reason to merge dimensions with different consequences or roles.
Whether removed distinctions are archived for recovery or must be relearned is
an open choice.

Changing or collapsing a distinction is as central to the research as creating
one. Evaluate whether keeping a distinction changes prediction, coordination,
or action in a relevant way under specified conditions. More distinctions or
more dimensions do not by themselves constitute progress.

## 4. Regulate structural change and its parameters

Creation, removal, splitting, merging, and collapse could be governed by a new
level of logic, arise partly through chance, be deliberately designed, or combine
these approaches. Humans, LLMs, and other AI agents may propose changes alongside
the system's own adaptive or evolutionary processes. A useful candidate
organization is to propose a change, evaluate its consequences, and retain,
revise, or undo it. Random proposals provide variation; their generation and
their retention need separately specified rules.

Further meta-rules may regulate or evolve hyperparameters such as relevance
thresholds, learning rates, trace durations, proposal frequencies, and resource
budgets. Their admissible ranges, feedback signals, and update timescales must
be defined. Early experiments should hold the evaluation criteria fixed while
testing adaptive parameters, so changing the criterion cannot itself count as
improvement. An unlimited hierarchy of meta-rules is not required initially.

## 5. Construct, evolve, or emulate a system

Support both construction of an initial system and incremental revision of an
existing one. Deliberate design and evolution may alternate or cooperate: for
example, a human or AI agent may construct a candidate, evolutionary variation
may explore alternatives, and subsequent design may revise the result.

Record the origin of each change and distinguish learning within a running
system, evolution across candidate systems or generations, and externally
designed modifications. All are valid research routes, but improvement supplied
by a designer must not be reported as learning achieved by the system itself.

When simulation or emulation of an existing system is the aim, specify the
reference system, the behaviors or mechanisms to reproduce, the experimental
conditions, and the acceptable discrepancy. Evaluate fidelity separately from
other notions of useful performance. Matching observed behavior alone does not
establish that the underlying mechanisms match. Use synthetic inputs or offline
reference data within the isolated environment.

## 6. Monitor, evaluate, and control each step

Apply the same experimental discipline regardless of who or what proposes a
change. Before a trial, record the starting version, proposed modification,
evaluation criteria, resource limits, and stopping conditions. Run the candidate
in isolation, monitor its behavior and structural changes, and compare its
results with the starting version and relevant reference systems. Record the
decision to retain, revise, or reject it, with a recoverable prior version.

Control may be exercised by a human, an automated supervisor operating within
defined limits, or both. The experimental controller must be able to pause or
terminate a trial and restore a prior version. Candidates must not silently
change their own acceptance criteria or operating limits; proposed changes to
those controls require a separately recorded evaluation step.

The agent–environment action loop remains essential, but its environment is a
simulation. Physical actuators, live accounts, and external operational systems
are outside the default experimental scope. Studying or emulating a real system
does not require connecting the experimental agent to that system.

## Current experimental progression

The next round follows **learning distinctions → learning relationships →
learning interfaces → learning how to learn**. Creation, retention, information
hiding, reopening, and collapse are relevant throughout. Distinguish ignoring
detail during prediction from hiding it behind an interface and from deleting
it. Randomness belongs in both environmental variation and candidate generation,
with its usefulness tested against controlled alternatives.

The [bounded plan](experiments/next_round_plan.md) begins with relationships.
[Experiment 010](results/bundles-v1/findings.md), completed 2026-10-20, learned
useful joint-feature predictions but failed its stochastic reliability criterion.
Deterministic search was more reliable at the declared endpoints; both proposal
types could discard useful structure on a noisy selection batch. This leaves
coverage and retention as concrete issues before learned folds or meta-learning.
[Experiment 011](results/bundle-retention-v1/findings.md) then separated shuffled
coverage from corroborated selection on fresh seeds. Coverage improved, but
the stricter gate blocked useful discoveries without an observed retention
benefit in the persistent conditions. The combined method still failed its
reliability target. Creating, hiding, and deleting a representation may need
different mechanisms.
[Experiment 012](results/interfaces-v1/findings.md) then separated hiding a
learned predictor from deleting its fitted detail. Its fixed criterion passed:
9/10 trajectories in each branch, with lower early return loss from retrieval
than rebuilding in 9/10 pairs. Retention gave no benefit when the old relationship
became wrong; continuously exposing detail adapted better to that novel change.
This supports selective visibility with retained predictive memory inside a
supplied interface language. It does not yet establish learned temporal folds,
discovery of memory boundaries, or meta-learning. The snapshot timing and
structural operations remained fixed, and raw observations stayed accessible
to search.
[Experiment 013](results/nested-abstractions-v1/findings.md) tested learned
local groupings composed through two supplied interface levels. Transfer to
unseen compositions passed in 10/10 seed pairs; lower revision with a frozen
upper relationship and final recovery after relevant reopening each passed in
9/10. The combined criterion failed because only 7/10 lower-remapping runs
finished correctly behind the coarse interface. Temporary lower errors could
cause persistent overexposure at the higher level. This adds restricted
abstraction and nesting to the demonstrated capabilities while leaving
attribution of failure and subsequent hiding unresolved. Prediction loss alone
selected changes in this test; architecture, thresholds and learning rules
remained supplied. Meta-learning is still a later enquiry.
[Experiment 014](results/reclosure-v1/findings.md) added an evidence-tested route
back to a coarse interface. It improved final coarse recovery in remapping
from 4/10 to 10/10 and preserved needed detail in every persistent-breach run.
The overall criterion failed: initial transfer and temporary-breach return
each passed only 7/10. The new operation reduced late parent raw reads by 40%
on average while leaving some useful reclosures unconfirmed within the budget.
This rounds out the operations with explicit limits on their reliability;
it does not establish learned consolidation or meta-learning.
[Experiment 015](results/form-retention-v1/findings.md) isolated protection of
an established local form. Earned corroboration preserved immediate acquisition
and prevented every harmful replacement during a brief misleading burst, while
uniform corroboration delayed discovery. The combined criterion failed because
post-change prediction loss rose beyond its allowance when change persisted.
This adds an explicit distinction between provisional discovery and protected
retention, with a measured adaptation cost. That study did not integrate
protection into the nested learner, and the protection rule remains constructed.
The [capability consolidation](results/relationships-interfaces-synthesis.md)
records what is learned, what remains supplied, and the unresolved questions.
No automatic progression follows from these completed runs.

## Suggested investigation sequence

The [consolidation plan](experiments/consolidation_round_plan.md), prepared
2026-10-21, began with C0 on 2026-10-22. The
[C0 engineering gate passed](results/consolidation-core-v1/findings.md): a
shared core matched all 380 complete saved traces from 012–015, with thirteen
correctness tests and an independent artifact audit. The continuing nested
learner now supports explicit protection/reclosure switches, evidence records
and checkpoint restoration.
[C1 / 017](results/protection-interfaces-v1/findings.md) completed on 2026-10-23:
all 120 runs passed independent audit, but the combined empirical criterion
failed. Earned protection reduced misleading-burst local errors while exceeding
the allowed loss and recovery delay after lasting change. Reclosure restored
abstraction after recovery; it did not remove the local adaptation cost.
The predeclared immediate/reclosure reference passed the separate progression
gate (10/10 transfer and 9/10 final full validity in every condition).
[C2 / 018](results/structural-consolidation-v1/findings.md) completed on
2026-10-23 with all 120 runs independently audited. Its primary criterion
failed: complete integrated trajectories were 0/10 for form return and 3/10
for each detail history, below the required 8/10. Structural reduction,
dependency selection and retained memory now coexist in one continuing
learner, but recovery of predictions did not reliably restore minimal forms
and interfaces. No archive was accepted, and retained and deleted memory
produced identical prediction paths.

The bounded round is complete; reliable integrated learning remains
unestablished. The [round synthesis](results/consolidation-round-synthesis.md)
identifies focused follow-on questions: when to preserve useful memory,
how to restore abstraction after recovery, and how to balance protection
against lasting change. Further experiments require a separate protocol.
The round used 19,728 of 20,000 synthetic fixture labels; the remaining 272
do not imply further tuning or seed searches.

[Experiment 019](results/consolidated-recovery-v1/findings.md), a separately
specified test round completed on 2026-10-26, retained the learner unchanged
and extended recovery on fresh worlds. All 120 runs passed independent audit.
Stable late prediction passed in 10/10 integrated runs in each history;
stable representation passed in 6/10 forms and 9/10 for each detail history.
The representation criterion failed overall, and retained memory provided no
gain in the designated return comparison. Some forms recovered and later
regressed; fixed local forms performed well as a control. Further work should
test prospective preservation and resistance to spurious revisions against
this unchanged baseline, while measuring their cost when change is genuine.
[Experiment 020](results/consolidated-protection-v1/findings.md) subsequently
tested corroboration of established local forms, keeping the upper/interface
and memory rules fixed. All 60 runs passed independent audit. Protection
reduced affected-form errors from 9 to 1 in stable noisy conditions and from
23 to 4 during misleading bursts, but delayed genuine-change recovery by
89.6 records and exceeded composite-loss allowances. Its combined criterion
failed. This is a measured stability/adaptation trade-off, not a promoted
replacement for the baseline. Prospective memory preservation and coordination
of provisional local changes with upper interfaces remain separate hypotheses
for a future protocol; neither has been tested by this intervention.

[Experiment 021](results/prospective-memory-v1/findings.md) then tested prospective
memory preservation separately, completing 60 independently audited runs on
2026-10-26. Early snapshots were confirmed in 7/10 pairs per history. Mean
early-return loss improved by .028616 nats, but only 3/10 pairs improved against
either control, below the required eight; the primary criterion failed.
Pre-return and reversal cost guards passed, and every policy reached stable
late prediction and appropriate structure on this batch. Saved traces showed
that archive availability could block fresh adaptation without retrieval.
Memory preservation is now tested, but reliable beneficial recall remains
unestablished. A separate selection/retrieval ablation is the focused next
question; coordination of provisional local changes with upper interfaces
remains untested. Neither intervention has been promoted into the baseline.

[Experiment 022](results/memory-selection-v1/findings.md) completed the separate
selection/retrieval test on 2026-10-26 with 80 independently audited runs.
Four policies isolated stored-but-ignored memory, competition without retrieval,
joint ranking and independent admission. Independent admission improved mean
early-return loss by .045996 nats versus ignoring memory, but only 4/10 pairs
improved, failing the required eight. All four beneficial pairs had preserved
snapshots before simplification, and independent admission matched the ignoring
control until retrieval. Competition alone gave no early-return benefit here.
Reversal costs met the mean allowance but included a larger individual failure.
Every policy achieved stable late validity and structure in this batch.
Capture quality/timing and the relative contributions of restored interfaces
and fitted parameters are now the focused open questions. No revised policy
has been promoted; provisional-local/upper coordination remains untested.

**Closure, 2026-10-26:** the follow-on test round 019–022 is complete, with
320 independently audited runs. The
[closure synthesis](results/consolidated-learner-test-round-synthesis.md)
records the connected findings, the unchanged integrated reference and the
experimental alternatives; the [current evidence map](results/evidence-map.md)
separates demonstrated capabilities from remaining assumptions and failures.
No further experiment is required to close this round. Capture quality/timing,
interface versus parameter reinstatement, and local/upper coordination are
questions for a separate future protocol. Interpretation and controlled
modification may be the next bounded enquiry; meta-learning remains later.
No new benchmark, policy promotion or scaling follows automatically from closure.

**Explicit-role comparison completed, 2026-10-28:** R0 reproduced all 30
saved integrated traces exactly. The 300-run comparison passed independent
audit but failed its empirical adoption gates. Stable exported meanings alone
left the primary representation-error count unchanged; history-guided proposals
helped on average but exceeded cost safeguards. Timing and predictive-update
controls separate those effects. The conditional confirmation seeds remain
unused, and the original integrated learner remains the reference. See the
[findings](results/explicit-roles-v1/findings.md) and
[architecture decision](results/explicit-roles-architecture-decision.md).
The current post covers the existing learner; the next can explain the decision
before examining steering. No steerability experiment has yet been run.

**Memory-control round completed, 2026-10-30:** [Experiment 026](results/memory-control-v2/findings.md)
compared elapsed-time and observation-time forgetting, selective and unconditional
fast-to-slow transfer, permanent slow memory, a single slow store and the original
reference. All 350 runs passed independent audit. Retention and transfer-selection
benefits were measured, but full performance gates failed. In reversal, a fixed
adequacy requirement repeatedly blocked improving transfers into an outdated
slow store. This supplies a focused next question: how can contradicted memory
be weakened, retired or replaced without losing rare, useful knowledge?
The new family retains raw sufficient statistics supporting forms; it does not
yet preserve and revise an autonomous slow repertoire of named forms. No new
baseline, steering capability or learned memory-control policy is established.

**Slow-memory revision completed, 2026-10-30:** [Experiment 027](results/memory-revision-v1/findings.md)
separated relaxed admission from selective weakening of old evidence. All 350
runs passed independent replay. Under relaxed admission, adding weakening
improved late reversal/remap loss in all ten pairs per history and raised final
reversal validity from 5/10 to 8/10. No selective weakening occurred in stable,
brief-reversal or familiar-return histories. The primary early-gain criterion
failed because its measurement window ended before the two-review rule could
affect prediction. That timing error is recorded; the criterion is not rewritten.
Two proposal replicates still lost a correct local form while using a raw bypass
to predict accurately. Next confirmation must predeclare a benefit window after
the intervention can act, with early adaptation costs still measured. No such
confirmation, policy promotion or steerability test had been performed at the
close of 027.

**Fresh memory confirmation completed, 2026-10-30:** [Experiment 028](results/memory-confirmation-v1/findings.md)
kept the learner fixed and evaluated fresh seeds over the complete window after
the first possible intervention. All 350 runs passed independent audit and all
primary criteria passed. Selective weakening improved the declared mean loss by
.033904 nats over admission alone, positive in all ten pairs and five environment
means. Final reversal validity rose from 3/10 to 10/10, with preservation guards
passing. This establishes a bounded benefit of selectively revising slow evidence;
the original and faster-forgetting controls still had lower adaptation loss.
The reference architecture is not automatically replaced. Interpretability and
controlled steering can now build on a tested memory-revision mechanism, with
the existing representation failures and retention/adaptation tradeoffs retained
as evaluation requirements. No steerability or meta-learning result is claimed.

The aim is learning and revising generalisations. Interpretability and
design-led extension follow conditionally; meta-learning remains a later
evaluation on held-out task families. The plan preserves the earlier frozen
protocols and does not assume that combining their mechanisms improves them.

1. Establish useful learning with fixed distinctions and connections.
2. Test relation creation and removal with fixed distinctions, including discovery
   of a newly useful relation and recovery after a relevance reversal.
3. Test changing or creating distinctions where the current representation
   misses a relevant difference, and merging or collapse where a separation
   becomes unnecessary. Splitting is one candidate operation.
4. Compare deterministic and partly random structural proposals under matched
   resource budgets.
5. Compare fixed hyperparameters with regulated or evolved hyperparameters.
6. Compare human-designed, AI-constructed, evolved, and combined approaches under
   comparable evaluation conditions and explicit resource budgets. For an
   emulation aim, include fidelity to the reference system in these comparisons.

Every stage remains within the small-scale research scope and uses the monitored
and controlled trial process above. At each stage, measure useful performance,
memory and computation costs,
adaptation after change, and loss of previously useful behavior. Compare against
the corresponding fixed-structure or fixed-parameter model. Each structural
operation must preserve the chosen representation's validity constraints and
keep delayed consequences attributable across the change, or explicitly record
where attribution is lost. Structural activity alone is not evidence of learning.
