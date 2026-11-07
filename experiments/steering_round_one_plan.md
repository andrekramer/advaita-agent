# First steering round: intended effects, limits and withdrawal

Status: completed 2026-11-06. See the [round synthesis](../results/steering-round-one-synthesis.md) and [final study](../results/recall-withdrawal-v1/findings.md). Experiments have stopped for the goals review. The original planning text follows.

2026-11-06. Direction agreed: complete a bounded first round of steering tests,
then review the evidence and choose the next research goals. This is a round
plan, not a frozen experiment protocol. No new benchmark has started under it.

## What the round should answer

Can an inspectable instruction selectively change learning or prediction, produce
the intended effect, limit harm elsewhere, and relinquish control when withdrawn?

Keep three conclusions separate:

1. **Execution:** the requested control changes exactly the specified mechanism.
2. **Usefulness:** the change helps the intended outcome under declared conditions.
3. **Limits:** inappropriate instructions, delayed feedback, downstream effects
   and loss of previously useful behavior remain visible and measurable.

An obeyed instruction need not be useful. A failed utility criterion need not
mean that the command was ignored. Finishing this round means answering the
bounded questions, not continuing until every intervention wins.

## Existing evidence belongs in this round

The recent studies already provide component-level steering evidence. Do not
repeat them or present the round as if no steering had been tested.

| Steering question | Existing evidence | Remaining boundary |
| --- | --- | --- |
| Can inspection identify relevant effects? | [031](../results/memory-steering-v1/findings.md), [032](../results/introspection-v1/findings.md): some useful intervention/effect forecasts, with failed full criteria. | Supplied dependency knowledge and scripted interpretation; human/LLM usability untested. |
| Can one distinction be held while another remains plastic? | [033](../results/selective-steering-v1/findings.md): successful local protection/plasticity, wrong-channel and release controls. | Composite benefit and preservation failed. A partition lock does not freeze probabilities or all memory. |
| Where should plasticity act? | [034](../results/coordinated-steering-v1/findings.md): downstream plasticity helped; joint local plasticity added no primary benefit. | No universal best intervention or learned coordination. |
| When should a plasticity boost end? | [035](../results/temporary-plasticity-v1/findings.md): duration and evidence-based closure comparisons. | Restoring stability did not solve returning-knowledge costs. |
| Can preserved knowledge be used without changing active learning? | [036](../results/preserved-prediction-v1/findings.md): actual immutable-predictor recall, with active-learning parity. | Early recall was inconsistent; stale authorization caused a cost after rechange. |

These studies used successive optional variants. Their positive findings must
not be combined into a claim that one evaluated configuration has all their
benefits. Preserve their frozen protocols, outcomes and failed criteria.

## Freeze the scope

Retain the current representation language, one-slot memory capacity, learning
rules and small constructed worlds. Use existing lock, plasticity and release
evidence as completed components. The final study extends only control over
whether preserved prediction may supply output.

Keep input-encoding changes, larger archives, new category languages, larger
benchmarks and meta-learning for the subsequent goals review. These may be
important, but they are not prerequisites for closing this steering round.

## Final study: withdraw recall when it becomes unhelpful

Proposed study 037, bounded to at most 240 fresh runs. Prepare and freeze its
exact protocol, implementation, fixtures and independent auditor before fresh
outcomes. One fresh seed batch; no adaptive threshold search or extra seeds.

Start from the unchanged 036 capture, compatibility and active-learning rules.
The archive still cannot veto updates or inject evidence. Separate explicit
external control from an evidence-responsive controller:

| Condition | Purpose |
| --- | --- |
| Shadow/no deployed recall | Existing no-recall prediction control; keep matched capture and diagnostic work. |
| Current review-interval recall | Frozen 036 behavior; measures the cost of its authorization interval. |
| Explicit recall block and release | Test a supplied instruction that overrides fresh admission until released. |
| Evidence-triggered withdrawal | Test whether observed errors can shorten authorization without waiting for the next ordinary review. |

The explicit instruction must be scheduled identically across histories and
logged with its reason, source, prior settings and state hashes. If its schedule
is chosen relative to the constructed change, call that supplied timing
knowledge. Its usefulness must not be credited to autonomous detection. After a
release, future fresh evidence must authorize recall again; releasing a block
must not silently resume stale authorization.

For evidence-triggered withdrawal, define one short observation window and one
loss-comparison threshold before outcomes. Use active and archived predictions
made BEFORE each label, then use the observed label to decide whether to withdraw
for subsequent predictions. Never revise the prediction whose label triggered
the decision. Keep ordinary learning and review cadence unchanged. Specify reset,
missing/incompatible evidence, reauthorization and checkpoint behavior explicitly.
No clean target, change marker or future observation enters the controller.

Reuse the six kinds of history from 036 with fresh seeds: stable, familiar
category return, familiar polarity return, persistent category change, persistent
polarity change, and a different-category return. With five environment seeds,
two proposal seeds and four conditions this is 240 runs. Shared histories and
proposal draws remain correlated. The exact resource ceilings, timing choices,
comparison thresholds and success criteria belong in the frozen protocol.

### What must be measured

- **Command fidelity:** blocked recall never supplies output; active learning
  continues; release permits only a later properly authorized use. Restore,
  command precedence, duplicate commands and copied inspection behave as defined.
- **Intended utility:** shorter exposure to stale recall after rechange, including
  the first 64 observations where 036 incurred its additional cost.
- **Preservation of useful recall:** early and whole familiar-return gains are
  retained within declared tolerances. Stopping everything is not a successful
  memory controller merely because it prevents stale-memory errors.
- **Collateral costs:** all three outputs, stable/permanent/altered-return tasks,
  individual worst pairs and final active/deployed validity.
- **Interpretability of the intervention:** each executed instruction has a
  readable before/after account of what was allowed, blocked, actually used and
  later released. This is auditability, not yet a human comprehension study.

The primary empirical comparison should be evidence-triggered withdrawal versus
current recall, with explicit preservation requirements and the shadow control.
The explicit block/release arm separately establishes execution and consequences
of a supplied command. Do not collapse these into a single success claim.

The experiment must preserve exact underlying active-learning parity. If that
fails, resolve the engineering issue separately before interpreting utility.
Account for added monitoring work and all generated outcomes. Do not retune the
withdrawal rule on its fresh results, even if the full criterion fails.

## Close the round after that study

Produce one synthesis linking the existing evidence and the final study. It
should contain:

1. A control inventory: mechanism affected, granularity, available inspection,
   command conditions, persistence, release semantics and known failure modes.
2. A result matrix separating execution, local effects, downstream usefulness,
   preservation and withdrawal. Include failed and adverse comparisons.
3. An implementation map identifying which optional class supports each control,
   rather than implying that the original default already implements everything.
4. A decision for each control: retain as experimental, require further evidence,
   revise, or set aside. No automatic default promotion.
5. A concise account of supplied assumptions and the claim the round supports.

Then stop experimentation and review with the user. No additional memory design,
confirmation round or broader benchmark is an automatic continuation.

## Questions for the subsequent goals review

Choose priorities after seeing the closure, rather than committing now:

- Is a coherent operator-facing inspection/control interface the next useful
  step, followed by a bounded human or LLM steering study?
- Is recall limited mainly by restoring compatible meanings, by admission and
  withdrawal, or by the current task construction? Which deserves the next test?
- Should a small independent task family challenge the current positive findings?
- Which mechanism is sufficiently supported to consolidate into a maintained
  optional configuration, and which should remain a research branch?
- Is there enough stable evidence to begin learning control policies and testing
  transfer of those policies, or is meta-learning still premature?

The intended first-round claim is **inspectable, selective control with measured
benefits and limitations in small learning systems**. Reliable general steering,
human interpretability, autonomous goals, meta-learning and a safety advantage
remain separate questions.
