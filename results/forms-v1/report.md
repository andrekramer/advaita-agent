# Experiment 006: acquisition results

One registered run per seed and learner; no tuning.

| Learner | Seed | Withheld accuracy | Withheld loss | Training loss | Forms | Leaves | Acquisition |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| lookup | 0 | 50% | 0.693147 | 0.165848 | — | — | not applicable |
| single_structure | 0 | 100% | 0.020203 | 0.215447 | 2 | 2 | True |
| retained_structure | 0 | 100% | 0.020203 | 0.208286 | 2 | 2 | True |
| fixed_features | 0 | 100% | 0.173492 | 0.151571 | — | — | not applicable |
| lookup | 1 | 50% | 0.693147 | 0.165848 | — | — | not applicable |
| single_structure | 1 | 100% | 0.020203 | 0.215447 | 2 | 2 | True |
| retained_structure | 1 | 100% | 0.020203 | 0.208286 | 2 | 2 | True |
| fixed_features | 1 | 100% | 0.174093 | 0.151504 | — | — | not applicable |
| lookup | 2 | 50% | 0.693147 | 0.165848 | — | — | not applicable |
| single_structure | 2 | 100% | 0.020203 | 0.215447 | 2 | 2 | True |
| retained_structure | 2 | 100% | 0.020203 | 0.208286 | 2 | 2 | True |
| fixed_features | 2 | 100% | 0.174801 | 0.151398 | — | — | not applicable |
| lookup | 3 | 50% | 0.693147 | 0.165848 | — | — | not applicable |
| single_structure | 3 | 100% | 0.020203 | 0.215447 | 2 | 2 | True |
| retained_structure | 3 | 100% | 0.020203 | 0.208286 | 2 | 2 | True |
| fixed_features | 3 | 100% | 0.170360 | 0.151882 | — | — | not applicable |
| lookup | 4 | 50% | 0.693147 | 0.165848 | — | — | not applicable |
| single_structure | 4 | 100% | 0.020203 | 0.215447 | 2 | 2 | True |
| retained_structure | 4 | 100% | 0.020203 | 0.208286 | 2 | 2 | True |
| fixed_features | 4 | 100% | 0.174523 | 0.151421 | — | — | not applicable |

## Learned structures

Feature positions were permuted per seed. Rules use encoded feature positions;
names are identifiers within each final model, not supplied semantic labels.

### single_structure, seed 0

Encoding: [0, 2, 1]; simulator-relevant position: 0.

- x0=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x0=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 1.

### retained_structure, seed 0

Encoding: [0, 2, 1]; simulator-relevant position: 0.

- x0=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x0=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 4.

### single_structure, seed 1

Encoding: [1, 2, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 1.

### retained_structure, seed 1

Encoding: [1, 2, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 4.

### single_structure, seed 2

Encoding: [1, 2, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 1.

### retained_structure, seed 2

Encoding: [1, 2, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 4.

### single_structure, seed 3

Encoding: [1, 2, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 1.

### retained_structure, seed 3

Encoding: [1, 2, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 4.

### single_structure, seed 4

Encoding: [2, 1, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 1.

### retained_structure, seed 4

Encoding: [2, 1, 0]; simulator-relevant position: 2.

- x2=0 → form-1; P(y=1 | a=0,1) = (0.020000, 0.980000).
- x2=1 → form-2; P(y=1 | a=0,1) = (0.980000, 0.020000).

Candidates scored: 22; reviews accepted: 4.

## Accounting

20 runs × (192 main + 48 selection + 4 final outcomes) = 4,880 presentations.
240 additional unlabelled final predictions; 240 paired A/N diagnostic probes.
Structural learners fit counts on 192 main records and use 48 selection outcomes
only for selection. Baselines update on all 240 feedback records.
All traces, candidates, probabilities, counts and decisions are in results.json.
See findings.md for interpretation and audit status.
