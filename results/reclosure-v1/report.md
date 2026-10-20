# Experiment 014: fixed benchmark

Primary criterion: **FAIL**.

| Branch | Variant | Exact + predictive | Coarse + valid | Affected fine + valid | Transient trajectory | Main loss | Late raw reads |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persistent | failure_only | 10/10 | 2/10 | 2/10 | 0/10 | 0.369090 | 0.650 |
| persistent | reclose | 10/10 | 8/10 | 0/10 | 0/10 | 0.367666 | 0.275 |
| remap | failure_only | 10/10 | 4/10 | 3/10 | 0/10 | 0.432492 | 0.600 |
| remap | reclose | 10/10 | 10/10 | 0/10 | 0/10 | 0.426315 | 0.100 |
| breach | failure_only | 10/10 | 0/10 | 10/10 | 0/10 | 0.427883 | 1.000 |
| breach | reclose | 10/10 | 0/10 | 10/10 | 0/10 | 0.427883 | 1.000 |
| transient | failure_only | 10/10 | 0/10 | 8/10 | 0/10 | 0.486785 | 1.000 |
| transient | reclose | 10/10 | 7/10 | 3/10 | 7/10 | 0.488261 | 0.600 |

Transient trajectory is the new two-witness operation, so failure_only cannot satisfy it.

## Fixed checks

```json
{
  "transfer": false,
  "persistent_coarse": true,
  "remap_coarse": true,
  "persistent_loss_guard": true,
  "breach_preserved": true,
  "breach_loss_guard": true,
  "transient_trajectories": false,
  "transient_access_pairs": false,
  "transient_access_mean": true,
  "transient_loss_guard": true
}
```

## Resources

```json
{
  "runs": 80,
  "allocated_label_presentations": 358400,
  "generated_labels": 89600,
  "evaluation_predictions": 32640,
  "max_pending_cells_per_run": 8,
  "costs": {
    "candidate_fits": 10240,
    "candidate_fit_rows": 1843200,
    "refits": 163840,
    "refit_rows": 28523520,
    "upper_refits": 37888,
    "upper_refit_rows": 7274496,
    "upper_candidate_fits": 2880,
    "upper_candidate_rows": 552960,
    "feedback_labels": 358400,
    "prediction_raw_reads": 37888,
    "challenger_predictions": 7840,
    "challenger_starts": 211,
    "group_invalidations": 0,
    "failed_witnesses": 184,
    "accepted_reclosures": 24
  }
}
```

## Every run

| Environment | Learner | Branch | Variant | Final valid | Mode | New reclosures | Reopenings | Late raw reads |
| --- | --- | --- | --- | --- | --- | --- | --- | ---: |
| 400 | 400 | persistent | failure_only | True | fine0 | [] | [704] | 0.250 |
| 400 | 400 | persistent | reclose | True | fine0 | [] | [704] | 0.250 |
| 400 | 401 | persistent | failure_only | True | fine0 | [] | [704] | 0.250 |
| 400 | 401 | persistent | reclose | True | fine0 | [] | [704] | 0.250 |
| 400 | 400 | remap | failure_only | True | coarse | [] | [] | 0.000 |
| 400 | 400 | remap | reclose | True | coarse | [] | [] | 0.000 |
| 400 | 401 | remap | failure_only | True | coarse | [] | [] | 0.000 |
| 400 | 401 | remap | reclose | True | coarse | [] | [] | 0.000 |
| 400 | 400 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 400 | 400 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 400 | 401 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 400 | 401 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 400 | 400 | transient | failure_only | True | fine0 | [] | [64] | 1.000 |
| 400 | 400 | transient | reclose | True | coarse | [640] | [64] | 0.500 |
| 400 | 401 | transient | failure_only | True | fine0 | [] | [64] | 1.000 |
| 400 | 401 | transient | reclose | True | coarse | [640] | [64] | 0.500 |
| 401 | 400 | persistent | failure_only | True | fine0 | [] | [192] | 1.000 |
| 401 | 400 | persistent | reclose | True | coarse | [320, 768] | [192, 576] | 0.750 |
| 401 | 401 | persistent | failure_only | True | fine0 | [] | [192] | 1.000 |
| 401 | 401 | persistent | reclose | True | coarse | [320, 768] | [192, 576] | 0.750 |
| 401 | 400 | remap | failure_only | True | fine1 | [] | [192] | 1.000 |
| 401 | 400 | remap | reclose | True | coarse | [320] | [192] | 0.000 |
| 401 | 401 | remap | failure_only | True | fine1 | [] | [192] | 1.000 |
| 401 | 401 | remap | reclose | True | coarse | [320, 768] | [192, 512] | 1.000 |
| 401 | 400 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 401 | 400 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 401 | 401 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 401 | 401 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 401 | 400 | transient | failure_only | True | fine1 | [] | [64] | 1.000 |
| 401 | 400 | transient | reclose | True | coarse | [576] | [64] | 0.250 |
| 401 | 401 | transient | failure_only | True | fine1 | [] | [64] | 1.000 |
| 401 | 401 | transient | reclose | True | coarse | [576] | [64] | 0.250 |
| 402 | 400 | persistent | failure_only | True | coarse | [] | [] | 0.000 |
| 402 | 400 | persistent | reclose | True | coarse | [] | [] | 0.000 |
| 402 | 401 | persistent | failure_only | True | coarse | [] | [] | 0.000 |
| 402 | 401 | persistent | reclose | True | coarse | [] | [] | 0.000 |
| 402 | 400 | remap | failure_only | True | coarse | [] | [] | 0.000 |
| 402 | 400 | remap | reclose | True | coarse | [] | [] | 0.000 |
| 402 | 401 | remap | failure_only | True | coarse | [] | [] | 0.000 |
| 402 | 401 | remap | reclose | True | coarse | [] | [] | 0.000 |
| 402 | 400 | breach | failure_only | True | fine0 | [] | [64] | 1.000 |
| 402 | 400 | breach | reclose | True | fine0 | [] | [64] | 1.000 |
| 402 | 401 | breach | failure_only | True | fine0 | [] | [64] | 1.000 |
| 402 | 401 | breach | reclose | True | fine0 | [] | [64] | 1.000 |
| 402 | 400 | transient | failure_only | True | fine0 | [] | [64] | 1.000 |
| 402 | 400 | transient | reclose | True | fine0 | [] | [64] | 1.000 |
| 402 | 401 | transient | failure_only | True | fine0 | [] | [64] | 1.000 |
| 402 | 401 | transient | reclose | True | fine0 | [] | [64] | 1.000 |
| 403 | 400 | persistent | failure_only | True | fine0 | [] | [64] | 1.000 |
| 403 | 400 | persistent | reclose | True | coarse | [320] | [64] | 0.000 |
| 403 | 401 | persistent | failure_only | True | fine0 | [] | [64] | 1.000 |
| 403 | 401 | persistent | reclose | True | coarse | [320] | [64] | 0.000 |
| 403 | 400 | remap | failure_only | True | fine0 | [] | [64] | 1.000 |
| 403 | 400 | remap | reclose | True | coarse | [256] | [64] | 0.000 |
| 403 | 401 | remap | failure_only | True | fine0 | [] | [192] | 1.000 |
| 403 | 401 | remap | reclose | True | coarse | [320] | [192] | 0.000 |
| 403 | 400 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 403 | 400 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 403 | 401 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 403 | 401 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 403 | 400 | transient | failure_only | True | fine1 | [] | [64] | 1.000 |
| 403 | 400 | transient | reclose | True | coarse | [640] | [64] | 0.500 |
| 403 | 401 | transient | failure_only | True | fine1 | [] | [64] | 1.000 |
| 403 | 401 | transient | reclose | True | coarse | [640] | [64] | 0.500 |
| 404 | 400 | persistent | failure_only | True | fine1 | [] | [64] | 1.000 |
| 404 | 400 | persistent | reclose | True | coarse | [192, 640] | [64, 448] | 0.500 |
| 404 | 401 | persistent | failure_only | True | fine1 | [] | [64] | 1.000 |
| 404 | 401 | persistent | reclose | True | coarse | [192, 576] | [64, 448] | 0.250 |
| 404 | 400 | remap | failure_only | True | fine1 | [] | [128] | 1.000 |
| 404 | 400 | remap | reclose | True | coarse | [256] | [128] | 0.000 |
| 404 | 401 | remap | failure_only | True | fine0 | [] | [128] | 1.000 |
| 404 | 401 | remap | reclose | True | coarse | [256] | [128] | 0.000 |
| 404 | 400 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 404 | 400 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 404 | 401 | breach | failure_only | True | fine1 | [] | [64] | 1.000 |
| 404 | 401 | breach | reclose | True | fine1 | [] | [64] | 1.000 |
| 404 | 400 | transient | failure_only | True | fine1 | [] | [64] | 1.000 |
| 404 | 400 | transient | reclose | True | coarse | [640] | [64] | 0.500 |
| 404 | 401 | transient | failure_only | True | fine1 | [] | [64] | 1.000 |
| 404 | 401 | transient | reclose | True | fine1 | [] | [64] | 1.000 |
