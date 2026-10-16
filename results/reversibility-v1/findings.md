# Experiment 009: reversible distinctions, with a transition cost

Completed 2026-10-16. **The predeclared acquire–collapse–reacquire test passed in
all five seeds.** One uninterrupted learner acquired two useful forms, reduced
them to one, and learned the distinction again when its consequences returned.
The learner and all its parameters were unchanged from Experiment 008.

This establishes a small instance of reversible structural revision within a
supplied language. It does not establish meta-learning, a category hierarchy,
memory retrieval, or an advantage for two timescales. Removing the distinction
also imposed a measurable temporary prediction cost when the world changed back.

[Fixed protocol](../../experiments/reversibility_protocol.md) ·
[Every seed and review](report.md) · [Metrics](metrics.json) ·
[Complete traces](results.json) · [Consolidated evidence](../research-synthesis.md)

## The continuous trajectory

Initially y=s XOR a, so one context feature distinguishes action consequences.
After main observation 108, the world changes to y=a: that feature no longer
matters. After observation 228, the original rule returns. Both change points
fall between scheduled reviews, which remain every 48 main observations.

There is no change flag, reset, or stored-form restoration. Both learners keep
the most recent 48 main records throughout, refitting their current counts
after each observation. Only the merge-enabled learner can remove a form.
Both can propose new splits. Selection uses separate outcome examples.

Every seed produced the same review results:

| Review | World | Enabled forms | Disabled forms | Enabled / disabled withheld accuracy | Enabled / disabled log loss |
| --- | --- | ---: | ---: | --- | --- |
| 48 | Initial distinction | 2 | 2 | 100% / 100% | 0.074108 / 0.074108 |
| 96 | Initial distinction | 2 | 2 | 100% / 100% | 0.074108 / 0.074108 |
| 144 | Equivalent consequences | 2 | 2 | 100% / 100% | 0.205290 / 0.205290 |
| 192 | Equivalent consequences | 1 | 2 | 100% / 100% | 0.039221 / 0.074108 |
| 240 | Distinction returned | 2 | 2 | 50% / 50% | 0.663435 / 0.663435 |
| 288 | Distinction returned | 2 | 2 | 100% / 100% | 0.074108 / 0.074108 |
| 336 | Distinction returned | 2 | 2 | 100% / 100% | 0.074108 / 0.074108 |

The four withheld context/action pairs never entered fitting or selection.
Additional unlabelled predictions checked the learned partition and invariance
to irrelevant features. At the successful one-form checkpoint, predictions
ignored every context feature but remained sensitive to action.

## Structural change and predictive recovery are different

At review 144 the window still contained 12 old-world and 36 new-world records.
The two-form candidate won the training ranking; the available merge did not
reach external selection. At review 192 only new-world evidence remained, and
the merge was accepted. Successful collapse therefore took **84 main and 24
selection observations after the first change**. The result is sensitive to
the fixed window and review schedule, not evidence of immediate change detection.

At review 240 the returning distinction had supplied only 12 main observations;
36 records still came from the equivalent-consequences world. A split was
nevertheless accepted. It improved selection predictive loss by 0.355993,
outweighing the 0.015 increase in complexity penalty. The recognition structure
had recovered the relevant feature, but its mixed-history probability estimates
still gave only 50% withheld accuracy.

By review 288, both learners satisfied the full acquisition criterion again,
and did so at the final review as well. Successful recovery was first observed
after **60 main and 24 selection observations since the return**. These are
checkpoint measurements, not the exact first individual observation at which
prediction became adequate. The split happened earlier: after 12 main and 12
selection observations. A category's reappearance alone did not establish
successful learning of its current consequences.

## Simplification has a cost when the distinction returns

Mean pre-feedback main log losses across seeds were:

| Period | Merge enabled | Merge disabled |
| --- | ---: | ---: |
| Initial phase | 0.376524 | 0.376524 |
| Equivalent-consequences phase | 0.239103 | 0.250160 |
| Returning-distinction phase | 0.306803 | 0.270226 |
| First 48 main observations after the return | 0.594797 | 0.512499 |
| Entire 336-observation run | 0.305035 | 0.297227 |

Merging improved the pooled model's confidence while the distinction was
irrelevant. On its return, keeping the old partition let the disabled control
adapt the two groups separately immediately. The merged learner initially
pooled their conflicting outcomes until its next structural review. Its first
48-observation return loss was approximately 16% higher, in the pooled mean;
the disadvantage appeared in every seed. After the review at 240, the learners'
current model states and subsequent main traces were identical.

Thus collapse preserved eventual competence but was not free. The declared
final-loss preservation conditions passed; they did not require equal
transition loss. The full-run loss also favoured the no-merge control for this
particular schedule. Neither condition demonstrates a generally optimal choice
about forgetting. The benefit of a smaller representation and the cost of
relearning must both remain visible.

## Interpretation and limits

The strongest supported claim is: **within a fixed representational language,
a learner can acquire a consequential distinction, remove it when unnecessary,
and recreate it when useful again, without being reset.**

Reacquisition is not evidence that the collapsed form was remembered. No saved
category was retrieved, no fresh-start speed comparison was made, and learning
rules or hyperparameters did not adapt. The two functional learning roles from
other experiments were not part of this single structural learner. Their
reciprocal complementarity remains unestablished.

The worlds were deterministic and balanced, with changes at two specified
offsets. Although the first post-change reviews contained mixed evidence,
successful collapse and prediction recovery were measured after old-world
records had expired. We have not tested reliable recovery before that expiry,
arbitrary change timing, rare consequential distinctions, noisy equivalence,
temporary convergence, or retention under interference. Identical checkpoint
scores follow from balanced counts, and five seeds covered only two feature
permutations; they do not establish broad robustness.

## Verification, budget, and stopping

Six synthetic tests passed before the benchmark. An independent saved-trace
audit then passed without importing learner code. It reconstructed streams,
candidate enumeration and ranking, rolling counts, pre-feedback predictions,
selection, frozen evaluations, recovery chronology, paired controls, all
criteria, budgets, and source hashes. The audit reused unchanged independent
arithmetic helpers from Experiment 008.

Exactly **4,480 outcome-bearing presentations** were used: ten runs, each with
336 main, 84 selection, and 28 withheld outcomes. There were 840 additional
unlabelled checkpoint predictions. Enabled used 190 candidate fits across seeds;
disabled used 170. Both replayed 75,000 rows for current-count updates across
their five runs; main storage never exceeded 48 records. Full costs are saved.

```sh
python3 -m unittest discover -s checks -p 'test_reversibility.py' -v
python3 experiments/reversibility.py
python3 checks/audit_reversibility.py
```

Source hashes were saved before execution. The benchmark ran once; there was
no tuning, benchmark rerun, or implementation correction after execution.
Previous experiment sources and results remain unchanged. This closes the
bounded reversibility test and pauses this stage; no further experiment or
scaling follows automatically.
