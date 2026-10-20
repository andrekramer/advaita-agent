# Experiment 015: fixed benchmark

Primary criterion: **FAIL**.

| Branch | Rule | Initial valid | Final valid | Invalid checkpoints | Inexact checkpoints | Main loss | Recovery index |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persistent | immediate | 10/10 | 10/10 | 0 | 0 | 0.356043 | 576.0 |
| persistent | uniform | 10/10 | 10/10 | 0 | 0 | 0.383433 | 576.0 |
| persistent | earned | 10/10 | 10/10 | 0 | 0 | 0.356043 | 576.0 |
| remap | immediate | 10/10 | 10/10 | 10 | 6 | 0.412770 | 640.0 |
| remap | uniform | 10/10 | 10/10 | 26 | 22 | 0.477641 | 742.4 |
| remap | earned | 10/10 | 10/10 | 20 | 16 | 0.439925 | 704.0 |
| transient | immediate | 10/10 | 10/10 | 16 | 16 | 0.432490 | 678.4 |
| transient | uniform | 10/10 | 10/10 | 0 | 0 | 0.433938 | 576.0 |
| transient | earned | 10/10 | 10/10 | 0 | 0 | 0.406549 | 576.0 |

Recovery index is meaningful for remap; persistent/transient use unchanged latent forms.

```json
{
  "acquisition": true,
  "stable_final": true,
  "protection": true,
  "persistent_loss": true,
  "transient_loss": true,
  "remap_final": true,
  "remap_latency": true,
  "remap_loss": false
}
```

## Resources

```json
{
  "runs": 90,
  "generated_labels": 23040,
  "allocated_labels": 138240,
  "checkpoint_queries": 6120,
  "main_predictions": 92160,
  "max_pending_cells": 2,
  "costs": {
    "candidate_fits": 5760,
    "candidate_fit_rows": 1036800,
    "refits": 92160,
    "refit_rows": 16044480,
    "pending_predictions": 2432,
    "pending_starts": 76,
    "pending_failures": 20,
    "confirmed_replacements": 56,
    "immediate_replacements": 104,
    "establishments": 131,
    "used_labels": 138240,
    "ordinary_selection_predictions": 92160
  }
}
```

## Every run

| Environment | Search | Branch | Rule | Initial | Final | Invalid | Acquisition | Recovery | Replacements |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 500 | 500 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 500 | 500 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 500 | 500 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 500 | 501 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 500 | 501 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 500 | 501 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 500 | 500 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 500 | 500 | remap | uniform | True | True | 3 | 128 | 768 | [128, 640, 768] |
| 500 | 500 | remap | earned | True | True | 2 | 64 | 704 | [64, 640, 704] |
| 500 | 501 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 500 | 501 | remap | uniform | True | True | 3 | 128 | 768 | [128, 640, 768] |
| 500 | 501 | remap | earned | True | True | 2 | 64 | 704 | [64, 640, 704] |
| 500 | 500 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 500 | 500 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 500 | 500 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 500 | 501 | transient | immediate | True | True | 3 | 64 | 768 | [64, 576, 640, 768] |
| 500 | 501 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 500 | 501 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 501 | 500 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 501 | 500 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 501 | 500 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 501 | 501 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 501 | 501 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 501 | 501 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 501 | 500 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576] |
| 501 | 500 | remap | uniform | True | True | 2 | 128 | 704 | [128, 640] |
| 501 | 500 | remap | earned | True | True | 2 | 64 | 704 | [64, 640] |
| 501 | 501 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576] |
| 501 | 501 | remap | uniform | True | True | 2 | 128 | 704 | [128, 640] |
| 501 | 501 | remap | earned | True | True | 2 | 64 | 704 | [64, 640] |
| 501 | 500 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 501 | 500 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 501 | 500 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 501 | 501 | transient | immediate | True | True | 3 | 64 | 768 | [64, 576, 640, 768] |
| 501 | 501 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 501 | 501 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 502 | 500 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 502 | 500 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 502 | 500 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 502 | 501 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 502 | 501 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 502 | 501 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 502 | 500 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 502 | 500 | remap | uniform | True | True | 3 | 128 | 768 | [128, 640, 768] |
| 502 | 500 | remap | earned | True | True | 2 | 64 | 704 | [64, 640, 704] |
| 502 | 501 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576] |
| 502 | 501 | remap | uniform | True | True | 2 | 128 | 704 | [128, 640] |
| 502 | 501 | remap | earned | True | True | 2 | 64 | 704 | [64, 640] |
| 502 | 500 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 502 | 500 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 502 | 500 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 502 | 501 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 502 | 501 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 502 | 501 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 503 | 500 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 503 | 500 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 503 | 500 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 503 | 501 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 503 | 501 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 503 | 501 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 503 | 500 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 503 | 500 | remap | uniform | True | True | 3 | 128 | 768 | [128, 640, 768] |
| 503 | 500 | remap | earned | True | True | 2 | 64 | 704 | [64, 640, 704] |
| 503 | 501 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576] |
| 503 | 501 | remap | uniform | True | True | 2 | 128 | 704 | [128, 640] |
| 503 | 501 | remap | earned | True | True | 2 | 64 | 704 | [64, 640] |
| 503 | 500 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 503 | 500 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 503 | 500 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 503 | 501 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 503 | 501 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 503 | 501 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 504 | 500 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 504 | 500 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 504 | 500 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 504 | 501 | persistent | immediate | True | True | 0 | 64 | 576 | [64] |
| 504 | 501 | persistent | uniform | True | True | 0 | 128 | 576 | [128] |
| 504 | 501 | persistent | earned | True | True | 0 | 64 | 576 | [64] |
| 504 | 500 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 504 | 500 | remap | uniform | True | True | 3 | 128 | 768 | [128, 640, 768] |
| 504 | 500 | remap | earned | True | True | 2 | 64 | 704 | [64, 640, 704] |
| 504 | 501 | remap | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 504 | 501 | remap | uniform | True | True | 3 | 128 | 768 | [128, 640, 768] |
| 504 | 501 | remap | earned | True | True | 2 | 64 | 704 | [64, 640, 704] |
| 504 | 500 | transient | immediate | True | True | 1 | 64 | 640 | [64, 576, 640] |
| 504 | 500 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 504 | 500 | transient | earned | True | True | 0 | 64 | 576 | [64] |
| 504 | 501 | transient | immediate | True | True | 3 | 64 | 768 | [64, 576, 768] |
| 504 | 501 | transient | uniform | True | True | 0 | 128 | 576 | [128] |
| 504 | 501 | transient | earned | True | True | 0 | 64 | 576 | [64] |
