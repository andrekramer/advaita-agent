# Experiment 013: fixed benchmark

Primary criterion: **FAIL**.

| Branch | Variant | Transfer passes | Final predictive passes | Transfer loss | Final loss | Main loss | Parent raw reads/main |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| persistent | reopen | 10/10 | 10/10 | 0.342068 | 0.348676 | 0.355432 | 0.087 |
| persistent | closed | 10/10 | 9/10 | 0.342068 | 0.380241 | 0.357163 | 0.000 |
| persistent | frozen | 10/10 | 10/10 | 0.342068 | 0.342068 | 0.353609 | 0.000 |
| persistent | flat | 0/10 | 8/10 | 0.693147 | 0.381037 | 0.419521 | 2.000 |
| remap | reopen | 10/10 | 10/10 | 0.342068 | 0.347517 | 0.469580 | 0.175 |
| remap | closed | 10/10 | 9/10 | 0.342068 | 0.380241 | 0.466690 | 0.000 |
| remap | frozen | 10/10 | 0/10 | 0.342068 | 1.074108 | 1.073267 | 0.000 |
| remap | flat | 0/10 | 6/10 | 0.693147 | 0.381037 | 0.498005 | 2.000 |
| breach | reopen | 10/10 | 9/10 | 0.342068 | 0.380493 | 0.463270 | 0.875 |
| breach | closed | 10/10 | 0/10 | 0.342068 | 1.072144 | 1.078503 | 0.000 |
| breach | frozen | 10/10 | 0/10 | 0.342068 | 1.074108 | 1.074949 | 0.000 |
| breach | flat | 0/10 | 8/10 | 0.693147 | 0.381037 | 0.419521 | 2.000 |

Final predictive passes require accuracy 1 and regret <=.10;
the primary criterion additionally tests local exactness, interface choices and controls.

## Fixed checks

```json
{
  "transfer_count": true,
  "transfer_gain": true,
  "remap_closed": true,
  "remap_upper_frozen": true,
  "remap_frozen_challenged": true,
  "remap_reopen_stays_coarse": false,
  "breach_correct_interface": true,
  "breach_closed_challenged": true,
  "breach_gain": true,
  "persistent_structure": true,
  "persistent_cost": true
}
```

## Resources

```json
{
  "runs": 120,
  "allocated_label_presentations": 399360,
  "generated_labels": 49920,
  "evaluation_predictions": 33600,
  "costs": {
    "candidate_fits": 7680,
    "candidate_fit_rows": 1290240,
    "refits": 122880,
    "refit_rows": 19192320,
    "upper_refits": 21184,
    "upper_refit_rows": 4067328,
    "upper_candidate_fits": 720,
    "upper_candidate_rows": 138240,
    "prediction_raw_reads": 36544,
    "feedback_labels": 253440
  }
}
```

## Every run

| Environment | Learner seed | Branch | Variant | Transfer | Final exact + predictive | Final mode | First valid review | Upper accepts |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 300 | 300 | persistent | reopen | True | True | coarse | 64 | [] |
| 300 | 300 | persistent | closed | True | True | coarse | 64 | [] |
| 300 | 300 | persistent | frozen | True | True | coarse | 64 | [] |
| 300 | 300 | persistent | flat | False | True | flat | 128 | [] |
| 300 | 301 | persistent | reopen | True | True | coarse | 64 | [] |
| 300 | 301 | persistent | closed | True | True | coarse | 64 | [] |
| 300 | 301 | persistent | frozen | True | True | coarse | 64 | [] |
| 300 | 301 | persistent | flat | False | True | flat | 128 | [] |
| 300 | 300 | remap | reopen | True | True | coarse | 64 | [] |
| 300 | 300 | remap | closed | True | True | coarse | 64 | [] |
| 300 | 300 | remap | frozen | True | False | coarse | None | [] |
| 300 | 300 | remap | flat | False | False | flat | None | [] |
| 300 | 301 | remap | reopen | True | True | coarse | 64 | [] |
| 300 | 301 | remap | closed | True | True | coarse | 64 | [] |
| 300 | 301 | remap | frozen | True | False | coarse | None | [] |
| 300 | 301 | remap | flat | False | False | flat | None | [] |
| 300 | 300 | breach | reopen | True | True | fine0 | 64 | [64] |
| 300 | 300 | breach | closed | True | False | coarse | None | [] |
| 300 | 300 | breach | frozen | True | False | coarse | None | [] |
| 300 | 300 | breach | flat | False | True | flat | 64 | [] |
| 300 | 301 | breach | reopen | True | True | fine0 | 64 | [64] |
| 300 | 301 | breach | closed | True | False | coarse | None | [] |
| 300 | 301 | breach | frozen | True | False | coarse | None | [] |
| 300 | 301 | breach | flat | False | True | flat | 64 | [] |
| 301 | 300 | persistent | reopen | True | True | coarse | 64 | [] |
| 301 | 300 | persistent | closed | True | True | coarse | 64 | [] |
| 301 | 300 | persistent | frozen | True | True | coarse | 64 | [] |
| 301 | 300 | persistent | flat | False | True | flat | 192 | [] |
| 301 | 301 | persistent | reopen | True | True | coarse | 64 | [] |
| 301 | 301 | persistent | closed | True | True | coarse | 64 | [] |
| 301 | 301 | persistent | frozen | True | True | coarse | 64 | [] |
| 301 | 301 | persistent | flat | False | True | flat | 192 | [] |
| 301 | 300 | remap | reopen | True | True | coarse | 128 | [] |
| 301 | 300 | remap | closed | True | True | coarse | 128 | [] |
| 301 | 300 | remap | frozen | True | False | coarse | None | [] |
| 301 | 300 | remap | flat | False | False | flat | None | [] |
| 301 | 301 | remap | reopen | True | True | fine0 | 192 | [64] |
| 301 | 301 | remap | closed | True | True | coarse | 128 | [] |
| 301 | 301 | remap | frozen | True | False | coarse | None | [] |
| 301 | 301 | remap | flat | False | False | flat | None | [] |
| 301 | 300 | breach | reopen | True | True | fine0 | 64 | [64] |
| 301 | 300 | breach | closed | True | False | coarse | None | [] |
| 301 | 300 | breach | frozen | True | False | coarse | None | [] |
| 301 | 300 | breach | flat | False | True | flat | 128 | [] |
| 301 | 301 | breach | reopen | True | True | fine0 | 64 | [64] |
| 301 | 301 | breach | closed | True | False | coarse | None | [] |
| 301 | 301 | breach | frozen | True | False | coarse | None | [] |
| 301 | 301 | breach | flat | False | True | flat | 128 | [] |
| 302 | 300 | persistent | reopen | True | True | coarse | 64 | [] |
| 302 | 300 | persistent | closed | True | True | coarse | 64 | [] |
| 302 | 300 | persistent | frozen | True | True | coarse | 64 | [] |
| 302 | 300 | persistent | flat | False | True | flat | 128 | [] |
| 302 | 301 | persistent | reopen | True | True | coarse | 64 | [] |
| 302 | 301 | persistent | closed | True | True | coarse | 64 | [] |
| 302 | 301 | persistent | frozen | True | True | coarse | 64 | [] |
| 302 | 301 | persistent | flat | False | True | flat | 128 | [] |
| 302 | 300 | remap | reopen | True | True | coarse | 64 | [] |
| 302 | 300 | remap | closed | True | True | coarse | 64 | [] |
| 302 | 300 | remap | frozen | True | False | coarse | None | [] |
| 302 | 300 | remap | flat | False | False | flat | None | [] |
| 302 | 301 | remap | reopen | True | True | coarse | 64 | [] |
| 302 | 301 | remap | closed | True | True | coarse | 64 | [] |
| 302 | 301 | remap | frozen | True | False | coarse | None | [] |
| 302 | 301 | remap | flat | False | False | flat | None | [] |
| 302 | 300 | breach | reopen | True | True | fine1 | 64 | [64] |
| 302 | 300 | breach | closed | True | False | coarse | None | [] |
| 302 | 300 | breach | frozen | True | False | coarse | None | [] |
| 302 | 300 | breach | flat | False | True | flat | 128 | [] |
| 302 | 301 | breach | reopen | True | True | fine1 | 64 | [64] |
| 302 | 301 | breach | closed | True | False | coarse | None | [] |
| 302 | 301 | breach | frozen | True | False | coarse | None | [] |
| 302 | 301 | breach | flat | False | True | flat | 128 | [] |
| 303 | 300 | persistent | reopen | True | True | fine1 | 128 | [64] |
| 303 | 300 | persistent | closed | True | True | coarse | 128 | [] |
| 303 | 300 | persistent | frozen | True | True | coarse | 64 | [] |
| 303 | 300 | persistent | flat | False | True | flat | 128 | [] |
| 303 | 301 | persistent | reopen | True | True | coarse | 64 | [] |
| 303 | 301 | persistent | closed | True | True | coarse | 64 | [] |
| 303 | 301 | persistent | frozen | True | True | coarse | 64 | [] |
| 303 | 301 | persistent | flat | False | True | flat | 128 | [] |
| 303 | 300 | remap | reopen | True | True | coarse | 64 | [] |
| 303 | 300 | remap | closed | True | True | coarse | 64 | [] |
| 303 | 300 | remap | frozen | True | False | coarse | None | [] |
| 303 | 300 | remap | flat | False | False | flat | None | [] |
| 303 | 301 | remap | reopen | True | True | coarse | 64 | [] |
| 303 | 301 | remap | closed | True | True | coarse | 64 | [] |
| 303 | 301 | remap | frozen | True | False | coarse | None | [] |
| 303 | 301 | remap | flat | False | False | flat | None | [] |
| 303 | 300 | breach | reopen | True | True | fine1 | 128 | [64] |
| 303 | 300 | breach | closed | True | False | coarse | None | [] |
| 303 | 300 | breach | frozen | True | False | coarse | None | [] |
| 303 | 300 | breach | flat | False | True | flat | 128 | [] |
| 303 | 301 | breach | reopen | True | True | fine1 | 64 | [64] |
| 303 | 301 | breach | closed | True | False | coarse | None | [] |
| 303 | 301 | breach | frozen | True | False | coarse | None | [] |
| 303 | 301 | breach | flat | False | True | flat | 128 | [] |
| 304 | 300 | persistent | reopen | True | True | coarse | 64 | [] |
| 304 | 300 | persistent | closed | True | True | coarse | 64 | [] |
| 304 | 300 | persistent | frozen | True | True | coarse | 64 | [] |
| 304 | 300 | persistent | flat | False | False | flat | 128 | [] |
| 304 | 301 | persistent | reopen | True | False | fine1 | 64 | [512] |
| 304 | 301 | persistent | closed | True | False | coarse | 64 | [] |
| 304 | 301 | persistent | frozen | True | True | coarse | 64 | [] |
| 304 | 301 | persistent | flat | False | False | flat | 128 | [] |
| 304 | 300 | remap | reopen | True | True | fine0 | 192 | [64] |
| 304 | 300 | remap | closed | True | True | coarse | 128 | [] |
| 304 | 300 | remap | frozen | True | False | coarse | None | [] |
| 304 | 300 | remap | flat | False | False | flat | None | [] |
| 304 | 301 | remap | reopen | True | False | fine1 | 64 | [512] |
| 304 | 301 | remap | closed | True | False | coarse | 64 | [] |
| 304 | 301 | remap | frozen | True | False | coarse | None | [] |
| 304 | 301 | remap | flat | False | False | flat | None | [] |
| 304 | 300 | breach | reopen | True | True | fine0 | 64 | [64] |
| 304 | 300 | breach | closed | True | False | coarse | None | [] |
| 304 | 300 | breach | frozen | True | False | coarse | None | [] |
| 304 | 300 | breach | flat | False | False | flat | 192 | [] |
| 304 | 301 | breach | reopen | True | False | fine0 | 64 | [64, 512] |
| 304 | 301 | breach | closed | True | False | coarse | None | [] |
| 304 | 301 | breach | frozen | True | False | coarse | None | [] |
| 304 | 301 | breach | flat | False | False | flat | 192 | [] |
