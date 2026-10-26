# Experiment 018 / C2: integration works mechanically, but reliable consolidation is unestablished

Completed 2026-10-23. **The primary criterion failed.** All 120 runs completed
within the frozen budget and passed independent reconstruction of their
streams, decisions, predictions, archive provenance, complete checkpoints,
evidence ledgers, evaluations and costs. No benchmark was repeated or tuned.

The integrated learner completed the required trajectory in **0/10 form-return
runs, 3/10 detail-return runs and 3/10 reversed-detail runs**, requiring at least
8/10 in each. Prediction frequently recovered without the intended structural
reduction. Retained and deleted-memory variants produced identical prediction
sequences in every paired run; no archive was accepted.

This completes the bounded consolidation round with a negative reliability
result. It does not establish successful consolidation of all capabilities.

## The combined system

The [frozen protocol](../../experiments/structural_consolidation_protocol.md)
extends the shared core with selected upper dependencies, adequate local
collapse, adequate interface reduction, and one frozen archive captured when
a reduction is accepted. Ordinary improvements take priority over pending
reductions. Two fresh adequate witnesses are required for reduction; archive
use requires compatible consumed meanings and fresh predictive improvement.

The same continuing learner encounters three phases of 240,288,240 records.
Forms or useful detail disappear in the middle and return in the last phase;
the reversed history returns a changed detailed relationship. Changes occur
between reviews, without resets or regime signals. Controls delete the hidden
predictor, expose both raw inputs throughout, or freeze lower partitions.
The [implementation](../../advaita/structural.py) supplies these operators; it
does not learn its architecture, proposal language, thresholds or learning rule.

## Correct prediction and appropriate structure separated

| Integrated learner | Valid prediction at 240 / 528 / 768 | Full minimal endpoints | Complete trajectory |
| --- | --- | --- | ---: |
| Form and relation return | 10 / 10 / 8 | 9 / 2 / 0 | 0/10 |
| Detail returns | 9 / 10 / 10 | 9 / 3 / 10 | 3/10 |
| Detail returns reversed | 9 / 10 / 10 | 9 / 3 / 10 | 3/10 |

Every count is out of ten paired runs. Full minimal endpoints additionally
require the appropriate local partitions and selected interface, with evaluator
checks of sufficiency, relevance of retained inputs and lack of benefit from
adding discarded raw information. Those checks are diagnostics, not feedback.

In the forms history, four of ten runs collapsed and recreated the affected
local form. Four removed and subsequently restored its upper dependency. Only
two achieved both required operations, and neither completed the full minimal
trajectory. At the end all ten had the correct local partitions, but all still
exposed raw detail; eight had valid predictions. Recreating the form therefore
did not reliably return the parent to the intended abstraction.

In the detail histories, all ten eventually regained valid prediction and the
required detailed interface. The main structural bottleneck was the middle
phase: only three returned to a valid coarse interface before detail reappeared.
The same three paired runs passed in both histories, which share all experience
through record 528. These are not six independent successes.

Raw access often bypassed unnecessary or missing abstraction. It would be
misleading to assess the scheme from final prediction scores alone.

## What happened to memory

The memory-benefit criteria failed: mean early-return gain over deletion was
**zero**, and **0/10 pairs** improved. Prediction paths were identical between
integrated and delete variants across all three histories. The reversed-return
cost guard passed with zero cost, but this provides no evidence of successfully
using or selectively rejecting an otherwise useful restored predictor: no
archive was deployed anywhere in the benchmark.

The provenance record reveals a concrete capture issue. All three integrated
detail-history captures occurred at review **448**. Their fitted construction
windows were **records 257–448**, entirely inside the no-detail phase. The
exposed predictor had already been refitted on that phase before it was frozen.
It preserved the raw representation but not a fitted table maintained from the
earlier detailed phase. These are direct trace facts; the broader explanation
of retention failure remains a hypothesis requiring a separate test.

Archive fingerprints did distinguish changed meanings. In the integrated
forms history, nine archive-review occasions were incompatible and eleven
were compatible and eligible for ranking. In the detail history, fifteen
occasions were compatible and eligible. Some archives won the main-data ranking,
but none passed ordinary deployment. Compatibility is consequently only one
part of useful memory; capture timing and preservation during adaptation remain
unresolved design questions. The [derived diagnostics](diagnostics.json) record
prediction equality and capture-window provenance without introducing new
success criteria.

## Controls and costs

All non-raw variants transferred to unseen compositions in 10/10 seed pairs;
the raw table passed in 0/10 under the restricted representative curriculum.
This is useful transfer within a supplied abstraction language, not a claim of
general learning. After seeing all contexts, the raw control often predicted
well, and had lower early-return observed loss than integrated learning in all
three histories. Its greater exposure has both costs and benefits.

Integrated mean parent raw reads during the 288-record hidden phase were
230.4 in forms and 264.0 in each detail history, versus 576 for the raw control
(two reads per record). Thus the declared read-saving criterion passed, despite
unreliable return to the smallest interface. Raw observations remained available
to lower modules and search; this is not reduced sensing or security isolation.

Freezing lower partitions still allowed valid composite prediction at the
middle forms endpoint in 10/10 runs, although it could not collapse the local
form. It matched the integrated learner's three complete trajectories in each
detail history. The controls therefore do not establish a general benefit from
all of the integrated structural operations. The [complete report](report.md)
includes every control, endpoint, paired memory comparison and individual run.

## Verification, budget and limits

Four new synthetic checks passed in one invocation, charging **512 labels**.
They covered independent replay of all variants, collapse and recreation,
capture on reduction, frozen memory, incompatible semantics, denied raw access,
and checkpoint continuation with pending upper reduction. The round charged
**19,728 of 20,000** fixture labels in total. No additional experiments were
started from the remaining allowance.

The benchmark allocated **537,600** label presentations and used **433,920**;
unused local feedback in controls is accounted separately. It fitted **16,056**
candidates and made **2,145,504** ranking/selection/challenger queries, **60,480**
composite evaluation predictions and **237,760** oracle context queries, all
within the frozen ceilings. The largest local pending table had one cell,
upper pending table eight, and archive sixteen. Historical tables remain in
audit records but are not accessible to prediction or search.

Execution took about 95 seconds; independent audit took about 74 seconds,
each below its 600-second limit. The audit reused saved evidence rather than
acquiring new labels. Earlier frozen dependencies remained unchanged. No
source or result correction was required.

The four-state modules, binary targets, two-level wiring, supervision, finite
partition language and structural preferences are supplied. Learned depth,
temporal folds, eigenforms, meta-learning, user interpretability and safety
advantages remain untested. The evidence supports implementing and inspecting
revisable distinctions; the stringent combined reliability claim failed.

Verify the saved record from the repository root:

```sh
python3 checks/audit_structural_consolidation.py
```

Saved artifacts: [manifest](manifest.json), [worlds](worlds.json),
[complete run traces](runs.jsonl.gz), [checkpoints](checkpoints/),
[summary](results.json), [test log](tests.txt), [audit](audit.json) and
[completion status](completion.json). The original benchmark summary remains
marked `completed_pending_audit`; the separate audit and completion records
confirm its subsequent verification.

The [round synthesis](../consolidation-round-synthesis.md) records the resulting
claim boundary and the questions this round leaves open.
