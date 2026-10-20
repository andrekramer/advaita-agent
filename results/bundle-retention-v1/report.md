# Experiment 011: coverage and corroboration

Primary criterion: **FAIL**.

All figures use fresh environment seeds 100–104 and proposal seeds 100,101.
Persistent passes require preservation after acquisition, not just endpoint recovery.

| Branch | Variant | Pass / 10 | Endpoint / 10 | Departures | Pair coverage A1 / A2 | Main loss |
| --- | --- | ---: | ---: | ---: | --- | ---: |
| reversible | iid_single | 3 | 3 | None | [7, 8] | 0.548178 |
| reversible | deck_single | 7 | 7 | None | [10, 9] | 0.532717 |
| reversible | iid_split | 3 | 3 | None | [7, 9] | 0.543877 |
| reversible | deck_split | 6 | 6 | None | [10, 9] | 0.540538 |
| persistent | iid_single | 7 | 7 | 0 | [7, 9] | 0.465743 |
| persistent | deck_single | 10 | 10 | 0 | [10, 10] | 0.409042 |
| persistent | iid_split | 6 | 6 | 0 | [7, 9] | 0.487944 |
| persistent | deck_split | 9 | 9 | 0 | [10, 10] | 0.425060 |

## Prediction and adaptation

| Branch | Variant | Endpoint losses | Phase main losses | First 64 after each change | Gate vetoes |
| --- | --- | --- | --- | --- | ---: |
| reversible | iid_single | 0.447579 / 0.340688 / 0.413364 | 0.580176 / 0.470086 / 0.594272 | 0.853051 / 0.950475 | 0 |
| reversible | deck_single | 0.340832 / 0.339583 / 0.377055 | 0.529967 / 0.470477 / 0.597707 | 0.896023 / 0.971655 | 0 |
| reversible | iid_split | 0.484317 / 0.341904 / 0.378211 | 0.594585 / 0.462252 / 0.574794 | 0.828907 / 0.948928 | 7 |
| reversible | deck_split | 0.376306 / 0.340165 / 0.377055 | 0.559951 / 0.467324 / 0.594337 | 0.883722 / 0.969235 | 12 |
| persistent | iid_single | 0.447579 / 0.377875 / 0.378211 | 0.580176 / 0.433025 / 0.384026 | 0.474851 / 0.350411 | 0 |
| persistent | deck_single | 0.340832 / 0.343731 / 0.342149 | 0.529967 / 0.349596 / 0.347564 | 0.364531 / 0.306969 | 0 |
| persistent | iid_split | 0.484317 / 0.413538 / 0.378211 | 0.594585 / 0.465745 / 0.403501 | 0.505519 / 0.396131 | 1 |
| persistent | deck_split | 0.376306 / 0.343731 / 0.342149 | 0.559951 / 0.367666 / 0.347564 | 0.407657 / 0.306969 | 1 |

## Per-run outcomes

| World | Variant | Proposal seed | Endpoint subsets | First successful reviews | Departures | Pass |
| --- | --- | ---: | --- | --- | --- | --- |
| 100-reversible | iid_single | 100 | [[2, 5], [0, 5], [2, 5]] | [256, None, 960] | [448] | False |
| 100-reversible | deck_single | 100 | [[2, 5], [5], [2, 5]] | [64, 512, 1024] | [448] | True |
| 100-reversible | iid_split | 100 | [[], [1, 5], [2, 5]] | [None, None, 960] | [] | False |
| 100-reversible | deck_split | 100 | [[2, 5], [5], [2, 5]] | [64, 512, 1024] | [512] | True |
| 100-reversible | iid_single | 101 | [[2, 5], [2, 5], [2, 5]] | [320, None, 960] | [] | False |
| 100-reversible | deck_single | 101 | [[2, 5], [5], [2, 5]] | [320, 512, 960] | [512] | True |
| 100-reversible | iid_split | 101 | [[2, 5], [2, 5], [2, 5]] | [320, None, 960] | [] | False |
| 100-reversible | deck_split | 101 | [[2, 5], [5], [2, 5]] | [320, 512, 960] | [512] | True |
| 100-persistent | iid_single | 100 | [[2, 5], [2, 5], [2, 5]] | [256, 448, 832] | [] | True |
| 100-persistent | deck_single | 100 | [[2, 5], [2, 5], [2, 5]] | [64, 448, 832] | [] | True |
| 100-persistent | iid_split | 100 | [[], [], [2, 5]] | [None, None, 960] | [] | False |
| 100-persistent | deck_split | 100 | [[2, 5], [2, 5], [2, 5]] | [64, 448, 832] | [] | True |
| 100-persistent | iid_single | 101 | [[2, 5], [2, 5], [2, 5]] | [320, 448, 832] | [] | True |
| 100-persistent | deck_single | 101 | [[2, 5], [2, 5], [2, 5]] | [320, 448, 832] | [] | True |
| 100-persistent | iid_split | 101 | [[2, 5], [2, 5], [2, 5]] | [320, 448, 832] | [] | True |
| 100-persistent | deck_split | 101 | [[2, 5], [2, 5], [2, 5]] | [320, 448, 832] | [] | True |
| 101-reversible | iid_single | 100 | [[1, 3], [3], [1, 3]] | [64, 512, 960] | [448] | True |
| 101-reversible | deck_single | 100 | [[1, 3], [3], [1, 3]] | [192, 512, 960] | [448] | True |
| 101-reversible | iid_split | 100 | [[1, 3], [3], [1, 3]] | [64, 512, 960] | [448] | True |
| 101-reversible | deck_split | 100 | [[1, 3], [3], [1, 3]] | [192, 512, 960] | [448] | True |
| 101-reversible | iid_single | 101 | [[1, 3], [2, 3], [1, 3]] | [128, None, 960] | [448, 704] | False |
| 101-reversible | deck_single | 101 | [[1, 3], [3], [1, 3]] | [320, 640, 960] | [448] | True |
| 101-reversible | iid_split | 101 | [[1, 3], [3], [1, 3]] | [128, 576, 960] | [576] | True |
| 101-reversible | deck_split | 101 | [[1, 3], [3], [1, 3]] | [320, 640, 960] | [640] | True |
| 101-persistent | iid_single | 100 | [[1, 3], [1, 3], [1, 3]] | [64, 448, 832] | [] | True |
| 101-persistent | deck_single | 100 | [[1, 3], [1, 3], [1, 3]] | [192, 448, 832] | [] | True |
| 101-persistent | iid_split | 100 | [[1, 3], [1, 3], [1, 3]] | [64, 448, 832] | [] | True |
| 101-persistent | deck_split | 100 | [[1, 3], [1, 3], [1, 3]] | [192, 448, 832] | [] | True |
| 101-persistent | iid_single | 101 | [[1, 3], [1, 3], [1, 3]] | [128, 448, 832] | [] | True |
| 101-persistent | deck_single | 101 | [[1, 3], [1, 3], [1, 3]] | [320, 448, 832] | [] | True |
| 101-persistent | iid_split | 101 | [[1, 3], [1, 3], [1, 3]] | [128, 448, 832] | [] | True |
| 101-persistent | deck_split | 101 | [[1, 3], [1, 3], [1, 3]] | [320, 448, 832] | [] | True |
| 102-reversible | iid_single | 100 | [[], [0, 4], [0, 4]] | [None, None, 896] | [] | False |
| 102-reversible | deck_single | 100 | [[0, 4], [0, 4], [0, 4]] | [128, None, 896] | [] | False |
| 102-reversible | iid_split | 100 | [[], [0, 4], [0, 4]] | [None, None, 896] | [] | False |
| 102-reversible | deck_split | 100 | [[0, 4], [0, 4], [0, 4]] | [128, None, 896] | [] | False |
| 102-reversible | iid_single | 101 | [[], [0], []] | [None, 512, None] | [] | False |
| 102-reversible | deck_single | 101 | [[0, 4], [0], [0, 4]] | [256, 512, 1088] | [448] | True |
| 102-reversible | iid_split | 101 | [[], [0], []] | [None, 512, None] | [] | False |
| 102-reversible | deck_split | 101 | [[0, 4], [0], [0, 4]] | [256, 512, 1088] | [448] | True |
| 102-persistent | iid_single | 100 | [[], [0, 4], [0, 4]] | [None, 704, 832] | [] | False |
| 102-persistent | deck_single | 100 | [[0, 4], [0, 4], [0, 4]] | [128, 448, 832] | [] | True |
| 102-persistent | iid_split | 100 | [[], [0, 4], [0, 4]] | [None, 704, 832] | [] | False |
| 102-persistent | deck_split | 100 | [[0, 4], [0, 4], [0, 4]] | [128, 448, 832] | [] | True |
| 102-persistent | iid_single | 101 | [[], [], []] | [None, None, None] | [] | False |
| 102-persistent | deck_single | 101 | [[0, 4], [0, 4], [0, 4]] | [256, 448, 832] | [] | True |
| 102-persistent | iid_split | 101 | [[], [], []] | [None, None, None] | [] | False |
| 102-persistent | deck_split | 101 | [[0, 4], [0, 4], [0, 4]] | [256, 448, 832] | [] | True |
| 103-reversible | iid_single | 100 | [[3, 5], [3], [3, 5]] | [64, 512, 960] | [448] | True |
| 103-reversible | deck_single | 100 | [[3, 5], [3], [3, 5]] | [256, 512, 960] | [448] | True |
| 103-reversible | iid_split | 100 | [[3, 5], [1, 3], [3, 5]] | [64, None, 960] | [512] | False |
| 103-reversible | deck_split | 100 | [[3, 5], [1, 3], [3, 5]] | [256, None, 960] | [512] | False |
| 103-reversible | iid_single | 101 | [[3, 5], [3], [3, 5]] | [256, 512, 1024] | [512] | True |
| 103-reversible | deck_single | 101 | [[3, 5], [3], [3, 5]] | [256, 640, 1024] | [448] | True |
| 103-reversible | iid_split | 101 | [[3, 5], [3], [3, 5]] | [256, 512, 1024] | [512] | True |
| 103-reversible | deck_split | 101 | [[3, 5], [3], [3, 5]] | [256, 640, 1024] | [512] | True |
| 103-persistent | iid_single | 100 | [[3, 5], [3, 5], [3, 5]] | [64, 448, 832] | [] | True |
| 103-persistent | deck_single | 100 | [[3, 5], [3, 5], [3, 5]] | [256, 448, 832] | [] | True |
| 103-persistent | iid_split | 100 | [[3, 5], [3, 5], [3, 5]] | [64, 448, 832] | [] | True |
| 103-persistent | deck_split | 100 | [[3, 5], [3, 5], [3, 5]] | [256, 448, 832] | [] | True |
| 103-persistent | iid_single | 101 | [[3, 5], [3, 5], [3, 5]] | [256, 448, 832] | [] | True |
| 103-persistent | deck_single | 101 | [[3, 5], [3, 5], [3, 5]] | [256, 448, 832] | [] | True |
| 103-persistent | iid_split | 101 | [[3, 5], [3, 5], [3, 5]] | [256, 448, 832] | [] | True |
| 103-persistent | deck_split | 101 | [[3, 5], [3, 5], [3, 5]] | [256, 448, 832] | [] | True |
| 104-reversible | iid_single | 100 | [[0, 3], [0], [2]] | [256, 512, None] | [448] | False |
| 104-reversible | deck_single | 100 | [[0, 3], [0, 5], [0, 3]] | [192, None, 1024] | [448] | False |
| 104-reversible | iid_split | 100 | [[0, 3], [0, 5], [0, 3]] | [256, None, 960] | [448] | False |
| 104-reversible | deck_split | 100 | [[0, 3], [0, 5], [0, 3]] | [192, None, 960] | [448] | False |
| 104-reversible | iid_single | 101 | [[], [0], [0, 3]] | [None, 512, 1024] | [] | False |
| 104-reversible | deck_single | 101 | [[0, 3], [0], []] | [64, 512, None] | [448] | False |
| 104-reversible | iid_split | 101 | [[], [0], [0, 3]] | [None, 512, 1024] | [] | False |
| 104-reversible | deck_split | 101 | [[], [0], []] | [None, 512, None] | [] | False |
| 104-persistent | iid_single | 100 | [[0, 3], [0, 3], [0, 3]] | [256, 448, 832] | [] | True |
| 104-persistent | deck_single | 100 | [[0, 3], [0, 3], [0, 3]] | [192, 448, 832] | [] | True |
| 104-persistent | iid_split | 100 | [[0, 3], [0, 3], [0, 3]] | [256, 448, 832] | [] | True |
| 104-persistent | deck_split | 100 | [[0, 3], [0, 3], [0, 3]] | [192, 448, 832] | [] | True |
| 104-persistent | iid_single | 101 | [[], [0, 3], [0, 3]] | [None, 640, 832] | [] | False |
| 104-persistent | deck_single | 101 | [[0, 3], [0, 3], [0, 3]] | [64, 448, 832] | [] | True |
| 104-persistent | iid_split | 101 | [[], [0, 3], [0, 3]] | [None, 640, 832] | [] | False |
| 104-persistent | deck_split | 101 | [[], [0, 3], [0, 3]] | [None, 576, 832] | [] | False |

## Resource accounting

```json
{
  "runs": 80,
  "generated_world_records": 17280,
  "outcome_presentations": 138240,
  "base_evaluation_predictions": 184320,
  "additional_ablation_predictions": 264064,
  "costs": {
    "main_prediction_feature_reads": 122624,
    "count_refits": 92160,
    "count_refit_rows": 16227840,
    "refit_feature_reads": 23283968,
    "candidate_fits": 5760,
    "candidate_fit_rows": 1044480,
    "candidate_fit_feature_reads": 1730816,
    "candidate_score_feature_reads": 1730816,
    "selection_outcomes": 46080,
    "selection_prediction_feature_reads": 119584
  }
}
```

Complete traces and paired differences are in results.json and metrics.json.
No learning of the proposal rule or gate; no learned interface or meta-learning.
