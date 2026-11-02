# 029 — Optional memory integration

Completed 2026-11-02. **All 350 saved 028 runs reproduced exactly** through the
common runtime: every prediction and review and the complete native engine
checkpoint, including learning costs. Each run was checkpointed and restored
midway. The independent artifact/coverage audit passed. Runtime replay took
287.941 seconds within the 900-second ceiling.

`advaita.continuing.ContinuingLearner` defaults to the original reference. An
explicit memory argument selects a frozen weighted policy. Acquisition remains
in StructuralLearner. Inspection returns copies; outer checkpoints include
clock, review history and explicit controls, plus the native engine checkpoint.
The API validates malformed inputs and repeated reviews before mutation.

A single `weaken_slow` operation halves one channel's retained evidence after
the current review, with an explicit rationale, before/after state hashes and
removed mass. It leaves fast evidence unchanged and invalidates that channel's
pending decisions. One action per channel/review is allowed. This is an API
capability, not yet evidence of useful steering. There is no protection/freeze
operator in this minimal integration.

This is integration by composition around unchanged engines, not a new unified
learning algorithm. The baseline retains its windows/archive; the optional
memory variant retains its different weighted fitting and no archive retrieval.
Raw sufficient statistics still exist behind coarse prediction interfaces.
The new interface is not a security boundary or human-interpretability result.

No new training data were generated. Compatibility re-presented 1,890,560 saved
labels; engineering fixtures re-presented another 294 saved labels. Frozen
sources and prior results were preserved. See [plan](../../experiments/memory_integration_plan.md),
[compatibility](compatibility.json), [audit](audit.json), [fixtures](fixtures.json)
and [manifest](manifest.json).
