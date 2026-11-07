# Temporary downstream plasticity (experimental, study 035)

The optional `TemporaryPlasticity` controller wraps the unchanged
`CoordinatedMemory` learner. Its question is whether ending a downstream
plasticity boost earlier can preserve adaptation while improving later recovery.
The original learner and default configuration are unchanged.

All arms hold the supplied stable local partition from the completed review at
512 through the completed review at 1024. Local slow evidence stays at half-life
1024; fast evidence stays at half-life 64. Only composite slow evidence has a
shorter half-life during a boost. Ending a boost changes future decay; it does
not restore a previous predictor or its numerical evidence.

| Policy | Boost duration |
| --- | --- |
| P | None |
| D128 | 128 ticks |
| D256 | 256 ticks |
| D512 | 512 ticks |
| G | Two consecutive adequate fresh reviews, or the 1024 ceiling |

For G, adequacy means observed mean composite log loss <= .55 nats. The controller
scores the deployed predictor before local/upper review and before using the
batch labels to fit or select models. It records predictor and batch identities,
predictions, loss, streak and before/after learner hashes. The ordinary review
then proceeds, using that same batch. Utility is evaluated on later observations.
All arms compute the diagnostic, but only G uses it to change the boost duration.

A failed review resets the streak; a successful pair closes only once. No
reopening is allowed. The supplied deadline overrides the reason for a closure
at 1024: that event is recorded as ceiling closure. Partition protection is
released at 1024 regardless of boost duration. A local lock protects the partition,
not group ordering, probability estimates or ordinary evidence updates.

`checkpoint()` serializes the schema-34 learner and controller state together
under schema 35. Restore the entire bundle to resume a streak or a previously
closed boost. Saving only the learner loses the controller history. The runner
checks round trips at 576 and 768, and the auditor reconstructs both states.

This is a bounded experimental controller with a supplied task role, opening and
deadline. It is not a general scheduling API, autonomous control or meta-learning.
The independent study tests its preservation costs as well as adaptation benefits.

- [Protocol](../experiments/temporary_plasticity_protocol.md)
- [Saved-result diagnosis](../results/downstream-retention-diagnosis/findings.md)
- [Findings](../results/temporary-plasticity-v1/findings.md)
- [Controller](../advaita/temporary_plasticity.py)
- [Independent auditor](../checks/audit_temporary_plasticity.py)
