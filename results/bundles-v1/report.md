# Experiment 010: stochastic minimal bundles

Primary criterion: **FAIL**.
Passing stochastic runs: {'reversible': 5, 'persistent': 7} (10 per branch).

Five environment seeds crossed with two proposal seeds; controls are not duplicated.
Expected loss uses the known noisy world distribution only inside frozen evaluation.
These are future-distribution predictions, not withheld-context or task-family transfer.

## Endpoint performance

| Branch | Learner | Runs | Loss at 384 | Loss at 768 | Loss at 1152 | Main loss | Prediction features/read |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| reversible | stochastic | 10 | 0.410547 | 0.335205 | 0.412981 | 0.555861 | 1.238889 |
| reversible | deterministic | 5 | 0.338195 | 0.333527 | 0.340098 | 0.508781 | 1.422222 |
| reversible | singleton | 10 | 0.698647 | 0.333527 | 0.695660 | 0.636567 | 0.538889 |
| reversible | full_context | 5 | 0.533203 | 0.523596 | 0.527681 | 0.576593 | 6.000000 |
| persistent | stochastic | 10 | 0.410547 | 0.341285 | 0.378014 | 0.436626 | 1.522222 |
| persistent | deterministic | 5 | 0.338195 | 0.341285 | 0.340098 | 0.421563 | 1.600000 |
| persistent | singleton | 10 | 0.698647 | 0.699474 | 0.695660 | 0.701674 | 0.211111 |
| persistent | full_context | 5 | 0.533203 | 0.523596 | 0.527681 | 0.533306 | 6.000000 |

Noise oracle expected log loss: 0.325083 nats.

## All stochastic runs

| World | Proposal seed | Correct structure/prediction | Singleton margins A1 / A2 | Cut effects A1 / A2 | Pass |
| --- | ---: | --- | --- | --- | --- |
| 0-reversible | 0 | False | 0.3522 / 0.3535 | 0.3531 / 0.3516 | False |
| 0-reversible | 1 | True | 0.3522 / 0.3535 | 0.3531 / 0.3516 | True |
| 0-persistent | 0 | True | 0.3522 / 0.3535 | 0.3531 / 0.3516 | True |
| 0-persistent | 1 | True | 0.3522 / 0.3535 | 0.3531 / 0.3516 | True |
| 1-reversible | 0 | False | 0.3580 / 0.3582 | 0.3552 / 0.3535 | False |
| 1-reversible | 1 | True | 0.3580 / 0.3582 | 0.3552 / 0.3535 | True |
| 1-persistent | 0 | False | 0.3580 / -0.0210 | 0.3552 / 0.0000 | False |
| 1-persistent | 1 | True | 0.3580 / 0.3582 | 0.3552 / 0.3535 | True |
| 2-reversible | 0 | False | 0.0154 / -0.0317 | 0.0000 / 0.0000 | False |
| 2-reversible | 1 | False | 0.0154 / -0.0015 | 0.0000 / 0.0000 | False |
| 2-persistent | 0 | False | 0.0154 / 0.3478 | 0.0000 / 0.3487 | False |
| 2-persistent | 1 | False | 0.0154 / 0.3478 | 0.0000 / 0.3487 | False |
| 3-reversible | 0 | False | 0.3552 / 0.3591 | 0.3557 / 0.3573 | False |
| 3-reversible | 1 | True | 0.3552 / 0.3591 | 0.3557 / 0.3573 | True |
| 3-persistent | 0 | True | 0.3552 / 0.3591 | 0.3557 / 0.3573 | True |
| 3-persistent | 1 | True | 0.3552 / 0.3591 | 0.3557 / 0.3573 | True |
| 4-reversible | 0 | True | 0.3596 / 0.3592 | 0.3584 / 0.3597 | True |
| 4-reversible | 1 | True | 0.3596 / 0.3592 | 0.3584 / 0.3597 | True |
| 4-persistent | 0 | True | 0.3596 / 0.3592 | 0.3584 / 0.3597 | True |
| 4-persistent | 1 | True | 0.3596 / 0.3592 | 0.3584 / 0.3597 | True |

## Endpoint subsets and discovery

| World | Learner | Proposal seed | Subsets at 384 / 768 / 1152 | First successful reviews in each phase |
| --- | --- | --- | --- | --- |
| 0-reversible | stochastic | 0 | [[0, 1], [0, 5], [0, 1]] | [384, None, 896] |
| 0-reversible | stochastic | 1 | [[0, 1], [0], [0, 1]] | [64, 512, 1024] |
| 0-reversible | singleton | 0 | [[], [0], []] | [None, 512, None] |
| 0-reversible | singleton | 1 | [[], [0], []] | [None, 512, None] |
| 0-reversible | deterministic | None | [[0, 1], [0], [0, 1]] | [128, 704, 896] |
| 0-reversible | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 0-persistent | stochastic | 0 | [[0, 1], [0, 1], [0, 1]] | [384, 448, 832] |
| 0-persistent | stochastic | 1 | [[0, 1], [0, 1], [0, 1]] | [64, 448, 832] |
| 0-persistent | singleton | 0 | [[], [], []] | [None, None, None] |
| 0-persistent | singleton | 1 | [[], [], []] | [None, None, None] |
| 0-persistent | deterministic | None | [[0, 1], [0, 1], [0, 1]] | [128, 448, 832] |
| 0-persistent | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 1-reversible | stochastic | 0 | [[0, 1], [0, 5], [0, 1]] | [384, None, 960] |
| 1-reversible | stochastic | 1 | [[0, 1], [0], [0, 1]] | [64, 512, 1024] |
| 1-reversible | singleton | 0 | [[4], [0], []] | [None, 512, None] |
| 1-reversible | singleton | 1 | [[4], [0], [3]] | [None, 512, None] |
| 1-reversible | deterministic | None | [[0, 1], [0], [0, 1]] | [128, 704, 960] |
| 1-reversible | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 1-persistent | stochastic | 0 | [[0, 1], [0, 1], [2]] | [384, 448, None] |
| 1-persistent | stochastic | 1 | [[0, 1], [0, 1], [0, 1]] | [64, 448, 896] |
| 1-persistent | singleton | 0 | [[4], [5], []] | [None, None, None] |
| 1-persistent | singleton | 1 | [[4], [], [3]] | [None, None, None] |
| 1-persistent | deterministic | None | [[0, 1], [0, 1], [0, 1]] | [128, 448, 1152] |
| 1-persistent | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 2-reversible | stochastic | 0 | [[], [2, 3], [3, 5]] | [None, None, None] |
| 2-reversible | stochastic | 1 | [[], [2], [3]] | [None, 512, None] |
| 2-reversible | singleton | 0 | [[1], [2], []] | [None, 512, None] |
| 2-reversible | singleton | 1 | [[], [2], []] | [None, 512, None] |
| 2-reversible | deterministic | None | [[1, 2], [2], [1, 2]] | [192, 768, 960] |
| 2-reversible | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 2-persistent | stochastic | 0 | [[], [1, 2], [1, 2]] | [None, 448, 832] |
| 2-persistent | stochastic | 1 | [[], [1, 2], [1, 2]] | [None, 448, 832] |
| 2-persistent | singleton | 0 | [[1], [1], []] | [None, None, None] |
| 2-persistent | singleton | 1 | [[], [], []] | [None, None, None] |
| 2-persistent | deterministic | None | [[1, 2], [1, 2], [1, 2]] | [192, 448, 832] |
| 2-persistent | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 3-reversible | stochastic | 0 | [[3, 5], [1, 5], [3, 5]] | [128, None, 1024] |
| 3-reversible | stochastic | 1 | [[3, 5], [5], [3, 5]] | [384, 512, 896] |
| 3-reversible | singleton | 0 | [[], [5], []] | [None, 512, None] |
| 3-reversible | singleton | 1 | [[], [5], []] | [None, 576, None] |
| 3-reversible | deterministic | None | [[3, 5], [5], [3, 5]] | [320, 512, 1024] |
| 3-reversible | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 3-persistent | stochastic | 0 | [[3, 5], [3, 5], [3, 5]] | [128, 448, 832] |
| 3-persistent | stochastic | 1 | [[3, 5], [3, 5], [3, 5]] | [384, 448, 832] |
| 3-persistent | singleton | 0 | [[], [], []] | [None, None, None] |
| 3-persistent | singleton | 1 | [[], [], []] | [None, None, None] |
| 3-persistent | deterministic | None | [[3, 5], [3, 5], [3, 5]] | [320, 448, 832] |
| 3-persistent | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 4-reversible | stochastic | 0 | [[0, 5], [5], [0, 5]] | [256, 576, 960] |
| 4-reversible | stochastic | 1 | [[0, 5], [5], [0, 5]] | [128, 576, 1088] |
| 4-reversible | singleton | 0 | [[], [5], []] | [None, 576, None] |
| 4-reversible | singleton | 1 | [[], [5], []] | [None, 576, None] |
| 4-reversible | deterministic | None | [[0, 5], [5], [0, 5]] | [192, 576, 960] |
| 4-reversible | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |
| 4-persistent | stochastic | 0 | [[0, 5], [0, 5], [0, 5]] | [256, 448, 832] |
| 4-persistent | stochastic | 1 | [[0, 5], [0, 5], [0, 5]] | [128, 448, 832] |
| 4-persistent | singleton | 0 | [[], [], []] | [None, None, None] |
| 4-persistent | singleton | 1 | [[], [], []] | [None, None, None] |
| 4-persistent | deterministic | None | [[0, 5], [0, 5], [0, 5]] | [192, 448, 832] |
| 4-persistent | full_context | None | [[0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5], [0, 1, 2, 3, 4, 5]] | [None, None, None] |

## Resource accounting

```json
{
  "runs": 60,
  "generated_world_records": 17280,
  "allocated_outcome_presentations": 103680,
  "used_outcome_presentations": 97920,
  "base_evaluation_predictions": 138240,
  "additional_ablation_predictions": 261632,
  "costs": {
    "main_prediction_feature_reads": 126976,
    "count_refits": 69120,
    "count_refit_rows": 12170880,
    "refit_feature_reads": 23181952,
    "candidate_fits": 3600,
    "candidate_fit_rows": 652800,
    "candidate_fit_feature_reads": 912960,
    "candidate_score_feature_reads": 912960,
    "selection_outcomes": 28800,
    "selection_prediction_feature_reads": 63200
  }
}
```

Full traces include every proposal, decision, accepted subset, prediction, and ablation.
Selection data never fit models. Raw feature buffers remain accessible to search.
No learned folds, meta-learning, autonomous actions, or fast/slow advantage are established.
