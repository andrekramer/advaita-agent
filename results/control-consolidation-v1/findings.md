# 038 — Memory, inspection and steering consolidation

Completed 2026-11-10. **Engineering consolidation passed on the first verification
attempt.** All240 saved 037 trajectories reproduced exactly through the optional
`ControlledLearner` interface. Six deterministic interaction/contract tests also
passed. The original reference remains the default. No new empirical learning or
steering advantage is claimed.

## What is now incorporated

One [supported optional interface](../../docs/controlled-learner.md) combines the
already existing schema-37 path: combined fast/slow weighted evidence, coherent
forms and prediction tables, local partition protection, selected plasticity,
one preserved predictor, recall permission and optional evidence withdrawal.
Composition leaves all native implementation files untouched.

The wrapper adds validated entry points, detached unified inspection, explicit
active/deployed prediction provenance, reason/source command records, native
before/after hashes and a checkpoint containing both native and interface state.
Its own default is shadow recall; enabling recall is explicit. The older
`ContinuingLearner` reference default is unchanged.

Inspection distinguishes the last observed prediction's source from the output
source currently permitted. A prediction can have come from recall even though
the evidence from its outcome has now withdrawn authorization. It also exposes
input meanings, memory masses, pending decisions, controls and the inherited
capture/confirmation schedule.

## Verification

The [protocol](../../experiments/control_consolidation_protocol.md) was written
before execution. The [recorded attempt](attempt-01.json) includes source hashes,
test output and counts. Run again with:

```sh
python3 checks/test_controlled_learner.py
```

The check creates a new numbered attempt without overwriting earlier results.

| Check | Result |
| --- | --- |
| Saved trajectories | 240/240 exact native replay |
| Observations | 491,520 deployed and active predictions checked |
| Reviews | 7,680 review outcomes checked |
| Midway restoration | 960 exact wrapper round trips and original native hashes |
| Final native state | Exact in all 240 trajectories |
| Recall-mode separation | Active predictions, reviews and learning-state projections equal within all 60 matched groups |
| Frozen artifacts | All 1,562 unique manifest/completion paths unchanged before and after |
| Contract fixtures | Six tests passed |

Replay also compared prediction-source events, native configuration and recall
commands, saved learning inspections and input-core immutability. The source
trajectories were independently audited in 037. This consolidation compares to
those saved results and uses deterministic contract checks; it is not a new
independent reimplementation of the learner or a fresh utility trial.

The contract fixtures establish:

- Invalid public observations, reviews and commands leave state unchanged.
- Inspection returns detached copies and diagnostic predictions do not change
  subsequent learning. Current local and upper tables match pure fits from the
  stored evidence, including after reviews.
- Protection and selected plasticity coexist and survive restoration. Releasing
  them changes settings without restoring evidence; subsequent reviews can once
  again consider changes to the released partition.
- A recall block overrides a genuinely admitting review while protection and
  plasticity remain active. Release leaves the route off until a fresh review.
- Incompatible meanings prevent archived output; restored meanings alone do not
  override an explicit block. The isolated meaning fixture substitutes a mapping
  deliberately; it is not evidence of a newly learned representation.
- A partial monitoring window survives a checkpoint. The16th recalled prediction
  can trigger withdrawal, with the next prediction coming from the active learner.

Verification used 2,211,840 reused scalar-label presentations and 1,914 synthetic
fixture scalar-label presentations. No fresh random labels or worlds were
generated. Saved acquisition checkpoints were restored rather than retrained.
Total verification time was 317.713 seconds, below the 900-second ceiling.

## Scope and decision

The native capture at 384, confirmation at 448/512 and admission from 576 remain
fixed. Selective weakening still uses its inherited review spacing and thresholds.
This is a supported interface for that bounded configuration, not a general
memory scheduler. Native cost counters exclude wrapper overhead and diagnostic
prediction queries.

The earlier one-shot halving command, temporary-plasticity closure heuristic,
alternative archive engines, arbitrary relation edits and policy changes during
a trajectory are deliberately excluded. Their interactions have not become
validated merely because other controls share an interface.

The earlier failed empirical criteria remain failed. Exact replay preserves those
failures along with the successes. Consolidation does not establish beneficial
human/LLM intervention, safety, broader task transfer or meta-learning. It supplies
a stable optional implementation on which those questions can later be tested.

**Close this consolidation round.** No policy is promoted and no next experiment
starts automatically. The next choice can be an operator-facing comprehension
study or an independent task family, with a separate protocol.
