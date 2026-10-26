# Experiment 020: complete descriptive report

All results are from the fixed benchmark; independent verification is recorded in `audit.json`. Counts are out of ten runs per history/policy, using five environments and two proposal draws each.

## Every group

| History | Policy | Transfer | Final full | Stable prediction | Stable full | Stable structure | Affected errors | Both-node errors | Late-node errors | Harmful replacements | Mean confirmed recovery |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| persistent | baseline | 10 | 8 | 9 | 7 | 3 | 9 | 19 | 3 | 13 | 268.8 |
| persistent | corroborated | 10 | 10 | 10 | 10 | 6 | 1 | 1 | 0 | 2 | 262.4 |
| burst | baseline | 10 | 8 | 10 | 7 | 3 | 23 | 26 | 3 | 20 | 435.2 |
| burst | corroborated | 10 | 10 | 10 | 10 | 6 | 4 | 4 | 0 | 2 | 281.6 |
| remap | baseline | 10 | 10 | 9 | 8 | 4 | 11 | 21 | 2 | 12 | 288.0 |
| remap | corroborated | 10 | 10 | 10 | 10 | 4 | 10 | 10 | 0 | 2 | 377.6 |

Affected errors use reviews 192–1280 for persistent/remap, 192–512 for burst. Stable metrics use every review 1024–1280. Confirmed recovery means the second consecutive fully valid review after 128; it is a genuine-change recovery measure only in remap.

## Loss, bypass and memory

Loss windows: persistent 1–1280, burst 129–320, remap 129–512. Raw reads and wrong-form bypass cover all main records.

| History | Policy | Observed composite | Latent composite | Affected latent | Late composite latent | Mean raw reads | Mean bypass records | Captures | Retrievals |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| persistent | baseline | 0.327009 | 0.346269 | 0.340327 | 0.340111 | 262.4 | 89.6 | 8 | 2 |
| persistent | corroborated | 0.321198 | 0.340561 | 0.332935 | 0.338981 | 115.2 | 6.4 | 6 | 0 |
| burst | baseline | 0.451849 | 0.477580 | 0.546446 | 0.341271 | 492.8 | 166.4 | 18 | 1 |
| burst | corroborated | 0.336093 | 0.361706 | 0.427980 | 0.338295 | 128.0 | 25.6 | 7 | 0 |
| remap | baseline | 0.480177 | 0.496217 | 0.470813 | 0.340929 | 249.6 | 83.2 | 6 | 1 |
| remap | corroborated | 0.544022 | 0.562119 | 0.510722 | 0.339756 | 371.2 | 0.0 | 15 | 0 |

## All paired comparisons

Positive error reduction favours protection; positive loss cost or delay favours baseline.

| History | Environment | Proposal | Error reduction | Recovery delay | Observed composite cost | Latent composite cost | Affected latent cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| burst | 900 | 900 | 1 | -64 | -0.097236 | -0.129056 | -0.109572 |
| persistent | 900 | 900 | 1 | 0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 900 | 900 | -1 | 128 | 0.070165 | 0.088904 | 0.054202 |
| burst | 900 | 901 | 2 | -128 | -0.097236 | -0.129056 | -0.166839 |
| persistent | 900 | 901 | 1 | 0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 900 | 901 | -1 | 128 | 0.070165 | 0.088904 | 0.054202 |
| burst | 901 | 900 | 1 | -64 | -0.132499 | -0.134429 | -0.112634 |
| persistent | 901 | 900 | 0 | 0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 901 | 900 | -1 | 128 | 0.091545 | 0.089679 | 0.055035 |
| burst | 901 | 901 | 3 | -192 | -0.132499 | -0.134429 | -0.190896 |
| persistent | 901 | 901 | 0 | 0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 901 | 901 | -1 | 128 | 0.091545 | 0.089679 | 0.055035 |
| burst | 902 | 900 | 0 | -64 | -0.072115 | -0.085136 | 0.000000 |
| persistent | 902 | 900 | 0 | -64 | -0.011402 | -0.015768 | 0.000000 |
| remap | 902 | 900 | 3 | -64 | -0.052348 | -0.069336 | 0.000000 |
| burst | 902 | 901 | 0 | -64 | 0.000000 | 0.000000 | 0.000000 |
| persistent | 902 | 901 | 0 | 0 | -0.018156 | -0.017431 | 0.000000 |
| remap | 902 | 901 | 2 | -64 | -0.007207 | -0.006148 | 0.000000 |
| burst | 903 | 900 | 2 | -64 | -0.146100 | -0.139258 | -0.108510 |
| persistent | 903 | 900 | 3 | 0 | -0.005546 | -0.002035 | -0.037039 |
| remap | 903 | 900 | 2 | 128 | 0.096794 | 0.095612 | 0.011603 |
| burst | 903 | 901 | 5 | -576 | -0.146100 | -0.139258 | -0.164015 |
| persistent | 903 | 901 | 3 | 0 | -0.023011 | -0.021847 | -0.036886 |
| remap | 903 | 901 | 0 | 128 | 0.106614 | 0.098271 | 0.053474 |
| burst | 904 | 900 | 2 | -128 | -0.166886 | -0.134057 | -0.166203 |
| persistent | 904 | 900 | 0 | 0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 904 | 900 | -1 | 128 | 0.085586 | 0.091728 | 0.057768 |
| burst | 904 | 901 | 3 | -192 | -0.166886 | -0.134057 | -0.165991 |
| persistent | 904 | 901 | 0 | 0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 904 | 901 | -1 | 128 | 0.085586 | 0.091728 | 0.057768 |

## Environment aggregates

Each row averages two proposal seeds. Histories share their pre-change evidence.

| History | Environment | Error reduction | Recovery delay | Observed cost | Latent cost | Local cost |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| burst | 900 | 1.5 | -96.0 | -0.097236 | -0.129056 | -0.138206 |
| persistent | 900 | 1.0 | 0.0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 900 | -1.0 | 128.0 | 0.070165 | 0.088904 | 0.054202 |
| burst | 901 | 2.0 | -128.0 | -0.132499 | -0.134429 | -0.151765 |
| persistent | 901 | 0.0 | 0.0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 901 | -1.0 | 128.0 | 0.091545 | 0.089679 | 0.055035 |
| burst | 902 | 0.0 | -64.0 | -0.036057 | -0.042568 | 0.000000 |
| persistent | 902 | 0.0 | -32.0 | -0.014779 | -0.016599 | 0.000000 |
| remap | 902 | 2.5 | -64.0 | -0.029778 | -0.037742 | 0.000000 |
| burst | 903 | 3.5 | -320.0 | -0.146100 | -0.139258 | -0.136262 |
| persistent | 903 | 3.0 | 0.0 | -0.014278 | -0.011941 | -0.036963 |
| remap | 903 | 1.0 | 128.0 | 0.101704 | 0.096941 | 0.032539 |
| burst | 904 | 2.5 | -160.0 | -0.166886 | -0.134057 | -0.166097 |
| persistent | 904 | 0.0 | 0.0 | 0.000000 | 0.000000 | 0.000000 |
| remap | 904 | -1.0 | 128.0 | 0.085586 | 0.091728 | 0.057768 |

## Every run

| History | Environment | Proposal | Policy | Transfer | Final full | Stable full | Stable structure | Affected errors | Confirmed recovery |
| --- | ---: | ---: | --- | --- | --- | --- | --- | ---: | ---: |
| persistent | 900 | 900 | baseline | True | False | False | False | 1 | 256 |
| persistent | 900 | 900 | corroborated | True | True | True | True | 0 | 256 |
| persistent | 900 | 901 | baseline | True | False | False | False | 1 | 256 |
| persistent | 900 | 901 | corroborated | True | True | True | True | 0 | 256 |
| burst | 900 | 900 | baseline | True | False | False | False | 1 | 320 |
| burst | 900 | 900 | corroborated | True | True | True | True | 0 | 256 |
| burst | 900 | 901 | baseline | True | False | False | False | 2 | 384 |
| burst | 900 | 901 | corroborated | True | True | True | True | 0 | 256 |
| remap | 900 | 900 | baseline | True | True | True | False | 0 | 256 |
| remap | 900 | 900 | corroborated | True | True | True | False | 1 | 384 |
| remap | 900 | 901 | baseline | True | True | True | True | 0 | 256 |
| remap | 900 | 901 | corroborated | True | True | True | False | 1 | 384 |
| persistent | 901 | 900 | baseline | True | True | True | True | 0 | 256 |
| persistent | 901 | 900 | corroborated | True | True | True | True | 0 | 256 |
| persistent | 901 | 901 | baseline | True | True | True | True | 0 | 256 |
| persistent | 901 | 901 | corroborated | True | True | True | True | 0 | 256 |
| burst | 901 | 900 | baseline | True | True | True | True | 1 | 320 |
| burst | 901 | 900 | corroborated | True | True | True | True | 0 | 256 |
| burst | 901 | 901 | baseline | True | True | True | True | 3 | 448 |
| burst | 901 | 901 | corroborated | True | True | True | True | 0 | 256 |
| remap | 901 | 900 | baseline | True | True | True | True | 0 | 256 |
| remap | 901 | 900 | corroborated | True | True | True | True | 1 | 384 |
| remap | 901 | 901 | baseline | True | True | True | True | 0 | 256 |
| remap | 901 | 901 | corroborated | True | True | True | True | 1 | 384 |
| persistent | 902 | 900 | baseline | True | True | True | False | 1 | 384 |
| persistent | 902 | 900 | corroborated | True | True | True | False | 1 | 320 |
| persistent | 902 | 901 | baseline | True | True | False | False | 0 | 256 |
| persistent | 902 | 901 | corroborated | True | True | True | False | 0 | 256 |
| burst | 902 | 900 | baseline | True | True | True | False | 1 | 384 |
| burst | 902 | 900 | corroborated | True | True | True | False | 1 | 320 |
| burst | 902 | 901 | baseline | True | True | False | False | 3 | 512 |
| burst | 902 | 901 | corroborated | True | True | True | False | 3 | 448 |
| remap | 902 | 900 | baseline | True | True | False | False | 3 | 320 |
| remap | 902 | 900 | corroborated | True | True | True | False | 0 | 256 |
| remap | 902 | 901 | baseline | True | True | False | False | 4 | 512 |
| remap | 902 | 901 | corroborated | True | True | True | False | 2 | 448 |
| persistent | 903 | 900 | baseline | True | True | True | False | 3 | 256 |
| persistent | 903 | 900 | corroborated | True | True | True | True | 0 | 256 |
| persistent | 903 | 901 | baseline | True | True | True | True | 3 | 256 |
| persistent | 903 | 901 | corroborated | True | True | True | True | 0 | 256 |
| burst | 903 | 900 | baseline | True | True | True | False | 2 | 320 |
| burst | 903 | 900 | corroborated | True | True | True | True | 0 | 256 |
| burst | 903 | 901 | baseline | True | True | True | True | 5 | 832 |
| burst | 903 | 901 | corroborated | True | True | True | True | 0 | 256 |
| remap | 903 | 900 | baseline | True | True | True | False | 3 | 256 |
| remap | 903 | 900 | corroborated | True | True | True | True | 1 | 384 |
| remap | 903 | 901 | baseline | True | True | True | True | 1 | 256 |
| remap | 903 | 901 | corroborated | True | True | True | True | 1 | 384 |
| persistent | 904 | 900 | baseline | True | True | True | False | 0 | 256 |
| persistent | 904 | 900 | corroborated | True | True | True | False | 0 | 256 |
| persistent | 904 | 901 | baseline | True | True | True | False | 0 | 256 |
| persistent | 904 | 901 | corroborated | True | True | True | False | 0 | 256 |
| burst | 904 | 900 | baseline | True | True | True | False | 2 | 384 |
| burst | 904 | 900 | corroborated | True | True | True | False | 0 | 256 |
| burst | 904 | 901 | baseline | True | True | True | False | 3 | 448 |
| burst | 904 | 901 | corroborated | True | True | True | False | 0 | 256 |
| remap | 904 | 900 | baseline | True | True | True | False | 0 | 256 |
| remap | 904 | 900 | corroborated | True | True | True | False | 1 | 384 |
| remap | 904 | 901 | baseline | True | True | True | False | 0 | 256 |
| remap | 904 | 901 | corroborated | True | True | True | False | 1 | 384 |

## Frozen checks

```json
{
  "persistent_acquisition_final": true,
  "persistent_composite_observed": true,
  "persistent_composite_latent": true,
  "persistent_affected_latent": true,
  "persistent_error_benefit": true,
  "burst_acquisition_final": true,
  "burst_composite_latent": true,
  "burst_affected_latent": true,
  "burst_error_benefit": true,
  "remap_acquisition_final": true,
  "remap_composite_observed": false,
  "remap_composite_latent": false,
  "remap_affected_latent": true,
  "remap_recovery_delay": false
}
```

## Resources

```json
{
  "runs": 60,
  "allocated_labels": 407040,
  "generated_labels": 101760,
  "used_labels": 407040,
  "candidate_fits": 18078,
  "scoring_queries": 2408960,
  "composite_predictions": 76800,
  "local_predictions": 153600,
  "evaluation_predictions": 49440,
  "oracle_context_queries": 239232,
  "confirmation_queries": 1280
}
```
