# Experiment 018: complete fixed benchmark record

**Primary criterion: FAIL.** All 120 runs passed independent full-trace and checkpoint audit.

End-to-end trajectory criteria apply to the integrated learner. Controls are included to expose prediction, transfer, memory and structural differences; raw/fixed controls cannot perform all required structural operations by design.

| History | Variant | Transfer | Predictive endpoints 240 / 528 / 768 | Full minimal endpoints | Complete trajectories | Mean early-return observed loss | Mean hidden raw reads | Captures / retrievals |
| --- | --- | ---: | --- | --- | ---: | ---: | ---: | --- |
| forms | integrated | 10/10 | 10 / 10 / 8 | 9 / 2 / 0 | 0/10 | 0.729015 | 230.4 | 4 / 0 |
| forms | delete | 10/10 | 10 / 10 / 8 | 9 / 2 / 0 | 0/10 | 0.729015 | 230.4 | 4 / 0 |
| forms | raw | 0/10 | 10 / 10 / 8 | 0 / 0 / 0 | 0/10 | 0.702971 | 576.0 | 0 / 0 |
| forms | fixed | 10/10 | 10 / 10 / 8 | 10 / 0 / 0 | 0/10 | 0.732715 | 244.8 | 5 / 0 |
| detail | integrated | 10/10 | 9 / 10 / 10 | 9 / 3 / 10 | 3/10 | 0.750141 | 264.0 | 3 / 0 |
| detail | delete | 10/10 | 9 / 10 / 10 | 9 / 3 / 10 | 3/10 | 0.750141 | 264.0 | 3 / 0 |
| detail | raw | 0/10 | 10 / 10 / 6 | 0 / 0 / 0 | 0/10 | 0.709507 | 576.0 | 0 / 0 |
| detail | fixed | 10/10 | 10 / 10 / 10 | 10 / 3 / 10 | 3/10 | 0.754226 | 264.0 | 3 / 0 |
| reversed | integrated | 10/10 | 9 / 10 / 10 | 9 / 3 / 10 | 3/10 | 0.745544 | 264.0 | 3 / 0 |
| reversed | delete | 10/10 | 9 / 10 / 10 | 9 / 3 / 10 | 3/10 | 0.745544 | 264.0 | 3 / 0 |
| reversed | raw | 0/10 | 10 / 10 / 8 | 0 / 0 / 0 | 0/10 | 0.717237 | 576.0 | 0 / 0 |
| reversed | fixed | 10/10 | 10 / 10 / 10 | 10 / 3 / 10 | 3/10 | 0.750743 | 264.0 | 3 / 0 |

All endpoint counts are out of ten paired runs. Full minimal endpoints require exact local partitions, accurate upper prediction, the declared exposure/dependencies and oracle sufficiency/minimality checks.

## Frozen checks

```json
{
  "forms_trajectory": false,
  "detail_trajectory": false,
  "reversed_trajectory": false,
  "memory_mean_gain": false,
  "memory_pairs": false,
  "reversed_cost": true,
  "hidden_read_saving": true
}
```

## Paired memory comparisons

Positive return gain favours retained memory over deletion. Early-return window: records 529–656. Hidden-read saving compares integrated with raw during records 241–528.

| Environment | Proposal | History | Observed return gain | Latent return gain | Hidden-read saving |
| --- | --- | --- | ---: | ---: | ---: |
| 700 | 700 | detail | 0.000000 | 0.000000 | 288 |
| 700 | 700 | forms | 0.000000 | 0.000000 | 304 |
| 700 | 700 | reversed | 0.000000 | 0.000000 | 288 |
| 700 | 701 | detail | 0.000000 | 0.000000 | 288 |
| 700 | 701 | forms | 0.000000 | 0.000000 | 368 |
| 700 | 701 | reversed | 0.000000 | 0.000000 | 288 |
| 701 | 700 | detail | 0.000000 | 0.000000 | 288 |
| 701 | 700 | forms | 0.000000 | 0.000000 | 368 |
| 701 | 700 | reversed | 0.000000 | 0.000000 | 288 |
| 701 | 701 | detail | 0.000000 | 0.000000 | 288 |
| 701 | 701 | forms | 0.000000 | 0.000000 | 304 |
| 701 | 701 | reversed | 0.000000 | 0.000000 | 288 |
| 702 | 700 | detail | 0.000000 | 0.000000 | 288 |
| 702 | 700 | forms | 0.000000 | 0.000000 | 304 |
| 702 | 700 | reversed | 0.000000 | 0.000000 | 288 |
| 702 | 701 | detail | 0.000000 | 0.000000 | 368 |
| 702 | 701 | forms | 0.000000 | 0.000000 | 448 |
| 702 | 701 | reversed | 0.000000 | 0.000000 | 368 |
| 703 | 700 | detail | 0.000000 | 0.000000 | 368 |
| 703 | 700 | forms | 0.000000 | 0.000000 | 384 |
| 703 | 700 | reversed | 0.000000 | 0.000000 | 368 |
| 703 | 701 | detail | 0.000000 | 0.000000 | 368 |
| 703 | 701 | forms | 0.000000 | 0.000000 | 384 |
| 703 | 701 | reversed | 0.000000 | 0.000000 | 368 |
| 704 | 700 | detail | 0.000000 | 0.000000 | 288 |
| 704 | 700 | forms | 0.000000 | 0.000000 | 288 |
| 704 | 700 | reversed | 0.000000 | 0.000000 | 288 |
| 704 | 701 | detail | 0.000000 | 0.000000 | 288 |
| 704 | 701 | forms | 0.000000 | 0.000000 | 304 |
| 704 | 701 | reversed | 0.000000 | 0.000000 | 288 |

## Resources

```json
{
  "runs": 120,
  "allocated_labels": 537600,
  "generated_labels": 67200,
  "used_labels": 433920,
  "candidate_fits": 16056,
  "scoring_queries": 2145504,
  "composite_predictions": 92160,
  "local_predictions": 138240,
  "evaluation_predictions": 60480
}
```

## Every run

The three endpoint booleans refer to full minimal validity at 240,528,768. Collapse, recreation, capture and retrieval lists contain review indices.

| Environment | Proposal | History | Variant | Transfer | Endpoints | Trajectory | Final spec | Collapse / recreate | Capture / retrieve |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 700 | 700 | forms | integrated | True | [True, False, False] | False | [2, 1] | [] / [] | [] / [] |
| 700 | 700 | forms | delete | True | [True, False, False] | False | [2, 1] | [] / [] | [] / [] |
| 700 | 700 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 700 | 700 | forms | fixed | True | [True, False, False] | False | [2, 1] | [] / [] | [512] / [] |
| 700 | 701 | forms | integrated | True | [True, False, False] | False | [2, 1] | [] / [] | [] / [] |
| 700 | 701 | forms | delete | True | [True, False, False] | False | [2, 1] | [] / [] | [] / [] |
| 700 | 701 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 700 | 701 | forms | fixed | True | [True, False, False] | False | [2, 1] | [] / [] | [512] / [] |
| 700 | 700 | detail | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 700 | detail | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 700 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 700 | 700 | detail | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 701 | detail | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 701 | detail | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 701 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 700 | 701 | detail | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 700 | reversed | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 700 | reversed | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 700 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 700 | 700 | reversed | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 701 | reversed | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 701 | reversed | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 700 | 701 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 700 | 701 | reversed | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | forms | integrated | True | [True, False, False] | False | [1, 2] | [448] / [576] | [] / [] |
| 701 | 700 | forms | delete | True | [True, False, False] | False | [1, 2] | [448] / [576] | [] / [] |
| 701 | 700 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 701 | 700 | forms | fixed | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | forms | integrated | True | [True, False, False] | False | [1, 2] | [512] / [576] | [] / [] |
| 701 | 701 | forms | delete | True | [True, False, False] | False | [1, 2] | [512] / [576] | [] / [] |
| 701 | 701 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 701 | 701 | forms | fixed | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | detail | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | detail | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 701 | 700 | detail | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | detail | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | detail | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 701 | 701 | detail | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | reversed | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | reversed | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 700 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 701 | 700 | reversed | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | reversed | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | reversed | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 701 | 701 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 701 | 701 | reversed | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | forms | integrated | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | forms | delete | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 702 | 700 | forms | fixed | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 701 | forms | integrated | True | [True, False, False] | False | [2, 1] | [] / [] | [448] / [] |
| 702 | 701 | forms | delete | True | [True, False, False] | False | [2, 1] | [] / [] | [448] / [] |
| 702 | 701 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 702 | 701 | forms | fixed | True | [True, False, False] | False | [2, 1] | [] / [] | [448] / [] |
| 702 | 700 | detail | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | detail | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 702 | 700 | detail | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 701 | detail | integrated | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 702 | 701 | detail | delete | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 702 | 701 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 702 | 701 | detail | fixed | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 702 | 700 | reversed | integrated | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | reversed | delete | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 700 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 702 | 700 | reversed | fixed | True | [True, False, True] | False | [1, 2] | [] / [] | [] / [] |
| 702 | 701 | reversed | integrated | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 702 | 701 | reversed | delete | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 702 | 701 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 702 | 701 | reversed | fixed | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 700 | forms | integrated | True | [True, True, False] | False | [1, 2] | [512] / [576] | [512] / [] |
| 703 | 700 | forms | delete | True | [True, True, False] | False | [1, 2] | [512] / [576] | [512] / [] |
| 703 | 700 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 703 | 700 | forms | fixed | True | [True, False, False] | False | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | forms | integrated | True | [True, True, False] | False | [1, 2] | [512] / [576] | [448] / [] |
| 703 | 701 | forms | delete | True | [True, True, False] | False | [1, 2] | [512] / [576] | [448] / [] |
| 703 | 701 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 703 | 701 | forms | fixed | True | [True, False, False] | False | [2, 1] | [] / [] | [448] / [] |
| 703 | 700 | detail | integrated | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 700 | detail | delete | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 700 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 703 | 700 | detail | fixed | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | detail | integrated | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | detail | delete | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 703 | 701 | detail | fixed | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 700 | reversed | integrated | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 700 | reversed | delete | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 700 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 703 | 700 | reversed | fixed | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | reversed | integrated | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | reversed | delete | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 703 | 701 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 703 | 701 | reversed | fixed | True | [True, True, True] | True | [1, 2] | [] / [] | [448] / [] |
| 704 | 700 | forms | integrated | True | [False, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 704 | 700 | forms | delete | True | [False, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 704 | 700 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 704 | 700 | forms | fixed | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 704 | 701 | forms | integrated | True | [True, False, False] | False | [1, 2] | [] / [] | [192] / [] |
| 704 | 701 | forms | delete | True | [True, False, False] | False | [1, 2] | [] / [] | [192] / [] |
| 704 | 701 | forms | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 704 | 701 | forms | fixed | True | [True, False, False] | False | [1, 2] | [] / [] | [] / [] |
| 704 | 700 | detail | integrated | True | [False, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 700 | detail | delete | True | [False, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 700 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 704 | 700 | detail | fixed | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 701 | detail | integrated | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 701 | detail | delete | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 701 | detail | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 704 | 701 | detail | fixed | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 700 | reversed | integrated | True | [False, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 700 | reversed | delete | True | [False, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 700 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 704 | 700 | reversed | fixed | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 701 | reversed | integrated | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 701 | reversed | delete | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
| 704 | 701 | reversed | raw | False | [False, False, False] | False | [2, 2] | [] / [] | [] / [] |
| 704 | 701 | reversed | fixed | True | [True, False, True] | False | [2, 1] | [] / [] | [] / [] |
