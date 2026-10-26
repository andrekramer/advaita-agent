# Experiment 019: complete descriptive report

Derived from the frozen benchmark artifacts. Audit status is recorded separately in `audit.json`.

## All variant groups

Counts are out of ten runs (five environments, two proposal seeds). Stable means every review from 1024 through 1280. Structural stability also requires successful transfer.

| History | Variant | Transfer | Trajectory by 768 | Stable prediction | Stable full validity | Stable structure | Captures retained | Retrieval events | Late latent loss | Late raw reads |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| forms | integrated | 10 | 0 | 10 | 9 | 6 | 16 | 4 | 0.346183 | 25.6 |
| forms | delete | 10 | 0 | 9 | 9 | 7 | 0 | 0 | 0.345238 | 19.2 |
| forms | raw | 0 | 0 | 6 | 6 | 0 | 0 | 0 | 0.387380 | 512.0 |
| forms | fixed | 10 | 0 | 10 | 10 | 8 | 16 | 2 | 0.344772 | 19.2 |
| detail | integrated | 10 | 4 | 10 | 9 | 9 | 4 | 0 | 0.359122 | 256.0 |
| detail | delete | 10 | 4 | 10 | 9 | 9 | 0 | 0 | 0.359122 | 256.0 |
| detail | raw | 0 | 0 | 4 | 4 | 0 | 0 | 0 | 0.387380 | 512.0 |
| detail | fixed | 10 | 4 | 10 | 10 | 10 | 4 | 0 | 0.359122 | 256.0 |
| reversed | integrated | 10 | 4 | 10 | 9 | 9 | 4 | 0 | 0.359122 | 256.0 |
| reversed | delete | 10 | 4 | 10 | 9 | 9 | 0 | 0 | 0.359122 | 256.0 |
| reversed | raw | 0 | 0 | 4 | 4 | 0 | 0 | 0 | 0.387380 | 512.0 |
| reversed | fixed | 10 | 4 | 10 | 10 | 10 | 4 | 0 | 0.359122 | 256.0 |

## All paired memory comparisons

Positive gain means lower loss with retention. Identical refers to all 1280 pre-update predictions; it does not require identical final post-review states.

| History | Environment | Proposal | Early observed gain | Return observed gain | Return latent gain | Late observed gain | Late latent gain | Identical predictions | Late read saving vs raw |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- | ---: |
| detail | 800 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 800 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 800 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 800 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 800 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 800 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 801 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 801 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 801 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 801 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 801 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 801 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 802 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 802 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 802 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 802 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 802 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 384 |
| reversed | 802 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 803 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 803 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 803 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 803 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 803 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 512 |
| reversed | 803 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 804 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 804 | 800 | 0.000000 | -0.003131 | -0.003216 | -0.009197 | -0.009448 | False | 448 |
| reversed | 804 | 800 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| detail | 804 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |
| forms | 804 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 448 |
| reversed | 804 | 801 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | 0.000000 | True | 256 |

## Environment-level aggregation

Each row averages the two proposal seeds. Paired detail/reversed rows share a history until record 528.

| History | Environment | Proposal draws | Stable integrated structures | Mean return gain |
| --- | ---: | ---: | ---: | ---: |
| detail | 800 | 2 | 1 | 0.000000 |
| forms | 800 | 2 | 1 | 0.000000 |
| reversed | 800 | 2 | 1 | 0.000000 |
| detail | 801 | 2 | 2 | 0.000000 |
| forms | 801 | 2 | 2 | 0.000000 |
| reversed | 801 | 2 | 2 | 0.000000 |
| detail | 802 | 2 | 2 | 0.000000 |
| forms | 802 | 2 | 1 | 0.000000 |
| reversed | 802 | 2 | 2 | 0.000000 |
| detail | 803 | 2 | 2 | 0.000000 |
| forms | 803 | 2 | 2 | 0.000000 |
| reversed | 803 | 2 | 2 | 0.000000 |
| detail | 804 | 2 | 2 | 0.000000 |
| forms | 804 | 2 | 0 | -0.001565 |
| reversed | 804 | 2 | 2 | 0.000000 |

## Every run

| History | Environment | Proposal | Variant | Structural at 768 / 1024 / 1280 | Stable prediction | Stable structure | Return observed loss |
| --- | ---: | ---: | --- | --- | --- | --- | ---: |
| forms | 800 | 800 | integrated | 0 / 1 / 0 | True | False | 0.439755 |
| forms | 800 | 800 | delete | 0 / 1 / 0 | False | False | 0.439755 |
| forms | 800 | 800 | raw | 0 / 0 / 0 | True | False | 0.461040 |
| forms | 800 | 800 | fixed | 0 / 1 / 1 | True | True | 0.428856 |
| forms | 800 | 801 | integrated | 0 / 1 / 1 | True | True | 0.436040 |
| forms | 800 | 801 | delete | 0 / 1 / 1 | True | True | 0.436040 |
| forms | 800 | 801 | raw | 0 / 0 / 0 | True | False | 0.461040 |
| forms | 800 | 801 | fixed | 0 / 1 / 1 | True | True | 0.428856 |
| detail | 800 | 800 | integrated | 1 / 1 / 0 | True | False | 0.442833 |
| detail | 800 | 800 | delete | 1 / 1 / 0 | True | False | 0.442833 |
| detail | 800 | 800 | raw | 0 / 0 / 0 | True | False | 0.463083 |
| detail | 800 | 800 | fixed | 1 / 1 / 1 | True | True | 0.442833 |
| detail | 800 | 801 | integrated | 1 / 1 / 1 | True | True | 0.458820 |
| detail | 800 | 801 | delete | 1 / 1 / 1 | True | True | 0.458820 |
| detail | 800 | 801 | raw | 0 / 0 / 0 | True | False | 0.463083 |
| detail | 800 | 801 | fixed | 1 / 1 / 1 | True | True | 0.458820 |
| reversed | 800 | 800 | integrated | 1 / 1 / 0 | True | False | 0.444467 |
| reversed | 800 | 800 | delete | 1 / 1 / 0 | True | False | 0.444467 |
| reversed | 800 | 800 | raw | 0 / 0 / 0 | True | False | 0.455272 |
| reversed | 800 | 800 | fixed | 1 / 1 / 1 | True | True | 0.444467 |
| reversed | 800 | 801 | integrated | 1 / 1 / 1 | True | True | 0.463052 |
| reversed | 800 | 801 | delete | 1 / 1 / 1 | True | True | 0.463052 |
| reversed | 800 | 801 | raw | 0 / 0 / 0 | True | False | 0.455272 |
| reversed | 800 | 801 | fixed | 1 / 1 / 1 | True | True | 0.463052 |
| forms | 801 | 800 | integrated | 1 / 1 / 1 | True | True | 0.412725 |
| forms | 801 | 800 | delete | 1 / 1 / 1 | True | True | 0.412725 |
| forms | 801 | 800 | raw | 0 / 0 / 0 | True | False | 0.439459 |
| forms | 801 | 800 | fixed | 1 / 1 / 1 | True | True | 0.434253 |
| forms | 801 | 801 | integrated | 1 / 1 / 1 | True | True | 0.412725 |
| forms | 801 | 801 | delete | 1 / 1 / 1 | True | True | 0.412725 |
| forms | 801 | 801 | raw | 0 / 0 / 0 | True | False | 0.439459 |
| forms | 801 | 801 | fixed | 1 / 1 / 1 | True | True | 0.434253 |
| detail | 801 | 800 | integrated | 1 / 1 / 1 | True | True | 0.463440 |
| detail | 801 | 800 | delete | 1 / 1 / 1 | True | True | 0.463440 |
| detail | 801 | 800 | raw | 0 / 0 / 0 | False | False | 0.442559 |
| detail | 801 | 800 | fixed | 1 / 1 / 1 | True | True | 0.463440 |
| detail | 801 | 801 | integrated | 1 / 1 / 1 | True | True | 0.434631 |
| detail | 801 | 801 | delete | 1 / 1 / 1 | True | True | 0.434631 |
| detail | 801 | 801 | raw | 0 / 0 / 0 | False | False | 0.442559 |
| detail | 801 | 801 | fixed | 1 / 1 / 1 | True | True | 0.434631 |
| reversed | 801 | 800 | integrated | 1 / 1 / 1 | True | True | 0.456299 |
| reversed | 801 | 800 | delete | 1 / 1 / 1 | True | True | 0.456299 |
| reversed | 801 | 800 | raw | 0 / 0 / 0 | False | False | 0.432687 |
| reversed | 801 | 800 | fixed | 1 / 1 / 1 | True | True | 0.456299 |
| reversed | 801 | 801 | integrated | 1 / 1 / 1 | True | True | 0.421652 |
| reversed | 801 | 801 | delete | 1 / 1 / 1 | True | True | 0.421652 |
| reversed | 801 | 801 | raw | 0 / 0 / 0 | False | False | 0.432687 |
| reversed | 801 | 801 | fixed | 1 / 1 / 1 | True | True | 0.421652 |
| forms | 802 | 800 | integrated | 1 / 1 / 1 | True | True | 0.407764 |
| forms | 802 | 800 | delete | 1 / 1 / 1 | True | True | 0.407764 |
| forms | 802 | 800 | raw | 0 / 0 / 0 | True | False | 0.422800 |
| forms | 802 | 800 | fixed | 0 / 1 / 1 | True | True | 0.388182 |
| forms | 802 | 801 | integrated | 0 / 0 / 1 | True | False | 0.431587 |
| forms | 802 | 801 | delete | 0 / 0 / 1 | True | False | 0.431587 |
| forms | 802 | 801 | raw | 0 / 0 / 0 | True | False | 0.422800 |
| forms | 802 | 801 | fixed | 0 / 1 / 1 | True | True | 0.392055 |
| detail | 802 | 800 | integrated | 1 / 1 / 1 | True | True | 0.381050 |
| detail | 802 | 800 | delete | 1 / 1 / 1 | True | True | 0.381050 |
| detail | 802 | 800 | raw | 0 / 0 / 0 | False | False | 0.418062 |
| detail | 802 | 800 | fixed | 1 / 1 / 1 | True | True | 0.381050 |
| detail | 802 | 801 | integrated | 0 / 1 / 1 | True | True | 0.476833 |
| detail | 802 | 801 | delete | 0 / 1 / 1 | True | True | 0.476833 |
| detail | 802 | 801 | raw | 0 / 0 / 0 | False | False | 0.418062 |
| detail | 802 | 801 | fixed | 1 / 1 / 1 | True | True | 0.414513 |
| reversed | 802 | 800 | integrated | 1 / 1 / 1 | True | True | 0.385945 |
| reversed | 802 | 800 | delete | 1 / 1 / 1 | True | True | 0.385945 |
| reversed | 802 | 800 | raw | 0 / 0 / 0 | True | False | 0.416039 |
| reversed | 802 | 800 | fixed | 1 / 1 / 1 | True | True | 0.385945 |
| reversed | 802 | 801 | integrated | 0 / 1 / 1 | True | True | 0.478109 |
| reversed | 802 | 801 | delete | 0 / 1 / 1 | True | True | 0.478109 |
| reversed | 802 | 801 | raw | 0 / 0 / 0 | True | False | 0.416039 |
| reversed | 802 | 801 | fixed | 1 / 1 / 1 | True | True | 0.414036 |
| forms | 803 | 800 | integrated | 1 / 1 / 1 | True | True | 0.465556 |
| forms | 803 | 800 | delete | 1 / 1 / 1 | True | True | 0.465556 |
| forms | 803 | 800 | raw | 0 / 0 / 0 | False | False | 0.463468 |
| forms | 803 | 800 | fixed | 1 / 1 / 1 | True | True | 0.436863 |
| forms | 803 | 801 | integrated | 1 / 1 / 1 | True | True | 0.436991 |
| forms | 803 | 801 | delete | 1 / 1 / 1 | True | True | 0.436991 |
| forms | 803 | 801 | raw | 0 / 0 / 0 | False | False | 0.463468 |
| forms | 803 | 801 | fixed | 1 / 1 / 1 | True | True | 0.436863 |
| detail | 803 | 800 | integrated | 1 / 1 / 1 | True | True | 0.481285 |
| detail | 803 | 800 | delete | 1 / 1 / 1 | True | True | 0.481285 |
| detail | 803 | 800 | raw | 0 / 0 / 0 | False | False | 0.486580 |
| detail | 803 | 800 | fixed | 1 / 1 / 1 | True | True | 0.481285 |
| detail | 803 | 801 | integrated | 1 / 1 / 1 | True | True | 0.496211 |
| detail | 803 | 801 | delete | 1 / 1 / 1 | True | True | 0.496211 |
| detail | 803 | 801 | raw | 0 / 0 / 0 | False | False | 0.486580 |
| detail | 803 | 801 | fixed | 1 / 1 / 1 | True | True | 0.496211 |
| reversed | 803 | 800 | integrated | 1 / 1 / 1 | True | True | 0.475833 |
| reversed | 803 | 800 | delete | 1 / 1 / 1 | True | True | 0.475833 |
| reversed | 803 | 800 | raw | 0 / 0 / 0 | False | False | 0.471732 |
| reversed | 803 | 800 | fixed | 1 / 1 / 1 | True | True | 0.475833 |
| reversed | 803 | 801 | integrated | 1 / 1 / 1 | True | True | 0.494669 |
| reversed | 803 | 801 | delete | 1 / 1 / 1 | True | True | 0.494669 |
| reversed | 803 | 801 | raw | 0 / 0 / 0 | False | False | 0.471732 |
| reversed | 803 | 801 | fixed | 1 / 1 / 1 | True | True | 0.494669 |
| forms | 804 | 800 | integrated | 0 / 1 / 0 | True | False | 0.411622 |
| forms | 804 | 800 | delete | 0 / 1 / 1 | True | True | 0.408491 |
| forms | 804 | 800 | raw | 0 / 0 / 0 | False | False | 0.444170 |
| forms | 804 | 800 | fixed | 0 / 1 / 0 | True | False | 0.414688 |
| forms | 804 | 801 | integrated | 0 / 1 / 0 | True | False | 0.413561 |
| forms | 804 | 801 | delete | 0 / 1 / 0 | True | False | 0.413561 |
| forms | 804 | 801 | raw | 0 / 0 / 0 | False | False | 0.444170 |
| forms | 804 | 801 | fixed | 0 / 1 / 0 | True | False | 0.410126 |
| detail | 804 | 800 | integrated | 1 / 1 / 1 | True | True | 0.490397 |
| detail | 804 | 800 | delete | 1 / 1 / 1 | True | True | 0.490397 |
| detail | 804 | 800 | raw | 0 / 0 / 0 | True | False | 0.458790 |
| detail | 804 | 800 | fixed | 1 / 1 / 1 | True | True | 0.490397 |
| detail | 804 | 801 | integrated | 1 / 1 / 1 | True | True | 0.456563 |
| detail | 804 | 801 | delete | 1 / 1 / 1 | True | True | 0.456563 |
| detail | 804 | 801 | raw | 0 / 0 / 0 | True | False | 0.458790 |
| detail | 804 | 801 | fixed | 1 / 1 / 1 | True | True | 0.456563 |
| reversed | 804 | 800 | integrated | 1 / 1 / 1 | True | True | 0.463815 |
| reversed | 804 | 800 | delete | 1 / 1 / 1 | True | True | 0.463815 |
| reversed | 804 | 800 | raw | 0 / 0 / 0 | False | False | 0.434014 |
| reversed | 804 | 800 | fixed | 1 / 1 / 1 | True | True | 0.463815 |
| reversed | 804 | 801 | integrated | 1 / 1 / 1 | True | True | 0.432119 |
| reversed | 804 | 801 | delete | 1 / 1 / 1 | True | True | 0.432119 |
| reversed | 804 | 801 | raw | 0 / 0 / 0 | False | False | 0.434014 |
| reversed | 804 | 801 | fixed | 1 / 1 / 1 | True | True | 0.432119 |

## Frozen criteria

```json
{
  "representation_checks": {
    "forms": false,
    "detail": true,
    "reversed": true
  },
  "representation_pass": false,
  "memory_checks": {
    "mean_gain": false,
    "improving_pairs": false,
    "reversed_cost": true
  },
  "memory_pass": false
}
```

## Resources

```json
{
  "runs": 120,
  "allocated_labels": 814080,
  "generated_labels": 101760,
  "used_labels": 641280,
  "candidate_fits": 23985,
  "scoring_queries": 3366144,
  "composite_predictions": 153600,
  "local_predictions": 230400,
  "evaluation_predictions": 91200,
  "oracle_context_queries": 361376
}
```
