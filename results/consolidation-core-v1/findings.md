# Consolidation C0 / 016: a shared core with exact compatibility

Completed 2026-10-22. **The C0 engineering gate passed.** The shared core
reproduced all 380 complete saved traces from Experiments 012–015 exactly.
Thirteen correctness tests and an independent artifact audit passed. No new
learning benchmark was generated or run.

This establishes preservation of earlier behaviour while separating prediction,
structural search, retention policies and state management. It does not improve
the earlier learning results or change any failed criterion. The consolidation
round remains open: C1 and C2 have not run.

## What is now shared

The [architecture specification](../../experiments/consolidation_core_spec.md)
maps capabilities to the new [`advaita` package](../../advaita/). A common
Beta(1,1) conditional-count table supports local forms, selected-coordinate
relationships and nested upper predictions. Input encodings remain explicit.
Search and retention policies preserve the earlier thresholds, proposal order,
tie-breaking and evidence rules.

The continuing [`NestedLearner`](../../advaita/runtime.py) accepts observations
and review batches without receiving world truth, branch names or change
boundaries. It predicts before feedback, updates lower forms before upper
review, and applies ordinary replacement before reclosure. Local protection
and upper reclosure are separate switches. The new protection/reclosure
combination has correctness-fixture coverage, but no empirical interaction
result yet.

State contracts add restricted prediction views, immutable archived predictors,
semantic dependency fingerprints, observation identities and an evidence-use
ledger. Reusing a selection batch across different decisions is explicit;
reusing it as a fresh witness for the same decision is rejected. Main and
selection evidence cannot overlap by identity. These checks rely on callers
assigning identities correctly; they do not detect the same observation
submitted under a different name.

A JSON checkpoint includes models, buffers, proposal decks and random states,
pending challengers, evidence state, counters and event history. Continuation
tests restored both a pending local replacement and a pending upper reclosure,
then required identical subsequent decisions and state. Audit history is kept
separately from the bounded learning buffers.

## Compatibility evidence

| Saved experiment | Complete exact matches | Replayed used label presentations |
| --- | ---: | ---: |
| 012: retained/deleted interface detail | 90 / 90 | 144,000 |
| 013: nested abstractions | 120 / 120 | 253,440 |
| 014: upper reclosure | 80 / 80 | 358,400 |
| 015: local form protection | 90 / 90 | 138,240 |
| Total | **380 / 380** | **894,080** |

Equality covers every field in each saved run: predictions, candidate states,
rankings, acceptance decisions, archive transitions, final state, evaluations,
metrics and costs. Experiments 012, 013 and 015 use the unchanged simulation
drivers with shared-core classes bound into isolated namespaces. All 80 runs
of 014 use the new continuing coordinator, with the historical evaluator kept
outside it. No original source or result was modified.

The independent checker imports no learner code. It compares the complete
compressed replay records against the saved originals, checks coverage and
digests, and recomputes label totals. It also verifies the coordinator's recorded
evidence totals: 3,072 main labels, 1,408 selection labels and 813 events per
014 run, with 384 declared reused selection labels for reclosure. It verifies
those summary records, rather than independently reconstructing the new
ledger's entire history. The existing historical auditors remain the separate
arithmetic checks for the original traces.

## Correctness and resources

The [13 tests](tests.txt) cover joint-only relationships; local split, collapse
and recreation; denied raw reads; changed and returning interface meanings;
frozen snapshots and one-entry eviction; evidence leakage and false witnesses;
earned protection; pending-evidence invalidation; checkpoint continuation;
pure prediction; and preservation of a stale deployed upper predictor.

There was one full compatibility attempt, lasting approximately 104 seconds.
The fixture suite ran once during development and once in that attempt.
The recorded conservative fixture allowance is **18,880 of 20,000 labels**
(9,440 per invocation). It includes generated but unused local labels in
upper-only composition rows and unused fixture rows; that surplus also covers
the duplicate presentations used to compare restored checkpoints. Candidate
refits and repeated scoring of existing evidence are computation, not fresh
observations. Carry the full recorded 18,880 forward against the round's fixture
ceiling, leaving 1,120. Saved-label replays are accounted separately above.
New benchmark labels: **zero**. Reserved 600/700-series seeds were not used.

## What remains open

The reusable archive primitive is not yet connected to nested capture and
retrieval. Legacy 012 still captures its prototype at a supplied boundary.
Learned dependency selection, adequate local collapse in a live consumer, and
capture-on-reduction remain C2 work. The deterministic collapse fixture shows
that the existing local language can split, collapse and recreate; it does not
establish reliable simplification under noise or parity with every earlier
form-learning experiment.

The next stage is C1 / proposed Experiment 017: the fixed 2×2 comparison of
immediate versus earned local protection and opening versus reclosure. It needs
a complete frozen protocol and independent auditor before any new seed is run.
C2 remains conditional on its stated gate. Architecture, candidate languages,
supervision, schedules and learning rules are still supplied. Meta-learning,
learned depth, temporal folds, eigenform recovery, user interpretability and
safety advantages remain untested.

## Reproducibility

From the repository root, verify the saved record without running learners:

```sh
python3 checks/audit_consolidation_core.py
```

For a separate reproduction, the replay runner refuses to overwrite an existing
output directory:

```sh
python3 checks/consolidation_compatibility.py --output /tmp/advaita-c0-replay
```

The original record consists of the [source manifest](manifest.json),
[compatibility summary and per-run digests](compatibility.json),
[complete compressed traces](replayed-runs.jsonl.gz), [test log](tests.txt) and
[audit result](audit.txt). The planning document and core specification remain
frozen in the manifest; current stage status is recorded here and in the roadmap.
