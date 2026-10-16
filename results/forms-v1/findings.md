# Experiment 006 findings: useful form discovery within a supplied language

Completed 2026-10-15. Both structural learners discovered the relevant feature,
ignored the two nuisance features, and generalised to the withheld feature
combinations in all five seeds. This establishes a small instance of learning
reusable forms from action consequences. It does **not** establish a need for
two timescales, broad abstraction, or discovery of perceptual primitives.

[Fixed protocol](../../experiments/forms_protocol.md) ·
[Every seed and learned rule](report.md) · [Metrics](metrics.json) ·
[Full trace and source hashes](results.json)

## What was learned

The learner started with one undifferentiated form and no category labels.
The first scheduled review, after 48 main observations, selected a split on the
relevant feature in every structural run. The result was two reusable forms
with opposite action-response profiles. The other two feature positions were
absent from the recognition rules. No benchmark run accepted a further split
or merge; later retained-model acceptances only refreshed response counts.

For example, the seed-0 final rules in both structural learners were:

| Recognition | Identifier | P(y=1, action 0) | P(y=1, action 1) |
| --- | --- | ---: | ---: |
| feature 0 = 0 | form-1 | 0.02 | 0.98 |
| feature 0 = 1 | form-2 | 0.98 | 0.02 |

Identifiers were assigned mechanically. The learner had to discover which
feature mattered, but we supplied the feature alphabet, action alphabet, split
and merge operators, probability estimator, and preference for simple models.
This is a form of supervised structural induction using outcome feedback; it
is not evidence that these representational primitives emerged autonomously.

## Frozen evaluation

The two withheld contexts, each under both actions, never entered fitting,
selection, or learning probes. They were evaluated once with all learning frozen.
Means across the five seeds are:

| Learner | Withheld accuracy | Withheld log loss | Main pre-update loss |
| --- | ---: | ---: | ---: |
| Exact-context lookup | 50% | 0.693147 | 0.165848 |
| Single structural learner | 100% | 0.020203 | 0.215447 |
| Provisional/retained structural learner | 100% | 0.020203 | 0.208286 |
| Fixed-feature logistic learner | 100% | 0.173454 | 0.151555 |

Both structural learners passed every registered acquisition condition in every
seed: exact partition agreement up to renaming, two forms/two recognition leaves,
100% withheld accuracy and loss below 0.25, no nuisance-feature effect, and
relevant-feature probability change 0.96 (required >=0.5).

The lookup learner stayed at probability 1/2 on the withheld contexts. Its 50%
accuracy follows the fixed tie-breaking convention. Its lower training loss
does not imply generalisation; it can memorise the repeated observed inputs.

The fixed-feature learner also achieved 100% withheld accuracy, so explicit
categories were unnecessary for successful classification here. Its probability
predictions still changed with nuisance features by at most about 0.109 on
average across seeds, compared with exactly zero for the structural models.
This is an observed difference for these fixed learners and budgets, not a
claim that conventional predictors cannot learn the same invariance.

The two structural learners ended with identical partitions and predictions.
Their final scores are identical across seeds because balanced data give the
same sufficient statistics after the correct feature is selected. Seeds changed
input order and shuffled feature positions, but happened to cover only two
distinct feature permutations. Five passes are not five independent task
families or evidence of significance/general robustness.

## What this says about fast/slow learning

The single structural learner updated response counts continuously. It accepted
the first structural split and declined three later proposals identical to its
already updated model. These were zero-gain proposals, not misleading candidates
successfully identified through noisy external evidence.

The retained learner changed its deployed model only after selection. It
accepted all four proposals: one split, then three count refreshes. It had a
slightly lower mean training loss than the single structural learner, but no
final advantage. The experiment does not test resistance to interference or
preservation of older forms. Calling one snapshot retained does not establish
long-term retention or the proposed "I know that" function under challenge.

Most notably, **the measured fast/slow response difference was zero at the first
review**, when the useful distinction had not yet been discovered. Both the
provisional and retained one-form models predicted 1/2 after a balanced block.
Scheduled structural search nevertheless found a split with a selection
objective improvement of 0.604039. A rule that required nonzero disagreement at
that review would not have considered this split. This is evidence in this task
that agreement does not establish adequacy; variation needs a route beyond the
current models' response differential. We did not run a gated counterfactual.

Subsequent disagreement reflected count updates within the discovered form.
Its necessity was not tested: reviews were scheduled, and the diagnostic did
not control acceptance. This implementation is a structural extension using
bounded search and externally checked replacement, not a validation of the
earlier additive F/S transfer equations or phase dynamics.

## Selection, computation, and verification

Each structural run evaluated 22 fitted candidates in total: four at the first
review and six at each later review. Thus both structural variants used equal
candidate counts, fit records, and selection feedback in this run. Only each
training-ranked winner reached external selection. Non-winning candidates were
not externally rejected. There were 10 actual structural changes across the ten
structural runs; the retained learner's extra 15 acceptances were count refreshes.

Structural learners stored at most 192 main observations, used 48 separate
selection outcomes only for selection, and shared counts across contexts within
a form. The retained variant also stored a provisional count model and performed
extra predictions. Baselines learned directly from all 240 feedback observations.
The allocation and total feedback access were matched, but feedback roles and
model costs differ. Repeated balanced feedback from this deterministic simulator
does not provide independent evidence about noisy or shifting ground truth.

Exactly **4,880 outcome-bearing presentations** were used. Frozen evaluation
added 240 unlabelled context/action predictions; retained-model diagnostics used
240 paired probes (480 predictions), plus 960 provisional predictions on main
training inputs. Candidate fitting/scoring reused stored training data. There
was no clipping, parameter tuning, extra seed search, or follow-on experiment.

All eight synthetic correctness tests passed before execution. The independent
saved-trace audit passed after execution, checking streams and feature encoding,
pre-update predictions, count and weight arithmetic, candidate counts fitted
only from main feedback, objective rankings, selection decisions, state
continuity, frozen evaluation, acquisition criteria, presentation budgets, and
source/protocol hashes. The audit imports none of the experiment implementation.
Split/merge coverage and caps were also exercised by synthetic fixture tests;
successful merging was not observed in this benchmark.

Commands used:

```sh
python3 -m unittest discover -s checks -p 'test_forms.py' -v
python3 experiments/forms.py
python3 checks/audit_forms_results.py
```

The benchmark command refuses to overwrite its existing result directory. No
implementation correction or protocol change was required after execution.

## Boundary and next question

The result supports learning a small, explicit action-conditioned grouping and
reusing it on unseen combinations. It does not establish autonomous exploration,
causal discovery from observations, general interpretability, steerability,
or safety. Actions were externally scheduled in an isolated simulator.

The next distinct question is whether a learned form can survive distraction
and be reopened when consequences change, compared with the same single-model
control. That requires a fresh protocol and has not been run. No larger model,
live-world connection, or automatic progression follows from this result.
