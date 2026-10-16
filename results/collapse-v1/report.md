# Experiment 008 results

Declared criterion: **True**, 5/5 seeds.

| World | Learner | Seed | Acquired forms | Final forms | Accuracy | Log loss | Merge delay |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| changed | merge_enabled | 0 | 2 | 1 | 100% | 0.039221 | 48 |
| changed | merge_disabled | 0 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_enabled | 0 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_disabled | 0 | 2 | 2 | 100% | 0.074108 | — |
| changed | merge_enabled | 1 | 2 | 1 | 100% | 0.039221 | 48 |
| changed | merge_disabled | 1 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_enabled | 1 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_disabled | 1 | 2 | 2 | 100% | 0.074108 | — |
| changed | merge_enabled | 2 | 2 | 1 | 100% | 0.039221 | 48 |
| changed | merge_disabled | 2 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_enabled | 2 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_disabled | 2 | 2 | 2 | 100% | 0.074108 | — |
| changed | merge_enabled | 3 | 2 | 1 | 100% | 0.039221 | 48 |
| changed | merge_disabled | 3 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_enabled | 3 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_disabled | 3 | 2 | 2 | 100% | 0.074108 | — |
| changed | merge_enabled | 4 | 2 | 1 | 100% | 0.039221 | 48 |
| changed | merge_disabled | 4 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_enabled | 4 | 2 | 2 | 100% | 0.074108 | — |
| unchanged | merge_disabled | 4 | 2 | 2 | 100% | 0.074108 | — |

## Review histories

Forms after each review; first phase ends at trial 96.

| World | Learner | Seed | Trial 48 | Trial 96 | Trial 144 | Trial 192 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| changed | merge_enabled | 0 | 2 | 2 | 1 | 1 |
| changed | merge_disabled | 0 | 2 | 2 | 2 | 2 |
| unchanged | merge_enabled | 0 | 2 | 2 | 2 | 2 |
| unchanged | merge_disabled | 0 | 2 | 2 | 2 | 2 |
| changed | merge_enabled | 1 | 2 | 2 | 1 | 1 |
| changed | merge_disabled | 1 | 2 | 2 | 2 | 2 |
| unchanged | merge_enabled | 1 | 2 | 2 | 2 | 2 |
| unchanged | merge_disabled | 1 | 2 | 2 | 2 | 2 |
| changed | merge_enabled | 2 | 2 | 2 | 1 | 1 |
| changed | merge_disabled | 2 | 2 | 2 | 2 | 2 |
| unchanged | merge_enabled | 2 | 2 | 2 | 2 | 2 |
| unchanged | merge_disabled | 2 | 2 | 2 | 2 | 2 |
| changed | merge_enabled | 3 | 2 | 2 | 1 | 1 |
| changed | merge_disabled | 3 | 2 | 2 | 2 | 2 |
| unchanged | merge_enabled | 3 | 2 | 2 | 2 | 2 |
| unchanged | merge_disabled | 3 | 2 | 2 | 2 | 2 |
| changed | merge_enabled | 4 | 2 | 2 | 1 | 1 |
| changed | merge_disabled | 4 | 2 | 2 | 2 | 2 |
| unchanged | merge_enabled | 4 | 2 | 2 | 2 | 2 |
| unchanged | merge_disabled | 4 | 2 | 2 | 2 | 2 |

## Accepted merges

| Seed | Trial | Predictive loss gain | Complexity gain | Total selection gain |
| --- | ---: | ---: | ---: | ---: |
| 0 | 144 | 0.034887 | 0.015000 | 0.049887 |
| 1 | 144 | 0.034887 | 0.015000 | 0.049887 |
| 2 | 144 | 0.034887 | 0.015000 | 0.049887 |
| 3 | 144 | 0.034887 | 0.015000 | 0.049887 |
| 4 | 144 | 0.034887 | 0.015000 | 0.049887 |

## Evidence and computation

| World | Learner | Candidate fits, all seeds | Candidate fit rows | Count refit rows |
| --- | --- | ---: | ---: | ---: |
| changed | merge_enabled | 100 | 4800 | 40440 |
| changed | merge_disabled | 95 | 4560 | 40440 |
| unchanged | merge_enabled | 110 | 5280 | 40440 |
| unchanged | merge_disabled | 95 | 4560 | 40440 |

4,960 outcome-bearing presentations; 480 additional unlabelled checkpoint predictions.
All runs used the same 48-main-observation rolling window from their start.
Full traces and criteria are saved in results.json; see findings.md for interpretation.
