# Experiment 012: hiding versus deleting predictive detail

Primary criterion: **PASS**.

| Branch | Variant | Acquisition /10 | Trajectory /10 | Endpoint losses | Return-192 loss | Prediction features | Retrievals |
| --- | --- | ---: | ---: | --- | ---: | ---: | ---: |
| return | retain | 9 | 9 | 0.386941 / 0.374619 / 0.377188 | 0.569511 | 1.3833 | 10 |
| return | delete | 9 | 9 | 0.386941 / 0.374619 / 0.377188 | 0.647676 | 1.3417 | 0 |
| return | open | 9 | 0 | 0.386941 / 0.380519 / 0.377679 | 0.593616 | 1.9000 | 0 |
| novel | retain | 9 | 9 | 0.386941 / 0.374619 / 0.377188 | 0.663578 | 1.3333 | 1 |
| novel | delete | 9 | 9 | 0.386941 / 0.374619 / 0.377188 | 0.663578 | 1.3250 | 0 |
| novel | open | 9 | 0 | 0.386941 / 0.380519 / 0.377679 | 0.600678 | 1.9000 | 0 |
| persistent | retain | 9 | 9 | 0.386941 / 0.379706 / 0.377188 | 0.376358 | 1.8083 | 0 |
| persistent | delete | 9 | 9 | 0.386941 / 0.379706 / 0.377188 | 0.376358 | 1.8083 | 0 |
| persistent | open | 9 | 9 | 0.386941 / 0.380519 / 0.377679 | 0.377014 | 1.9000 | 0 |

Open is not expected to pass the reduced-interface criterion in return/novel.
Counts include failed acquisition; accuracy is against the most probable noisy-world outcome.

## Per-run transitions

| World | Variant | Proposal seed | Parent | Hide | Reopen | Retrieve | Delete | Recovery | Pass |
| --- | --- | ---: | --- | --- | --- | --- | --- | --- | --- |
| 200-return | retain | 200 | [3, 4] | [448, 768] | [704, 832] | [832] | [] | 832 | True |
| 200-return | delete | 200 | [3, 4] | [448, 768] | [704, 832] | [] | [448] | 960 | True |
| 200-return | open | 200 | [3, 4] | [] | [] | [] | [] | 960 | False |
| 200-return | retain | 201 | [3, 4] | [448, 768] | [704, 832] | [832] | [] | 832 | True |
| 200-return | delete | 201 | [3, 4] | [448, 768] | [704, 832] | [] | [448] | 960 | True |
| 200-return | open | 201 | [3, 4] | [] | [] | [] | [] | 960 | False |
| 200-novel | retain | 200 | [3, 4] | [448, 768] | [704, 832] | [] | [] | 896 | True |
| 200-novel | delete | 200 | [3, 4] | [448, 768] | [704, 832] | [] | [448] | 896 | True |
| 200-novel | open | 200 | [3, 4] | [] | [] | [] | [] | 896 | False |
| 200-novel | retain | 201 | [3, 4] | [448, 768] | [704, 832] | [] | [] | 896 | True |
| 200-novel | delete | 201 | [3, 4] | [448, 768] | [704, 832] | [] | [448] | 896 | True |
| 200-novel | open | 201 | [3, 4] | [] | [] | [] | [] | 896 | False |
| 200-persistent | retain | 200 | [3, 4] | [] | [] | [] | [] | 832 | True |
| 200-persistent | delete | 200 | [3, 4] | [] | [] | [] | [] | 832 | True |
| 200-persistent | open | 200 | [3, 4] | [] | [] | [] | [] | 832 | True |
| 200-persistent | retain | 201 | [3, 4] | [] | [] | [] | [] | 832 | True |
| 200-persistent | delete | 201 | [3, 4] | [] | [] | [] | [] | 832 | True |
| 200-persistent | open | 201 | [3, 4] | [] | [] | [] | [] | 832 | True |
| 201-return | retain | 200 | [4, 5] | [448] | [832] | [832] | [] | 832 | True |
| 201-return | delete | 200 | [4, 5] | [448] | [832] | [] | [448] | 896 | True |
| 201-return | open | 200 | [4, 5] | [] | [] | [] | [] | 896 | False |
| 201-return | retain | 201 | [4, 5] | [448] | [832] | [832] | [] | 832 | True |
| 201-return | delete | 201 | [4, 5] | [448] | [832] | [] | [448] | 896 | True |
| 201-return | open | 201 | [4, 5] | [] | [] | [] | [] | 896 | False |
| 201-novel | retain | 200 | [4, 5] | [448] | [832] | [] | [] | 960 | True |
| 201-novel | delete | 200 | [4, 5] | [448] | [832] | [] | [448] | 960 | True |
| 201-novel | open | 200 | [4, 5] | [] | [] | [] | [] | 960 | False |
| 201-novel | retain | 201 | [4, 5] | [448] | [832] | [] | [] | 960 | True |
| 201-novel | delete | 201 | [4, 5] | [448] | [832] | [] | [448] | 960 | True |
| 201-novel | open | 201 | [4, 5] | [] | [] | [] | [] | 960 | False |
| 201-persistent | retain | 200 | [4, 5] | [] | [] | [] | [] | 832 | True |
| 201-persistent | delete | 200 | [4, 5] | [] | [] | [] | [] | 832 | True |
| 201-persistent | open | 200 | [4, 5] | [] | [] | [] | [] | 832 | True |
| 201-persistent | retain | 201 | [4, 5] | [] | [] | [] | [] | 832 | True |
| 201-persistent | delete | 201 | [4, 5] | [] | [] | [] | [] | 832 | True |
| 201-persistent | open | 201 | [4, 5] | [] | [] | [] | [] | 832 | True |
| 202-return | retain | 200 | [0, 1] | [448] | [832] | [832] | [] | 832 | True |
| 202-return | delete | 200 | [0, 1] | [448] | [832] | [] | [448] | 960 | True |
| 202-return | open | 200 | [0, 1] | [] | [] | [] | [] | 960 | False |
| 202-return | retain | 201 | [0, 1] | [448] | [832] | [832] | [] | 832 | True |
| 202-return | delete | 201 | [0, 1] | [448] | [832] | [] | [448] | 960 | True |
| 202-return | open | 201 | [0, 1] | [] | [] | [] | [] | 960 | False |
| 202-novel | retain | 200 | [0, 1] | [448] | [896] | [] | [] | 896 | True |
| 202-novel | delete | 200 | [0, 1] | [448] | [896] | [] | [448] | 896 | True |
| 202-novel | open | 200 | [0, 1] | [] | [] | [] | [] | 896 | False |
| 202-novel | retain | 201 | [0, 1] | [448] | [896] | [] | [] | 896 | True |
| 202-novel | delete | 201 | [0, 1] | [448] | [896] | [] | [448] | 896 | True |
| 202-novel | open | 201 | [0, 1] | [] | [] | [] | [] | 896 | False |
| 202-persistent | retain | 200 | [0, 1] | [] | [] | [] | [] | 832 | True |
| 202-persistent | delete | 200 | [0, 1] | [] | [] | [] | [] | 832 | True |
| 202-persistent | open | 200 | [0, 1] | [] | [] | [] | [] | 832 | True |
| 202-persistent | retain | 201 | [0, 1] | [] | [] | [] | [] | 832 | True |
| 202-persistent | delete | 201 | [0, 1] | [] | [] | [] | [] | 832 | True |
| 202-persistent | open | 201 | [0, 1] | [] | [] | [] | [] | 832 | True |
| 203-return | retain | 200 | [1, 2] | [448] | [832] | [832] | [] | 832 | True |
| 203-return | delete | 200 | [1, 2] | [448] | [896] | [] | [448] | 960 | True |
| 203-return | open | 200 | [1, 2] | [] | [] | [] | [] | 960 | False |
| 203-return | retain | 201 | [1, 2] | [448] | [832] | [832] | [] | 832 | True |
| 203-return | delete | 201 | [1, 2] | [448] | [896] | [] | [448] | 960 | True |
| 203-return | open | 201 | [1, 2] | [] | [] | [] | [] | 960 | False |
| 203-novel | retain | 200 | [1, 2] | [448] | [832] | [] | [] | 960 | True |
| 203-novel | delete | 200 | [1, 2] | [448] | [832] | [] | [448] | 960 | True |
| 203-novel | open | 200 | [1, 2] | [] | [] | [] | [] | 960 | False |
| 203-novel | retain | 201 | [1, 2] | [448] | [832] | [] | [] | 960 | True |
| 203-novel | delete | 201 | [1, 2] | [448] | [832] | [] | [448] | 960 | True |
| 203-novel | open | 201 | [1, 2] | [] | [] | [] | [] | 960 | False |
| 203-persistent | retain | 200 | [1, 2] | [] | [] | [] | [] | 832 | True |
| 203-persistent | delete | 200 | [1, 2] | [] | [] | [] | [] | 832 | True |
| 203-persistent | open | 200 | [1, 2] | [] | [] | [] | [] | 832 | True |
| 203-persistent | retain | 201 | [1, 2] | [] | [] | [] | [] | 832 | True |
| 203-persistent | delete | 201 | [1, 2] | [] | [] | [] | [] | 832 | True |
| 203-persistent | open | 201 | [1, 2] | [] | [] | [] | [] | 832 | True |
| 204-return | retain | 200 | [3] | [448, 768] | [704] | [704] | [] | None | False |
| 204-return | delete | 200 | [3] | [448] | [] | [] | [448] | None | False |
| 204-return | open | 200 | [3] | [] | [] | [] | [] | None | False |
| 204-return | retain | 201 | [2, 3] | [448] | [832] | [832] | [] | 832 | True |
| 204-return | delete | 201 | [2, 3] | [448] | [832] | [] | [448] | 960 | True |
| 204-return | open | 201 | [2, 3] | [] | [] | [] | [] | 960 | False |
| 204-novel | retain | 200 | [3] | [448, 768] | [704] | [704] | [] | None | False |
| 204-novel | delete | 200 | [3] | [448] | [] | [] | [448] | None | False |
| 204-novel | open | 200 | [3] | [] | [] | [] | [] | None | False |
| 204-novel | retain | 201 | [2, 3] | [448] | [896] | [] | [] | 960 | True |
| 204-novel | delete | 201 | [2, 3] | [448] | [896] | [] | [448] | 960 | True |
| 204-novel | open | 201 | [2, 3] | [] | [] | [] | [] | 960 | False |
| 204-persistent | retain | 200 | [3] | [448] | [] | [] | [] | None | False |
| 204-persistent | delete | 200 | [3] | [448] | [] | [] | [448] | None | False |
| 204-persistent | open | 200 | [3] | [] | [] | [] | [] | None | False |
| 204-persistent | retain | 201 | [2, 3] | [] | [] | [] | [] | 832 | True |
| 204-persistent | delete | 201 | [2, 3] | [] | [] | [] | [] | 832 | True |
| 204-persistent | open | 201 | [2, 3] | [] | [] | [] | [] | 832 | True |

## Primary checks

```json
{
  "trajectories": true,
  "return_improved_count": true,
  "return_mean_gain": true,
  "novel_cost_guard": true,
  "persistent_cost_guard": true
}
```

## Resources

```json
{
  "runs": 90,
  "generated_world_records": 25920,
  "allocated_outcome_presentations": 155520,
  "used_outcome_presentations": 144000,
  "base_evaluation_predictions": 207360,
  "additional_ablation_predictions": 304512,
  "costs": {
    "main_prediction_feature_reads": 141696,
    "count_refits": 102400,
    "count_refit_rows": 18010560,
    "refit_feature_reads": 26336640,
    "candidate_fits": 4196,
    "candidate_fit_rows": 736512,
    "candidate_fit_feature_reads": 916800,
    "candidate_score_feature_reads": 724864,
    "selection_outcomes": 40320,
    "selection_prediction_feature_reads": 93408,
    "prototype_candidate_scores": 138,
    "prototype_selection_predictions": 544,
    "main_prototype_steps": 1280
  }
}
```
