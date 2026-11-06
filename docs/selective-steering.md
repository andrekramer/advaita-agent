# Selective protection and plasticity

Experiment 033 adds an optional experimental `SteerableMemory` class alongside
the frozen learners. It does not change the reference default. Its purpose is to
test a supplied instruction about where learning should remain stable or adapt.

There are two distinct controls:

| Control | What stays fixed or changes | What continues learning |
| --- | --- | --- |
| Lock a local distinction | The current partition of four raw states into categories stays fixed. Structural proposals for that channel stop. | Category probabilities, fast and slow evidence, transfer and automatic weakening. |
| Increase local plasticity | The selected slow store's half-life decreases from 1024 to 128 ticks. | The same predictive updates, structural search, transfer and weakening rules. Fast half-life remains 64. |

The partition lock preserves membership equivalence. Probability-ordered group
IDs can change order; a lock does not fix probability values or their labels.
It also does not establish that a protected distinction is correct. Locking an
incorrect representation can prevent its correction until release.

The prototype configures local channels 0 and 1 only. The composite channel and
its interfaces retain their original learning rules. A local control can affect
later composite learning, but local confidence itself is not an upper input.
This is not arbitrary editing of a hierarchy or freezing an entire long-term
core. The tested notion of plasticity is specifically faster slow-evidence decay.

## Experimental API

```python
from advaita.selective_steering import SteerableMemory

learner = SteerableMemory(acquired_structural_learner)
# Feed observations and complete the current review first.
learner.configure(
    lock=[0], plastic=[1],
    reason="Preserve this distinction while adapting the other")

view = learner.inspect()  # Detached forms, memory masses, controls and pending state.
saved = learner.checkpoint()
learner = SteerableMemory.restore(saved)

# After a later completed review:
learner.configure(lock=[], plastic=[], reason="Release the temporary instruction")
```

One configuration is allowed per review. Each replaces the configuration in full:
empty lists release the controls. Locking/releasing clears structural pending
state for the affected lock channels; probability updates and evidence are not
reset. Plasticity changes take effect at the next tick. Release restores ordinary
learning rules; it does not restore evidence already forgotten. Commands include
reasons, prior settings and the prior checkpoint hash, and survive checkpointing.

## Coherent inspection boundaries

The subclass refits active models once at the end of each review. This makes the
exposed prediction tables consistent with current forms and accumulated evidence,
addressing the snapshot issue found in 032. Within-review comparisons and choices
retain the original algorithm. The study separately compares refresh-only with
the old engine, so refresh cannot be credited to steering.

This is a narrow consistency change to the experimental subclass. It does not
establish that every internal comparison in the old algorithm is free of stale
model effects, nor silently repair earlier experiments. The original continuing
runtime remains as recorded in 029–032.

The [protocol](../experiments/selective_steering_protocol.md) specifies a supplied
protected/flexible channel mapping, fixed control and release times, matched
observations, wrong-channel controls, and independent state replay. It tests
execution and consequences of a known instruction, not autonomous goal selection,
learned control policy or human/LLM interpretation.

The separate [034 extension](coordinated-steering.md) allows composite slow-memory
plasticity as well. Its [factorial results](../results/coordinated-steering-v1/findings.md)
found downstream benefits but no extra primary benefit from joint local plasticity,
with preservation costs. The 033 class and findings remain unchanged.
