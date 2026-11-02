# 031 — Bounded external memory steering

Completed 2026-11-02. **All 60 runs independently audited; the primary steering criterion failed.**
Targeted control improved mean composite loss over no intervention by **0.008889 nats**, positive in **4/10 changing-history pairs**.
This missed the declared .01-nat and 8/10 thresholds. Stable histories triggered
no controls, and all declared collateral-cost guards passed. Final validity in
the changing history remained below the 8/10 requirement.

## What was steered

All runs used the same combined learner. A scripted external controller inspected
current review diagnostics and selected the first qualifying, not-yet-automatically
accepted weakening proposal, ranked by slow-minus-fast loss. It acted at most once
per run, up to tick1024. No latent truth entered that choice. No new labels were
provided by the intervention. Halving applied to the whole slow channel after
the completed review, including any evidence just migrated there.

No-control runs logged the same proposed trigger. Targeted runs halved that
channel; rotated controls halved the next channel modulo3. Rotated is a
specificity control, not necessarily an irrelevant channel. Each event recorded
the review identity, rationale, removed mass and before/after engine hashes.
This tests a scripted controller and the API, not human or LLM interpretability.

Five fresh environments each had two proposal replicates; the ten pairs are
not ten independent environments. All five draws happened to change node0.
No extra seeds were drawn to change that coverage limitation. The fixed primary
window577–1024 was not aligned to actual intervention times (640–832 here).
The [protocol](../../experiments/memory_steering_protocol.md) preserves the full design.

| History | Policy | Triggers | Interventions | Primary observed loss | Return loss | Later loss | Final full validity |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| stable | unsteered | 0 | 0 | 0.336443 | 0.335002 | 0.334227 | 10/10 |
| stable | targeted | 0 | 0 | 0.336443 | 0.335002 | 0.334227 | 10/10 |
| stable | rotated | 0 | 0 | 0.336443 | 0.335002 | 0.334227 | 10/10 |
| repeated | unsteered | 10 | 0 | 0.652881 | 0.539612 | 0.691161 | 5/10 |
| repeated | targeted | 10 | 10 | 0.643992 | 0.542990 | 0.688684 | 6/10 |
| repeated | rotated | 10 | 10 | 0.654734 | 0.537871 | 0.692294 | 4/10 |

Final validity requires correct partitions, all modal composite predictions
correct and expected regret<=.10. Returned knowledge and later reversals remain
part of evaluation even though only one early control is allowed.

| Gate | Result |
| --- | --- |
| benefit | fail |
| benefit pairs | fail |
| specificity | pass |
| specificity pairs | fail |
| final validity | fail |
| cost mean | pass |
| cost worst | pass |
| unaffected mean | pass |
| unaffected worst | pass |

Mean gain over rotated control was 0.010742 nats, positive in 5/10 pairs: the mean specificity gate passed, but consistency failed.

## A useful distinction in the diagnostics

Post-audit examination separates improvement in a selected local prediction from
improvement in the composite output. These diagnostics were not primary criteria
and do not overturn the failed test.

| Seed / proposal | Selected channel | Tick | Selected-channel gain | Composite gain | Composite probabilities unchanged in primary window |
| --- | ---: | ---: | ---: | ---: | --- |
| 2000 / 2000 | 2 | 768 | 0.020170 | 0.020170 | False |
| 2000 / 2001 | 2 | 704 | 0.028957 | 0.028957 | False |
| 2001 / 2000 | 2 | 768 | 0.024108 | 0.024108 | False |
| 2001 / 2001 | 0 | 704 | 0.021046 | 0.000000 | True |
| 2002 / 2000 | 0 | 704 | 0.002507 | 0.000000 | True |
| 2002 / 2001 | 0 | 640 | 0.024612 | 0.000000 | True |
| 2003 / 2000 | 2 | 768 | 0.015655 | 0.015655 | False |
| 2003 / 2001 | 0 | 832 | 0.019093 | 0.000000 | True |
| 2004 / 2000 | 0 | 704 | 0.032443 | 0.000000 | True |
| 2004 / 2001 | 0 | 832 | 0.021877 | 0.000000 | True |

Four interventions selected composite channel2; all four improved the measured
composite outcome. Six selected local channel0; all six improved that local
prediction, while composite probabilities were unchanged in the primary window.
The upper predictor consumes category membership, not local confidence. Improving
local probability estimates need not alter its prediction. This exposes a
limitation of ranking intervention targets by local surprise without measuring
their relevance to the intended output. It is not a post-hoc success claim.

The next steering question is therefore more specific: can a controller identify
which representation or evidence change will affect the intended outcome? A
future test would need a preregistered target and downstream-effect checks.
No new controller, additional interventions or follow-up seeds were tried here.

## Verification and scope

All worlds, pre-update predictions, automatic decisions, explicit interventions,
event hashes, native/outer checkpoints, metrics, paired gates and budgets passed
independent reconstruction. The audit imports no runtime or experiment policy.
Fixtures used672 label presentations of a1000 allowance. Benchmark generated
102400 labels and presented614400 across60 runs. All resource ceilings passed.
Benchmark 32.043s; audit 25.188s, each below900s.
No restart, tuning, default promotion or claim of general steerability.

Artifacts: [results](results.json), [audit](audit.json), [manifest](manifest.json),
[worlds](worlds.json), [traces](runs.jsonl.gz), [secondary diagnostics](diagnostics.json),
[fixtures](../memory-steering-fixtures/attempt-01.json).
