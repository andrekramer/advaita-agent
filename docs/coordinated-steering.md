# Testing local and downstream plasticity together

Experiment 034 extends the 033 experimental class with permission to change the
composite slow-memory half-life. Local category locks and all learning rules
remain inherited from 033. The original default learner is unchanged.

| Policy | Stable local form | Changing local slow half-life | Composite slow half-life |
| --- | --- | ---: | ---: |
| U: unsteered | Unlocked | 1024 | 1024 |
| P: protection only | Locked | 1024 | 1024 |
| L: local plasticity | Locked | 128 | 1024 |
| D: downstream plasticity | Locked | 1024 | 128 |
| C: coordinated plasticity | Locked | 128 | 128 |

Fast evidence still has a 64-tick half-life. Both shorter slow-memory settings
are temporary. Releasing them restores ordinary learning rates, without
restoring evidence already forgotten or resetting the structural search.

```python
from advaita.coordinated_steering import CoordinatedMemory

learner = CoordinatedMemory(acquired_structural_learner)
# After observations and a completed review:
learner.configure(
    lock=[0], plastic=[1, 2],
    reason="Protect local0 while adapting local1 and its composite predictor")
# After a later completed review:
learner.configure(lock=[], plastic=[], reason="Release the temporary instruction")
```

Channel 2 can become more plastic; it cannot be locked by this API. The command
specifies the entire configuration. Inspection includes the current settings,
control history, evidence masses and pending decisions. The new class uses
checkpoint schema 34; it does not alter earlier checkpoints or runtime classes.

The experiment changes the whole composite slow store, not a selected relation
inside that store. Its channel mapping, timing and intended output are supplied
by the experimenter. “Coordinated” here means a simultaneous external instruction;
it does not mean that the learner detects dependencies and regulates plasticity.

The decisive comparison is C against D: does local plasticity add benefit when
the composite predictor is already more plastic? C against L measures the value
of adding downstream plasticity. P, L, D and C also separate additive effects
from an interaction. If their expected losses are denoted by the same letters,
the interaction gain is `(D − C) − (P − L)`. A positive value indicates that
local plasticity helps more in the presence of downstream plasticity.

All conclusions are limited by returning-knowledge, stable-history, collateral
and final-validity checks in the [frozen protocol](../experiments/coordinated_steering_protocol.md).
A benefit against one comparator is not a general steerability result.

[Completed results](../results/coordinated-steering-v1/findings.md): 150 audited
runs. C did not beat D in the primary window (16 ties, four losses); D beat P in
all 20 changing pairs. C passed the comparisons against L and U but failed
preservation guards. The experimental extension is not promoted to a default.
