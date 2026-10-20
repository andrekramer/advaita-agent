# Experiment 015: protecting a form after it earns support

Completed 2026-10-20. **The combined primary criterion failed.** Earned
protection prevented harmful structural replacements during the temporary
corruption burst in all ten runs, without delaying initial acquisition.
However, it raised loss after a lasting change by .054309 nats, exceeding
the fixed .05 allowance. Keep that failure alongside the observed benefit.

This was a local point test following 014, not another nested-interface run.
It isolates one question: can initial discovery remain permissive while
replacement of an established form requires more evidence?

## Design and what was supplied

One learner maps four observed states to a binary local effect. It can propose
eight partitions into one or two groups. Counts update from a rolling
192-observation buffer; four randomly ordered proposals are fitted every
64 observations, with the training-ranked winner assessed on 32 fresh
selection labels. These are the unchanged local primitives from 013.

Three policies receive identical observations and candidate-fit budgets:

* **Immediate:** accept a fresh-batch improvement greater than .005 nats.
* **Uniform:** require two consecutive improvements for a frozen challenger
  before any replacement.
* **Earned:** initially accept immediately. After the incumbent survives two
  consecutive adequate review batches, require two witnesses to replace it.
  Replacement clears that protection, allowing provisional revision again.

“Adequate” is a fixed loss threshold of .55 nats. It is not an oracle judgment
of category correctness. Selection evidence updates the policy state but
never fits model counts. Pending challengers remain frozen between witnesses.
The original incumbent continues updating its probabilities.

Five fresh environments crossed with two proposal seeds produce ten paired
runs per condition. Three conditions cover an unchanged form, a lasting
membership change after observation 512, and a 64-observation burst of
misleading outcomes. In the last condition, observed outcomes temporarily
follow the alternative form while the evaluator's latent form remains
unchanged. All conditions also have independent 10% outcome noise.

The [fixed protocol](../../experiments/form_retention_protocol.md) specifies
the regimes, criteria and full budget. The learner has no branch or change
signal. Architecture, candidate language, timing and acceptance rules are
supplied; this is not learned consolidation policy or meta-learning.

## Acquisition and final learning

All three policies were valid at observation 256 and at the final observation
1,024 in every condition: exact exported forms, 100% modal prediction accuracy
over all four states, and expected-loss regret no greater than .10 nats.
That does not mean every intermediate prediction or representation was right.

Immediate and earned first acquired a valid form at review **64 in all ten
seed pairs**. Uniform first acquired it at **128 in all ten**. Shared acquisition
is counted once per seed pair, not three times for the three conditions.

Thus earned protection avoided uniform corroboration's initial delay in this
sample. The correct candidate was reachable early in every run; this does
not resolve the missed-discovery failures of 014 under its different sample
and two-module curriculum.

## Protection against a temporary misleading signal

| Outcome | Immediate | Uniform | Earned |
| --- | ---: | ---: | ---: |
| Harmful replacements at review 576 | 10 | 0 | 0 |
| Invalid checkpoints, reviews 320–1,024 | 16 | 0 | 0 |
| Mean latent expected loss, main 513–768 | .468794 | .371666 | .371666 |
| Mean observed loss, all main records | .432490 | .433938 | .406549 |
| Final-valid runs | 10/10 | 10/10 | 10/10 |

Every immediate learner replaced a correct form at the corrupted review.
Seven recovered validity at the next review, 640. Three took until 768,
having passed through another incorrect partition.

Both corroborated policies started a pending challenger at 576 and rejected
it on fresh evidence at 640. Earned reduced latent expected loss over the
declared window by **20.7%** relative to immediate. All ten paired runs had
fewer invalid checkpoints. Retaining the partition did not freeze numerical
estimates: its counts were still affected by the misleading observations.

For a concrete trace, environment 500/search 501's incumbent selection loss
was .75186 at review 576, versus .69494 for the fresh challenger. Immediate
accepted the alternative partition. Earned kept it pending. At review 640,
the retained incumbent scored .37527, while the frozen challenger scored
.69622, so earned rejected the replacement. Immediate did not regain the
correct form until review 768.

One incorrect immediate form also accumulated two adequate batches and was
marked established at review 704 (environment 504/search 501). This flag was
diagnostic only for that control, so it did not protect the error. It still
demonstrates why the adequacy flag cannot be equated with correctness.
No incorrect form earned that flag in the earned-policy runs.

In the persistent condition there were no invalid checkpoints or harmful
replacements under any policy. Earned and immediate made identical predictions.
Protection against ordinary independent noise alone therefore remains
undemonstrated here; the measured benefit comes from the structured burst.

## The cost when the change persists

| Outcome after lasting change | Immediate | Uniform | Earned |
| --- | ---: | ---: | ---: |
| Mean stable recovery index | 640 | 742.4 | 704 |
| Invalid checkpoints, reviews 320–1,024 | 10 | 26 | 20 |
| Inexact-form checkpoints in that window | 6 | 22 | 16 |
| Mean observed loss, main 513–1,024 | .450748 | .525712 | .505057 |
| Final-valid runs | 10/10 | 10/10 | 10/10 |

Stable recovery means the first of two consecutive valid post-change reviews.
It is only confirmed at the second review. Earned's first stable valid
checkpoint was exactly **64 main observations later in every pair** than
immediate's. This met the latency allowance at its boundary.

All ten earned learners started a challenger at 576 and accepted it at 640.
Six still needed another immediate structural replacement at 704. The other
four already had the correct grouping at 640 but required further probability
updates to meet the loss criterion. A challenger can beat an outdated
incumbent twice without being an adequate final representation: its frozen
counts were fitted from a buffer containing both old and new observations.

The post-change loss increase was **.054309**, above the predeclared **.05**
limit. This single failed check makes the combined result a failure even
though protection, acquisition, final validity and the other loss checks
passed. Uniform imposed further delay in six runs; earned's temporary return
to immediate revision after replacement reduced that extra cost.

## What this adds, and what it leaves open

This supports separating **discovery, establishment and replacement** as
operations with different evidence requirements. A form can be provisionally
useful before it earns resistance to revision. Its numerical predictions can
continue adapting while its grouping is protected.

The same mechanism carries a stability–adaptation tradeoff. It has no general
ability to identify noise versus change. The test's brief corruption ends
before a second corroborating review; that duration and alignment favor a
two-witness rule. Longer bursts, switches between review boundaries, rare
states and less balanced exposure were not tested. Five environments and
two search seeds also remain a very small, dependent sample.

There is no upper interface here, so this result does not demonstrate fewer
unnecessary reopenings in 013–014. It adds a tested local operation and an
explicit cost, not an integrated solution. The learner has evolving
representation and evidence state, but the rule for using that state is fixed.
It does not yet learn how much inertia to apply.

## Verification and resources

Eight targeted tests passed before execution. A separate synthetic seed
validated independent replay before the benchmark seeds were run. The
benchmark ran once, with no threshold adjustment or post-result source change.
An independent auditor reconstructed all **90 runs**, including streams,
candidate tables and ranking, policy decisions, predictions, evaluation,
metrics, criteria and resource totals. All six manifests from 010–015 verify.

* **138,240 allocated and used label presentations**, from 23,040 generated
  branch-stream labels; shared histories are not independent evidence.
* **5,760 candidate fits**, with 1,036,800 candidate-fit row visits.
* **92,160 main predictions/refits**, with 16,044,480 refit row visits.
* **6,120 checkpoint prediction queries**; latent scoring also uses existing
  main predictions.
* **2,432 extra pending-selection predictions**, on top of 92,160 ordinary
  incumbent/winner selection predictions.
* **76 pending challengers**, 56 confirmed and 20 rejected. Each stored at
  most two cells; all buffers stayed bounded at 192 main records.

The extra scoring and memory mean this is label- and fit-budget matched,
not perfectly compute matched. Different accepted incumbents also affect
later proposal order through exclusion from the candidate deck.

Inspect the [full report](report.md), [metrics](metrics.json),
[complete traces](results.json), and [frozen manifest](manifest.json).
Verification can be repeated without rerunning the benchmark:

```sh
python3 -m unittest discover -s checks -p test_form_retention.py -v
python3 checks/audit_form_retention.py
```

This bounded follow-up is complete. Its findings are incorporated into the
[capability consolidation](../relationships-interfaces-synthesis.md).
