# Experiment 008: collapse when a distinction stops mattering

Completed 2026-10-16. **The predeclared point test passed in all five seeds.**
The learner first acquired a useful distinction, collapsed it when both groups
acquired the same action consequences, and preserved it in the unchanged-world
control. Final prediction accuracy on withheld feature combinations was 100%
in every condition.

[Fixed protocol](../../experiments/collapse_protocol.md) ·
[All seeds, reviews, and costs](report.md) · [Metrics](metrics.json) ·
[Full traces and source hashes](results.json)

## What happened

All learners began with one undifferentiated form. In the initial world,
y=s XOR a, one observable feature determined which action produced which
outcome. Both learners discovered that feature and acquired two forms, rather
than receiving a constructed two-form starting state.

After 96 main observations, one world changed to y=a. The original feature no
longer affected the outcome, but the action still did. In the paired control
world the original rule continued. Neither learner received a change flag.
Both used a rolling window of 48 main observations from the very beginning;
the window was never reset at the change.

Every seed produced this form-count history:

| World | Learner | Trial 48 | Trial 96 | Trial 144 | Trial 192 |
| --- | --- | ---: | ---: | ---: | ---: |
| Changed | Merge enabled | 2 | 2 | 1 | 1 |
| Changed | Merge disabled | 2 | 2 | 2 | 2 |
| Unchanged | Merge enabled | 2 | 2 | 2 | 2 |
| Unchanged | Merge disabled | 2 | 2 | 2 | 2 |

The merge occurred at the first scheduled review after the change: **48 new
main observations, followed by 12 selection observations**. By then the rolling
window contained only the new rule. The two recognition leaves became one
all-wildcard rule, and their separate response tables became one shared table.
The model did not split again at the remaining review.

This timing is a consequence of the fixed window and review schedule. It does
not establish that the learner detected the change immediately or would collapse
appropriately after fewer examples or at an arbitrary change time.

## Predictions remained useful

Contexts 000 and 111, under both actions, were withheld from training and
selection. Final frozen-evaluation results were identical across seeds:

| World | Learner | Final forms / leaves | Withheld accuracy | Log loss |
| --- | --- | ---: | ---: | ---: |
| Changed | Merge enabled | 1 / 1 | 100% | 0.039221 |
| Changed | Merge disabled | 2 / 2 | 100% | 0.074108 |
| Unchanged | Merge enabled | 2 / 2 | 100% | 0.074108 |
| Unchanged | Merge disabled | 2 / 2 | 100% | 0.074108 |

In the changed world, the merged model's prediction became invariant to all
three context features while remaining sensitive to action. It predicted
P(y=1|a=0)=1/26 and P(y=1|a=1)=25/26, for any context. This was useful
simplification, not a constant-output collapse or merely deleting observations.

The no-merge learner adapted too. Its two groups ended with identical response
predictions, 1/14 and 13/14 for the two actions, while still using the original
feature to assign contexts to two forms. Thus **behavioural insensitivity to a
feature can occur without removing the structural distinction**.

Merging pooled 24 observations per action instead of keeping 12 per action in
each group. With the fixed added-count estimator this increased confidence in
the same correct answers. The lower log loss does not mean higher accuracy:
both learners were already correct on all four held-out examples.

## Selection and the preservation control

Each accepted merge improved selection predictive loss by 0.034887 and reduced
the complexity penalty by 0.015, giving total selection-objective improvement
0.049887, above the fixed 0.001 margin. Prediction improvement and the supplied
preference for fewer forms both favoured this merge. We did not separately
ablate that preference, and cannot claim it was necessary.

In the unchanged world, merging would have erased a still-useful distinction.
The available one-form candidate lost during **training ranking**, so it did
not advance to external selection. The winner was the existing two-form model;
its zero selection gain did not justify replacement. This demonstrates
preservation by the complete proposal/ranking/selection procedure, not repeated
external rejection of harmful merges. A synthetic fixture separately verified
that the selection code can reject a harmful merge.

All runs passed the initial acquisition requirements. In the unchanged world
the correct partition and nuisance-feature invariance persisted. In the changed
world the merge-disabled learner remained a functioning predictor, and the
merge-enabled learner met the declared loss-preservation margin as well as
the structural-collapse criteria.

## What the result establishes and leaves open

This supports a small operational version of **letting go of a distinction
when it no longer changes the consequences that matter to the task**. The
distinction was learned and later removed within the running learner. The
result does not depend on two timescales or resolve the failed complementarity
test from Experiment 007.

The representation language, merge operator, recent-evidence window, and
complexity preference were supplied by us. The learner did not invent those
principles. The world was deterministic, balanced and fully sampled across both
groups and actions. Infrequent but important differences, noisy equivalence,
temporary convergence, and recovery of an old distinction remain untested.
Discarding old evidence on a fixed schedule may be inappropriate in those cases.

The change was aligned with a review boundary, and all old-regime records had
expired by the decisive review. Selection examples came from the same target
process, not an independent source of ground truth. Identical final scores across
seeds follow from balanced counts after the correct feature is identified;
the feature shuffles covered only two distinct permutations. Five passes on this
constructed point test are not evidence of general robustness or significance.

## Verification and budget

Six synthetic correctness tests passed before execution. The independent saved-
trace audit passed after execution, without importing learner code. It checked
stream regeneration, paired prefixes, rolling expiration, full candidate
enumeration, fitted counts, pre-feedback predictions, training rankings, selection
gains, frozen evaluation, criteria, computation counts, budgets and source hashes.

Exactly **4,960 outcome-bearing presentations** were used across 20 runs:
192 main, 48 selection and eight held-out evaluation outcomes per run. There
were 480 additional unlabelled checkpoint predictions. Main storage never
exceeded 48 records. Both variants replayed the same main-window data to update
their current counts; their candidate search costs differed because one allowed
merges. Those costs are reported separately.

Commands used:

```sh
python3 -m unittest discover -s checks -p 'test_collapse.py' -v
python3 experiments/collapse.py
python3 checks/audit_collapse.py
```

The benchmark refuses to overwrite its result directory. No tuning, benchmark
rerun, post-execution implementation correction, or further experiment was
performed. The Experiment 006 structural primitives were reused unchanged;
previous experiments and their source/result hashes remain intact.
