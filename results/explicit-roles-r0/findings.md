# R0 / Experiment 023: implementation contracts

Completed 2026-10-28 before reserved comparison seeds were generated.

The B64 compatibility implementation reproduced all 30 integrated Experiment
019 runs exactly: predictions, selected models, event traces, resource counts,
and serialized checkpoint hashes. This checks that extracting a new candidate
implementation did not change the reference behavior. It is replay of saved
evidence, not new evidence for learning performance.

Eight synthetic contracts cover world generation and regime boundaries; all
six policies' full independent reconstruction; checkpoint continuation and
atomic rejection of reused evidence; stable group meanings during probability
crossing; bounded history and deterministic priority arithmetic; group-only
predictive refitting and empty-history equivalence; two-witness collapse,
recreation, frozen memory and incompatible archive rejection; paired metric
and gate arithmetic; and measurement windows and censored recovery. Some of
these checks share a test method. The independent replay imports no learner
or experiment policy code.

The fixture log preserves three attempts. Attempt 01 found two fixture issues:
an exact floating-point equality assertion and a review invoked without local
training data. Attempt 02 passed all seven non-summary contracts and exposed
a reporting variable overwritten by the history-gain loop. The fix changes
only the displayed representation-reduction fraction; the primary Boolean
checks had already used the correct numerator. Attempt 03 reran that sole
failed summary contract, checking unchanged test-method syntax and unaffected
source hashes against saved attempt-02 sources. No learning data were needed
for the final arithmetic check.

Cumulative fixture charge: **3,516 labels**, including conservatively charged
failed work, against the 5,000 ceiling. No reserved outcome was inspected during
these repairs. All earlier frozen artifact hashes remained intact. The
[completion record](completion.json), [compatibility proof](compatibility.json),
and fixture attempts retain the detailed evidence.

The implementation contract and comparison protocol are now frozen for R1.
Passing R0 establishes implementation consistency, not an architectural benefit.
