# Experiment 017: complete fixed benchmark record

Primary combined criterion: **FAIL**. C2 progression gate: **PASS**, independently audited.

Each cell contains ten environment/proposal-seed pairs. Transfer tests 24 unseen compositions. Full final validity requires both local maps and the composite predictor to be valid; coarse validity additionally requires hidden raw detail.

| Condition | Variant | Transfer | Final full | Final coarse | Composite observed loss | Composite latent loss | Mean raw reads / 512 | Wrong-form bypass records |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| persistent | immediate_opening | 10/10 | 9/10 | 7/10 | 0.351043 | 0.343631 | 96.0 | 6.4 |
| persistent | immediate_reclosure | 10/10 | 9/10 | 8/10 | 0.350518 | 0.343522 | 44.8 | 6.4 |
| persistent | earned_opening | 9/10 | 10/10 | 8/10 | 0.355170 | 0.346841 | 51.2 | 0.0 |
| persistent | earned_reclosure | 9/10 | 10/10 | 10/10 | 0.354607 | 0.346896 | 25.6 | 0.0 |
| remap | immediate_opening | 10/10 | 9/10 | 5/10 | 0.454442 | 0.461964 | 172.8 | 38.4 |
| remap | immediate_reclosure | 10/10 | 9/10 | 8/10 | 0.458953 | 0.465562 | 115.2 | 38.4 |
| remap | earned_opening | 9/10 | 10/10 | 0/10 | 0.481021 | 0.485108 | 320.0 | 108.8 |
| remap | earned_reclosure | 9/10 | 10/10 | 10/10 | 0.481384 | 0.485618 | 230.4 | 108.8 |
| burst | immediate_opening | 10/10 | 9/10 | 0/10 | 0.361372 | 0.349668 | 332.8 | 83.2 |
| burst | immediate_reclosure | 10/10 | 9/10 | 8/10 | 0.358658 | 0.345969 | 172.8 | 83.2 |
| burst | earned_opening | 9/10 | 10/10 | 7/10 | 0.356224 | 0.346980 | 83.2 | 12.8 |
| burst | earned_reclosure | 9/10 | 10/10 | 10/10 | 0.356009 | 0.346764 | 44.8 | 12.8 |

## Earned protection minus immediate replacement

Costs are positive when protection is worse. Changes use records 129–512; burst loss uses 129–320. Invalid checkpoints count the affected local module at reviews 192–512.

| Upper policy | Condition | Composite change observed cost | Composite change latent cost | Local change latent cost | Confirmation delay | Raw-read difference | Invalid checkpoint difference |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| opening | persistent | -0.002246 | -0.001585 | 0.000000 | -6.400000 | -44.800000 | 0.000000 |
| opening | remap | 0.027691 | 0.024994 | 0.069240 | 76.800000 | 147.200000 | 1.200000 |
| opening | burst | -0.014612 | -0.009448 | -0.043751 | -6.400000 | -249.600000 | -1.000000 |
| reclosure | persistent | -0.002297 | -0.001367 | 0.000000 | -6.400000 | -19.200000 | 0.000000 |
| reclosure | remap | 0.022160 | 0.020876 | 0.069240 | 76.800000 | 115.200000 | 1.200000 |
| reclosure | burst | -0.011279 | -0.004804 | -0.043751 | -6.400000 | -128.000000 | -1.000000 |

## Factorial interaction

Each value is (earned reclosure − earned opening) − (immediate reclosure − immediate opening), averaged over the ten pairs. These descriptive interactions are not significance tests.

| Condition | Composite latent-loss interaction | Raw-read interaction | Affected-local checkpoint interaction |
| --- | ---: | ---: | ---: |
| persistent | 0.000164 | 25.6 | 0.0 |
| remap | -0.003088 | -32.0 | 0.0 |
| burst | 0.003483 | 121.6 | 0.0 |

## Fixed checks

```json
{
  "primary": {
    "opening": {
      "endpoint_validity": true,
      "persistent_loss": true,
      "remap_loss": false,
      "remap_delay": false,
      "burst_loss": true,
      "protection": true
    },
    "reclosure": {
      "endpoint_validity": true,
      "persistent_loss": true,
      "remap_loss": false,
      "remap_delay": false,
      "burst_loss": true,
      "protection": true
    }
  },
  "progression": {
    "persistent": true,
    "remap": true,
    "burst": true
  }
}
```

## Resources

```json
{
  "runs": 120,
  "generated_labels": 49920,
  "allocated_labels": 399360,
  "used_labels": 399360,
  "candidate_fits": 14400,
  "scoring_queries": 1540896,
  "composite_predictions": 61440,
  "local_predictions": 122880,
  "evaluation_predictions": 33600
}
```

## Every run

Times refer to adaptation records. A first valid checkpoint is distinct from the second checkpoint confirming recovery. No confirmation was censored in this benchmark.

| Environment | Proposal seed | Condition | Variant | Transfer | Final full | Final mode | First valid | Confirmed at | Invalid affected checkpoints | Reopen / reclose |
| --- | --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- |
| 600 | 600 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 600 | 600 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 600 | 600 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 600 | 600 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 600 | 601 | persistent | immediate_opening | True | True | fine0 | 128 | 192 | 0 | [64] / [] |
| 600 | 601 | persistent | immediate_reclosure | True | True | fine0 | 128 | 192 | 0 | [64, 448] / [192] |
| 600 | 601 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 600 | 601 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 600 | 600 | remap | immediate_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 600 | 600 | remap | immediate_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [320] |
| 600 | 600 | remap | earned_opening | True | True | fine1 | 384 | 448 | 3 | [192] / [] |
| 600 | 600 | remap | earned_reclosure | True | True | coarse | 384 | 448 | 3 | [192] / [448] |
| 600 | 601 | remap | immediate_opening | True | True | fine0 | 320 | 384 | 0 | [64] / [] |
| 600 | 601 | remap | immediate_reclosure | True | True | fine0 | 320 | 384 | 0 | [64, 448] / [320] |
| 600 | 601 | remap | earned_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 600 | 601 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [320] |
| 600 | 600 | burst | immediate_opening | True | True | fine1 | 256 | 320 | 1 | [192] / [] |
| 600 | 600 | burst | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [192] / [320] |
| 600 | 600 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 600 | 600 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 600 | 601 | burst | immediate_opening | True | True | fine0 | 256 | 320 | 1 | [64] / [] |
| 600 | 601 | burst | immediate_reclosure | True | True | fine0 | 256 | 320 | 1 | [64, 448] / [320] |
| 600 | 601 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 600 | 601 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 601 | 600 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 600 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 600 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 600 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 601 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 601 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 601 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 601 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 601 | 600 | remap | immediate_opening | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 601 | 600 | remap | immediate_reclosure | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 601 | 600 | remap | earned_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 601 | 600 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [448] |
| 601 | 601 | remap | immediate_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 601 | 601 | remap | immediate_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [448] |
| 601 | 601 | remap | earned_opening | True | True | fine1 | 320 | 384 | 2 | [192] / [] |
| 601 | 601 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 2 | [192] / [384] |
| 601 | 600 | burst | immediate_opening | True | True | fine1 | 256 | 320 | 1 | [192] / [] |
| 601 | 600 | burst | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [192] / [320] |
| 601 | 600 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 601 | 600 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 601 | 601 | burst | immediate_opening | True | True | fine1 | 256 | 320 | 1 | [192] / [] |
| 601 | 601 | burst | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [192] / [320] |
| 601 | 601 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 601 | 601 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 602 | 600 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 600 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 600 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 600 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 601 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 601 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 601 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 601 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 602 | 600 | remap | immediate_opening | True | True | coarse | 256 | 320 | 1 | [] / [] |
| 602 | 600 | remap | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [] / [] |
| 602 | 600 | remap | earned_opening | True | True | fine0 | 320 | 384 | 2 | [192] / [] |
| 602 | 600 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 2 | [192] / [384] |
| 602 | 601 | remap | immediate_opening | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 602 | 601 | remap | immediate_reclosure | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 602 | 601 | remap | earned_opening | True | True | fine0 | 320 | 384 | 1 | [192] / [] |
| 602 | 601 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [448] |
| 602 | 600 | burst | immediate_opening | True | True | fine0 | 256 | 320 | 1 | [192] / [] |
| 602 | 600 | burst | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [192] / [320] |
| 602 | 600 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 602 | 600 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 602 | 601 | burst | immediate_opening | True | True | fine0 | 256 | 320 | 1 | [192] / [] |
| 602 | 601 | burst | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [192] / [320] |
| 602 | 601 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 602 | 601 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 603 | 600 | persistent | immediate_opening | True | True | fine0 | 64 | 128 | 0 | [256] / [] |
| 603 | 600 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [256] / [384] |
| 603 | 600 | persistent | earned_opening | True | True | fine0 | 64 | 128 | 0 | [256] / [] |
| 603 | 600 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [256] / [384] |
| 603 | 601 | persistent | immediate_opening | True | False | fine0 | 64 | 128 | 0 | [256] / [] |
| 603 | 601 | persistent | immediate_reclosure | True | False | fine0 | 64 | 128 | 0 | [256, 512] / [384] |
| 603 | 601 | persistent | earned_opening | True | True | fine0 | 64 | 128 | 0 | [256] / [] |
| 603 | 601 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [256] / [384] |
| 603 | 600 | remap | immediate_opening | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 603 | 600 | remap | immediate_reclosure | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 603 | 600 | remap | earned_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 603 | 600 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [384] |
| 603 | 601 | remap | immediate_opening | True | False | fine0 | 320 | 384 | 1 | [192] / [] |
| 603 | 601 | remap | immediate_reclosure | True | False | fine0 | 320 | 384 | 1 | [192, 512] / [384] |
| 603 | 601 | remap | earned_opening | True | True | fine1 | 448 | 512 | 4 | [192] / [] |
| 603 | 601 | remap | earned_reclosure | True | True | coarse | 448 | 512 | 4 | [192] / [512] |
| 603 | 600 | burst | immediate_opening | True | True | fine1 | 256 | 320 | 1 | [192] / [] |
| 603 | 600 | burst | immediate_reclosure | True | True | coarse | 256 | 320 | 1 | [192] / [384] |
| 603 | 600 | burst | earned_opening | True | True | fine0 | 256 | 320 | 0 | [256] / [] |
| 603 | 600 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [256] / [384] |
| 603 | 601 | burst | immediate_opening | True | False | fine0 | 256 | 320 | 1 | [192] / [] |
| 603 | 601 | burst | immediate_reclosure | True | False | fine0 | 256 | 320 | 1 | [192, 512] / [384] |
| 603 | 601 | burst | earned_opening | True | True | fine0 | 256 | 320 | 0 | [256] / [] |
| 603 | 601 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [256] / [384] |
| 604 | 600 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 600 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 600 | persistent | earned_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 600 | persistent | earned_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 601 | persistent | immediate_opening | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 601 | persistent | immediate_reclosure | True | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 601 | persistent | earned_opening | False | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 601 | persistent | earned_reclosure | False | True | coarse | 64 | 128 | 0 | [] / [] |
| 604 | 600 | remap | immediate_opening | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 604 | 600 | remap | immediate_reclosure | True | True | coarse | 192 | 256 | 0 | [] / [] |
| 604 | 600 | remap | earned_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 604 | 600 | remap | earned_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [448] |
| 604 | 601 | remap | immediate_opening | True | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 604 | 601 | remap | immediate_reclosure | True | True | coarse | 320 | 384 | 1 | [192] / [448] |
| 604 | 601 | remap | earned_opening | False | True | fine1 | 320 | 384 | 1 | [192] / [] |
| 604 | 601 | remap | earned_reclosure | False | True | coarse | 320 | 384 | 1 | [192] / [448] |
| 604 | 600 | burst | immediate_opening | True | True | fine1 | 320 | 384 | 2 | [192] / [] |
| 604 | 600 | burst | immediate_reclosure | True | True | coarse | 320 | 384 | 2 | [192] / [384] |
| 604 | 600 | burst | earned_opening | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 604 | 600 | burst | earned_reclosure | True | True | coarse | 256 | 320 | 0 | [] / [] |
| 604 | 601 | burst | immediate_opening | True | True | fine1 | 320 | 384 | 2 | [192] / [] |
| 604 | 601 | burst | immediate_reclosure | True | True | coarse | 320 | 384 | 2 | [192] / [384] |
| 604 | 601 | burst | earned_opening | False | True | fine1 | 320 | 384 | 2 | [192] / [] |
| 604 | 601 | burst | earned_reclosure | False | True | coarse | 320 | 384 | 2 | [192] / [384] |
