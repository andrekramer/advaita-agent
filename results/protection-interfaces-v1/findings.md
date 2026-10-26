# Experiment 017 / C1: protection helps against misleading evidence, but delays real change

Completed 2026-10-23. **The combined primary criterion failed; the separate C2
progression gate passed.** All 120 runs completed, and independent replay
verified the streams, decisions, predictions, complete checkpoints, evidence
ledgers, metrics and costs. No criteria were changed and no benchmark was rerun.

Earned protection reduced local errors during a misleading burst, but exceeded
both the allowed local loss cost and recovery delay when the local form really
changed. Reclosure helped hide detail again after recovery. These operations
can now coexist in one continuing learner, with measurable interactions and
trade-offs. This does not establish that their combination is generally better.

## What was tested

The [frozen protocol](../../experiments/protection_interfaces_protocol.md)
crossed immediate versus earned local protection with opening-only versus
reclosure at the upper interface. Every variant used the unchanged C0 core,
two lower modules and one upper predictor. The three conditions were persistent
forms, lasting remapping after record 128, and a misleading burst at records
129–192 affecting one local feedback channel only. The burst left true local
forms and composite outcomes unchanged.

Five fresh environments and two proposal seeds produced ten paired runs per
cell. Acquisition was shared across conditions, so those histories are not
independent replications. Learning rules, alphabets, partitions, architecture,
supervision and thresholds remained supplied. Evaluator truth never entered
the learner. The study tests fixed-policy interaction, not meta-learning.

## Protection against a misleading local signal

With either upper policy, earned protection reduced affected-local errors from
**12 to 2 of 60 post-change checkpoints**, an 83.3% reduction. Nine of ten seed
pairs improved. Thus the positive-control and protection-benefit criteria were
met; this was not a case of claiming protection when nothing went wrong.

Over records 129–320, affected-local latent expected loss fell from .481642 to
.394140 nats. Composite latent loss also fell, from .352316 to .342121. The
parent often maintained good predictions by using raw detail when the local
abstraction was wrong. Mean affected-module bypass time fell from 83.2 to 12.8
records with protection, under either upper policy.

Protection reduced the need for this bypass. Reclosure supplied the separate
ability to stop exposing raw detail afterwards:

| Burst condition | Mean parent raw reads, out of 512 | Fully valid coarse endpoints |
| --- | ---: | ---: |
| Immediate / opening only | 332.8 | 0/10 |
| Immediate / reclosure | 172.8 | 8/10 |
| Earned / opening only | 83.2 | 7/10 |
| Earned / reclosure | 44.8 | 10/10 |

These are costs at the prediction interface. Search and the lower modules
still received raw observations; no reduction in sensing or secure information
isolation has been demonstrated.

## The cost of protecting a form when the world changes

After lasting remapping, protection increased affected-local latent loss by
**.069240 nats**, exceeding the .05 allowance, under both upper policies.
Mean confirmed recovery moved from **326.4 to 403.2 records**, a delay of
**76.8**, exceeding the allowed 64. No run was censored for this comparison.
These two failures defeated the combined primary criterion.

Composite prediction alone would give a more favourable account: its observed
post-change loss cost was .027691 with opening-only and .022160 with reclosure,
both within the .05 allowance. Its latent costs also passed. The parent could
partly compensate for slower lower learning by exposing raw states. This is
why the protocol checked the lower forms as well as the final output.

Reclosure did not remove that local delay. It did restore abstraction after
recovery: earned/opening finished with a fully valid coarse interface in 0/10
remap runs, whereas earned/reclosure did so in 10/10. Mean raw reads fell from
320.0 to 230.4. With immediate learning, reclosure improved coarse endpoints
from 5/10 to 8/10 and reduced reads from 172.8 to 115.2.

The factorial results do not support a blanket claim of synergy. For example,
in the burst condition reclosure saved fewer additional reads when protection
had already prevented much of the exposure. The full paired differences and
interaction terms are in the [complete report](report.md).

## Endpoint validity and retained failures

Immediate variants transferred correctly in 10/10 pairs; earned variants in
9/10. This one acquisition failure remained in every denominator. At the end,
immediate variants were fully valid in 9/10 pairs in every condition, and
earned variants in 10/10. All variants nevertheless had valid composite
predictions in 10/10 final evaluations. Correct output therefore did not always
mean correct local structure.

The repeated immediate failure was environment 603, proposal seed 601: the
unaffected lower module had an incorrect final map. The earned transfer failure
was environment 604, proposal seed 601; it recovered during adaptation. Each
appears in several paired conditions and must not be counted as several
independent discoveries. The report lists all 120 runs, including first valid
reviews, subsequent confirmation, exposure and reclosure events.

Persistent-world loss guards, burst loss guards and endpoint criteria passed.
The earned-protection success conjunction failed specifically on lasting-change
local loss and confirmed recovery delay, under both upper policies.

## Consolidation status

The preselected immediate/reclosure reference achieved **10/10 transfer and
9/10 final full validity in each condition**, meeting the >=8/10 progression
gate. Its coarse final validity was 8/10 in each condition, reported separately
from that gate. Independent correctness checks passed, so C2 is eligible to
proceed with the already-chosen immediate/reclosure policy. This choice was
fixed before the benchmark; it is not a post-result winner selection.

**C1 is complete; the consolidation round is not.** C2 has not started. It still
needs a frozen specification for dependency selection, adequate structural
reduction and capture/retrieval of a retained upper predictor. This experiment
does not integrate the archive, learn depth or temporal folds, adapt its own
learning rules, establish eigenforms, or demonstrate an interpretability or
safety advantage.

## Verification and resources

Four new synthetic tests passed before freezing, including independent state
replay of all four combinations and checks of corruption boundaries and gate
logic. The [test log](tests.txt) and [fixture accounting](../protection-interfaces-fixtures.json)
record one invocation. Its conservative charge was 336 labels, bringing the
round total to 19,216 of 20,000 and leaving **784** for later fixtures.

The benchmark used **399,360 label presentations**, exactly its allocation,
from 49,920 generated labels including paired duplicated histories. It fitted
14,400 candidates, made 1,540,896 ranking/selection/challenger queries and
33,600 composite evaluation queries. Local and composite main predictions are
counted separately in the complete report. Pending local tables reached two
cells and pending upper tables eight; no archive was used.

Execution took about 69 seconds; the independent audit took about 48 seconds,
each below its frozen 600-second limit. Audit replay reused 399,360 saved label
presentations; it acquired no new benchmark evidence. Earlier frozen source
and result dependencies remained unchanged.

Verify the saved record from the repository root with:

```sh
python3 checks/audit_protection_interfaces.py
```

The [source manifest](manifest.json), [benchmark summary](results.json),
[complete compressed run traces](runs.jsonl.gz), [per-run checkpoints](checkpoints/),
[independent audit result](audit.json) and [stage status](completion.json) are
retained. The benchmark's original status says `completed_pending_audit` because
it was saved before verification; `audit.json` and `completion.json` record the
subsequent successful audit. No source, threshold or result correction was needed.
