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
retention, with a measured adaptation cost. It has not been integrated into
the nested learner, and the protection rule remains constructed.
The [capability consolidation](results/relationships-interfaces-synthesis.md)
records what is learned, what remains supplied, and the unresolved questions.
No automatic progression follows from these completed runs.

## Suggested investigation sequence

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
