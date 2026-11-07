# Recall permission and withdrawal (experimental, 037)

`RecallWithdrawal` extends the optional schema-36 preserved predictor. Active
learning and capture are unchanged. Its new controls affect only permission to
use frozen predictions. The original default remains unchanged.

```python
from advaita.recall_withdrawal import RecallWithdrawal

learner = RecallWithdrawal(acquired_structural_learner, 'command')
# After a completed labelled observation:
learner.set_recall_block(
    True, reason='Temporarily suspend this stored predictor', source='operator')
# After a later completed labelled observation:
learner.set_recall_block(
    False, reason='Permit fresh consideration of recall', source='operator')
```

A block overrides subsequent admissions. Both commands clear existing recall
authorization and partial monitor evidence. Release allows a later fresh review
to authorize recall; it does not resume old permission. Commands apply to future
predictions and never rewrite the observation that preceded the command.
A reason/source and a boolean state are required; duplicate commands at the same
tick and commands after missing labels are rejected without mutation.

The `evidence` policy additionally checks non-overlapping windows of 16 consecutive
predictions actually supplied by recall. It compares observed log losses of the
archived and active predictions, both recorded before their labels entered
learning. If the archive is worse by more than .02 nats, authorization ends after
that observation. Subsequent output comes from the active learner until a later
fresh ordinary review admits the archive again. No phase marker or target truth
is used. The window resets on review, command, incompatibility, non-recall or
missing labels. A noisy window can withdraw useful recall; this is measured.

`current` keeps the previous authorization behavior and `shadow` never deploys
recall. All policies compute the additional archived monitoring prediction when
a confirmed slot exists. Only `evidence` uses the monitor to withdraw permission.

`inspect_steering()` returns a detached record of permission, authorization,
confirmation, compatibility, partial monitoring, commands and decisions. Inherited
`inspect()` still describes active learning. Schema 37 checkpoints preserve both.
Logs support tracing instructions and their consequences; this is not yet a test
of human comprehension, an interface usability study or a safety guarantee.

The experiment's explicit command arm uses supplied timing relative to the
constructed change. Treat its execution and benefit separately from automatic
evidence-driven withdrawal. The tested permission concerns one frozen composite
predictor, not arbitrary parts of a neural network or individual relationships.

- [Protocol](../experiments/recall_withdrawal_protocol.md)
- [Findings](../results/recall-withdrawal-v1/findings.md)
- [First-round synthesis](../results/steering-round-one-synthesis.md)
