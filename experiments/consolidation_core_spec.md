# Consolidation C0 / 016: shared-core specification

Started 2026-10-22 under the [consolidation plan](consolidation_round_plan.md).
This stage establishes implementation compatibility and state contracts. It
does not sample a new benchmark or revise any completed experiment's criteria.

## Implementation decisions fixed before compatibility execution

Create an `advaita` package with no runtime imports from experiment or audit
modules. Share a Beta(1,1) conditional-count table across local partitions,
selected-coordinate relationships and nested upper tables. Keep their input
encodings explicit. Preserve arithmetic order, tie-breaking, candidate ordering
and legacy count layouts so comparison can require exact JSON equality.

Separate prediction models from policies. Immediate local improvement,
earned/uniform protection, failure-triggered upper replacement, reclosure,
and retained/deleted projection memory remain named policies. Their thresholds
and rules remain fixed. Legacy complexity penalties are preserved only in
projection compatibility; they do not silently enter the nested learner.

Provide restricted observation views for both projection and nested consumers.
The restriction is a prediction API contract, not secure process isolation.
Provide explicit immutable archive snapshots, semantic dependency fingerprints,
an evidence-use ledger and a JSON checkpoint for a continuing nested learner.

The continuing learner executes prediction before feedback, lower updates
before upper preparation, and ordinary upper replacement before reclosure.
It exposes no branch, ground-truth, phase or evaluator interface. Its event log
records observation identities and intentional reuse of selection evidence.
Existing serialized trace layouts remain unchanged for compatibility adapters.

## Capability map

| Capability | Shared implementation | Verification |
| --- | --- | --- |
| Conditional prediction | `advaita/models.py` | All 012–015 predictions and fitted states |
| Local grouping and proposal selection | `advaita/local.py` | 013–015 full decisions; split/collapse fixtures |
| Joint feature relationships | `advaita/projection.py` | 012 acquisition plus XOR-only interaction fixture |
| Restricted prediction access | `advaita/models.py` | 012–014 read counts and denied-access fixtures |
| Retained/deleted predictor | `advaita/projection.py` | Every 012 archive/source transition |
| Protected replacement and reclosure | `advaita/policies.py` | Every 014–015 evidence transition |
| Meaning compatibility and provenance | `advaita/state.py` | Returning mappings, stale archives, leakage and eviction fixtures |
| Continuing composition and restart | `advaita/runtime.py` | Mid-witness JSON checkpoint/continuation and event-order fixtures |

## Compatibility method

Load the saved observation streams and complete traces of 012, 013, 014 and
015: 90 +120 +80 +90 =380 runs. Bind their read-only simulation/evaluation
drivers to the new learner classes in isolated namespaces. Never patch the
original files or execute their generators. Reusing a driver keeps the original
curriculum and evaluation; the models and decisions must execute in the new
package. Explicitly assert which implementations are bound.

Require exact equality of the full JSON result for each run, including all
proposal states, selected winners, decisions, observations of archive state,
predictions, evaluations, metrics and counted costs. Hash both the shared code
and saved source/result dependencies. An independent checker verifies the
record's per-run digests against the original traces and checks coverage and
accounting. The historical independent auditors remain the arithmetic evidence
for those traces; compatibility is not an independent replication of learning.

If arithmetic or decisions differ, report the first differing path and repair
the refactor. This stage may repeat compatibility checks because its target is
preservation of already-observed behaviour; those replays are not fresh learning
benchmarks. Record attempts. Never select a subset of successful runs.

## State and meaning

Archive snapshots own immutable serialized predictive state. Compatibility is
based on consumed port domains and exported membership maps, not revision
numbers. A newer revision with exactly restored mappings can reuse a snapshot;
the same numeric labels with changed membership cannot. The archive holds one
entry and reports displacement. Retrieval returns a copy and does not learn.
It is an eligible candidate, not automatically a deployed prediction.

Record main and selection observation IDs separately. Candidate fitting may
reuse main records but cannot use selection records; a selection batch can be
used by several declared decisions with each use recorded. These identities
refer to labelled observations, not to encodings or hypothetical independent
evidence. The ledger is audit metadata, not an additional training buffer.

The checkpoint includes deployed tables, buffers, local decks/RNG states,
protection flags, frozen challengers, upper reclosure evidence, counters and
event/evidence history. Restore must reproduce subsequent predictions and
decisions with the same incoming observations. No world state belongs in it.

## Deliberate limits

Legacy 012 still captures its prototype at its supplied acquisition boundary;
the shared archive primitive does not retroactively make that event learned.
C0 does not integrate projection archive selection into the nested loop.
Nested capture-on-reduction, dependency selection and adequate local collapse
remain C2 changes. The core supports the existing collapsed partition, but the
legacy local acceptance rule is not replaced by a new simplification rule.

Core fixtures test generic fingerprint/ledger contracts. Legacy policies keep
their existing trace-compatible evidence layout. The runtime adds auditable
label identities around those policies; it does not claim that old experiments
used these records or solved arbitrary semantic correspondence.

Eigenforms remain a conceptual lens, with no new mathematical or empirical
claim in this stage. Fixed-point recovery, user interpretability, steering,
meta-learning and safety improvements are not C0 outcomes.

## Completion record

Save `results/consolidation-core-v1/` with the compatibility coverage, per-run
reference/replay digests, resource accounting, test evidence, source manifest
and findings. Count saved-label replays separately from synthetic fixtures and
new benchmarks. No reserved 600/700-series benchmark seeds are used in C0.
The next experiment, 017, still requires its own complete frozen protocol.
