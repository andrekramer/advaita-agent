# 029–031: integrate, stress-test, then exercise bounded steering

2026-11-02. Authorized after the 028 confirmation. No old source or result is
modified. Default architecture remains the original integrated learner.

## 029 — Compatibility and inspectable integration

Provide a common ContinuingLearner around the frozen StructuralLearner and
RevisionLearner. Construction explicitly opts into fast, relaxed or combined
memory (the other frozen policies remain available). Original acquisition stays
in StructuralLearner. The API validates inputs before mutation, advances elapsed
ticks, reviews fresh batches, returns copied inspection state and checkpoints
the wrapper plus engine. The wrapper does not add a learning rule.

Replay all 350 saved 028 traces, including the original reference. Check every
prediction and review, and exact final native engine checkpoint bytes including
all learning costs. Preserve original diagnostic probe calls. Round-trip the new
checkpoint halfway through each replay. No new world generation or training data.
Record per-run digests, coverage and source provenance. Independently verify
coverage/digests against saved artifacts. Fixtures cover rejected operations,
read-only inspection, checkpointing and explicitly logged controls.

Add one narrowly bounded steering operation: halve one slow evidence channel
following the current completed review, with a required rationale and at most
one operation per channel per review. It invalidates that channel's pending
structural/weakening decisions, leaves fast evidence unchanged, refits predictions
and records before/after engine hashes and removed mass. This API is an
engineering affordance; its usefulness requires 031. No external-world action.

## 030 — Remaining memory tradeoffs

After 029 passes, preregister fresh comparisons of original, fast-only,
admission-only and combined variants under repeated prediction reversals,
returning earlier categories and rarely observed distinctions. Preserve all
outcomes, measure prediction AND representation, include context-balanced probes
so rare knowledge cannot disappear in common-context averages. Run the fixed
budget once, then independently audit. No parameter tuning or default promotion.

## 031 — Bounded steering

After 030 is audited, preregister a small paired study of a single evidence-led
weakening intervention versus no intervention and the same intervention applied
to a different channel. Select the intervention from observed review diagnostics,
never simulator truth. Include a stable negative-control history and measure
unchanged local knowledge as well as the changed composite prediction. This
tests a scripted external controller and API, not human interpretability, broad
steerability, meta-learning or safety. A failed performance test still completes
the stage; do not tune or silently substitute a more successful intervention.

Each stage records its own sources, fixtures, budgets, outcomes and audit before
the next stage uses it. Prior evidence and the original baseline remain intact.
