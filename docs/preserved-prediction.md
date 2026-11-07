# One preserved downstream predictor (experimental)

Study 036 adds an optional frozen prediction route around the continuing
schema-34 learner. Active learning, structural search, weakening and migration
continue identically whether the archive is discarded, stored or used.
The original default remains unchanged.

A single post-review predictor is nominated at tick 384. The copy contains its
upper probability table, specification and consumed local group meanings.
It is confirmed on the fresh batches at 448 and 512 if both losses are <= .55
and the meanings remain compatible. Failed candidates are removed. Confirmed
copies are never updated or replaced. Capture timing is supplied.

From 576, fresh reviews score the archive and the pre-review active predictor.
An archive can supply the composite output for the next interval if its loss is
<= .55, improves on the active predictor by at least .02, and its meanings match
before and after ordinary review. The active learner still receives every label.
No evidence or parameter copy is injected into it; no selection decision is
blocked by memory. Admission is not allowed on the confirmation batch.

Compatibility is also checked immediately before each main prediction, after
normal decay/refitting and before its label is added. Abstract ports bind exact
state-to-group maps; raw ports bind the fixed raw alphabet. If a dependency no
longer matches, that prediction falls back to the active model. This guards
meaning changes but does not detect every change in the predicted relationship.

The three policies are `discard`, `shadow`, and `recall`. After qualification,
discard uses a second active score as a query-count-matched dummy; it holds no
deployable past model. Shadow computes the same archive scores as recall but
never routes output. Query counts match; storage capacity intentionally differs.

`PreservedPrediction.checkpoint()` includes the active learner, immutable slot,
corroboration state, admission state and audit events in schema 36. Restoring
that checkpoint preserves both partial qualification and current authorization.
The separate `active_predictions()` method exposes the continuing predictor;
`predictions()` exposes the routed output. Study traces keep both. Inspection
inherited from schema 34 describes the active learner; memory events and the
schema-36 checkpoint provide the separate archive record.

This is a small experiment in prediction reuse, not a general memory API or a
claim that recall improves learned representations. Delayed compatibility and
stale authorization are measured failure modes.

- [Findings](../results/preserved-prediction-v1/findings.md)
- [Frozen protocol](../experiments/preserved_prediction_protocol.md)
- [Implementation](../advaita/preserved_prediction.py)
- [Independent verifier](../checks/audit_preserved_prediction.py)
